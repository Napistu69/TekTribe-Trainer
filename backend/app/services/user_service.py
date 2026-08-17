"""User service — handles user creation and retrieval."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CurrencyLedger, LockdownState, User
from app.core.database import AsyncSessionLocal


async def get_user_by_id(user_id: str) -> Optional[User]:
    """Fetch a user by ID."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()


async def get_user_by_email(email: str) -> Optional[User]:
    """Fetch a user by email."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()


async def get_user_by_passport_id(passport_id: str) -> Optional[User]:
    """Fetch a user by Immutable Passport ID."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.passport_id == passport_id)
        )
        return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    email: str,
    passport_id: str,
    wallet_address: str,
) -> User:
    """Create a new user with initial state.
    
    Creates:
    - User record
    - LockdownState (active)
    - CurrencyLedger (all balances 0)
    """
    user = User(
        email=email,
        passport_id=passport_id,
        created_at=datetime.now(timezone.utc),
        lockdown_graduated=False,
        lockdown_started_at=datetime.now(timezone.utc),
        care_action_count=0,
        egg_pull_count_today=0,
    )
    db.add(user)
    await db.flush()  # Get the user ID

    # Create lockdown state
    lockdown = LockdownState(
        user_id=user.id,
        started_at=datetime.now(timezone.utc),
        care_actions_completed=0,
        min_bond_achieved=0,
        is_active=True,
    )
    db.add(lockdown)

    # Create currency ledger (all zeros)
    ledger = CurrencyLedger(
        user_id=user.id,
        dust_balance=0,
        shard_balance=0,
        cuboid_balance=0,
        ele_balance=0,
    )
    db.add(ledger)

    await db.commit()
    await db.refresh(user)
    return user


async def get_or_create_user(
    db: AsyncSession,
    email: str,
    passport_id: str,
    wallet_address: str,
) -> tuple[User, bool]:
    """Get existing user or create a new one.
    
    Returns:
        Tuple of (user, is_new_user)
    """
    # Check by passport_id first
    user = await get_user_by_passport_id(passport_id)
    if user:
        return user, False

    # Check by email
    user = await get_user_by_email(email)
    if user:
        return user, False

    # Create new user
    user = await create_user(db, email, passport_id, wallet_address)
    return user, True
