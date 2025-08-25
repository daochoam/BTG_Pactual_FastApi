from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from app.documents.auth_models import SessionUserModel
from app.documents.category_models import CreateCategoryModel, UpdateCategoryModel
from app.utils.time import get_current_time
import app.schemas.category as category

# CREATE
def create_category_controller(user_session: SessionUserModel, data: CreateCategoryModel):
    category_schema = category.CategorySchema(user_session.user_id, data.name, data.description)
    category.categories_db.put_item(Item=category_schema.to_dict())


    body = {
            "detail": "Category created successfully",
            "data": category_schema.to_dict(),
        }

    return JSONResponse(content=body, status_code=status.HTTP_201_CREATED)

# READ
def get_categories_controller(id:str=None):
    response = category.categories_db.scan()
    items = response.get("Items", [])
    if id:
        items = [item for item in items if item.get("id") == id]
        if not items:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    body = {
            "detail": "Category retrieved successfully",
            "data":  sorted(items, key=lambda x: x.get("created_at", ""), reverse=True),
        }
    return JSONResponse(content=body, status_code=status.HTTP_200_OK)

def update_category_controller(user_session: SessionUserModel, id: str, data: UpdateCategoryModel):
    update_expr = []
    expr_values = {}
    expr_names = {}  # <- aquí guardamos los alias

    if data.name:
        update_expr.append("#n = :n")
        expr_values[":n"] = data.name
        expr_names["#n"] = "name"  # alias para evitar reserved word

    if data.description:
        update_expr.append("#d = :d")
        expr_values[":d"] = data.description
        expr_names["#d"] = "description"  # alias para evitar reserved word

    if not update_expr:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nothing to update")

    # Siempre actualizar user_created y update_date
    update_expr.append("user_created = :u")
    expr_values[":u"] = user_session.user_id
    update_expr.append("updated_at = :t")
    expr_values[":t"] = get_current_time()

    response = category.categories_db.update_item(
        Key={"id": id},
        UpdateExpression="SET " + ", ".join(update_expr),
        ExpressionAttributeValues=expr_values,
        ExpressionAttributeNames=expr_names if expr_names else None,  # <- agregamos aquí
        ReturnValues="ALL_NEW"
    )

    body = {
        "detail": "Category updated successfully",
        "data": response.get("Attributes"),
    }
    return JSONResponse(content=body, status_code=status.HTTP_200_OK)
