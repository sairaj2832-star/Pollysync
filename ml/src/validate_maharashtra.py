"""
validate_maharashtra.py
Comprehensive validation of Maharashtra-specific models.
  - Leave-one-district-out cross-validation
  - Physical sanity checks
  - General model vs MH model comparison
  - District-level accuracy analysis

Usage:
    python validate_maharashtra.py
"""

from pathlib import Path
import sys
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error

sys.path.append(str(Path(__file__).parent))
from maharashtra_features import prepare_mh_features

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

MAHARASHTRA_DISTRICTS = [
    "nashik", "pune", "solapur", "aurangabad", "nagpur",
    "amravati", "kolhapur", "satara", "jalgaon", "latur",
]


def load_mh_model(prefix="_mh"):
    models = {}
    for name in ("flowering", "psi", "risk"):
        m_path = MODELS_DIR / f"{name}_model{prefix}.pkl"
        s_path = MODELS_DIR / f"{name}_scaler{prefix}.pkl"
        if m_path.exists() and s_path.exists():
            models[name] = joblib.load(str(m_path))
            models[f"{name}_scaler"] = joblib.load(str(s_path))
            print(f"  Loaded {name}_model{prefix}.pkl")
    return models


def load_general_model():
    return load_mh_model("")


def validate_leave_one_district():
    print("\n" + "=" * 70)
    print("LEAVE-ONE-DISTRICT-OUT CROSS-VALIDATION")
    print("=" * 70)

    path = DATA_DIR / "maharashtra_ground_truth.csv"
    if not path.exists():
        print("  SKIP: no ground truth data")
        return

    df = pd.read_csv(path)
    district_scores = []

    for held_out in MAHARASHTRA_DISTRICTS:
        train = df[df["district"] != held_out].copy()
        test = df[df["district"] == held_out].copy()

        if len(test) < 5:
            print(f"  {held_out}: too few test samples ({len(test)}), skipping")
            continue

        X_tr = prepare_mh_features(train)
        y_tr = train["start_doy"]
        X_te = prepare_mh_features(test)
        y_te = test["start_doy"]

        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import r2_score, mean_absolute_error

        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr)
        X_te_s = scaler.transform(X_te)

        model = RandomForestRegressor(
            n_estimators=200, max_depth=None,
            min_samples_leaf=2, min_samples_split=5,
            random_state=42, n_jobs=-1,
        )
        model.fit(X_tr_s, y_tr)
        y_pred = model.predict(X_te_s)

        r2 = r2_score(y_te, y_pred)
        mae = mean_absolute_error(y_te, y_pred)

        district_scores.append({"district": held_out, "r2": r2, "mae": mae,
                                "train_samples": len(train), "test_samples": len(test)})
        print(f"  {held_out:12s} R2={r2:.4f} MAE={mae:.1f}d  train={len(train)} test={len(test)}")

    if district_scores:
        scores_df = pd.DataFrame(district_scores)
        print(f"\n  Overall:")
        print(f"    Mean R2:  {scores_df['r2'].mean():.4f} (+/- {scores_df['r2'].std():.4f})")
        print(f"    Mean MAE: {scores_df['mae'].mean():.1f} days")
        return scores_df


def validate_physical_sanity():
    print("\n" + "=" * 70)
    print("PHYSICAL SANITY CHECKS (MH Models)")
    print("=" * 70)

    models = load_mh_model("_mh")
    if "flowering" not in models:
        print("  SKIP: MH models not found")
        return

    f_model = models["flowering"]
    f_scaler = models["flowering_scaler"]

    def _predict_doy(temp, humidity=60, rainfall=5, wind=10, ndvi=0.6,
                     bee_richness=4, bee_count=20, pollen=3, crop="sunflower",
                     month=6, doy=166, district="nashik"):
        row = {
            "temp_7d_mean": temp, "humidity": humidity, "rainfall_7d": rainfall,
            "wind_speed": wind, "ndvi": ndvi,
            "day_of_year": doy, "month": month,
            "crop_mustard": 1 if crop == "mustard" else 0,
            "crop_wheat": 1 if crop == "wheat" else 0,
            "crop_sunflower": 1 if crop == "sunflower" else 0,
            "crop_rice": 1 if crop == "rice" else 0,
            "crop_cotton": 1 if crop == "cotton" else 0,
            "bee_richness": bee_richness, "bee_count": bee_count,
            "pollen_tree": pollen, "pollen_grass": pollen, "pollen_weed": pollen,
            "elevation_m": 500, "district": district,
        }
        from maharashtra_features import add_district_features, add_engineered_features
        df = pd.DataFrame([row])
        df = add_district_features(df)
        df = add_engineered_features(df)
        try:
            expected_cols = list(f_model.feature_names_in_)
        except (AttributeError, Exception):
            expected_cols = list(f_scaler.feature_names_in_) if hasattr(f_scaler, 'feature_names_in_') else [
                "temp_7d_mean", "humidity", "rainfall_7d", "wind_speed", "ndvi",
                "day_of_year", "month",
                "crop_mustard", "crop_wheat", "crop_sunflower", "crop_rice", "crop_cotton",
                "bee_richness", "bee_count", "pollen_tree", "pollen_grass", "pollen_weed",
                "elevation_m",
                "zone_western_ghats", "zone_scarce_rainfall", "zone_marathwada",
                "zone_vidarbha", "zone_konkan", "zone_khandesh",
                "temp_humidity", "temp_ndvi", "humidity_rainfall",
                "temp_sq", "ndvi_sq", "bee_total", "temp_wind",
            ]
        for c in expected_cols:
            if c not in df.columns:
                df[c] = 0
        df = df[expected_cols]
        X_s = f_scaler.transform(df)
        pred = f_model.predict(X_s)[0]
        return max(1, min(365, int(round(pred))))

    checks = []
    checks_passed = 0
    checks_total = 0

    # 1. Warmer = earlier flowering (sunflower)
    checks_total += 1
    cool = _predict_doy(20, crop="sunflower", month=6, doy=166)
    warm = _predict_doy(32, crop="sunflower", month=6, doy=166)
    passed = warm <= cool
    checks_passed += passed
    checks.append(f"  {'PASS' if passed else 'FAIL'}: Warm->earlier sunflower: {cool}d vs {warm}d")

    # 2. Mustard flowers Dec/Jan range
    checks_total += 1
    mustard_doy = _predict_doy(18, crop="mustard", month=11, doy=320)
    passed = 300 <= mustard_doy <= 365
    checks_passed += passed
    checks.append(f"  {'PASS' if passed else 'FAIL'}: Mustard DOY in range: {mustard_doy}")

    # 3. Sunflower flowers Jun-Sep range
    checks_total += 1
    sunf_doy = _predict_doy(28, crop="sunflower", month=7, doy=190)
    passed = 150 <= sunf_doy <= 270
    checks_passed += passed
    checks.append(f"  {'PASS' if passed else 'FAIL'}: Sunflower DOY in range: {sunf_doy}")

    # 4. Wheat (Rabi, winter) flowers at higher DOY (later calendar) than Rice (Kharif, summer)
    checks_total += 1
    rice_doy = _predict_doy(28, crop="rice", month=7, doy=190)
    wheat_doy = _predict_doy(18, crop="wheat", month=11, doy=320)
    passed = wheat_doy > rice_doy
    checks_passed += passed
    checks.append(f"  {'PASS' if passed else 'FAIL'}: Wheat DOY ({wheat_doy}) > Rice DOY ({rice_doy}) (Rabi later than Kharif)")

    # 5. Higher NDVI = slightly later (better veg = more growth)
    checks_total += 1
    low_ndvi = _predict_doy(25, ndvi=0.3, crop="sunflower", month=6, doy=166)
    high_ndvi = _predict_doy(25, ndvi=0.8, crop="sunflower", month=6, doy=166)
    passed = abs(high_ndvi - low_ndvi) < 30
    checks_passed += passed
    checks.append(f"  {'PASS' if passed else 'FAIL'}: NDVI stability: {low_ndvi}d vs {high_ndvi}d")

    # 6. Kolhapur (cool, wet) produces later flowering than Solapur (hot, dry)
    checks_total += 1
    kolhapur = _predict_doy(24, district="kolhapur", crop="sunflower", month=6, doy=166)
    solapur = _predict_doy(28, district="solapur", crop="sunflower", month=6, doy=166)
    passed = kolhapur >= solapur
    checks_passed += passed
    checks.append(f"  {'PASS' if passed else 'FAIL'}: Kolhapur DOY ({kolhapur}) >= Solapur DOY ({solapur})")

    for c in checks:
        print(c)
    print(f"\n  Physical sanity: {checks_passed}/{checks_total} passed")


def compare_models():
    print("\n" + "=" * 70)
    print("GENERAL MODEL vs MH MODEL COMPARISON")
    print("=" * 70)

    path = DATA_DIR / "maharashtra_ground_truth.csv"
    if not path.exists():
        print("  SKIP: no ground truth data")
        return

    df = pd.read_csv(path)
    X = prepare_mh_features(df)
    y = df["start_doy"]

    general = load_general_model()
    mh = load_mh_model("_mh")

    if "flowering" not in general or "flowering" not in mh:
        print("  SKIP: models not found")
        return

    # General model: use only V1 features
    from maharashtra_features import MH_V2_FEATURES
    v1_features = [c for c in MH_V2_FEATURES
                   if c not in ("elevation_m", "zone_western_ghats", "zone_scarce_rainfall",
                                "zone_marathwada", "zone_vidarbha", "zone_konkan", "zone_khandesh",
                                "temp_humidity", "temp_ndvi", "humidity_rainfall",
                                "temp_sq", "ndvi_sq", "bee_total", "temp_wind")]

    # General model prediction
    gen_model = general["flowering"]
    gen_scaler = general["flowering_scaler"]
    if hasattr(gen_model, "feature_names_in_"):
        gen_cols = list(gen_model.feature_names_in_)
    else:
        gen_cols = v1_features

    X_gen = df.copy()
    for c in gen_cols:
        if c not in X_gen.columns and c in X.columns:
            X_gen[c] = X[c]
    X_gen = X_gen[gen_cols]
    gen_scaled = gen_scaler.transform(X_gen)
    gen_pred = gen_model.predict(gen_scaled)
    gen_r2 = r2_score(y, gen_pred)
    gen_mae = mean_absolute_error(y, gen_pred)

    # MH model prediction
    mh_model = mh["flowering"]
    mh_scaler = mh["flowering_scaler"]
    if hasattr(mh_model, "feature_names_in_"):
        mh_cols = list(mh_model.feature_names_in_)
    else:
        mh_cols = list(X.columns)

    X_mh = X[mh_cols]
    mh_scaled = mh_scaler.transform(X_mh)
    mh_pred = mh_model.predict(mh_scaled)
    mh_r2 = r2_score(y, mh_pred)
    mh_mae = mean_absolute_error(y, mh_pred)

    print(f"\n  {'Model':20s} {'R2':>8s} {'MAE':>8s}")
    print(f"  {'-'*20} {'-'*8} {'-'*8}")
    print(f"  {'General (V1)':20s} {gen_r2:>8.4f} {gen_mae:>8.1f}d")
    print(f"  {'MH-Specific (V2)':20s} {mh_r2:>8.4f} {mh_mae:>8.1f}d")
    improvement = ((gen_mae - mh_mae) / gen_mae) * 100
    print(f"\n  MAE improvement: {improvement:.1f}%")
    print(f"  {'Better' if mh_r2 > gen_r2 else 'Worse'}: MH model {'outperforms' if mh_r2 > gen_r2 else 'underperforms'} general model")

    return {"general_r2": gen_r2, "general_mae": gen_mae,
            "mh_r2": mh_r2, "mh_mae": mh_mae}


def validate_against_real_data():
    print("\n" + "=" * 70)
    print("VALIDATION AGAINST ORIGINAL REAL DATA (flowering_data_real.csv)")
    print("=" * 70)

    path = DATA_DIR / "flowering_data_real.csv"
    if not path.exists():
        print("  SKIP: no real data file")
        return

    df = pd.read_csv(path)
    y = df["start_doy"]

    mh = load_mh_model("_mh")
    general = load_general_model()

    if "flowering" not in mh or "flowering" not in general:
        print("  SKIP: models not found")
        return

    result = {}

    for label, models in [("General (V1)", general), ("MH-Specific (V2)", mh)]:
        model = models["flowering"]
        scaler = models["flowering_scaler"]

        try:
            expected_cols = list(model.feature_names_in_)
        except (Exception):
            expected_cols = list(scaler.feature_names_in_) if hasattr(scaler, 'feature_names_in_') else []

        X = df.copy()
        for c in expected_cols:
            if c not in X.columns:
                if c.startswith("zone_") or c.startswith("dist_"):
                    X[c] = 0
                elif c in ("elevation_m",):
                    X[c] = 500
                elif c in ("temp_humidity", "temp_ndvi", "humidity_rainfall",
                           "temp_sq", "ndvi_sq", "bee_total", "temp_wind"):
                    X[c] = 0
                elif c in ("bee_count",):
                    X[c] = 15
                else:
                    X[c] = 0

        real_cols = [c for c in expected_cols if c in X.columns]
        missing = set(expected_cols) - set(X.columns)
        if missing:
            print(f"  {label}: missing {missing}")

        X = X[expected_cols]
        X_s = scaler.transform(X)
        y_pred = model.predict(X_s)
        r2 = r2_score(y, y_pred)
        mae = mean_absolute_error(y, y_pred)

        print(f"  {label:20s} R2={r2:.4f} MAE={mae:.1f}d  n={len(df)}")
        result[label] = {"r2": r2, "mae": mae}

    return result


def main():
    print("=" * 70)
    print("MAHARASHTRA MODEL VALIDATION REPORT")
    print("=" * 70)

    validate_leave_one_district()
    validate_physical_sanity()
    compare_models()
    validate_against_real_data()

    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
