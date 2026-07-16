from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationPreferenceUpdate(BaseModel):
    push_critical: bool | None = None
    push_daily: bool | None = None
    push_system: bool | None = None
    email_weekly: bool | None = None
    email_billing: bool | None = None
    whatsapp_urgent: bool | None = None
    sms_alerts: bool | None = None


class NotificationPreferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    push_critical: bool = True
    push_daily: bool = True
    push_system: bool = False
    email_weekly: bool = True
    email_billing: bool = True
    whatsapp_urgent: bool = False
    sms_alerts: bool = True
    created_at: datetime
    updated_at: datetime
