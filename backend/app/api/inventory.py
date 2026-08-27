"""Inventory API router — REST endpoints for items and inventory."""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import session_service, inventory_service

router = APIRouter(prefix="/inventory", tags=["inventory"])


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


@router.get("/")
async def get_inventory(
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Get user's inventory items."""
    user_id = await get_current_user_id(authorization)
    items = await inventory_service.get_inventory(db, user_id)
    return {"items": items}


@router.post("/purchase")
async def purchase_item(
    request: dict,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Purchase an item from the shop."""
    user_id = await get_current_user_id(authorization)
    item_id = request.get("item_id")
    quantity = request.get("quantity", 1)
    
    if not item_id:
        raise HTTPException(status_code=400, detail="item_id required")
    
    result = await inventory_service.purchase_item(db, user_id, item_id, quantity)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=result["error"],
        )
    return result


@router.post("/use")
async def use_item(
    request: dict,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Use an inventory item on a companion."""
    user_id = await get_current_user_id(authorization)
    companion_uuid = request.get("companion_uuid")
    item_id = request.get("item_id")
    
    if not companion_uuid or not item_id:
        raise HTTPException(
            status_code=400,
            detail="companion_uuid and item_id required",
        )
    
    result = await inventory_service.use_item_on_companion(
        db, user_id, companion_uuid, item_id
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/free-action")
async def perform_free_action(
    request: dict,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Perform a free care action (imprint or rest)."""
    user_id = await get_current_user_id(authorization)
    companion_uuid = request.get("companion_uuid")
    action_type = request.get("action")
    
    if not companion_uuid or not action_type:
        raise HTTPException(
            status_code=400,
            detail="companion_uuid and action required",
        )
    
    result = await inventory_service.perform_free_care_action(
        db, user_id, companion_uuid, action_type
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
