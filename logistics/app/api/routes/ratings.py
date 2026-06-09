from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.schemas import RatingCreate, RatingOut
from app.services.rating_service import submit_rating, get_rider_ratings_summary

router = APIRouter(prefix="/ratings", tags=["Ratings"])


@router.post("/", response_model=RatingOut, status_code=201)
async def rate_order(data: RatingCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await submit_rating(data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rider/{rider_id}", response_model=dict)
async def rider_rating_summary(rider_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await get_rider_ratings_summary(rider_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
