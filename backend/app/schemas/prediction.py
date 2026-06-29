from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class PredictionCreate(BaseModel):
    farm_id: int


class PredictionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    farm_id: int
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


class DashboardSummary(BaseModel):
    farm: Any
    current_weather: dict | None = None
    latest_prediction: PredictionRead | None = None
    bee_species: list[str] = []
