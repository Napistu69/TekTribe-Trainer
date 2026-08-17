"""Egg model — incubating eggs waiting to hatch."""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Egg(Base):
    __tablename__ = "eggs"

    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    species: Mapped[str] = mapped_column(String(50), nullable=True)  # Hidden until hatch
    rarity: Mapped[str] = mapped_column(String(20), nullable=False)
    source: Mapped[str] = mapped_column(String(30), default="starter")
    pulled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    hatched: Mapped[bool] = mapped_column(Boolean, default=False)
    hatched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    hatched_companion_uuid: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=True)
    incubation_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    temperature: Mapped[float] = mapped_column(Float, default=0.5)
    stability: Mapped[float] = mapped_column(Float, default=0.5)
