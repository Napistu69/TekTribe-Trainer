"""Expedition model — dispatched and completed expeditions."""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Expedition(Base):
    __tablename__ = "expeditions"

    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    companion_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companions.uuid"), nullable=False
    )
    biome_zone: Mapped[str] = mapped_column(String(50), nullable=False)
    dispatched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    returns_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="dispatched")
    result: Mapped[dict] = mapped_column(JSONB, nullable=True)
    risk_level: Mapped[float] = mapped_column(Float, default=0.5)
    loadout: Mapped[dict] = mapped_column(JSONB, default={})
