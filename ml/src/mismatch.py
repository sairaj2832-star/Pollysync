"""
mismatch.py
The single entry point backend should call. Combines the GDD flowering model,
the NDVI curve-fit cross-check, and the pollinator proxy model into one
mismatch prediction.

Contract for backend integration:

    from mismatch import predict_mismatch

    result = predict_mismatch(
        crop="sunflower",            # "sunflower" or "mustard"
        region="Karnataka",          # Indian state, for pollinator proxy lookup
        sowing_date=date(2025, 6, 15),
        temp_df=temp_df,             # DataFrame: date, T2M_MAX, T2M_MIN (NASA POWER)
        ndvi_df=ndvi_df,             # DataFrame: date, ndvi (Earth Engine export), optional
    )

    result is a dict, JSON-serializable (see to_dict()), ready to return
    straight from a FastAPI endpoint.
"""

from dataclasses import dataclass, asdict
from datetime import date
from typing import Optional
import pandas as pd

from gdd_model import predict_flowering_date, CROP_PARAMS
from ndvi_model import fit_ndvi_curve
from pollinator_proxy_v2 import predict_pollinator_peak_v2


@dataclass
class MismatchResult:
    crop: str
    region: str
    sowing_date: str
    predicted_flowering_date: Optional[str]
    flowering_method: str
    flowering_confidence: str
    ndvi_cross_check_date: Optional[str]
    ndvi_fit_quality: Optional[float]
    ndvi_note: str
    predicted_pollinator_peak_date: Optional[str]
    pollinator_species_note: str
    gap_days: Optional[int]
    alert: str
    overall_confidence: str

    def to_dict(self):
        return asdict(self)


def _safe_iso(d):
    return d.isoformat() if d is not None else None


def predict_mismatch(
    crop: str,
    region: str,
    sowing_date: date,
    temp_df: pd.DataFrame,
    ndvi_df: Optional[pd.DataFrame] = None,
    gbif_activity_df: Optional[pd.DataFrame] = None,
) -> dict:
    if crop not in CROP_PARAMS:
        raise ValueError(f"Unknown crop '{crop}'. Must be 'sunflower' or 'mustard'.")

    # 1. GDD-based flowering prediction (primary signal)
    flowering = predict_flowering_date(temp_df, crop, sowing_date)

    # 2. NDVI cross-check (secondary, independent signal) — optional
    ndvi_result = None
    ndvi_note = "No NDVI data supplied; skipped cross-check."
    if ndvi_df is not None and len(ndvi_df) > 0:
        ndvi_result = fit_ndvi_curve(ndvi_df)
        ndvi_note = ndvi_result.note

    # 3. Pollinator prediction (GBIF data preferred, literature fallback)
    pollinator = predict_pollinator_peak_v2(
        crop=crop, region=region, sowing_date=sowing_date,
        temp_df=temp_df, gbif_activity_df=gbif_activity_df,
    )

    # 4. Mismatch gap
    gap_days = None
    alert = "Insufficient data to compute mismatch."
    if flowering.predicted_flowering_date and pollinator.predicted_peak_date:
        gap_days = (pollinator.predicted_peak_date - flowering.predicted_flowering_date).days
        if gap_days > 5:
            alert = (
                f"Pollinators are predicted to peak {gap_days} days AFTER flowering. "
                f"Risk of poor pollination — consider early-blooming companion plants "
                f"or supplemental pollination."
            )
        elif gap_days < -5:
            alert = (
                f"Pollinators are predicted to peak {abs(gap_days)} days BEFORE flowering. "
                f"Risk of missed pollination window."
            )
        else:
            alert = "Flowering and pollinator activity are well-aligned (within 5 days)."

    # 5. Overall confidence: weakest link wins
    overall_confidence = "high" if flowering.confidence == "high" else "low"
    if pollinator.confidence == "low":
        overall_confidence = "low"  # pollinator side is always a proxy

    result = MismatchResult(
        crop=crop,
        region=region,
        sowing_date=_safe_iso(sowing_date),
        predicted_flowering_date=_safe_iso(flowering.predicted_flowering_date),
        flowering_method=flowering.method,
        flowering_confidence=flowering.confidence,
        ndvi_cross_check_date=_safe_iso(ndvi_result.inflection_date) if ndvi_result and ndvi_result.success else None,
        ndvi_fit_quality=ndvi_result.r_squared if ndvi_result and ndvi_result.success else None,
        ndvi_note=ndvi_note,
        predicted_pollinator_peak_date=_safe_iso(pollinator.predicted_peak_date),
        pollinator_species_note=pollinator.note,
        gap_days=gap_days,
        alert=alert,
        overall_confidence=overall_confidence,
    )

    return result.to_dict()
