"""
ndvi_model.py
Fits a double-logistic curve to a satellite NDVI time series to estimate the
date of peak vegetative growth / inflection, used as an independent
cross-check against the GDD-based flowering prediction.

This is the genuine "ML/stats" component of the pipeline: curve fitting via
non-linear least squares (scipy.optimize.curve_fit).
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


def double_logistic(t, vmin, vmax, t1, k1, t2, k2):
    """
    Standard double-logistic phenology curve:
    rises from vmin to vmax around t1 (green-up), stays near vmax,
    then declines back toward vmin around t2 (senescence).
    t is day-of-year (or days since first observation).
    """
    green_up = 1 / (1 + np.exp(-k1 * (t - t1)))
    senescence = 1 / (1 + np.exp(-k2 * (t - t2)))
    return vmin + (vmax - vmin) * (green_up - senescence)


@dataclass
class NDVIFitResult:
    success: bool
    inflection_day: Optional[int]       # days since series start, green-up midpoint
    inflection_date: Optional[date]
    peak_ndvi: Optional[float]
    fit_params: Optional[dict]
    r_squared: Optional[float]
    note: str = ""


def fit_ndvi_curve(ndvi_df: pd.DataFrame) -> NDVIFitResult:
    """
    ndvi_df must have columns: 'date' (datetime/date) and 'ndvi' (float, 0-1).
    Drops NaNs (cloud-masked observations) before fitting.

    Returns the green-up inflection point (t1), which is used as a proxy
    flowering-window signal: rapid NDVI rise typically precedes/coincides
    with flowering in row crops.
    """
    df = ndvi_df.dropna(subset=["ndvi"]).copy().sort_values("date").reset_index(drop=True)

    if len(df) < 6:
        return NDVIFitResult(
            success=False, inflection_day=None, inflection_date=None,
            peak_ndvi=None, fit_params=None, r_squared=None,
            note="Not enough cloud-free NDVI observations to fit a curve (need >=6).",
        )

    start_date = df["date"].iloc[0]
    t = np.array([(d - start_date).days for d in df["date"]], dtype=float)
    y = df["ndvi"].values.astype(float)

    vmin_guess = float(np.percentile(y, 10))
    vmax_guess = float(np.percentile(y, 90))
    t_mid = float(t.mean())
    span = max(t.max() - t.min(), 1)

    p0 = [vmin_guess, vmax_guess, t_mid - span / 4, 0.2, t_mid + span / 4, 0.2]
    bounds = (
        [-1, -1, t.min(), 0.001, t.min(), 0.001],
        [1, 1, t.max(), 2.0, t.max(), 2.0],
    )

    try:
        popt, _ = curve_fit(double_logistic, t, y, p0=p0, bounds=bounds, maxfev=10000)
    except RuntimeError as e:
        return NDVIFitResult(
            success=False, inflection_day=None, inflection_date=None,
            peak_ndvi=None, fit_params=None, r_squared=None,
            note=f"Curve fit failed to converge: {e}",
        )

    vmin, vmax, t1, k1, t2, k2 = popt
    y_pred = double_logistic(t, *popt)
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    inflection_day = int(round(t1))
    inflection_date = start_date + timedelta(days=inflection_day)

    return NDVIFitResult(
        success=True,
        inflection_day=inflection_day,
        inflection_date=inflection_date,
        peak_ndvi=float(vmax),
        fit_params={
            "vmin": float(vmin), "vmax": float(vmax),
            "t1_green_up": float(t1), "k1": float(k1),
            "t2_senescence": float(t2), "k2": float(k2),
        },
        r_squared=float(r_squared),
        note="Fit converged." if r_squared > 0.6 else "Fit converged but R^2 is low; treat with caution.",
    )
