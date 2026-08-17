"""Security utilities for JWT token generation and validation."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"


def create_session_token(user_id: str) -> str:
    """Create a JWT session token for a user."""
    expires = datetime.now(timezone.utc) + timedelta(hours=settings.session_ttl_hours)
    payload = {
        "sub": user_id,
        "exp": expires,
        "iat": datetime.now(timezone.utc),
        "type": "session",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def verify_session_token(token: str) -> Optional[str]:
    """Verify a JWT session token and return the user_id if valid."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != "session":
            return None
        return payload.get("sub")
    except JWTError:
        return None
