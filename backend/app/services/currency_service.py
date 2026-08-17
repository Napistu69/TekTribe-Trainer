"""Currency service — handles awarding and spending currency."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import CurrencyLedger


async def get_balance(user_id: str) -> Optional[CurrencyLedger]:
    """Get a user's currency balance."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CurrencyLedger).where(CurrencyLedger.user_id == user_id)
        )
        return result.scalar_one_or_none()


async def award_dust(user_id: str, amount: int, source: str) -> int:
    """Award Dust to a user. Returns new balance."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CurrencyLedger).where(CurrencyLedger.user_id == user_id)
        )
        ledger = result.scalar_one_or_none()
        if not ledger:
            ledger = CurrencyLedger(user_id=user_id)
            session.add(ledger)
        
        ledger.dust_balance += amount
        ledger.updated_at = datetime.now(timezone.utc)
        ledger.transaction_log.append({
            "type": "award",
            "currency": "dust",
            "amount": amount,
            "source": source,
            "timestamp": str(datetime.now(timezone.utc)),
        })
        await session.commit()
        return ledger.dust_balance


async def award_shards(user_id: str, amount: int, source: str) -> int:
    """Award Shards to a user. Returns new balance."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CurrencyLedger).where(CurrencyLedger.user_id == user_id)
        )
        ledger = result.scalar_one_or_none()
        if not ledger:
            ledger = CurrencyLedger(user_id=user_id)
            session.add(ledger)
        
        ledger.shard_balance += amount
        ledger.updated_at = datetime.now(timezone.utc)
        ledger.transaction_log.append({
            "type": "award",
            "currency": "shard",
            "amount": amount,
            "source": source,
            "timestamp": str(datetime.now(timezone.utc)),
        })
        await session.commit()
        return ledger.shard_balance


async def spend_dust(user_id: str, amount: int, sink: str) -> tuple[bool, int]:
    """Spend Dust. Returns (success, new_balance)."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CurrencyLedger).where(CurrencyLedger.user_id == user_id)
        )
        ledger = result.scalar_one_or_none()
        if not ledger or ledger.dust_balance < amount:
            return False, ledger.dust_balance if ledger else 0
        
        ledger.dust_balance -= amount
        ledger.updated_at = datetime.now(timezone.utc)
        ledger.transaction_log.append({
            "type": "spend",
            "currency": "dust",
            "amount": amount,
            "sink": sink,
            "timestamp": str(datetime.now(timezone.utc)),
        })
        await session.commit()
        return True, ledger.dust_balance
