from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.routers.user import router as user_router
from app.schemas.user import User as UserSchema
from app.utils.auth import get_current_user

app = FastAPI()
app.include_router(user_router)
client = TestClient(app)

# Mock users
mock_user = UserSchema(
    id=1, username="testuser", password="testpass", age=30, user_level="user", vota=""
)

mock_admin = UserSchema(
    id=2, username="admin", password="adminpass", age=40, user_level="admin", vota=""
)


@pytest.fixture
def test_user_payload():
    return {
        "id": 1,
        "username": "testuser",
        "password": "testpass",
        "age": 30,
        "user_level": "user",
        "vota": "",
    }


def test_create_user(test_user_payload):
    response = client.post("/users/", json=test_user_payload)
    assert response.status_code == 201


def test_get_users():
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user():
    response = client.get("/users/1")
    if response.status_code == 200:
        assert "id" in response.json()
    elif response.status_code == 404:
        assert response.json() == {"detail": "User not found"}


def test_update_user_unauthorized(test_user_payload):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    response = client.put("/users/2", json=test_user_payload)
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authorized to update this user"}
    app.dependency_overrides.clear()


def test_update_user_authorized(test_user_payload):
    app.dependency_overrides[get_current_user] = lambda: mock_admin
    response = client.put("/users/1", json=test_user_payload)
    assert response.status_code in [200, 404]
    app.dependency_overrides.clear()


def test_delete_user_unauthorized():
    app.dependency_overrides[get_current_user] = lambda: mock_user
    response = client.delete("/users/2")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authorized to delete this user"}
    app.dependency_overrides.clear()


def test_delete_user_authorized():
    app.dependency_overrides[get_current_user] = lambda: mock_admin
    response = client.delete("/users/1")
    assert response.status_code in [204, 404]
    app.dependency_overrides.clear()
