"""Training API router — REST endpoints for mini-game training."""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas import TrainingSubmitRequest, TrainingResultResponse
from app.services import session_service, training_service

router = APIRouter(prefix="/training", tags=["training"])


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


@router.get("/available/{companion_uuid}")
async def get_available_games(
    companion_uuid: str,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Get available mini-games for a companion."""
    user_id = await get_current_user_id(authorization)
    
    from uuid import UUID
    try:
        UUID(companion_uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    try:
        games = await training_service.get_available_games(db, user_id, companion_uuid)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return games


@router.post("/submit", response_model=TrainingResultResponse)
async def submit_training(
    request: TrainingSubmitRequest,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Submit a mini-game result and apply gains."""
    user_id = await get_current_user_id(authorization)
    
    try:
        result = await training_service.apply_training(
            db, user_id, request.companion_uuid, request.game_id, request.score, request.duration_seconds
        )
    except ValueError as e:
        error_msg = str(e)
        if "cooldown" in error_msg.lower():
            raise HTTPException(status_code=429, detail=error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    
    return TrainingResultResponse(**result)
