"""Auth routes: register and login."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from src.core.database import get_db
from src.core.security import hash_password, verify_password
from src.data.models.users import Users

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(Users).filter(Users.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = Users(email=body.email, password=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return AuthResponse(id=user.id, email=user.email)


@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.email == body.email).first()
    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return AuthResponse(id=user.id, email=user.email)
