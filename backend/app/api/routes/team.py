from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.farm import Farm
from app.models.team_member import TeamMember
from app.models.user import User
from app.schemas.team_member import TeamMemberCreate, TeamMemberRead, TeamMemberUpdate

router = APIRouter(prefix="/farms/{farm_id}/team", tags=["team"])


def _owned_farm_or_404(farm_id: str, user_id: str, db: Session) -> Farm:
    farm = db.scalar(select(Farm).where(Farm.id == farm_id, Farm.user_id == user_id))
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm


@router.get("", response_model=list[TeamMemberRead])
def list_team(
    farm_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TeamMember]:
    _owned_farm_or_404(farm_id, current_user.id, db)
    return list(
        db.scalars(
            select(TeamMember)
            .where(TeamMember.farm_id == farm_id)
            .order_by(TeamMember.created_at.desc())
        )
    )


@router.post("", response_model=TeamMemberRead, status_code=status.HTTP_201_CREATED)
def invite_member(
    farm_id: str,
    payload: TeamMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TeamMember:
    _owned_farm_or_404(farm_id, current_user.id, db)
    existing = db.scalar(
        select(TeamMember).where(
            TeamMember.farm_id == farm_id, TeamMember.email == payload.email
        )
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A member with this email already exists on this farm",
        )
    member = TeamMember(
        farm_id=farm_id,
        email=payload.email,
        name=payload.name,
        role=payload.role,
        invited_by=current_user.id,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.patch("/{member_id}", response_model=TeamMemberRead)
def update_member(
    farm_id: str,
    member_id: str,
    payload: TeamMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TeamMember:
    member = db.scalar(
        select(TeamMember).where(
            TeamMember.id == member_id,
            TeamMember.farm_id == farm_id,
        )
    )
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(member, field, value)
    db.commit()
    db.refresh(member)
    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    farm_id: str,
    member_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    member = db.scalar(
        select(TeamMember).where(
            TeamMember.id == member_id,
            TeamMember.farm_id == farm_id,
        )
    )
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    db.delete(member)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
