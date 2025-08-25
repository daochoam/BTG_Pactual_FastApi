from fastapi import APIRouter, Depends, Path
from app.controllers.auth_decorators import auth_required
from app.controllers.user_bank_funds_audit_controller import (
    get_user_bank_funds_audit_controller,
)
from app.documents.auth_models import SessionUserModel

user_bank_funds_audit_routes = APIRouter(prefix="/user-bank-funds-audit", tags=["user_bank_funds_audit"])

# READ ALL
@user_bank_funds_audit_routes.get("/", summary="Obtener todos los registros de auditoría de fondos bancarios por usuario")
def get_user_bank_funds_audit_list(
    user_session: SessionUserModel = Depends(auth_required())
):
    return get_user_bank_funds_audit_controller(user_session)

# READ ONE
@user_bank_funds_audit_routes.get("/{user_bank_funds_audit_id}", summary="Obtener un registro de auditoría por ID")
def get_user_bank_fund_audit(
    user_bank_funds_audit_id: str = Path(..., description="ID del registro de auditoría"),
    user_session: SessionUserModel = Depends(auth_required())
):
    return get_user_bank_funds_audit_controller(user_session, user_bank_funds_audit_id)
