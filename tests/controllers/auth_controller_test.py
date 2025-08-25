import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from app.controllers.auth_controller import register_user, login_user, logout_user
from app.schemas.users import UserSchema
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def fake_register_data():
    return type("RegisterUserModel", (), {
        "nit": "123",
        "name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password": "Test123!",
        "phone": "+573001112233",
        "role": None
    })()


@pytest.fixture
def fake_login_data():
    return type("LoginUserModel", (), {
        "email": "john@example.com",
        "password": "Test123!"
    })()


### --------------------------
### register_user tests
### --------------------------
def test_register_user_success(fake_register_data):
    with patch("app.controllers.auth_controller.users_db") as mock_db, \
         patch("app.controllers.auth_controller.cognito_client") as mock_cognito, \
         patch("app.controllers.auth_controller.get_secret_hash", return_value="fakehash"):

        # Simular que no existe usuario previo
        mock_db.scan.return_value = {"Items": []}
        # Simular cognito sign_up
        mock_cognito.sign_up.return_value = {"UserSub": "fake-user-id"}

        response = register_user(fake_register_data)

        assert response["status"] == status.HTTP_201_CREATED
        assert response["items"]["user_id"] == "fake-user-id"
        mock_db.put_item.assert_called_once()


def test_register_user_already_exists(fake_register_data):
    with patch("app.controllers.auth_controller.users_db") as mock_db:
        mock_db.scan.return_value = {"Items": [{"email": "john@example.com"}]}

        with pytest.raises(HTTPException) as exc:
            register_user(fake_register_data)

        assert exc.value.status_code == 400
        assert "NIT or Email already registered" in str(exc.value.detail)


### --------------------------
### login_user tests
### --------------------------
def test_login_user_success(fake_login_data):
    with patch("app.controllers.auth_controller.users_db") as mock_db, \
         patch("app.controllers.auth_controller.cognito_client") as mock_cognito, \
         patch("app.controllers.auth_controller.get_secret_hash", return_value="fakehash"):

        # Simular que el usuario existe y está verificado
        mock_db.scan.return_value = {"Items": [{"email": "john@example.com", "verified": True}]}

        mock_cognito.initiate_auth.return_value = {
            "AuthenticationResult": {
                "AccessToken": "fake-access",
                "RefreshToken": "fake-refresh"
            }
        }
        mock_cognito.get_user.return_value = {
            "UserAttributes": [
                {"Name": "sub", "Value": "fake-sub"},
                {"Name": "custom:role", "Value": "USER"}
            ]
        }

        response = login_user(fake_login_data)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        assert response.headers["Authorization"] == "Bearer fake-access"
        assert response.headers["X-Refresh-Token"] == "fake-refresh"


def test_login_user_not_found(fake_login_data):
    with patch("app.controllers.auth_controller.users_db") as mock_db:
        mock_db.scan.return_value = {"Items": []}

        with pytest.raises(HTTPException) as exc:
            login_user(fake_login_data)

        assert exc.value.status_code == 404


def test_login_user_not_verified(fake_login_data):
    with patch("app.controllers.auth_controller.users_db") as mock_db:
        mock_db.scan.return_value = {"Items": [{"email": "john@example.com", "verified": False}]}

        with pytest.raises(HTTPException) as exc:
            login_user(fake_login_data)

        assert exc.value.status_code == 401


### --------------------------
### logout_user tests
### --------------------------
def test_logout_user_success_client():
    response = client.post("/api/auth/logout", headers={
        "Authorization": "Bearer fake-access",
        "X-Refresh-Token": "fake-refresh"
    })
    assert response.status_code == 200
    assert response.json()["detail"] == "Logout successful"



def test_logout_user_missing_tokens():
    with pytest.raises(HTTPException) as exc:
        logout_user("", "fake-refresh")
    assert exc.value.status_code == 401

    with pytest.raises(HTTPException) as exc:
        logout_user("Bearer fake-access", "")
    assert exc.value.status_code == 401

