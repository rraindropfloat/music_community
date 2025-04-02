from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str
    user_info: dict


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

