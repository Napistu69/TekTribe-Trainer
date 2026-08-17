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
    
    companion.name = name
    await db.commit()
    
    return {"status": "renamed", "name": name}
