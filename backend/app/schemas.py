# app/schemas/orders.py
from pydantic import BaseModel, Field

# For orders

class OrderBase(BaseModel):
    lat: float = Field(..., description="Latitude of the delivery location", ge=-90, le=90)
    lng: float = Field(..., description="Longitude of the delivery location", ge=-180, le=180)

class OrderCreate(OrderBase):
    id: str = Field(..., description="Unique alphanumeric identifier for the order")
    status: str = Field(default="placed", description="Current status: placed, assigned, picked_up, delivered")

class OrderResponse(OrderCreate):
    class Config:
        from_attributes = True

# For riders

class RiderBase(BaseModel):
    lat: float = Field(..., description="Current latitude of the rider", ge=-90, le=90)
    lng: float = Field(..., description="Current longitude of the rider", ge=-180, le=180)

class RiderLocationUpdate(RiderBase):
    id: str = Field(..., description="Unique alphanumeric identifier for the driver")
    status: str = Field(default="idle", description="Current operational status: idle, delivering")

class RiderResponse(RiderLocationUpdate):
    class Config:
        from_attributes = True