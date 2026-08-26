"""Add cancel expedition endpoint

Allows players to recall a companion from an expedition early.
Companion returns immediately and is available again.

"""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.expeditions import get_current_user_id

router = APIRouter(prefix="/expeditions", tags=["expeditions"])


@router.post("/{expedition_uuid}/cancel")
async def cancel_expedition(
    expedition_uuid: str,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Cancel an active expedition and recall the companion."""
    user_id = await get_current_user_id(authorization)
    
    from sqlalchemy import select
    from app.models import Expedition, Companion
    
    result = await db.execute(
        select(Expedition).where(
            Expedition.uuid == expedition_uuid,
            Expedition.user_id == user_id
        )
    )
    expedition = result.scalar_one_or_none()
    
    if not expedition:
        raise HTTPException(status_code=404, detail="Expedition not found")
    
    if expedition.status != "dispatched":
        raise HTTPException(status_code=400, detail="Expedition is not active")
    
    # Set companion back to resting
    companion_result = await db.execute(
        select(Companion).where(Companion.uuid == expedition.companion_uuid)
    )
    companion = companion_result.scalar_one_or_none()
    if companion:
        companion.current_state = "resting"
    
    # Mark expedition as cancelled
    expedition.status = "cancelled"
    
    await db.commit()
    
    return {"status": "cancelled", "companion_uuid": str(expedition.companion_uuid)}


@router.post("/{expedition_uuid}/force-complete")
async def force_complete_expedition(
    expedition_uuid: str,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Force-complete an expedition and grant rewards (for stuck expeditions)."""
    user_id = await get_current_user_id(authorization)
    
    from sqlalchemy import select
    from app.models import Expedition, Companion
    
    result = await db.execute(
        select(Expedition).where(
            Expedition.uuid == expedition_uuid,
            Expedition.user_id == user_id
        )
    )
    expedition = result.scalar_one_or_none()
    
    if not expedition:
        raise HTTPException(status_code=404, detail="Expedition not found")
    
    if expedition.status != "dispatched":
        raise HTTPException(status_code=400, detail="Expedition is not active")
    
    # Resolve the expedition with full rewards
    from app.services.expedition_service import resolve_expedition
    outcome = await resolve_expedition(db, expedition_uuid)
    
    return {"status": "completed", "result": outcome}
async def cancel_all_expeditions(
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Cancel all active expeditions for a user."""
    user_id = await get_current_user_id(authorization)
    
    from sqlalchemy import select
    from app.models import Expedition, Companion
    
    result = await db.execute(
        select(Expedition).where(
            Expedition.user_id == user_id,
            Expedition.status == "dispatched"
        )
    )
    expeditions = result.scalars().all()
    
    cancelled = []
    for expedition in expeditions:
        companion_result = await db.execute(
            select(Companion).where(Companion.uuid == expedition.companion_uuid)
        )
        companion = companion_result.scalar_one_or_none()
        if companion:
            companion.current_state = "resting"
        expedition.status = "cancelled"
        cancelled.append(str(expedition.uuid))
    
    await db.commit()
    
    return {"status": "cancelled_all", "cancelled_count": len(cancelled)}
