from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt

from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserCreate, UserOut
from app.crud import create_user, get_user_by_email
from app.auth import create_access_token, authenticate_user 
from app.config import get_settings 

from pydantic import BaseModel


settings = get_settings()

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

class RegisterResponse(BaseModel):
    result: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

class TokenRequest(BaseModel):
    token: str

router = APIRouter()

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Devuelve el contenido del token si es válido
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/validate-token")
def validate_token(request: TokenRequest):
    token = request.token
    try:
        verify_token(token)  # Implementa esta función para validar el token
        return {"valid": True}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

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

@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User Login",
    description="Authenticate a user and return an access token."
)
def login_user(login_request: LoginRequest, db: Session = Depends(get_db)):
    email = login_request.email
    password = login_request.password

    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
