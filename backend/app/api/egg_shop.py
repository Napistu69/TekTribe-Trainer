"""Egg shop API router — REST endpoints for purchasing eggs with shards."""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import session_service, egg_shop_service

router = APIRouter(prefix="/shop", tags=["shop"])


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


@router.get("/eggs")
async def get_egg_offerings():
    """Get available egg shop offerings."""
    offerings = egg_shop_service.get_egg_shop_offerings()
    return {"offerings": offerings}


@router.post("/eggs/purchase")
async def purchase_egg(
    request: dict,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Purchase an egg by rarity tier."""
    user_id = await get_current_user_id(authorization)
    rarity = request.get("rarity")
    
    if not rarity:
        raise HTTPException(status_code=400, detail="rarity required")
    
    result = await egg_shop_service.purchase_egg(db, user_id, rarity)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=result["error"],
        )
    return result
