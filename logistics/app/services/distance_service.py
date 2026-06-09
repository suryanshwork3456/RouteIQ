"""
Distance Service
----------------
Provides two modes:
  1. Haversine  – fast straight-line distance (always available)
  2. OSRM       – real road distance (requires OSRM server)

Falls back to Haversine automatically when OSRM is unreachable.
"""

from math import radians, sin, cos, sqrt, atan2
from typing import Tuple, List, Optional
import httpx
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Earth radius in km
_R = 6371.0


# ── Core Haversine ────────────────────────────────────────────────────────────

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Return the great-circle distance in km between two (lat, lon) points.
    """
    φ1, φ2 = radians(lat1), radians(lat2)
    Δφ = radians(lat2 - lat1)
    Δλ = radians(lon2 - lon1)

    a = sin(Δφ / 2) ** 2 + cos(φ1) * cos(φ2) * sin(Δλ / 2) ** 2
    return _R * 2 * atan2(sqrt(a), sqrt(1 - a))


def haversine_matrix(
    origins: List[Tuple[float, float]],
    destinations: List[Tuple[float, float]],
) -> List[List[float]]:
    """
    Return an (m x n) distance matrix [km] for m origins × n destinations.
    Used for bulk scoring without an external API call.
    """
    return [
        [haversine(olat, olon, dlat, dlon) for dlat, dlon in destinations]
        for olat, olon in origins
    ]


# ── OSRM road distance ────────────────────────────────────────────────────────

async def osrm_distance(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
) -> Optional[float]:
    """
    Query OSRM for the road distance in km.
    Returns None on failure so callers can fall back to Haversine.
    """
    url = (
        f"{settings.OSRM_BASE_URL}/route/v1/driving/"
        f"{lon1},{lat1};{lon2},{lat2}"
        f"?overview=false"
    )
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            distance_m = data["routes"][0]["distance"]   # metres
            return round(distance_m / 1000, 3)
    except Exception as exc:
        logger.warning("OSRM unavailable (%s); falling back to Haversine", exc)
        return None


async def osrm_matrix(
    origins: List[Tuple[float, float]],
    destinations: List[Tuple[float, float]],
) -> Optional[List[List[float]]]:
    """
    Batch road-distance matrix via OSRM /table endpoint.
    Returns None on failure.
    """
    all_coords = origins + destinations
    coord_str = ";".join(f"{lon},{lat}" for lat, lon in all_coords)
    src_idx   = ";".join(str(i) for i in range(len(origins)))
    dst_idx   = ";".join(str(i) for i in range(len(origins), len(all_coords)))
    url = (
        f"{settings.OSRM_BASE_URL}/table/v1/driving/{coord_str}"
        f"?sources={src_idx}&destinations={dst_idx}&annotations=distance"
    )
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            raw = resp.json()["distances"]   # metres
            return [[d / 1000 for d in row] for row in raw]
    except Exception as exc:
        logger.warning("OSRM matrix unavailable (%s); will fall back", exc)
        return None


# ── Unified entry point ───────────────────────────────────────────────────────

async def get_distance(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
    prefer_road: bool = True,
) -> float:
    """
    Return distance in km. Uses OSRM if available, Haversine otherwise.
    """
    if prefer_road:
        road = await osrm_distance(lat1, lon1, lat2, lon2)
        if road is not None:
            return road
    return haversine(lat1, lon1, lat2, lon2)


async def get_distance_matrix(
    origins: List[Tuple[float, float]],
    destinations: List[Tuple[float, float]],
    prefer_road: bool = True,
) -> List[List[float]]:
    """
    Return (m x n) distance matrix [km]. Uses OSRM batch if available.
    """
    if prefer_road:
        matrix = await osrm_matrix(origins, destinations)
        if matrix is not None:
            return matrix
    return haversine_matrix(origins, destinations)


# ── Utility ───────────────────────────────────────────────────────────────────

def total_route_distance(
    rider_lat: float, rider_lon: float,
    market_lat: float, market_lon: float,
    customer_lat: float, customer_lon: float,
) -> Tuple[float, float, float]:
    """
    Returns (rider→market km, market→customer km, total km) using Haversine.
    For synchronous use inside the scoring engine.
    """
    d1 = haversine(rider_lat, rider_lon, market_lat, market_lon)
    d2 = haversine(market_lat, market_lon, customer_lat, customer_lon)
    return d1, d2, d1 + d2
