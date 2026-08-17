"""Lockdown API router — REST endpoints for account lockdown status."""
from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.services import session_service, lockdown_service

router = APIRouter(prefix="/lockdown", tags=["lockdown"])


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


@router.get("/status")
async def get_lockdown_status(
    authorization: str = Header(None, alias="Authorization"),
):
    """Get lockdown status for the current user."""
    user_id = await get_current_user_id(authorization)
    return await lockdown_service.get_lockdown_status(user_id)


@router.post("/check-graduation")
async def check_graduation(
    authorization: str = Header(None, alias="Authorization"),
):
    """Check if user can graduate from lockdown."""
    user_id = await get_current_user_id(authorization)
    graduated = await lockdown_service.check_graduation(user_id)
    return {"graduated": graduated}
