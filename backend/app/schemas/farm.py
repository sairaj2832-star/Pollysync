from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FarmCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    crop_type: str = Field(min_length=2, max_length=80)
    location_lat: float = Field(ge=-90, le=90)
    location_lng: float = Field(ge=-180, le=180)


class FarmRead(FarmCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
