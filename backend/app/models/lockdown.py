"""LockdownState model — tracks account lockdown for new players."""
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LockdownState(Base):
    __tablename__ = "lockdown_states"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), primary_key=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    graduated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    care_actions_completed: Mapped[int] = mapped_column(Integer, default=0)
    min_bond_achieved: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
