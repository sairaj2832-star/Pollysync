"""
debug_predict.py
Debug version to identify why trained models aren't being used.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from datetime import date
import pandas as pd
import joblib
from predict import PollinationFeatures, predict, _build_feature_dict

def debug_prediction():
    """Debug the prediction pipeline."""
    print("🔍 DEBUGGING PREDICTION PIPELINE\n")
    print("=" * 70)
    
    # Load models
    MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
    
    print("📂 Checking models directory:", MODELS_DIR)
    print("   Files:", [f.name for f in MODELS_DIR.glob("*.pkl")])
    print()
    
    # Load each model
    try:
        flowering_model = joblib.load(MODELS_DIR / "flowering_model.pkl")
        flowering_scaler = joblib.load(MODELS_DIR / "flowering_scaler.pkl")
        psi_model = joblib.load(MODELS_DIR / "psi_model.pkl")
        psi_scaler = joblib.load(MODELS_DIR / "psi_scaler.pkl")
        risk_model = joblib.load(MODELS_DIR / "risk_model.pkl")
        risk_scaler = joblib.load(MODELS_DIR / "risk_scaler.pkl")
        print("✅ All models loaded successfully")
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        return
    
    # Test features
    features = PollinationFeatures(
        temperature_c=27.5,
        humidity_percent=62.0,
        rainfall_mm=4.2,
        wind_speed_kmh=10.0,
        ndvi=0.58,
        bee_count=4,
        bee_abundance=28,
        pollen_level=3,
        crop_type="sunflower",
        month=7,
        day_of_year=190,
        region="Maharashtra",
        sowing_date="2025-06-15",
    )
    
    print("\n📊 Test Features:")
    print(f"   Crop: {features.crop_type}")
    print(f"   Region: {features.region}")
    print(f"   Temp: {features.temperature_c}°C")
    print(f"   NDVI: {features.ndvi}")
    print()
    
    # Build feature dict
    feature_dict = _build_feature_dict(features)
    df = pd.DataFrame([feature_dict])
    
    print("📋 Feature DataFrame columns:")
    print(f"   {df.columns.tolist()}")
    print()
    
    # Check model expectations
    if hasattr(flowering_model, 'feature_names_in_'):
        expected_cols = flowering_model.feature_names_in_
        print("🔢 Model expects these columns:")
        print(f"   {expected_cols}")
        print()
        
        # Check if all expected columns exist
        missing_cols = [col for col in expected_cols if col not in df.columns]
        extra_cols = [col for col in df.columns if col not in expected_cols]
        
        if missing_cols:
            print("⚠️  Missing columns:", missing_cols)
            # Add missing columns
            for col in missing_cols:
                df[col] = 0
            print("   Added missing columns with default value 0")
        else:
            print("✅ All expected columns present")
        
        if extra_cols:
            print("ℹ️  Extra columns (ignored):", extra_cols[:5])
        
        # Reorder to match model
        df = df[expected_cols]
        print("✅ DataFrame reordered to match model")
        print()
    
    # Try prediction
    try:
        print("🚀 Attempting prediction...")
        X_scaled = flowering_scaler.transform(df)
        prediction = flowering_model.predict(X_scaled)
        print(f"✅ Prediction successful: {prediction[0]:.2f}")
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
    
    # Now try the full predict function
    print("\n" + "=" * 70)
    print("🔄 Running full predict() function...")
    result = predict(features)
    print(f"✅ Result source: {result.source}")
    print(f"   Flowering start DOY: {result.flowering_start_doy}")
    print(f"   PSI Score: {result.psi_score}")
    print(f"   Risk Level: {result.risk_level}")
    print(f"   Gap Days: {result.gap_days}")

if __name__ == "__main__":
    debug_prediction()