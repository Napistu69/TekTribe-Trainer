"""Companion model — the core creature entity.

NOTE: rarity and is_locked are COMPUTED PROPERTIES, not database columns.
rarity is derived from species, and is_locked is stored in origin_metadata.
"""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

# Species-to-rarity mapping (from roster_v0_2.json)
SPECIES_RARITY = {
    "parasaur": "common",
    "dilo": "common",
    "trike": "uncommon",
    "ptera": "uncommon",
    "raptor": "rare",
    "rex": "epic",
}
DEFAULT_RARITY = "common"

# Species diet mapping
SPECIES_DIET = {
    "parasaur": "herbivore",
    "dilo": "carnivore",
    "trike": "herbivore",
    "ptera": "carnivore",
    "raptor": "carnivore",
    "rex": "carnivore",
}
DEFAULT_DIET = "omnivore"


class Companion(Base):
    __tablename__ = "companions"

    uuid: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    species: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(32), nullable=True)

    # Origin
    origin_type: Mapped[str] = mapped_column(String(20), default="hatched")
    origin_metadata: Mapped[dict] = mapped_column(JSONB, default={})
    creation_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Life stage
    life_stage: Mapped[str] = mapped_column(String(20), default="baby")
    maturation_progress: Mapped[float] = mapped_column(Float, default=0.0)

    # Stats
    base_stats: Mapped[dict] = mapped_column(JSONB, default={})
    mutated_stats: Mapped[dict] = mapped_column(JSONB, default={})

    # Hidden (server-side only)
    hidden_genetic_potential: Mapped[float] = mapped_column(Float, default=0.0)

    # Color regions
    color_regions: Mapped[dict] = mapped_column(JSONB, default={})
    seasonal_pattern: Mapped[str] = mapped_column(String(50), nullable=True)

    # Personality
    personality_type: Mapped[str] = mapped_column(String(50), default="neutral")
    personality_traits: Mapped[list] = mapped_column(JSONB, default=[])
    behavioral_quirks: Mapped[list] = mapped_column(JSONB, default=[])

    # Imprint
    imprint_level: Mapped[int] = mapped_column(Integer, default=0)
    care_streak: Mapped[int] = mapped_column(Integer, default=0)

    # Lineage
    parent_a_uuid: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("companions.uuid"), nullable=True)
    parent_b_uuid: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("companions.uuid"), nullable=True)
    generation: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    current_state: Mapped[str] = mapped_column(String(20), default="resting")
    health_status: Mapped[float] = mapped_column(Float, default=1.0)
    breeding_cooldown_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Blockchain
    on_chain_record: Mapped[dict] = mapped_column(JSONB, nullable=True)

    # Relationships
    care_state: Mapped["CareState"] = relationship("CareState", back_populates="companion", uselist=False)

    @property
    def rarity(self) -> str:
        """Computed rarity based on species. NOT a database column."""
        return SPECIES_RARITY.get(self.species, DEFAULT_RARITY)

    @rarity.setter
    def rarity(self, value):
        """Allow setting rarity (stored in origin_metadata for compatibility)."""
        pass  # rarity is computed from species, setter is a no-op

    @property
    def diet(self) -> str:
        """Computed diet based on species. NOT a database column."""
        return SPECIES_DIET.get(self.species, DEFAULT_DIET)

    @property
    def display_life_stage(self) -> str:
        """Life stage for display on card. Adult (100%) shows no tag."""
        if self.maturation_progress >= 1.0:
            return "adult"
        return self.life_stage

    @property
    def biological_sex(self) -> str:
        """Biological sex stored in origin_metadata. NOT a database column."""
        if not self.origin_metadata:
            return "unknown"
        return self.origin_metadata.get("_biological_sex", "unknown")

    @property
    def is_locked(self) -> bool:
        """Lock status stored in origin_metadata. NOT a database column."""
        if not self.origin_metadata:
            return False
        return self.origin_metadata.get("_locked", False)

    @is_locked.setter
    def is_locked(self, value: bool):
        """Set lock status in origin_metadata."""
        if not self.origin_metadata:
            self.origin_metadata = {}
        self.origin_metadata["_locked"] = value
        # Mark the field as modified so SQLAlchemy detects the change
        from sqlalchemy.orm import attributes
        attributes.flag_modified(self, "origin_metadata")
