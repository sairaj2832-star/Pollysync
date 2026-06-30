"""
pollinator_proxy.py
Since live pollinator occurrence data (GBIF/iNaturalist) is too sparse in
India to use directly, this module encodes published species-activity
temperature/GDD thresholds as a regional proxy for pollinator peak activity.

This is intentionally simple and literature-driven rather than learned from
data — and the project openly states this as a limitation.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional
import pandas as pd

from gdd_model import daily_gdd


# Regional proxy table: pollinator activity threshold by crop + Indian state/region.
# t_base/threshold values are illustrative placeholders pulled from general bee
# activity literature (most bees become active once daily mean temp exceeds
# ~10-13°C and accelerates with accumulated warmth). Replace with
# region-specific published values as you source them — flagged in README.
POLLINATOR_PROXY_TABLE = {
    "sunflower": {
        "default": {"t_base": 10.0, "gdd_threshold": 250, "species_note": "Apis spp., wild bees"},
        "Karnataka": {"t_base": 10.0, "gdd_threshold": 230, "species_note": "Apis cerana indica"},
        "Maharashtra": {"t_base": 10.0, "gdd_threshold": 240, "species_note": "Apis cerana indica"},
        "Andhra Pradesh": {"t_base": 10.5, "gdd_threshold": 220, "species_note": "Apis dorsata, wild bees"},
    },
    "mustard": {
        "default": {"t_base": 8.0, "gdd_threshold": 300, "species_note": "Apis spp., good bee plant"},
        "Rajasthan": {"t_base": 8.0, "gdd_threshold": 310, "species_note": "Apis mellifera (managed), wild bees"},
        "Madhya Pradesh": {"t_base": 8.0, "gdd_threshold": 290, "species_note": "Apis cerana indica"},
        "Uttar Pradesh": {"t_base": 7.5, "gdd_threshold": 280, "species_note": "Apis cerana indica"},
    },
}


@dataclass
class PollinatorPrediction:
    crop: str
    region: str
    predicted_peak_date: Optional[date]
    days_from_start: Optional[int]
    cumulative_gdd_at_peak: Optional[float]
    species_note: str
    confidence: str = "low"  # always low — this is a proxy, not measured data


def predict_pollinator_peak(temp_df: pd.DataFrame, crop: str, region: str, start_date: date) -> PollinatorPrediction:
    """
    temp_df: columns 'date', 'T2M_MAX', 'T2M_MIN' starting at start_date.
    region: Indian state name matching POLLINATOR_PROXY_TABLE, falls back to 'default'.
    """
    if crop not in POLLINATOR_PROXY_TABLE:
        raise ValueError(f"No pollinator proxy data for crop: {crop}")

    region_table = POLLINATOR_PROXY_TABLE[crop]
    params = region_table.get(region, region_table["default"])

    df = temp_df.copy().sort_values("date").reset_index(drop=True)
    df["pollinator_gdd"] = df.apply(
        lambda r: daily_gdd(r["T2M_MAX"], r["T2M_MIN"], params["t_base"]), axis=1
    )
    df["cumulative_pollinator_gdd"] = df["pollinator_gdd"].cumsum()

    threshold = params["gdd_threshold"]
    hit = df[df["cumulative_pollinator_gdd"] >= threshold]

    if hit.empty:
        return PollinatorPrediction(
            crop=crop, region=region, predicted_peak_date=None,
            days_from_start=None, cumulative_gdd_at_peak=df.iloc[-1]["cumulative_pollinator_gdd"] if len(df) else None,
            species_note=params["species_note"],
        )

    first_hit = hit.iloc[0]
    days_elapsed = (first_hit["date"] - start_date).days
    return PollinatorPrediction(
        crop=crop, region=region,
        predicted_peak_date=first_hit["date"],
        days_from_start=days_elapsed,
        cumulative_gdd_at_peak=first_hit["cumulative_pollinator_gdd"],
        species_note=params["species_note"],
    )
