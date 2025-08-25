from decimal import Decimal
from fastapi import status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.documents.auth_models import SessionUserModel
from app.utils.send_email import send_insufficient_funds_email, send_retired_funds_email, send_subscription_funds_email
from app.utils.time import get_current_time

import app.schemas.users as users
import app.schemas.bank_funds as bankFunds
import app.schemas.user_bank_funds as userBankFunds
import app.schemas.user_bank_funds_audit as userBankFundsAudit

# CREATE
def create_user_bank_fund_controller(user_session:SessionUserModel, bank_funds_id:str):
    # Buscar el usuario en la tabla de usuarios
    user_response = users.users_db.get_item(Key={"id": user_session.user_id})
    user = user_response.get("Item")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verificar que el BankFund existe
    bf_response = bankFunds.bank_funds_db.get_item(Key={"id": bank_funds_id})
    bank_fund = bf_response.get("Item")
    if not bank_fund:
        raise HTTPException(status_code=404, detail="BankFund not found")

    # Validar saldo disponible
    user_amount = Decimal(user.get("amount", "0"))
    min_amount = Decimal(bank_fund["min_amount"])

    if user_amount < min_amount:
        send_insufficient_funds_email(
            to_email=user.get("email"),
            user_name=user.get("name"),
            bank_fund=bank_fund
        )
        raise HTTPException(status_code=400, detail=f"No tiene saldo disponible para vincularse al fondo {bank_fund['name']}")

    # Actualizar saldo del usuario
    new_amount = user_amount - min_amount
    users.users_db.update_item(
        Key={"id": user['id']},
        UpdateExpression="SET amount = :a, updated_at = :u",
        ExpressionAttributeValues={
            ":a": new_amount,
            ":u": get_current_time()
        }
    )

    # Crear relación user-bankfund y su auditoría
    user_bank_funds = userBankFunds.UserBankFundsSchema(
        user_id=user['id'],
        bank_fund_id=bank_funds_id,
        amount=min_amount,
        currency=bank_fund["currency"],
        status='OPEN'
    )
    user_bank_funds_audit = userBankFundsAudit.UserBankFundsAuditSchema(parent=user_bank_funds)

    userBankFunds.user_bank_funds_db.put_item(Item=user_bank_funds.to_dict())
    userBankFundsAudit.user_bank_funds_audit_db.put_item(Item=user_bank_funds_audit.to_dict())

    # Enviar correo de confirmación
    send_subscription_funds_email(
        to_email=user.get("email"),
        user_name=user.get("name"),
        bank_fund=bank_fund
    )
    
    body = {
        "detail": "User bank funds created successfully",
        "data": user_bank_funds.to_dict()

    }
    return JSONResponse(content=jsonable_encoder(body), status_code=status.HTTP_201_CREATED)

# READ
def get_user_bank_funds_controller(user_session:SessionUserModel, id:str=None):
    if id:
        response = userBankFunds.user_bank_funds_db.get_item(Key={"id": id})
        return {'item': response.get("Item")}, 200

    # Buscar todos los items de un usuario con scan
    response = userBankFunds.user_bank_funds_db.scan(
        FilterExpression="user_id = :uid",
        ExpressionAttributeValues={":uid": user_session.user_id},
    )
    items = response.get("Items", [])

    body = {
        "detail": "User bank funds retrieved successfully",
        "data": sorted(items, key=lambda x: x.get("created_at", ""), reverse=True),

    }
    return JSONResponse(content=jsonable_encoder(body), status_code=status.HTTP_200_OK)

# DELETE
def delete_user_bank_fund_controller(user_session:SessionUserModel, user_bank_funds_id:str):
    # Buscar el usuario en la tabla de usuarios
    user_response = users.users_db.get_item(Key={"id": user_session.user_id})
    user = user_response.get("Item")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Verificar que el UserBankFund existe
    response = userBankFunds.user_bank_funds_db.get_item(Key={"id": user_bank_funds_id})
    user_bank_fund = response.get("Item")
    if not user_bank_fund:
        raise HTTPException(status_code=404, detail="User bank fund not found")

    # Verificar que el BankFund existe
    response = bankFunds.bank_funds_db.get_item(Key={"id": user_bank_fund.get("bank_funds_id")})
    bank_fund = response.get("Item")
    if not bank_fund:
        raise HTTPException(status_code=404, detail="Bank fund not found")


    # Actualizar saldo del usuario
    user_amount = Decimal(user.get("amount", "0"))
    refund_amount = Decimal(bank_fund["min_amount"])
    new_amount = user_amount + refund_amount

    users.users_db.update_item(
        Key={"id": user['id']},
        UpdateExpression="SET amount = :a, updated_at = :u",
        ExpressionAttributeValues={
            ":a": new_amount,
            ":u": get_current_time()
        }
    )

    # Actualizar estado del UserBankFund
    updated_at = get_current_time()
    userBankFunds.user_bank_funds_db.update_item(
        Key={"id": user_bank_funds_id},
        UpdateExpression="SET #s = :s, updated_at = :u",
        ExpressionAttributeNames={
            "#s": "status"
        },
        ExpressionAttributeValues={
            ":s": "CLOSED",
            ":u": updated_at
        }
    )

    # Obtener el UserBankFund actualizado
    updated_response = userBankFunds.user_bank_funds_db.get_item(Key={"id": user_bank_funds_id})
    updated_user_bank_fund = updated_response.get("Item")

    # Registrar en auditoría
    user_bank_funds_schema = userBankFunds.UserBankFundsSchema.from_dict(updated_user_bank_fund)
    user_bank_fund_audit = userBankFundsAudit.UserBankFundsAuditSchema(parent=user_bank_funds_schema)
    userBankFundsAudit.user_bank_funds_audit_db.put_item(Item=user_bank_fund_audit.to_dict())

    # Enviar correo de confirmación
    send_retired_funds_email(
        to_email=user.get("email"),
        user_name=user.get("name"),
        bank_fund=bank_fund
    )

    body = {
        "detail": "User bank funds deleted successfully",
        "data": user_bank_funds_schema.to_dict()
    }
    return JSONResponse(content=jsonable_encoder(body), status_code=status.HTTP_200_OK)

