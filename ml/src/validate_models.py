"""
validate_models.py - Fixed version with proper feature handling
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# Feature columns that match the training data
FEATURE_COLS = [
    "temp_7d_mean", "humidity", "rainfall_7d", "wind_speed", "ndvi",
    "day_of_year", "month",
    "crop_mustard", "crop_wheat", "crop_sunflower", "crop_rice", "crop_cotton",
    "bee_richness", "bee_count", "pollen_tree", "pollen_grass", "pollen_weed",
]

def prepare_features(df):
    """Prepare features in the exact format expected by the model."""
    # One-hot encode crops
    df_copy = df.copy()
    for crop in ["mustard", "wheat", "sunflower", "rice", "cotton"]:
        df_copy[f"crop_{crop}"] = (df_copy["crop"].str.lower() == crop).astype(int)
    
    # Ensure all feature columns exist
    for col in FEATURE_COLS:
        if col not in df_copy.columns:
            if col.startswith("crop_"):
                df_copy[col] = 0
            elif col in ["pollen_tree", "pollen_grass", "pollen_weed"]:
                df_copy[col] = df_copy.get("pollen_level", 3)
            else:
                df_copy[col] = df_copy.get(col, 0)
    
    return df_copy[FEATURE_COLS]

def validate_flowering_model():
    """Validate flowering model with detailed metrics."""
    # Load data
    df = pd.read_csv(DATA_DIR / "flowering_data_real.csv")
    
    # Load model and scaler
    model = joblib.load(MODELS_DIR / "flowering_model.pkl")
    scaler = joblib.load(MODELS_DIR / "flowering_scaler.pkl")
    
    # Prepare features
    X = prepare_features(df)
    y = df["start_doy"]
    
    # Scale
    X_scaled = scaler.transform(X)
    
    # Predict
    y_pred = model.predict(X_scaled)
    
    # Metrics
    r2 = r2_score(y, y_pred)
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    
    print("\n📊 Flowering Model Validation:")
    print(f"   R² Score: {r2:.4f}")
    print(f"   MAE: {mae:.2f} days")
    print(f"   RMSE: {rmse:.2f} days")
    
    # Error distribution
    errors = y - y_pred
    print(f"   Error Range: {errors.min():.2f} to {errors.max():.2f} days")
    print(f"   Error Std Dev: {errors.std():.2f} days")
    
    # Feature importance
    if hasattr(model, 'feature_importances_'):
        feature_names = model.feature_names_in_
        importances = model.feature_importances_
        print("\n📈 Top 10 Most Important Features:")
        indices = np.argsort(importances)[::-1][:10]
        for i, idx in enumerate(indices):
            print(f"   {i+1}. {feature_names[idx]}: {importances[idx]:.3f}")
    
    return r2, mae, rmse

if __name__ == "__main__":
    print("🔍 Validating PolliSync Models\n")
    validate_flowering_model()
    print("\n✅ Validation complete")