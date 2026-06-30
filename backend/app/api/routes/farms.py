from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.farm import Farm
from app.schemas.farm import FarmCreate, FarmRead

router = APIRouter(prefix="/farms", tags=["farms"])


@router.get("", response_model=list[FarmRead])
def list_farms(db: Session = Depends(get_db)) -> list[Farm]:
    return list(db.scalars(select(Farm).order_by(Farm.created_at.desc())))


@router.post("", response_model=FarmRead, status_code=status.HTTP_201_CREATED)
def create_farm(payload: FarmCreate, db: Session = Depends(get_db)) -> Farm:
    farm = Farm(**payload.model_dump())
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm
