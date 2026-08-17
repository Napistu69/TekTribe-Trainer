"""User model — accounts linked to Immutable Passport."""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    passport_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    lockdown_graduated: Mapped[bool] = mapped_column(Boolean, default=False)
    lockdown_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    care_action_count: Mapped[int] = mapped_column(Integer, default=0)
    egg_pull_count_today: Mapped[int] = mapped_column(Integer, default=0)
    last_egg_pull_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
