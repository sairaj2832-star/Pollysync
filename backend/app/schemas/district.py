from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DistrictRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    name: str
    state: str
    centroid_lat: float
    centroid_lng: float
    radius_km: float
    created_at: datetime
