from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.prediction import DashboardSummary
from app.api.routes.predictions import build_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(
    farm_id: int = Query(...),
    db: Session = Depends(get_db),
) -> DashboardSummary:
    return build_dashboard_summary(farm_id, db)
