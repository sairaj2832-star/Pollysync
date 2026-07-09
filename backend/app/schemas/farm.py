from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FarmCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    crop_type: str = Field(min_length=2, max_length=80)
    location_name: str | None = Field(default=None, max_length=255)
    location_lat: float | None = Field(default=None, ge=-90, le=90)
    location_lng: float | None = Field(default=None, ge=-180, le=180)
    area_acres: float | None = Field(default=None, gt=0)
    soil_type: str | None = Field(default=None, max_length=50)

    @model_validator(mode="before")
    @classmethod
    def normalize_frontend_fields(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        normalized = dict(data)
        if "crop_type" not in normalized and "crop" in normalized:
            normalized["crop_type"] = normalized["crop"]
        if "location_name" not in normalized and "location" in normalized:
            normalized["location_name"] = normalized["location"]
        if normalized.get("location_name") and normalized.get("location_lat") is None:
            normalized["location_lat"] = 20.0
        if normalized.get("location_name") and normalized.get("location_lng") is None:
            normalized["location_lng"] = 78.0
        return normalized


class FarmUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    crop_type: str | None = Field(default=None, min_length=2, max_length=80)
    location_name: str | None = Field(default=None, max_length=255)
    location_lat: float | None = Field(default=None, ge=-90, le=90)
    location_lng: float | None = Field(default=None, ge=-180, le=180)
    area_acres: float | None = Field(default=None, gt=0)
    soil_type: str | None = Field(default=None, max_length=50)

    @model_validator(mode="before")
    @classmethod
    def normalize_frontend_fields(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        normalized = dict(data)
        if "crop_type" not in normalized and "crop" in normalized:
            normalized["crop_type"] = normalized["crop"]
        if "location_name" not in normalized and "location" in normalized:
            normalized["location_name"] = normalized["location"]
        if normalized.get("location_name") and "location_lat" not in normalized:
            normalized["location_lat"] = 20.0
        if normalized.get("location_name") and "location_lng" not in normalized:
            normalized["location_lng"] = 78.0
        return normalized


class FarmRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    crop_type: str
    crop: str
    location_name: str | None = None
    location: str | None = None
    location_lat: float | None = None
    location_lng: float | None = None
    area_acres: float | None = None
    soil_type: str | None = None
    latest_psi: int | None = None
    created_at: datetime
