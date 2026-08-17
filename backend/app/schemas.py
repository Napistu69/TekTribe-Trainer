"""Pydantic schemas for authentication."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Request body for POST /auth/login."""
    email: str
    passport_proof: str  # From Immutable Passport SDK
    wallet_address: str  # Extracted from Passport — used internally only


class AuthResponse(BaseModel):
    """Response body for POST /auth/login."""
    user_id: str
    session_token: str
    is_new_user: bool
    lockdown_state: dict
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Public user data — never includes wallet_address."""
    id: str
    email: str
    created_at: datetime
    lockdown_graduated: bool
    lockdown_started_at: datetime
    care_action_count: int
    
    class Config:
        from_attributes = True
