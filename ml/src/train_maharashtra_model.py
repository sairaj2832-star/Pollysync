"""
train_maharashtra_model.py
Trains Maharashtra-specific models using real ground truth + synthetic data.
Saves as *_mh.pkl alongside existing models.

Key differences from train_improved_models.py:
  - Uses maharashtra_ground_truth.csv as primary data (real weather + GDD labels)
  - Augments with synthetic data from flower_data_large.csv
  - Adds district features (elevation, agro-climatic zone)
  - Sample weights: 5x on real data, 1x on synthetic
  - GridSearch tuned for Maharashtra-specific patterns

Usage:
    python train_maharashtra_model.py
"""

from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import r2_score, accuracy_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler, LabelEncoder
import xgboost as xgb

from maharashtra_features import (
    prepare_mh_features, compute_sample_weights, MH_V2_FEATURES, ZONE_DUMMY_COLS
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def load_maharashtra_data() -> pd.DataFrame:
    path = DATA_DIR / "maharashtra_ground_truth.csv"
    if not path.exists():
        print(f"ERROR: {path} not found. Run build_maharashtra_ground_truth.py first.")
        return pd.DataFrame()
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} ground truth rows")
    print(f"  Crops: {df['crop'].value_counts().to_dict()}")
    print(f"  Districts: {df['district'].nunique()}")
    print(f"  Years: {df['year'].min()}–{df['year'].max()}")
    return df


def load_augmented_synthetic(n_desired: int = 3000) -> pd.DataFrame:
    """Load synthetic data and filter to Maharashtra rows where possible."""
    path = DATA_DIR / "flowering_data_large.csv"
    if not path.exists():
        print("No synthetic data available.")
        return pd.DataFrame()

    df = pd.read_csv(path)
    df["data_source"] = "synthetic"

    mh_rows = df[df["region"] == "Maharashtra"].copy()
    if len(mh_rows) >= n_desired:
        print(f"Using {len(mh_rows)} synthetic Maharashtra rows")
        return mh_rows.sample(n=n_desired, random_state=42)

    other = df[df["region"] != "Maharashtra"]
    needed = n_desired - len(mh_rows)
    if len(other) >= needed:
        sampled = other.sample(n=needed, random_state=42)
        result = pd.concat([mh_rows, sampled], ignore_index=True)
    else:
        result = pd.concat([mh_rows, other], ignore_index=True)

    print(f"Using {len(result)} synthetic rows ({len(mh_rows)} from Maharashtra)")
    return result


def temporal_split_by_year(df, X, y, sample_weight=None, test_years=None):
    """Split data temporally: train on earlier years, test on later years.

    This prevents future data from leaking into training (unlike random train_test_split).
    Synthetic rows (no year column) always go to training.
    """
    if test_years is None:
        test_years = [2020, 2021]

    if "year" not in df.columns:
        df = df.copy()
        df["year"] = -1
    train_mask = ~df["year"].fillna(-1).isin(test_years)
    test_mask = df["year"].fillna(-1).isin(test_years)

    X_tr = X[train_mask.values]
    X_te = X[test_mask.values]
    y_tr = y[train_mask.values]
    y_te = y[test_mask.values]

    if sample_weight is not None:
        sw_tr = sample_weight[train_mask.values]
        sw_te = sample_weight[test_mask.values]
    else:
        sw_tr = None
        sw_te = None

    print(f"  Temporal split: train years = {sorted(df.loc[train_mask, 'year'].unique())}")
    print(f"                  test years  = {sorted(df.loc[test_mask, 'year'].unique())}")
    print(f"  Train: {len(X_tr)}, Test: {len(X_te)}")
    y_tr_a = y_tr.values if hasattr(y_tr, "values") else y_tr
    y_te_a = y_te.values if hasattr(y_te, "values") else y_te
    return X_tr, X_te, y_tr_a, y_te_a, sw_tr, sw_te


def train_flowering_model(df, X, y, sample_weight=None):
    print(f"\n--- Training Flowering Model (MH) ---")
    print(f"  Samples: {len(X)}, Features: {X.shape[1]}")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_tr, X_te, y_tr, y_te, sw_tr, sw_te = temporal_split_by_year(
        df, X_scaled, y, sample_weight
    )

    if len(X_te) == 0:
        from sklearn.model_selection import train_test_split
        X_tr, X_te, y_tr, y_te, sw_tr, sw_te = train_test_split(
            X_scaled, y, sample_weight, test_size=0.2, random_state=42
        ) if sample_weight is not None else (
            *train_test_split(X_scaled, y, test_size=0.2, random_state=42), None, None
        )

    # RF with GridSearch
    rf_grid = GridSearchCV(
        RandomForestRegressor(random_state=42, n_jobs=-1),
        {"n_estimators": [200, 300], "max_depth": [10, 14, None],
         "min_samples_split": [5, 10], "min_samples_leaf": [2, 4]},
        cv=3, scoring="r2", n_jobs=-1, verbose=0,
    )
    rf_grid.fit(X_tr, y_tr)
    rf_best = rf_grid.best_estimator_
    rf_r2 = r2_score(y_te, rf_best.predict(X_te))
    rf_mae = mean_absolute_error(y_te, rf_best.predict(X_te))
    print(f"  RF params: {rf_grid.best_params_}")
    print(f"  RF R2={rf_r2:.4f}, MAE={rf_mae:.1f}")

    # XGBoost
    xgb_model = xgb.XGBRegressor(
        n_estimators=300, max_depth=8, learning_rate=0.08,
        subsample=0.8, colsample_bytree=0.8,
        reg_alpha=0.1, reg_lambda=1.0,
        random_state=42, n_jobs=-1, verbosity=0,
    )
    if sw_tr is not None:
        xgb_model.fit(X_tr, y_tr, sample_weight=sw_tr)
    else:
        xgb_model.fit(X_tr, y_tr)
    xgb_r2 = r2_score(y_te, xgb_model.predict(X_te))
    xgb_mae = mean_absolute_error(y_te, xgb_model.predict(X_te))
    print(f"  XGB R2={xgb_r2:.4f}, MAE={xgb_mae:.1f}")

    # Feature importance comparison
    if hasattr(rf_best, "feature_names_in_"):
        fi = pd.DataFrame({
            "feature": rf_best.feature_names_in_,
            "importance": rf_best.feature_importances_,
        }).sort_values("importance", ascending=False)
        print(f"\n  Top 10 features (RF):")
        for _, r in fi.head(10).iterrows():
            print(f"    {r['feature']:25s} {r['importance']:.4f}")

    best = rf_best if rf_r2 >= xgb_r2 else xgb_model
    best_name = "RandomForest" if rf_r2 >= xgb_r2 else "XGBoost"
    print(f"  Best: {best_name}")

    try:
        best.feature_names_in_ = list(X.columns)
    except (AttributeError, TypeError):
        pass

    return best, scaler


def train_psi_and_risk(df, X, y_psi, y_risk, sample_weight=None):
    print(f"\n--- Training PSI & Risk Models (MH) ---")
    print(f"  Samples: {len(X)}, Features: {X.shape[1]}")

    from sklearn.model_selection import train_test_split

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Use temporal split if year column exists and has multiple years; else random split
    has_year = "year" in df.columns and df["year"].nunique() > 1
    if has_year:
        test_years = [2020, 2021]
        train_mask = ~df["year"].fillna(-1).isin(test_years)
        test_mask = df["year"].fillna(-1).isin(test_years)
        X_tr = X_scaled[train_mask.values]
        X_te = X_scaled[test_mask.values]
        y_psi_tr = y_psi[train_mask.values]
        y_psi_te = y_psi[test_mask.values]
        y_risk_tr = y_risk[train_mask.values]
        y_risk_te = y_risk[test_mask.values]
        sw_tr = sample_weight[train_mask.values] if sample_weight is not None else None
        sw_te = sample_weight[test_mask.values] if sample_weight is not None else None
        print(f"  Temporal split: train={train_mask.sum()} test={test_mask.sum()}")
    else:
        split = train_test_split(X_scaled, y_psi, y_risk, sample_weight,
                                 test_size=0.2, random_state=42)
        X_tr, X_te, y_psi_tr, y_psi_te, y_risk_tr, y_risk_te, sw_tr, sw_te = split
        print(f"  Random split: train={len(X_tr)} test={len(X_te)}")

    if len(X_te) == 0:
        X_tr, X_te, y_psi_tr, y_psi_te, y_risk_tr, y_risk_te, sw_tr, sw_te = train_test_split(
            X_scaled, y_psi, y_risk, sample_weight, test_size=0.2, random_state=42
        )
        print(f"  (fallback random split: train={len(X_tr)} test={len(X_te)})")

    # PSI model
    psi_rf = RandomForestRegressor(
        n_estimators=300, max_depth=12, min_samples_split=5,
        min_samples_leaf=2, random_state=42, n_jobs=-1
    )
    if sw_tr is not None:
        psi_rf.fit(X_tr, y_psi_tr, sample_weight=sw_tr)
    else:
        psi_rf.fit(X_tr, y_psi_tr)
    psi_r2 = r2_score(y_psi_te, psi_rf.predict(X_te))
    psi_mae = mean_absolute_error(y_psi_te, psi_rf.predict(X_te))

    psi_xgb = xgb.XGBRegressor(
        n_estimators=200, max_depth=6, learning_rate=0.1,
        random_state=42, n_jobs=-1, verbosity=0
    )
    psi_xgb.fit(X_tr, y_psi_tr)
    psi_xgb_r2 = r2_score(y_psi_te, psi_xgb.predict(X_te))
    psi_xgb_mae = mean_absolute_error(y_psi_te, psi_xgb.predict(X_te))

    psi_model = psi_rf if psi_r2 >= psi_xgb_r2 else psi_xgb
    psi_name = "RF" if psi_r2 >= psi_xgb_r2 else "XGB"
    print(f"  PSI: RF R2={psi_r2:.4f} MAE={psi_mae:.1f} | "
          f"XGB R2={psi_xgb_r2:.4f} MAE={psi_xgb_mae:.1f} -> {psi_name}")

    # Risk model
    risk_le = LabelEncoder()
    y_risk_enc = risk_le.fit_transform(y_risk)
    y_risk_tr_enc = risk_le.transform(y_risk_tr)
    y_risk_te_enc = risk_le.transform(y_risk_te)

    risk_rf = RandomForestClassifier(
        n_estimators=300, max_depth=10, min_samples_split=5,
        min_samples_leaf=2, random_state=42, n_jobs=-1
    )
    risk_rf.fit(X_tr, y_risk_tr)
    risk_rf_acc = accuracy_score(y_risk_te, risk_rf.predict(X_te))

    risk_xgb = xgb.XGBClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.1,
        random_state=42, n_jobs=-1, verbosity=0
    )
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
            m.feature_names_in_ = list(X.columns)
        except (AttributeError, TypeError):
            pass

    return psi_model, risk_model, scaler


def train_on_available_psi(df_f, df_psi, sample_weight_f, sample_weight_psi):
    """Train PSI and risk on whichever data is available."""
    psi_target = None
    risk_target = None

    if "psi_score" in df_f.columns:
        psi_target = df_f["psi_score"]
        risk_target = df_f["risk_level"]
        print(f"\nUsing PSI data from ground truth: {len(df_f)} rows")
    elif df_psi is not None:
        psi_target = df_psi.get("psi_score")
        risk_target = df_psi.get("risk_level")
        print(f"\nUsing PSI data from synthetic: {len(df_psi)} rows")

    if psi_target is None:
        print("No PSI target available. Skipping PSI/risk training.")
        return None, None, None

    X_psi = prepare_mh_features(df_f if "psi_score" in df_f.columns else df_psi)
    psi_df = df_f if "psi_score" in df_f.columns else df_psi
    return train_psi_and_risk(psi_df, X_psi, psi_target, risk_target,
                              sample_weight_f if "psi_score" in df_f.columns else sample_weight_psi)


def main():
    print("=" * 60)
    print("MAHARASHTRA-SPECIFIC MODEL TRAINING")
    print("=" * 60)

    # Load data
    df_real = load_maharashtra_data()
    df_synth = load_augmented_synthetic(3000)

    # Combine: real data gets data_source column, synthetic gets it too
    if df_real.empty and df_synth.empty:
        print("No training data available.")
        return

    df_f = pd.concat([df_real, df_synth], ignore_index=True) if not df_real.empty else df_synth
    if "data_source" not in df_f.columns:
        df_f["data_source"] = "synthetic"

    # Compute sample weights (5x for real data)
    sample_weights = compute_sample_weights(df_f, real_weight=5.0)
    real_count = (df_f["data_source"].str.contains("nasa_power", na=False)).sum()
    synth_count = len(df_f) - real_count
    print(f"\nData composition: {real_count} real + {synth_count} synthetic = {len(df_f)} total")

    # Prepare features for flowering model
    X_f = prepare_mh_features(df_f, use_v2=True)
    y_f = df_f["start_doy"]
    print(f"Flowering feature matrix: {X_f.shape}")

    # Train flowering model (with temporal split to prevent leakage)
    f_model, f_scaler = train_flowering_model(df_f, X_f, y_f, sample_weights)

    # Save flowering model
    joblib.dump(f_model, MODELS_DIR / "flowering_model_mh.pkl")
    joblib.dump(f_scaler, MODELS_DIR / "flowering_scaler_mh.pkl")
    print(f"\nSaved flowering_model_mh.pkl + flowering_scaler_mh.pkl")

    # Train PSI and risk
    df_psi = None
    psi_path = DATA_DIR / "psi_data.csv"
    if psi_path.exists():
        df_psi = pd.read_csv(psi_path)
        for c in ["mustard", "sunflower", "cotton"]:
            df_psi[f"crop_{c}"] = (df_psi["crop"].str.lower() == c).astype(int)

    sw_psi = compute_sample_weights(df_psi, real_weight=5.0) if df_psi is not None else None
    psi_model, risk_model, pr_scaler = train_on_available_psi(df_f, df_psi, sample_weights, sw_psi)

    if psi_model is not None:
        joblib.dump(psi_model, MODELS_DIR / "psi_model_mh.pkl")
        joblib.dump(pr_scaler, MODELS_DIR / "psi_scaler_mh.pkl")
        joblib.dump(risk_model, MODELS_DIR / "risk_model_mh.pkl")
        joblib.dump(pr_scaler, MODELS_DIR / "risk_scaler_mh.pkl")
        print("Saved psi_model_mh.pkl, risk_model_mh.pkl + scalers")

    print(f"\n{'=' * 60}")
    print(f"All Maharashtra models saved to {MODELS_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()

