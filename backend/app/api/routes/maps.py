from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.farm import Farm
from app.models.user import User
from app.services.bee_service import fetch_bees, store_bees, get_bee_species_for_farm

router = APIRouter(prefix="/maps", tags=["maps"])


@router.get("/bees")
async def bee_occurrences(
    farm_id: str = Query(...),
    radius: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    farm = db.scalar(select(Farm).where(Farm.id == farm_id, Farm.user_id == current_user.id))
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    occurrences = await fetch_bees(farm.location_lat, farm.location_lng, radius)
    if occurrences:
        store_bees(farm_id, occurrences, db)

    cached = get_bee_species_for_farm(farm_id, db)
    return {
        "center": {"lat": farm.location_lat, "lng": farm.location_lng},
        "occurrences": occurrences,
        "species_summary": cached,
    }
