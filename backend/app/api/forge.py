"""Forge API router — REST endpoints for currency refinement."""
from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.core.database import get_db
from app.schemas import ForgeOptionResponse, ForgeRefineRequest, ForgeRefineResponse
from app.services import session_service, forge_service

router = APIRouter(prefix="/forge", tags=["forge"])


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


@router.get("/options", response_model=list[ForgeOptionResponse])
async def get_forge_options():
    """Get available refinement options with rates."""
    options = await forge_service.get_refinement_options()
    return [ForgeOptionResponse(**opt) for opt in options]


@router.post("/refine", response_model=ForgeRefineResponse)
async def refine_currency(
    request: ForgeRefineRequest,
    authorization: str = Header(None, alias="Authorization"),
):
    """Refine currency (Dust > Shards > Cuboids > $ELE)."""
    user_id = await get_current_user_id(authorization)
    
    result = await forge_service.refine_currency(
        user_id=user_id,
        refinement_type=request.refinement_type,
        times=request.times,
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Refinement failed"),
        )
    
    return ForgeRefineResponse(**result)
