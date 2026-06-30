"""
app/services/prediction_service.py

Replaces the old version's hardcoded `ndvi=0.65` and current-weather-only
call with real environment data (NASA POWER 7-day weather, Earth Engine
NDVI, GBIF bee richness) via environment_service.get_environment_features().

Drop-in replacement: same run_prediction(farm, db) signature, same callers
(predictions.py route doesn't need to change at all).
"""

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.farm import Farm
from app.models.prediction import Prediction
from app.services.environment_service import get_environment_features
from app.services.bee_service import get_mock_bees

from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"

flowering_model = None
psi_model = None
risk_model = None


def _load_models():
    global flowering_model, psi_model, risk_model
    try:
        import joblib
        flowering_path = MODELS_DIR / "flowering_model.pkl"
        psi_path = MODELS_DIR / "psi_model.pkl"
        risk_path = MODELS_DIR / "risk_model.pkl"
        if flowering_path.exists():
            flowering_model = joblib.load(str(flowering_path))
        if psi_path.exists():
            psi_model = joblib.load(str(psi_path))
        if risk_path.exists():
            risk_model = joblib.load(str(risk_path))
    except Exception:
        pass


_load_models()


def _predict_flowering_baseline(features: dict) -> tuple[int, float]:
    base = {"mustard": 15, "wheat": 45, "sunflower": 60, "rice": 90, "cotton": 120}
    crop = "mustard"
    for key in base:
        if features.get(f"crop_{key}", 0):
            crop = key
            break
    temp = features.get("temp_7d_mean") or 25
    start = base[crop] + int(temp - 25) * 2
    start = max(1, min(365, start))
    return start, 0.70


def _predict_psi_baseline(features: dict) -> tuple[int, str]:
    score = 0
    temp = features.get("temp_7d_mean") or 25
    humidity = features.get("humidity") or 60
    ndvi = features.get("ndvi") or 0.5
    bee_count = features.get("bee_richness") or 0

    if 20 <= temp <= 32:
        score += 25
    elif 15 <= temp <= 35:
        score += 15
    if 50 <= humidity <= 80:
        score += 20
    elif 30 <= humidity <= 90:
        score += 10
    if ndvi > 0.6:
        score += 20
    elif ndvi > 0.4:
        score += 10
    if bee_count >= 3:
        score += 15
    elif bee_count >= 1:
        score += 8

    score = max(0, min(100, score))
    risk = "Low" if score >= 70 else "Medium" if score >= 40 else "High"
    return score, risk


async def run_prediction(farm: Farm, db: Session) -> Prediction:
    now = datetime.now(timezone.utc)

    # Real environment data: NASA POWER (weather) + Earth Engine (NDVI) +
    # GBIF (bee richness) + seasonal pollen table, all keyed off farm's
    # actual lat/lon and crop. Falls back gracefully if NDVI/EE isn't
    # configured (returns None -> baseline below treats it as 0.5).
    features = await get_environment_features(
        lat=farm.location_lat,
        lon=farm.location_lng,
        crop_type=farm.crop_type,
        as_of=now.date(),
    )

    bee_species = get_mock_bees(farm.crop_type)  # still used for display list in dashboard

    if flowering_model and psi_model and features["ndvi"] is not None:
        import pandas as pd
        from app.services.feature_engineering import CROP_ENCODER  # noqa: F401  (kept for column order reference)

        model_features = {k: v for k, v in features.items() if not k.startswith("_")}
        df = pd.DataFrame([model_features])
        start_doy = int(flowering_model.predict(df)[0])
        confidence = 0.87
        psi = int(psi_model.predict(df)[0])
        psi = max(0, min(100, psi))
        risk = risk_model.predict(df)[0] if risk_model else "Medium"
    else:
        start_doy, confidence = _predict_flowering_baseline(features)
        psi, risk = _predict_psi_baseline(features)

    start_date = datetime.fromordinal(datetime(now.year, 1, 1).toordinal() + start_doy - 1)
    end_date = datetime.fromordinal(start_date.toordinal() + 7)

    weather_summary = {
        "temperature": features["temp_7d_mean"],
        "humidity": features["humidity"],
        "rainfall": features["rainfall_7d"],
        "wind_speed": features["wind_speed"],
    }

    prediction = Prediction(
        farm_id=farm.id,
        flowering_start=start_date.strftime("%Y-%m-%d"),
        flowering_end=end_date.strftime("%Y-%m-%d"),
        flowering_confidence=confidence,
        psi_score=psi,
        risk_level=risk,
        weather_summary=json.dumps(weather_summary),
        pollen_summary=json.dumps({
            "tree": features["pollen_tree"],
            "grass": features["pollen_grass"],
            "weed": features["pollen_weed"],
        }),
        ndvi_value=features["ndvi"] if features["ndvi"] is not None else 0.5,
        bee_species=json.dumps(bee_species),
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction