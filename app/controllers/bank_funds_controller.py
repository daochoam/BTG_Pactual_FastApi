from decimal import Decimal
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from boto3.dynamodb.types import TypeDeserializer
from app.config import dynamodb_client
from app.documents.auth_models import SessionUserModel
from app.documents.bank_funds_models import CreateBankFundsModel, UpdateBankFundsModel
from app.utils.time import get_current_time

import app.schemas.category as category
import app.schemas.bank_funds as bankFunds

serializer = TypeDeserializer()

def deserialize(item):
    """Convierte un item de DynamoDB a dict normal"""
    return {k: serializer.deserialize(v) for k, v in item.items()}

# CREATE
def create_bank_funds_controller(user_session: SessionUserModel, data: CreateBankFundsModel):
    """Crea un nuevo fondo bancario."""
    cat_response = category.categories_db.get_item(Key={"id": data.category_id})
    if "Item" not in cat_response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category does not exist")

    bankfund_schema = bankFunds.BankFundsSchema(
        name=data.name,
        category_id=data.category_id,
        min_amount=data.min_amount,
        currency=data.currency or None,
        user_created=user_session.user_id
    )

    bankFunds.bank_funds_db.put_item(Item=bankfund_schema.to_dict())

    body = {
        "detail": "Bank fund created successfully",
        "data": bankfund_schema.to_dict(),
    }
    return JSONResponse(content=jsonable_encoder(body), status_code=status.HTTP_201_CREATED)

def get_bank_funds_controller(id=None):
    response = bankFunds.bank_funds_db.scan()
    items = response.get("Items", [])
    if id:
        items = [item for item in items if item.get("id") == id]
        if not items:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BankFund not found")

    # Obtener todos los category_ids únicos
    category_ids = list({item["category_id"] for item in items if "category_id" in item})

    if category_ids:
        keys = [{"id": {"S": cid}} for cid in category_ids]
        batch_response = dynamodb_client.batch_get_item(
            RequestItems={category.categories_db.name: {"Keys": keys}}
        )
        categories_raw = batch_response.get("Responses", {}).get(category.categories_db.name, [])
        categories = [deserialize(cat) for cat in categories_raw]
        cat_map = {cat["id"]: cat for cat in categories}

        for item in items:
            cat_id = item.get("category_id")
            if cat_id and cat_id in cat_map:
                item["category_id"] = cat_map[cat_id]
    
    body = {
        "detail": "Bank fund retrieved successfully",
        "data":  sorted(items, key=lambda x: x.get("created_at", ""), reverse=True),
    }
    return JSONResponse(content=jsonable_encoder(body), status_code=status.HTTP_200_OK)

# UPDATE
def update_bank_fund_controller(user_session: SessionUserModel, id: str, data: UpdateBankFundsModel):
    try:
        update_expr = []
        expr_values = {}
        expr_names = {}

        # Campos editables
        if data.name:
            update_expr.append("#n = :n")
            expr_values[":n"] = data.name
            expr_names["#n"] = "name"
            
        if data.category_id:
            cat_response = category.categories_db.get_item(Key={"id": data.category_id})
            if "Item" not in cat_response:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Category does not exist"
                )
            update_expr.append("category_id = :c")
            expr_values[":c"] = data.category_id
            # category_id no es reserved word, pero igual podrías aliasar si quieres consistencia

        if data.min_amount:
            update_expr.append("min_amount = :m")
            expr_values[":m"] = Decimal(data.min_amount)

        if not update_expr:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Nothing to update"
            )

        # Auditoría: siempre actualizar user_updated y updated_at
        update_expr.append("user_updated = :u")
        expr_values[":u"] = user_session.user_id
        update_expr.append("updated_at = :t")
        expr_values[":t"] = get_current_time()

        # Ejecutar update en DynamoDB
        response = bankFunds.bank_funds_db.update_item(
            Key={"id": id},
            UpdateExpression="SET " + ", ".join(update_expr),
            ExpressionAttributeValues=expr_values,
            ExpressionAttributeNames=expr_names if expr_names else None,
            ReturnValues="ALL_NEW"
        )

        body = {
            "detail": "Bank fund updated successfully",
            "data": response.get("Attributes"),
        }
        return JSONResponse(content=jsonable_encoder(body), status_code=status.HTTP_200_OK)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        )
    