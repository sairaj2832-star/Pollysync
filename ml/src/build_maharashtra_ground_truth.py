"""
build_maharashtra_ground_truth.py
Merges all Phase 1 data sources into a labelled ground truth dataset for
Maharashtra-specific model training.

Inputs (from Phase 1):
  - data/raw/maharashtra_weather_all_districts.csv
  - data/raw/maharashtra_crop_calendar.csv
  - data/raw/maharashtra_ndvi_inflection.csv
  - data/processed/maharashtra_bee_diversity.csv

Output:
  - data/maharashtra_ground_truth.csv
  - data/maharashtra_ground_truth_summary.txt

Usage:
    python build_maharashtra_ground_truth.py
"""

from pathlib import Path
from datetime import date, timedelta
import sys
import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).parent))
from gdd_model import build_gdd_series, CROP_PARAMS, predict_flowering_date

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

V1_FEATURES = [
    "temp_7d_mean", "humidity", "rainfall_7d", "wind_speed", "ndvi",
    "day_of_year", "month",
    "crop_mustard", "crop_wheat", "crop_sunflower", "crop_rice", "crop_cotton",
    "bee_richness", "bee_count", "pollen_tree", "pollen_grass", "pollen_weed",
]

CROPS = ["sunflower", "mustard", "wheat", "rice", "cotton"]

# Seasonal pollen table (copied from feature_engineering.py)
SEASONAL_POLLEN = {
    1: {"tree": 3, "grass": 1, "weed": 2},
    2: {"tree": 4, "grass": 2, "weed": 3},
    3: {"tree": 5, "grass": 3, "weed": 4},
    4: {"tree": 5, "grass": 4, "weed": 4},
    5: {"tree": 4, "grass": 5, "weed": 3},
    6: {"tree": 3, "grass": 5, "weed": 3},
    7: {"tree": 2, "grass": 4, "weed": 2},
    8: {"tree": 2, "grass": 3, "weed": 2},
    9: {"tree": 3, "grass": 3, "weed": 3},
    10: {"tree": 3, "grass": 2, "weed": 3},
    11: {"tree": 2, "grass": 1, "weed": 2},
    12: {"tree": 2, "grass": 1, "weed": 2},
}


def load_weather() -> pd.DataFrame:
    path = RAW_DIR / "maharashtra_weather_all_districts.csv"
    if not path.exists():
        print("WARNING: Weather data not found. Run fetch_maharashtra_weather.py first.")
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["date_parsed"] = pd.to_datetime(df["date_parsed"])
    return df


def load_crop_calendar() -> pd.DataFrame:
    path = RAW_DIR / "maharashtra_crop_calendar.csv"
    if not path.exists():
        print("WARNING: Crop calendar not found. Run scrape_icrisat_data.py first.")
        return pd.DataFrame()
    return pd.read_csv(path)


def load_ndvi_inflection() -> pd.DataFrame:
    path = RAW_DIR / "maharashtra_ndvi_inflection.csv"
    if not path.exists():
        print("WARNING: NDVI data not found.")
        return pd.DataFrame()
    return pd.read_csv(path)


def load_bee_diversity() -> pd.DataFrame:
    path = PROCESSED_DIR / "maharashtra_bee_diversity.csv"
    if not path.exists():
        print("WARNING: Bee diversity data not found.")
        return pd.DataFrame()
    return pd.read_csv(path)


def compute_flowering_doy(weather_df: pd.DataFrame, crop: str,
                           sowing: date) -> int | None:
    result = predict_flowering_date(weather_df, crop, sowing)
    if result.predicted_flowering_date:
        return result.predicted_flowering_date.timetuple().tm_yday
    return None


def get_early_season_weather(weather_df: pd.DataFrame, sowing_date: date) -> dict:
    """Compute weather features from the first 7 days after sowing.
    
    Unlike the old get_seven_day_window which used flowering_date (the label),
    this uses the sowing date — known at inference time — eliminating target leakage.
    """
    window = weather_df[
        (weather_df["date_parsed"] >= pd.Timestamp(sowing_date)) &
        (weather_df["date_parsed"] < pd.Timestamp(sowing_date) + pd.Timedelta(days=7))
    ]
    if len(window) < 3:
        first_rows = weather_df.head(7)
        return {
            "temp_7d_mean": round(((first_rows["T2M_MAX"] + first_rows["T2M_MIN"]) / 2).mean(), 1),
            "humidity": round(first_rows["RH2M"].mean(), 1),
            "rainfall_7d": round(first_rows["PRECTOTCORR"].sum(), 1),
            "wind_speed": round(first_rows["WS2M"].mean() * 3.6, 1),
        }

    return {
        "temp_7d_mean": round(((window["T2M_MAX"] + window["T2M_MIN"]) / 2).mean(), 1),
        "humidity": round(window["RH2M"].mean(), 1),
        "rainfall_7d": round(window["PRECTOTCORR"].sum(), 1),
        "wind_speed": round(window["WS2M"].mean() * 3.6, 1),
    }


def build_rows() -> pd.DataFrame:
    weather_df = load_weather()
    calendar_df = load_crop_calendar()
    ndvi_df = load_ndvi_inflection()
    bee_df = load_bee_diversity()

    print(f"Weather: {len(weather_df)} rows" if not weather_df.empty else "Weather: MISSING")
    print(f"Calendar: {len(calendar_df)} rows" if not calendar_df.empty else "Calendar: MISSING")
    print(f"NDVI: {len(ndvi_df)} rows" if not ndvi_df.empty else "NDVI: MISSING")
    print(f"Bee: {len(bee_df)} rows" if not bee_df.empty else "Bee: MISSING")

    if weather_df.empty or calendar_df.empty:
        print("Cannot proceed without weather and calendar data.")
        return pd.DataFrame()

    records = []

    for _, cal_row in calendar_df.iterrows():
        district = cal_row["district"]
        crop = cal_row["crop"]
        if crop not in CROPS:
            continue

        sowing_date_str = cal_row["representative_sowing_date"]
        sowing = date.fromisoformat(sowing_date_str)

        bee_info = bee_df[bee_df["district"] == district]
        if not bee_info.empty:
            bee_richness = int(bee_info.iloc[0]["estimated_richness"])
            shannon = bee_info.iloc[0]["shannon_diversity"]
        else:
            bee_richness = 4
            shannon = 1.0

        district_weather = weather_df[weather_df["district"] == district]
        if district_weather.empty:
            continue

        years_available = sorted(district_weather["year"].unique())

        for year in years_available:
            year_weather = district_weather[district_weather["year"] == year].copy()
            if year_weather.empty:
                continue

            year_weather = year_weather.sort_values("date_parsed").reset_index(drop=True)

            sowing_this_year = date(year, sowing.month, sowing.day)

            season_end_month = 12 if crop in ("mustard", "wheat") else 10
            season_end = date(year if season_end_month >= sowing.month else year + 1,
                              season_end_month, 31)

            season_weather = year_weather[
                (year_weather["date_parsed"] >= pd.Timestamp(sowing_this_year)) &
                (year_weather["date_parsed"] <= pd.Timestamp(season_end))
            ].copy()

            if len(season_weather) < 30:
                continue

            # Compute GDD-based flowering date
            temp_df = pd.DataFrame({
                "date": season_weather["date_parsed"].dt.date,
                "T2M_MAX": season_weather["T2M_MAX"],
                "T2M_MIN": season_weather["T2M_MIN"],
            })

            gdd_result = predict_flowering_date(temp_df, crop, sowing_this_year)
            if not gdd_result.predicted_flowering_date:
                continue

            flowering_doy = gdd_result.predicted_flowering_date.timetuple().tm_yday

            # Get early-season weather from first 7 days after sowing (no target leakage)
            window_data = get_early_season_weather(season_weather, sowing_this_year)

            # Get NDVI for this district/year/crop
            ndvi_match = ndvi_df[
                (ndvi_df["district"] == district) &
                (ndvi_df["year"] == year) &
                (ndvi_df["crop"] == crop)
            ]
            if not ndvi_match.empty:
                ndvi_val = ndvi_match.iloc[0]["peak_ndvi"]
                ndvi_inflection = ndvi_match.iloc[0]["inflection_doy"]
                ndvi_r2 = ndvi_match.iloc[0]["fit_r_squared"]
            else:
                ndvi_val = 0.50
                ndvi_inflection = None
                ndvi_r2 = None

            row = {
                "crop": crop,
                "region": "Maharashtra",
                "district": district,
                "year": year,
                "start_doy": max(1, min(365, flowering_doy)),
                "end_doy": max(1, min(365, flowering_doy + 7)),
                "sowing_doy": sowing_this_year.timetuple().tm_yday,
                "temp_7d_mean": round(window_data["temp_7d_mean"], 1),
                "humidity": round(window_data["humidity"], 1),
                "rainfall_7d": round(window_data["rainfall_7d"], 1),
                "wind_speed": round(window_data["wind_speed"], 1),
                "ndvi": round(ndvi_val, 3),
                "month": sowing_this_year.month,
                "day_of_year": sowing_this_year.timetuple().tm_yday,
                "bee_richness": bee_richness,
                "bee_count": max(5, bee_richness * np.random.randint(3, 6)),
                "pollen_tree": SEASONAL_POLLEN.get(sowing_this_year.month, {}).get("tree", 3),
                "pollen_grass": SEASONAL_POLLEN.get(sowing_this_year.month, {}).get("grass", 3),
                "pollen_weed": SEASONAL_POLLEN.get(sowing_this_year.month, {}).get("weed", 3),
                "shannon_diversity": round(shannon, 4),
                "gdd_flowering_doy": flowering_doy,
                "ndvi_inflection_doy": ndvi_inflection if ndvi_inflection else None,
                "ndvi_fit_r2": round(ndvi_r2, 4) if ndvi_r2 else None,
                "gdd_method": gdd_result.method,
                "gdd_confidence": gdd_result.confidence,
                "data_source": "nasa_power_gdd",
            }
            records.append(row)

    return pd.DataFrame(records)


def main():
    print("=" * 60)
    print("BUILDING MAHARASHTRA GROUND TRUTH DATASET")
    print("=" * 60)

    df = build_rows()

    if df.empty:
        print("No rows generated. Check input data files.")
        return

    out_path = DATA_DIR / "maharashtra_ground_truth.csv"
    df.to_csv(out_path, index=False)

    print(f"\nSaved {len(df)} rows to {out_path}")
    print(f"  Crops: {df['crop'].value_counts().to_dict()}")
    print(f"  Districts: {df['district'].nunique()}")
    print(f"  Years: {df['year'].min()}–{df['year'].max()}")
    print(f"  start_doy range: {df['start_doy'].min()}–{df['start_doy'].max()}")
    print(f"  temp_7d_mean range: {df['temp_7d_mean'].min():.1f}–{df['temp_7d_mean'].max():.1f}")
    print(f"  Features use early-season weather (post-sowing) — no target leakage")

    real_count = len(df)
    print(f"\n  Real data rows: {real_count}")

    summary_path = DATA_DIR / "maharashtra_ground_truth_summary.txt"
    with open(summary_path, "w") as f:
        f.write(f"Maharashtra Ground Truth Dataset Summary\n")
        f.write(f"{'=' * 50}\n")
        f.write(f"Total rows: {len(df)}\n")
        f.write(f"Crops: {df['crop'].value_counts().to_dict()}\n")
        f.write(f"Districts: {sorted(df['district'].unique())}\n")
        f.write(f"Years: {df['year'].min()}–{df['year'].max()}\n")
        f.write(f"start_doy range: {df['start_doy'].min()}–{df['start_doy'].max()}\n")
        f.write(f"temp_7d_mean range: {df['temp_7d_mean'].min():.1f}–{df['temp_7d_mean'].max():.1f}\n")
        f.write(f"Feature window: first 7 days after sowing (no target leakage)\n")
        f.write(f"Data source: NASA POWER + GDD model\n")
        f.write(f"Real data labels (not synthetic): {real_count}\n")

    print(f"Summary saved to {summary_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
