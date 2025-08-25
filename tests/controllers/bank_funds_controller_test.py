import pytest
import json
from decimal import Decimal
from fastapi import status
from fastapi.responses import JSONResponse

from app.controllers import bank_funds_controller as controller
from app.controllers.bank_funds_controller import (
    create_bank_funds_controller,
    get_bank_funds_controller,
    update_bank_fund_controller,
)
from app.documents.bank_funds_models import CreateBankFundsModel, UpdateBankFundsModel
from app.documents.auth_models import SessionUserModel

# Módulos reales
import app.schemas.category as category
import app.schemas.bank_funds as bankFunds
import app.controllers.bank_funds_controller as bank_ctrl


class DummyDB:
    """Fake DynamoDB-like client for testing."""
    def __init__(self, name="DummyTable"):
        self.items = {}
        self.name = name

    def get_item(self, Key):
        if Key["id"] in self.items:
            return {"Item": self.items[Key["id"]]}
        return {}

    def put_item(self, Item):
        self.items[Item["id"]] = Item
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    def scan(self):
        return {"Items": list(self.items.values())}

    def update_item(self, **kwargs):
        key = kwargs["Key"]["id"]
        # Obtener item actual o vacío
        attrs = self.items.get(key, {}).copy()

        expr_values = kwargs.get("ExpressionAttributeValues", {})
        expr_names = kwargs.get("ExpressionAttributeNames", {})

        # Parse simple de "SET #alias = :value" o "attr = :value"
        update_expr = kwargs.get("UpdateExpression", "")
        if update_expr.startswith("SET "):
            parts = update_expr[4:].split(", ")
            for part in parts:
                if "=" not in part:
                    continue
                left, right = part.split("=", 1)
                left = left.strip()
                right = right.strip()
                # Resolver alias
                attr_name = expr_names.get(left, left)
                value = expr_values.get(right, None)
                attrs[attr_name] = value

        self.items[key] = attrs
        return {"Attributes": attrs}

class DummyDynamoClient:
    """Mock para dynamodb_client.batch_get_item"""
    def batch_get_item(self, RequestItems):
        # Devuelve las categorías del DummyDB
        table_name = list(RequestItems.keys())[0]
        keys = RequestItems[table_name]["Keys"]
        items = []
        for key in keys:
            cat_id = key["id"]["S"]
            item = category.categories_db.get_item(Key={"id": cat_id}).get("Item")
            if item:
                items.append({k: {"S": str(v)} for k, v in item.items()})
        return {"Responses": {table_name: items}}


@pytest.fixture
def mock_user():
    return SessionUserModel(user_id="user-123", role="ADMIN")


@pytest.fixture
def mock_db(monkeypatch):
    dummy = DummyDB()
    # Seed categoría base
    dummy.items["cat-1"] = {"id": "cat-1", "name": "Category One"}

    # Parchar schemas
    monkeypatch.setattr(category, "categories_db", dummy)
    monkeypatch.setattr(bankFunds, "bank_funds_db", dummy)
    # Parchar dynamodb_client
    monkeypatch.setattr(bank_ctrl, "dynamodb_client", DummyDynamoClient())
    return dummy


def test_create_bank_fund_success(mock_user, mock_db):
    data = CreateBankFundsModel(
        name="Fund A",
        category_id="cat-1",
        min_amount=1000,
        currency="USD",
    )
    response: JSONResponse = create_bank_funds_controller(mock_user, data)
    body = json.loads(response.body.decode())
    
    assert response.status_code == status.HTTP_201_CREATED
    assert "Bank fund created successfully" in body["detail"]
    assert any(item["name"] == "Fund A" for item in mock_db.items.values())


def test_get_bank_funds_success(mock_user, mock_db):
    mock_db.items["fund-1"] = {
        "id": "fund-1",
        "name": "Fund A",
        "category_id": "cat-1",
        "created_at": "2025-01-01T00:00:00",
    }

    response: JSONResponse = get_bank_funds_controller()
    body = json.loads(response.body.decode())
    
    assert response.status_code == status.HTTP_200_OK
    assert body["detail"] == "Bank fund retrieved successfully"
    assert len(body["data"]) >= 1
    assert body["data"][0]["category_id"]["id"] == "cat-1"


def test_update_bank_fund_success(mock_user, mock_db):
    mock_db.items["fund-1"] = {
        "id": "fund-1",
        "name": "Old Fund",
        "category_id": "cat-1",
        "min_amount": Decimal("500"),
    }

    data = UpdateBankFundsModel(
        name="Updated Fund",
        category_id="cat-1",
        min_amount=2000,
        currency="USD",
    )
    response: JSONResponse = update_bank_fund_controller(mock_user, "fund-1", data)
    body = json.loads(response.body.decode())
    
    assert response.status_code == status.HTTP_200_OK
    assert body["detail"] == "Bank fund updated successfully"
    assert body["data"]["name"] == "Updated Fund"
    assert mock_db.items["fund-1"]["name"] == "Updated Fund"
