"""Temporary admin endpoint to unstuck companions (for testing)."""
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select, update

from app.core.database import get_db
from app.api.expeditions import get_current_user_id
from app.models import Companion

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/unstuck-companions")
async def unstuck_companions(
    authorization: str = Header(None, alias="Authorization"),
    db=Depends(get_db),
):
    """Reset all companions stuck on_expedition back to resting (for testing)."""
    user_id = await get_current_user_id(authorization)

    # Reset companions
    await db.execute(
        update(Companion)
        .where(Companion.user_id == user_id, Companion.current_state == "on_expedition")
        .values(current_state="resting")
    )
    await db.commit()

    # Also cancel any active expeditions
    from app.models import Expedition
    await db.execute(
        update(Expedition)
        .where(Expedition.user_id == user_id, Expedition.status == "dispatched")
        .values(status="cancelled")
    )
    await db.commit()

    # Count remaining companions
    result = await db.execute(
        select(Companion).where(Companion.user_id == user_id)
    )
    companions = result.scalars().all()

    return {
        "status": "unstuck",
        "companions_reset": len([c for c in companions]),
        "companions_resting": len([c for c in companions if c.current_state == "resting"]),
    }
