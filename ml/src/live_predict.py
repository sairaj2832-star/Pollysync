"""
live_predict.py — Test a prediction with the retrained MH V2 models.

Usage:
    python live_predict.py --lat 20.2566 --lon 73.6106 --species "Helianthus annuus" --sowing-date 2025-06-15
"""

from pathlib import Path
from datetime import date, datetime, timedelta
import argparse
import sys
import json

import joblib
import pandas as pd
import requests

sys.path.append(str(Path(__file__).parent))
from maharashtra_features import prepare_mh_features, add_district_features, add_engineered_features, MH_V2_FEATURES

SPECIES_MAP = {
    "helianthus annuus": "sunflower",
    "sunflower": "sunflower",
    "brassica juncea": "mustard",
    "mustard": "mustard",
    "triticum aestivum": "wheat",
    "wheat": "wheat",
    "oryza sativa": "rice",
    "rice": "rice",
    "gossypium hirsutum": "cotton",
    "cotton": "cotton",
}

DISTRICTS = {
    "nashik": (19.99, 73.79), "pune": (18.52, 73.86), "solapur": (17.67, 75.91),
    "aurangabad": (19.88, 75.32), "nagpur": (21.15, 79.09), "amravati": (20.93, 77.75),
    "kolhapur": (16.70, 74.24), "satara": (17.69, 73.99), "jalgaon": (21.01, 75.56),
    "latur": (18.40, 76.56),
}


def find_nearest_district(lat, lon):
    best, best_dist = None, float("inf")
    for name, (dlat, dlon) in DISTRICTS.items():
        d = ((lat - dlat) ** 2 + (lon - dlon) ** 2) ** 0.5
        if d < best_dist:
            best, best_dist = name, d
    return best


def fetch_nasa_power(lat, lon, start_date, end_date):
    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?parameters=T2M_MAX,T2M_MIN,RH2M,PRECTOTCORR,WS2M"
        f"&community=AG&longitude={lon}&latitude={lat}"
        f"&start={start_date.strftime('%Y%m%d')}&end={end_date.strftime('%Y%m%d')}"
        f"&format=JSON"
    )
    r = requests.get(url, timeout=30)
    data = r.json()["properties"]["parameter"]
    dates = sorted(data["T2M_MAX"].keys())
    records = []
    for d in dates:
        if data["T2M_MAX"][d] is None:
            continue
        records.append({
            "date_parsed": pd.Timestamp(d),
            "T2M_MAX": data["T2M_MAX"][d],
            "T2M_MIN": data["T2M_MIN"][d],
            "RH2M": data["RH2M"][d],
            "PRECTOTCORR": data["PRECTOTCORR"][d],
            "WS2M": data["WS2M"][d],
        })
    return pd.DataFrame(records)


def main():
    parser = argparse.ArgumentParser(description="Live MH V2 model prediction")
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--species", type=str, required=True, help="e.g. 'Helianthus annuus' or 'sunflower'")
    parser.add_argument("--sowing-date", type=str, required=True, help="YYYY-MM-DD")
    args = parser.parse_args()

    crop = SPECIES_MAP.get(args.species.lower())
    if not crop:
        print(f"Unknown species: {args.species}")
        print(f"Known: {list(SPECIES_MAP.keys())}")
        sys.exit(1)

    district = find_nearest_district(args.lat, args.lon)
    sowing = date.fromisoformat(args.sowing_date)

    MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

    print(f"\n{'='*50}")
    print(f"Crop:         {crop}")
    print(f"District:     {district}")
    print(f"Sowing date:  {sowing}")
    print(f"Location:     {args.lat}, {args.lon}")
    print(f"{'='*50}")

    print(f"\nFetching weather from NASA POWER...")
    start = sowing
    end = sowing + timedelta(days=14)
    try:
        weather_df = fetch_nasa_power(args.lat, args.lon, start, end)
        if len(weather_df) < 3:
            raise ValueError(f"Only {len(weather_df)} days")
        print(f"  Got {len(weather_df)} days of weather data")
    except Exception as e:
        print(f"  Weather fetch failed: {e}")
        print(f"  Using synthetic defaults")
        weather_df = pd.DataFrame({
            "date_parsed": [pd.Timestamp(sowing + timedelta(days=i)) for i in range(7)],
            "T2M_MAX": [30.0] * 7, "T2M_MIN": [20.0] * 7,
            "RH2M": [60.0] * 7, "PRECTOTCORR": [5.0] * 7, "WS2M": [2.0] * 7,
        })

    early = weather_df[
        (weather_df["date_parsed"] >= pd.Timestamp(sowing)) &
        (weather_df["date_parsed"] < pd.Timestamp(sowing) + pd.Timedelta(days=7))
    ]
    if len(early) < 3:
        early = weather_df.head(7)

    temp_7d = round(((early["T2M_MAX"] + early["T2M_MIN"]) / 2).mean(), 1)
    humidity = round(early["RH2M"].mean(), 1)
    rainfall = round(early["PRECTOTCORR"].sum(), 1)
    wind = round(early["WS2M"].mean() * 3.6, 1)

    print(f"\nEarly-season weather (first 7d after sowing):")
    print(f"  temp_7d_mean:  {temp_7d} °C")
    print(f"  humidity:      {humidity}%")
    print(f"  rainfall_7d:   {rainfall} mm")
    print(f"  wind_speed:    {wind} km/h")

    row = {
        "temp_7d_mean": temp_7d, "humidity": humidity,
        "rainfall_7d": rainfall, "wind_speed": wind,
        "ndvi": 0.55, "month": sowing.month,
        "day_of_year": sowing.timetuple().tm_yday,
        "crop_mustard": 0, "crop_wheat": 0,
        "crop_sunflower": 0, "crop_rice": 0, "crop_cotton": 0,
        "crop": crop,
        "bee_richness": 5, "bee_count": 25,
        "pollen_tree": 3, "pollen_grass": 3, "pollen_weed": 3,
        "district": district,
    }
    row[f"crop_{crop}"] = 1

    print(f"\nLoading MH V2 models...")
    try:
        f_model = joblib.load(str(MODELS_DIR / "flowering_model_mh.pkl"))
        f_scaler = joblib.load(str(MODELS_DIR / "flowering_scaler_mh.pkl"))
        p_model = joblib.load(str(MODELS_DIR / "psi_model_mh.pkl"))
        p_scaler = joblib.load(str(MODELS_DIR / "psi_scaler_mh.pkl"))
        r_model = joblib.load(str(MODELS_DIR / "risk_model_mh.pkl"))
        r_scaler = joblib.load(str(MODELS_DIR / "risk_scaler_mh.pkl"))
        print(f"  Models loaded successfully")
    except Exception as e:
        print(f"  Model loading failed: {e}")
        sys.exit(1)

    X = prepare_mh_features(pd.DataFrame([row]), use_v2=True)
    expected_cols = list(f_model.feature_names_in_)
    for c in expected_cols:
        if c not in X.columns:
            X[c] = 0
    X = X[expected_cols]

    X_s = f_scaler.transform(X)
    start_doy = int(round(f_model.predict(X_s)[0]))
    start_doy = max(1, min(365, start_doy))

    psi = int(round(p_model.predict(p_scaler.transform(X))[0]))
    psi = max(0, min(100, psi))

    risk_raw = r_model.predict(r_scaler.transform(X))[0]
    risk = risk_raw if isinstance(risk_raw, str) else r_model._label_encoder.inverse_transform([risk_raw])[0]

    start_date = date(2026, 1, 1) + timedelta(days=start_doy - 1)
    end_date = start_date + timedelta(days=7)

    print(f"\n{'='*50}")
    print(f"PREDICTION RESULTS (MH V2)")
    print(f"{'='*50}")
    print(f"  Flowering start: DOY {start_doy} ({start_date})")
    print(f"  Flowering end:   DOY {min(365, start_doy + 7)} ({end_date})")
    print(f"  PSI Score:       {psi}/100")
    print(f"  Risk Level:      {risk}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
