"""
WebSocket Manager
-----------------
Manages two WebSocket channels:

  /ws/rider/{rider_id}   – rider app sends GPS location updates,
                           receives new order assignments in real-time

  /ws/dashboard          – ops dashboard receives all events
                           (assignments, location updates, deliveries)

Uses Redis Pub/Sub as the message bus so multiple FastAPI workers
stay in sync.
"""

import asyncio
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect

from app.db.redis_client import get_redis, set_rider_location, publish_event

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        # rider_id → WebSocket
        self.rider_connections: Dict[int, WebSocket] = {}
        # set of dashboard WebSocket connections
        self.dashboard_connections: Set[WebSocket] = set()

    # ── Connect / disconnect ──────────────────────────────────────────────────

    async def connect_rider(self, rider_id: int, ws: WebSocket):
        await ws.accept()
        self.rider_connections[rider_id] = ws
        logger.info("Rider %d connected via WebSocket", rider_id)
        await self._broadcast_dashboard({
            "event": "rider_connected",
            "rider_id": rider_id,
        })

    async def disconnect_rider(self, rider_id: int):
        self.rider_connections.pop(rider_id, None)
        logger.info("Rider %d disconnected", rider_id)
        await self._broadcast_dashboard({
            "event": "rider_disconnected",
            "rider_id": rider_id,
        })

    async def connect_dashboard(self, ws: WebSocket):
        await ws.accept()
        self.dashboard_connections.add(ws)
        logger.info("Dashboard client connected (%d total)", len(self.dashboard_connections))

    async def disconnect_dashboard(self, ws: WebSocket):
        self.dashboard_connections.discard(ws)

    # ── Send to specific rider ────────────────────────────────────────────────

    async def send_to_rider(self, rider_id: int, data: dict):
        ws = self.rider_connections.get(rider_id)
        if ws:
            try:
                await ws.send_json(data)
            except Exception as exc:
                logger.warning("Failed to send to rider %d: %s", rider_id, exc)
                await self.disconnect_rider(rider_id)

    # ── Broadcast to dashboard ────────────────────────────────────────────────

    async def _broadcast_dashboard(self, data: dict):
        dead = set()
        for ws in self.dashboard_connections:
            try:
                await ws.send_json(data)
            except Exception:
                dead.add(ws)
        self.dashboard_connections -= dead

    # ── Handle incoming rider message ─────────────────────────────────────────

    async def handle_rider_message(self, rider_id: int, raw: str):
        """
        Rider app sends JSON messages, e.g.:
          {"type": "location", "lat": 28.61, "lon": 77.20}
          {"type": "status",   "status": "picked_up"}
        """
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            return

        msg_type = msg.get("type")

        if msg_type == "location":
            lat, lon = msg.get("lat"), msg.get("lon")
            if lat is not None and lon is not None:
                await set_rider_location(rider_id, lat, lon)
                await publish_event("locations", {
                    "event": "rider_location",
                    "rider_id": rider_id,
                    "lat": lat,
                    "lon": lon,
                })
                await self._broadcast_dashboard({
                    "event": "rider_location",
                    "rider_id": rider_id,
                    "lat": lat,
                    "lon": lon,
                })

        elif msg_type == "status":
            status = msg.get("status")
            await publish_event("status_updates", {
                "event": "rider_status",
                "rider_id": rider_id,
                "status": status,
            })
            await self._broadcast_dashboard({
                "event": "rider_status",
                "rider_id": rider_id,
                "status": status,
            })


# Singleton
manager = ConnectionManager()


# ── Redis subscriber (run as background task) ─────────────────────────────────

async def redis_event_listener():
    """
    Listens to Redis channels and forwards events to the correct WebSocket clients.
    Run this as an asyncio background task on app startup.
    """
    r = await get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe("assignments", "ratings", "locations", "status_updates")

    logger.info("Redis event listener started")

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue
        try:
            data = json.loads(message["data"])
            channel = message["channel"]

            # Forward assignment events to specific rider
            if channel == "assignments":
                rider_id = data.get("rider_id")
                if rider_id:
                    await manager.send_to_rider(rider_id, data)
                await manager._broadcast_dashboard(data)

            elif channel in ("ratings", "status_updates"):
                await manager._broadcast_dashboard(data)

        except Exception as exc:
            logger.error("Redis listener error: %s", exc)
