# app/routers/tracking.py
from fastapi import APIRouter, status
from app.database.state import state
from app.routers.map_ws import manager

# Import schemas for both entities
from app.schemas.orders import OrderCreate
from app.schemas.riders import RiderLocationUpdate

# We use a broader prefix like /api since this router handles multiple resources
router = APIRouter(prefix="/api", tags=["Logistics Tracking"])

# -----------------------------------------------------------------------------
# 1. ORDERS ENDPOINTS
# -----------------------------------------------------------------------------
@router.post("/orders", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_new_order(payload: OrderCreate):
    """Inserts a fresh customer order and drops a package popup onto the map views."""
    order_id = payload.id
    
    # Save to in-memory store
    state["orders"][order_id] = {
        "lat": payload.lat,
        "lng": payload.lng,
        "status": payload.status
    }
    
    # Direct live synchronization signal down to websocket pipelines
    broadcast_data = {
        "type": "ORDER_UPDATED",
        "id": order_id,
        "lat": payload.lat,
        "lng": payload.lng,
        "status": payload.status
    }
    await manager.broadcast(broadcast_data)
    
    return {"status": "success", "message": f"Order {order_id} generated."}


# -----------------------------------------------------------------------------
# 2. RIDERS ENDPOINTS
# -----------------------------------------------------------------------------
@router.post("/riders/location", response_model=dict, status_code=status.HTTP_200_OK)
async def update_rider_location(payload: RiderLocationUpdate):
    """Receives coordinate pings from active delivery personnel apps and moves map markers."""
    rider_id = payload.id
    
    # Save to in-memory store
    state["riders"][rider_id] = {
        "lat": payload.lat,
        "lng": payload.lng,
        "status": payload.status
    }
    
    # Push immediate marker shifts out to monitoring clients
    broadcast_data = {
        "type": "RIDER_UPDATED",
        "id": rider_id,
        "lat": payload.lat,
        "lng": payload.lng,
        "status": payload.status
    }
    await manager.broadcast(broadcast_data)
    
    return {"status": "success"}