"""
maharashtra_features.py
Feature engineering utilities for Maharashtra-specific model.
Adds district one-hot encoding, elevation, agro-climatic zone, and GDD features.
"""

import pandas as pd
import numpy as np

MAHARASHTRA_DISTRICTS = [
    "nashik", "pune", "solapur", "aurangabad", "nagpur",
    "amravati", "kolhapur", "satara", "jalgaon", "latur",
]

DISTRICT_ELEVATION = {
    "nashik": 570, "pune": 560, "solapur": 460, "aurangabad": 570,
    "nagpur": 310, "amravati": 340, "kolhapur": 560, "satara": 650,
    "jalgaon": 210, "latur": 520,
}

# Agro-climatic zones of Maharashtra (based on rainfall, soil, temp)
AGRO_CLIMATIC_ZONES = {
    "nashik": "western_ghats",
    "pune": "western_ghats",
    "solapur": "scarce_rainfall",
    "aurangabad": "marathwada",
    "nagpur": "vidarbha",
    "amravati": "vidarbha",
    "kolhapur": "konkan",
    "satara": "western_ghats",
    "jalgaon": "khandesh",
    "latur": "marathwada",
}

ZONE_DUMMY_COLS = [
    "zone_western_ghats", "zone_scarce_rainfall", "zone_marathwada",
    "zone_vidarbha", "zone_konkan", "zone_khandesh",
]

DISTRICT_DUMMY_COLS = [f"dist_{d}" for d in MAHARASHTRA_DISTRICTS]

MH_V2_FEATURES = [
    # Original V1 features
    "temp_7d_mean", "humidity", "rainfall_7d", "wind_speed", "ndvi",
    "day_of_year", "month",
    "crop_mustard", "crop_wheat", "crop_sunflower", "crop_rice", "crop_cotton",
    "bee_richness", "bee_count", "pollen_tree", "pollen_grass", "pollen_weed",
    # District features
    "elevation_m",
    "zone_western_ghats", "zone_scarce_rainfall", "zone_marathwada",
    "zone_vidarbha", "zone_konkan", "zone_khandesh",
    # Engineered features
    "temp_humidity", "temp_ndvi", "humidity_rainfall",
    "temp_sq", "ndvi_sq", "bee_total", "temp_wind",
]


def add_district_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add elevation and agro-climatic zone one-hot columns."""
    df = df.copy()

    if "district" in df.columns:
        df["elevation_m"] = df["district"].map(DISTRICT_ELEVATION).fillna(500)
        zone_map = {d: AGRO_CLIMATIC_ZONES.get(d, "unknown") for d in MAHARASHTRA_DISTRICTS}
        zone_series = df["district"].map(zone_map).fillna("unknown")

        for zone_col in ZONE_DUMMY_COLS:
            zone_name = zone_col.replace("zone_", "")
            df[zone_col] = (zone_series == zone_name).astype(int)

    return df


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add interaction terms (same as train_improved_models.py add_engineered_features)."""
    df = df.copy()
    if "temp_7d_mean" in df.columns and "humidity" in df.columns:
        df["temp_humidity"] = df["temp_7d_mean"] * df["humidity"] / 100
    if "temp_7d_mean" in df.columns and "ndvi" in df.columns:
        df["temp_ndvi"] = df["temp_7d_mean"] * df["ndvi"]
    if "humidity" in df.columns and "rainfall_7d" in df.columns:
        df["humidity_rainfall"] = df["humidity"] * df["rainfall_7d"] / 100
    if "temp_7d_mean" in df.columns:
        df["temp_sq"] = df["temp_7d_mean"] ** 2
    if "ndvi" in df.columns:
        df["ndvi_sq"] = df["ndvi"] ** 2
    if "bee_richness" in df.columns and "bee_count" in df.columns:
        df["bee_total"] = df["bee_richness"] * df["bee_count"]
    if "temp_7d_mean" in df.columns and "wind_speed" in df.columns:
        df["temp_wind"] = df["temp_7d_mean"] * df["wind_speed"]
    return df


def onehot_crop(df: pd.DataFrame, crop_col: str = "crop") -> pd.DataFrame:
    df = df.copy()
    for c in ["mustard", "wheat", "sunflower", "rice", "cotton"]:
        col_name = f"crop_{c}"
        if col_name not in df.columns:
            df[col_name] = (df[crop_col].str.lower() == c).astype(int)
    return df


def fill_missing_features(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing features with defaults. Handles V1 + MH extended features."""
    df = df.copy()
    defaults = {
        "wind_speed": 10.0, "day_of_year": 150, "month": 6,
        "bee_richness": 4, "bee_count": 15,
        "pollen_tree": 3, "pollen_grass": 3, "pollen_weed": 3,
        "elevation_m": 500,
    }
    for zone_col in ZONE_DUMMY_COLS:
        defaults[zone_col] = 0

    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default
        elif df[col].isna().any():
            df[col] = df[col].fillna(default)
    return df


def compute_sample_weights(df: pd.DataFrame, real_weight: float = 5.0) -> np.ndarray:
    """
    Compute sample weights giving higher weight to real data rows.
    Real data = rows from maharashtra_ground_truth.csv with nasa_power_gdd source.
    Synthetic data = rows from generate_more_data.py etc.
    """
    weights = np.ones(len(df))
    if "data_source" in df.columns:
        real_mask = df["data_source"].str.contains("nasa_power", na=False)
        weights[real_mask] = real_weight
    return weights


def prepare_mh_features(df: pd.DataFrame, use_v2: bool = True) -> pd.DataFrame:
    """Full feature preparation pipeline for Maharashtra model."""
    df = df.copy()

    if "crop" in df.columns:
        df = onehot_crop(df)

    df = fill_missing_features(df)
    df = add_district_features(df)
    df = add_engineered_features(df)

    feature_cols = MH_V2_FEATURES if use_v2 else [
        c for c in MH_V2_FEATURES
        if c not in ("temp_humidity", "temp_ndvi", "humidity_rainfall",
                     "temp_sq", "ndvi_sq", "bee_total", "temp_wind")
    ]

    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0

    return df[feature_cols]
