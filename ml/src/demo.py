"""
demo.py
Generates synthetic but realistic-shaped temperature and NDVI data to test
the full pipeline end-to-end before wiring up real Earth Engine / NASA POWER
API pulls. Run: python demo.py
"""

import os
import numpy as np
import pandas as pd
from datetime import date, timedelta

from mismatch import predict_mismatch


def make_synthetic_temp_series(start_date: date, n_days: int, base_temp: float, amplitude: float):
    """Smooth seasonal warming trend + daily noise."""
    dates = [start_date + timedelta(days=i) for i in range(n_days)]
    t = np.arange(n_days)
    mean_temp = base_temp + amplitude * (t / n_days)  # gradual warming
    noise = np.random.normal(0, 1.5, n_days)
    t_max = mean_temp + 5 + noise
    t_min = mean_temp - 5 + noise
    return pd.DataFrame({"date": dates, "T2M_MAX": t_max, "T2M_MIN": t_min})


def make_synthetic_ndvi_series(start_date: date, n_days: int, green_up_day: int, senescence_day: int):
    """Double-logistic-shaped NDVI with noise and some missing (cloud-masked) days."""
    dates = [start_date + timedelta(days=i) for i in range(n_days)]
    t = np.arange(n_days)
    vmin, vmax = 0.15, 0.75
    k1, k2 = 0.15, 0.15
    green_up = 1 / (1 + np.exp(-k1 * (t - green_up_day)))
    senescence = 1 / (1 + np.exp(-k2 * (t - senescence_day)))
    ndvi = vmin + (vmax - vmin) * (green_up - senescence)
    ndvi += np.random.normal(0, 0.03, n_days)

    df = pd.DataFrame({"date": dates, "ndvi": ndvi})
    # simulate cloud-masked gaps: keep observations only every ~5 days
    df = df.iloc[::5].reset_index(drop=True)
    return df


if __name__ == "__main__":
    np.random.seed(42)

    print("=" * 70)
    print("SUNFLOWER demo — Maharashtra, Kharif season")
    print("=" * 70)
    sowing = date(2025, 6, 15)
    temp_df = make_synthetic_temp_series(sowing, n_days=120, base_temp=22, amplitude=6)
    ndvi_df = make_synthetic_ndvi_series(sowing, n_days=120, green_up_day=40, senescence_day=85)

    # Load real GBIF-derived activity data if you've run fetch_gbif_data.py
    # and process_gbif_data.py already. Falls back to literature proxy if not.
    gbif_path = "../data/processed/pollinator_monthly_activity.csv"
    gbif_activity_df = None
    if os.path.exists(gbif_path):
        gbif_activity_df = pd.read_csv(gbif_path)
        print(f"Loaded real GBIF activity data from {gbif_path}")
    else:
        print(f"No processed GBIF data found at {gbif_path} — using literature fallback.")

    result = predict_mismatch(
        crop="sunflower",
        region="Maharashtra",
        sowing_date=sowing,
        temp_df=temp_df,
        ndvi_df=ndvi_df,
        gbif_activity_df=gbif_activity_df,
    )
    for k, v in result.items():
        print(f"  {k}: {v}")

    print()
    print("=" * 70)
    print("MUSTARD demo — Rajasthan, Rabi season")
    print("=" * 70)
    sowing_m = date(2025, 10, 20)
    temp_df_m = make_synthetic_temp_series(sowing_m, n_days=120, base_temp=14, amplitude=4)
    ndvi_df_m = make_synthetic_ndvi_series(sowing_m, n_days=120, green_up_day=35, senescence_day=80)

    result_m = predict_mismatch(
        crop="mustard",
        region="Rajasthan",
        sowing_date=sowing_m,
        temp_df=temp_df_m,
        ndvi_df=ndvi_df_m,
    )
    for k, v in result_m.items():
        print(f"  {k}: {v}")
