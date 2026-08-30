"""Egg API router — REST endpoints for egg management."""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas import EggResponse, EggDetailResponse, CompanionResponse
from app.services import session_service, egg_service, companion_service

router = APIRouter(prefix="/eggs", tags=["eggs"])


def parse_uuid(value: str):
    """Parse a string to UUID, raising 400 on invalid format."""
    from uuid import UUID
    try:
        return UUID(value)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format",
        )


async def get_current_user_id(authorization: str = Header(None, alias="Authorization")) -> str:
    """Extract and validate user_id from session token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )
    token = authorization.replace("Bearer ", "")
    user_id = await session_service.validate_session(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )
    return user_id


@router.post("/pull", response_model=EggResponse)
async def pull_egg(
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Pull a new egg. Species is hidden until hatch."""
    user_id = await get_current_user_id(authorization)
    
    # Check if user can pull
    allowed, reason = await egg_service.can_pull(db, user_id)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=reason,
        )
    
    # Pull the egg
    egg = await egg_service.pull_egg(db, user_id, source="standard")
    
    return EggResponse(
        uuid=str(egg.uuid),
        user_id=egg.user_id,
        species=egg.species,
        rarity=egg.rarity,
        source=egg.source,
        pulled_at=egg.pulled_at.isoformat(),
        hatched=egg.hatched,
        temperature=egg.temperature,
        stability=egg.stability,
    )


@router.get("", response_model=list[EggResponse])
async def list_eggs(
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """List all eggs for the current user."""
    user_id = await get_current_user_id(authorization)
    
    from sqlalchemy import select
    from app.models import Egg
    result = await db.execute(
        select(Egg).where(Egg.user_id == user_id, Egg.hatched == False).order_by(Egg.pulled_at.desc())
    )
    eggs = result.scalars().all()
    
    return [
        EggResponse(
            uuid=str(e.uuid),
            user_id=e.user_id,
            species=e.species,
            rarity=e.rarity,
            source=e.source,
            pulled_at=e.pulled_at.isoformat(),
            hatched=e.hatched,
            temperature=e.temperature,
            stability=e.stability,
        )
        for e in eggs
    ]


@router.get("/{egg_uuid}", response_model=EggDetailResponse)
async def get_egg(
    egg_uuid: str,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Get egg detail."""
    user_id = await get_current_user_id(authorization)
    
    from sqlalchemy import select
    from app.models import Egg
    result = await db.execute(
        select(Egg).where(Egg.user_id == user_id, Egg.uuid == parse_uuid(egg_uuid))
    )
    egg = result.scalar_one_or_none()
    if not egg:
        raise HTTPException(status_code=404, detail="Egg not found")
    
    return EggDetailResponse(
        uuid=str(egg.uuid),
        user_id=egg.user_id,
        species=egg.species,
        rarity=egg.rarity,
        source=egg.source,
        pulled_at=egg.pulled_at.isoformat(),
        hatched=egg.hatched,
        incubation_started_at=egg.incubation_started_at.isoformat() if egg.incubation_started_at else None,
        temperature=egg.temperature,
        stability=egg.stability,
    )


@router.post("/{egg_uuid}/release")
async def release_egg(
    egg_uuid: str,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Release a duplicate egg in exchange for Element Shards."""
    user_id = await get_current_user_id(authorization)
    
    try:
        shards = await egg_service.release_egg(db, user_id, parse_uuid(egg_uuid))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"status": "released", "shards_gained": shards}


@router.post("/{egg_uuid}/incubate")
async def start_incubation(
    egg_uuid: str,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Start incubation for an egg."""
    user_id = await get_current_user_id(authorization)
    
    from sqlalchemy import select
    from app.models import Egg
    result = await db.execute(
        select(Egg).where(Egg.user_id == user_id, Egg.uuid == parse_uuid(egg_uuid))
    )
    egg = result.scalar_one_or_none()
    if not egg:
        raise HTTPException(status_code=404, detail="Egg not found")
    if egg.hatched:
        raise HTTPException(status_code=409, detail="Egg already hatched")
    
    egg.incubation_started_at = datetime.now(timezone.utc)
    await db.commit()
    
    return {"status": "incubation_started", "egg_uuid": str(egg.uuid)}


@router.post("/{egg_uuid}/hatch", response_model=CompanionResponse)
async def hatch_egg(
    egg_uuid: str,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Hatch an egg into a companion."""
    user_id = await get_current_user_id(authorization)
    
    try:
        companion = await companion_service.hatch_egg(db, user_id, parse_uuid(egg_uuid))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return CompanionResponse(**companion_service.serialize_companion(companion))
