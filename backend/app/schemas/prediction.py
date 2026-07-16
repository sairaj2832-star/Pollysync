from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class PredictionCreate(BaseModel):
    farm_id: str
    region: str = "auto"  # "maharashtra", "auto", or other


class PredictionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    farm_id: str
    flowering_start: str
    flowering_end: str
    flowering_confidence: float
    psi_score: int
    risk_level: str
    weather_summary: Any
    pollen_summary: Any
    ndvi_value: float
    bee_species: list[str]
    recommendation: str
    created_at: datetime
    model_source: str | None = None
    data_confidence: str | None = None
    prediction_inputs: Any = None


class DashboardSummary(BaseModel):
    farm: Any
    current_weather: dict | None = None
    latest_prediction: PredictionRead | None = None
    bee_species: list[str] = []
