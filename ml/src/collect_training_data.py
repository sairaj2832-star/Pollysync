"""
ml/src/collect_training_data.py

Builds a real-data version of flowering_data.csv, replacing generate_data.py's
synthetic rows. For each real district coordinate:
  1. Pulls real daily NASA POWER temperature series for the crop's sowing window
  2. Uses gdd_model.py's literature-sourced GDD thresholds to compute the
     "ground truth" flowering day-of-year (pseudo-label -- there's no live API
     for actual observed flowering dates, so this is the same logic the
     project doc cites as real/citable, just run on real weather instead of
     a flat synthetic temperature)
  3. Pulls real humidity/rainfall/wind for the same window (NASA POWER)
  4. Pulls real NDVI for the same window if Earth Engine is configured
  5. Pulls real bee richness for that coordinate (GBIF)
  6. Writes one row per site/season to ml/data/flowering_data_real.csv

Run:
    python collect_training_data.py
Then point train_model.py at flowering_data_real.csv instead of
flowering_data.csv (or merge the two) before re-running training.

This is synchronous (plain requests), unlike the FastAPI environment_service.py,
since it's a one-off offline script, not a request-handling server.
"""

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests

from gdd_model import predict_flowering_date, CROP_PARAMS  # existing module in this repo

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Real growing-district coordinates from the project doc's confirmed belts.
# (lat, lon, region_name, crop, sowing_date) -- add more rows as you collect them.
SITES = [
    # Sunflower (Kharif, ~June sowing)
    {"lat": 15.32, "lon": 75.71, "region": "Karnataka", "crop": "sunflower", "sowing_date": "2025-06-15"},
    {"lat": 19.99, "lon": 73.79, "region": "Maharashtra", "crop": "sunflower", "sowing_date": "2025-06-20"},
    {"lat": 15.91, "lon": 79.74, "region": "Andhra Pradesh", "crop": "sunflower", "sowing_date": "2025-06-18"},
    # Mustard (Rabi, ~October sowing)
    {"lat": 27.02, "lon": 74.22, "region": "Rajasthan", "crop": "mustard", "sowing_date": "2025-10-10"},
    {"lat": 23.26, "lon": 77.41, "region": "Madhya Pradesh", "crop": "mustard", "sowing_date": "2025-10-12"},
    {"lat": 26.85, "lon": 80.95, "region": "Uttar Pradesh", "crop": "mustard", "sowing_date": "2025-10-08"},
]

NASA_POWER_URL = (
    "https://power.larc.nasa.gov/api/temporal/daily/point"
    "?parameters=T2M_MAX,T2M_MIN,RH2M,PRECTOTCORR,WS2M"
    "&community=AG&longitude={lon}&latitude={lat}"
    "&start={start}&end={end}&format=JSON"
)
GBIF_URL = (
    "https://api.gbif.org/v1/occurrence/search"
    "?taxonKey=4334&decimalLatitude={lat_min},{lat_max}"
    "&decimalLongitude={lon_min},{lon_max}&limit=300"
)


def fetch_nasa_power_series(lat: float, lon: float, sowing: date, n_days: int = 150) -> pd.DataFrame:
    """Real daily T2M_MAX/MIN/RH2M/PRECTOTCORR/WS2M for n_days starting at sowing."""
    start = sowing.strftime("%Y%m%d")
    end = (sowing + timedelta(days=n_days)).strftime("%Y%m%d")
    resp = requests.get(NASA_POWER_URL.format(lat=lat, lon=lon, start=start, end=end), timeout=30)
    resp.raise_for_status()
    params = resp.json()["properties"]["parameter"]

    dates = sorted(params["T2M_MAX"].keys())
    return pd.DataFrame({
        "date": [date(int(d[:4]), int(d[4:6]), int(d[6:8])) for d in dates],
        "T2M_MAX": [params["T2M_MAX"][d] for d in dates],
        "T2M_MIN": [params["T2M_MIN"][d] for d in dates],
        "RH2M": [params["RH2M"][d] for d in dates],
        "PRECTOTCORR": [params["PRECTOTCORR"][d] for d in dates],
        "WS2M": [params["WS2M"][d] for d in dates],
    })


def fetch_bee_richness(lat: float, lon: float, radius_km: float = 25) -> int:
    deg = radius_km / 111
    url = GBIF_URL.format(lat_min=lat - deg, lat_max=lat + deg, lon_min=lon - deg, lon_max=lon + deg)
    resp = requests.get(url, timeout=30)
    if resp.status_code != 200:
        return 0
    results = resp.json().get("results", [])
    species = {r.get("species") for r in results if r.get("species")}
    return len(species)


def fetch_ndvi(lat: float, lon: float, as_of: date, window_days: int = 20):
    """Optional -- only runs if `earthengine-api` is installed and authenticated.
    Returns None (caller should impute) if EE isn't set up."""
    try:
        import ee
        ee.Initialize()
    except Exception:
        return None

    point = ee.Geometry.Point([lon, lat])
    start = (as_of - timedelta(days=window_days)).isoformat()
    end = as_of.isoformat()
    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(point).filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
    )
    if collection.size().getInfo() == 0:
        return None

    def add_ndvi(img):
        return img.addBands(img.normalizedDifference(["B8", "B4"]).rename("ndvi"))

    mean_img = collection.map(add_ndvi).select("ndvi").mean()
    value = mean_img.reduceRegion(reducer=ee.Reducer.mean(), geometry=point, scale=10).get("ndvi")
    result = value.getInfo()
    return round(result, 4) if result is not None else None


def build_row(site: dict) -> dict | None:
    sowing = date.fromisoformat(site["sowing_date"])
    temp_df = fetch_nasa_power_series(site["lat"], site["lon"], sowing)

    # Ground-truth-ish flowering DOY from the literature GDD thresholds
    # (gdd_model.py), applied to REAL temperature data instead of a flat
    # synthetic series.
    result = predict_flowering_date(
        temp_df.rename(columns={"date": "date"}), site["crop"], sowing
    )
    if not result.predicted_flowering_date:
        print(f"  skip {site['region']}/{site['crop']}: GDD threshold never reached in window")
        return None
    flowering_date = result.predicted_flowering_date
    start_doy = flowering_date.timetuple().tm_yday

    # 7 days of weather ending at the flowering date (matches what
    # FEATURE_COLS expects: a window leading up to the predicted event)
    window = temp_df[(temp_df["date"] > flowering_date - timedelta(days=7)) & (temp_df["date"] <= flowering_date)]
    temp_7d_mean = ((window["T2M_MAX"] + window["T2M_MIN"]) / 2).mean()
    humidity = window["RH2M"].mean()
    rainfall_7d = window["PRECTOTCORR"].sum()
    wind_speed = window["WS2M"].mean() * 3.6  # m/s -> km/h

    ndvi = fetch_ndvi(site["lat"], site["lon"], flowering_date)
    bee_richness = fetch_bee_richness(site["lat"], site["lon"])

    return {
        "crop": site["crop"],
        "region": site["region"],
        "start_doy": start_doy,
        "end_doy": start_doy + 7,
        "temp_7d_mean": round(temp_7d_mean, 2),
        "humidity": round(humidity, 2),
        "rainfall_7d": round(rainfall_7d, 2),
        "wind_speed": round(wind_speed, 2),
        "ndvi": ndvi if ndvi is not None else 0.5,  # imputed if EE not configured -- flag in README
        "month": flowering_date.month,
        "day_of_year": start_doy,
        "bee_richness": bee_richness,
    }


def main():
    rows = []
    for site in SITES:
        print(f"Fetching {site['region']} / {site['crop']} ...")
        row = build_row(site)
        if row:
            rows.append(row)

    if not rows:
        print("No rows collected -- check NASA POWER connectivity.")
        return

    df = pd.DataFrame(rows)
    out_path = DATA_DIR / "flowering_data_real.csv"
    df.to_csv(out_path, index=False)
    print(f"\nSaved {len(df)} real rows to {out_path}")
    print("NDVI imputed to 0.5 for any row where Earth Engine wasn't configured -- check before training.")


if __name__ == "__main__":
    main()