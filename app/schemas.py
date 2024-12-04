from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class Event(BaseModel):
    idEvent: str
    strEvent: str
    strHomeTeam: str
    strAwayTeam: str
    idHomeTeam: str
    idAwayTeam: str
    dateEvent: str
    strTime: str
    strHomeTeamBadge: Optional[str] = None
    strAwayTeamBadge: Optional[str] = None
    idLeague: str
    idVenue: Optional[str] = None
    strVenue: Optional[str] = None
    clima: dict
    pronostico: str

    class Config:
        orm_mode = True
