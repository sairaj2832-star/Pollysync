from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.farm import Farm
from app.models.notification import Notification
from app.models.prediction import Prediction
from app.models.user import User
from app.schemas.farm import FarmCreate, FarmRead, FarmUpdate

router = APIRouter(prefix="/farms", tags=["farms"])


@router.get("", response_model=list[FarmRead])
def list_farms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FarmRead]:
    farms = list(
        db.scalars(
            select(Farm)
            .where(Farm.user_id == current_user.id)
            .order_by(Farm.created_at.desc())
        )
    )
    latest_by_farm = _latest_prediction_scores([farm.id for farm in farms], db)
    return [_to_farm_read(farm, latest_by_farm.get(farm.id)) for farm in farms]


@router.post("", response_model=FarmRead, status_code=status.HTTP_201_CREATED)
def create_farm(
    payload: FarmCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FarmRead:
    farm = Farm(**payload.model_dump(), user_id=current_user.id)
    db.add(farm)
    db.flush()
    db.add(
        Notification(
            user_id=current_user.id,
            farm_id=farm.id,
            type="info",
            title="Farm added",
            message=f'{farm.name} has been added to your farms.',
        )
    )
    db.commit()
    db.refresh(farm)
    return _to_farm_read(farm)


@router.patch("/{farm_id}", response_model=FarmRead)
def update_farm(
    farm_id: int,
    payload: FarmUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FarmRead:
    farm = _owned_farm_or_404(farm_id, current_user.id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(farm, field, value)
    db.commit()
    db.refresh(farm)
    latest_prediction = (
        db.scalars(
            select(Prediction)
            .where(Prediction.farm_id == farm.id)
            .order_by(Prediction.created_at.desc())
            .limit(1)
        )
        .first()
    )
    return _to_farm_read(farm, latest_prediction.psi_score if latest_prediction else None)


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    farm = _owned_farm_or_404(farm_id, current_user.id, db)
    db.query(Notification).filter(Notification.farm_id == farm.id).delete()
    db.query(Prediction).filter(Prediction.farm_id == farm.id).delete()
    db.delete(farm)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _owned_farm_or_404(farm_id: int, user_id: int, db: Session) -> Farm:
    farm = db.scalar(select(Farm).where(Farm.id == farm_id, Farm.user_id == user_id))
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm


def _latest_prediction_scores(farm_ids: list[int], db: Session) -> dict[int, int]:
    if not farm_ids:
        return {}
    predictions = list(
        db.scalars(
            select(Prediction)
            .where(Prediction.farm_id.in_(farm_ids))
            .order_by(Prediction.farm_id, Prediction.created_at.desc())
        )
    )
    latest_by_farm: dict[int, int] = {}
    for prediction in predictions:
        latest_by_farm.setdefault(prediction.farm_id, prediction.psi_score)
    return latest_by_farm


def _to_farm_read(farm: Farm, latest_psi: int | None = None) -> FarmRead:
    location = farm.location_name
    return FarmRead(
        id=farm.id,
        name=farm.name,
        crop_type=farm.crop_type,
        crop=farm.crop_type,
        variety=farm.variety,
        irrigation_method=farm.irrigation_method,
        planting_date=farm.planting_date,
        harvest_date=farm.harvest_date,
        location_name=location,
        location=location,
        location_lat=farm.location_lat,
        location_lng=farm.location_lng,
        area_acres=farm.area_acres,
        soil_type=farm.soil_type,
        latest_psi=latest_psi,
        created_at=farm.created_at,
    )
