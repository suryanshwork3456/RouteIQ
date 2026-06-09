from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    ForeignKey, DateTime, Enum, Text, func
)
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


# ── Enums ─────────────────────────────────────────────────────────────────────

class RiderStatus(str, enum.Enum):
    idle        = "idle"
    en_route    = "en_route"   # heading to supermarket
    delivering  = "delivering" # heading to customer
    maxed_out   = "maxed_out"  # at capacity


class OrderStatus(str, enum.Enum):
    pending    = "pending"
    assigned   = "assigned"
    picked_up  = "picked_up"
    delivered  = "delivered"
    cancelled  = "cancelled"


# ── Models ────────────────────────────────────────────────────────────────────

class Supermarket(Base):
    __tablename__ = "supermarkets"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(150), nullable=False)
    address     = Column(Text)
    lat         = Column(Float, nullable=False)
    lon         = Column(Float, nullable=False)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    orders      = relationship("Order", back_populates="supermarket")


class Rider(Base):
    __tablename__ = "riders"

    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String(100), nullable=False)
    phone           = Column(String(20), unique=True, nullable=False)
    email           = Column(String(150), unique=True)
    hashed_password = Column(String, nullable=False)

    # live location (also mirrored in Redis for speed)
    current_lat     = Column(Float, nullable=True)
    current_lon     = Column(Float, nullable=True)
    location_updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    status          = Column(Enum(RiderStatus), default=RiderStatus.idle)
    max_capacity    = Column(Integer, default=4)   # max simultaneous orders
    is_active       = Column(Boolean, default=True)

    # Rating (rolling average stored for fast reads)
    avg_rating      = Column(Float, default=5.0)
    total_ratings   = Column(Integer, default=0)
    total_deliveries = Column(Integer, default=0)

    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    orders          = relationship("Order", back_populates="rider")
    ratings         = relationship("RiderRating", back_populates="rider")


class Customer(Base):
    __tablename__ = "customers"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)
    phone       = Column(String(20), unique=True, nullable=False)
    email       = Column(String(150), unique=True)
    lat         = Column(Float, nullable=False)
    lon         = Column(Float, nullable=False)
    address     = Column(Text)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    orders      = relationship("Order", back_populates="customer")


class Order(Base):
    __tablename__ = "orders"

    id              = Column(Integer, primary_key=True, index=True)
    customer_id     = Column(Integer, ForeignKey("customers.id"), nullable=False)
    supermarket_id  = Column(Integer, ForeignKey("supermarkets.id"), nullable=False)
    rider_id        = Column(Integer, ForeignKey("riders.id"), nullable=True)

    # delivery location (snapshot at order time)
    delivery_lat    = Column(Float, nullable=False)
    delivery_lon    = Column(Float, nullable=False)
    delivery_address = Column(Text)

    status          = Column(Enum(OrderStatus), default=OrderStatus.pending)
    items_json      = Column(Text)  # JSON string of order items

    # Distances (filled after assignment)
    rider_to_market_km  = Column(Float, nullable=True)
    market_to_customer_km = Column(Float, nullable=True)
    total_distance_km   = Column(Float, nullable=True)

    # Efficiency score at time of assignment
    assignment_score    = Column(Float, nullable=True)

    # Batch info
    batch_id        = Column(String(50), nullable=True, index=True)  # riders sharing batch

    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    assigned_at     = Column(DateTime(timezone=True), nullable=True)
    picked_up_at    = Column(DateTime(timezone=True), nullable=True)
    delivered_at    = Column(DateTime(timezone=True), nullable=True)

    customer        = relationship("Customer", back_populates="orders")
    supermarket     = relationship("Supermarket", back_populates="orders")
    rider           = relationship("Rider", back_populates="orders")
    rating          = relationship("RiderRating", back_populates="order", uselist=False)


class RiderRating(Base):
    __tablename__ = "rider_ratings"

    id          = Column(Integer, primary_key=True, index=True)
    rider_id    = Column(Integer, ForeignKey("riders.id"), nullable=False)
    order_id    = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    stars       = Column(Float, nullable=False)  # 1.0 – 5.0
    comment     = Column(Text, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    rider       = relationship("Rider", back_populates="ratings")
    order       = relationship("Order", back_populates="rating")
