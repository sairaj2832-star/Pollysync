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

# Maharashtra-specific models
flowering_model_mh = None
flowering_scaler_mh = None
psi_model_mh = None
psi_scaler_mh = None
risk_model_mh = None
risk_scaler_mh = None

# Maharashtra bounding box (approximate)
MAHARASHTRA_BBOX = {"lat_min": 15.5, "lat_max": 22.0, "lon_min": 72.5, "lon_max": 80.5}


def _load_models():
    global flowering_model, flowering_scaler, psi_model, psi_scaler, risk_model, risk_scaler
    global flowering_model_mh, flowering_scaler_mh, psi_model_mh, psi_scaler_mh, risk_model_mh, risk_scaler_mh
    try:
        import joblib
        # General models
        for name in ("flowering", "psi", "risk"):
            model_path = MODELS_DIR / f"{name}_model.pkl"
            scaler_path = MODELS_DIR / f"{name}_scaler.pkl"
            if model_path.exists():
                globals()[f"{name}_model"] = joblib.load(str(model_path))
            if scaler_path.exists():
                globals()[f"{name}_scaler"] = joblib.load(str(scaler_path))
        # MH-specific models
        for name in ("flowering", "psi", "risk"):
            model_path = MODELS_DIR / f"{name}_model_mh.pkl"
            scaler_path = MODELS_DIR / f"{name}_scaler_mh.pkl"
            if model_path.exists():
                globals()[f"{name}_model_mh"] = joblib.load(str(model_path))
            if scaler_path.exists():
                globals()[f"{name}_scaler_mh"] = joblib.load(str(scaler_path))
    except Exception:
        pass


_load_models()


def _is_in_maharashtra(lat: float, lon: float) -> bool:
    return (
        MAHARASHTRA_BBOX["lat_min"] <= lat <= MAHARASHTRA_BBOX["lat_max"]
        and MAHARASHTRA_BBOX["lon_min"] <= lon <= MAHARASHTRA_BBOX["lon_max"]
    )


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


def _prepare_features_for_model(features: dict, model) -> dict:
    """Augment feature dict with zone features expected by MH model."""
    if hasattr(model, "feature_names_in_"):
        try:
            expected = list(model.feature_names_in_)
        except Exception:
            expected = []
    else:
        expected = []

    if not expected:
        return features

    # Add any zone/elevation features if missing
    augmented = dict(features)
    zone_defaults = {
        "zone_western_ghats": 0, "zone_scarce_rainfall": 0,
        "zone_marathwada": 0, "zone_vidarbha": 0,
        "zone_konkan": 0, "zone_khandesh": 0,
        "elevation_m": 500,
    }
    for col, val in zone_defaults.items():
        if col in expected and col not in augmented:
            augmented[col] = val

    # Add engineered features if expected
    eng_defaults = {
        "temp_humidity": 0, "temp_ndvi": 0, "humidity_rainfall": 0,
        "temp_sq": 0, "ndvi_sq": 0, "bee_total": 0, "temp_wind": 0,
    }
    if "temp_humidity" in expected:
        augmented["temp_humidity"] = (
            augmented.get("temp_7d_mean", 25) * augmented.get("humidity", 60) / 100
        )
        augmented["temp_sq"] = augmented.get("temp_7d_mean", 25) ** 2
        augmented["ndvi_sq"] = augmented.get("ndvi", 0.5) ** 2
        augmented["bee_total"] = (
            augmented.get("bee_richness", 0) * augmented.get("bee_count", 15)
        )
        augmented["temp_wind"] = (
            augmented.get("temp_7d_mean", 25) * augmented.get("wind_speed", 10)
        )
        if "temp_ndvi" in expected:
            augmented["temp_ndvi"] = (
                augmented.get("temp_7d_mean", 25) * augmented.get("ndvi", 0.5)
            )
        if "humidity_rainfall" in expected:
            augmented["humidity_rainfall"] = (
                augmented.get("humidity", 60) * augmented.get("rainfall_7d", 5) / 100
            )

    return augmented


async def run_prediction(farm: Farm, db: Session, region: str = "auto") -> Prediction:
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

    # Determine if we should use MH model
    use_mh = False
    if region == "maharashtra":
        use_mh = True
    elif region == "auto":
        use_mh = _is_in_maharashtra(farm.location_lat, farm.location_lng)

    # Select models
    if use_mh:
        f_model = flowering_model_mh
        f_scaler = flowering_scaler_mh
        p_model = psi_model_mh
        p_scaler = psi_scaler_mh
        r_model = risk_model_mh
        r_scaler = risk_scaler_mh
        model_source = "maharashtra_v2"
        data_confidence = "high (1545 real MH rows)"
    else:
        f_model = flowering_model
        f_scaler = flowering_scaler
        p_model = psi_model
        p_scaler = psi_scaler
        r_model = risk_model
        r_scaler = risk_scaler
        model_source = "general_v1"
        data_confidence = "standard"

    models_loaded = all([f_model, f_scaler, p_model, p_scaler, r_model, r_scaler])

    if models_loaded:
        import pandas as pd
        from app.services.feature_engineering import CROP_ENCODER

        # Augment features for the specific model
        augmented = _prepare_features_for_model(features, f_model)

        expected_cols = sorted(augmented.keys())
        df = pd.DataFrame([augmented])[expected_cols]

        X_scaled = f_scaler.transform(df)
        start_doy = int(round(f_model.predict(X_scaled)[0]))
        start_doy = max(1, min(365, start_doy))
        confidence = 0.92 if use_mh else 0.87

        psi = int(round(p_model.predict(p_scaler.transform(df))[0]))
        psi = max(0, min(100, psi))

        risk_raw = r_model.predict(r_scaler.transform(df))[0]
        if hasattr(r_model, "_label_encoder"):
            risk = r_model._label_encoder.inverse_transform([risk_raw])[0]
        else:
            risk = risk_raw
    else:
        start_doy, confidence = _predict_flowering_baseline(features)
        psi, risk = _predict_psi_baseline(features)
        model_source = "baseline"
        data_confidence = "low"

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
        model_source=model_source,
        data_confidence=data_confidence,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction
