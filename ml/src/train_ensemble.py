"""
train_ensemble.py
Advanced ensemble training:
  - Stacking: XGBoost + RandomForest + GDD model predictions
  - Uncertainty quantification via quantile regression
  - Blending GDD physics with ML flexibility

Usage: python train_ensemble.py
"""

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))

import joblib
import pandas as pd
import numpy as np
from datetime import date, timedelta
from sklearn.ensemble import RandomForestRegressor, StackingRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import RidgeCV
import xgboost as xgb

import warnings
warnings.filterwarnings("ignore")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

V1_FEATURES = [
    "temp_7d_mean", "humidity", "rainfall_7d", "wind_speed", "ndvi",
    "day_of_year", "month",
    "crop_mustard", "crop_wheat", "crop_sunflower", "crop_rice", "crop_cotton",
    "bee_richness", "bee_count", "pollen_tree", "pollen_grass", "pollen_weed",
]


def make_gdd_features(temp_7d_mean, crop_type, month, day_of_year, sowing_doy=None):
    """Generate GDD-based flowering estimate as a feature."""
    from gdd_model import CROP_PARAMS
    crop = crop_type.lower() if isinstance(crop_type, str) else "sunflower"
    params = CROP_PARAMS.get(crop, CROP_PARAMS["sunflower"])
    if params.get("gdd_to_flowering") is not None:
        daily_gdd_rate = max(temp_7d_mean - params["t_base"], 0)
        if daily_gdd_rate > 0:
            days_to_flower = params["gdd_to_flowering"] / daily_gdd_rate
        else:
            days_to_flower = 999
    else:
        days_to_flower = params.get("days_to_flowering", 60)
    return max(days_to_flower, 0)


def build_dataset_with_gdd_features():
    """Build training set with GDD-based features."""
    from gdd_model import CROP_PARAMS, build_gdd_series

    df = pd.read_csv(DATA_DIR / "flowering_data_large.csv")
    for crop in ["mustard", "wheat", "sunflower", "rice", "cotton"]:
        df[f"crop_{crop}"] = (df["crop"].str.lower() == crop).astype(int)
    for col in V1_FEATURES:
        if col not in df.columns:
            df[col] = 0

    # Add GDD estimate features
    gdd_estimates = []
    for _, row in df.iterrows():
        crop = row["crop"]
        temp = row.get("temp_7d_mean", 25)
        gdd_days = make_gdd_features(temp, crop, row.get("month", 6), row.get("day_of_year", 150))
        gdd_estimates.append(gdd_days)
    df["gdd_estimate_days"] = gdd_estimates

    engineered_cols = V1_FEATURES + ["gdd_estimate_days"]
    return df, engineered_cols


def train_stacking_ensemble():
    """Train a stacking ensemble with XGBoost + RandomForest + GDD features."""
    print("=" * 60)
    print("STACKING ENSEMBLE TRAINING")
    print("=" * 60)

    df, feat_cols = build_dataset_with_gdd_features()
    X = df[feat_cols]
    y = df["start_doy"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_tr, X_te, y_tr, y_te = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    print(f"  Samples: {len(X_tr) + len(X_te)}, Features: {len(feat_cols)}")

    # Base estimators
    estimators = [
        ("rf", RandomForestRegressor(n_estimators=200, max_depth=12,
                                      min_samples_split=5, min_samples_leaf=2,
                                      random_state=42, n_jobs=-1)),
        ("xgb", xgb.XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1,
                                  subsample=0.8, random_state=42, n_jobs=-1, verbosity=0)),
        ("gbr", GradientBoostingRegressor(n_estimators=100, max_depth=4,
                                          learning_rate=0.1, random_state=42)),
    ]

    # Stacking with Ridge meta-learner
    stack = StackingRegressor(
        estimators=estimators,
        final_estimator=RidgeCV(alphas=[0.1, 1.0, 10.0]),
        cv=5,
        n_jobs=-1,
    )
    stack.fit(X_tr, y_tr)
    y_pred = stack.predict(X_te)
    r2 = r2_score(y_te, y_pred)
    mae = mean_absolute_error(y_te, y_pred)
    print(f"\n  Stacking Ensemble R²: {r2:.4f}")
    print(f"  Stacking Ensemble MAE: {mae:.1f} days")

    # Individual model comparison
    for name, model in estimators:
        model.fit(X_tr, y_tr)
        m_pred = model.predict(X_te)
        m_r2 = r2_score(y_te, m_pred)
        m_mae = mean_absolute_error(y_te, m_pred)
        print(f"  {name}: R²={m_r2:.4f}, MAE={m_mae:.1f}")

    stack.feature_names_in_ = feat_cols
    joblib.dump(stack, MODELS_DIR / "ensemble_stacking.pkl")
    joblib.dump(scaler, MODELS_DIR / "ensemble_scaler.pkl")
    print(f"\n  ✅ Saved ensemble_stacking.pkl")

    # Cross-validation
    cv_r2 = cross_val_score(stack, X_scaled, y, cv=5, scoring="r2")
    print(f"  5-fold CV R²: {cv_r2.mean():.4f} (±{cv_r2.std():.4f})")

    return stack, scaler, feat_cols


def train_quantile_model():
    """Train a quantile regression model for uncertainty intervals."""
    print("\n" + "=" * 60)
    print("QUANTILE REGRESSION FOR UNCERTAINTY")
    print("=" * 60)

    df, feat_cols = build_dataset_with_gdd_features()
    X = df[feat_cols]
    y = df["start_doy"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_tr, X_te, y_tr, y_te = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # GradientBoostingRegressor with quantile loss
    models = {}
    for alpha, name in [(0.1, "lower"), (0.5, "median"), (0.9, "upper")]:
        model = GradientBoostingRegressor(
            loss="quantile", alpha=alpha,
            n_estimators=100, max_depth=4,
            learning_rate=0.1, random_state=42,
        )
        model.fit(X_tr, y_tr)
        models[name] = model

        pred = model.predict(X_te)
        if alpha == 0.5:
            r2 = r2_score(y_te, pred)
            mae = mean_absolute_error(y_te, pred)
            print(f"  Median predictor R²: {r2:.4f}, MAE: {mae:.1f} days")

    # Coverage on test set
    lower = models["lower"].predict(X_te)
    upper = models["upper"].predict(X_te)
    covered = ((y_te >= lower) & (y_te <= upper)).mean()
    interval_width = (upper - lower).mean()
    print(f"  80% prediction interval coverage: {covered:.1%}")
    print(f"  Average interval width: {interval_width:.1f} days")

    for name, m in models.items():
        joblib.dump(m, MODELS_DIR / f"quantile_{name}.pkl")
    joblib.dump(scaler, MODELS_DIR / "quantile_scaler.pkl")
    print("  ✅ Saved quantile models")


def main():
    train_stacking_ensemble()
    train_quantile_model()
    print("\n" + "=" * 60)
    print("Done — all ensemble/quantile models saved.")
    print("=" * 60)


if __name__ == "__main__":
    main()
