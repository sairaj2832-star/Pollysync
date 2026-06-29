import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.farm import Farm
from app.models.prediction import Prediction
from app.services.bee_service import get_mock_bees
from app.services.feature_engineering import build_features
from app.services.weather_service import cache_weather, fetch_weather, get_cached_weather

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

    if flowering_model and psi_model:
        import pandas as pd
        df = pd.DataFrame([features])
        start_doy = int(flowering_model.predict(df)[0])
        confidence = 0.87
        psi = int(psi_model.predict(df)[0])
        psi = max(0, min(100, psi))
        risk = risk_model.predict(df)[0] if risk_model else "Medium"
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
