"""
train_improved_models.py
Advanced model training with hyperparameter tuning, XGBoost, and feature engineering.
Saves v1 (17-feature) models as default and v2 (engineered) models as _v2 suffixed.
"""

from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import r2_score, accuracy_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

V1_FEATURES = [
    "temp_7d_mean", "humidity", "rainfall_7d", "wind_speed", "ndvi",
    "day_of_year", "month",
    "crop_mustard", "crop_wheat", "crop_sunflower", "crop_rice", "crop_cotton",
    "bee_richness", "bee_count", "pollen_tree", "pollen_grass", "pollen_weed",
]

V2_FEATURES = V1_FEATURES + [
    "temp_humidity", "temp_ndvi", "humidity_rainfall",
    "temp_sq", "ndvi_sq", "bee_total", "temp_wind",
]


def _onehot_crop(df, crop_col="crop"):
    df = df.copy()
    for c in ["mustard", "wheat", "sunflower", "rice", "cotton"]:
        df[f"crop_{c}"] = (df[crop_col].str.lower() == c).astype(int)
    return df


def _fill_missing_features(df):
    df = df.copy()
    defaults = {
        "wind_speed": df.get("wind_speed", 10.0).median() if "wind_speed" in df.columns else 10.0,
        "day_of_year": df.get("day_of_year", 150).median() if "day_of_year" in df.columns else 150,
        "month": df.get("month", 6).median() if "month" in df.columns else 6,
        "bee_richness": df.get("bee_richness", 4).median() if "bee_richness" in df.columns else 4,
        "bee_count": df.get("bee_count", 15).median() if "bee_count" in df.columns else 15,
        "pollen_tree": 3, "pollen_grass": 3, "pollen_weed": 3,
    }
    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default
        elif df[col].isna().any():
            df[col] = df[col].fillna(default)
    return df


def add_engineered_features(df):
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


def _flowering_data_path():
    for name in ["flowering_data_large.csv", "flowering_data_real.csv", "flowering_data.csv"]:
        path = DATA_DIR / name
        if path.exists():
            print(f"  Using: {name}")
            return path
    raise FileNotFoundError("No flowering data CSV found.")


def _load_psi_data():
    path = DATA_DIR / "psi_data.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    df = _onehot_crop(df)
    df = _fill_missing_features(df)
    if "pollen_level" in df.columns:
        df["pollen_tree"] = df["pollen_level"]
        df["pollen_grass"] = df["pollen_level"]
        df["pollen_weed"] = df["pollen_level"]
    return df


def train_flowering(feature_cols, add_engineered):
    df = pd.read_csv(_flowering_data_path())
    df = _onehot_crop(df)
    df = _fill_missing_features(df)
    if add_engineered:
        df = add_engineered_features(df)
    X = df[feature_cols]
    y = df["start_doy"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_tr, X_te, y_tr, y_te = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    print(f"  Train: {len(X_tr)}, Test: {len(X_te)}, Features: {len(feature_cols)}")

    # RF with GridSearch
    rf_grid = GridSearchCV(
        RandomForestRegressor(random_state=42, n_jobs=-1),
        {"n_estimators": [100, 200, 300], "max_depth": [6, 10, 14, None],
         "min_samples_split": [5, 10], "min_samples_leaf": [2, 4]},
        cv=3, scoring="r2", n_jobs=-1, verbose=0,
    )
    rf_grid.fit(X_tr, y_tr)
    rf_best = rf_grid.best_estimator_
    rf_r2 = r2_score(y_te, rf_best.predict(X_te))
    rf_mae = mean_absolute_error(y_te, rf_best.predict(X_te))
    print(f"  RF params: {rf_grid.best_params_} | R²={rf_r2:.4f}, MAE={rf_mae:.1f}")

    # XGBoost
    xgb_model = xgb.XGBRegressor(
        n_estimators=200, max_depth=6, learning_rate=0.1,
        subsample=0.8, colsample_bytree=0.8,
        random_state=42, n_jobs=-1, verbosity=0,
    )
    xgb_model.fit(X_tr, y_tr)
    xgb_r2 = r2_score(y_te, xgb_model.predict(X_te))
    xgb_mae = mean_absolute_error(y_te, xgb_model.predict(X_te))
    print(f"  XGB R²={xgb_r2:.4f}, MAE={xgb_mae:.1f}")

    best = rf_best if rf_r2 >= xgb_r2 else xgb_model
    best_name = "RandomForest" if rf_r2 >= xgb_r2 else "XGBoost"
    print(f"  Best: {best_name}")

    try:
        best.feature_names_in_ = feature_cols
    except (AttributeError, TypeError):
        pass
    return best, scaler


def train_psi_and_risk(feature_cols, add_engineered):
    df = _load_psi_data()
    if df is None:
        return None, None, None
    if add_engineered:
        df = add_engineered_features(df)
    X = df[feature_cols]
    y_psi = df["psi_score"]
    y_risk = df["risk_level"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_tr, X_te, y_psi_tr, y_psi_te, y_risk_tr, y_risk_te = train_test_split(
        X_scaled, y_psi, y_risk, test_size=0.2, random_state=42
    )

    # PSI
    psi_rf = RandomForestRegressor(n_estimators=300, max_depth=12, min_samples_split=5,
                                    min_samples_leaf=2, random_state=42, n_jobs=-1)
    psi_rf.fit(X_tr, y_psi_tr)
    psi_rf_r2 = r2_score(y_psi_te, psi_rf.predict(X_te))
    psi_rf_mae = mean_absolute_error(y_psi_te, psi_rf.predict(X_te))

    psi_xgb = xgb.XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1,
                                random_state=42, n_jobs=-1, verbosity=0)
    psi_xgb.fit(X_tr, y_psi_tr)
    psi_xgb_r2 = r2_score(y_psi_te, psi_xgb.predict(X_te))
    psi_xgb_mae = mean_absolute_error(y_psi_te, psi_xgb.predict(X_te))

    psi_model = psi_rf if psi_rf_r2 >= psi_xgb_r2 else psi_xgb
    psi_name = "RF" if psi_rf_r2 >= psi_xgb_r2 else "XGB"
    print(f"  PSI: RF R²={psi_rf_r2:.4f} MAE={psi_rf_mae:.1f} | XGB R²={psi_xgb_r2:.4f} MAE={psi_xgb_mae:.1f} -> {psi_name}")

    # Risk (encode labels for XGBoost)
    from sklearn.preprocessing import LabelEncoder
    risk_le = LabelEncoder()
    y_risk_enc = risk_le.fit_transform(y_risk)
    y_risk_tr_enc = risk_le.transform(y_risk_tr)
    y_risk_te_enc = risk_le.transform(y_risk_te)

    risk_rf = RandomForestClassifier(n_estimators=300, max_depth=10, min_samples_split=5,
                                      min_samples_leaf=2, random_state=42, n_jobs=-1)
    risk_rf.fit(X_tr, y_risk_tr)
    risk_rf_acc = accuracy_score(y_risk_te, risk_rf.predict(X_te))

    risk_xgb = xgb.XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1,
                                  random_state=42, n_jobs=-1, verbosity=0)
    risk_xgb.fit(X_tr, y_risk_tr_enc)
    risk_xgb_acc = accuracy_score(y_risk_te_enc, risk_xgb.predict(X_te))

    if risk_rf_acc >= risk_xgb_acc:
        risk_model = risk_rf
        risk_name = "RF"
    else:
        risk_model = risk_xgb
        risk_model._label_encoder = risk_le
        risk_name = "XGB"
    print(f"  Risk: RF acc={risk_rf_acc:.4f} | XGB acc={risk_xgb_acc:.4f} -> {risk_name}")

    for m in (psi_model, risk_model):
        try:
            m.feature_names_in_ = feature_cols
        except (AttributeError, TypeError):
            pass
    return psi_model, risk_model, scaler


def main():
    print("=" * 60)
    print("POLLISYNC IMPROVED MODEL TRAINING")
    print("=" * 60)

    # --- V1: 17 features (backward-compatible) ---
    print("\n--- V1: 17 Basic Features ---")
    f_model, f_scaler = train_flowering(V1_FEATURES, add_engineered=False)
    psi_model, risk_model, pr_scaler = train_psi_and_risk(V1_FEATURES, add_engineered=False)

    joblib.dump(f_model, MODELS_DIR / "flowering_model.pkl")
    joblib.dump(f_scaler, MODELS_DIR / "flowering_scaler.pkl")
    if psi_model:
        joblib.dump(psi_model, MODELS_DIR / "psi_model.pkl")
        joblib.dump(pr_scaler, MODELS_DIR / "psi_scaler.pkl")
        joblib.dump(risk_model, MODELS_DIR / "risk_model.pkl")
        joblib.dump(pr_scaler, MODELS_DIR / "risk_scaler.pkl")
        print("  ✅ Saved v1 models (default)")

    # --- V2: Engineered features ---
    print("\n--- V2: 24 Engineered Features ---")
    f_model_v2, f_scaler_v2 = train_flowering(V2_FEATURES, add_engineered=True)
    psi_v2, risk_v2, pr_scaler_v2 = train_psi_and_risk(V2_FEATURES, add_engineered=True)

    joblib.dump(f_model_v2, MODELS_DIR / "flowering_model_v2.pkl")
    joblib.dump(f_scaler_v2, MODELS_DIR / "flowering_scaler_v2.pkl")
    if psi_v2:
        joblib.dump(psi_v2, MODELS_DIR / "psi_model_v2.pkl")
        joblib.dump(pr_scaler_v2, MODELS_DIR / "psi_scaler_v2.pkl")
        joblib.dump(risk_v2, MODELS_DIR / "risk_model_v2.pkl")
        joblib.dump(pr_scaler_v2, MODELS_DIR / "risk_scaler_v2.pkl")
        print("  ✅ Saved v2 models (engineered features)")

    print(f"\n{'=' * 60}")
    print("All models saved to:", MODELS_DIR)
    print("=" * 60)


if __name__ == "__main__":
    main()
