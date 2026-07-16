from datetime import datetime
import uuid

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True)
    flowering_start: Mapped[str] = mapped_column(String(16))
    flowering_end: Mapped[str] = mapped_column(String(16))
    flowering_confidence: Mapped[float] = mapped_column(Float)
    psi_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(16))
    weather_summary: Mapped[str] = mapped_column(Text, default="{}")
    pollen_summary: Mapped[str] = mapped_column(Text, default="{}")
    ndvi_value: Mapped[float] = mapped_column(Float, default=0.0)
    bee_species: Mapped[str] = mapped_column(Text, default="[]")
    recommendation: Mapped[str] = mapped_column(Text, default="")
    model_source: Mapped[str] = mapped_column(String(32), default="general")
    data_confidence: Mapped[str] = mapped_column(String(32), default="standard")
    prediction_inputs: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
