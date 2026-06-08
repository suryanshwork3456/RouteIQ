from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth_utils

router = APIRouter(prefix="/api/admin", tags=["Admin Authentication"])

@router.post("/signup", response_model=schemas.AdminResponse, status_code=status.HTTP_201_CREATED)
def signup_admin(admin_data: schemas.AdminCreate, db: Session = Depends(get_db)):
    db_admin = db.query(models.Admin).filter(models.Admin.email == admin_data.email).first()
    if db_admin:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = auth_utils.hash_password(admin_data.password)
    new_admin = models.Admin(name=admin_data.name, email=admin_data.email, hashed_password=hashed_pwd)
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

@router.post("/login", response_model=schemas.TokenResponse)
def login_admin(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.email == login_data.email).first()
    if not admin or not auth_utils.verify_password(login_data.password, admin.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = auth_utils.create_access_token(data={"sub": str(admin.id), "role": "admin"})
    return {"access_token": token, "token_type": "bearer", "role": "admin"}