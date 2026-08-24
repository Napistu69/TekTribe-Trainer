"""Companion service — creates and manages companion entities."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import Companion, Egg, CareState
from app.services import genetics_service


async def hatch_egg(db: AsyncSession, user_id: str, egg_uuid: str) -> Optional[Companion]:
    """Hatch an egg into a companion.
    
    - Converts egg to companion
    - Initializes all fields from species template
    - Generates hidden genetic potential (server-side only)
    - Sets personality, color regions, base stats
    - Marks egg as hatched
    """
    # Fetch the egg
    result = await db.execute(
        select(Egg).where(Egg.user_id == user_id, Egg.uuid == egg_uuid)
    )
    egg = result.scalar_one_or_none()
    
    if not egg:
        raise ValueError("Egg not found")
    if egg.hatched:
        raise ValueError("Egg already hatched")
    
    species = egg.species
    
    # Generate companion data
    base_stats = genetics_service.generate_base_stats(species)
    personality_type, personality_traits, behavioral_quirks = genetics_service.generate_personality(species)
    color_regions = genetics_service.generate_color_regions()
    hidden_potential = await genetics_service.generate_hidden_potential()
    
    # Create companion
    companion = Companion(
        user_id=user_id,
        species=species,
        name=None,  # Player names it later
        origin_type=egg.source,
        origin_metadata={"egg_uuid": str(egg.uuid), "source": egg.source},
        creation_timestamp=datetime.now(timezone.utc),
        life_stage="hatchling",
        maturation_progress=0.0,
        base_stats=base_stats,
        mutated_stats={},  # No mutations on first hatch
        hidden_genetic_potential=hidden_potential,
        color_regions=color_regions,
        seasonal_pattern=None,
        personality_type=personality_type,
        personality_traits=personality_traits,
        behavioral_quirks=behavioral_quirks,
        bond_level=0,
        care_streak=0,
        parent_a_uuid=None,
        parent_b_uuid=None,
        generation=0,
        current_state="resting",
        health_status=1.0,
        breeding_cooldown_until=None,
        on_chain_record=None,
    )
    db.add(companion)
    await db.flush()  # Generate companion UUID
    
    # Create initial care state
    care_state = CareState(
        companion_uuid=companion.uuid,  # Now populated after flush
        hunger=1.0,
        energy=1.0,
        morale=1.0,
        cleanliness=1.0,
        last_updated=datetime.now(timezone.utc),
    )
    db.add(care_state)
    
    # Mark egg as hatched
    egg.hatched = True
    egg.hatched_at = datetime.now(timezone.utc)
    egg.hatched_companion_uuid = companion.uuid
    
    await db.commit()
    await db.refresh(companion)
    return companion


async def get_companion(db: AsyncSession, user_id: str, companion_uuid: str) -> Optional[Companion]:
    """Get a companion by UUID, ensuring user ownership."""
    result = await db.execute(
        select(Companion).where(
            Companion.uuid == companion_uuid,
            Companion.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def get_companions(db: AsyncSession, user_id: str) -> list[Companion]:
    """Get all companions for a user."""
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Companion)
        .where(Companion.user_id == user_id)
        .options(selectinload(Companion.care_state))
    )
    return list(result.scalars().all())


async def update_life_stage(db: AsyncSession, companion_uuid: str) -> Optional[str]:
    """Check and update life stage based on maturation progress and bond level.
    
    Returns the new life stage if changed, None otherwise.
    """
    result = await db.execute(
        select(Companion).where(Companion.uuid == companion_uuid)
    )
    companion = result.scalar_one_or_none()
    if not companion:
        return None
    
    old_stage = companion.life_stage
    
    # Stage progression rules
    if companion.maturation_progress >= 1.0 and companion.bond_level >= 1000:
        companion.life_stage = "elder"
    elif companion.maturation_progress >= 0.7 and companion.bond_level >= 500:
        companion.life_stage = "adult"
    elif companion.maturation_progress >= 0.3 and companion.bond_level >= 100:
        companion.life_stage = "juvenile"
    elif companion.maturation_progress >= 0.1:
        companion.life_stage = "hatchling"
    
    if companion.life_stage != old_stage:
        await db.commit()
        return companion.life_stage
    return None


def serialize_companion(companion: Companion) -> dict:
    """Serialize companion data for API response.
    
    CRITICAL: Excludes hidden_genetic_potential and latent_traits.
    These fields must NEVER be sent to the client.
    """
    care_state_data = {}
    if companion.care_state:
        care_state_data = {
            "hunger": companion.care_state.hunger,
            "energy": companion.care_state.energy,
            "morale": companion.care_state.morale,
            "cleanliness": companion.care_state.cleanliness,
        }
    
    return {
        "uuid": str(companion.uuid),
        "user_id": companion.user_id,
        "species": companion.species,
        "name": companion.name,
        "origin_type": companion.origin_type,
        "origin_metadata": companion.origin_metadata,
        "creation_timestamp": companion.creation_timestamp.isoformat(),
        "life_stage": companion.life_stage,
        "maturation_progress": companion.maturation_progress,
        "base_stats": companion.base_stats,
        "mutated_stats": companion.mutated_stats,
        # NOTE: hidden_genetic_potential is INTENTIONALLY EXCLUDED
        "color_regions": companion.color_regions,
        "seasonal_pattern": companion.seasonal_pattern,
        "personality_type": companion.personality_type,
        "personality_traits": companion.personality_traits,
        "behavioral_quirks": companion.behavioral_quirks,
        "bond_level": companion.bond_level,
        "care_streak": companion.care_streak,
        "parent_a_uuid": str(companion.parent_a_uuid) if companion.parent_a_uuid else None,
        "parent_b_uuid": str(companion.parent_b_uuid) if companion.parent_b_uuid else None,
        "generation": companion.generation,
        "current_state": companion.current_state,
        "health_status": companion.health_status,
        "breeding_cooldown_until": companion.breeding_cooldown_until.isoformat() if companion.breeding_cooldown_until else None,
        "on_chain_record": companion.on_chain_record,
        "care_state": care_state_data,
    }
