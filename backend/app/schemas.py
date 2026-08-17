"""Pydantic schemas for API requests and responses."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# === Auth Schemas ===

class LoginRequest(BaseModel):
    """Request body for POST /auth/login."""
    email: str
    passport_proof: str
    wallet_address: str


class AuthResponse(BaseModel):
    """Response body for POST /auth/login."""
    user_id: str
    session_token: str
    is_new_user: bool
    lockdown_state: dict


class UserResponse(BaseModel):
    """Public user data — never includes wallet_address."""
    id: str
    email: str
    created_at: datetime
    lockdown_graduated: bool
    lockdown_started_at: datetime
    care_action_count: int


# === Egg Schemas ===

class EggResponse(BaseModel):
    """Egg data for list endpoints. Species is hidden until hatch."""
    uuid: str
    rarity: str
    source: str
    pulled_at: datetime
    incubation_started_at: Optional[datetime] = None
    temperature: float
    stability: float


class EggDetailResponse(BaseModel):
    """Detailed egg data for single egg endpoint."""
    uuid: str
    rarity: str
    source: str
    pulled_at: datetime
    hatched: bool
    incubation_started_at: Optional[datetime] = None
    temperature: float
    stability: float


# === Companion Schemas ===

class CompanionResponse(BaseModel):
    """Companion data — NEVER includes hidden_genetic_potential."""
    uuid: str
    user_id: str
    species: str
    name: Optional[str] = None
    origin_type: str
    origin_metadata: dict
    creation_timestamp: str
    life_stage: str
    maturation_progress: float
    base_stats: dict
    mutated_stats: dict
    color_regions: dict
    seasonal_pattern: Optional[str] = None
    personality_type: str
    personality_traits: list
    behavioral_quirks: list
    bond_level: int
    care_streak: int
    parent_a_uuid: Optional[str] = None
    parent_b_uuid: Optional[str] = None
    generation: int
    current_state: str
    health_status: float
    breeding_cooldown_until: Optional[str] = None
    on_chain_record: Optional[dict] = None
