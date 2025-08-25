from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.documents.auth_models import SessionUserModel

import app.schemas.users as users

def get_all_users_controller(user_session: SessionUserModel=None):
    """Obtener todos los usuarios (solo admin)"""
    response = users.users_db.scan()
    items = response.get("Items", [])
    if user_session:
        items = [item for item in items if item.get("id") == user_session.user_id]
        if not items:
            raise HTTPException(status_code=404, detail="User not found")

    body = {
        "detail": "User retrieved successfully",
        "data": items
    }
    return JSONResponse(content=jsonable_encoder(body), status_code=status.HTTP_200_OK)
