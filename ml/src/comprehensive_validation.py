"""
comprehensive_validation.py
Full model validation: cross-val on real data, A/B baseline comparison, error analysis.
"""

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))

import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, accuracy_score
from sklearn.model_selection import cross_val_score
from datetime import date, timedelta

import warnings
warnings.filterwarnings("ignore")

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

V1_FEATURES = [
    "temp_7d_mean", "humidity", "rainfall_7d", "wind_speed", "ndvi",
    "day_of_year", "month",
    "crop_mustard", "crop_wheat", "crop_sunflower", "crop_rice", "crop_cotton",
    "bee_richness", "bee_count", "pollen_tree", "pollen_grass", "pollen_weed",
]


def load_models(prefix=""):
    models = {}
    for name in ("flowering", "psi", "risk"):
        m_path = MODELS_DIR / f"{name}_model{prefix}.pkl"
        s_path = MODELS_DIR / f"{name}_scaler{prefix}.pkl"
        if m_path.exists() and s_path.exists():
            models[name] = joblib.load(str(m_path))
            models[f"{name}_scaler"] = joblib.load(str(s_path))
    return models


def prepare_features(df, feature_cols=None):
    if feature_cols is None:
        feature_cols = V1_FEATURES
    df_copy = df.copy()
    if "crop" in df_copy.columns:
        for crop in ["mustard", "wheat", "sunflower", "rice", "cotton"]:
            df_copy[f"crop_{crop}"] = (df_copy["crop"].str.lower() == crop).astype(int)
    for col in feature_cols:
        if col not in df_copy.columns:
            df_copy[col] = 0
    for col in ["pollen_tree", "pollen_grass", "pollen_weed"]:
        if col in df_copy.columns and "pollen_level" in df_copy.columns:
            df_copy[col] = df_copy["pollen_level"]
    for col in ["bee_count"]:
        if col not in df_copy.columns and "bee_abundance" in df_copy.columns:
            df_copy[col] = df_copy["bee_abundance"]
        elif col not in df_copy.columns:
            df_copy[col] = 15
    return df_copy[feature_cols]


def validate_on_real_data():
    print("=" * 70)
    print("VALIDATION ON REAL DATA (flowering_data_real.csv)")
    print("=" * 70)

    path = DATA_DIR / "flowering_data_real.csv"
    if not path.exists():
        print("  SKIP: no real data file")
        return

    df = pd.read_csv(path)
    X = prepare_features(df)
    y = df["start_doy"]

    models_v1 = load_models("")
    if "flowering" not in models_v1:
        print("  SKIP: no v1 models loaded")
        return

    model = models_v1["flowering"]
    scaler = models_v1["flowering_scaler"]

    X_scaled = scaler.transform(X)
    y_pred = model.predict(X_scaled)

    r2 = r2_score(y, y_pred)
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    errors = y - y_pred
    mape = np.mean(np.abs(errors / y)) * 100

    print(f"\n  Model type: {type(model).__name__}")
    print(f"  Samples: {len(df)}")
    print(f"  R²:  {r2:.4f}")
    print(f"  MAE: {mae:.1f} days")
    print(f"  RMSE: {rmse:.1f} days")
    print(f"  MAPE: {mape:.1f}%")
    print(f"  Error range: {errors.min():.1f} to {errors.max():.1f} days")
    print(f"  Error std: {errors.std():.1f} days")

    # Baseline comparison
    from predict import _baseline_flowering, PollinationFeatures
    baseline_preds = []
    for _, row in df.iterrows():
        feats = PollinationFeatures(
            temperature_c=row.get("temp_7d_mean", 25),
            humidity_percent=row.get("humidity", 60),
            rainfall_mm=row.get("rainfall_7d", 5),
            wind_speed_kmh=row.get("wind_speed", 10),
            ndvi=row.get("ndvi", 0.5),
            bee_count=row.get("bee_richness", 3),
            bee_abundance=row.get("bee_count", 15),
            pollen_level=row.get("pollen_tree", 3),
            crop_type=row["crop"],
            month=row.get("month", 6),
            day_of_year=row.get("day_of_year", 150),
            region="Maharashtra",
        )
        s, _ = _baseline_flowering(feats)
        baseline_preds.append(s)

    bl_r2 = r2_score(y, baseline_preds)
    bl_mae = mean_absolute_error(y, baseline_preds)
    print(f"\n  Baseline comparison:")
    print(f"    Baseline R²:  {bl_r2:.4f}  (model: {r2:.4f})")
    print(f"    Baseline MAE: {bl_mae:.1f} days  (model: {mae:.1f} days)")
    improvement = ((bl_mae - mae) / bl_mae) * 100
    print(f"    MAE improvement: {improvement:.1f}%")

    # Cross-validation
    try:
        cv_scores = cross_val_score(model.__class__(**model.get_params()),
                                    X_scaled, y, cv=5, scoring="r2")
        print(f"\n  5-fold CV R²: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
    except Exception as e:
        print(f"  CV skipped: {e}")

    print(f"\n  Error percentiles:")
    for p in [10, 25, 50, 75, 90]:
        print(f"    {p}th: {np.percentile(errors, p):.1f} days")

    return {"r2": r2, "mae": mae, "rmse": rmse, "improvement_pct": improvement}


def validate_all_models():
    """Compare v1 vs v2 models."""
    print("\n" + "=" * 70)
    print("MODEL COMPARISON: V1 (17 features) vs V2 (24 engineered features)")
    print("=" * 70)

    df_large = pd.read_csv(DATA_DIR / "flowering_data_large.csv")
    X_v1 = prepare_features(df_large)
    y = df_large["start_doy"]

    for prefix, label in [("", "V1 (17 features)"), ("_v2", "V2 (24 engineered)")]:
        models = load_models(prefix)
        if "flowering" not in models:
            print(f"\n  {label}: models not found")
            continue
        model = models["flowering"]
        scaler = models["flowering_scaler"]
        v2_features = list(scaler.feature_names_in_) if hasattr(scaler, 'feature_names_in_') else list(model.get_booster().feature_names) if hasattr(model, 'get_booster') else V1_FEATURES
        X = X_v1 if prefix == "" else prepare_features(df_large, v2_features)
        X_scaled = scaler.transform(X)
        y_pred = model.predict(X_scaled)
        r2 = r2_score(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        print(f"\n  {label}: R²={r2:.4f}, MAE={mae:.1f} days")


def validate_psi_models():
    print("\n" + "=" * 70)
    print("PSI & RISK MODEL VALIDATION")
    print("=" * 70)

    psi_path = DATA_DIR / "psi_data.csv"
    if not psi_path.exists():
        print("  SKIP: no psi_data.csv")
        return

    df = pd.read_csv(psi_path)
    for crop in ["mustard", "wheat", "sunflower", "rice", "cotton"]:
        df[f"crop_{crop}"] = (df["crop"].str.lower() == crop).astype(int)
    for col in V1_FEATURES:
        if col not in df.columns:
            df[col] = 0
    if "pollen_level" in df.columns:
        df["pollen_tree"] = df["pollen_level"]
        df["pollen_grass"] = df["pollen_level"]
        df["pollen_weed"] = df["pollen_level"]

    X = df[V1_FEATURES]
    y_psi = df["psi_score"]
    y_risk = df["risk_level"]

    models_v1 = load_models("")
    if not all(k in models_v1 for k in ("psi", "risk")):
        print("  SKIP: no PSI/risk models")
        return

    scaler = models_v1["psi_scaler"]
    X_scaled = scaler.transform(X)

    psi_pred = models_v1["psi"].predict(X_scaled)
    psi_r2 = r2_score(y_psi, psi_pred)
    psi_mae = mean_absolute_error(y_psi, psi_pred)
    print(f"\n  PSI Model ({type(models_v1['psi']).__name__}):")
    print(f"    R²:  {psi_r2:.4f}")
    print(f"    MAE: {psi_mae:.1f}")

    risk_raw = models_v1["risk"].predict(X_scaled)
    if hasattr(models_v1["risk"], "_label_encoder"):
        risk_pred = models_v1["risk"]._label_encoder.inverse_transform(risk_raw)
    else:
        risk_pred = risk_raw
    risk_acc = accuracy_score(y_risk, risk_pred)
    print(f"\n  Risk Model ({type(models_v1['risk']).__name__}):")
    print(f"    Accuracy: {risk_acc:.4f}")
    from sklearn.metrics import classification_report
    print(f"\n    Classification Report:")
    print(classification_report(y_risk, risk_pred))


def validate_backend_feature_alignment():
    print("\n" + "=" * 70)
    print("BACKEND FEATURE ALIGNMENT CHECK")
    print("=" * 70)

    model_features = set(V1_FEATURES)

    backend_path = Path(__file__).resolve().parent.parent.parent / "backend" / "app" / "services" / "feature_engineering.py"
    if not backend_path.exists():
        print("  SKIP: backend not found")
        return

    from importlib.util import spec_from_file_location, module_from_spec
    spec = spec_from_file_location("feature_engineering", str(backend_path))
    fe = module_from_spec(spec)
    spec.loader.exec_module(fe)

    test_feats = fe.build_features("sunflower", 25, 60, 5, 10, 0.6, 4, 6, 166)
    backend_features = set(test_feats.keys())
    model_features = set(V1_FEATURES)

    missing_in_backend = model_features - backend_features
    extra_in_backend = backend_features - model_features

    if missing_in_backend:
        print(f"  ❌ Missing in backend: {missing_in_backend}")
    if extra_in_backend:
        print(f"  ℹ️  Extra in backend: {extra_in_backend}")
    if not missing_in_backend:
        print(f"  ✅ Backend features match model ({len(backend_features)} features)")
    
    from app.services.prediction_service import MODELS_DIR as bm_dir
    from pathlib import Path as P
    bm_path = P(bm_dir)
    print(f"  Backend model path: {bm_path}")
    print(f"  Path exists: {bm_path.exists()}")
    if bm_path.exists():
        files = [f.name for f in bm_path.glob("*.pkl")]
        print(f"  Model files: {files}")
    else:
        print(f"  ❌ Backend model path does not exist")


def test_physical_sanity():
    print("\n" + "=" * 70)
    print("PHYSICAL SANITY CHECKS")
    print("=" * 70)
    from predict import PollinationFeatures, predict

    checks_passed = 0
    checks_total = 0

    for label, features, expected_check in [
        ("Warmer = earlier flowering",
         [PollinationFeatures(**dict({"temperature_c": 20, "humidity_percent": 60, "rainfall_mm": 5,
                                      "wind_speed_kmh": 10, "ndvi": 0.6, "bee_count": 4,
                                      "bee_abundance": 20, "pollen_level": 3, "crop_type": "sunflower",
                                      "month": 6, "day_of_year": 166, "region": "Maharashtra",
                                      "sowing_date": "2025-06-15"})),
          PollinationFeatures(**dict({"temperature_c": 32, "humidity_percent": 60, "rainfall_mm": 5,
                                      "wind_speed_kmh": 10, "ndvi": 0.6, "bee_count": 4,
                                      "bee_abundance": 20, "pollen_level": 3, "crop_type": "sunflower",
                                      "month": 6, "day_of_year": 166, "region": "Maharashtra",
                                      "sowing_date": "2025-06-15"}))],
         lambda r1, r2: r2.flowering_start_doy <= r1.flowering_start_doy),
        ("Higher NDVI = higher PSI",
         [PollinationFeatures(**dict({"temperature_c": 25, "humidity_percent": 60, "rainfall_mm": 5,
                                      "wind_speed_kmh": 10, "ndvi": 0.2, "bee_count": 3,
                                      "bee_abundance": 15, "pollen_level": 2, "crop_type": "sunflower",
                                      "month": 6, "day_of_year": 166, "region": "Maharashtra",
                                      "sowing_date": "2025-06-15"})),
          PollinationFeatures(**dict({"temperature_c": 25, "humidity_percent": 60, "rainfall_mm": 5,
                                      "wind_speed_kmh": 10, "ndvi": 0.8, "bee_count": 6,
                                      "bee_abundance": 30, "pollen_level": 4, "crop_type": "sunflower",
                                      "month": 6, "day_of_year": 166, "region": "Maharashtra",
                                      "sowing_date": "2025-06-15"}))],
         lambda r1, r2: r2.psi_score >= r1.psi_score),
        ("Mustard flowers Dec/Jan (DOY ~335-365)",
         [PollinationFeatures(temperature_c=18, humidity_percent=55, rainfall_mm=1,
                              wind_speed_kmh=8, ndvi=0.45, bee_count=2, bee_abundance=11,
                              pollen_level=4, crop_type="mustard", month=11, day_of_year=320,
                              region="Rajasthan", sowing_date="2025-10-20")],
         lambda r: r.flowering_start_doy >= 300 and r.flowering_start_doy <= 365),
        ("Sunflower flowers Jun-Sep (DOY ~150-270)",
         [PollinationFeatures(temperature_c=28, humidity_percent=62, rainfall_mm=4,
                              wind_speed_kmh=10, ndvi=0.58, bee_count=4, bee_abundance=20,
                              pollen_level=3, crop_type="sunflower", month=7, day_of_year=190,
                              region="Maharashtra", sowing_date="2025-06-15")],
         lambda r: 150 <= r.flowering_start_doy <= 270),
        ("PSI is 0-100 bounded",
         [PollinationFeatures(temperature_c=10, humidity_percent=20, rainfall_mm=0,
                              wind_speed_kmh=30, ndvi=0.1, bee_count=0, bee_abundance=0,
                              pollen_level=1, crop_type="sunflower", month=1, day_of_year=1,
                              region="Maharashtra", sowing_date="2025-01-01"),
          PollinationFeatures(temperature_c=28, humidity_percent=65, rainfall_mm=5,
                              wind_speed_kmh=8, ndvi=0.7, bee_count=6, bee_abundance=30,
                              pollen_level=4, crop_type="sunflower", month=7, day_of_year=190,
                              region="Maharashtra", sowing_date="2025-06-15")],
         lambda r1, r2: 0 <= r1.psi_score <= 100 and 0 <= r2.psi_score <= 100),
    ]:
        checks_total += 1
        results = [predict(f) for f in features]
        if len(results) == 2:
            passed = expected_check(results[0], results[1])
        else:
            passed = expected_check(results[0])
        status = "PASS" if passed else "FAIL"
        if passed:
            checks_passed += 1
        print(f"  {status}: {label}")

    print(f"\n  Physical sanity: {checks_passed}/{checks_total} passed")


if __name__ == "__main__":
    print("\n" + "#" * 70)
    print("# POLLISYNC COMPREHENSIVE VALIDATION REPORT")
    print("#" * 70)

    validate_on_real_data()
    validate_all_models()
    validate_psi_models()
    test_physical_sanity()

    print("\n" + "#" * 70)
    print("# VALIDATION COMPLETE")
    print("#" * 70)
