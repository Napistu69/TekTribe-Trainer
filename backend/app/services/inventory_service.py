"""Inventory service — handles item purchases and usage."""
import json
import os
from math import floor
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import InventoryItem, Companion, CareState

# Load shop items
SHOP_ITEMS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "shop_items.json")
with open(SHOP_ITEMS_PATH) as f:
    SHOP_ITEMS = json.load(f)["shop_items"]

# Item lookup by ID
ITEM_MAP = {item["item_id"]: item for item in SHOP_ITEMS}

# Diet-compatible feed items
FEED_ITEMS = {
    "carnivore": ["meat", "jerky"],
    "herbivore": ["berries", "crops"],
    "omnivore": ["meat", "jerky", "berries", "crops"],
}

# Dust payout rate (30% of item cost)
DUST_PAYOUT_RATE = 0.3

# Free action dust rewards
FREE_IMPRINT_DUST = 1
FREE_REST_DUST = 1
FREE_IMPRINT_GAIN = 5
FREE_REST_ENERGY = 0.25


async def get_inventory(db: AsyncSession, user_id: str) -> list[dict]:
    """Get user's inventory items."""
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.user_id == user_id)
    )
    items = result.scalars().all()
    return [
        {
            "item_id": item.item_id,
            "quantity": item.quantity,
            "name": ITEM_MAP.get(item.item_id, {}).get("name", item.item_id),
            "description": ITEM_MAP.get(item.item_id, {}).get("description", ""),
        }
        for item in items
        if item.quantity > 0
    ]


async def purchase_item(db: AsyncSession, user_id: str, item_id: str, quantity: int = 1) -> dict:
    """Purchase an item from the shop."""
    if item_id not in ITEM_MAP:
        return {"success": False, "error": "Item not found"}
    
    item_def = ITEM_MAP[item_id]
    total_cost = item_def["cost"] * quantity
    
    # Check user balance
    from app.services.currency_service import get_balance, deduct_dust
    balance = await get_balance(user_id)
    if balance["dust"] < total_cost:
        return {"success": False, "error": "Insufficient dust"}
    
    # Deduct dust
    await deduct_dust(user_id, total_cost, f"shop_purchase_{item_id}")
    
    # Add to inventory
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.user_id == user_id,
            InventoryItem.item_id == item_id,
        )
    )
    inv_item = result.scalar_one_or_none()
    
    if inv_item:
        inv_item.quantity += quantity
    else:
        inv_item = InventoryItem(
            user_id=user_id,
            item_id=item_id,
            quantity=quantity,
        )
        db.add(inv_item)
    
    await db.commit()
    
    return {
        "success": True,
        "item_id": item_id,
        "quantity": quantity,
        "total_cost": total_cost,
    }


async def use_item_on_companion(
    db: AsyncSession,
    user_id: str,
    companion_uuid: str,
    item_id: str,
) -> dict:
    """Use an inventory item on a companion."""
    if item_id not in ITEM_MAP:
        return {"success": False, "error": "Item not found"}
    
    # Verify companion ownership
    result = await db.execute(
        select(Companion).where(
            Companion.uuid == companion_uuid,
            Companion.user_id == user_id,
        )
    )
    companion = result.scalar_one_or_none()
    if not companion:
        return {"success": False, "error": "Companion not found"}
    
    # Check inventory
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.user_id == user_id,
            InventoryItem.item_id == item_id,
            InventoryItem.quantity > 0,
        )
    )
    inv_item = result.scalar_one_or_none()
    if not inv_item:
        return {"success": False, "error": "Item not in inventory"}
    
    item_def = ITEM_MAP[item_id]
    effect = item_def.get("effect", {})
    
    # Get care state
    result = await db.execute(
        select(CareState).where(CareState.companion_uuid == companion_uuid)
    )
    care_state = result.scalar_one_or_none()
    if not care_state:
        return {"success": False, "error": "Care state not found"}
    
    # Apply effect based on item type
    dust_gained = 0
    action_type = effect.get("type", "")
    
    if action_type == "care" and effect.get("action") == "feed":
        # Check diet compatibility
        feed_item_id = item_id
        compatible_feeds = FEED_ITEMS.get(companion.diet, [])
        if feed_item_id not in compatible_feeds:
            return {
                "success": False,
                "error": f"{companion.species} is a {companion.diet} and cannot eat {item_def['name']}",
            }
        
        # Apply hunger restore
        hunger_restore = effect.get("value", 0.4)
        care_state.hunger = min(1.0, care_state.hunger + hunger_restore)
        
        # Award dust (30% of item cost)
        dust_gained = floor(item_def["cost"] * DUST_PAYOUT_RATE)
        
    elif action_type == "care" and effect.get("action") == "clean":
        # Apply cleanliness restore
        clean_restore = effect.get("value", 1.0)
        care_state.cleanliness = min(1.0, care_state.cleanliness + clean_restore)
        
        # Award dust (30% of item cost)
        dust_gained = floor(item_def["cost"] * DUST_PAYOUT_RATE)
        
    elif action_type == "imprint_boost":
        # Apply imprint boost
        imprint_boost = effect.get("value", 0.2)
        companion.imprint_level = min(100, companion.imprint_level + int(imprint_boost * 100))
        dust_gained = 0  # Premium item, no dust back
        
    elif action_type == "care_all":
        # Restore all meters
        restore_value = effect.get("value", 0.7)
        care_state.hunger = min(1.0, care_state.hunger + restore_value)
        care_state.cleanliness = min(1.0, care_state.cleanliness + restore_value)
        care_state.energy = min(1.0, care_state.energy + restore_value)
        care_state.morale = min(1.0, care_state.morale + restore_value)
        dust_gained = floor(item_def["cost"] * DUST_PAYOUT_RATE)
    
    # Consume item
    inv_item.quantity -= 1
    
    # Award dust
    if dust_gained > 0:
        from app.services.currency_service import award_dust
        await award_dust(user_id, dust_gained, f"care_{action_type}_{item_id}")
    
    await db.commit()
    
    return {
        "success": True,
        "item_id": item_id,
        "action": action_type,
        "dust_gained": dust_gained,
        "care_state": {
            "hunger": care_state.hunger,
            "energy": care_state.energy,
            "morale": care_state.morale,
            "cleanliness": care_state.cleanliness,
        },
        "imprint_level": companion.imprint_level,
    }


async def perform_free_care_action(
    db: AsyncSession,
    user_id: str,
    companion_uuid: str,
    action_type: str,
) -> dict:
    """Perform a free care action (imprint or rest)."""
    if action_type not in ("imprint", "rest"):
        return {"success": False, "error": "Only imprint and rest are free actions"}
    
    # Verify companion ownership
    result = await db.execute(
        select(Companion).where(
            Companion.uuid == companion_uuid,
            Companion.user_id == user_id,
        )
    )
    companion = result.scalar_one_or_none()
    if not companion:
        return {"success": False, "error": "Companion not found"}
    
    # Get care state
    result = await db.execute(
        select(CareState).where(CareState.companion_uuid == companion_uuid)
    )
    care_state = result.scalar_one_or_none()
    if not care_state:
        return {"success": False, "error": "Care state not found"}
    
    dust_gained = 0
    
    if action_type == "imprint":
        # Free imprint: +5% imprint, +1 dust
        companion.imprint_level = min(100, companion.imprint_level + FREE_IMPRINT_GAIN)
        dust_gained = FREE_IMPRINT_DUST
        
    elif action_type == "rest":
        # Free rest: +25% energy, +1 dust
        care_state.energy = min(1.0, care_state.energy + FREE_REST_ENERGY)
        dust_gained = FREE_REST_DUST
    
    # Award dust
    if dust_gained > 0:
        from app.services.currency_service import award_dust
        await award_dust(user_id, dust_gained, f"care_{action_type}_free")
    
    await db.commit()
    
    return {
        "success": True,
        "action": action_type,
        "dust_gained": dust_gained,
        "imprint_level": companion.imprint_level,
        "care_state": {
            "hunger": care_state.hunger,
            "energy": care_state.energy,
            "morale": care_state.morale,
            "cleanliness": care_state.cleanliness,
        },
    }
