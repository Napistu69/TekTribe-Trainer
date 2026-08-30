"""Egg shop service — handles egg purchases by rarity tier."""
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Egg

# Load roster data
ROSTER_PATH = Path(__file__).parent.parent / "data" / "roster_v0_2.json"
with open(ROSTER_PATH) as f:
    ROSTER = json.load(f)

CREATURES = ROSTER["creatures"]
RARITY_ORDER = ["common", "uncommon", "rare", "epic", "legendary"]

# Egg shop pricing (shards)
EGG_SHOP_PRICING = {
    "common": 50,
    "uncommon": 150,
    "rare": 400,
    "epic": 750,
    "legendary": 1500,
}

# Daily stock per tier
EGG_SHOP_STOCK = {
    "common": 5,
    "uncommon": 3,
    "rare": 2,
    "epic": 1,
    "legendary": 1,
}

# 5% chance to upgrade to next tier
UPGRADE_CHANCE = 0.05


def get_egg_shop_offerings() -> list[dict]:
    """Get current egg shop offerings with pricing."""
    offerings = []
    for rarity in RARITY_ORDER:
        if rarity not in EGG_SHOP_PRICING:
            continue
        offerings.append({
            "rarity": rarity,
            "cost": EGG_SHOP_PRICING[rarity],
            "currency": "shard",
            "daily_stock": EGG_SHOP_STOCK.get(rarity, 0),
            "upgrade_chance": UPGRADE_CHANCE if rarity != "legendary" else 0,
        })
    return offerings


async def purchase_egg(db: AsyncSession, user_id: str, rarity: str) -> dict:
    """Purchase an egg by rarity tier.
    
    Companion rarity matches egg tier with 5% chance to upgrade to next tier.
    e.g. common egg → random common companion, 5% chance for uncommon.
    """
    if rarity not in EGG_SHOP_PRICING:
        return {"success": False, "error": "Invalid rarity tier"}

    cost = EGG_SHOP_PRICING[rarity]

    # Check shard balance
    from app.services.currency_service import get_balance, spend_shards
    balance = await get_balance(user_id)
    if not balance or balance.shard_balance < cost:
        return {"success": False, "error": "Insufficient shards"}

    # Check daily stock
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(Egg).where(
            Egg.user_id == user_id,
            Egg.source == "shop",
            Egg.pulled_at >= today_start,
            Egg.rarity == rarity,
        )
    )
    eggs_today = len(result.scalars().all())
    if eggs_today >= EGG_SHOP_STOCK.get(rarity, 0):
        return {"success": False, "error": f"Daily stock for {rarity} eggs exhausted"}

    # Spend shards
    success, new_balance = await spend_shards(user_id, cost, f"egg_shop_{rarity}")
    if not success:
        return {"success": False, "error": "Failed to spend shards"}

    # Roll for upgrade (5% chance to get next tier)
    actual_rarity = rarity
    roll = secrets.randbelow(100)
    if roll < int(UPGRADE_CHANCE * 100) and rarity != "legendary":
        rarity_idx = RARITY_ORDER.index(rarity)
        if rarity_idx < len(RARITY_ORDER) - 1:
            actual_rarity = RARITY_ORDER[rarity_idx + 1]

    # Select random creature from tier pool
    tier_creatures = [c for c in CREATURES if c["rarity"] == actual_rarity]
    if not tier_creatures:
        tier_creatures = CREATURES
    selected = secrets.choice(tier_creatures)

    # Create egg
    egg = Egg(
        user_id=user_id,
        species=selected["creature_id"],
        rarity=selected["rarity"],
        source="shop",
        pulled_at=datetime.now(timezone.utc),
        hatched=False,
        temperature=0.5,
        stability=0.5,
    )
    db.add(egg)
    await db.commit()
    await db.refresh(egg)

    return {
        "success": True,
        "egg_uuid": str(egg.uuid),
        "species": selected["creature_id"],
        "rarity": selected["rarity"],
        "cost": cost,
        "upgraded": actual_rarity != rarity,
    }
