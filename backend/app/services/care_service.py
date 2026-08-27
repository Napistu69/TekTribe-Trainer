"""Care service — handles companion care actions with decay."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import CareState, Companion

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
