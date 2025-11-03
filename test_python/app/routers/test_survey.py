import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.dependencies import get_current_user
from app.routers import survey as survey_router
from app.schemas.user import User

# Crea l’app di test
app = FastAPI()
app.include_router(survey_router.router)
client = TestClient(app)

# Utente amministratore mock per bypassare controllo is_admin
mock_admin = User(
    id=1, username="admin", password="adminpass", age=40, user_level="admin", vota=""
)


# Override della dipendenza get_current_user
@pytest.fixture(autouse=True)
def override_current_user():
    app.dependency_overrides[get_current_user] = lambda: mock_admin
    yield
    app.dependency_overrides.clear()


# ==================== Payload di test ====================
# Questi payload devono corrispondere ai tuoi modelli Pydantic per la richiesta (POST/PUT)
survey_create_payload = {
    "name": "Survey Title",
    "expires": "2025-12-31T23:59:59+00:00",
    "multiple": False,
    "active": False,
    "options": [{"name": "Option 1", "notes": ""}],
}

survey_update_payload = {
    "name": "Survey Title Updated",
    "expires": "2026-01-31T23:59:59+00:00",
    "multiple": True,
    "active": True,
    "options": [{"notes": "Updated notes"}],  # Optional, depending on your update logic
}

option_create_payload = {"name": "Option text", "notes": ""}

option_update_payload = {"votes": 10, "notes": "Updated option notes"}

# ==================== Mock risposte che corrispondono ai response_model ====================
mock_survey_response = {
    "id": 1,
    "name": "Survey Title",
    "expires": "2025-12-31T23:59:59+00:00",
    "multiple": False,
    "active": False,
    "options": [{"id": 1, "name": "Option 1", "notes": ""}],
}

mock_survey_updated_response = {
    "id": 1,
    "name": "Survey Title Updated",
    "expires": "2026-01-31T23:59:59+00:00",
    "multiple": True,
    "active": True,
    "options": [{"id": 1, "name": "Option 1", "notes": "Updated notes"}],
}

mock_option_response = {"id": 1, "name": "Option text", "notes": ""}

mock_option_updated_response = {
    "id": 1,
    "name": "Option text",
    "votes": 10,
    "notes": "Updated option notes",
}

# ==================== Test ====================


def test_get_active_surveys_none(monkeypatch):
    monkeypatch.setattr(survey_router.survey_service, "get_active_surveys", lambda: [])
    response = client.get("/survey/")
    assert response.status_code == 404
    assert response.json() == {"detail": "No active surveys found"}


def test_get_active_surveys_success(monkeypatch):
    monkeypatch.setattr(
        survey_router.survey_service,
        "get_active_surveys",
        lambda: [mock_survey_response],
    )
    response = client.get("/survey/")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert body[0]["id"] == mock_survey_response["id"]


def test_get_all_surveys(monkeypatch):
    monkeypatch.setattr(
        survey_router.survey_service, "get_all_surveys", lambda: [mock_survey_response]
    )
    response = client.get("/survey/all")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert body[0]["id"] == mock_survey_response["id"]


def test_get_survey_by_id_found(monkeypatch):
    monkeypatch.setattr(
        survey_router.survey_service,
        "get_survey_by_id",
        lambda _id: mock_survey_response,
    )
    response = client.get("/survey/1")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == mock_survey_response["id"]


def test_get_survey_by_id_not_found(monkeypatch):
    monkeypatch.setattr(
        survey_router.survey_service, "get_survey_by_id", lambda _id: None
    )
    response = client.get("/survey/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Survey not found"}


def test_create_survey(monkeypatch):
    monkeypatch.setattr(
        survey_router.survey_service, "create_survey", lambda s: mock_survey_response
    )
    response = client.post("/survey/", json=survey_create_payload)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == mock_survey_response["id"]
    assert body["name"] == mock_survey_response["name"]


def test_update_survey_success(monkeypatch):
    monkeypatch.setattr(
        survey_router.survey_service,
        "update_survey",
        lambda _id, upd: mock_survey_updated_response,
    )
    response = client.put("/survey/1", json=survey_update_payload)
    assert response.status_code == 200
    body = response.json()
    assert "updated successfully" in body["message"]
    assert body["survey"]["name"] == mock_survey_updated_response["name"]


def test_update_survey_not_found(monkeypatch):
    monkeypatch.setattr(
        survey_router.survey_service, "update_survey", lambda _id, upd: None
    )
    response = client.put("/survey/999", json=survey_update_payload)
    assert response.status_code == 404
    assert response.json() == {"detail": "Survey not found"}


def test_delete_survey_success(monkeypatch):
    monkeypatch.setattr(survey_router.survey_service, "delete_survey", lambda _id: True)
    response = client.delete("/survey/1")
    assert response.status_code == 200
    body = response.json()
    assert "deleted successfully" in body["message"]


def test_delete_survey_not_found(monkeypatch):
    monkeypatch.setattr(
        survey_router.survey_service, "delete_survey", lambda _id: False
    )
    response = client.delete("/survey/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Survey not found"}


def test_activate_survey_success(monkeypatch):
    monkeypatch.setattr(
        survey_router.survey_service, "activate_survey", lambda _id: True
    )
    response = client.post("/survey/1/activate")
    assert response.status_code == 200
    body = response.json()
    assert "activated successfully" in body["message"]


def test_activate_survey_not_found(monkeypatch):
    monkeypatch.setattr(
        survey_router.survey_service, "activate_survey", lambda _id: False
    )
    response = client.post("/survey/999/activate")
    assert response.status_code == 404
    assert response.json() == {"detail": "Survey not found"}


def test_get_options_success(monkeypatch):
    monkeypatch.setattr(
        survey_router.survey_service, "get_options", lambda _id: [mock_option_response]
    )
    response = client.get("/survey/1/option")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert body[0]["id"] == mock_option_response["id"]


def test_get_options_not_found(monkeypatch):
    monkeypatch.setattr(survey_router.survey_service, "get_options", lambda _id: None)
    response = client.get("/survey/999/option")
    assert response.status_code == 404
    assert response.json() == {"detail": "Survey not found"}


def test_add_option_success(monkeypatch):
    monkeypatch.setattr(
        survey_router.survey_service,
        "add_option",
        lambda _id, opt: mock_option_response,
    )
    response = client.post("/survey/1/option", json=option_create_payload)
    assert response.status_code == 200
    body = response.json()
    assert body["option"]["id"] == mock_option_response["id"]
    assert body["option"]["name"] == mock_option_response["name"]


def test_add_option_not_found(monkeypatch):
    monkeypatch.setattr(
        survey_router.survey_service, "add_option", lambda _id, opt: None
    )
    response = client.post("/survey/999/option", json=option_create_payload)
    assert response.status_code == 404
    assert response.json() == {"detail": "Survey not found"}


def test_update_option_success(monkeypatch):
    monkeypatch.setattr(
        survey_router.survey_service,
        "update_option",
        lambda sid, oid, upd: mock_option_updated_response,
    )
    response = client.put("/survey/1/option/1", json=option_update_payload)
    assert response.status_code == 200
    body = response.json()
    assert body["option"]["votes"] == mock_option_updated_response.get("votes")
    assert body["option"]["notes"] == mock_option_updated_response.get("notes")


def test_update_option_not_found(monkeypatch):
    monkeypatch.setattr(
        survey_router.survey_service, "update_option", lambda sid, oid, upd: None
    )
    response = client.put("/survey/999/option/999", json=option_update_payload)
    assert response.status_code == 404
    assert response.json() == {"detail": "Option or survey not found"}


def test_delete_option_success(monkeypatch):
    monkeypatch.setattr(
        survey_router.survey_service, "delete_option", lambda sid, oid: True
    )
    response = client.delete("/survey/1/option/1")
    assert response.status_code == 200
    body = response.json()
    assert "deleted" in body["message"]


def test_delete_option_not_found(monkeypatch):
    monkeypatch.setattr(
        survey_router.survey_service, "delete_option", lambda sid, oid: False
    )
    response = client.delete("/survey/999/option/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Option or survey not found"}
