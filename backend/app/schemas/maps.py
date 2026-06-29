from pydantic import BaseModel


class BeeOccurrenceOut(BaseModel):
    species: str
    lat: float
    lng: float


class BeeMapResponse(BaseModel):
    center: dict[str, float]
    occurrences: list[BeeOccurrenceOut]
