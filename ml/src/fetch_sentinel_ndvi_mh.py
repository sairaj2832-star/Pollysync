"""
fetch_sentinel_ndvi_mh.py
Fetches Sentinel-2 NDVI time series for Maharashtra districts from Earth Engine,
fits double-logistic curves to find green-up inflection date (flowering proxy).

Output: ml/data/raw/maharashtra_ndvi_inflection.csv

Usage:
    python fetch_sentinel_ndvi_mh.py
"""

from pathlib import Path
from datetime import date, timedelta
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

from ndvi_model import fit_ndvi_curve, double_logistic

MAHARASHTRA_DISTRICTS = [
    {"name": "nashik",     "lat": 19.99, "lon": 73.79},
    {"name": "pune",       "lat": 18.52, "lon": 73.86},
    {"name": "solapur",    "lat": 17.67, "lon": 75.91},
    {"name": "aurangabad", "lat": 19.88, "lon": 75.32},
    {"name": "nagpur",     "lat": 21.15, "lon": 79.09},
    {"name": "amravati",   "lat": 20.93, "lon": 77.75},
    {"name": "kolhapur",   "lat": 16.70, "lon": 74.24},
    {"name": "satara",     "lat": 17.69, "lon": 73.99},
    {"name": "jalgaon",    "lat": 21.01, "lon": 75.56},
    {"name": "latur",      "lat": 18.40, "lon": 76.56},
]

YEARS = list(range(2018, 2026))

CROP_SEASONS = {
    "sunflower": {"start_month": 5, "end_month": 10},
    "mustard":   {"start_month": 10, "end_month": 3},
    "wheat":     {"start_month": 10, "end_month": 4},
    "rice":      {"start_month": 6, "end_month": 11},
    "cotton":    {"start_month": 5, "end_month": 11},
}


def _synthetic_ndvi_series(district: str, year: int, season_start: date,
                           season_end: date) -> pd.DataFrame:
    """Generate a realistic NDVI time series when Earth Engine is unavailable."""
    np.random.seed(hash(f"{district}_{year}_ndvi") % (2**31))

    base_ndvi = {
        "nashik": 0.55, "pune": 0.50, "solapur": 0.35, "aurangabad": 0.40,
        "nagpur": 0.55, "amravati": 0.50, "kolhapur": 0.60, "satara": 0.55,
        "jalgaon": 0.45, "latur": 0.40,
    }.get(district, 0.50)

    n_days = (season_end - season_start).days
    dates = [season_start + timedelta(days=int(i)) for i in np.linspace(0, n_days, 60)]
    t = np.linspace(0, n_days, 60)

    # Double-logistic shape for NDVI: rise, peak, fall
    t1 = n_days * 0.3   # green-up ~30% through season
    t2 = n_days * 0.7   # senescence ~70% through season
    ndvi_values = base_ndvi + 0.35 * (
        1 / (1 + np.exp(-0.15 * (t - t1)))
        - 1 / (1 + np.exp(-0.1 * (t - t2)))
    )
    ndvi_values = ndvi_values + np.random.normal(0, 0.03, len(t))
    ndvi_values = np.clip(ndvi_values, 0.1, 0.9)

    return pd.DataFrame({
        "date": dates,
        "ndvi": ndvi_values,
    })


def _try_earth_engine(district: dict, year: int, season_start: date,
                      season_end: date) -> pd.DataFrame | None:
    """Try to fetch real Sentinel-2 NDVI from Earth Engine."""
    try:
        import ee

        try:
            ee.Initialize()
        except Exception:
            return None

        point = ee.Geometry.Point([district["lon"], district["lat"]])

        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(point)
            .filterDate(season_start.isoformat(), season_end.isoformat())
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        )

        size = collection.size().getInfo()
        if size < 3:
            return None

        def add_ndvi(img):
            ndvi = img.normalizedDifference(["B8", "B4"]).rename("ndvi")
            date_str = img.date().format("YYYY-MM-dd")
            return img.addBands(ndvi).set("date_str", date_str)

        with_ndvi = collection.map(add_ndvi).select("ndvi")

        # Get NDVI at each timestamp
        dates_data = []
        ndvi_data = []
        for i in range(size):
            img = ee.Image(with_ndvi.toList(size).get(i))
            date_val = img.date().format("YYYY-MM-dd").getInfo()
            ndvi_val = img.reduceRegion(
                reducer=ee.Reducer.mean(), geometry=point, scale=10
            ).get("ndvi").getInfo()
            if ndvi_val is not None:
                dates_data.append(date.fromisoformat(date_val))
                ndvi_data.append(round(float(ndvi_val), 4))

        if len(dates_data) < 6:
            return None

        return pd.DataFrame({"date": dates_data, "ndvi": ndvi_data})

    except Exception:
        return None


def process_district_year(district: dict, year: int, crop: str) -> dict:
    season = CROP_SEASONS[crop]
    season_start = date(year, season["start_month"], 1)
    if season["end_month"] <= season["start_month"]:
        season_end = date(year + 1, season["end_month"], 1)
    else:
        season_end = date(year, season["end_month"], 30)

    result = {
        "district": district["name"],
        "lat": district["lat"],
        "lon": district["lon"],
        "year": year,
        "crop": crop,
        "season_start": season_start.isoformat(),
        "season_end": season_end.isoformat(),
        "inflection_date": None,
        "inflection_doy": None,
        "peak_ndvi": None,
        "fit_r_squared": None,
        "data_source": "none",
        "n_observations": 0,
        "success": False,
    }

    ndvi_df = _try_earth_engine(district, year, season_start, season_end)

    if ndvi_df is not None:
        result["data_source"] = "sentinel2"
        result["n_observations"] = len(ndvi_df)
    else:
        ndvi_df = _synthetic_ndvi_series(district["name"], year, season_start, season_end)
        result["data_source"] = "synthetic"
        result["n_observations"] = len(ndvi_df)

    fit_result = fit_ndvi_curve(ndvi_df)
    if fit_result.success:
        result["inflection_date"] = fit_result.inflection_date.isoformat()
        result["inflection_doy"] = fit_result.inflection_date.timetuple().tm_yday
        result["peak_ndvi"] = round(float(fit_result.peak_ndvi), 4)
        result["fit_r_squared"] = round(float(fit_result.r_squared), 4)
        result["success"] = True

    return result


def main():
    print("=" * 60)
    print("MAHARASHTRA NDVI INFLECTION POINT COLLECTION")
    print(f"  Districts: {len(MAHARASHTRA_DISTRICTS)}")
    print(f"  Years: {YEARS[0]}–{YEARS[-1]}")
    print(f"  Crops: {list(CROP_SEASONS.keys())}")
    print("=" * 60)

    all_results = []
    total = len(MAHARASHTRA_DISTRICTS) * len(YEARS) * len(CROP_SEASONS)
    count = 0

    for district in MAHARASHTRA_DISTRICTS:
        for year in YEARS:
            for crop in CROP_SEASONS:
                count += 1
                result = process_district_year(district, year, crop)
                all_results.append(result)

                status = "OK" if result["success"] else "FAIL"
                if result["success"]:
                    detail = f"DOY {result['inflection_doy']}, NDVI={result['peak_ndvi']}, src={result['data_source']}"
                else:
                    detail = f"failed, src={result['data_source']}"
                print(f"[{count}/{total}] {district['name']} {year} {crop} {status} {detail}")

    df = pd.DataFrame(all_results)
    out_path = DATA_DIR / "maharashtra_ndvi_inflection.csv"
    df.to_csv(out_path, index=False)

    successes = df["success"].sum()
    print(f"\n{'=' * 60}")
    print(f"COMPLETE: {successes}/{len(df)} successful fits")
    print(f"  Saved to {out_path}")

    data_sources = df["data_source"].value_counts().to_dict()
    print(f"  Data sources: {data_sources}")

    if successes > 0:
        good_fits = df[df["success"]].copy()
        per_district = good_fits.groupby("district").agg(
            avg_inflection_doy=("inflection_doy", "mean"),
            avg_peak_ndvi=("peak_ndvi", "mean"),
        ).round(2)
        print(f"\n  Per-district average inflection:")
        print(per_district.to_string())

    print("=" * 60)


if __name__ == "__main__":
    main()
