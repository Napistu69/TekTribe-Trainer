"""Egg pull engine — server-side weighted random with pity and lockdown."""
import json
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Egg

# Load roster data
ROSTER_PATH = Path(__file__).parent.parent / "data" / "roster_v0_2.json"
with open(ROSTER_PATH) as f:
    ROSTER = json.load(f)

CREATURES = ROSTER["creatures"]
RARITY_ORDER = ["common", "uncommon", "rare", "epic", "legendary"]
PITY_THRESHOLD = ROSTER["pity_threshold"]
PITY_MIN_RARITY = ROSTER["pity_minimum_rarity"]
LOCKDOWN_MAX_EGGS = ROSTER["lockdown_max_eggs"]
LOCKDOWN_DAILY_LIMIT = ROSTER["lockdown_daily_limit"]

# Rarity pull rates for hatchery (Common → Legendary, no Ascendant/Mythic yet)
# Rates: Common 50%, Uncommon 35%, Rare 10%, Epic 4%, Legendary 1%
RARITY_PULL_RATES = {
    "common": 50,
    "uncommon": 35,
    "rare": 10,
    "epic": 4,
    "legendary": 1,
}

TOTAL_RARITY_WEIGHT = int(sum(RARITY_PULL_RATES.values()))  # 100


def _get_pity_min_index() -> int:
    """Get the index of the minimum rarity that counts as a 'pity success'."""
    return RARITY_ORDER.index(PITY_MIN_RARITY)


def _is_rarity_at_least(rarity: str, minimum: str) -> bool:
    """Check if rarity is >= minimum in the rarity hierarchy."""
    return RARITY_ORDER.index(rarity) >= RARITY_ORDER.index(minimum)


def _roll_rarity() -> str:
    """Roll for egg rarity based on pull rates."""
    rand = secrets.randbelow(TOTAL_RARITY_WEIGHT)
    cumulative = 0
    for rarity in RARITY_ORDER:
        cumulative += RARITY_PULL_RATES[rarity]
        if rand < cumulative:
            return rarity
    return RARITY_ORDER[-1]  # Fallback


def _select_creature_from_rarity(rarity: str) -> dict:
    """Select a random creature from a given rarity pool."""
    pool = [c for c in CREATURES if c["rarity"] == rarity]
    if not pool:
        pool = CREATURES
    return secrets.choice(pool)


async def _count_user_pulls(db: AsyncSession, user_id: str) -> int:
    """Count total eggs pulled by user (for pity tracking)."""
    result = await db.execute(
        select(Egg).where(Egg.user_id == user_id)
    )
    return len(result.scalars().all())


async def _count_pulls_since_rare(db: AsyncSession, user_id: str) -> int:
    """Count pulls since last Rare+ (for pity counter)."""
    result = await db.execute(
        select(Egg).where(Egg.user_id == user_id).order_by(Egg.pulled_at.desc())
    )
    eggs = result.scalars().all()

    count = 0
    for egg in eggs:
        creature = next((c for c in CREATURES if c["creature_id"] == egg.species), None)
        if creature and _is_rarity_at_least(creature["rarity"], PITY_MIN_RARITY):
            break
        count += 1
    return count


async def _count_eggs_today(db: AsyncSession, user_id: str) -> int:
    """Count eggs pulled today (UTC)."""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(Egg).where(
            Egg.user_id == user_id,
            Egg.pulled_at >= today_start
        )
    )
    return len(result.scalars().all())


async def can_pull(db: AsyncSession, user_id: str) -> tuple[bool, Optional[str]]:
    """Check if user can pull an egg. Returns (allowed, reason)."""
    from app.services.lockdown_service import can_perform
    if not await can_perform(user_id, "egg_pull"):
        return False, "Lockdown egg limit reached (max 3 during lockdown, 1 per day)"

    return True, None


async def pull_egg(db: AsyncSession, user_id: str, source: str = "starter") -> Egg:
    """Pull a new egg. Server-side RNG determines rarity then species.

    Rarity rates: Common 50%, Uncommon 35%, Rare 10%, Epic 4%, Legendary 1%
    Pity rule: guaranteed Rare+ within 10 pulls.
    """
    # Check pity counter
    pulls_since_rare = await _count_pulls_since_rare(db, user_id)

    if pulls_since_rare >= PITY_THRESHOLD - 1:
        # Pity triggered — guarantee Rare+
        pity_rarities = [r for r in RARITY_ORDER if _is_rarity_at_least(r, PITY_MIN_RARITY)]
        weights = [RARITY_PULL_RATES[r] for r in pity_rarities]
        total = int(sum(weights))
        rand = secrets.randbelow(total)
        cumulative = 0
        selected_rarity = pity_rarities[-1]
        for i, w in enumerate(weights):
            cumulative += w
            if rand < cumulative:
                selected_rarity = pity_rarities[i]
                break
    else:
        # Normal pull — roll rarity
        selected_rarity = _roll_rarity()

    # Select random creature from rarity pool
    selected = _select_creature_from_rarity(selected_rarity)

    # Create egg
    egg = Egg(
        user_id=user_id,
        species=selected["creature_id"],
        rarity=selected["rarity"],
        source=source,
        pulled_at=datetime.now(timezone.utc),
        hatched=False,
        temperature=0.5,
        stability=0.5,
    )
    db.add(egg)
    await db.commit()
    await db.refresh(egg)
    return egg


async def pull_starter_egg(db: AsyncSession, user_id: str) -> Egg:
    """Pull the starter egg for a new account."""
    return await pull_egg(db, user_id, source="starter")


async def release_egg(db: AsyncSession, user_id: str, egg_uuid: str) -> Optional[int]:
    """Release a duplicate egg for Element Shards."""
    result = await db.execute(
        select(Egg).where(Egg.user_id == user_id, Egg.uuid == egg_uuid)
    )
    egg = result.scalar_one_or_none()
    if not egg or egg.hatched:
        return None

    creature = next((c for c in CREATURES if c["creature_id"] == egg.species), None)
    if not creature:
        return None

    shards = creature["duplicate_yield_shards"]

    await db.delete(egg)

    from app.services.currency_service import award_shards
    await award_shards(user_id, shards, "release")

    await db.commit()
    return shards
