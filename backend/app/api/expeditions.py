"""Expedition API router — REST endpoints for expedition management."""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas import ExpeditionDispatchRequest, ExpeditionResponse
from app.services import session_service, expedition_service

router = APIRouter(prefix="/expeditions", tags=["expeditions"])


async def get_current_user_id(authorization: str = Header(None, alias="Authorization")) -> str:
    """Extract and validate user_id from session token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )
    token = authorization.replace("Bearer ", "")
    user_id = await session_service.validate_session(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )
    return user_id


@router.post("/dispatch", response_model=ExpeditionResponse)
async def dispatch_expedition(
    request: ExpeditionDispatchRequest,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Dispatch one or more companions on an expedition."""
    user_id = await get_current_user_id(authorization)
    
    try:
        expedition = await expedition_service.dispatch_expedition(
            db, user_id, request.companion_uuids, request.biome_zone, request.duration_hours
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return ExpeditionResponse(
        uuid=str(expedition.uuid),
        companion_uuids=[str(uuid) for uuid in expedition.companion_uuids],
        biome_zone=expedition.biome_zone,
        dispatched_at=expedition.dispatched_at,
        returns_at=expedition.returns_at,
        status=expedition.status,
        risk_level=expedition.risk_level,
        max_companions=expedition.max_companions,
    )


@router.get("/active")
async def get_active_expeditions(
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Get all active expeditions for the current user."""
    user_id = await get_current_user_id(authorization)
    expeditions = await expedition_service.get_active_expeditions(db, user_id)
    
    return [
        {
            "uuid": str(e.uuid),
            "companion_uuids": [str(uuid) for uuid in e.companion_uuids],
            "biome_zone": e.biome_zone,
            "dispatched_at": e.dispatched_at.isoformat(),
            "returns_at": e.returns_at.isoformat(),
            "status": e.status,
            "risk_level": e.risk_level,
            "max_companions": e.max_companions,
        }
        for e in expeditions
    ]


@router.get("/history")
async def get_expedition_history(
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Get past completed expeditions."""
    user_id = await get_current_user_id(authorization)
    expeditions = await expedition_service.get_expedition_history(db, user_id)
    
    return [
        {
            "uuid": str(e.uuid),
            "companion_uuids": [str(uuid) for uuid in e.companion_uuids],
            "biome_zone": e.biome_zone,
            "dispatched_at": e.dispatched_at.isoformat(),
            "returns_at": e.returns_at.isoformat(),
            "status": e.status,
            "result": e.result,
        }
        for e in expeditions
    ]


@router.post("/{expedition_uuid}/collect")
async def collect_expedition(
    expedition_uuid: str,
    authorization: str = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
):
    """Collect results of a completed expedition."""
    user_id = await get_current_user_id(authorization)
    
    from uuid import UUID
    try:
        uuid = UUID(expedition_uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    # Verify ownership
    from sqlalchemy import select
    from app.models import Expedition
    result = await db.execute(
        select(Expedition).where(Expedition.uuid == expedition_uuid, Expedition.user_id == user_id)
    )
    expedition = result.scalar_one_or_none()
    if not expedition:
        raise HTTPException(status_code=404, detail="Expedition not found")
    
    try:
        outcome = await expedition_service.resolve_expedition(db, expedition_uuid)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return outcome
