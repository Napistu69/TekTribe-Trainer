"""Biome unlock service — checks and unlocks biomes based on player progress."""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Companion, Expedition, CurrencyLedger


# Biome unlock criteria
BIOME_UNLOCK_CRITERIA = {
    "mirelands": {
        "type": "adult_companions",
        "threshold": 1,
        "description": "Raise your first Adult companion",
        "icon": "🦕",
    },
    "stonecrest": {
        "type": "dust_spent",
        "threshold": 1000,
        "description": "Spend 1,000 Dust total",
        "icon": "✨",
    },
    "emberfall": {
        "type": "shards_spent",
        "threshold": 1000,
        "description": "Spend 1,000 Shards total",
        "icon": "💎",
    },
    "tek_ruins": {
        "type": "expeditions_completed",
        "threshold": 250,
        "description": "Complete 250 expeditions",
        "icon": "🗺️",
    },
    "void_center": {
        "type": "expeditions_completed",
        "threshold": 500,
        "description": "Complete 500 expeditions",
        "icon": "🌌",
    },
}


async def get_biome_unlock_progress(db: AsyncSession, user_id: str) -> dict:
    """Get unlock progress for all locked biomes.
    
    Returns a dict with biome zone_ids as keys and progress info as values.
    """
    # Count adult companions (maturation >= 100%)
    result = await db.execute(
        select(func.count(Companion.uuid)).where(
            Companion.user_id == user_id,
            Companion.maturation_progress >= 1.0
        )
    )
    adult_count = result.scalar() or 0

    # Count completed expeditions
    result = await db.execute(
        select(func.count(Expedition.uuid)).where(
            Expedition.user_id == user_id,
            Expedition.status == "completed"
        )
    )
    expeditions_completed = result.scalar() or 0

    # Get currency spent totals
    result = await db.execute(
        select(CurrencyLedger).where(CurrencyLedger.user_id == user_id)
    )
    ledger = result.scalar_one_or_none()
    
    dust_spent = 0
    shards_spent = 0
    if ledger and ledger.transaction_log:
        for tx in ledger.transaction_log:
            if tx.get("type") == "spend":
                amount = tx.get("amount", 0)
                currency = tx.get("currency", "")
                if currency == "dust":
                    dust_spent += amount
                elif currency == "shard":
                    shards_spent += amount

    # Build progress for each locked biomes
    progress = {}
    for zone_id, criteria in BIOME_UNLOCK_CRITERIA.items():
        current = 0
        if criteria["type"] == "adult_companions":
            current = adult_count
        elif criteria["type"] == "dust_spent":
            current = dust_spent
        elif criteria["type"] == "shards_spent":
            current = shards_spent
        elif criteria["type"] == "expeditions_completed":
            current = expeditions_completed

        threshold = criteria["threshold"]
        unlocked = current >= threshold

        progress[zone_id] = {
            "zone_id": zone_id,
            "criteria_type": criteria["type"],
            "description": criteria["description"],
            "icon": criteria["icon"],
            "current": current,
            "threshold": threshold,
            "unlocked": unlocked,
            "progress_percent": min(100, int((current / threshold) * 100)) if threshold > 0 else 100,
        }

    return progress


async def check_biome_unlocked(db: AsyncSession, user_id: str, zone_id: str) -> bool:
    """Check if a specific biome is unlocked for a user."""
    if zone_id not in BIOME_UNLOCK_CRITERIA:
        return True  # Verdant Hollow or unknown biomes are always accessible

    progress = await get_biome_unlock_progress(db, user_id)
    return progress.get(zone_id, {}).get("unlocked", False)
