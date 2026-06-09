"""
Logistics Backend — FastAPI Entry Point
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import engine
from app.db.redis_client import get_redis, close_redis
from app.models.models import Base
from app.utils.websocket_manager import redis_event_listener

# ── Routes ────────────────────────────────────────────────────────────────────
from app.api.routes.auth         import router as auth_router
from app.api.routes.orders       import router as orders_router
from app.api.routes.riders       import router as riders_router
from app.api.routes.supermarkets import router as supermarkets_router
from app.api.routes.ratings      import router as ratings_router
from app.api.routes.websockets   import router as ws_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Logistics API...")

    # Create all DB tables (use Alembic for production migrations)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Verify Redis
    await get_redis()
    logger.info("Redis connected")

    # Start Redis Pub/Sub listener as background task
    task = asyncio.create_task(redis_event_listener())

    yield

    # Shutdown
    task.cancel()
    await close_redis()
    await engine.dispose()
    logger.info("Logistics API shut down cleanly")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Logistics Assignment API",
    description="Smart order assignment with batching, scoring, and real-time tracking",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ──────────────────────────────────────────────────────────

app.include_router(auth_router,         prefix="/api")
app.include_router(orders_router,       prefix="/api")
app.include_router(riders_router,       prefix="/api")
app.include_router(supermarkets_router, prefix="/api")
app.include_router(ratings_router,      prefix="/api")
app.include_router(ws_router)           # WebSocket — no /api prefix


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


# ── Dev entrypoint ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
