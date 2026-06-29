import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.farm import Farm
from app.models.prediction import Prediction
from app.schemas.prediction import DashboardSummary, PredictionCreate, PredictionRead
from app.services.prediction_service import run_prediction

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("", response_model=PredictionRead, status_code=201)
async def create_prediction(payload: PredictionCreate, db: Session = Depends(get_db)) -> Prediction:
    farm = db.get(Farm, payload.farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    prediction = await run_prediction(farm, db)
    return _prediction_to_read(prediction)


@router.get("", response_model=list[PredictionRead])
def list_predictions(farm_id: int = Query(...), db: Session = Depends(get_db)) -> list[Prediction]:
    rows = (
        db.scalars(
            select(Prediction)
            .where(Prediction.farm_id == farm_id)
            .order_by(Prediction.created_at.desc())
        )
        .all()
    )
    return [_prediction_to_read(p) for p in rows]


@router.get("/latest", response_model=PredictionRead | None)
def latest_prediction(farm_id: int = Query(...), db: Session = Depends(get_db)) -> Prediction | None:
    prediction = (
        db.scalars(
            select(Prediction)
            .where(Prediction.farm_id == farm_id)
            .order_by(Prediction.created_at.desc())
            .limit(1)
        )
        .first()
    )
    if not prediction:
        return None
    return _prediction_to_read(prediction)


@router.get("/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(farm_id: int = Query(...), db: Session = Depends(get_db)) -> DashboardSummary:
    farm = db.get(Farm, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    prediction = (
        db.scalars(
            select(Prediction)
            .where(Prediction.farm_id == farm_id)
            .order_by(Prediction.created_at.desc())
            .limit(1)
        )
        .first()
    )
    from app.services.bee_service import get_bee_species_for_farm
    bee_species = get_bee_species_for_farm(farm_id, db)
    return DashboardSummary(
        farm={"id": farm.id, "name": farm.name, "crop_type": farm.crop_type,
              "location_lat": farm.location_lat, "location_lng": farm.location_lng},
        current_weather=_get_weather_summary(farm_id, db),
        latest_prediction=_prediction_to_read(prediction) if prediction else None,
        bee_species=bee_species,
    )


def _prediction_to_read(p: Prediction) -> PredictionRead:
    return PredictionRead(
        id=p.id,
        farm_id=p.farm_id,
        flowering_start=p.flowering_start,
        flowering_end=p.flowering_end,
        flowering_confidence=p.flowering_confidence,
        psi_score=p.psi_score,
        risk_level=p.risk_level,
        weather_summary=json.loads(p.weather_summary) if p.weather_summary else {},
        pollen_summary=json.loads(p.pollen_summary) if p.pollen_summary else {},
        ndvi_value=p.ndvi_value,
        bee_species=json.loads(p.bee_species) if p.bee_species else [],
        recommendation=p.recommendation,
        created_at=p.created_at,
    )


def _get_weather_summary(farm_id: int, db: Session) -> dict | None:
    from app.models.weather_cache import WeatherCache
    wc = (
        db.query(WeatherCache)
        .filter(WeatherCache.farm_id == farm_id)
        .order_by(WeatherCache.timestamp.desc())
        .first()
    )
    if not wc:
        return None
    return {
        "temperature": wc.temperature,
        "humidity": wc.humidity,
        "rainfall": wc.rainfall,
        "wind_speed": wc.wind_speed,
    }
