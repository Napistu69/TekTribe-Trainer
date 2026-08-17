"""Economy API router — REST endpoints for currency and shop."""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas import EconomyBalanceResponse, EconomyHistoryResponse, ShopItemResponse, ShopPurchaseRequest
from app.services import session_service, currency_service

router = APIRouter(prefix="/economy", tags=["economy"])


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


@router.get("/balance", response_model=EconomyBalanceResponse)
async def get_balance(
    authorization: str = Header(None, alias="Authorization"),
):
    """Get the current user's currency balances."""
    user_id = await get_current_user_id(authorization)
    balance = await currency_service.get_balance(user_id)
    
    if not balance:
        return EconomyBalanceResponse(
            dust=0, shard=0, cuboid=0, ele=0
        )
    
    return EconomyBalanceResponse(
        dust=balance.dust_balance,
        shard=balance.shard_balance,
        cuboid=balance.cuboid_balance,
        ele=balance.ele_balance,
    )


@router.get("/history", response_model=EconomyHistoryResponse)
async def get_history(
    limit: int = 50,
    authorization: str = Header(None, alias="Authorization"),
):
    """Get transaction history for the current user."""
    user_id = await get_current_user_id(authorization)
    history = await currency_service.get_transaction_history(user_id, limit)
    
    return EconomyHistoryResponse(transactions=history)


@router.get("/shop", response_model=list[ShopItemResponse])
async def get_shop_items():
    """Get available shop items."""
    import json
    from pathlib import Path
    
    shop_path = Path(__file__).parent.parent / "data" / "shop_items.json"
    with open(shop_path) as f:
        data = json.load(f)
    
    return [ShopItemResponse(**item) for item in data["shop_items"]]


@router.post("/shop/purchase")
async def purchase_item(
    request: ShopPurchaseRequest,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Purchase a shop item with Dust."""
    user_id = await get_current_user_id(authorization)
    
    # Get shop items
    import json
    from pathlib import Path
    
    shop_path = Path(__file__).parent.parent / "data" / "shop_items.json"
    with open(shop_path) as f:
        data = json.load(f)
    
    item = next((i for i in data["shop_items"] if i["item_id"] == request.item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Spend dust
    success, new_balance = await currency_service.spend_dust(user_id, item["cost"], f"shop_{request.item_id}")
    if not success:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient Dust. Need {item['cost']}, have {new_balance}"
        )
    
    # Apply effect
    result = await currency_service.apply_shop_effect(db, user_id, request.companion_uuid, item)
    
    return {
        "success": True,
        "item_id": request.item_id,
        "cost": item["cost"],
        "new_balance": new_balance,
        "effect": result,
    }
