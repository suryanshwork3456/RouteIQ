"""
Celery Worker
-------------
Runs the assignment engine on a periodic beat schedule.
Also handles async tasks triggered by new order creation.

Start worker:
    celery -A app.worker.celery_app worker --loglevel=info

Start beat scheduler:
    celery -A app.worker.celery_app beat --loglevel=info
"""

import asyncio
import logging
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "logistics",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "run-assignment-cycle": {
            "task": "app.worker.run_assignment_cycle_task",
            "schedule": settings.ASSIGNMENT_INTERVAL_SECONDS,
        },
    },
)


def _run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.worker.run_assignment_cycle_task", bind=True, max_retries=3)
def run_assignment_cycle_task(self):
    """Periodic task: assign pending orders to riders."""
    async def _inner():
        from app.db.session import AsyncSessionLocal
        from app.services.assignment_engine import run_assignment_cycle

        async with AsyncSessionLocal() as db:
            result = await run_assignment_cycle(db)
            logger.info(
                "Celery assignment cycle: %d assigned, %d unassigned",
                len(result.assignments),
                len(result.unassigned_order_ids),
            )
            return {
                "assigned": len(result.assignments),
                "unassigned": len(result.unassigned_order_ids),
            }

    try:
        return _run_async(_inner())
    except Exception as exc:
        logger.error("Assignment cycle failed: %s", exc)
        raise self.retry(exc=exc, countdown=10)


@celery_app.task(name="app.worker.assign_order_task", bind=True, max_retries=3)
def assign_order_task(self, order_id: int):
    """Triggered immediately when a new order is created."""
    async def _inner():
        from app.db.session import AsyncSessionLocal
        from app.services.assignment_engine import assign_single_order

        async with AsyncSessionLocal() as db:
            result = await assign_single_order(order_id, db)
            if result:
                logger.info("Immediately assigned order %d to rider %d", order_id, result.rider_id)
                return {"assigned": True, "rider_id": result.rider_id}
            logger.info("Order %d queued for next cycle", order_id)
            return {"assigned": False}

    try:
        return _run_async(_inner())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
