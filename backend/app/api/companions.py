"""Companion API router — REST endpoints for companion management."""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas import CompanionResponse
from app.services import session_service, companion_service

router = APIRouter(prefix="/companions", tags=["companions"])


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


@router.get("", response_model=list[CompanionResponse])
async def list_companions(
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """List all companions for the current user."""
    user_id = await get_current_user_id(authorization)
    companions = await companion_service.get_companions(db, user_id)
    return [CompanionResponse(**companion_service.serialize_companion(c)) for c in companions]


@router.get("/{companion_uuid}", response_model=CompanionResponse)
async def get_companion(
    companion_uuid: str,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific companion's detail."""
    user_id = await get_current_user_id(authorization)
    
    from uuid import UUID
    try:
        uuid = UUID(companion_uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    companion = await companion_service.get_companion(db, user_id, companion_uuid)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")
    
    return CompanionResponse(**companion_service.serialize_companion(companion))


@router.patch("/{companion_uuid}/name")
async def rename_companion(
    companion_uuid: str,
    name: str,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Rename a companion."""
    user_id = await get_current_user_id(authorization)
    
    from uuid import UUID
    try:
        uuid = UUID(companion_uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    companion = await companion_service.get_companion(db, user_id, companion_uuid)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")
    
    # Validate name
    if len(name) < 1 or len(name) > 32:
        raise HTTPException(status_code=400, detail="Name must be 1-32 characters")
    
    # Only allow alphanumeric, spaces, and basic punctuation
    import re
    if not re.match(r'^[\w\s\-]+$', name):
        raise HTTPException(status_code=400, detail="Name contains invalid characters")
    
    # Force capitalization (first letter of each word)
    name = name.title()
    
    companion.name = name
    await db.commit()
    
    return {"status": "renamed", "name": name}


@router.post("/{companion_uuid}/release")
async def release_companion(
    companion_uuid: str,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Release a companion in exchange for Element Shards."""
    user_id = await get_current_user_id(authorization)
    
    from uuid import UUID
    try:
        uuid = UUID(companion_uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    companion = await companion_service.get_companion(db, user_id, companion_uuid)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")
    
    if companion.is_locked:
        raise HTTPException(status_code=400, detail="Companion is locked")
    
    # Calculate shards based on rarity
    shard_amounts = {
        "common": 10,
        "uncommon": 20,
        "rare": 40,
        "epic": 75,
        "ascendant": 150,
        "legendary": 300,
        "mythic": 500,
    }
    shards = shard_amounts.get(companion.rarity, 10)
    
    # Award shards
    from app.services.currency_service import award_shards
    await award_shards(user_id, shards, "companion_release")
    
    # Delete the companion's care_state first (foreign key constraint)
    from app.models import CareState
    from sqlalchemy import select as sa_select
    care_result = await db.execute(
        sa_select(CareState).where(CareState.companion_uuid == companion.uuid)
    )
    care_state = care_result.scalar_one_or_none()
    if care_state:
        await db.delete(care_state)
    
    # Delete the companion
    await db.delete(companion)
    await db.commit()
    
    return {"status": "released", "shards_gained": shards}


@router.patch("/{companion_uuid}/lock")
async def toggle_lock_companion(
    companion_uuid: str,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Toggle lock status on a companion."""
    user_id = await get_current_user_id(authorization)
    
    from uuid import UUID
    try:
        uuid = UUID(companion_uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    companion = await companion_service.get_companion(db, user_id, companion_uuid)
    if not companion:
        raise HTTPException(status_code=404, detail="Companion not found")
    
    companion.is_locked = not companion.is_locked
    await db.flush()  # Force SQLAlchemy to detect the change
    await db.commit()
    
    return {"status": "updated", "is_locked": companion.is_locked}
