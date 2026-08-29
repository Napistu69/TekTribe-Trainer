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


# === Companion Schemas ===

class CompanionResponse(BaseModel):
    """Companion data — NEVER includes hidden_genetic_potential."""
    uuid: str
    user_id: str
    species: str
    name: Optional[str] = None
    rarity: str
    diet: str
    biological_sex: str
    is_locked: bool
    origin_type: str
    origin_metadata: dict
    creation_timestamp: str
    life_stage: str
    display_life_stage: str
    maturation_progress: float
    base_stats: dict
    mutated_stats: dict
    color_regions: dict
    seasonal_pattern: Optional[str] = None
    personality_type: str
    personality_traits: list
    behavioral_quirks: list
    imprint_level: int
    care_streak: int
    parent_a_uuid: Optional[str] = None
    parent_b_uuid: Optional[str] = None
    generation: int
    current_state: str
    health_status: float
    breeding_cooldown_until: Optional[str] = None


class CompanionReleaseRequest(BaseModel):
    """Request body for POST /companions/{uuid}/release."""
    confirm: bool = False


class CompanionNameRequest(BaseModel):
    """Request body for PATCH /companions/{uuid}/name."""
    name: str = Field(..., min_length=1, max_length=32)


# === Egg Schemas ===

class EggResponse(BaseModel):
    """Egg data."""
    uuid: str
    user_id: str
    species: str
    rarity: str
    source: str
    pulled_at: str
    hatched: bool
    temperature: float
    stability: float


class EggDetailResponse(BaseModel):
    """Detailed egg data (for single egg endpoint)."""
    uuid: str
    rarity: str
    source: str
    pulled_at: str
    hatched: bool
    incubation_started_at: Optional[str] = None
    temperature: float
    stability: float


class EggHatchRequest(BaseModel):
    """Request body for POST /eggs/{uuid}/hatch."""
    pass


# === Care Schemas ===

class CareStateResponse(BaseModel):
    """Care state data."""
    companion_uuid: str
    hunger: float
    energy: float
    morale: float
    cleanliness: float
    last_fed: Optional[str] = None
    last_cleaned: Optional[str] = None
    last_imprint: Optional[str] = None
    last_rest: Optional[str] = None
    imprint_quality: int = 0


class CareActionRequest(BaseModel):
    """Request body for POST /care/{companion_uuid}/{action}."""
    action: str


class CareCooldownsResponse(BaseModel):
    """Response for GET /care/{companion_uuid}/cooldowns."""
    imprint_available: bool
    imprint_cooldown_remaining: int
    rest_available: bool
    rest_cooldown_remaining: int


# === Economy Schemas ===

class EconomyBalanceResponse(BaseModel):
    """Response body for GET /economy/balance."""
    dust: int
    shard: int
    cuboid: int
    ele: int


class EconomyHistoryResponse(BaseModel):
    """Response body for GET /economy/history."""
    transactions: list[dict]


class ShopItemResponse(BaseModel):
    """Shop item data."""
    item_id: str
    name: str
    description: str
    cost: int
    effect: dict
    category: str


class ShopPurchaseRequest(BaseModel):
    """Request body for POST /economy/shop/purchase."""
    item_id: str
    companion_uuid: str


# === Expedition Schemas ===

class ExpeditionDispatchRequest(BaseModel):
    """Request body for POST /expeditions/dispatch."""
    companion_uuids: list[str]  # 1-3 companion UUIDs
    biome_zone: str
    duration_hours: str  # "2h", "6h", "12h", "24h"


class ExpeditionResponse(BaseModel):
    """Response body for expedition endpoints."""
    uuid: str
    companion_uuids: list[str]
    biome_zone: str
    dispatched_at: datetime
    returns_at: datetime
    status: str
    risk_level: float
    result: dict | None = None


# === Forge Schemas ===

class ForgeOptionResponse(BaseModel):
    """Forge refinement option."""
    id: str
    input_currency: str
    input_amount: int
    output_currency: str
    output_amount: int


class ForgeRefineRequest(BaseModel):
    """Request body for POST /forge/refine."""
    refinement_type: str  # "dust_to_shard", "shard_to_cuboid", "cuboid_to_ele"
    times: int = Field(default=1, ge=1, le=100)


class ForgeRefineResponse(BaseModel):
    """Response body for POST /forge/refine."""
    success: bool
    refinement_type: str
    input_currency: str
    input_amount: int
    output_currency: str
    output_amount: int
    times: int
    new_balances: dict


# === Training Schemas ===

class TrainingSubmitRequest(BaseModel):
    """Request body for POST /training/submit."""
    companion_uuid: str
    game_id: str
    score: int = Field(..., ge=0, le=100)
    duration_seconds: int = Field(..., ge=0, le=3600)


class TrainingResultResponse(BaseModel):
    """Response body for POST /training/submit."""
    success: bool
    companion_uuid: str
    game_id: str
    stat_gains: dict
    dust_gained: int
    cooldown_until: Optional[str] = None
