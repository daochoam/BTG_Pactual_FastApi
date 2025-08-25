from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.documents.auth_models import SessionUserModel

import app.schemas.user_bank_funds_audit as userBankFundsAudit

# READ
def get_user_bank_funds_audit_controller(user_session: SessionUserModel, user_bank_funds_audit_id: str = None):

    # Buscar todos los items de un usuario con scan
    response = userBankFundsAudit.user_bank_funds_audit_db.scan(
        FilterExpression="user_id = :uid",
        ExpressionAttributeValues={":uid": user_session.user_id},
    )
    items = response.get("Items", [])
    
    if user_bank_funds_audit_id:
        items = [item for item in items if item.get("id") == user_bank_funds_audit_id]
        if not items:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User bank funds audit not found")
    
    
    body = {
        "detail": "User bank funds audit retrieved successfully",
        "data": sorted(items, key=lambda x: x.get("created_at", ""), reverse=True),
    }
    return JSONResponse(content=jsonable_encoder(body), status_code=status.HTTP_200_OK)
