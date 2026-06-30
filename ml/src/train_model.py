"""
train_model.py
Trains flowering_model.pkl, psi_model.pkl, risk_model.pkl from the CSVs in
ml/data/. These are the models predict.py already tries to load — without
running this script, predict.py silently uses the baseline GDD/proxy logic
instead (source="baseline").

IMPORTANT: feature columns here must exactly match _build_feature_dict()
in predict.py, or joblib's loaded model will throw a column-mismatch error
at inference time.

Usage:
    python generate_data.py   # creates flowering_data.csv, psi_data.csv first
    python train_model.py
"""

from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, accuracy_score

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Must match the dict keys/order produced by predict.py's _build_feature_dict()
FEATURE_COLS = [
    "temp_7d_mean", "humidity", "rainfall_7d", "wind_speed", "ndvi",
    "day_of_year", "month",
    "crop_mustard", "crop_wheat", "crop_sunflower", "crop_rice", "crop_cotton",
    "bee_richness", "pollen_tree", "pollen_grass", "pollen_weed",
]


def _onehot_crop(df: pd.DataFrame, crop_col: str = "crop") -> pd.DataFrame:
    df = df.copy()
    for c in ["mustard", "wheat", "sunflower", "rice", "cotton"]:
        df[f"crop_{c}"] = (df[crop_col].str.lower() == c).astype(int)
    return df


def _fill_missing_features(df: pd.DataFrame) -> pd.DataFrame:
    """Adds any FEATURE_COLS missing from a given CSV with neutral placeholder values."""
    df = df.copy()
    defaults = {
        "wind_speed": 10.0,
        "day_of_year": 150,
        "month": 6,
        "bee_richness": df["bee_richness"] if "bee_richness" in df.columns else 3,
        "pollen_tree": 2, "pollen_grass": 2, "pollen_weed": 2,
    }
    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default
    return df


def train_flowering_model():
    df = pd.read_csv(DATA_DIR / "flowering_data_real.csv")
    df = _onehot_crop(df)
    df = _fill_missing_features(df)

    X = df[FEATURE_COLS]
    y = df["start_doy"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    print(f"flowering_model R^2 on holdout: {r2_score(y_test, preds):.3f}")

    joblib.dump(model, MODELS_DIR / "flowering_model.pkl")
    print(f"Saved flowering_model.pkl")


def train_psi_and_risk_models():
    df = pd.read_csv(DATA_DIR / "psi_data.csv")
    df = _onehot_crop(df)
    df = _fill_missing_features(df)
    # psi_data.csv doesn't include pollen_tree/grass/weed split, only pollen_level
    if "pollen_level" in df.columns:
        df["pollen_tree"] = df["pollen_level"]
        df["pollen_grass"] = df["pollen_level"]
        df["pollen_weed"] = df["pollen_level"]

    X = df[FEATURE_COLS]
    y_psi = df["psi_score"]
    y_risk = df["risk_level"]

    X_train, X_test, y_psi_train, y_psi_test, y_risk_train, y_risk_test = train_test_split(
        X, y_psi, y_risk, test_size=0.2, random_state=42
    )

    psi_model = RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42)
    psi_model.fit(X_train, y_psi_train)
    print(f"psi_model R^2 on holdout: {r2_score(y_psi_test, psi_model.predict(X_test)):.3f}")
    joblib.dump(psi_model, MODELS_DIR / "psi_model.pkl")
    print(f"Saved psi_model.pkl")

    risk_model = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
    risk_model.fit(X_train, y_risk_train)
    print(f"risk_model accuracy on holdout: {accuracy_score(y_risk_test, risk_model.predict(X_test)):.3f}")
    joblib.dump(risk_model, MODELS_DIR / "risk_model.pkl")
    print(f"Saved risk_model.pkl")


if __name__ == "__main__":
    train_flowering_model()
    train_psi_and_risk_models()
    print(f"\nAll models saved to {MODELS_DIR}")