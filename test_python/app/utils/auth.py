import base64
import binascii
import datetime
import json
import os
from typing import Annotated, Optional

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError

from app.schemas.user import User

# === Config ===
SECRET_KEY = "aisent"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 1
DATA_FILE = "./storage/user.json"

# === FastAPI Auth Setup ===
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()


# === JWT Access Token Creation ===
def create_access_token(
    data: dict, expires_delta: Optional[datetime.timedelta] = None
) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (
        expires_delta or datetime.timedelta(hours=TOKEN_EXPIRE_HOURS)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# === Password Hashing ===
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return base64.b64encode(hashed).decode("utf-8")


# === Password Verification ===
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        hashed_bytes = base64.b64decode(hashed_password.encode("utf-8"))
    except binascii.Error:
        hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_bytes)


# === Get current user from token ===
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        user_level = payload.get("user_level")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    if not os.path.exists(DATA_FILE):
        raise credentials_exception

    with open(DATA_FILE, "r") as f:
        users = json.load(f)

    user_data = users.get(str(user_id))
    if not user_data:
        raise credentials_exception

    # Add user_level from token if missing in user data
    if user_level and "user_level" not in user_data:
        user_data["user_level"] = user_level

    return User(**user_data)


# === Admin Checker ===
def is_admin(user: User) -> bool:
    return user.user_level == "admin"


# === LOGIN Endpoint ===
@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=500, detail="User data file missing")

    with open(DATA_FILE, "r") as f:
        users = json.load(f)

    user = next(
        (u for u in users.values() if u["username"] == form_data.username), None
    )

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ✅ Add user_level to token
    token_data = {"id": user["id"], "user_level": user.get("user_level", "user")}
    access_token = create_access_token(data=token_data)

    return {"access_token": access_token, "token_type": "bearer"}
