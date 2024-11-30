from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate
from passlib.hash import bcrypt

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    password = bcrypt.hash(user.password)
    db_user = User(email=user.email, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"result": "success"}
