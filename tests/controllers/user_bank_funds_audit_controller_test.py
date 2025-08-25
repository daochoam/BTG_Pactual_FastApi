import pytest
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse

from app.controllers.user_bank_funds_audit_controller import (
    get_user_bank_funds_audit_controller,
)
from app.documents.auth_models import SessionUserModel


class DummyAuditDB:
    """Fake DB for user_bank_funds_audit."""
    def __init__(self):
        self.items = []

    def scan(self, **kwargs):
        # simulamos filter con user_id
        uid = kwargs["ExpressionAttributeValues"][":uid"]
        filtered = [item for item in self.items if item["user_id"] == uid]
        return {"Items": filtered}


@pytest.fixture
def mock_user():
    return SessionUserModel(user_id="user-123")


@pytest.fixture
def mock_db(monkeypatch):
    dummy = DummyAuditDB()
    import app.schemas.user_bank_funds_audit as audit
    monkeypatch.setattr(audit, "user_bank_funds_audit_db", dummy)
    return dummy


def test_get_user_audits_success(mock_user, mock_db):
    mock_db.items = [
        {"id": "a1", "user_id": "user-123", "created_at": "2025-01-01"},
        {"id": "a2", "user_id": "user-123", "created_at": "2025-01-02"},
        {"id": "a3", "user_id": "other", "created_at": "2025-01-03"},
    ]
    response: JSONResponse = get_user_bank_funds_audit_controller(mock_user)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["detail"] == "User bank funds audit retrieved successfully"
    assert len(body["data"]) == 2
    # check ordering desc
    assert body["data"][0]["created_at"] == "2025-01-02"


def test_get_user_audit_by_id_found(mock_user, mock_db):
    mock_db.items = [
        {"id": "a1", "user_id": "user-123", "created_at": "2025-01-01"},
    ]
    response: JSONResponse = get_user_bank_funds_audit_controller(mock_user, "a1")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["data"][0]["id"] == "a1"


def test_get_user_audit_by_id_not_found(mock_user, mock_db):
    mock_db.items = [
        {"id": "a1", "user_id": "user-123", "created_at": "2025-01-01"},
    ]
    with pytest.raises(HTTPException) as e:
        get_user_bank_funds_audit_controller(mock_user, "does-not-exist")

    assert e.value.status_code == status.HTTP_404_NOT_FOUND
    assert e.value.detail == "User bank funds audit not found"


def test_get_user_audits_empty(mock_user, mock_db):
    mock_db.items = []
    response: JSONResponse = get_user_bank_funds_audit_controller(mock_user)
    body = response.json()
    assert body["data"] == []
