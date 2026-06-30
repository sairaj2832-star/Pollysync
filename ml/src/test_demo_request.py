"""
test_demo_request.py
End-to-end smoke test simulating what the backend will send: crop + lat/lon
(resolved to region) + environment parameters. Run this after train_model.py
to confirm the full chain works before wiring up the real backend endpoint.

Usage: python test_demo_request.py
"""

from datetime import date
from geo_lookup import DEMO_LOCATIONS
from predict import PollinationFeatures, predict

# Demo environment parameter values — stand-ins for what the backend will
# eventually fetch live from NASA POWER (temp/humidity/rainfall/wind) and
# Earth Engine (ndvi), plus whatever bee/pollen sensor or estimate exists.
DEMO_ENV_PARAMS = {
    "sunflower": {
        "temperature_c": 27.5, "humidity_percent": 62.0, "rainfall_mm": 4.2,
        "wind_speed_kmh": 10.0, "ndvi": 0.58, "bee_count": 4, "pollen_level": 3,
        "month": 7, "day_of_year": 190, "sowing_date": "2025-06-15",
    },
    "mustard": {
        "temperature_c": 18.0, "humidity_percent": 55.0, "rainfall_mm": 1.0,
        "wind_speed_kmh": 8.0, "ndvi": 0.45, "bee_count": 2, "pollen_level": 4,
        "month": 11, "day_of_year": 320, "sowing_date": "2025-10-20",
    },
}


def run_demo():
    for crop, loc in DEMO_LOCATIONS.items():
        env = DEMO_ENV_PARAMS[crop]
        features = PollinationFeatures(
            temperature_c=env["temperature_c"],
            humidity_percent=env["humidity_percent"],
            rainfall_mm=env["rainfall_mm"],
            wind_speed_kmh=env["wind_speed_kmh"],
            ndvi=env["ndvi"],
            bee_count=env["bee_count"],
            pollen_level=env["pollen_level"],
            crop_type=crop,
            month=env["month"],
            day_of_year=env["day_of_year"],
            region=loc["region"],
            sowing_date=env["sowing_date"],
        )
        result = predict(features)
        print(f"\n=== {crop.upper()} (lat={loc['lat']}, lon={loc['lon']}, region={loc['region']}) ===")
        for k, v in result.__dict__.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    run_demo()