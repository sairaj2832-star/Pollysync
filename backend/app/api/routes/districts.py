from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.farm import District
from app.schemas.district import DistrictRead

router = APIRouter(prefix="/districts", tags=["districts"])


@router.get("", response_model=list[DistrictRead])
def list_districts(
    db: Session = Depends(get_db),
) -> list[DistrictRead]:
    """Get all Maharashtra districts."""
    districts = list(db.scalars(select(District).order_by(District.name)))
    return districts


@router.get("/{slug}", response_model=DistrictRead)
def get_district(
    slug: str,
    db: Session = Depends(get_db),
) -> DistrictRead:
    """Get a specific district by slug."""
    district = db.scalar(select(District).where(District.slug == slug))
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    return district
