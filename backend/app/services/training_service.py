"""Training service — validates mini-game results and applies stat gains."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import Companion, ImprintEvent

# Mini-game definitions (mirrors frontend)
MINI_GAMES = {
    "target_tap": {"name": "Target Tap", "species": "dilo", "stats": ["focus", "trick_skill"]},
    "rhythm_graze": {"name": "Rhythm Graze", "species": "parasaur", "stats": ["trust", "affection"]},
    "sprint_course": {"name": "Sprint Course", "species": "raptor", "stats": ["speed", "drive"]},
    "sky_glide": {"name": "Sky Glide", "species": "ptera", "stats": ["agility", "curiosity"]},
    "charge_line": {"name": "Charge Line", "species": "trike", "stats": ["grit", "defense"]},
    "alpha_resolve": {"name": "Alpha Resolve", "species": "rex", "stats": ["power", "discipline"]},
}

# Juvenile+ games (available to all species at juvenile stage)
GENERAL_MINI_GAMES = {
    "chase_drills": {"name": "Chase Drills", "species": "any", "stats": ["speed"]},
    "balance_crossing": {"name": "Balance Crossing", "species": "any", "stats": ["temperament", "awareness"]},
    "roar_timing": {"name": "Roar Timing", "species": "any", "stats": ["strength", "morale"]},
}

COOLDOWN_HOURS = 1


async def validate_score(game_id: str, score: float, duration: float) -> tuple[bool, Optional[str]]:
    """Validate a mini-game submission.
    
    Returns (valid, error_message).
    """
    if game_id not in MINI_GAMES and game_id not in GENERAL_MINI_GAMES:
        return False, f"Unknown mini-game: {game_id}"
    
    if score < 0 or score > 100:
        return False, "Score must be between 0 and 100"
    
    if duration < 5 or duration > 300:
        return False, "Duration must be between 5 and 300 seconds"
    
    return True, None


def calculate_stat_gains(game_id: str, score: float) -> dict:
    """Calculate stat gains based on score.
    
    Score 0-100 maps to multipliers:
    - 0: 0.2x
    - 50: 1.0x
    - 100: 1.5x
    """
    # Linear interpolation: 0.2 at 0, 1.0 at 50, 1.5 at 100
    if score <= 50:
        multiplier = 0.2 + (score / 50) * 0.8
    else:
        multiplier = 1.0 + ((score - 50) / 50) * 0.5
    
    # Base gain per stat
    base_gain = 2
    
    game = MINI_GAMES.get(game_id) or GENERAL_MINI_GAMES.get(game_id)
    if not game:
        return {}
    
    return {stat: round(base_gain * multiplier, 1) for stat in game["stats"]}


def calculate_imprint_gain(score: float) -> int:
    """Calculate imprint gain from score."""
    if score >= 80:
        return 5
    elif score >= 50:
        return 3
    elif score >= 20:
        return 1
    return 0


def calculate_dust_reward(score: float) -> int:
    """Calculate Dust reward for high scores."""
    if score >= 90:
        return 5
    elif score >= 80:
        return 3
    elif score >= 70:
        return 1
    return 0


async def check_cooldown(db: AsyncSession, companion_uuid: str, game_id: str) -> tuple[bool, Optional[int]]:
    """Check if a mini-game is on cooldown.
    
    Returns (can_play, remaining_seconds).
    """
    import redis.asyncio as redis
    from app.core.config import settings
    
    r = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    key = f"training_cooldown:{companion_uuid}:{game_id}"
    value = await r.get(key)
    
    if value:
        expires = datetime.fromisoformat(value)
        remaining = (expires - datetime.now(timezone.utc)).total_seconds()
        if remaining > 0:
            return False, int(remaining)
    
    return True, None


async def apply_training(
    db: AsyncSession,
    user_id: str,
    companion_uuid: str,
    game_id: str,
    score: float,
    duration: float,
) -> dict:
    """Apply training results to a companion.
    
    Returns result dict with gains and rewards.
    """
    # Validate
    valid, error = await validate_score(game_id, score, duration)
    if not valid:
        raise ValueError(error)
    
    # Check cooldown
    can_play, remaining = await check_cooldown(db, companion_uuid, game_id)
    if not can_play:
        raise ValueError(f"Training on cooldown. Try again in {remaining} seconds")
    
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
    
    # Calculate gains
    stat_gains = calculate_stat_gains(game_id, score)
    imprint_gain = calculate_imprint_gain(score)
    dust_reward = calculate_dust_reward(score)
    
    # Apply stat gains to mutated_stats
    if not companion.mutated_stats:
        companion.mutated_stats = {}
    
    for stat, gain in stat_gains.items():
        current = companion.mutated_stats.get(stat, 0)
        companion.mutated_stats[stat] = current + gain
    
    # Apply imprint gain
    companion.imprint_level += imprint_gain
    
    # Set cooldown
    import redis.asyncio as redis
    from app.core.config import settings
    
    r = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    key = f"training_cooldown:{companion_uuid}:{game_id}"
    expires_at = datetime.now(timezone.utc) + timedelta(hours=COOLDOWN_HOURS)
    await r.setex(key, COOLDOWN_HOURS * 3600, expires_at.isoformat())
    
    # Log imprint event
    if imprint_gain > 0:
        imprint_event = ImprintEvent(
            companion_uuid=companion_uuid,
            event_type=f"training_{game_id}",
            imprint_delta=imprint_gain,
            description=f"Training {game_id}: +{imprint_gain} imprint, score={score:.0f}",
        )
        db.add(imprint_event)
    
    # Award Dust if applicable
    if dust_reward > 0:
        from app.services.currency_service import award_dust
        await award_dust(user_id, dust_reward, f"training_{game_id}")
    
    await db.commit()
    
    return {
        "score": score,
        "stat_gains": stat_gains,
        "imprint_gained": imprint_gain,
        "dust_earned": dust_reward,
    }


async def get_available_games(db: AsyncSession, user_id: str, companion_uuid: str) -> list[dict]:
    """Get available mini-games for a companion.
    
    Filters by species and life stage, checks cooldowns.
    """
    # Get companion
    result = await db.execute(
        select(Companion).where(
            Companion.uuid == companion_uuid,
            Companion.user_id == user_id
        )
    )
    companion = result.scalar_one_or_none()
    if not companion:
        raise ValueError("Companion not found")
    
    available = []
    
    # Species-specific games
    for game_id, game in MINI_GAMES.items():
        if game["species"] == companion.species:
            can_play, remaining = await check_cooldown(db, companion_uuid, game_id)
            available.append({
                "id": game_id,
                "name": game["name"],
                "stats": game["stats"],
                "cooldown_remaining": remaining,
                "available": can_play,
            })
    
    # General games (juvenile+)
    if companion.life_stage in ["juvenile", "adult", "elder"]:
        for game_id, game in GENERAL_MINI_GAMES.items():
            can_play, remaining = await check_cooldown(db, companion_uuid, game_id)
            available.append({
                "id": game_id,
                "name": game["name"],
                "stats": game["stats"],
                "cooldown_remaining": remaining,
                "available": can_play,
            })
    
    return available
