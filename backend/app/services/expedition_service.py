"""Expedition service — dispatches and resolves idle expeditions."""
import json
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import Expedition, Companion

# Load biome data
BIOMES_PATH = Path(__file__).parent.parent / "data" / "biomes.json"
with open(BIOMES_PATH) as f:
    BIOMES = json.load(f)

BIOME_MAP = {b["zone_id"]: b for b in BIOMES["biomes"]}


async def dispatch_expedition(
    db: AsyncSession,
    user_id: str,
    companion_uuids: list[str],
    biome_zone: str,
    duration_key: str,
) -> Expedition:
    """Dispatch one or more companions on an expedition.
    
    - Sets companion states to 'on_expedition'
    - Calculates return time
    - Sets risk level based on biome and duration
    - Supports up to 3 companions per expedition
    """
    # Validate biome
    if biome_zone not in BIOME_MAP:
        raise ValueError(f"Unknown biome: {biome_zone}")
    
    biome = BIOME_MAP[biome_zone]
    
    # Phase 1: only Verdant Hollow accessible
    if not biome.get("in_phase1", False):
        raise ValueError(f"Biome {biome_zone} is not yet accessible")
    
    # Validate duration
    if duration_key not in BIOMES["durations"]:
        raise ValueError(f"Unknown duration: {duration_key}")
    
    duration_hours = BIOMES["durations"][duration_key]["hours"]
    
    # Validate companion count (max 3)
    if len(companion_uuids) == 0:
        raise ValueError("At least one companion required")
    if len(companion_uuids) > 3:
        raise ValueError("Maximum 3 companions per expedition")
    
    # Verify all companions are owned and available
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
    
    # Calculate risk level
    base_risk = biome["base_risk"]
    injury_chance = BIOMES["injury_chances"][duration_key]
    risk_level = min(1.0, base_risk + injury_chance * 0.5)
    
    # Create expedition
    now = datetime.now(timezone.utc)
    expedition = Expedition(
        user_id=user_id,
        biome_zone=biome_zone,
        dispatched_at=now,
        returns_at=now + timedelta(hours=duration_hours),
        status="dispatched",
        risk_level=risk_level,
        companion_uuids=companion_uuids,
        max_companions=3,
    )
    db.add(expedition)
    
    # Update all companion states
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
    """Resolve a completed expedition."""
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
    
    # Calculate outcome for each companion
    results = []
    for uuid in expedition.companion_uuids:
        companion_result = await db.execute(
            select(Companion).where(Companion.uuid == uuid)
        )
        companion = companion_result.scalar_one()
        outcome = calculate_outcome(companion, biome, expedition)
        
        # Apply results
        if outcome["companion_injured"]:
            companion.health_status = max(0.1, companion.health_status - 0.3)
        
        companion.current_state = "resting"
        results.append({
            "companion_uuid": str(uuid),
            "species": companion.species,
            **outcome
        })
    
    expedition.status = "completed"
    expedition.result = {"companion_results": results}
    
    # Award dust (sum of all companions)
    total_dust = sum(r["dust_gained"] for r in results)
    if total_dust > 0:
        from app.services.currency_service import award_dust
        await award_dust(expedition.user_id, total_dust, f"expedition_{expedition.biome_zone}")
    
    # Apply imprint changes
    for uuid, result in zip(expedition.companion_uuids, results):
        companion_result = await db.execute(
            select(Companion).where(Companion.uuid == uuid)
        )
        companion = companion_result.scalar_one()
        if result["imprint_change"] != 0:
            companion.imprint_level += result["imprint_change"]
    
    await db.commit()
    
    return {
        "expedition_uuid": str(expedition.uuid),
        "biome_zone": expedition.biome_zone,
        "companion_results": results,
        "total_dust_gained": total_dust,
    }


def calculate_outcome(companion: Companion, biome: dict, expedition: Expedition) -> dict:
    """Calculate expedition outcome for a single companion."""
    duration_key = None
    for key, d in BIOMES["durations"].items():
        if d["hours"] == (expedition.returns_at - expedition.dispatched_at).total_seconds() / 3600:
            duration_key = key
            break
    
    if not duration_key:
        duration_key = "6h"
    
    # Base success chance from companion stats
    stats = companion.base_stats
    avg_stat = sum(stats.values()) / len(stats) if stats else 50
    stat_factor = min(1.0, avg_stat / 100)
    
    # Risk factor
    risk_factor = 1.0 - expedition.risk_level
    
    # Duration multiplier
    duration_mult = biome["duration_multipliers"][duration_key]
    
    # RNG variance (±20%)
    rng = 0.8 + secrets.randbelow(40) / 100  # 0.8 to 1.2
    
    # Final success chance
    success_chance = min(0.95, stat_factor * risk_factor * rng)
    roll = secrets.randbelow(100) / 100
    
    success = roll < success_chance
    
    # Calculate rewards
    base_dust = biome["base_dust_reward"]
    dust_gained = int(base_dust * duration_mult * rng) if success else int(base_dust * duration_mult * 0.25)
    
    # Injury check
    injury_chance = BIOMES["injury_chances"][duration_key]
    injured = secrets.randbelow(100) / 100 < injury_chance
    
    # Oracle fragment chance
    oracle_chance = BIOMES.get("oracle_fragment_chance_tek_ruins") if biome["zone_id"] == "tek_ruins" else BIOMES["oracle_fragment_chance"]
    oracle_fragment_found = secrets.randbelow(100) / 100 < oracle_chance
    
    # Imprint change
    imprint_change = 0
    if success:
        imprint_change = 5 + int(duration_mult)  # 5-11 based on duration
    else:
        imprint_change = -2 - int(duration_mult / 2)  # -2 to -5
    
    # Generate encounter story
    encounter_story = generate_encounter_story(biome, success, injured, oracle_fragment_found)
    
    return {
        "success": success,
        "dust_gained": dust_gained,
        "companion_injured": injured,
        "oracle_fragment_found": oracle_fragment_found,
        "encounter_story": encounter_story,
        "imprint_change": imprint_change,
        "resources_gained": biome["resources"][:2] if success else [],
    }


def generate_encounter_story(biome: dict, success: bool, injured: bool, oracle_fragment: bool) -> str:
    """Generate a narrative encounter story."""
    biome_name = biome["name"]
    
    stories = []
    
    if success:
        stories.append(f"Your companion explored the {biome_name} and returned triumphantly.")
        if oracle_fragment:
            stories.append("They discovered a glowing Oracle fragment along the way!")
    else:
        stories.append(f"The {biome_name} proved challenging. Your companion returned empty-handed but wiser.")
    
    if injured:
        stories.append("They sustained minor injuries but will recover with rest.")
    
    return " ".join(stories)


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
