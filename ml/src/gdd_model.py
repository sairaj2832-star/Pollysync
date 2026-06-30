"""
gdd_model.py
Growing Degree Day (GDD) accumulation and threshold-based flowering prediction.

This is a deterministic phenology model, not a trained ML model, but it is the
backbone signal that the NDVI model (ndvi_model.py) is used to cross-validate.
"""

from dataclasses import dataclass
from datetime import date, timedelta
import pandas as pd


# Crop-specific parameters sourced from published agronomy literature.
# See project README for citations. Mustard's t_base is flagged as a
# lower-confidence value (single well-documented study).
CROP_PARAMS = {
    "sunflower": {
        "t_base": 6.7,          # °C
        "gdd_to_flowering": 958,  # GDD units
        "gdd_to_maturity": 1725,
        "confidence": "high",
    },
    "mustard": {
        "t_base": 5.0,           # °C, lower confidence
        "gdd_to_flowering": None,  # not GDD-calibrated in literature
        "days_to_flowering": 47,   # average of 46-48 day range, IGP trials
        "gdd_to_maturity": 1700,
        "confidence": "low",
    },
}


@dataclass
class FloweringPrediction:
    crop: str
    predicted_flowering_date: date
    days_from_start: int
    cumulative_gdd_at_flowering: float
    method: str          # "gdd_threshold" or "days_after_sowing"
    confidence: str       # "high" or "low"


def daily_gdd(temp_max: float, temp_min: float, t_base: float) -> float:
    """Single-day GDD contribution. Clipped at zero (no negative GDD)."""
    avg_temp = (temp_max + temp_min) / 2
    return max(avg_temp - t_base, 0.0)


def build_gdd_series(temp_df: pd.DataFrame, crop: str) -> pd.DataFrame:
    """
    temp_df must have columns: 'date', 'T2M_MAX', 'T2M_MIN' (NASA POWER naming).
    Returns a copy with 'gdd' and 'cumulative_gdd' columns added.
    """
    if crop not in CROP_PARAMS:
        raise ValueError(f"Unknown crop: {crop}. Expected one of {list(CROP_PARAMS)}")

    t_base = CROP_PARAMS[crop]["t_base"]
    df = temp_df.copy().sort_values("date").reset_index(drop=True)
    df["gdd"] = df.apply(
        lambda r: daily_gdd(r["T2M_MAX"], r["T2M_MIN"], t_base), axis=1
    )
    df["cumulative_gdd"] = df["gdd"].cumsum()
    return df


def predict_flowering_date(temp_df: pd.DataFrame, crop: str, sowing_date: date) -> FloweringPrediction:
    """
    Predicts flowering date for a crop given a daily temperature series
    starting at sowing_date.

    Sunflower: uses GDD threshold crossing (thermally driven, literature-backed).
    Mustard: falls back to days-after-sowing average, since no GDD threshold
             for flowering is well established in literature. This is flagged
             as lower confidence in the output.
    """
    params = CROP_PARAMS[crop]

    if crop == "sunflower" or params.get("gdd_to_flowering") is not None:
        gdd_df = build_gdd_series(temp_df, crop)
        threshold = params["gdd_to_flowering"]
        hit = gdd_df[gdd_df["cumulative_gdd"] >= threshold]
        if hit.empty:
            # Not enough days of data to reach threshold yet
            last_row = gdd_df.iloc[-1]
            return FloweringPrediction(
                crop=crop,
                predicted_flowering_date=None,
                days_from_start=None,
                cumulative_gdd_at_flowering=last_row["cumulative_gdd"],
                method="gdd_threshold_not_reached",
                confidence=params["confidence"],
            )
        first_hit = hit.iloc[0]
        days_elapsed = (first_hit["date"] - sowing_date).days
        return FloweringPrediction(
            crop=crop,
            predicted_flowering_date=first_hit["date"],
            days_from_start=days_elapsed,
            cumulative_gdd_at_flowering=first_hit["cumulative_gdd"],
            method="gdd_threshold",
            confidence=params["confidence"],
        )
    else:
        # Mustard fallback: fixed days-after-sowing
        days = params["days_to_flowering"]
        flowering_date = sowing_date + timedelta(days=days)
        gdd_df = build_gdd_series(temp_df, crop)
        cum_gdd = gdd_df.iloc[min(days, len(gdd_df) - 1)]["cumulative_gdd"] if len(gdd_df) else None
        return FloweringPrediction(
            crop=crop,
            predicted_flowering_date=flowering_date,
            days_from_start=days,
            cumulative_gdd_at_flowering=cum_gdd,
            method="days_after_sowing",
            confidence=params["confidence"],
        )
