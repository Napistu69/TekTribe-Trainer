"""Expedition service — dispatches and resolves idle expeditions with percentage-based rewards."""
import json
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import Expedition, Companion, InventoryItem

# Load biome data
BIOMES_PATH = Path(__file__).parent.parent / "data" / "biomes.json"
with open(BIOMES_PATH) as f:
    BIOMES = json.load(f)

BIOME_MAP = {b["zone_id"]: b for b in BIOMES["biomes"]}

# Application constant for max companions per expedition
MAX_COMPANIONS = 3

# Percentage-based reward tables per biome
# Each entry: (chance%, min_qty, max_qty) — qty is per companion
REWARD_TABLES = {
    "verdant_hollow": {
        "dust": [(1.0, 10, 15), (1.0, 25, 35), (1.0, 40, 60), (1.0, 60, 90)],
        "meat": [(0.4, 1, 2), (0.6, 2, 3), (0.75, 3, 4), (0.9, 4, 6)],
        "berries": [(0.4, 1, 2), (0.6, 2, 3), (0.75, 3, 4), (0.9, 4, 6)],
        "common_egg": [(0.08,), (0.12,), (0.18,), (0.25,)],
        "uncommon_egg": [(0.03,), (0.05,), (0.08,), (0.12,)],
    },
    "mirelands": {
        "dust": [(1.0, 20, 30), (1.0, 50, 70), (1.0, 80, 120), (1.0, 120, 180)],
        "shard": [(0.3, 5, 10), (0.5, 10, 20), (0.7, 20, 30), (0.85, 30, 50)],
        "jerky": [(0.3, 1, 2), (0.5, 2, 3), (0.65, 3, 4), (0.8, 4, 5)],
        "crops": [(0.3, 1, 2), (0.5, 2, 3), (0.65, 3, 4), (0.8, 4, 5)],
        "uncommon_egg": [(0.05,), (0.08,), (0.12,), (0.18,)],
        "rare_egg": [(0.02,), (0.04,), (0.06,), (0.10,)],
    },
    "stonecrest": {
        "dust": [(1.0, 30, 45), (1.0, 75, 105), (1.0, 120, 180), (1.0, 180, 270)],
        "shard": [(0.5, 10, 20), (0.7, 20, 35), (0.85, 35, 50), (0.95, 50, 75)],
        "cuboid": [(0.1, 1, 2), (0.2, 2, 3), (0.3, 3, 5), (0.4, 5, 8)],
        "rare_egg": [(0.05,), (0.08,), (0.12,), (0.18,)],
        "epic_egg": [(0.01,), (0.02,), (0.04,), (0.06,)],
    },
    "emberfall": {
        "dust": [(1.0, 45, 65), (1.0, 115, 160), (1.0, 180, 260), (1.0, 270, 400)],
        "shard": [(0.6, 15, 25), (0.8, 30, 50), (0.9, 50, 70), (0.95, 70, 100)],
        "cuboid": [(0.25, 2, 3), (0.4, 3, 5), (0.55, 5, 7), (0.7, 7, 10)],
        "sponge": [(0.2, 1, 2), (0.35, 2, 3), (0.5, 3, 4), (0.65, 4, 6)],
        "rare_egg": [(0.05,), (0.08,), (0.12,), (0.18,)],
        "epic_egg": [(0.02,), (0.04,), (0.06,), (0.10,)],
    },
    "tek_ruins": {
        "dust": [(1.0, 50, 75), (1.0, 125, 190), (1.0, 200, 300), (1.0, 300, 450)],
        "shard": [(0.7, 20, 35), (0.85, 40, 60), (0.95, 60, 90), (0.98, 90, 130)],
        "cuboid": [(0.35, 3, 5), (0.55, 5, 8), (0.7, 8, 12), (0.85, 12, 18)],
        "imprint_boost": [(0.05, 1, 1), (0.1, 1, 2), (0.15, 2, 3), (0.2, 3, 4)],
        "epic_egg": [(0.05,), (0.08,), (0.12,), (0.18,)],
        "ascendant_egg": [(0.01,), (0.02,), (0.03,), (0.05,)],
    },
    "void_center": {
        "dust": [(1.0, 75, 110), (1.0, 190, 280), (1.0, 300, 450), (1.0, 450, 675)],
        "shard": [(0.8, 30, 50), (0.95, 60, 90), (0.98, 90, 130), (0.99, 130, 200)],
        "cuboid": [(0.5, 5, 8), (0.7, 8, 12), (0.85, 12, 18), (0.95, 18, 25)],
        "care_kit": [(0.1, 1, 1), (0.2, 1, 2), (0.3, 2, 3), (0.4, 3, 5)],
        "epic_egg": [(0.05,), (0.08,), (0.12,), (0.18,)],
        "ascendant_egg": [(0.02,), (0.03,), (0.05,), (0.08,)],
    },
}

# Duration index mapping
DURATION_INDEX = {"2h": 0, "6h": 1, "12h": 2, "24h": 3}


def _roll_reward(chance: float) -> bool:
    """Roll against a percentage chance."""
    return secrets.randbelow(10000) / 100 < chance


def _roll_quantity(min_qty: int, max_qty: int) -> int:
    """Roll a random quantity between min and max."""
    if min_qty == max_qty:
        return min_qty
    return min_qty + secrets.randbelow(max_qty - min_qty + 1)


def _get_duration_index(duration_key: str) -> int:
    """Get the reward table index for a duration."""
    return DURATION_INDEX.get(duration_key, 0)


async def dispatch_expedition(
    db: AsyncSession,
    user_id: str,
    companion_uuids: list[str],
    biome_zone: str,
    duration_key: str,
) -> Expedition:
    """Dispatch one or more companions on an expedition."""
    if biome_zone not in BIOME_MAP:
        raise ValueError(f"Unknown biome: {biome_zone}")
    
    biome = BIOME_MAP[biome_zone]
    
    if not biome.get("in_phase1", False):
        raise ValueError(f"Biome {biome_zone} is not yet accessible")
    
    if duration_key not in BIOMES["durations"]:
        raise ValueError(f"Unknown duration: {duration_key}")
    
    duration_hours = BIOMES["durations"][duration_key]["hours"]
    
    if len(companion_uuids) == 0:
        raise ValueError("At least one companion required")
    if len(companion_uuids) > MAX_COMPANIONS:
        raise ValueError(f"Maximum {MAX_COMPANIONS} companions per expedition")
    
    for uuid in companion_uuids:
        result = await db.execute(
            select(Companion).where(
                Companion.uuid == uuid,
                Companion.user_id == user_id
            )
        )
        companion = result.scalar_one_or_none()
        if not companion:
            raise ValueError(f"Companion {uuid} not found")
        if companion.current_state == "on_expedition":
            raise ValueError(f"Companion {companion.species} is already on expedition")
        if companion.health_status < 0.5:
            raise ValueError(f"Companion {companion.species} is too injured (health < 0.5)")
    
    base_risk = biome["base_risk"]
    injury_chance = BIOMES["injury_chances"][duration_key]
    risk_level = min(1.0, base_risk + injury_chance * 0.5)
    
    now = datetime.now(timezone.utc)
    expedition = Expedition(
        user_id=user_id,
        biome_zone=biome_zone,
        dispatched_at=now,
        returns_at=now + timedelta(hours=duration_hours),
        status="dispatched",
        risk_level=risk_level,
        result={"companion_uuids": companion_uuids, "companion_results": []},
    )
    db.add(expedition)
    
    for uuid in companion_uuids:
        result = await db.execute(
            select(Companion).where(Companion.uuid == uuid)
        )
        companion = result.scalar_one()
        companion.current_state = "on_expedition"
    
    await db.commit()
    await db.refresh(expedition)
    return expedition


async def resolve_expedition(db: AsyncSession, expedition_uuid: str) -> dict:
    """Resolve a completed expedition with percentage-based rewards."""
    result = await db.execute(
        select(Expedition).where(Expedition.uuid == expedition_uuid)
    )
    expedition = result.scalar_one_or_none()
    if not expedition:
        raise ValueError("Expedition not found")
    
    if expedition.status != "dispatched":
        raise ValueError(f"Expedition is {expedition.status}, not dispatched")
    
    if datetime.now(timezone.utc) < expedition.returns_at:
        raise ValueError("Expedition has not returned yet")
    
    biome = BIOME_MAP[expedition.biome_zone]
    companion_uuids = expedition.result.get("companion_uuids", []) if expedition.result else []
    
    # Determine duration index
    duration_hours = (expedition.returns_at - expedition.dispatched_at).total_seconds() / 3600
    duration_key = None
    for key, d in BIOMES["durations"].items():
        if d["hours"] == duration_hours:
            duration_key = key
            break
    if not duration_key:
        duration_key = "2h"
    dur_idx = _get_duration_index(duration_key)
    
    # Get reward table for this biome
    reward_table = REWARD_TABLES.get(expedition.biome_zone, {})
    
    # Roll rewards for each companion
    all_rewards = {
        "dust": 0, "shard": 0, "cuboid": 0, "ele": 0,
        "meat": 0, "jerky": 0, "berries": 0, "crops": 0,
        "sponge": 0, "imprint_boost": 0, "care_kit": 0,
        "common_egg": 0, "uncommon_egg": 0, "rare_egg": 0, "epic_egg": 0, "ascendant_egg": 0,
    }
    
    companion_results = []
    for uuid in companion_uuids:
        companion_result = await db.execute(
            select(Companion).where(Companion.uuid == uuid)
        )
        companion = companion_result.scalar_one()
        
        # Roll each reward type
        for reward_type, entries in reward_table.items():
            if dur_idx >= len(entries):
                continue
            entry = entries[dur_idx]
            chance = entry[0]
            
            if _roll_reward(chance * 100):  # Convert to percentage
                if len(entry) == 1:
                    # Egg or fixed quantity
                    qty = 1
                else:
                    qty = _roll_quantity(entry[1], entry[2])
                
                all_rewards[reward_type] = all_rewards.get(reward_type, 0) + qty
        
        # Injury check
        injury_chance = BIOMES["injury_chances"].get(duration_key, 0.05)
        injured = _roll_reward(injury_chance * 100)
        
        if injured:
            companion.health_status = max(0.1, companion.health_status - 0.3)
        
        companion.current_state = "resting"
        companion_results.append({
            "companion_uuid": str(uuid),
            "species": companion.species,
            "injured": injured,
        })
    
    # Award dust
    total_dust = all_rewards.get("dust", 0)
    if total_dust > 0:
        from app.services.currency_service import award_dust
        await award_dust(expedition.user_id, total_dust, f"expedition_{expedition.biome_zone}")
    
    # Award shards
    total_shards = all_rewards.get("shard", 0)
    if total_shards > 0:
        from app.services.currency_service import award_shards
        await award_shards(expedition.user_id, total_shards, f"expedition_{expedition.biome_zone}")
    
    # Award cuboids
    total_cuboids = all_rewards.get("cuboid", 0)
    if total_cuboids > 0:
        from app.services.currency_service import award_cuboids
        await award_cuboids(expedition.user_id, total_cuboids, f"expedition_{expedition.biome_zone}")
    
    # Award items to inventory
    item_rewards = ["meat", "jerky", "berries", "crops", "sponge", "imprint_boost", "care_kit"]
    for item_id in item_rewards:
        qty = all_rewards.get(item_id, 0)
        if qty > 0:
            await _add_to_inventory(db, expedition.user_id, item_id, qty)
    
    # Award eggs (create Egg records)
    egg_rarities = ["common_egg", "uncommon_egg", "rare_egg", "epic_egg", "ascendant_egg"]
    egg_count = 0
    for egg_type in egg_rarities:
        qty = all_rewards.get(egg_type, 0)
        for _ in range(qty):
            rarity = egg_type.replace("_egg", "")
            await _create_egg(db, expedition.user_id, rarity)
            egg_count += 1
    
    expedition.status = "completed"
    expedition.result = {
        "companion_uuids": companion_uuids,
        "companion_results": companion_results,
        "rewards": all_rewards,
        "total_dust_gained": total_dust,
        "total_shards_gained": total_shards,
        "total_cuboids_gained": total_cuboids,
        "eggs_gained": egg_count,
    }
    
    await db.commit()
    
    return {
        "expedition_uuid": str(expedition.uuid),
        "biome_zone": expedition.biome_zone,
        "companion_results": companion_results,
        "rewards": all_rewards,
        "total_dust_gained": total_dust,
        "total_shards_gained": total_shards,
        "total_cuboids_gained": total_cuboids,
        "eggs_gained": egg_count,
    }


async def _add_to_inventory(db: AsyncSession, user_id: str, item_id: str, quantity: int) -> None:
    """Add items to user's inventory."""
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


async def _create_egg(db: AsyncSession, user_id: str, rarity: str) -> None:
    """Create an egg of a given rarity."""
    from app.models import Egg
    import random
    
    # Load roster to get species for rarity
    ROSTER_PATH = Path(__file__).parent.parent / "data" / "roster_v0_2.json"
    with open(ROSTER_PATH) as f:
        roster = json.load(f)
    
    creatures = [c for c in roster["creatures"] if c["rarity"] == rarity]
    if not creatures:
        creatures = roster["creatures"]
    
    selected = random.choice(creatures)
    
    egg = Egg(
        user_id=user_id,
        species=selected["creature_id"],
        rarity=rarity,
        source="expedition",
        pulled_at=datetime.now(timezone.utc),
        hatched=False,
        temperature=0.5,
        stability=0.5,
    )
    db.add(egg)


async def get_active_expeditions(db: AsyncSession, user_id: str) -> list[Expedition]:
    """Get all active (dispatched) expeditions for a user."""
    result = await db.execute(
        select(Expedition).where(
            Expedition.user_id == user_id,
            Expedition.status == "dispatched"
        ).order_by(Expedition.returns_at)
    )
    return list(result.scalars().all())


async def get_expedition_history(db: AsyncSession, user_id: str, limit: int = 20) -> list[Expedition]:
    """Get past completed expeditions."""
    result = await db.execute(
        select(Expedition).where(
            Expedition.user_id == user_id,
            Expedition.status == "completed"
        ).order_by(Expedition.dispatched_at.desc()).limit(limit)
    )
    return list(result.scalars().all())
