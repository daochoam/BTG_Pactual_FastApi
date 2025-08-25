# app/routes/auth_ns.py
from fastapi import APIRouter, Header
from app.controllers.auth_controller import register_user, login_user, logout_user
from app.documents.auth_models import RegisterUserModel, LoginUserModel


auth_routes = APIRouter(prefix="/auth", tags=["auth"])

@auth_routes.post('/register')
def register(data: RegisterUserModel):
    response = register_user(data)
    return response

@auth_routes.post('/login')
def login(data: LoginUserModel):
    return login_user(data)


@auth_routes.post('/logout')
def logout(
    authorization: str = Header(None, alias="Authorization"),
    refresh_token: str = Header(None, alias="X-Refresh-Token")
):
    return logout_user(authorization, refresh_token)

