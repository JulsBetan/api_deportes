from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserCreate, UserOut
from app.crud import create_user, get_user_by_email
from app.auth import create_access_token, authenticate_user

from pydantic import BaseModel

class RegisterResponse(BaseModel):
    result: str

router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        
        if get_user_by_email(db, user.email):
            # raise HTTPException(status_code=400, detail="Email already registered")
            return {"result": "Email previamente registrado"}

        else:
            return create_user(db, user)
    except Exception as e:
        print(e)
        return {"result": "error", "detail": "Error al registrar Email"}

@router.post("/login")
def login_user(email: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
