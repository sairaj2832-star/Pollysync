"""
generate_more_data.py
Generates large training dataset grounded in the GDD phenology model.
Flowering DOY is derived from actual temperature-driven GDD accumulation,
giving the ML model a real weather-to-flowering signal to learn.
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

from gdd_model import CROP_PARAMS, build_gdd_series

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

CROP_REGIONS = {
    "sunflower": {
        "regions": ["Maharashtra", "Karnataka", "Andhra Pradesh", "Telangana"],
        "sowing_month_range": (5, 7),
        "temp_base_range": (22, 32),
        "temp_amplitude": 6,
    },
    "mustard": {
        "regions": ["Rajasthan", "Madhya Pradesh", "Uttar Pradesh", "Haryana"],
        "sowing_month_range": (9, 11),
        "temp_base_range": (10, 22),
        "temp_amplitude": 4,
    },
}


def _simulate_temp_series(sowing, n_days, base_temp, amplitude):
    t = np.arange(n_days)
    noise = np.random.normal(0, 1.5, n_days)
    mean_temp = base_temp + amplitude * (t / n_days)
    return pd.DataFrame({
        "date": [sowing + timedelta(days=int(i)) for i in t],
        "T2M_MAX": mean_temp + 5 + noise,
        "T2M_MIN": mean_temp - 5 + noise,
    })


def generate_improved_dataset(n_per_crop=2000, seed=42):
    """Generate large dataset with GDD-grounded flowering DOY."""
    np.random.seed(seed)
    records = []

    for crop, cfg in CROP_REGIONS.items():
        for _ in range(n_per_crop):
            region = np.random.choice(cfg["regions"])
            sow_month = np.random.randint(*cfg["sowing_month_range"])
            sow_day = np.random.randint(1, 28)
            sowing = date(2024, sow_month, sow_day)
            base_temp = np.random.uniform(*cfg["temp_base_range"])

            temp_df = _simulate_temp_series(sowing, 150, base_temp, cfg["temp_amplitude"])
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
            end_doy = min(365, start_doy + 7 + np.random.randint(-2, 3))

            # Pre-flowering 7-day window weather
            window = temp_df[
                (temp_df["date"] > flowering_date - timedelta(days=7)) &
                (temp_df["date"] <= flowering_date)
            ]
            if not window.empty:
                avg_temp = ((window["T2M_MAX"] + window["T2M_MIN"]) / 2).mean()
            else:
                avg_temp = base_temp

            humidity = round(np.random.normal(60, 12), 1)
            rainfall = round(np.random.exponential(8), 1)
            wind_speed = round(np.random.normal(10, 3), 1)
            ndvi = round(np.random.normal(0.65, 0.12), 3)
            bee_richness = max(1, int(np.random.poisson(4)))
            bee_abundance = max(5, int(bee_richness * np.random.uniform(3, 8)))
            pollen = np.random.randint(1, 6)

            records.append({
                "crop": crop,
                "region": region,
                "start_doy": start_doy,
                "end_doy": end_doy,
                "temp_7d_mean": round(avg_temp, 1),
                "humidity": humidity,
                "rainfall_7d": rainfall,
                "wind_speed": wind_speed,
                "ndvi": ndvi,
                "month": sow_month,
                "day_of_year": sowing.timetuple().tm_yday,
                "bee_richness": bee_richness,
                "bee_count": bee_abundance,
                "pollen_tree": pollen,
                "pollen_grass": pollen,
                "pollen_weed": pollen,
            })

    return pd.DataFrame(records)


def generate_improved_psi_data(n_per_crop=2000, seed=42):
    """Generate PSI training data with richer scoring function."""
    np.random.seed(seed)
    records = []

    for crop, cfg in CROP_REGIONS.items():
        for _ in range(n_per_crop):
            region = np.random.choice(cfg["regions"])
            base_temp = np.random.uniform(*cfg["temp_base_range"])
            temp = round(base_temp + np.random.normal(5, 3), 1)
            humidity = round(np.random.normal(60, 12), 1)
            rainfall = round(np.random.exponential(12), 1)
            wind_speed = round(np.random.normal(10, 3), 1)
            ndvi = round(np.random.normal(0.65, 0.12), 2)
            bee_richness = max(1, int(np.random.poisson(4)))
            bee_abundance = max(5, int(bee_richness * np.random.uniform(3, 8)))
            pollen = np.random.randint(1, 6)

            # PSI scoring with interaction effects for richer learning
            score = 0

            # Temperature score (non-linear optimal range)
            if 20 <= temp <= 32:
                score += 25
            elif 15 <= temp <= 35:
                score += 15
            else:
                score += max(0, 10 - abs(temp - 25) * 0.5)

            # Humidity score
            if 50 <= humidity <= 80:
                score += 20
            elif 30 <= humidity <= 90:
                score += 10

            # NDVI × bee interaction (richer signal)
            ndvi_bee = ndvi * min(bee_richness, 5) / 5
            if ndvi > 0.6 and bee_richness >= 3:
                score += 25
            elif ndvi > 0.4 and bee_richness >= 2:
                score += 15
            elif ndvi_bee > 0.3:
                score += 10
            else:
                score += 5

            # Wind penalty (strong wind reduces pollination)
            if wind_speed > 20:
                score -= 10
            elif wind_speed > 15:
                score -= 5

            # Rainfall bonus (light rain is good, heavy is bad)
            if 2 <= rainfall <= 10:
                score += 5
            elif rainfall > 20:
                score -= 5

            # Pollen availability
            if pollen >= 3:
                score += 10
            elif pollen >= 2:
                score += 5

            # Abundance scaling
            abundance_factor = min(bee_abundance / 20, 1.5)
            score = int(score * abundance_factor)

            score = max(0, min(100, score + np.random.randint(-3, 4)))
            risk = "Low" if score >= 70 else "Medium" if score >= 40 else "High"

            records.append({
                "crop": crop,
                "region": region,
                "temp_7d_mean": temp,
                "humidity": humidity,
                "rainfall_7d": rainfall,
                "wind_speed": wind_speed,
                "ndvi": ndvi,
                "month": np.random.randint(*cfg["sowing_month_range"]),
                "day_of_year": np.random.randint(120, 340),
                "crop_mustard": 1 if crop == "mustard" else 0,
                "crop_wheat": 0,
                "crop_sunflower": 1 if crop == "sunflower" else 0,
                "crop_rice": 0,
                "crop_cotton": 0,
                "bee_richness": bee_richness,
                "bee_count": bee_abundance,
                "pollen_tree": pollen,
                "pollen_grass": pollen,
                "pollen_weed": pollen,
                "psi_score": score,
                "risk_level": risk,
            })

    return pd.DataFrame(records)


if __name__ == "__main__":
    print("Generating improved large training dataset...")

    df_f = generate_improved_dataset(2000)
    out_f = DATA_DIR / "flowering_data_large.csv"
    df_f.to_csv(out_f, index=False)
    print(f"Generated {len(df_f)} flowering rows -> {out_f}")
    print(f"  Crops: {df_f['crop'].value_counts().to_dict()}")
    print(f"  start_doy range: {df_f['start_doy'].min()} - {df_f['start_doy'].max()}")
    print(f"  temp_7d_mean range: {df_f['temp_7d_mean'].min():.1f} - {df_f['temp_7d_mean'].max():.1f}")

    df_p = generate_improved_psi_data(2000)
    out_p = DATA_DIR / "psi_data.csv"
    df_p.to_csv(out_p, index=False)
    print(f"Generated {len(df_p)} PSI rows -> {out_p}")
    print(f"  psi_score range: {df_p['psi_score'].min()} - {df_p['psi_score'].max()}")
    print(f"  risk levels: {df_p['risk_level'].value_counts().to_dict()}")
