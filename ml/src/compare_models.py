"""
compare_models.py
Compare trained model vs baseline predictions.
"""

import pandas as pd
from pathlib import Path
from datetime import date
from predict import PollinationFeatures, predict
from geo_lookup import DEMO_LOCATIONS

def compare_predictions():
    """Compare trained model vs baseline predictions."""
    print("📊 Comparing Model Predictions\n")
    print("=" * 70)
    
    for crop, loc in DEMO_LOCATIONS.items():
        print(f"\n🔍 {crop.upper()} in {loc['region']}")
        print("-" * 50)
        
        # Test different environmental conditions
        test_cases = [
            {"temp": 25, "humidity": 60, "rainfall": 5, "ndvi": 0.6, "bee_count": 4},
            {"temp": 28, "humidity": 65, "rainfall": 8, "ndvi": 0.7, "bee_count": 6},
            {"temp": 30, "humidity": 55, "rainfall": 2, "ndvi": 0.5, "bee_count": 2},
            {"temp": 22, "humidity": 70, "rainfall": 12, "ndvi": 0.4, "bee_count": 3},
            {"temp": 26, "humidity": 58, "rainfall": 4, "ndvi": 0.65, "bee_count": 5},
        ]
        
        for i, case in enumerate(test_cases, 1):
            # Determine sowing date
            if crop == "sunflower":
                sowing = "2025-06-15"
                month, doy = 6, 166
            else:
                sowing = "2025-10-20"
                month, doy = 10, 293
            
            features = PollinationFeatures(
                temperature_c=case["temp"],
                humidity_percent=case["humidity"],
                rainfall_mm=case["rainfall"],
                wind_speed_kmh=10,
                ndvi=case["ndvi"],
                bee_count=case["bee_count"],
                bee_abundance=case["bee_count"] * 5,
                pollen_level=3,
                crop_type=crop,
                month=month,
                day_of_year=doy,
                region=loc["region"],
                sowing_date=sowing,
            )
            
            result = predict(features)
            
            print(f"  Case {i}: T={case['temp']}°C, NDVI={case['ndvi']}, Bees={case['bee_count']}")
            print(f"    Flowering: DOY {result.flowering_start_doy}-{result.flowering_end_doy}")
            print(f"    PSI: {result.psi_score} ({result.risk_level})")
            print(f"    Gap: {result.gap_days} days")
            print(f"    Source: {result.source}")
            print()

if __name__ == "__main__":
    compare_predictions()