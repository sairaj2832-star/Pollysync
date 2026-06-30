"""
generate_data.py (v2)
Generates synthetic training data SPECIFIC to sunflower and mustard, in
their real growing regions and seasons, anchored to gdd_model.py's
CROP_PARAMS so synthetic flowering windows match the literature-derived
GDD thresholds rather than arbitrary placeholder numbers.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from datetime import date, timedelta

from gdd_model import CROP_PARAMS, build_gdd_series

# Only the two crops this project actually covers, in their real belts
CROP_REGIONS = {
    "sunflower": {
        "regions": ["Maharashtra", "Karnataka", "Andhra Pradesh"],
        "sowing_month_range": (5, 7),     # Kharif: May-July sowing
        "base_temp_range": (24, 30),      # warm season
    },
    "mustard": {
        "regions": ["Rajasthan", "Madhya Pradesh", "Uttar Pradesh"],
        "sowing_month_range": (9, 11),    # Rabi: Sept-Nov sowing
        "base_temp_range": (12, 20),      # cool season
    },
}


def _simulate_temp_series(sowing: date, n_days: int, base_temp: float):
    t = np.arange(n_days)
    noise = np.random.normal(0, 1.5, n_days)
    mean_temp = base_temp + 3 * (t / n_days)
    return pd.DataFrame({
        "date": [sowing + timedelta(days=int(i)) for i in t],
        "T2M_MAX": mean_temp + 5 + noise,
        "T2M_MIN": mean_temp - 5 + noise,
    })


def generate_flowering_data(n_per_crop=200, seed=42):
    """
    For each crop+region, simulates a temperature series from a random
    sowing date in-season, runs it through the REAL GDD model, and records
    the actual day-of-year the GDD threshold (or days-after-sowing rule)
    was hit. This makes start_doy a genuine function of temperature inputs
    rather than an arbitrary random offset.
    """
    np.random.seed(seed)
    records = []

    for crop, cfg in CROP_REGIONS.items():
        for _ in range(n_per_crop):
            region = np.random.choice(cfg["regions"])
            sow_month = np.random.randint(*cfg["sowing_month_range"])
            sow_day = np.random.randint(1, 28)
            sowing = date(2024, sow_month, sow_day)
            base_temp = np.random.uniform(*cfg["base_temp_range"])

            temp_df = _simulate_temp_series(sowing, n_days=150, base_temp=base_temp)
            gdd_df = build_gdd_series(temp_df, crop)

            params = CROP_PARAMS[crop]
            if params.get("gdd_to_flowering") is not None:
                hit = gdd_df[gdd_df["cumulative_gdd"] >= params["gdd_to_flowering"]]
                if hit.empty:
                    continue
                flowering_date = hit.iloc[0]["date"]
            else:
                flowering_date = sowing + timedelta(days=params["days_to_flowering"])

            start_doy = flowering_date.timetuple().tm_yday
            end_doy = start_doy + 7

            humidity = round(np.random.normal(60, 10), 1)
            rainfall = round(np.random.exponential(8), 1)
            ndvi = round(np.random.normal(0.65, 0.1), 2)

            records.append({
                "crop": crop,
                "region": region,
                "start_doy": start_doy,
                "end_doy": end_doy,
                "temp_7d_mean": round(base_temp, 1),
                "humidity": humidity,
                "rainfall_7d": rainfall,
                "ndvi": ndvi,
                "month": sow_month,
                "day_of_year": sowing.timetuple().tm_yday,
            })

    return pd.DataFrame(records)


def generate_psi_data(n_per_crop=200, seed=42):
    """
    PSI = Pollination Suitability Index. Same crop+region scoping as above,
    but scores environment quality for pollination rather than predicting
    a flowering date.
    """
    np.random.seed(seed)
    records = []

    for crop, cfg in CROP_REGIONS.items():
        for _ in range(n_per_crop):
            region = np.random.choice(cfg["regions"])
            base_temp = np.random.uniform(*cfg["base_temp_range"])
            temp = round(base_temp + np.random.normal(5, 3), 1)
            humidity = round(np.random.normal(60, 12), 1)
            rainfall = round(np.random.exponential(12), 1)
            ndvi = round(np.random.normal(0.65, 0.12), 2)
            bee_count = int(np.random.poisson(5))
            pollen = int(np.random.randint(1, 6))

            score = 0
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
            if pollen >= 3:
                score += 15
            elif pollen >= 2:
                score += 8

            score = max(0, min(100, score + np.random.randint(-5, 6)))
            risk = "Low" if score >= 70 else "Medium" if score >= 40 else "High"

            records.append({
                "crop": crop,
                "region": region,
                "temp_7d_mean": temp,
                "humidity": humidity,
                "rainfall_7d": rainfall,
                "ndvi": ndvi,
                "bee_richness": bee_count,
                "pollen_level": pollen,
                "psi_score": score,
                "risk_level": risk,
            })

    return pd.DataFrame(records)


if __name__ == "__main__":
    DATA_DIR = Path(__file__).resolve().parent.parent / "data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    df_f = generate_flowering_data()
    df_f.to_csv(DATA_DIR / "flowering_data.csv", index=False)
    print(f"Created flowering_data.csv with {len(df_f)} rows")
    print(df_f["crop"].value_counts())
    print(df_f.groupby("crop")["region"].value_counts())

    df_p = generate_psi_data()
    df_p.to_csv(DATA_DIR / "psi_data.csv", index=False)
    print(f"\nCreated psi_data.csv with {len(df_p)} rows")