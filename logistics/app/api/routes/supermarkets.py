from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from app.models.models import Supermarket
from app.schemas.schemas import SupermarketCreate, SupermarketOut

router = APIRouter(prefix="/supermarkets", tags=["Supermarkets"])


@router.post("/", response_model=SupermarketOut, status_code=201)
async def create_supermarket(data: SupermarketCreate, db: AsyncSession = Depends(get_db)):
    sm = Supermarket(**data.model_dump())
    db.add(sm)
    await db.commit()
    await db.refresh(sm)
    return sm


@router.get("/", response_model=List[SupermarketOut])
async def list_supermarkets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supermarket).where(Supermarket.is_active == True))
    return result.scalars().all()


@router.get("/{sm_id}", response_model=SupermarketOut)
async def get_supermarket(sm_id: int, db: AsyncSession = Depends(get_db)):
    sm = await db.get(Supermarket, sm_id)
    if not sm:
        raise HTTPException(status_code=404, detail="Supermarket not found")
    return sm


@router.delete("/{sm_id}", response_model=dict)
async def deactivate_supermarket(sm_id: int, db: AsyncSession = Depends(get_db)):
    sm = await db.get(Supermarket, sm_id)
    if not sm:
        raise HTTPException(status_code=404, detail="Supermarket not found")
    sm.is_active = False
    await db.commit()
    return {"status": "deactivated", "id": sm_id}
