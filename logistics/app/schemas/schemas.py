from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models.models import RiderStatus, OrderStatus


# ── Supermarket ───────────────────────────────────────────────────────────────

class SupermarketBase(BaseModel):
    name: str
    address: Optional[str] = None
    lat: float
    lon: float


class SupermarketCreate(SupermarketBase):
    pass


class SupermarketOut(SupermarketBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Rider ─────────────────────────────────────────────────────────────────────

class RiderCreate(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    password: str
    max_capacity: int = 4


class RiderLocationUpdate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class RiderOut(BaseModel):
    id: int
    name: str
    phone: str
    status: RiderStatus
    current_lat: Optional[float]
    current_lon: Optional[float]
    avg_rating: float
    total_deliveries: int
    max_capacity: int
    is_active: bool

    class Config:
        from_attributes = True


class RiderStatusUpdate(BaseModel):
    status: RiderStatus


# ── Customer ──────────────────────────────────────────────────────────────────

class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    lat: float
    lon: float
    address: Optional[str] = None


class CustomerOut(BaseModel):
    id: int
    name: str
    phone: str
    lat: float
    lon: float
    address: Optional[str]

    class Config:
        from_attributes = True


# ── Order ─────────────────────────────────────────────────────────────────────

class OrderCreate(BaseModel):
    customer_id: int
    supermarket_id: int
    delivery_lat: float
    delivery_lon: float
    delivery_address: Optional[str] = None
    items_json: Optional[str] = None   # JSON string


class OrderOut(BaseModel):
    id: int
    customer_id: int
    supermarket_id: int
    rider_id: Optional[int]
    delivery_lat: float
    delivery_lon: float
    delivery_address: Optional[str]
    status: OrderStatus
    batch_id: Optional[str]
    rider_to_market_km: Optional[float]
    market_to_customer_km: Optional[float]
    total_distance_km: Optional[float]
    assignment_score: Optional[float]
    created_at: datetime
    assigned_at: Optional[datetime]
    delivered_at: Optional[datetime]

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


# ── Rating ────────────────────────────────────────────────────────────────────

class RatingCreate(BaseModel):
    order_id: int
    stars: float = Field(..., ge=1.0, le=5.0)
    comment: Optional[str] = None


class RatingOut(BaseModel):
    id: int
    rider_id: int
    order_id: int
    stars: float
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Assignment ────────────────────────────────────────────────────────────────

class AssignmentResult(BaseModel):
    order_id: int
    rider_id: int
    efficiency_score: float
    distance_score: float
    batch_score: float
    rating_score: float
    busyness_score: float
    batch_id: Optional[str]
    total_distance_km: float


class BatchAssignmentResult(BaseModel):
    assignments: List[AssignmentResult]
    unassigned_order_ids: List[int]
    total_orders_processed: int


# ── Auth ──────────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    phone: str
    password: str
