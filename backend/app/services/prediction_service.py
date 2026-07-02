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
        try:
            raw = await fetch_weather(farm.location_lat, farm.location_lng)
            cached = cache_weather(farm.id, raw, db)
            weather = {"temperature": cached.temperature, "humidity": cached.humidity,
                       "rainfall": cached.rainfall, "wind_speed": cached.wind_speed}
        except Exception:
            weather = _seasonal_weather_fallback(farm.crop_type)

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

    start_date = datetime.fromordinal(datetime(now.year, 1, 1).toordinal() + start_doy - 1)
    end_date = datetime.fromordinal(start_date.toordinal() + 7)
    recommendation = generate_local_recommendation(
        crop_type=farm.crop_type,
        flowering_start=start_date.strftime("%Y-%m-%d"),
        flowering_end=end_date.strftime("%Y-%m-%d"),
        psi_score=psi,
        risk_level=str(risk),
        weather=weather,
    )

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
        recommendation=recommendation,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


def _seasonal_weather_fallback(crop_type: str) -> dict:
    crop = crop_type.lower()
    defaults = {
        "mustard": {"temperature": 24, "humidity": 62, "rainfall": 2, "wind_speed": 8},
        "wheat": {"temperature": 22, "humidity": 58, "rainfall": 1, "wind_speed": 9},
        "sunflower": {"temperature": 28, "humidity": 55, "rainfall": 3, "wind_speed": 10},
        "rice": {"temperature": 30, "humidity": 78, "rainfall": 12, "wind_speed": 7},
        "cotton": {"temperature": 29, "humidity": 64, "rainfall": 4, "wind_speed": 11},
    }
    return defaults.get(crop, defaults["mustard"])


def generate_local_recommendation(
    crop_type: str,
    flowering_start: str,
    flowering_end: str,
    psi_score: int,
    risk_level: str,
    weather: dict,
) -> str:
    risk = risk_level.lower()
    if risk == "high":
        action = (
            "Prioritise field inspection, avoid pesticide sprays during flowering, "
            "and consider managed pollinator support if bee activity is low."
        )
    elif risk == "medium":
        action = (
            "Keep irrigation steady, watch wind and rainfall during flowering, "
            "and protect bee activity during morning hours."
        )
    else:
        action = (
            "Maintain current crop care, avoid disruptive sprays during peak bloom, "
            "and monitor bee visits on clear mornings."
        )

    return (
        f"## Assessment for {crop_type}\n\n"
        f"Flowering is expected from **{flowering_start} to {flowering_end}**. "
        f"The current Pollination Suitability Index is **{psi_score}/100**, "
        f"which indicates **{risk_level}** risk for pollination.\n\n"
        f"**Recommended actions:** {action}\n\n"
        f"Weather snapshot: {weather.get('temperature', 'N/A')} C, "
        f"{weather.get('humidity', 'N/A')}% humidity, "
        f"{weather.get('rainfall', 'N/A')} mm rainfall, "
        f"{weather.get('wind_speed', 'N/A')} km/h wind.\n\n"
        "**Confidence:** Moderate. This MVP combines live or cached weather, "
        "seasonal pollen estimates, bee proxies, and baseline ML fallbacks."
    )
