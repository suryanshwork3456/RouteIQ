from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.websocket_manager import manager
from app.db.session import get_db

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/rider/{rider_id}")
async def rider_websocket(rider_id: int, ws: WebSocket):
    """
    Rider app connects here.
    Send:  {"type": "location", "lat": 28.61, "lon": 77.20}
           {"type": "status",   "status": "picked_up"}
    Recv:  assignment events, new order notifications
    """
    await manager.connect_rider(rider_id, ws)
    try:
        while True:
            raw = await ws.receive_text()
            await manager.handle_rider_message(rider_id, raw)
    except WebSocketDisconnect:
        await manager.disconnect_rider(rider_id)


@router.websocket("/dashboard")
async def dashboard_websocket(ws: WebSocket):
    """
    Ops dashboard connects here to receive all real-time events:
    - rider_location updates
    - order_assigned events
    - order_status_changed events
    - rider_connected / rider_disconnected
    """
    await manager.connect_dashboard(ws)
    try:
        while True:
            # Dashboard is read-only; just keep connection alive
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect_dashboard(ws)
