from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    farm_id: Mapped[int] = mapped_column(index=True)
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
