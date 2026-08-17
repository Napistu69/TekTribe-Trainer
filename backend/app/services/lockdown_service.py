"""Lockdown service — enforces account lockdown for new players."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models import LockdownState, User, Companion

# Configurable thresholds
LOCKDOWN_MIN_BOND = settings.lockdown_min_bond  # 100
LOCKDOWN_MIN_CARE_ACTIONS = settings.lockdown_min_care_actions  # 50
LOCKDOWN_MIN_DAYS = settings.lockdown_min_days  # 7
LOCKDOWN_MAX_EGGS = 3
LOCKDOWN_DAILY_LIMIT = 1


async def is_in_lockdown(user_id: str) -> bool:
    """Check if a user is in lockdown."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(LockdownState).where(LockdownState.user_id == user_id)
        )
        state = result.scalar_one_or_none()
        
        if not state:
            return False
        
        if not state.is_active:
            return False
        
        # Check minimum days
        days_elapsed = (datetime.now(timezone.utc) - state.started_at).days
        if days_elapsed < LOCKDOWN_MIN_DAYS:
            return True
        
        # Check graduation criteria
        if await _check_graduation_criteria(session, user_id):
            await _graduate(user_id)
            return False
        
        return True


async def check_graduation(user_id: str) -> bool:
    """Check and process graduation for a user."""
    async with AsyncSessionLocal() as session:
        if await _check_graduation_criteria(session, user_id):
            await _graduate(user_id)
            return True
        return False


async def _check_graduation_criteria(session: AsyncSession, user_id: str) -> bool:
    """Check if user meets graduation criteria."""
    # Get user
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return False
    
    # Check minimum days
    result = await session.execute(
        select(LockdownState).where(LockdownState.user_id == user_id)
    )
    state = result.scalar_one_or_none()
    if not state:
        return False
    
    days_elapsed = (datetime.now(timezone.utc) - state.started_at).days
    if days_elapsed < LOCKDOWN_MIN_DAYS:
        return False
    
    # Check bond level
    result = await session.execute(
        select(Companion).where(Companion.user_id == user_id)
    )
    companions = result.scalars().all()
    
    max_bond = max((c.bond_level for c in companions), default=0)
    if max_bond < LOCKDOWN_MIN_BOND:
        return False
    
    # Check care actions
    if user.care_action_count < LOCKDOWN_MIN_CARE_ACTIONS:
        return False
    
    return True


async def _graduate(user_id: str) -> None:
    """Graduate a user from lockdown."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(LockdownState).where(LockdownState.user_id == user_id)
        )
        state = result.scalar_one_or_none()
        
        if state:
            state.is_active = False
            state.graduated_at = datetime.now(timezone.utc)
            await session.commit()


async def can_perform(user_id: str, action: str) -> bool:
    """Check if a user can perform an action during lockdown."""
    lockdown = await is_in_lockdown(user_id)
    if not lockdown:
        return True
    
    # Actions blocked during lockdown
    blocked_actions = ["trade", "breed", "stud_list", "tribe_contribute"]
    
    if action in blocked_actions:
        return False
    
    # Egg pull has limits
    if action == "egg_pull":
        return await _can_pull_egg(user_id)
    
    return True


async def _can_pull_egg(user_id: str) -> bool:
    """Check if user can pull an egg during lockdown."""
    async with AsyncSessionLocal() as session:
        # Count total eggs
        from app.models import Egg
        result = await session.execute(
            select(Egg).where(Egg.user_id == user_id)
        )
        total_eggs = len(result.scalars().all())
        
        if total_eggs >= LOCKDOWN_MAX_EGGS:
            return False
        
        # Count today's eggs
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        result = await session.execute(
            select(Egg).where(
                Egg.user_id == user_id,
                Egg.pulled_at >= today_start
            )
        )
        eggs_today = len(result.scalars().all())
        
        if eggs_today >= LOCKDOWN_DAILY_LIMIT:
            return False
        
        return True


async def get_lockdown_status(user_id: str) -> dict:
    """Get lockdown status for a user."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(LockdownState).where(LockdownState.user_id == user_id)
        )
        state = result.scalar_one_or_none()
        
        if not state:
            return {
                "is_active": False,
                "days_elapsed": 0,
                "care_actions_remaining": 0,
                "bond_level_required": LOCKDOWN_MIN_BOND,
                "egg_pulls_used": 0,
                "egg_pulls_max": LOCKDOWN_MAX_EGGS,
            }
        
        days_elapsed = (datetime.now(timezone.utc) - state.started_at).days
        
        # Get user
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        # Count eggs
        from app.models import Egg
        result = await session.execute(
            select(Egg).where(Egg.user_id == user_id)
        )
        egg_pulls_used = len(result.scalars().all())
        
        # Get max bond
        result = await session.execute(
            select(Companion).where(Companion.user_id == user_id)
        )
        companions = result.scalars().all()
        max_bond = max((c.bond_level for c in companions), default=0)
        
        return {
            "is_active": state.is_active,
            "days_elapsed": days_elapsed,
            "care_actions_remaining": max(0, LOCKDOWN_MIN_CARE_ACTIONS - (user.care_action_count if user else 0)),
            "bond_level_required": LOCKDOWN_MIN_BOND,
            "current_bond": max_bond,
            "egg_pulls_used": egg_pulls_used,
            "egg_pulls_max": LOCKDOWN_MAX_EGGS,
        }
