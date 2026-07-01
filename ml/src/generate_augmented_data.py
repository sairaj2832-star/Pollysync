"""
generate_augmented_data.py
Generates augmented training data with realistic variations for better model training.
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def generate_augmented_dataset(n_samples=500):
    """Generate a larger dataset with realistic variations."""
    np.random.seed(42)
    records = []
    
    crops = ["sunflower", "mustard"]
    regions = {
        "sunflower": ["Maharashtra", "Karnataka", "Andhra Pradesh", "Telangana"],
        "mustard": ["Rajasthan", "Madhya Pradesh", "Uttar Pradesh", "Haryana"]
    }
    
    for crop in crops:
        for region in regions[crop]:
            for _ in range(n_samples // 8):
                # Generate sowing date with realistic season
                if crop == "sunflower":
                    # Kharif: May-July
                    month = np.random.randint(5, 8)
                    day = np.random.randint(1, 28)
                else:
                    # Rabi: October-November
                    month = np.random.randint(10, 12)
                    day = np.random.randint(1, 28)
                
                sowing = date(2024, month, day)
                
                # Generate realistic features
                if crop == "sunflower":
                    base_temp = np.random.uniform(24, 32)
                    start_doy = 150 + np.random.normal(0, 15)
                    flowering_duration = 60 + np.random.normal(0, 10)
                else:
                    base_temp = np.random.uniform(12, 22)
                    start_doy = 300 + np.random.normal(0, 15)
                    flowering_duration = 70 + np.random.normal(0, 10)
                
                # Add regional variations
                if region in ["Maharashtra", "Karnataka"]:
                    temp_shift = np.random.uniform(1, 3)
                    humidity_shift = np.random.uniform(-10, 10)
                elif region in ["Rajasthan", "Haryana"]:
                    temp_shift = np.random.uniform(-2, 0)
                    humidity_shift = np.random.uniform(-15, -5)
                else:
                    temp_shift = np.random.uniform(-1, 1)
                    humidity_shift = np.random.uniform(-5, 5)
                
                # Create feature vector
                row = {
                    "crop": crop,
                    "region": region,
                    "start_doy": int(start_doy),
                    "end_doy": int(start_doy + 7),
                    "temp_7d_mean": round(base_temp + temp_shift + np.random.normal(0, 2), 1),
                    "humidity": round(60 + humidity_shift + np.random.normal(0, 8), 1),
                    "rainfall_7d": round(np.random.exponential(6) + 2, 1),
                    "wind_speed": round(np.random.uniform(5, 15) + np.random.normal(0, 2), 1),
                    "ndvi": round(np.random.normal(0.6 if crop == "sunflower" else 0.5, 0.1), 3),
                    "month": month,
                    "day_of_year": sowing.timetuple().tm_yday,
                    "bee_richness": int(max(1, np.random.poisson(4) + (0 if crop == "sunflower" else 2))),
                    "bee_count": int(max(5, np.random.poisson(15) + (0 if crop == "sunflower" else 10))),
                    "pollen_tree": np.random.randint(1, 5),
                    "pollen_grass": np.random.randint(1, 5),
                    "pollen_weed": np.random.randint(1, 5),
                }
                records.append(row)
    
    return pd.DataFrame(records)

if __name__ == "__main__":
    print("Generating augmented dataset...")
    df = generate_augmented_dataset(1000)
    
    # Save to CSV
    out_path = DATA_DIR / "flowering_data_augmented.csv"
    df.to_csv(out_path, index=False)
    
    print(f"✅ Generated {len(df)} rows")
    print(f"   Crops: {df['crop'].value_counts().to_dict()}")
    print(f"   Regions: {df['region'].value_counts().head(10).to_dict()}")
    print(f"   Feature summary:")
    for col in df.select_dtypes(include=[np.number]).columns:
        print(f"     {col}: mean={df[col].mean():.2f}, std={df[col].std():.2f}")