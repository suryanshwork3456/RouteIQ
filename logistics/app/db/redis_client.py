import redis.asyncio as aioredis
from app.core.config import settings
import json
from typing import Any, Optional

redis_client: aioredis.Redis = None


async def get_redis() -> aioredis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return redis_client


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()


# ── Rider location cache ──────────────────────────────────────────────────────

async def set_rider_location(rider_id: int, lat: float, lon: float, ttl: int = 300):
    r = await get_redis()
    key = f"rider:location:{rider_id}"
    await r.hset(key, mapping={"lat": lat, "lon": lon})
    await r.expire(key, ttl)


async def get_rider_location(rider_id: int) -> Optional[dict]:
    r = await get_redis()
    data = await r.hgetall(f"rider:location:{rider_id}")
    if data:
        return {"lat": float(data["lat"]), "lon": float(data["lon"])}
    return None


# ── Rider active order counter ────────────────────────────────────────────────

async def increment_rider_orders(rider_id: int) -> int:
    r = await get_redis()
    return await r.incr(f"rider:active_orders:{rider_id}")


async def decrement_rider_orders(rider_id: int) -> int:
    r = await get_redis()
    val = await r.decr(f"rider:active_orders:{rider_id}")
    return max(0, val)


async def get_rider_active_orders(rider_id: int) -> int:
    r = await get_redis()
    val = await r.get(f"rider:active_orders:{rider_id}")
    return int(val) if val else 0


# ── Pub/Sub helpers ───────────────────────────────────────────────────────────

async def publish_event(channel: str, data: Any):
    r = await get_redis()
    await r.publish(channel, json.dumps(data))


async def get_pubsub():
    r = await get_redis()
    return r.pubsub()
