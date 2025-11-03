import datetime
import json
import os
from typing import Annotated, List, Optional

import bcrypt
import jwt
from fastapi import Body, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from pydantic import BaseModel, Field, field_validator, validator

from app.routers import survey, user, vote
from app.schemas.user import User
from app.utils import auth

app = FastAPI()
app.include_router(auth.router)
app.include_router(vote.ruoter)
app.include_router(survey.router)
app.include_router(user.router)

SECRET_KEY = "aisent"


class OptionUpdate(BaseModel):
    votes: Optional[int] = None
    notes: Optional[str] = None


class Option(BaseModel):
    id: Optional[int] = None
    name: str
    votes: int = 0
    notes: str = ""


class Survey(BaseModel):
    name: str
    id: Optional[int] = None
    expires: Optional[str] = None  # store as string
    multiple: bool = False
    active: bool = False
    options: list[Option] = Field(
        default_factory=lambda: [
            Option(name="Apple"),
            Option(name="Banana"),
        ]
    )
    expires: Optional[str] = None  # store as string

    @validator("expires", pre=True, always=True)
    def parse_expires(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime.datetime):
            return v.isoformat()
        # Parse the Z format
        if isinstance(v, str):
            if v.endswith("Z"):
                v = v[:-1] + "+00:00"
            return v
        return v


class SurveyUpdate(BaseModel):
    name: Optional[str] = None
    expires: Optional[str] = None
    multiple: Optional[bool] = None
    active: Optional[bool] = None
    options: Optional[List[OptionUpdate]] = None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione meglio specificare l'origine
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
