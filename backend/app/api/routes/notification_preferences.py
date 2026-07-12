from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.notification_preference import NotificationPreference
from app.models.user import User
from app.schemas.notification_preference import (
    NotificationPreferenceRead,
    NotificationPreferenceUpdate,
)

router = APIRouter(prefix="/notifications/preferences", tags=["notifications"])


def _get_or_create_prefs(user_id: str, db: Session) -> NotificationPreference:
    prefs = db.scalar(
        select(NotificationPreference).where(NotificationPreference.user_id == user_id)
    )
    if prefs is None:
        prefs = NotificationPreference(user_id=user_id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs


@router.get("", response_model=NotificationPreferenceRead)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationPreference:
    return _get_or_create_prefs(current_user.id, db)


@router.patch("", response_model=NotificationPreferenceRead)
def update_preferences(
    payload: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationPreference:
    prefs = _get_or_create_prefs(current_user.id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(prefs, field, value)
    db.commit()
    db.refresh(prefs)
    return prefs
