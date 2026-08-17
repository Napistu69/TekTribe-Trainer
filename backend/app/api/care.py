"""Care API router — REST endpoints for companion care."""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import session_service, care_service

router = APIRouter(prefix="/care", tags=["care"])


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


@router.get("/{companion_uuid}")
async def get_care_state(
    companion_uuid: str,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Get care state for a companion."""
    user_id = await get_current_user_id(authorization)
    
    from uuid import UUID
    try:
        uuid = UUID(companion_uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    # Verify ownership
    from sqlalchemy import select
    from app.models import Companion
    result = await db.execute(
        select(Companion).where(Companion.uuid == companion_uuid, Companion.user_id == user_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Companion not found")
    
    care_state = await care_service.get_care_state(db, companion_uuid)
    if not care_state:
        raise HTTPException(status_code=404, detail="Care state not found")
    
    return {
        "hunger": care_state.hunger,
        "energy": care_state.energy,
        "morale": care_state.morale,
        "cleanliness": care_state.cleanliness,
        "last_updated": care_state.last_updated.isoformat(),
    }


@router.post("/{companion_uuid}/{action}")
async def perform_care_action(
    companion_uuid: str,
    action: str,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Perform a care action on a companion."""
    user_id = await get_current_user_id(authorization)
    
    try:
        result = await care_service.perform_care_action(db, user_id, companion_uuid, action)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if not result["success"] and result.get("error") == "cooldown":
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=result,
        )
    
    return result


@router.get("/{companion_uuid}/cooldowns")
async def get_cooldowns(
    companion_uuid: str,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Get cooldown timers for a companion."""
    user_id = await get_current_user_id(authorization)
    
    from uuid import UUID
    try:
        uuid = UUID(companion_uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    # Verify ownership
    from sqlalchemy import select
    from app.models import Companion
    result = await db.execute(
        select(Companion).where(Companion.uuid == companion_uuid, Companion.user_id == user_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Companion not found")
    
    return await care_service.get_cooldowns(db, companion_uuid)
