"""Companion entity — represents a player's hatched creature."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSONB, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# Species-to-rarity mapping (from roster_v0_2.json)
SPECIES_RARITY = {
    "parasaur": "common",
    "dilo": "common",
    "trike": "uncommon",
    "ptera": "uncommon",
    "raptor": "rare",
    "rex": "epic",
}

# Default rarity for unknown species
DEFAULT_RARITY = "common"


class Companion(Base):
    __tablename__ = "companions"

    uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    species: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(32), nullable=True)

    # Origin
    origin_type: Mapped[str] = mapped_column(String(20), default="hatched")
    origin_metadata: Mapped[dict] = mapped_column(JSONB, default={})
    creation_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Life stage
    life_stage: Mapped[str] = mapped_column(String(20), default="hatchling")
    maturation_progress: Mapped[float] = mapped_column(Float, default=0.0)

    # Stats (game-adjacent)
    base_stats: Mapped[dict] = mapped_column(JSONB, default={})
    mutated_stats: Mapped[dict] = mapped_column(JSONB, default={})

    # Hidden systems — SERVER-SIDE ONLY, NEVER SERIALIZED TO CLIENT
    hidden_genetic_potential: Mapped[float] = mapped_column(Float, default=0.0)

    # Color regions (5 independent mutation zones)
    color_regions: Mapped[dict] = mapped_column(JSONB, default={})
    seasonal_pattern: Mapped[str] = mapped_column(String(50), nullable=True)

    # Personality
    personality_type: Mapped[str] = mapped_column(String(50), nullable=True)
    personality_traits: Mapped[dict] = mapped_column(JSONB, default={})
    behavioral_quirks: Mapped[dict] = mapped_column(JSONB, default={})

    # Imprint (renamed from bond)
    imprint_level: Mapped[int] = mapped_column(Integer, default=0)
    care_streak: Mapped[int] = mapped_column(Integer, default=0)

    # Lineage
    parent_a_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companions.uuid"), nullable=True
    )
    parent_b_uuid: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companions.uuid"), nullable=True
    )
    generation: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    current_state: Mapped[str] = mapped_column(String(20), default="resting")
    health_status: Mapped[float] = mapped_column(Float, default=1.0)
    breeding_cooldown_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Blockchain (dormant until Phase 4)
    on_chain_record: Mapped[dict] = mapped_column(JSONB, nullable=True)

    # Relationships
    care_state: Mapped["CareState"] = relationship(
        "CareState", back_populates="companion", uselist=False
    )

    @property
    def rarity(self) -> str:
        """Get rarity based on species mapping."""
        return SPECIES_RARITY.get(self.species, DEFAULT_RARITY)

    @property
    def is_locked(self) -> bool:
        """Get lock status from origin_metadata."""
        return self.origin_metadata.get("_locked", False)

    @is_locked.setter
    def is_locked(self, value: bool):
        """Set lock status in origin_metadata."""
        if not self.origin_metadata:
            self.origin_metadata = {}
        self.origin_metadata["_locked"] = value
