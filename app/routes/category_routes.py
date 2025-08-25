from fastapi import APIRouter, Depends, Path, Request, Body
from app.controllers.auth_decorators import auth_required
from app.documents.auth_models import SessionUserModel
from app.documents.category_models import CreateCategoryModel, UpdateCategoryModel
from app.controllers.category_controller import (
    create_category_controller,
    get_categories_controller,
    update_category_controller
)

category_routes = APIRouter(prefix="/category", tags=["category"])

# CREATE
@category_routes.post("/", summary="Crear una categoría")
def create_category(
    data: CreateCategoryModel = Body(...),
    user_session: SessionUserModel = Depends(auth_required(require_admin=True))
):
    return create_category_controller(user_session, data)

# READ ALL
@category_routes.get("/", summary="Obtener todas las categorías")
def get_categories():
    return get_categories_controller()

# READ ONE
@category_routes.get("/{id}", summary="Obtener una categoría por ID")
def get_category(id: str = Path(...)):
    return get_categories_controller(id)


# UPDATE
@category_routes.put("/{id}", summary="Actualizar una categoría")
def update_category(
    id: str = Path(...),
    data: UpdateCategoryModel = Body(...),
    user_session: SessionUserModel = Depends(auth_required(require_admin=True))
):
    return update_category_controller(user_session, id, data)
