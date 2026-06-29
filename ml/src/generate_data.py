from pathlib import Path

import numpy as np
import pandas as pd

CROPS = ["Mustard", "Wheat", "Sunflower", "Rice", "Cotton"]
REGIONS = ["Nashik", "Punjab", "Haryana", "Gujarat", "Madhya Pradesh"]


def generate_flowering_data(n=300, seed=42):
    np.random.seed(seed)
    BASE_START = {"Mustard": 15, "Wheat": 45, "Sunflower": 60, "Rice": 90, "Cotton": 120}
    records = []
    for _ in range(n):
        crop = np.random.choice(CROPS)
        region = np.random.choice(REGIONS)
        base = BASE_START[crop]
        start = base + int(np.random.randint(-7, 8))
        end = start + int(np.random.randint(5, 10))
        temp = round(np.random.normal(25, 5), 1)
        humidity = round(np.random.normal(60, 10), 1)
        rainfall = round(np.random.exponential(10), 1)
        ndvi = round(np.random.normal(0.7, 0.1), 2)
        records.append({
            "crop": crop,
            "region": region,
            "start_doy": start,
            "end_doy": end,
            "temp_7d_mean": temp,
            "humidity": humidity,
            "rainfall_7d": rainfall,
            "ndvi": ndvi,
            "month": 1,
            "day_of_year": start - 5,
        })
    return pd.DataFrame(records)


def generate_psi_data(n=300, seed=42):
    np.random.seed(seed)
    records = []
    for _ in range(n):
        crop = np.random.choice(CROPS)
        temp = round(np.random.normal(28, 6), 1)
        humidity = round(np.random.normal(65, 15), 1)
        rainfall = round(np.random.exponential(15), 1)
        ndvi = round(np.random.normal(0.65, 0.15), 2)
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

    df_p = generate_psi_data()
    df_p.to_csv(DATA_DIR / "psi_data.csv", index=False)
    print(f"Created psi_data.csv with {len(df_p)} rows")
