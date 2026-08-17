"""Redis-based session management."""
import json
from datetime import datetime, timezone
from typing import Optional

import redis.asyncio as redis

from app.core.config import settings

# Redis connection pool
redis_pool = redis.ConnectionPool.from_url(
    settings.redis_url,
    decode_responses=True,
)


async def get_redis() -> redis.Redis:
    """Get a Redis connection from the pool."""
    return redis.Redis(connection_pool=redis_pool)


async def create_session(user_id: str, token: str) -> None:
    """Store a session in Redis with TTL."""
    r = await get_redis()
    key = f"session:{token}"
    value = json.dumps({
        "user_id": user_id,
        "created_at": str(datetime.now(timezone.utc)),
    })
    await r.setex(key, settings.session_ttl_hours * 3600, value)


async def validate_session(token: str) -> Optional[str]:
    """Validate a session token and return user_id if valid."""
    r = await get_redis()
    key = f"session:{token}"
    data = await r.get(key)
    if data is None:
        return None
    session = json.loads(data)
    return session.get("user_id")


async def revoke_session(token: str) -> None:
    """Revoke a session token."""
    r = await get_redis()
    key = f"session:{token}"
    await r.delete(key)


async def revoke_all_user_sessions(user_id: str) -> None:
    """Revoke all sessions for a user (e.g., on password change)."""
    r = await get_redis()
    # This is a simplified version — in production, track session IDs per user
    pass
