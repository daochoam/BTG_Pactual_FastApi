from fastapi import APIRouter, Depends, Request, Body, Path
from app.controllers.auth_decorators import auth_required
from app.controllers.bank_funds_controller import (
    create_bank_funds_controller,
    get_bank_funds_controller,
    update_bank_fund_controller
)
from app.documents.auth_models import SessionUserModel
from app.documents.bank_funds_models import CreateBankFundsModel, UpdateBankFundsModel

bank_funds_routes = APIRouter(prefix="/bank-funds", tags=["bank_funds"])

# CREATE
@bank_funds_routes.post("/", summary="Crear un fondo bancario")
def create_bank_fund(
    request: Request,
    data: CreateBankFundsModel = Body(...),
    user_session: SessionUserModel = Depends(auth_required(require_admin=True))
):
    """Crear un fondo bancario"""
    return create_bank_funds_controller(user_session, data)

# READ ALL
@bank_funds_routes.get("/", summary="Obtener todos los fondos bancarios")
def get_bank_funds():
    """Obtener todos los fondos bancarios"""
    return get_bank_funds_controller()

# READ ONE & UPDATE
@bank_funds_routes.get("/{bank_funds_id}", summary="Obtener todos los fondos bancarios")
def get_bank_fund(bank_funds_id: str = Path(...)):
    """Obtener un fondo bancario por ID"""
    return get_bank_funds_controller(bank_funds_id)

# UPDATE
@bank_funds_routes.put("/{bank_funds_id}", summary="Actualizar un fondo bancario")
def update_bank_fund(
    request: Request,
    bank_funds_id: str = Path(...),
    data: UpdateBankFundsModel = Body(...),
    user_session: SessionUserModel = Depends(auth_required(require_admin=True))
):
    """Actualizar un fondo bancario"""
    return update_bank_fund_controller(user_session, bank_funds_id, data)
