"""Dialogue service — manages Overseer dialogue trees and player progress."""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.core.database import AsyncSessionLocal

# Load dialogue data
DIALOGUE_PATH = Path(__file__).parent.parent / "data" / "dialogue_trees.json"
with open(DIALOGUE_PATH) as f:
    DIALOGUE_TREES = json.load(f)


async def get_dialogue(user_id: str, trigger_id: str) -> Optional[dict]:
    """Get dialogue tree for a trigger."""
    if trigger_id not in DIALOGUE_TREES:
        return None
    
    # Check if already seen (except daily)
    if trigger_id != "daily_greeting":
        seen = await _check_dialogue_seen(user_id, trigger_id)
        if seen:
            return None
    
    return DIALOGUE_TREES[trigger_id]


async def log_dialogue_seen(user_id: str, trigger_id: str) -> None:
    """Record that a player has seen a dialogue."""
    import redis.asyncio as redis
    from app.core.config import settings
    
    r = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    key = f"dialogue_seen:{user_id}:{trigger_id}"
    await r.set(key, datetime.now(timezone.utc).isoformat())


async def _check_dialogue_seen(user_id: str, trigger_id: str) -> bool:
    """Check if a player has seen a dialogue."""
    import redis.asyncio as redis
    from app.core.config import settings
    
    r = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    key = f"dialogue_seen:{user_id}:{trigger_id}"
    return await r.exists(key) > 0


async def get_daily_greeting(user_id: str) -> dict:
    """Get contextual daily greeting based on player state."""
    # Base greeting
    greeting = DIALOGUE_TREES.get("daily_greeting", {})
    
    # Add context based on day of week
    day_of_week = datetime.now(timezone.utc).strftime("%A")
    
    # Get companion count
    from sqlalchemy import select
    from app.models import Companion
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Companion).where(Companion.user_id == user_id)
        )
        companions = result.scalars().all()
    
    companion_count = len(companions)
    
    # Modify greeting based on state
    if companion_count == 0:
        text = "The Tribe awaits your first companion. An egg will find you when the time is right."
    else:
        text = f"The Tribe greets you on this {day_of_week}. Your {companion_count} companion{'s' if companion_count != 1 else ''} remember your care."
    
    return {
        "id": "daily_greeting",
        "nodes": [{
            "id": "daily_context",
            "speaker": "Overseer",
            "text": text,
            "choices": [{"text": "Thank you, Overseer.", "next": None}]
        }]
    }
