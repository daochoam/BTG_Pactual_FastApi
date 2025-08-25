# app/controllers/auth_decorators.py
from fastapi import Request, HTTPException, status
from app.config import Config, cognito_client
from app.documents.auth_models import SessionUserModel

def validate_tokens(access_header, refresh_token):
    if not access_header or not access_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token requerido")

    access_token = access_header.split(" ")[1]

    try:
        user_info = cognito_client.get_user(AccessToken=access_token)
        attributes = {attr["Name"]: attr["Value"] for attr in user_info["UserAttributes"]}
    except cognito_client.exceptions.NotAuthorizedException:
        try:
            response = cognito_client.initiate_auth(
                ClientId=Config.AWS_COGNITO_CLIENT_ID,
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters={"REFRESH_TOKEN": refresh_token}
            )
            access_token = response["AuthenticationResult"]["AccessToken"]
            refresh_token = response["AuthenticationResult"].get("RefreshToken", refresh_token)
            user_info = cognito_client.get_user(AccessToken=access_token)
            attributes = {attr["Name"]: attr["Value"] for attr in user_info["UserAttributes"]}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token inválido o refresh token expirado: {str(e)}")

    payload = {
        "user_id": attributes.get("sub"),
        "role": attributes.get("custom:role"),
    }
    return payload

def get_auth_payload(request: Request):
    access_header = request.headers.get("Authorization")
    refresh_token = request.headers.get("X-Refresh-Token")
    return validate_tokens(access_header, refresh_token)

def auth_required(require_admin: bool = False):
    def dependency(request: Request):
        payload = get_auth_payload(request)
        if require_admin and payload.get("role", "").lower() != "admin":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acceso denegado")
        return SessionUserModel(**payload)
    return dependency
