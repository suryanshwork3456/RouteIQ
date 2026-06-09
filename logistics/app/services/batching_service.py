"""
Batching Service
----------------
Groups pending orders into batches so one rider can deliver multiple
orders from the same supermarket in a single trip.

Algorithm:
  1. Group orders by supermarket_id
  2. Within each supermarket group, cluster customer delivery locations
     using DBSCAN (density-based) — no need to pre-specify # of clusters
  3. Enforce MAX_BATCH_SIZE per batch
  4. Return list of BatchGroup objects
"""

import uuid
import logging
from dataclasses import dataclass, field
from typing import List, Dict
from collections import defaultdict

import numpy as np
from sklearn.cluster import DBSCAN

from app.core.config import settings
from app.models.models import Order

logger = logging.getLogger(__name__)

# DBSCAN uses radians when metric='haversine'
_KM_TO_RAD = 1.0 / 6371.0


@dataclass
class BatchGroup:
    batch_id: str
    supermarket_id: int
    order_ids: List[int]
    centroid_lat: float
    centroid_lon: float
    estimated_extra_km: float = 0.0   # extra km vs single delivery


def _dbscan_cluster(
    orders: List[Order],
    radius_km: float,
    min_samples: int = 1,
) -> Dict[int, List[Order]]:
    """
    Cluster orders by delivery location using DBSCAN.
    Returns {cluster_label: [Order, ...]}
    """
    if len(orders) == 1:
        return {0: orders}

    coords = np.radians(
        np.array([[o.delivery_lat, o.delivery_lon] for o in orders])
    )
    eps = radius_km * _KM_TO_RAD

    labels = DBSCAN(
        eps=eps,
        min_samples=min_samples,
        algorithm="ball_tree",
        metric="haversine",
    ).fit_predict(coords)

    clusters: Dict[int, List[Order]] = defaultdict(list)
    for order, label in zip(orders, labels):
        clusters[label].append(order)

    return dict(clusters)


def _split_oversized(orders: List[Order], max_size: int) -> List[List[Order]]:
    """Split a cluster that exceeds MAX_BATCH_SIZE into smaller chunks."""
    return [orders[i: i + max_size] for i in range(0, len(orders), max_size)]


def _centroid(orders: List[Order]):
    lats = [o.delivery_lat for o in orders]
    lons = [o.delivery_lon for o in orders]
    return sum(lats) / len(lats), sum(lons) / len(lons)


def build_batches(
    pending_orders: List[Order],
    radius_km: float = None,
    max_batch_size: int = None,
) -> List[BatchGroup]:
    """
    Main entry point.
    Takes a flat list of pending orders, returns a list of BatchGroup objects.
    Each BatchGroup will be assigned to one rider.
    """
    radius_km      = radius_km      or settings.MAX_BATCH_RADIUS_KM
    max_batch_size = max_batch_size or settings.MAX_BATCH_SIZE

    if not pending_orders:
        return []

    # Step 1 – group by supermarket
    by_market: Dict[int, List[Order]] = defaultdict(list)
    for o in pending_orders:
        by_market[o.supermarket_id].append(o)

    batches: List[BatchGroup] = []

    for market_id, market_orders in by_market.items():
        if len(market_orders) == 1:
            # No batching possible; single order
            o = market_orders[0]
            batches.append(BatchGroup(
                batch_id=str(uuid.uuid4()),
                supermarket_id=market_id,
                order_ids=[o.id],
                centroid_lat=o.delivery_lat,
                centroid_lon=o.delivery_lon,
            ))
            continue

        # Step 2 – cluster by delivery location
        clusters = _dbscan_cluster(market_orders, radius_km)

        for label, cluster_orders in clusters.items():
            # Step 3 – enforce max batch size
            sub_batches = _split_oversized(cluster_orders, max_batch_size)

            for sub in sub_batches:
                clat, clon = _centroid(sub)
                batches.append(BatchGroup(
                    batch_id=str(uuid.uuid4()),
                    supermarket_id=market_id,
                    order_ids=[o.id for o in sub],
                    centroid_lat=clat,
                    centroid_lon=clon,
                ))

    logger.info(
        "Batching: %d orders → %d batches",
        len(pending_orders), len(batches),
    )
    return batches


def get_batchable_count(
    target_order: Order,
    all_pending: List[Order],
    radius_km: float = None,
) -> int:
    """
    How many orders (including target) can be batched with target_order?
    Used in scoring without building full batches.
    """
    radius_km = radius_km or settings.MAX_BATCH_RADIUS_KM
    from app.services.distance_service import haversine

    same_market = [
        o for o in all_pending
        if o.supermarket_id == target_order.supermarket_id and o.id != target_order.id
    ]
    count = 1  # the order itself
    for o in same_market:
        d = haversine(
            target_order.delivery_lat, target_order.delivery_lon,
            o.delivery_lat, o.delivery_lon,
        )
        if d <= radius_km:
            count += 1
            if count >= settings.MAX_BATCH_SIZE:
                break
    return count
