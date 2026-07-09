from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TeamMemberCreate(BaseModel):
    email: str = Field(max_length=255)
    name: str = Field(min_length=1, max_length=120)
    role: str = Field(default="viewer", pattern="^(viewer|editor|admin)$")


class TeamMemberUpdate(BaseModel):
    role: str | None = Field(default=None, pattern="^(viewer|editor|admin)$")
    status: str | None = Field(default=None, pattern="^(pending|active|inactive)$")


class TeamMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    farm_id: int
    email: str
    name: str
    role: str
    status: str
    invited_by: int
    created_at: datetime
