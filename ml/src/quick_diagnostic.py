"""
debug_predict_v2.py
Detailed debug to see why models aren't being used.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from datetime import date
import pandas as pd
import joblib
from predict import PollinationFeatures, predict, _build_feature_dict, _load_model_with_scaler

def debug_prediction_detailed():
    """Detailed debug of prediction pipeline."""
    print("🔍 DETAILED DEBUGGING\n")
    print("=" * 70)
    
    MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
    
    # Load models using the same function as predict.py
    print("📂 Loading models with _load_model_with_scaler():")
    flowering_model, flowering_scaler = _load_model_with_scaler("flowering_model.pkl")
    psi_model, psi_scaler = _load_model_with_scaler("psi_model.pkl")
    risk_model, risk_scaler = _load_model_with_scaler("risk_model.pkl")
    print()
    
    # Check if models are loaded
    print(f"📊 Model status:")
    print(f"   flowering_model: {flowering_model is not None}")
    print(f"   flowering_scaler: {flowering_scaler is not None}")
    print(f"   psi_model: {psi_model is not None}")
    print(f"   psi_scaler: {psi_scaler is not None}")
    print(f"   risk_model: {risk_model is not None}")
    print(f"   risk_scaler: {risk_scaler is not None}")
    print()
    
    # Create test features
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
    
    print("📊 Test Features:")
    print(f"   Crop: {features.crop_type}")
    print(f"   Region: {features.region}")
    print(f"   Temp: {features.temperature_c}°C")
    print(f"   NDVI: {features.ndvi}")
    print()
    
    # Build feature vector
    feature_dict = _build_feature_dict(features)
    df = pd.DataFrame([feature_dict])
    
    print("📋 Feature DataFrame:")
    print(f"   Columns: {df.columns.tolist()}")
    print(f"   Shape: {df.shape}")
    print()
    
    # Try prediction step by step
    if flowering_model is not None and flowering_scaler is not None:
        print("🚀 Attempting prediction with trained model...")
        
        try:
            # Check feature names
            if hasattr(flowering_model, 'feature_names_in_'):
                expected_cols = flowering_model.feature_names_in_
                print(f"   Model expects {len(expected_cols)} features")
                
                # Check if all expected columns exist
                missing_cols = [col for col in expected_cols if col not in df.columns]
                if missing_cols:
                    print(f"   ⚠️  Missing columns: {missing_cols}")
                    for col in missing_cols:
                        df[col] = 0
                    print(f"   ✅ Added missing columns with default value 0")
                
                # Reorder columns
                df = df[expected_cols]
                print(f"   ✅ Reordered DataFrame to match model")
            else:
                print("   ℹ️  Model doesn't have feature_names_in_ attribute")
            
            # Scale
            print(f"   Scaling features...")
            X_scaled = flowering_scaler.transform(df)
            print(f"   ✅ Scaled features: shape {X_scaled.shape}")
            
            # Predict
            print(f"   Making prediction...")
            prediction = flowering_model.predict(X_scaled)
            print(f"   ✅ Prediction: {prediction[0]:.2f}")
            start_doy = int(round(prediction[0]))
            start_doy = max(1, min(365, start_doy))
            print(f"   ✅ Clamped DOY: {start_doy}")
            
            print("\n🎯 TRAINED MODEL PREDICTION SUCCESSFUL!")
            print(f"   Predicted flowering DOY: {start_doy}")
            
        except Exception as e:
            print(f"   ❌ Prediction failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Flowering model or scaler not loaded")
    
    print("\n" + "=" * 70)
    print("🔄 Now running full predict() function...")
    result = predict(features)
    print(f"\n📊 Result:")
    print(f"   Source: {result.source}")
    print(f"   Flowering DOY: {result.flowering_start_doy}-{result.flowering_end_doy}")
    print(f"   PSI: {result.psi_score}")
    print(f"   Risk: {result.risk_level}")
    print(f"   Gap Days: {result.gap_days}")

if __name__ == "__main__":
    debug_prediction_detailed()