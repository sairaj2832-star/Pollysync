SEASONAL_POLLEN = {
    1: {"tree": 3, "grass": 1, "weed": 2},
    2: {"tree": 4, "grass": 2, "weed": 3},
    3: {"tree": 5, "grass": 3, "weed": 4},
    4: {"tree": 5, "grass": 4, "weed": 4},
    5: {"tree": 4, "grass": 5, "weed": 3},
    6: {"tree": 3, "grass": 5, "weed": 3},
    7: {"tree": 2, "grass": 4, "weed": 2},
    8: {"tree": 2, "grass": 3, "weed": 2},
    9: {"tree": 3, "grass": 3, "weed": 3},
    10: {"tree": 3, "grass": 2, "weed": 3},
    11: {"tree": 2, "grass": 1, "weed": 2},
    12: {"tree": 2, "grass": 1, "weed": 2},
}

CROP_ENCODER = ["crop_mustard", "crop_wheat", "crop_sunflower", "crop_rice", "crop_cotton"]


def get_pollen_for_month(month: int) -> dict:
    return SEASONAL_POLLEN.get(month, {"tree": 2, "grass": 2, "weed": 2})


def build_features(
    crop_type: str,
    temperature: float,
    humidity: float,
    rainfall: float,
    wind_speed: float,
    ndvi: float,
    bee_count: int,
    month: int,
    day_of_year: int,
    bee_abundance: int = 15,
) -> dict:
    pollen = get_pollen_for_month(month)
    crop = crop_type.lower()
    features = {
        "temp_7d_mean": temperature,
        "humidity": humidity,
        "rainfall_7d": rainfall,
        "wind_speed": wind_speed,
        "ndvi": ndvi,
        "day_of_year": day_of_year,
        "month": month,
        "crop_mustard": 1 if crop == "mustard" else 0,
        "crop_wheat": 1 if crop == "wheat" else 0,
        "crop_sunflower": 1 if crop == "sunflower" else 0,
        "crop_rice": 1 if crop == "rice" else 0,
        "crop_cotton": 1 if crop == "cotton" else 0,
        "bee_richness": bee_count,
        "bee_count": bee_abundance,
        "pollen_tree": pollen["tree"],
        "pollen_grass": pollen["grass"],
        "pollen_weed": pollen["weed"],
    }
    return features
