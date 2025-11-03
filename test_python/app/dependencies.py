import json
import os
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError

from app.schemas.user import User

DATA_FILE = "./storage/user.json"
SECRET_KEY = "aisent"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: int = payload.get("id")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    if not os.path.exists(DATA_FILE):
        raise credentials_exception

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    user_data = data.get(str(user_id))
    if not user_data:
        raise credentials_exception

    return User(**user_data)


def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.user_level != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action",
        )
    return user
