from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import Rider
from app.schemas.schemas import RiderCreate, RiderOut, Token, LoginRequest
from app.core.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=RiderOut, status_code=201)
async def register_rider(data: RiderCreate, db: AsyncSession = Depends(get_db)):
    # Check phone uniqueness
    existing = await db.execute(select(Rider).where(Rider.phone == data.phone))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Phone already registered")

    rider = Rider(
        name=data.name,
        phone=data.phone,
        email=data.email,
        hashed_password=hash_password(data.password),
        max_capacity=data.max_capacity,
    )
    db.add(rider)
    await db.commit()
    await db.refresh(rider)
    return rider


@router.post("/login", response_model=Token)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Rider).where(Rider.phone == data.phone))
    rider: Rider = result.scalar_one_or_none()

    if not rider or not verify_password(data.password, rider.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone or password",
        )
    if not rider.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    token = create_access_token({"sub": str(rider.id)})
    return Token(access_token=token)
