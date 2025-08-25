from fastapi import APIRouter, Depends, HTTPException, Path
from app.controllers.auth_decorators import auth_required
from app.controllers.user_bank_funds_controller import (
    create_user_bank_fund_controller,
    get_user_bank_funds_controller,
    delete_user_bank_fund_controller
)
from app.documents.auth_models import SessionUserModel

user_bank_funds_routes = APIRouter(prefix="/user-bank-funds",tags=["user_bank_funds"])

# CREATE
@user_bank_funds_routes.post("/{bank_funds_id}", summary="Asociar un fondo bancario a un usuario")
def create_user_bank_fund(
    user_session: SessionUserModel = Depends(auth_required()),
    bank_funds_id: str = Path(..., description="ID del fondo bancario"),
):
    return create_user_bank_fund_controller(user_session, bank_funds_id)

# READ ALL
@user_bank_funds_routes.get("/", summary="Obtener todos los fondos bancarios de un usuario")
def list_user_bank_funds(
    user_session: SessionUserModel = Depends(auth_required())
):
    return get_user_bank_funds_controller(user_session)

# READ ONE
@user_bank_funds_routes.get("/{id}", summary="Obtener un fondo bancario de un usuario por ID")
def get_user_bank_fund(
    user_session: SessionUserModel = Depends(auth_required()),
    id: str = Path(..., description="ID del fondo bancario"),
):
    return get_user_bank_funds_controller(user_session, id)

# DELETE
@user_bank_funds_routes.delete("/{user_bank_funds_id}", summary="Eliminar un fondo bancario asociado a un usuario")
def delete_user_bank_fund(
    user_session: SessionUserModel = Depends(auth_required()),
    user_bank_funds_id: str = Path(..., description="ID de la relación usuario-fondo bancario"),
):
    response = delete_user_bank_fund_controller(user_session, user_bank_funds_id)
    if [200, 201] not in response.get("status"):
        raise HTTPException(status_code=response.get("status"), detail=response.get("error"))
