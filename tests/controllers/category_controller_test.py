import pytest
import json
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse

from app.controllers.category_controller import (
    create_category_controller,
    get_categories_controller,
    update_category_controller,
)
from app.documents.auth_models import SessionUserModel
from app.documents.category_models import CreateCategoryModel, UpdateCategoryModel


class DummyDB:
    """Fake DynamoDB-like DB for tests."""
    def __init__(self):
        self.items = {}
        self.name = "Categories"

    def put_item(self, Item):
        self.items[Item["id"]] = Item
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    def scan(self):
        return {"Items": list(self.items.values())}

    def update_item(self, **kwargs):
        key = kwargs["Key"]["id"]
        if key not in self.items:
            return {"Attributes": {}}
        attrs = self.items[key].copy()
        for k, v in kwargs["ExpressionAttributeValues"].items():
            attr_map = {"n": "name", "d": "description", "u": "user_created", "t": "updated_at"}
            attr_name = attr_map.get(k[1:])
            if attr_name:
                attrs[attr_name] = v
        self.items[key] = attrs
        return {"Attributes": attrs}


@pytest.fixture
def mock_user():
    return SessionUserModel(user_id="user-123", role="ADMIN")


@pytest.fixture
def mock_db(monkeypatch):
    dummy = DummyDB()
    import app.schemas.category as cat
    monkeypatch.setattr(cat, "categories_db", dummy)
    return dummy


def test_create_category_success(mock_user, mock_db):
    data = CreateCategoryModel(name="Category A", description="Test description")
    response: JSONResponse = create_category_controller(mock_user, data)
    body = json.loads(response.body.decode())

    assert response.status_code == status.HTTP_201_CREATED
    assert body["detail"] == "Category created successfully"
    assert body["data"]["name"] == "Category A"
    assert body["data"]["description"] == "Test description"


def test_get_categories_success(mock_user, mock_db):
    cat_id = "cat-1"
    mock_db.items[cat_id] = {"id": cat_id, "name": "Category A", "description": "desc", "created_at": "2025-01-01"}

    response: JSONResponse = get_categories_controller()
    body = json.loads(response.body.decode())
    assert response.status_code == status.HTTP_200_OK
    assert body["detail"] == "Category retrieved successfully"
    assert len(body["data"]) >= 1


def test_get_category_by_id_found(mock_user, mock_db):
    cat_id = "cat-123"
    mock_db.items[cat_id] = {"id": cat_id, "name": "Category X", "description": "desc", "created_at": "2025-01-02"}

    response: JSONResponse = get_categories_controller(cat_id)
    body = json.loads(response.body.decode())
    assert response.status_code == status.HTTP_200_OK
    assert body["data"][0]["id"] == cat_id


def test_get_category_by_id_not_found(mock_user, mock_db):
    with pytest.raises(HTTPException) as e:
        get_categories_controller("does-not-exist")
    assert e.value.status_code == status.HTTP_404_NOT_FOUND


def test_update_category_success(mock_user, mock_db):
    cat_id = "cat-1"
    mock_db.items[cat_id] = {"id": cat_id, "name": "Old", "description": "Old desc"}

    data = UpdateCategoryModel(name="New Name", description="New desc")
    response: JSONResponse = update_category_controller(mock_user, cat_id, data)
    body = json.loads(response.body.decode())

    assert response.status_code == status.HTTP_200_OK
    assert body["detail"] == "Category updated successfully"
    assert body["data"]["name"] == "New Name"
    assert body["data"]["description"] == "New desc"


def test_update_category_nothing_to_update(mock_user, mock_db):
    cat_id = "cat-2"
    mock_db.items[cat_id] = {"id": cat_id, "name": "Keep", "description": "Keep desc"}

    data = UpdateCategoryModel(name=None, description=None)
    with pytest.raises(HTTPException) as e:
        update_category_controller(mock_user, cat_id, data)

    assert e.value.status_code == status.HTTP_400_BAD_REQUEST
    assert e.value.detail == "Nothing to update"
