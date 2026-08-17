"""Dialogue API router — REST endpoints for Overseer dialogue."""
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from app.services import session_service, dialogue_service

router = APIRouter(prefix="/dialogue", tags=["dialogue"])


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


@router.get("/trigger/{trigger_id}")
async def get_dialogue_trigger(
    trigger_id: str,
    authorization: str = Header(None, alias="Authorization"),
):
    """Get dialogue for a trigger. Returns null if already seen."""
    user_id = await get_current_user_id(authorization)
    
    dialogue = await dialogue_service.get_dialogue(user_id, trigger_id)
    if not dialogue:
        return {"dialogue": None, "seen": True}
    
    return {"dialogue": dialogue, "seen": False}


@router.get("/daily")
async def get_daily_greeting(
    authorization: str = Header(None, alias="Authorization"),
):
    """Get today's daily greeting."""
    user_id = await get_current_user_id(authorization)
    return await dialogue_service.get_daily_greeting(user_id)


@router.post("/seen")
async def mark_dialogue_seen(
    trigger_id: str = Query(...),
    authorization: str = Header(None, alias="Authorization"),
):
    """Mark a dialogue as seen."""
    user_id = await get_current_user_id(authorization)
    await dialogue_service.log_dialogue_seen(user_id, trigger_id)
    return {"status": "seen"}
