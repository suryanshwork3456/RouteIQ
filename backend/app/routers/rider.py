from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth_utils

router = APIRouter(prefix="/api/rider", tags=["Rider Authentication"])

@router.post("/signup", response_model=schemas.RiderResponse, status_code=status.HTTP_201_CREATED)
def signup_rider(rider_data: schemas.RiderCreate, db: Session = Depends(get_db)):
    db_rider = db.query(models.Rider).filter(models.Rider.email == rider_data.email).first()
    if db_rider:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = auth_utils.hash_password(rider_data.password)
    new_rider = models.Rider(
        name=rider_data.name, 
        email=rider_data.email, 
        hashed_password=hashed_pwd,
        vehicle_type=rider_data.vehicle_type
    )
    
    db.add(new_rider)
    db.commit()
    db.refresh(new_rider)
    return new_rider

@router.post("/login", response_model=schemas.TokenResponse)
def login_rider(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    rider = db.query(models.Rider).filter(models.Rider.email == login_data.email).first()
    if not rider or not auth_utils.verify_password(login_data.password, rider.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = auth_utils.create_access_token(data={"sub": str(rider.id), "role": "rider"})
    return {"access_token": token, "token_type": "bearer", "role": "rider"}