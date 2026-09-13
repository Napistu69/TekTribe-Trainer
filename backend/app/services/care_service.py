"""Care service — handles companion care actions with decay."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import CareState, Companion

# Care action effects
CARE_ACTIONS = {
    "feed": {"hunger": 0.4, "imprint": 2},
    "clean": {"cleanliness": 0.5, "imprint": 2},
    "reassure": {"morale": 0.3, "imprint": 3},
    "rest": {"energy": 0.25, "imprint": 1},
    "imprint": {"imprint": 10},
}

# Cooldowns (hours)
CARE_COOLDOWNS = {
    "imprint": 4,
    "rest": 6,
}

# Decay rates per hour
DECAY_RATES = {
    "hunger": -0.05,
    "energy": -0.03,
    "morale": -0.02,
    "cleanliness": -0.04,
}

# Imprint degradation when hunger = 0
IMPRINT_DEGRADE_RATE = -0.01  # per hour


async def get_care_state(db: AsyncSession, companion_uuid: str) -> Optional[CareState]:
    """Get care state with decay applied."""
    result = await db.execute(
        select(CareState).where(CareState.companion_uuid == companion_uuid)
    )
    care_state = result.scalar_one_or_none()
    if care_state:
        apply_decay(care_state)
    return care_state


async def perform_care_action(db: AsyncSession, user_id: str, companion_uuid: str, action: str) -> dict:
    """Perform a direct care action on a companion."""
    if action not in CARE_ACTIONS:
        return {"success": False, "error": f"Unknown action: {action}"}

    # Verify ownership
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

    now = datetime.now(timezone.utc)
    if not companion.origin_metadata:
        companion.origin_metadata = {}

    # Check cooldowns for timed actions
    cooldown_hours = CARE_COOLDOWNS.get(action)
    if cooldown_hours:
        last_key = f"_last_{action}_at"
        last_ts = companion.origin_metadata.get(last_key)
        if last_ts:
            last_dt = datetime.fromisoformat(last_ts)
            hours_since = (now - last_dt).total_seconds() / 3600
            if hours_since < cooldown_hours:
                remaining = cooldown_hours - hours_since
                return {"success": False, "error": f"{action} on cooldown. {remaining:.1f}h remaining"}

    # Apply effects
    effects = CARE_ACTIONS[action]
    imprint_given = effects.get("imprint", 0)

    if "hunger" in effects:
        care_state.hunger = min(1.0, care_state.hunger + effects["hunger"])
    if "cleanliness" in effects:
        care_state.cleanliness = min(1.0, care_state.cleanliness + effects["cleanliness"])
    if "morale" in effects:
        care_state.morale = min(1.0, care_state.morale + effects["morale"])
    if "energy" in effects:
        care_state.energy = min(1.0, care_state.energy + effects["energy"])

    if imprint_given > 0:
        companion.imprint_level = min(100, companion.imprint_level + imprint_given)
        companion.maturation_progress = min(1.0, companion.maturation_progress + 0.01)

    # Update cooldown timestamp
    if cooldown_hours:
        companion.origin_metadata[f"_last_{action}_at"] = now.isoformat()
        from sqlalchemy.orm import attributes
        attributes.flag_modified(companion, "origin_metadata")

    care_state.last_updated = now
    await db.commit()

    return {
        "success": True,
        "action": action,
        "imprint_given": imprint_given,
        "care_state": {
            "hunger": care_state.hunger,
            "energy": care_state.energy,
            "morale": care_state.morale,
            "cleanliness": care_state.cleanliness,
        },
        "imprint_level": companion.imprint_level,
        "maturation_progress": companion.maturation_progress,
    }


async def get_cooldowns(db: AsyncSession, companion_uuid: str) -> dict:
    """Get remaining cooldown hours for timed care actions."""
    result = await db.execute(
        select(Companion).where(Companion.uuid == companion_uuid)
    )
    companion = result.scalar_one_or_none()
    if not companion:
        return {}

    now = datetime.now(timezone.utc)
    meta = companion.origin_metadata or {}
    cooldowns = {}

    for action, hours in CARE_COOLDOWNS.items():
        last_ts = meta.get(f"_last_{action}_at")
        if last_ts:
            last_dt = datetime.fromisoformat(last_ts)
            elapsed = (now - last_dt).total_seconds() / 3600
            remaining = max(0.0, hours - elapsed)
            cooldowns[action] = round(remaining, 1)
        else:
            cooldowns[action] = 0.0

    return cooldowns


def apply_decay(care_state: CareState) -> None:
    """Apply time-based decay to care meters."""
    now = datetime.now(timezone.utc)
    time_diff = (now - care_state.last_updated).total_seconds() / 3600  # hours
    
    if time_diff <= 0:
        return
    
    care_state.hunger = max(0.0, min(1.0, care_state.hunger + DECAY_RATES["hunger"] * time_diff))
    care_state.energy = max(0.0, min(1.0, care_state.energy + DECAY_RATES["energy"] * time_diff))
    care_state.morale = max(0.0, min(1.0, care_state.morale + DECAY_RATES["morale"] * time_diff))
    care_state.cleanliness = max(0.0, min(1.0, care_state.cleanliness + DECAY_RATES["cleanliness"] * time_diff))
    
    # Imprint degrades if hunger is 0
    if care_state.hunger <= 0:
        care_state.imprint_quality = max(0.0, care_state.imprint_quality + IMPRINT_DEGRADE_RATE * time_diff)
    
    care_state.last_updated = now


async def apply_expedition_energy_drain(care_state: CareState, hours: float) -> None:
    """Drain energy after an expedition."""
    drain = 0.1 * hours  # 10% per hour of expedition
    care_state.energy = max(0.0, care_state.energy - drain)
