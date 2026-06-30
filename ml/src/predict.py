import json
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path

import joblib
import pandas as pd

from gdd_model import predict_flowering_date, CROP_PARAMS
from pollinator_proxy_v2 import predict_pollinator_peak_v2

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
    region: str = "Maharashtra"     # added: needed for pollinator proxy lookup
    sowing_date: str = None         # added: ISO date string, needed for GDD calc


@dataclass
class PredictionResult:
    flowering_start_doy: int
    flowering_end_doy: int
    psi_score: int
    risk_level: str
    gap_days: int = None            # added: pollination mismatch (new field)
    source: str = "baseline"        # added: "trained_model" or "baseline"


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
        "pollen_tree": features.pollen_level,
        "pollen_grass": features.pollen_level,
        "pollen_weed": features.pollen_level,
    }

def _baseline_flowering(features: PollinationFeatures) -> tuple[int, int]:
    """
    Real baseline: GDD-threshold model (sunflower/mustard) instead of the
    crude `base + (temp-25)*2` placeholder. Falls back to the old simple
    heuristic for crops outside this project's scope (wheat/rice/cotton),
    since those don't have a GDD model wired up here yet.
    """
    crop = features.crop_type.lower()

    if crop in CROP_PARAMS and features.sowing_date:
        sowing = date.fromisoformat(features.sowing_date)
        # Build a flat 1-row-per-day temp series using the 7-day mean as a
        # stand-in constant temperature. This is a simplification — once
        # real NASA POWER daily series are available, pass those instead
        # of synthesizing a flat series from one averaged feature.
        n_days = 150
        temp_df = pd.DataFrame({
            "date": [sowing + timedelta(days=i) for i in range(n_days)],
            "T2M_MAX": [features.temperature_c + 5] * n_days,
            "T2M_MIN": [features.temperature_c - 5] * n_days,
        })
        result = predict_flowering_date(temp_df, crop, sowing)
        if result.predicted_flowering_date:
            start_doy = result.predicted_flowering_date.timetuple().tm_yday
            return start_doy, start_doy + 7

    # Fallback for crops without a GDD model, or missing sowing_date
    base = {"mustard": 15, "wheat": 45, "sunflower": 60, "rice": 90, "cotton": 120}
    start = base.get(crop, 60)
    start += int(features.temperature_c - 25) * 2
    start = max(1, min(365, start))
    return start, start + 7


def _baseline_psi(features: PollinationFeatures) -> tuple[int, str, int]:
    """
    Real baseline: combines the existing PSI heuristic (temp/humidity/ndvi/
    bee_count/pollen scoring — kept as-is, it's a reasonable composite) with
    the actual GDD/pollinator-proxy mismatch gap as an additional signal.
    Large mismatch gaps now reduce the PSI score instead of being ignored.
    """
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

    gap_days = None
    crop = features.crop_type.lower()
    if crop in CROP_PARAMS and features.sowing_date:
        sowing = date.fromisoformat(features.sowing_date)
        n_days = 150
        temp_df = pd.DataFrame({
            "date": [sowing + timedelta(days=i) for i in range(n_days)],
            "T2M_MAX": [features.temperature_c + 5] * n_days,
            "T2M_MIN": [features.temperature_c - 5] * n_days,
        })
        flowering = predict_flowering_date(temp_df, crop, sowing)
        pollinator = predict_pollinator_peak_v2(
            crop=crop, region=features.region, sowing_date=sowing, temp_df=temp_df,
        )
        if flowering.predicted_flowering_date and pollinator.predicted_peak_date:
            gap_days = (pollinator.predicted_peak_date - flowering.predicted_flowering_date).days
            # Penalize the PSI score for large mismatches
            score -= min(abs(gap_days), 30)

    score = max(0, min(100, score))
    risk = "Low" if score >= 70 else "Medium" if score >= 40 else "High"
    return score, risk, gap_days


def predict(features: PollinationFeatures) -> PredictionResult:
    if flowering_model and psi_model:
        feature_dict = _build_feature_dict(features)
        df = pd.DataFrame([feature_dict])
        start_doy = int(flowering_model.predict(df)[0])
        end_doy = start_doy + 7
        psi = int(psi_model.predict(df)[0])
        psi = max(0, min(100, psi))
        risk = risk_model.predict(df)[0] if risk_model else "Medium"

        # Always compute gap_days/mismatch, even when using trained models,
        # since this is the core output of the project.
        gap_days = None
        if features.crop_type.lower() in CROP_PARAMS and features.sowing_date:
            sowing = date.fromisoformat(features.sowing_date)
            n_days = 150
            temp_df = pd.DataFrame({
                "date": [sowing + timedelta(days=i) for i in range(n_days)],
                "T2M_MAX": [features.temperature_c + 5] * n_days,
                "T2M_MIN": [features.temperature_c - 5] * n_days,
            })
            flowering = predict_flowering_date(temp_df, features.crop_type.lower(), sowing)
            pollinator = predict_pollinator_peak_v2(
                crop=features.crop_type.lower(), region=features.region,
                sowing_date=sowing, temp_df=temp_df,
            )
            if flowering.predicted_flowering_date and pollinator.predicted_peak_date:
                gap_days = (pollinator.predicted_peak_date - flowering.predicted_flowering_date).days

        return PredictionResult(
            flowering_start_doy=start_doy, flowering_end_doy=end_doy,
            psi_score=psi, risk_level=risk, gap_days=gap_days, source="trained_model",
        )

    start_doy, end_doy = _baseline_flowering(features)
    psi, risk, gap_days = _baseline_psi(features)

    return PredictionResult(
        flowering_start_doy=start_doy,
        flowering_end_doy=end_doy,
        psi_score=psi,
        risk_level=risk,
        gap_days=gap_days,
        source="baseline",
    )

def predict_from_dict(d: dict) -> dict:
    features = PollinationFeatures(**d)
    result = predict(features)
    return asdict(result)
