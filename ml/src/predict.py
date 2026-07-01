"""
predict.py - Completely fixed version with robust model/scaler loading
"""

import json
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path

import joblib
import pandas as pd
import numpy as np

from gdd_model import predict_flowering_date, CROP_PARAMS
from pollinator_proxy_v2 import predict_pollinator_peak_v2

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"


@dataclass(frozen=True)
class PollinationFeatures:
    temperature_c: float
    humidity_percent: float
    rainfall_mm: float
    wind_speed_kmh: float
    ndvi: float
    bee_count: int
    pollen_level: int
    crop_type: str
    month: int
    day_of_year: int
    region: str = "Maharashtra"
    sowing_date: str = None
    bee_abundance: int = 15


@dataclass
class PredictionResult:
    flowering_start_doy: int
    flowering_end_doy: int
    psi_score: int
    risk_level: str
    gap_days: int = None
    source: str = "baseline"


# Load models and scalers with explicit file checking
print("📂 Loading models from:", MODELS_DIR)
print("   Files found:", [f.name for f in MODELS_DIR.glob("*.pkl")])
print()

# Initialize all as None
flowering_model = None
flowering_scaler = None
psi_model = None
psi_scaler = None
risk_model = None
risk_scaler = None

# Load flowering model and scaler
try:
    model_path = MODELS_DIR / "flowering_model.pkl"
    scaler_path = MODELS_DIR / "flowering_scaler.pkl"
    
    if model_path.exists():
        flowering_model = joblib.load(str(model_path))
        print(f"✅ Loaded flowering_model.pkl ({type(flowering_model).__name__})")
    else:
        print("❌ flowering_model.pkl not found")
        
    if scaler_path.exists():
        flowering_scaler = joblib.load(str(scaler_path))
        print(f"✅ Loaded flowering_scaler.pkl ({type(flowering_scaler).__name__})")
    else:
        print("❌ flowering_scaler.pkl not found")
        
except Exception as e:
    print(f"⚠️  Error loading flowering models: {e}")

# Load PSI model and scaler
try:
    model_path = MODELS_DIR / "psi_model.pkl"
    scaler_path = MODELS_DIR / "psi_scaler.pkl"
    
    if model_path.exists():
        psi_model = joblib.load(str(model_path))
        print(f"✅ Loaded psi_model.pkl ({type(psi_model).__name__})")
    else:
        print("❌ psi_model.pkl not found")
        
    if scaler_path.exists():
        psi_scaler = joblib.load(str(scaler_path))
        print(f"✅ Loaded psi_scaler.pkl ({type(psi_scaler).__name__})")
    else:
        print("❌ psi_scaler.pkl not found")
        
except Exception as e:
    print(f"⚠️  Error loading PSI models: {e}")

# Load Risk model and scaler
try:
    model_path = MODELS_DIR / "risk_model.pkl"
    scaler_path = MODELS_DIR / "risk_scaler.pkl"
    
    if model_path.exists():
        risk_model = joblib.load(str(model_path))
        print(f"✅ Loaded risk_model.pkl ({type(risk_model).__name__})")
    else:
        print("❌ risk_model.pkl not found")
        
    if scaler_path.exists():
        risk_scaler = joblib.load(str(scaler_path))
        print(f"✅ Loaded risk_scaler.pkl ({type(risk_scaler).__name__})")
    else:
        print("❌ risk_scaler.pkl not found")
        
except Exception as e:
    print(f"⚠️  Error loading risk models: {e}")

print()
print("📊 Model Status Summary:")
print(f"   Flowering Model: {'✅' if flowering_model else '❌'}")
print(f"   Flowering Scaler: {'✅' if flowering_scaler else '❌'}")
print(f"   PSI Model: {'✅' if psi_model else '❌'}")
print(f"   PSI Scaler: {'✅' if psi_scaler else '❌'}")
print(f"   Risk Model: {'✅' if risk_model else '❌'}")
print(f"   Risk Scaler: {'✅' if risk_scaler else '❌'}")
print()


def _build_feature_dict(features: PollinationFeatures) -> dict:
    crop = features.crop_type.lower()
    return {
        "temp_7d_mean": features.temperature_c,
        "humidity": features.humidity_percent,
        "rainfall_7d": features.rainfall_mm,
        "wind_speed": features.wind_speed_kmh,
        "ndvi": features.ndvi,
        "day_of_year": features.day_of_year,
        "month": features.month,
        "crop_mustard": 1 if crop == "mustard" else 0,
        "crop_wheat": 1 if crop == "wheat" else 0,
        "crop_sunflower": 1 if crop == "sunflower" else 0,
        "crop_rice": 1 if crop == "rice" else 0,
        "crop_cotton": 1 if crop == "cotton" else 0,
        "bee_richness": features.bee_count,
        "bee_count": features.bee_abundance,
        "pollen_tree": features.pollen_level,
        "pollen_grass": features.pollen_level,
        "pollen_weed": features.pollen_level,
    }


def _baseline_flowering(features: PollinationFeatures) -> tuple[int, int]:
    """Baseline GDD-threshold model."""
    crop = features.crop_type.lower()

    if crop in CROP_PARAMS and features.sowing_date:
        sowing = date.fromisoformat(features.sowing_date)
        n_days = 150
        temp_df = pd.DataFrame({
            "date": [sowing + timedelta(days=i) for i in range(n_days)],
            "T2M_MAX": [features.temperature_c + 5] * n_days,
            "T2M_MIN": [features.temperature_c - 5] * n_days,
        })
        result = predict_flowering_date(temp_df, crop, sowing)
        if result.predicted_flowering_date:
            start_doy = result.predicted_flowering_date.timetuple().tm_yday
            return start_doy, start_doy + 7

    # Fallback
    base = {"mustard": 15, "wheat": 45, "sunflower": 60, "rice": 90, "cotton": 120}
    start = base.get(crop, 60)
    start += int(features.temperature_c - 25) * 2
    start = max(1, min(365, start))
    return start, start + 7


def _baseline_psi(features: PollinationFeatures) -> tuple[int, str, int]:
    """Baseline PSI with mismatch penalty."""
    score = 0
    if 20 <= features.temperature_c <= 32:
        score += 25
    elif 15 <= features.temperature_c <= 35:
        score += 15
    if 50 <= features.humidity_percent <= 80:
        score += 20
    elif 30 <= features.humidity_percent <= 90:
        score += 10
    if features.ndvi > 0.6:
        score += 20
    elif features.ndvi > 0.4:
        score += 10
    if features.bee_count >= 3:
        score += 15
    elif features.bee_count >= 1:
        score += 8
    if features.pollen_level >= 3:
        score += 15
    elif features.pollen_level >= 2:
        score += 8

    gap_days = None
    crop = features.crop_type.lower()
    if crop in CROP_PARAMS and features.sowing_date:
        sowing = date.fromisoformat(features.sowing_date)
        n_days = 150
        temp_df = pd.DataFrame({
            "date": [sowing + timedelta(days=i) for i in range(n_days)],
            "T2M_MAX": [features.temperature_c + 5] * n_days,
            "T2M_MIN": [features.temperature_c - 5] * n_days,
        })
        flowering = predict_flowering_date(temp_df, crop, sowing)
        pollinator = predict_pollinator_peak_v2(
            crop=crop, region=features.region, sowing_date=sowing, temp_df=temp_df,
        )
        if flowering.predicted_flowering_date and pollinator.predicted_peak_date:
            gap_days = (pollinator.predicted_peak_date - flowering.predicted_flowering_date).days
            score -= min(abs(gap_days), 30)

    score = max(0, min(100, score))
    risk = "Low" if score >= 70 else "Medium" if score >= 40 else "High"
    return score, risk, gap_days


def predict(features: PollinationFeatures) -> PredictionResult:
    """Main prediction function with trained models."""
    
    print(f"\n🔮 Predicting for {features.crop_type} in {features.region}...")
    
    # Build feature vector
    feature_dict = _build_feature_dict(features)
    df = pd.DataFrame([feature_dict])
    
    # Check if ALL models and scalers are loaded
    models_loaded = all([
        flowering_model is not None,
        flowering_scaler is not None,
        psi_model is not None,
        psi_scaler is not None,
        risk_model is not None,
        risk_scaler is not None
    ])
    
    if models_loaded:
        try:
            print("   🚀 Using trained models...")
            
            # Ensure correct column order for flowering model
            if hasattr(flowering_model, 'feature_names_in_'):
                expected_cols = flowering_model.feature_names_in_
                # Add any missing columns with default values
                for col in expected_cols:
                    if col not in df.columns:
                        df[col] = 0
                df = df[expected_cols]
                print(f"   ✅ Reordered DataFrame to match model features")
            
            # Scale features for flowering
            X_scaled = flowering_scaler.transform(df)
            
            # Predict flowering
            start_doy = int(round(flowering_model.predict(X_scaled)[0]))
            # Clamp to valid range
            start_doy = max(1, min(365, start_doy))
            end_doy = min(365, start_doy + 7)
            
            print(f"   ✅ Flowering prediction: DOY {start_doy}")
            
            # PSI prediction
            if hasattr(psi_model, 'feature_names_in_'):
                psi_cols = psi_model.feature_names_in_
                df_psi = df[psi_cols]
            else:
                df_psi = df
            
            X_psi_scaled = psi_scaler.transform(df_psi)
            psi = int(round(psi_model.predict(X_psi_scaled)[0]))
            psi = max(0, min(100, psi))
            print(f"   ✅ PSI prediction: {psi}")
            
            # Risk prediction
            if hasattr(risk_model, 'feature_names_in_'):
                risk_cols = risk_model.feature_names_in_
                df_risk = df[risk_cols]
            else:
                df_risk = df
            
            X_risk_scaled = risk_scaler.transform(df_risk)
            risk = risk_model.predict(X_risk_scaled)[0]
            print(f"   ✅ Risk prediction: {risk}")
            
            # Calculate gap days
            gap_days = None
            if features.crop_type.lower() in CROP_PARAMS and features.sowing_date:
                sowing = date.fromisoformat(features.sowing_date)
                n_days = 150
                temp_df = pd.DataFrame({
                    "date": [sowing + timedelta(days=i) for i in range(n_days)],
                    "T2M_MAX": [features.temperature_c + 5] * n_days,
                    "T2M_MIN": [features.temperature_c - 5] * n_days,
                })
                flowering = predict_flowering_date(temp_df, features.crop_type.lower(), sowing)
                pollinator = predict_pollinator_peak_v2(
                    crop=features.crop_type.lower(),
                    region=features.region,
                    sowing_date=sowing,
                    temp_df=temp_df,
                )
                if flowering.predicted_flowering_date and pollinator.predicted_peak_date:
                    gap_days = (pollinator.predicted_peak_date - flowering.predicted_flowering_date).days
            
            print("   ✅ Using trained model for all predictions")
            return PredictionResult(
                flowering_start_doy=start_doy,
                flowering_end_doy=end_doy,
                psi_score=psi,
                risk_level=risk,
                gap_days=gap_days,
                source="trained_model"
            )
            
        except Exception as e:
            print(f"   ❌ Trained model prediction failed: {e}")
            import traceback
            traceback.print_exc()
            print(f"   Falling back to baseline...")
    else:
        # Show what's missing
        missing = []
        if flowering_model is None: missing.append("flowering_model")
        if flowering_scaler is None: missing.append("flowering_scaler")
        if psi_model is None: missing.append("psi_model")
        if psi_scaler is None: missing.append("psi_scaler")
        if risk_model is None: missing.append("risk_model")
        if risk_scaler is None: missing.append("risk_scaler")
        print(f"   ⚠️  Missing models/scalers: {missing}")
        print(f"   ℹ️  Check that all .pkl files exist in {MODELS_DIR}")
    
    # Fallback to baseline
    print(f"ℹ️  Using baseline model")
    start_doy, end_doy = _baseline_flowering(features)
    psi, risk, gap_days = _baseline_psi(features)
    
    return PredictionResult(
        flowering_start_doy=start_doy,
        flowering_end_doy=end_doy,
        psi_score=psi,
        risk_level=risk,
        gap_days=gap_days,
        source="baseline",
    )


def predict_from_dict(d: dict) -> dict:
    """Convenience function to predict from a dictionary."""
    features = PollinationFeatures(**d)
    result = predict(features)
    return asdict(result)


if __name__ == "__main__":
    # Quick test
    print("🧪 Running quick test...")
    test_features = PollinationFeatures(
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
    result = predict(test_features)
    print(f"\n📊 Test Result:")
    print(f"   Source: {result.source}")
    print(f"   Flowering DOY: {result.flowering_start_doy}")
    print(f"   PSI: {result.psi_score}")
    print(f"   Risk: {result.risk_level}")