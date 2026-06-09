from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from app.models.models import Rider, RiderStatus
from app.schemas.schemas import RiderOut, RiderLocationUpdate, RiderStatusUpdate
from app.core.auth import get_current_rider
from app.db.redis_client import (
    set_rider_location,
    get_rider_active_orders,
    get_rider_location,
    publish_event,
)

router = APIRouter(prefix="/riders", tags=["Riders"])


@router.get("/", response_model=List[RiderOut])
async def list_riders(
    status: RiderStatus = None,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db),
):
    query = select(Rider).where(Rider.is_active == is_active)
    if status:
        query = query.where(Rider.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/me", response_model=RiderOut)
async def get_me(current_rider: Rider = Depends(get_current_rider)):
    return current_rider


@router.get("/{rider_id}", response_model=RiderOut)
async def get_rider(rider_id: int, db: AsyncSession = Depends(get_db)):
    rider = await db.get(Rider, rider_id)
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")
    return rider


@router.patch("/me/location", response_model=dict)
async def update_my_location(
    data: RiderLocationUpdate,
    current_rider: Rider = Depends(get_current_rider),
    db: AsyncSession = Depends(get_db),
):
    """Rider app calls this via REST (alternative to WebSocket)."""
    # Update DB (for persistence)
    current_rider.current_lat = data.lat
    current_rider.current_lon = data.lon
    await db.commit()

    # Update Redis (for fast scoring reads)
    await set_rider_location(current_rider.id, data.lat, data.lon)

    # Broadcast to dashboard
    await publish_event("locations", {
        "event": "rider_location",
        "rider_id": current_rider.id,
        "lat": data.lat,
        "lon": data.lon,
    })

    return {"status": "ok", "rider_id": current_rider.id, "lat": data.lat, "lon": data.lon}


@router.patch("/me/status", response_model=RiderOut)
async def update_my_status(
    data: RiderStatusUpdate,
    current_rider: Rider = Depends(get_current_rider),
    db: AsyncSession = Depends(get_db),
):
    current_rider.status = data.status
    await db.commit()
    await db.refresh(current_rider)

    await publish_event("status_updates", {
        "event": "rider_status",
        "rider_id": current_rider.id,
        "status": data.status,
    })
    return current_rider


@router.get("/{rider_id}/stats", response_model=dict)
async def get_rider_stats(rider_id: int, db: AsyncSession = Depends(get_db)):
    """Live stats including Redis-based active order count."""
    rider = await db.get(Rider, rider_id)
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")

    active_orders  = await get_rider_active_orders(rider_id)
    live_location  = await get_rider_location(rider_id)

    return {
        "rider_id": rider_id,
        "name": rider.name,
        "status": rider.status,
        "avg_rating": rider.avg_rating,
        "total_ratings": rider.total_ratings,
        "total_deliveries": rider.total_deliveries,
        "active_orders": active_orders,
        "max_capacity": rider.max_capacity,
        "live_location": live_location,
    }
