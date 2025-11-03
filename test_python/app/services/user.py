import json
import os

from app.models.user import UserModel
from app.utils.auth import hash_password

STORAGE_PATH = "./storage/user.json"


class UserService:
    @staticmethod
    def _load_data():
        if not os.path.exists(STORAGE_PATH):
            return {}
        with open(STORAGE_PATH, "r") as f:
            try:
                data = json.load(f)
                if not isinstance(data, dict):
                    return {}
                return data
            except json.JSONDecodeError:
                return {}

    @staticmethod
    def _save_data(data: dict):
        with open(STORAGE_PATH, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def get_user(user_id: int):
        data = UserService._load_data()
        return data.get(str(user_id))

    @staticmethod
    def get_all_users():
        data = UserService._load_data()
        return list(data.values())

    @staticmethod
    def create_user(user_model: dict):
        data = UserService._load_data()
        if data:
            max_id = max(int(uid) for uid in data.keys())
            next_id = max_id + 1
        else:
            next_id = 1

        user_model["id"] = next_id

        # Se la password è già hashata, salvala così
        # altrimenti hashala qui, se serve
        # user_model["password"] = hash_password(user_model["password"])

        data[str(next_id)] = user_model
        UserService._save_data(data)
        return user_model

    @staticmethod
    def update_user(user_id: int, update_model: dict):
        data = UserService._load_data()
        user = data.get(str(user_id))
        if not user:
            return None

        # Non permettere di modificare l'id
        if "id" in update_model:
            del update_model["id"]

        # Se la password viene modificata, hashala (opzionale)
        if "password" in update_model:
            update_model["password"] = hash_password(update_model["password"])

        user.update(update_model)
        data[str(user_id)] = user
        UserService._save_data(data)
        return user

    @staticmethod
    def delete_user(user_id: int) -> bool:
        data = UserService._load_data()
        user_id_str = str(user_id)

        if user_id_str not in data:
            return False

        del data[user_id_str]
        UserService._save_data(data)
        return True
