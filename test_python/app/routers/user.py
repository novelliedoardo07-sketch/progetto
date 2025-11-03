from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.schemas.user import User, UserCreate  # <-- Input/Output separati
from app.services.user import UserService
from app.utils.auth import get_current_user, hash_password, is_admin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[User])
def get_users():
    return UserService.get_all_users()


@router.get("/{user_id}", response_model=User)
def get_user(user_id: str):  # ID come stringa
    user = UserService.get_user(user_id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


@router.post("/", response_model=User, status_code=201)
def create_user(user: UserCreate):
    # 🔐 Hash password prima di salvare
    user_data = user.model_dump()
    user_data["password"] = hash_password(user.password)
    new_user = UserService.create_user(user_data)
    return new_user


@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: str,
    user: UserCreate,
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id and not is_admin(current_user):
        raise HTTPException(
            status_code=403, detail="Not authorized to update this user"
        )

    user_data = user.model_dump()
    user_data["password"] = hash_password(user.password)  # Rihasha
    updated_user = UserService.update_user(user_id, user_data)
    if updated_user:
        return updated_user
    raise HTTPException(status_code=404, detail="User not found")


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
):
    # Allow if the user is deleting themselves or is an admin
    if current_user.id != user_id and not is_admin(current_user):
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this user"
        )

    success = UserService.delete_user(user_id)
    if success:
        return
    raise HTTPException(status_code=404, detail="User not found")
