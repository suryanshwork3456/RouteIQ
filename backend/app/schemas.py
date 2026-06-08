from pydantic import BaseModel, Field
from pydantic import BaseModel, EmailStr
from typing import Optional

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

# Base Schemas
class AdminBase(BaseModel):
    name: str
    email: EmailStr

class RiderBase(BaseModel):
    name: str
    email: EmailStr
    vehicle_type: str

# Create (Signup) Schemas
class AdminCreate(AdminBase):
    password: str

class RiderCreate(RiderBase):
    password: str

# Response (Out) Schemas
class AdminResponse(AdminBase):
    id: int
    role: str
    
    class Config:
        from_attributes = True

class RiderResponse(RiderBase):
    id: int
    is_available: bool

    class Config:
        from_attributes = True

# Login Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str