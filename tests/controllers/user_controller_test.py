# tests/test_users_controller.py
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException, status

from app.controllers.user_controller import get_all_users_controller
from app.documents.auth_models import SessionUserModel

# Mock de datos de usuarios
mock_users = [
    {"id": "user1", "name": "Alice", "email": "alice@test.com"},
    {"id": "user2", "name": "Bob", "email": "bob@test.com"},
]

@pytest.fixture
def mock_scan():
    with patch("app.schemas.users.users_db.scan") as mock_scan_func:
        yield mock_scan_func

def test_get_all_users_no_session(mock_scan):
    # Escenario: sin sesión, devuelve todos los usuarios
    mock_scan.return_value = {"Items": mock_users}
    response = get_all_users_controller()
    assert response.status_code == status.HTTP_200_OK
    assert response.body
    data = response.body.decode()
    assert "Alice" in data and "Bob" in data

def test_get_all_users_with_valid_session(mock_scan):
    # Escenario: con sesión válida, devuelve solo ese usuario
    mock_scan.return_value = {"Items": mock_users}
    session = SessionUserModel(user_id="user1")
    response = get_all_users_controller(user_session=session)
    assert response.status_code == status.HTTP_200_OK
    data = response.body.decode()
    assert "Alice" in data
    assert "Bob" not in data

def test_get_all_users_with_invalid_session(mock_scan):
    # Escenario: sesión no existente -> lanza HTTPException
    mock_scan.return_value = {"Items": mock_users}
    session = SessionUserModel(user_id="user3")
    with pytest.raises(HTTPException) as exc:
        get_all_users_controller(user_session=session)
    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"
