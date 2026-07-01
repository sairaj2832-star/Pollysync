"""
generate_more_data.py
Generate a much larger training dataset with realistic variations.
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta
from pathlib import Path
import random

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def generate_large_dataset(n_samples=2000):
    """Generate a large, diverse training dataset."""
    np.random.seed(42)
    random.seed(42)
    
    records = []
    crops = ["sunflower", "mustard"]
    
    # Region-specific parameters
    region_params = {
        "Maharashtra": {"temp_base": 28, "temp_var": 3, "humidity_base": 65, "humidity_var": 10},
        "Karnataka": {"temp_base": 29, "temp_var": 2.5, "humidity_base": 70, "humidity_var": 8},
        "Andhra Pradesh": {"temp_base": 30, "temp_var": 2, "humidity_base": 68, "humidity_var": 9},
        "Telangana": {"temp_base": 28, "temp_var": 3, "humidity_base": 62, "humidity_var": 10},
        "Rajasthan": {"temp_base": 22, "temp_var": 4, "humidity_base": 50, "humidity_var": 12},
        "Madhya Pradesh": {"temp_base": 24, "temp_var": 3.5, "humidity_base": 55, "humidity_var": 10},
        "Uttar Pradesh": {"temp_base": 23, "temp_var": 4, "humidity_base": 58, "humidity_var": 11},
        "Haryana": {"temp_base": 22, "temp_var": 3, "humidity_base": 52, "humidity_var": 10},
    }
    
    for i in range(n_samples):
        # Select crop and region
        crop = random.choice(crops)
        
        if crop == "sunflower":
            regions = ["Maharashtra", "Karnataka", "Andhra Pradesh", "Telangana"]
            # Kharif season: May-July
            month = random.randint(5, 7)
            day = random.randint(1, 28)
            base_flowering_doy = random.randint(150, 220)
            season_factor = 1
        else:  # mustard
            regions = ["Rajasthan", "Madhya Pradesh", "Uttar Pradesh", "Haryana"]
            # Rabi season: October-November
            month = random.randint(10, 11)
            day = random.randint(1, 28)
            base_flowering_doy = random.randint(290, 340)
            season_factor = -1
        
        region = random.choice(regions)
        params = region_params[region]
        
        # Add temperature variation
        temp = params["temp_base"] + np.random.normal(0, params["temp_var"])
        if crop == "sunflower":
            temp += np.random.uniform(-2, 4)  # Warmer for sunflower
        else:
            temp += np.random.uniform(-3, 2)  # Cooler for mustard
        
        # Add seasonal variation
        seasonal_temp = 5 * np.sin(2 * np.pi * month / 12)
        temp += seasonal_temp * 0.3
        
        # Other features with realistic correlations
        humidity = params["humidity_base"] + np.random.normal(0, params["humidity_var"])
        humidity = max(20, min(95, humidity))
        
        # Rainfall varies by season
        if crop == "sunflower":
            rainfall = np.random.exponential(10) + 2
        else:
            rainfall = np.random.exponential(3) + 0.5
        
        wind_speed = np.random.normal(10, 3)
        wind_speed = max(2, wind_speed)
        
        # NDVI varies by crop and region
        if crop == "sunflower":
            ndvi = np.random.normal(0.65, 0.12)
        else:
            ndvi = np.random.normal(0.52, 0.10)
        ndvi = max(0.1, min(0.95, ndvi))
        
        # Bee diversity varies by region and crop
        if crop == "sunflower":
            bee_base = 5
        else:
            bee_base = 3
        bee_richness = max(1, int(bee_base + np.random.normal(0, 1.5)))
        bee_abundance = max(5, int(bee_richness * np.random.uniform(3, 8)))
        
        # Pollen levels
        pollen = random.randint(1, 5)
        
        # Sowing date
        sowing = date(2024, month, day)
        sowing_doy = sowing.timetuple().tm_yday
        
        # Add some noise to flowering date
        flowering_doy = base_flowering_doy + np.random.normal(0, 10)
        flowering_doy = max(1, min(365, int(flowering_doy)))
        
        records.append({
            "crop": crop,
            "region": region,
            "start_doy": flowering_doy,
            "end_doy": min(365, flowering_doy + 7 + random.randint(-2, 3)),
            "temp_7d_mean": round(temp, 1),
            "humidity": round(humidity, 1),
            "rainfall_7d": round(rainfall, 1),
            "wind_speed": round(wind_speed, 1),
            "ndvi": round(ndvi, 3),
            "month": month,
            "day_of_year": sowing_doy,
            "bee_richness": bee_richness,
            "bee_count": bee_abundance,
            "pollen_tree": pollen,
            "pollen_grass": pollen,
            "pollen_weed": pollen,
        })
    
    return pd.DataFrame(records)

if __name__ == "__main__":
    print("📊 Generating large training dataset...")
    print("   This may take a moment...")
    
    df = generate_large_dataset(2000)
    
    # Save to CSV
    out_path = DATA_DIR / "flowering_data_large.csv"
    df.to_csv(out_path, index=False)
    
    print(f"\n✅ Generated {len(df)} rows")
    print(f"   Saved to: {out_path}")
    print(f"\n📊 Dataset Summary:")
    print(f"   Crops: {df['crop'].value_counts().to_dict()}")
    print(f"   Regions: {df['region'].value_counts().to_dict()}")
    
    print(f"\n📈 Feature Statistics:")
    for col in df.select_dtypes(include=[np.number]).columns:
        print(f"   {col}: mean={df[col].mean():.2f}, std={df[col].std():.2f}")