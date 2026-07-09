from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, unique=True)
    push_critical: Mapped[bool] = mapped_column(Boolean, default=True)
    push_daily: Mapped[bool] = mapped_column(Boolean, default=True)
    push_system: Mapped[bool] = mapped_column(Boolean, default=False)
    email_weekly: Mapped[bool] = mapped_column(Boolean, default=True)
    email_billing: Mapped[bool] = mapped_column(Boolean, default=True)
    whatsapp_urgent: Mapped[bool] = mapped_column(Boolean, default=False)
    sms_alerts: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
