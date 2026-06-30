"""
pollinator_proxy_v2.py
Predicts pollinator peak activity date using a two-tier approach:

  Tier 1 (preferred): GBIF-derived monthly activity index, if enough
                       occurrence records exist for the species+region
                       (see fetch_gbif_data.py + process_gbif_data.py).
  Tier 2 (fallback):  Literature-derived GDD threshold proxy (original
                       pollinator_proxy.py), used when GBIF data is too
                       sparse to trust.

This dual-tier design is the honest way to use real (but sparse) occurrence
data without pretending it's denser than it is.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional
import calendar
import pandas as pd

from pollinator_proxy import POLLINATOR_PROXY_TABLE, predict_pollinator_peak as _gdd_fallback_predict
from process_gbif_data import get_peak_month


@dataclass
class PollinatorPrediction:
    crop: str
    region: str
    species: Optional[str]
    predicted_peak_date: Optional[date]
    source: str          # "gbif_data" or "literature_proxy"
    confidence: str       # "medium" (gbif w/ enough records), "low" (fallback/sparse)
    note: str


def _month_to_approx_date(year: int, month: int) -> date:
    """Mid-month date as the representative 'peak' date for that month."""
    return date(year, month, 15)


def predict_pollinator_peak_v2(
    crop: str,
    region: str,
    sowing_date: date,
    temp_df: pd.DataFrame,
    gbif_activity_df: Optional[pd.DataFrame] = None,
    species_candidates: Optional[list] = None,
    min_records_threshold: int = 10,
) -> PollinatorPrediction:
    """
    crop, region, sowing_date, temp_df: same as original pollinator_proxy.
    gbif_activity_df: output of process_gbif_data.build_monthly_activity_index(),
                       or None to skip straight to the literature fallback.
    species_candidates: list of species names to check for this crop/region
                         (e.g. ["Apis cerana", "Apis dorsata"]). If None,
                         uses all species present in gbif_activity_df for
                         that region.
    """
    # --- Tier 1: try GBIF-derived data ---
    if gbif_activity_df is not None and not gbif_activity_df.empty:
        region_data = gbif_activity_df[gbif_activity_df["stateProvince"] == region]
        candidates = species_candidates or region_data["species"].unique().tolist()

        best = None
        for sp in candidates:
            peak = get_peak_month(gbif_activity_df, sp, region)
            if peak["confidence"] in ("medium",) and peak["peak_month"] is not None:
                if best is None or peak["total_records"] > best["total_records"]:
                    best = peak

        if best is not None:
            # Anchor the peak month to the flowering season's year
            target_year = sowing_date.year
            peak_date = _month_to_approx_date(target_year, best["peak_month"])
            # If peak month is earlier in calendar than sowing month, it likely
            # refers to next year's occurrence of that month (e.g. winter crop)
            if peak_date < sowing_date - timedelta(days=60):
                peak_date = _month_to_approx_date(target_year + 1, best["peak_month"])

            return PollinatorPrediction(
                crop=crop, region=region, species=best["species"],
                predicted_peak_date=peak_date,
                source="gbif_data",
                confidence="medium",
                note=(
                    f"Based on {best['total_records']} GBIF occurrence records "
                    f"of {best['species']} in {region}, peak activity in month "
                    f"{best['peak_month']}."
                ),
            )

    # --- Tier 2: fall back to literature GDD-threshold proxy ---
    fallback = _gdd_fallback_predict(temp_df, crop, region, sowing_date)
    return PollinatorPrediction(
        crop=crop, region=region, species=None,
        predicted_peak_date=fallback.predicted_peak_date,
        source="literature_proxy",
        confidence="low",
        note=(
            f"GBIF data insufficient for {region} (fewer than {min_records_threshold} "
            f"records per species). Falling back to literature-derived GDD threshold "
            f"proxy. {fallback.species_note}"
        ),
    )
