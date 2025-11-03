from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    user_level: str = "user"


class UserCreate(UserBase):
    password: str = Field(..., min_length=5)
    age: Optional[int] = None


class User(UserBase):
    id: Optional[int] = None
    age: Optional[int] = None

    class Config:
        orm_mode = True


class LoginModel(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
