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


async def award_cuboids(user_id: str, amount: int, source: str) -> int:
    """Award Cuboids to a user. Returns new balance."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CurrencyLedger).where(CurrencyLedger.user_id == user_id)
        )
        ledger = result.scalar_one_or_none()
        if not ledger:
            ledger = CurrencyLedger(user_id=user_id)
            session.add(ledger)
        
        ledger.cuboid_balance += amount
        ledger.updated_at = datetime.now(timezone.utc)
        ledger.transaction_log.append({
            "type": "award",
            "currency": "cuboid",
            "amount": amount,
            "source": source,
            "timestamp": str(datetime.now(timezone.utc)),
        })
        await session.commit()
        return ledger.cuboid_balance


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


async def spend_shards(user_id: str, amount: int, sink: str) -> tuple[bool, int]:
    """Spend Shards. Returns (success, new_balance)."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CurrencyLedger).where(CurrencyLedger.user_id == user_id)
        )
        ledger = result.scalar_one_or_none()
        if not ledger or ledger.shard_balance < amount:
            return False, ledger.shard_balance if ledger else 0
        
        ledger.shard_balance -= amount
        ledger.updated_at = datetime.now(timezone.utc)
        ledger.transaction_log.append({
            "type": "spend",
            "currency": "shard",
            "amount": amount,
            "sink": sink,
            "timestamp": str(datetime.now(timezone.utc)),
        })
        await session.commit()
        return True, ledger.shard_balance


async def get_transaction_history(user_id: str, limit: int = 50) -> list[dict]:
    """Get recent transaction history for a user."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CurrencyLedger).where(CurrencyLedger.user_id == user_id)
        )
        ledger = result.scalar_one_or_none()
        if not ledger:
            return []
        
        # Return most recent transactions
        return ledger.transaction_log[-limit:][::-1]


async def apply_shop_effect(db: AsyncSession, user_id: str, companion_uuid: str, item: dict) -> dict:
    """Apply a shop item's effect."""
    from app.models import Companion, CareState
    
    effect = item.get("effect", {})
    effect_type = effect.get("type")
    
    if effect_type == "care":
        # Apply care action
        result = await db.execute(
            select(CareState).where(CareState.companion_uuid == companion_uuid)
        )
        care_state = result.scalar_one_or_none()
        if care_state:
            action = effect.get("action")
            value = effect.get("value", 0)
            if action == "feed":
                care_state.hunger = min(1.0, care_state.hunger + value)
            return {"type": "care", "action": action, "applied": True}
    
    elif effect_type == "heal":
        # Heal companion
        result = await db.execute(
            select(Companion).where(Companion.uuid == companion_uuid, Companion.user_id == user_id)
        )
        companion = result.scalar_one_or_none()
        if companion:
            companion.health_status = min(1.0, companion.health_status + effect.get("value", 0))
            await db.commit()
            return {"type": "heal", "value": effect.get("value"), "applied": True}
    
    elif effect_type == "care_all":
        # Restore all meters
        result = await db.execute(
            select(CareState).where(CareState.companion_uuid == companion_uuid)
        )
        care_state = result.scalar_one_or_none()
        if care_state:
            value = effect.get("value", 0.7)
            care_state.hunger = value
            care_state.energy = value
            care_state.morale = value
            care_state.cleanliness = value
            await db.commit()
            return {"type": "care_all", "value": value, "applied": True}
    
    elif effect_type == "incubation_boost":
        # Boost incubation — handled by egg service
        return {"type": "incubation_boost", "value": effect.get("value"), "applied": True}
    
    return {"type": "unknown", "applied": False}
