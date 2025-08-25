# tests/test_auth_decorators.py
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException, status
from fastapi.requests import Request

from app.controllers.auth_decorators import validate_tokens, get_auth_payload, auth_required
from app.documents.auth_models import SessionUserModel

# Mock de usuario retornado por Cognito
mock_user_attributes = [
    {"Name": "sub", "Value": "user123"},
    {"Name": "custom:role", "Value": "ADMIN"}  # Mayúsculas
]

@pytest.fixture
def mock_request():
    request = MagicMock(spec=Request)
    request.headers = {
        "Authorization": "Bearer validtoken",
        "X-Refresh-Token": "validrefreshtoken"
    }
    return request

@patch("app.controllers.auth_decorators.cognito_client")
def test_validate_tokens_success(mock_cognito):
    mock_cognito.get_user.return_value = {"UserAttributes": mock_user_attributes}
    payload = validate_tokens("Bearer validtoken", "validrefreshtoken")
    assert payload["user_id"] == "user123"
    assert payload["role"] == "ADMIN"

@patch("app.controllers.auth_decorators.cognito_client")
def test_validate_tokens_refresh_token(mock_cognito):
    # Definir excepción real
    class NotAuthorizedException(Exception):
        pass

    # Asignar excepción al mock
    mock_cognito.exceptions = MagicMock()
    mock_cognito.exceptions.NotAuthorizedException = NotAuthorizedException

    # Simular get_user
    def get_user_side_effect(AccessToken):
        if AccessToken == "invalidtoken":
            raise NotAuthorizedException()
        return {"UserAttributes": mock_user_attributes}

    mock_cognito.get_user.side_effect = get_user_side_effect

    # Simular initiate_auth
    mock_cognito.initiate_auth.return_value = {
        "AuthenticationResult": {"AccessToken": "newtoken"}
    }

    # Ejecutar función
    payload = validate_tokens("Bearer invalidtoken", "validrefreshtoken")
    assert payload["user_id"] == "user123"
    assert payload["role"] == "ADMIN"


def test_validate_tokens_missing_access():
    with pytest.raises(HTTPException) as exc:
        validate_tokens(None, "some_refresh")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Token requerido" in exc.value.detail

def test_validate_tokens_missing_refresh():
    with pytest.raises(HTTPException) as exc:
        validate_tokens("Bearer token", None)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Refresh token requerido" in exc.value.detail

@patch("app.controllers.auth_decorators.get_auth_payload")
def test_auth_required_decorator_admin(mock_get_payload):
    mock_get_payload.return_value = {"user_id": "user123", "role": "ADMIN"}
    dependency = auth_required(require_admin=True)
    request = MagicMock()
    user = dependency(request)
    assert isinstance(user, SessionUserModel)
    assert user.user_id == "user123"
    assert user.role == "ADMIN"

@patch("app.controllers.auth_decorators.get_auth_payload")
def test_auth_required_decorator_non_admin(mock_get_payload):
    mock_get_payload.return_value = {"user_id": "user123", "role": "USER"}
    dependency = auth_required(require_admin=True)
    request = MagicMock()
    with pytest.raises(HTTPException) as exc:
        dependency(request)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Acceso denegado" in exc.value.detail

@patch("app.controllers.auth_decorators.get_auth_payload")
def test_auth_required_decorator_no_admin_required(mock_get_payload):
    mock_get_payload.return_value = {"user_id": "user123", "role": "USER"}
    dependency = auth_required(require_admin=False)
    request = MagicMock()
    user = dependency(request)
    assert isinstance(user, SessionUserModel)
    assert user.user_id == "user123"
    assert user.role == "USER"
