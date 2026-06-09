"""
Efficiency Scoring Engine
--------------------------
Computes a composite score [0, 1] for each (rider, batch) pair.

Formula:
    score = w_dist * distance_score
          + w_batch * batch_score
          + w_rating * rating_score
          + w_busy  * busyness_score

All sub-scores are normalised to [0, 1].
Higher score = better assignment.
"""

import logging
from dataclasses import dataclass
from typing import List, Tuple

from app.core.config import settings
from app.models.models import Rider
from app.services.distance_service import haversine, total_route_distance
from app.services.batching_service import BatchGroup

logger = logging.getLogger(__name__)

# City-wide worst-case distance cap for normalisation (km).
# Adjust for the actual city size.
_MAX_CITY_DISTANCE_KM = 50.0


@dataclass
class ScoreBreakdown:
    rider_id: int
    batch_id: str
    total_score: float

    distance_score: float
    batch_score: float
    rating_score: float
    busyness_score: float

    rider_to_market_km: float
    market_to_centroid_km: float
    total_distance_km: float
    active_orders: int


# ── Individual sub-scorers ────────────────────────────────────────────────────

def _distance_score(
    rider: Rider,
    market_lat: float,
    market_lon: float,
    centroid_lat: float,
    centroid_lon: float,
) -> Tuple[float, float, float, float]:
    """
    Returns (distance_score, rider→market km, market→centroid km, total km).
    Score is higher when total route is shorter.
    """
    d_rider_market  = haversine(rider.current_lat, rider.current_lon, market_lat, market_lon)
    d_market_cust   = haversine(market_lat, market_lon, centroid_lat, centroid_lon)
    total           = d_rider_market + d_market_cust

    score = max(0.0, 1.0 - (total / _MAX_CITY_DISTANCE_KM))
    return round(score, 4), d_rider_market, d_market_cust, total


def _batch_score(batch_size: int) -> float:
    """
    Larger batch = higher efficiency.
    score = (batch_size - 1) / (MAX_BATCH_SIZE - 1)
    Single order → 0, full batch → 1.
    """
    max_b = max(settings.MAX_BATCH_SIZE - 1, 1)
    return round(min((batch_size - 1) / max_b, 1.0), 4)


def _rating_score(avg_rating: float) -> float:
    """
    Normalise 1–5 star rating to [0, 1].
    """
    return round(max(0.0, min((avg_rating - 1.0) / 4.0, 1.0)), 4)


def _busyness_score(active_orders: int, max_capacity: int) -> float:
    """
    Penalise busy riders.
    0 active orders → 1.0, full capacity → 0.0.
    """
    if max_capacity <= 0:
        return 0.0
    return round(max(0.0, 1.0 - (active_orders / max_capacity)), 4)


# ── Composite scorer ──────────────────────────────────────────────────────────

def compute_score(
    rider: Rider,
    active_orders: int,          # from Redis counter
    batch: BatchGroup,
    market_lat: float,
    market_lon: float,
) -> ScoreBreakdown:
    """
    Compute the full efficiency score for one (rider, batch) pair.
    """
    w = settings  # shorthand

    d_score, d_rm, d_mc, d_total = _distance_score(
        rider, market_lat, market_lon,
        batch.centroid_lat, batch.centroid_lon,
    )
    b_score  = _batch_score(len(batch.order_ids))
    r_score  = _rating_score(rider.avg_rating)
    bu_score = _busyness_score(active_orders, rider.max_capacity)

    total = (
        w.WEIGHT_DISTANCE * d_score +
        w.WEIGHT_BATCH    * b_score +
        w.WEIGHT_RATING   * r_score +
        w.WEIGHT_BUSYNESS * bu_score
    )

    return ScoreBreakdown(
        rider_id=rider.id,
        batch_id=batch.batch_id,
        total_score=round(total, 4),
        distance_score=d_score,
        batch_score=b_score,
        rating_score=r_score,
        busyness_score=bu_score,
        rider_to_market_km=round(d_rm, 3),
        market_to_centroid_km=round(d_mc, 3),
        total_distance_km=round(d_total, 3),
        active_orders=active_orders,
    )


def rank_riders_for_batch(
    batch: BatchGroup,
    riders: List[Rider],
    active_orders_map: dict,     # {rider_id: int}
    market_lat: float,
    market_lon: float,
) -> List[ScoreBreakdown]:
    """
    Score all eligible riders for a given batch and return sorted descending.
    Filters out riders who are maxed_out or have no location data.
    """
    eligible = [
        r for r in riders
        if r.is_active
        and r.current_lat is not None
        and r.current_lon is not None
        and active_orders_map.get(r.id, 0) < r.max_capacity
    ]

    if not eligible:
        logger.warning("No eligible riders for batch %s", batch.batch_id)
        return []

    scores = [
        compute_score(
            rider=r,
            active_orders=active_orders_map.get(r.id, 0),
            batch=batch,
            market_lat=market_lat,
            market_lon=market_lon,
        )
        for r in eligible
    ]

    scores.sort(key=lambda s: s.total_score, reverse=True)
    return scores
