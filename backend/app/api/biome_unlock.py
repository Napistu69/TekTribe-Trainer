"""Biome unlock API router — REST endpoints for biome progression."""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import session_service
from app.services.biome_unlock_service import get_biome_unlock_progress

router = APIRouter(prefix="/biomes", tags=["biomes"])


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


@router.get("/progress")
async def get_biome_progress(
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Get biome unlock progress for the current user."""
    user_id = await get_current_user_id(authorization)
    progress = await get_biome_unlock_progress(db, user_id)
    return {"biomes": progress}
