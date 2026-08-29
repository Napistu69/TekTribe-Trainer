"""Forge service — handles currency refinement (Dust > Shards > Cuboids > $ELE)."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import CurrencyLedger

# Refinement rates
REFINEMENT_RATES = {
    "dust_to_shard": {"input": 100, "output": 1},    # 100 Dust = 1 Shard
    "shard_to_cuboid": {"input": 10, "output": 1},   # 10 Shards = 1 Cuboid
    "cuboid_to_ele": {"input": 10, "output": 1},     # 10 Cuboids = 1 $ELE
}

REFINEMENT_COSTS = {
    "dust_to_shard": {"currency": "dust", "amount": 100},
    "shard_to_cuboid": {"currency": "shard", "amount": 10},
    "cuboid_to_ele": {"currency": "cuboid", "amount": 10},
}

REFINEMENT_OUTPUTS = {
    "dust_to_shard": {"currency": "shard", "amount": 1},
    "shard_to_cuboid": {"currency": "cuboid", "amount": 1},
    "cuboid_to_ele": {"currency": "ele", "amount": 1},
}


async def get_refinement_options() -> list[dict]:
    """Get available refinement options with rates."""
    options = []
    for key, rate in REFINEMENT_RATES.items():
        cost = REFINEMENT_COSTS[key]
        output = REFINEMENT_OUTPUTS[key]
        options.append({
            "id": key,
            "input_currency": cost["currency"],
            "input_amount": cost["amount"],
            "output_currency": output["currency"],
            "output_amount": output["amount"],
        })
    return options


async def refine_currency(
    user_id: str,
    refinement_type: str,
    times: int = 1,
) -> dict:
    """
    Refine currency. Returns result with success status and details.
    
    Args:
        user_id: User ID
        refinement_type: One of 'dust_to_shard', 'shard_to_cuboid', 'cuboid_to_ele'
        times: Number of times to refine (default 1)
    """
    if refinement_type not in REFINEMENT_RATES:
        return {"success": False, "error": "Invalid refinement type"}
    
    if times < 1 or times > 100:
        return {"success": False, "error": "Times must be between 1 and 100"}
    
    cost = REFINEMENT_COSTS[refinement_type]
    output = REFINEMENT_OUTPUTS[refinement_type]
    
    total_input = cost["amount"] * times
    total_output = output["amount"] * times
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CurrencyLedger).where(CurrencyLedger.user_id == user_id)
        )
        ledger = result.scalar_one_or_none()
        
        if not ledger:
            return {"success": False, "error": "No wallet found"}
        
        # Check balance
        balance_attr = f"{cost['currency']}_balance"
        current_balance = getattr(ledger, balance_attr, 0)
        
        if current_balance < total_input:
            return {
                "success": False,
                "error": f"Insufficient {cost['currency']}. Need {total_input}, have {current_balance}",
                "current_balance": current_balance,
                "required": total_input,
            }
        
        # Deduct input
        setattr(ledger, balance_attr, current_balance - total_input)
        
        # Add output
        output_attr = f"{output['currency']}_balance"
        current_output = getattr(ledger, output_attr, 0)
        setattr(ledger, output_attr, current_output + total_output)
        
        ledger.updated_at = datetime.now(timezone.utc)
        ledger.transaction_log.append({
            "type": "refine",
            "refinement_type": refinement_type,
            "input_currency": cost["currency"],
            "input_amount": total_input,
            "output_currency": output["currency"],
            "output_amount": total_output,
            "times": times,
            "timestamp": str(datetime.now(timezone.utc)),
        })
        
        await session.commit()
        
        return {
            "success": True,
            "refinement_type": refinement_type,
            "input_currency": cost["currency"],
            "input_amount": total_input,
            "output_currency": output["currency"],
            "output_amount": total_output,
            "times": times,
            "new_balances": {
                "dust": ledger.dust_balance,
                "shard": ledger.shard_balance,
                "cuboid": ledger.cuboid_balance,
                "ele": ledger.ele_balance,
            },
        }
