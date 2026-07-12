"""
train_model.py - Fixed version saving all scalers
"""

from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, accuracy_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Feature columns must match what predict.py expects
FEATURE_COLS = [
    "temp_7d_mean", "humidity", "rainfall_7d", "wind_speed", "ndvi",
    "day_of_year", "month",
    "crop_mustard", "crop_sunflower", "crop_cotton",
    "bee_richness", "bee_count", "pollen_tree", "pollen_grass", "pollen_weed",
]

def _onehot_crop(df: pd.DataFrame, crop_col: str = "crop") -> pd.DataFrame:
    df = df.copy()
    for c in ["mustard", "sunflower", "cotton"]:
        df[f"crop_{c}"] = (df[crop_col].str.lower() == c).astype(int)
    return df

def _fill_missing_features(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing features with appropriate default values."""
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

def _flowering_data_path() -> Path:
    """Prefer larger datasets for training."""
    datasets = [
        "flowering_data_large.csv",
        "flowering_data_with_bees.csv", 
        "flowering_data_real.csv",
        "flowering_data.csv"
    ]
    
    for name in datasets:
        path = DATA_DIR / name
        if path.exists():
            print(f"📂 Training on: {name}")
            return path
    
    raise FileNotFoundError(
        "No flowering data CSV found. Run generate_more_data.py or collect_training_data.py first."
    )

def train_flowering_model():
    """Train the flowering date prediction model."""
    df = pd.read_csv(_flowering_data_path())
    
    # Prepare features
    df = _onehot_crop(df)
    df = _fill_missing_features(df)
    
    # Create features and target
    X = df[FEATURE_COLS]
    y = df["start_doy"]
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    
    print(f"   Training samples: {len(X_train)}")
    print(f"   Test samples: {len(X_test)}")
    
    # Train model
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        min_samples_split=10,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)
    train_r2 = r2_score(y_train, train_pred)
    test_r2 = r2_score(y_test, test_pred)
    test_mae = mean_absolute_error(y_test, test_pred)
    
    print(f"   Train R²: {train_r2:.3f}")
    print(f"   Test R²: {test_r2:.3f}")
    print(f"   Test MAE: {test_mae:.1f} days")
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='r2')
    print(f"   Cross-validation R²: {cv_scores.mean():.3f} (±{cv_scores.std():.3f})")
    
    # Save model and scaler with feature names
    model.feature_names_in_ = X.columns.tolist()
    joblib.dump(model, MODELS_DIR / "flowering_model.pkl")
    joblib.dump(scaler, MODELS_DIR / "flowering_scaler.pkl")
    print(f"✅ Saved flowering_model.pkl and flowering_scaler.pkl")
    
    return model, scaler

def train_psi_and_risk_models():
    """Train the PSI and risk models."""
    # Find PSI data
    psi_path = DATA_DIR / "psi_data.csv"
    if not psi_path.exists():
        print("⚠️  psi_data.csv not found - generating synthetic PSI data")
        # Generate synthetic PSI data if needed
        from generate_data import generate_psi_data
        generate_psi_data()
        df = pd.read_csv(psi_path)
    else:
        df = pd.read_csv(psi_path)
    
    # Prepare features
    df = _onehot_crop(df)
    df = _fill_missing_features(df)
    
    if "pollen_level" in df.columns:
        df["pollen_tree"] = df["pollen_level"]
        df["pollen_grass"] = df["pollen_level"]
        df["pollen_weed"] = df["pollen_level"]
    
    X = df[FEATURE_COLS]
    y_psi = df["psi_score"]
    y_risk = df["risk_level"]
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split data
    X_train, X_test, y_psi_train, y_psi_test, y_risk_train, y_risk_test = train_test_split(
        X_scaled, y_psi, y_risk, test_size=0.2, random_state=42
    )
    
    # Train PSI model
    psi_model = RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        min_samples_split=10,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1
    )
    psi_model.fit(X_train, y_psi_train)
    
    psi_pred = psi_model.predict(X_test)
    psi_r2 = r2_score(y_psi_test, psi_pred)
    psi_mae = mean_absolute_error(y_psi_test, psi_pred)
    
    print(f"\n📊 PSI Model:")
    print(f"   R²: {psi_r2:.3f}")
    print(f"   MAE: {psi_mae:.1f}")
    
    psi_model.feature_names_in_ = X.columns.tolist()
    joblib.dump(psi_model, MODELS_DIR / "psi_model.pkl")
    joblib.dump(scaler, MODELS_DIR / "psi_scaler.pkl")  # Save PSI scaler
    print(f"✅ Saved psi_model.pkl and psi_scaler.pkl")
    
    # Train risk model
    risk_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_split=10,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1
    )
    risk_model.fit(X_train, y_risk_train)
    
    risk_pred = risk_model.predict(X_test)
    risk_acc = accuracy_score(y_risk_test, risk_pred)
    
    print(f"\n📊 Risk Model:")
    print(f"   Accuracy: {risk_acc:.3f}")
    
    risk_model.feature_names_in_ = X.columns.tolist()
    joblib.dump(risk_model, MODELS_DIR / "risk_model.pkl")
    joblib.dump(scaler, MODELS_DIR / "risk_scaler.pkl")  # Save risk scaler
    print(f"✅ Saved risk_model.pkl and risk_scaler.pkl")
    
    return psi_model, risk_model, scaler

def main():
    print("🚀 Training PolliSync ML Models\n")
    
    # Train flowering model
    print("📊 Training Flowering Model...")
    train_flowering_model()
    
    # Train PSI and risk models
    print("\n📊 Training PSI and Risk Models...")
    train_psi_and_risk_models()
    
    print(f"\n✅ All models saved to {MODELS_DIR}")
    print("\n📋 Next steps:")
    print("   1. Run: python debug_predict.py to verify models load correctly")
    print("   2. Run: python test_demo_request.py to test predictions")

if __name__ == "__main__":
    main()

