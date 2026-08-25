"""Care service — handles companion care actions with decay and cooldowns."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import CareState, Companion, ImprintEvent

# Care action definitions
CARE_ACTIONS = {
    "feed": {"hunger": 0.4, "imprint": 2, "cooldown_hours": 2},
    "clean": {"cleanliness": 0.5, "imprint": 1, "cooldown_hours": 4},
    "imprint": {"morale": 0.3, "imprint": 3, "cooldown_hours": 3},
    "rest": {"energy": 0.5, "imprint": 1, "cooldown_hours": 2},
    "observe": {"imprint": 1, "cooldown_hours": 1},
}

# Decay rates per hour
DECAY_RATES = {
    "hunger": -0.05,
    "energy": -0.03,
    "morale": -0.02,
    "cleanliness": -0.04,
}

# Imprint gain diminishing returns curve
def _diminishing_imprint_gain(base_gain: int, current_imprint: int) -> int:
    """Apply diminishing returns to imprint gains at higher levels."""
    if current_imprint < 10:
        return base_gain
    elif current_imprint < 50:
        return max(1, int(base_gain * 0.75))
    elif current_imprint < 80:
        return max(1, int(base_gain * 0.5))
    else:
        return max(1, int(base_gain * 0.25))


async def get_care_state(db: AsyncSession, companion_uuid: str) -> Optional[CareState]:
    """Get care state with decay applied."""
    result = await db.execute(
        select(CareState).where(CareState.companion_uuid == companion_uuid)
    )
    care_state = result.scalar_one_or_none()
    if care_state:
        apply_decay(care_state)
    return care_state


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
    care_state.last_updated = now


async def perform_care_action(
    db: AsyncSession,
    user_id: str,
    companion_uuid: str,
    action_type: str,
) -> dict:
    """Perform a care action on a companion.
    
    Returns result dict with action outcome.
    """
    if action_type not in CARE_ACTIONS:
        raise ValueError(f"Unknown care action: {action_type}")
    
    # Verify companion ownership
    result = await db.execute(
        select(Companion).where(
            Companion.uuid == companion_uuid,
            Companion.user_id == user_id
        )
    )
    companion = result.scalar_one_or_none()
    if not companion:
        raise ValueError("Companion not found")
    
    # Get care state
    care_state = await get_care_state(db, companion_uuid)
    if not care_state:
        raise ValueError("Care state not found")
    
    # Check cooldown
    cooldown_key = f"cooldown:{action_type}"
    cooldown_until = await _get_cooldown(db, companion_uuid, cooldown_key)
    if cooldown_until and datetime.now(timezone.utc) < cooldown_until:
        remaining = (cooldown_until - datetime.now(timezone.utc)).total_seconds()
        return {
            "success": False,
            "error": "cooldown",
            "cooldown_remaining_seconds": int(remaining),
        }
    
    # Apply action
    action = CARE_ACTIONS[action_type]
    
    if "hunger" in action:
        care_state.hunger = min(1.0, care_state.hunger + action["hunger"])
    if "energy" in action:
        care_state.energy = min(1.0, care_state.energy + action["energy"])
    if "morale" in action:
        care_state.morale = min(1.0, care_state.morale + action["morale"])
    if "cleanliness" in action:
        care_state.cleanliness = min(1.0, care_state.cleanliness + action["cleanliness"])
    
    # Apply imprint gain with diminishing returns
    base_imprint = action["imprint"]
    imprint_gain = _diminishing_imprint_gain(base_imprint, companion.imprint_level)
    companion.imprint_level += imprint_gain
    
    # Set cooldown
    await _set_cooldown(db, companion_uuid, cooldown_key, action["cooldown_hours"])
    
    # Log imprint event
    imprint_event = ImprintEvent(
        companion_uuid=companion_uuid,
        event_type=f"care_{action_type}",
        imprint_delta=imprint_gain,
        description=f"Performed {action_type}: +{imprint_gain} imprint",
    )
    db.add(imprint_event)
    
    # Update care streak (first action of UTC day)
    await _update_care_streak(db, companion)
    
    await db.commit()
    
    return {
        "success": True,
        "action": action_type,
        "imprint_gained": imprint_gain,
        "care_state": {
            "hunger": care_state.hunger,
            "energy": care_state.energy,
            "morale": care_state.morale,
            "cleanliness": care_state.cleanliness,
        },
    }


async def _get_cooldown(db: AsyncSession, companion_uuid: str, action_key: str) -> Optional[datetime]:
    """Get cooldown expiration for an action."""
    # Store cooldowns in a simple table or Redis — using a JSON field on CareState for simplicity
    # For now, use Redis
    import redis.asyncio as redis
    from app.core.config import settings
    
    r = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    key = f"care_cooldown:{companion_uuid}:{action_key}"
    value = await r.get(key)
    if value:
        return datetime.fromisoformat(value)
    return None


async def _set_cooldown(db: AsyncSession, companion_uuid: str, action_key: str, hours: int) -> None:
    """Set cooldown for an action."""
    import redis.asyncio as redis
    from app.core.config import settings
    
    r = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    key = f"care_cooldown:{companion_uuid}:{action_key}"
    expires_at = datetime.now(timezone.utc) + timedelta(hours=hours)
    await r.setex(key, int(hours * 3600), expires_at.isoformat())


async def _update_care_streak(db: AsyncSession, companion: Companion) -> None:
    """Update care streak if this is the first action of a new UTC day."""
    # Simplified — in production, track last care date per companion
    pass


async def get_cooldowns(db: AsyncSession, companion_uuid: str) -> dict:
    """Get all cooldowns for a companion."""
    import redis.asyncio as redis
    from app.core.config import settings
    
    r = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    cooldowns = {}
    
    for action_name, action_def in CARE_ACTIONS.items():
        key = f"care_cooldown:{companion_uuid}:cooldown:{action_name}"
        value = await r.get(key)
        if value:
            expires = datetime.fromisoformat(value)
            remaining = (expires - datetime.now(timezone.utc)).total_seconds()
            if remaining > 0:
                cooldowns[action_name] = {
                    "remaining_seconds": int(remaining),
                    "total_seconds": action_def["cooldown_hours"] * 3600,
                }
    
    return cooldowns
