from datetime import datetime
import uuid

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AgentRateLimit(Base):
    __tablename__ = "agent_rate_limits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    identifier: Mapped[str] = mapped_column(String(255), index=True)
    timestamp: Mapped[float] = mapped_column(Float, index=True)
