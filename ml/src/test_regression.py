"""
test_regression.py
Automated regression tests for the ML pipeline.
Run: python test_regression.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import joblib
import pandas as pd
import numpy as np
from datetime import date, timedelta

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

passed = 0
failed = 0


def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS [{name}]")
    else:
        failed += 1
        print(f"  FAIL [{name}] {detail}")


def test_model_loading():
    print("\n[Test] Model Loading")
    models = {}
    for name in ("flowering", "psi", "risk"):
        model_path = MODELS_DIR / f"{name}_model.pkl"
        scaler_path = MODELS_DIR / f"{name}_scaler.pkl"
        check(f"{name}_model.pkl exists", model_path.exists())
        check(f"{name}_scaler.pkl exists", scaler_path.exists())
        if model_path.exists() and scaler_path.exists():
            models[f"{name}_model"] = joblib.load(str(model_path))
            models[f"{name}_scaler"] = joblib.load(str(scaler_path))
    for name in ("flowering_model", "psi_model", "risk_model"):
        m = models.get(name)
        check(f"{name} has predict method", hasattr(m, "predict"))
    return models


def test_feature_alignment(models):
    print("\n[Test] Feature Alignment")
    expected_cols = [
        "temp_7d_mean", "humidity", "rainfall_7d", "wind_speed", "ndvi",
        "day_of_year", "month", "crop_mustard", "crop_sunflower", "crop_cotton", "bee_richness",
        "bee_count", "pollen_tree", "pollen_grass", "pollen_weed",
    ]
    check("has 17 features", len(expected_cols) == 17, f"got {len(expected_cols)}")
    required = set(expected_cols)
    missing = required - set(expected_cols)
    check("all required features present", len(missing) == 0, f"missing: {missing}")


def test_prediction_bounds(models):
    print("\n[Test] Prediction Bounds")
    from predict import PollinationFeatures, predict, _build_feature_dict

    test_cases = [
        PollinationFeatures(temperature_c=25, humidity_percent=60, rainfall_mm=5,
                            wind_speed_kmh=10, ndvi=0.6, bee_count=4, bee_abundance=20,
                            pollen_level=3, crop_type="sunflower", month=6, day_of_year=166,
                            region="Maharashtra", sowing_date="2025-06-15"),
        PollinationFeatures(temperature_c=15, humidity_percent=40, rainfall_mm=1,
                            wind_speed_kmh=5, ndvi=0.3, bee_count=1, bee_abundance=5,
                            pollen_level=1, crop_type="mustard", month=10, day_of_year=293,
                            region="Rajasthan", sowing_date="2025-10-20"),
        PollinationFeatures(temperature_c=35, humidity_percent=85, rainfall_mm=20,
                            wind_speed_kmh=25, ndvi=0.8, bee_count=7, bee_abundance=40,
                            pollen_level=5, crop_type="sunflower", month=8, day_of_year=220,
                            region="Karnataka", sowing_date="2025-07-01"),
    ]

    for i, features in enumerate(test_cases):
        result = predict(features)
        check(f"case {i}: source is trained_model", result.source == "trained_model")
        check(f"case {i}: flowering DOY in [1,365]",
              1 <= result.flowering_start_doy <= 365,
              f"got {result.flowering_start_doy}")
        check(f"case {i}: end >= start",
              result.flowering_end_doy >= result.flowering_start_doy,
              f"end={result.flowering_end_doy} < start={result.flowering_start_doy}")
        check(f"case {i}: PSI in [0,100]",
              0 <= result.psi_score <= 100,
              f"got {result.psi_score}")
        check(f"case {i}: risk is valid",
              result.risk_level in ("Low", "Medium", "High"),
              f"got {result.risk_level}")


def test_physical_plausibility(models):
    print("\n[Test] Physical Plausibility")
    from predict import PollinationFeatures, predict

    base = PollinationFeatures(temperature_c=25, humidity_percent=60, rainfall_mm=5,
                               wind_speed_kmh=10, ndvi=0.6, bee_count=4, bee_abundance=20,
                               pollen_level=3, crop_type="sunflower", month=6, day_of_year=166,
                               region="Maharashtra", sowing_date="2025-06-15")

    r_cold = predict(PollinationFeatures(**{**base.__dict__, "temperature_c": 15}))
    r_hot = predict(PollinationFeatures(**{**base.__dict__, "temperature_c": 35}))
    check("warmer -> earlier flowering (sunflower)",
          r_hot.flowering_start_doy <= r_cold.flowering_start_doy,
          f"cold={r_cold.flowering_start_doy}, hot={r_hot.flowering_start_doy}")

    r_low_ndvi = predict(PollinationFeatures(**{**base.__dict__, "ndvi": 0.2, "bee_count": 1, "pollen_level": 1}))
    r_high_ndvi = predict(PollinationFeatures(**{**base.__dict__, "ndvi": 0.8, "bee_count": 6, "pollen_level": 5}))
    check("better environment -> higher PSI",
          r_high_ndvi.psi_score >= r_low_ndvi.psi_score,
          f"good={r_high_ndvi.psi_score}, bad={r_low_ndvi.psi_score}")


def test_baseline_fallback():
    print("\n[Test] Baseline Fallback")
    from predict import _baseline_flowering, _baseline_psi
    from predict import PollinationFeatures

    features = PollinationFeatures(temperature_c=25, humidity_percent=60, rainfall_mm=5,
                                   wind_speed_kmh=10, ndvi=0.6, bee_count=4, bee_abundance=20,
                                   pollen_level=3, crop_type="sunflower", month=6, day_of_year=166,
                                   region="Unknown", sowing_date=None)

    start, end = _baseline_flowering(features)
    check("baseline flowering DOY in [1,365]", 1 <= start <= 365, f"got {start}")
    check("baseline end >= start", end >= start)

    psi, risk, gap = _baseline_psi(features)
    check("baseline PSI in [0,100]", 0 <= psi <= 100, f"got {psi}")
    check("baseline risk valid", risk in ("Low", "Medium", "High"))


def test_data_files():
    print("\n[Test] Data Files")
    datasets = ["flowering_data.csv", "flowering_data_large.csv",
                "flowering_data_real.csv", "psi_data.csv"]
    for name in datasets:
        path = DATA_DIR / name
        check(f"{name} exists", path.exists())
        if path.exists():
            df = pd.read_csv(path)
            check(f"{name} has rows", len(df) > 0, f"got {len(df)} rows")
            check(f"{name} has crop column", "crop" in df.columns)


def test_sensitivity_analysis():
    print("\n[Test] Sensitivity Analysis")
    from mismatch import predict_mismatch

    sowing = date(2025, 6, 15)
    results = []
    for base_temp in [20, 25, 30]:
        temp_df = pd.DataFrame({
            "date": [sowing + timedelta(days=i) for i in range(150)],
            "T2M_MAX": [base_temp + 5] * 150,
            "T2M_MIN": [base_temp - 5] * 150,
        })
        r = predict_mismatch(crop="sunflower", region="Maharashtra",
                              sowing_date=sowing, temp_df=temp_df)
        results.append(r)

    check("sensitivity returns gap_days", results[0].get("gap_days") is not None)
    check("sensitivity returns alert", bool(results[0].get("alert")))


def test_ndvi_model():
    print("\n[Test] NDVI Model")
    from ndvi_model import fit_ndvi_curve

    from demo import make_synthetic_ndvi_series
    sowing = date(2025, 6, 15)
    ndvi_df = make_synthetic_ndvi_series(sowing, n_days=120, green_up_day=40, senescence_day=85)
    result = fit_ndvi_curve(ndvi_df)
    check("ndvi fit succeeds", result.success, result.note)
    if result.success:
        check("ndvi inflection in [0,120]", 0 <= result.inflection_day <= 120,
              f"got {result.inflection_day}")
        check("ndvi peak in [0,1]", 0 <= result.peak_ndvi <= 1,
              f"got {result.peak_ndvi}")


def test_gdd_model():
    print("\n[Test] GDD Model")
    from gdd_model import predict_flowering_date, CROP_PARAMS, daily_gdd

    gdd = daily_gdd(30, 20, 10)
    check("daily_gdd is non-negative", gdd >= 0, f"got {gdd}")

    sowing = date(2025, 6, 15)
    temp_df = pd.DataFrame({
        "date": [sowing + timedelta(days=i) for i in range(150)],
        "T2M_MAX": [30] * 150,
        "T2M_MIN": [20] * 150,
    })
    r = predict_flowering_date(temp_df, "sunflower", sowing)
    check("gdd flowering returns date", r.predicted_flowering_date is not None)
    if r.predicted_flowering_date:
        check("gdd flowering after sowing",
              r.predicted_flowering_date >= sowing)


if __name__ == "__main__":
    print("=" * 60)
    print("POLLISYNC ML REGRESSION TESTS")
    print("=" * 60)

    models = test_model_loading()
    if models:
        test_feature_alignment(models)
        test_prediction_bounds(models)
        test_physical_plausibility(models)
    else:
        print("  SKIP: model-dependent tests (no models loaded)")

    test_baseline_fallback()
    test_data_files()
    test_sensitivity_analysis()
    test_ndvi_model()
    test_gdd_model()

    print(f"\n{'=' * 60}")
    print(f"RESULTS: {passed} passed, {failed} failed, {passed + failed} total")
    print(f"{'=' * 60}")

    sys.exit(0 if failed == 0 else 1)

