import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.farm import Farm
from app.models.prediction import Prediction
from app.services.bee_service import get_mock_bees
from app.services.feature_engineering import build_features
from app.services.weather_service import cache_weather, fetch_weather, get_cached_weather

MODELS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "ml" / "models"

flowering_model = None
flowering_scaler = None
psi_model = None
psi_scaler = None
risk_model = None
risk_scaler = None


def _load_models():
    global flowering_model, flowering_scaler, psi_model, psi_scaler, risk_model, risk_scaler
    try:
        import joblib
        for name in ("flowering", "psi", "risk"):
            model_path = MODELS_DIR / f"{name}_model.pkl"
            scaler_path = MODELS_DIR / f"{name}_scaler.pkl"
            if model_path.exists():
                globals()[f"{name}_model"] = joblib.load(str(model_path))
            if scaler_path.exists():
                globals()[f"{name}_scaler"] = joblib.load(str(scaler_path))
    except Exception:
        pass


_load_models()


def _predict_flowering_baseline(features: dict) -> tuple[int, float]:
    base = {
        "mustard": 15, "wheat": 45, "sunflower": 60, "rice": 90, "cotton": 120,
    }
    crop = "mustard"
    for key in base:
        if features.get(f"crop_{key}", 0):
            crop = key
            break
    start = base[crop] + int(features.get("temp_7d_mean", 25) - 25) * 2
    start = max(1, min(365, start))
    confidence = 0.70
    return start, confidence


def _predict_psi_baseline(features: dict) -> tuple[int, str]:
    score = 0
    temp = features.get("temp_7d_mean", 25)
    humidity = features.get("humidity", 60)
    ndvi = features.get("ndvi", 0.5)
    bee_count = features.get("bee_richness", 0)

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

    if score >= 70:
        risk = "Low"
    elif score >= 40:
        risk = "Medium"
    else:
        risk = "High"

    return score, risk


async def run_prediction(farm: Farm, db: Session) -> Prediction:
    cached = get_cached_weather(farm.id, db)
    if cached:
        weather = {"temperature": cached.temperature, "humidity": cached.humidity,
                   "rainfall": cached.rainfall, "wind_speed": cached.wind_speed}
    else:
        raw = await fetch_weather(farm.location_lat, farm.location_lng)
        cached = cache_weather(farm.id, raw, db)
        weather = {"temperature": cached.temperature, "humidity": cached.humidity,
                   "rainfall": cached.rainfall, "wind_speed": cached.wind_speed}

    now = datetime.now(timezone.utc)
    bee_species = get_mock_bees(farm.crop_type)

    features = build_features(
        crop_type=farm.crop_type,
        temperature=weather["temperature"],
        humidity=weather["humidity"],
        rainfall=weather["rainfall"],
        wind_speed=weather["wind_speed"],
        ndvi=0.65,
        bee_count=len(bee_species),
        month=now.month,
        day_of_year=now.timetuple().tm_yday,
    )

    if all([flowering_model, flowering_scaler, psi_model, psi_scaler, risk_model, risk_scaler]):
        import pandas as pd
        from app.services.feature_engineering import CROP_ENCODER
        expected_cols = sorted(features.keys())
        df = pd.DataFrame([features])[expected_cols]

        X_scaled = flowering_scaler.transform(df)
        start_doy = int(round(flowering_model.predict(X_scaled)[0]))
        start_doy = max(1, min(365, start_doy))
        confidence = 0.87

        psi = int(round(psi_model.predict(psi_scaler.transform(df))[0]))
        psi = max(0, min(100, psi))

        risk_raw = risk_model.predict(risk_scaler.transform(df))[0]
        if hasattr(risk_model, '_label_encoder'):
            risk = risk_model._label_encoder.inverse_transform([risk_raw])[0]
        else:
            risk = risk_raw
    else:
        start_doy, confidence = _predict_flowering_baseline(features)
        psi, risk = _predict_psi_baseline(features)

    from datetime import datetime as dt
    start_date = dt.fromordinal(dt(2026, 1, 1).toordinal() + start_doy - 1)
    end_date = dt.fromordinal(start_date.toordinal() + 7)

    prediction = Prediction(
        farm_id=farm.id,
        flowering_start=start_date.strftime("%Y-%m-%d"),
        flowering_end=end_date.strftime("%Y-%m-%d"),
        flowering_confidence=confidence,
        psi_score=psi,
        risk_level=risk,
        weather_summary=json.dumps(weather),
        pollen_summary=json.dumps({"tree": features["pollen_tree"],
                                    "grass": features["pollen_grass"],
                                    "weed": features["pollen_weed"]}),
        ndvi_value=features["ndvi"],
        bee_species=json.dumps(bee_species),
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction
