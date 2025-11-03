from typing import Optional

from pydantic import BaseModel


class UserModel(BaseModel):

    username: str
    password: str
    age: int = 0
    user_level: str = "user"
