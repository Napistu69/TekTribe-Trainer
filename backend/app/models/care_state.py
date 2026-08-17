"""CareState model — tracks companion care meters with decay."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CareState(Base):
    __tablename__ = "care_states"

    companion_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companions.uuid"), primary_key=True
    )
    hunger: Mapped[float] = mapped_column(Float, default=1.0)
    energy: Mapped[float] = mapped_column(Float, default=1.0)
    morale: Mapped[float] = mapped_column(Float, default=1.0)
    cleanliness: Mapped[float] = mapped_column(Float, default=1.0)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
