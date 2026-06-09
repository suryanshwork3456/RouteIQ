"""
Rating Service
--------------
Handles rider ratings submitted after delivery.
Uses a rolling average update to keep avg_rating accurate without
recalculating from all rows each time.

Formula for rolling avg:
    new_avg = (old_avg * total_ratings + new_stars) / (total_ratings + 1)
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import RiderRating, Rider, Order, OrderStatus
from app.schemas.schemas import RatingCreate, RatingOut
from app.db.redis_client import publish_event

logger = logging.getLogger(__name__)


async def submit_rating(
    data: RatingCreate,
    db: AsyncSession,
) -> RatingOut:
    """
    Submit a star rating for a completed order.
    Updates rider's rolling average atomically.
    Raises ValueError on invalid input.
    """
    # Validate order exists and is delivered
    order: Order = await db.get(Order, data.order_id)
    if not order:
        raise ValueError(f"Order {data.order_id} not found")
    if order.status != OrderStatus.delivered:
        raise ValueError("Can only rate delivered orders")
    if not order.rider_id:
        raise ValueError("Order has no assigned rider")

    # Check if already rated
    existing = await db.execute(
        select(RiderRating).where(RiderRating.order_id == data.order_id)
    )
    if existing.scalar_one_or_none():
        raise ValueError("Order already rated")

    # Fetch rider
    rider: Rider = await db.get(Rider, order.rider_id)
    if not rider:
        raise ValueError("Rider not found")

    # Create rating record
    rating = RiderRating(
        rider_id=rider.id,
        order_id=data.order_id,
        stars=data.stars,
        comment=data.comment,
    )
    db.add(rating)

    # Rolling average update
    new_total = rider.total_ratings + 1
    new_avg   = (rider.avg_rating * rider.total_ratings + data.stars) / new_total

    rider.avg_rating    = round(new_avg, 2)
    rider.total_ratings = new_total

    await db.commit()
    await db.refresh(rating)

    # Publish rating event
    await publish_event("ratings", {
        "event": "rider_rated",
        "rider_id": rider.id,
        "order_id": data.order_id,
        "stars": data.stars,
        "new_avg": rider.avg_rating,
    })

    logger.info(
        "Rider %d rated %.1f stars (new avg: %.2f over %d ratings)",
        rider.id, data.stars, rider.avg_rating, rider.total_ratings,
    )

    return RatingOut(
        id=rating.id,
        rider_id=rating.rider_id,
        order_id=rating.order_id,
        stars=rating.stars,
        comment=rating.comment,
        created_at=rating.created_at,
    )


async def get_rider_ratings_summary(rider_id: int, db: AsyncSession) -> dict:
    """Returns rating summary stats for a rider."""
    rider: Rider = await db.get(Rider, rider_id)
    if not rider:
        raise ValueError("Rider not found")

    result = await db.execute(
        select(RiderRating).where(RiderRating.rider_id == rider_id)
        .order_by(RiderRating.created_at.desc())
        .limit(20)
    )
    recent_ratings = result.scalars().all()

    breakdown = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in recent_ratings:
        key = round(r.stars)
        breakdown[key] = breakdown.get(key, 0) + 1

    return {
        "rider_id": rider_id,
        "avg_rating": rider.avg_rating,
        "total_ratings": rider.total_ratings,
        "total_deliveries": rider.total_deliveries,
        "recent_ratings": [
            {"order_id": r.order_id, "stars": r.stars, "comment": r.comment, "created_at": r.created_at}
            for r in recent_ratings
        ],
        "star_breakdown": breakdown,
    }
