import json
from dataclasses import dataclass, asdict
from pathlib import Path

import joblib
import pandas as pd

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"


@dataclass(frozen=True)
class PollinationFeatures:
    temperature_c: float
    humidity_percent: float
    rainfall_mm: float
    wind_speed_kmh: float
    ndvi: float
    bee_count: int
    pollen_level: int
    crop_type: str
    month: int
    day_of_year: int


@dataclass
class PredictionResult:
    flowering_start_doy: int
    flowering_end_doy: int
    psi_score: int
    risk_level: str


def _load_model(name: str):
    path = MODELS_DIR / name
    if path.exists():
        return joblib.load(str(path))
    return None


flowering_model = _load_model("flowering_model.pkl")
psi_model = _load_model("psi_model.pkl")
risk_model = _load_model("risk_model.pkl")


def _build_feature_dict(features: PollinationFeatures) -> dict:
    crop = features.crop_type.lower()
    return {
        "temp_7d_mean": features.temperature_c,
        "humidity": features.humidity_percent,
        "rainfall_7d": features.rainfall_mm,
        "wind_speed": features.wind_speed_kmh,
        "ndvi": features.ndvi,
        "day_of_year": features.day_of_year,
        "month": features.month,
        "crop_mustard": 1 if crop == "mustard" else 0,
        "crop_wheat": 1 if crop == "wheat" else 0,
        "crop_sunflower": 1 if crop == "sunflower" else 0,
        "crop_rice": 1 if crop == "rice" else 0,
        "crop_cotton": 1 if crop == "cotton" else 0,
        "bee_richness": features.bee_count,
        "pollen_tree": 2,
        "pollen_grass": 2,
        "pollen_weed": 2,
    }


def _baseline_flowering(features: PollinationFeatures) -> tuple[int, int]:
    base = {
        "mustard": 15, "wheat": 45, "sunflower": 60, "rice": 90, "cotton": 120,
    }
    start = base.get(features.crop_type.lower(), 60)
    start += int(features.temperature_c - 25) * 2
    start = max(1, min(365, start))
    return start, start + 7


def _baseline_psi(features: PollinationFeatures) -> tuple[int, str]:
    score = 0
    if 20 <= features.temperature_c <= 32:
        score += 25
    elif 15 <= features.temperature_c <= 35:
        score += 15
    if 50 <= features.humidity_percent <= 80:
        score += 20
    elif 30 <= features.humidity_percent <= 90:
        score += 10
    if features.ndvi > 0.6:
        score += 20
    elif features.ndvi > 0.4:
        score += 10
    if features.bee_count >= 3:
        score += 15
    elif features.bee_count >= 1:
        score += 8
    if features.pollen_level >= 3:
        score += 15
    elif features.pollen_level >= 2:
        score += 8
    score = max(0, min(100, score))
    risk = "Low" if score >= 70 else "Medium" if score >= 40 else "High"
    return score, risk


def predict(features: PollinationFeatures) -> PredictionResult:
    if flowering_model and psi_model:
        feature_dict = _build_feature_dict(features)
        df = pd.DataFrame([feature_dict])
        start_doy = int(flowering_model.predict(df)[0])
        end_doy = start_doy + 7
        psi = int(psi_model.predict(df)[0])
        psi = max(0, min(100, psi))
        risk = risk_model.predict(df)[0] if risk_model else "Medium"
    else:
        start_doy, end_doy = _baseline_flowering(features)
        psi, risk = _baseline_psi(features)

    return PredictionResult(
        flowering_start_doy=start_doy,
        flowering_end_doy=end_doy,
        psi_score=psi,
        risk_level=risk,
    )


def predict_from_dict(d: dict) -> dict:
    features = PollinationFeatures(**d)
    result = predict(features)
    return asdict(result)
