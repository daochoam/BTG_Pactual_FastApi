import pytest
from decimal import Decimal
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from app.controllers import user_bank_funds_controller as controller
from app.documents.auth_models import SessionUserModel
from app.documents.user_bank_funds_models import CreateUserBankFundsModel

# DummyDB que soporta scan con filtro
class DummyDB:
    def __init__(self):
        self.items = {}

    def put_item(self, Item):
        # Usar bank_fund_id si existe, sino id
        key = Item.get("bank_fund_id") or Item.get("id")
        self.items[key] = Item
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    def get_item(self, Key):
        key = Key.get("bank_fund_id") or Key.get("id")
        return {"Item": self.items.get(key)}

    def scan(self, FilterExpression=None, ExpressionAttributeValues=None):
        items = list(self.items.values())
        if FilterExpression and ExpressionAttributeValues:
            uid = ExpressionAttributeValues.get(":uid")
            items = [item for item in items if item.get("user_id") == uid]
        return {"Items": items}

    def delete_item(self, Key):
        key = Key.get("bank_fund_id") or Key.get("id")
        return self.items.pop(key, None)

# Fixture usuario de prueba
@pytest.fixture
def mock_user():
    return SessionUserModel(user_id="user123", role="ADMIN")

# Fixture DB parcheada
@pytest.fixture
def mock_db(monkeypatch):
    dummy_funds = DummyDB()
    dummy_users = DummyDB()
    # Agregar usuario de prueba
    dummy_users.put_item({"id": "user123", "name": "Test User"})

    # Parchar DBs internas
    import app.schemas.users as users
    import app.schemas.user_bank_funds as userBankFunds

    monkeypatch.setattr(userBankFunds, "user_bank_funds_db", dummy_funds)
    monkeypatch.setattr(users, "users_db", dummy_users)

    return dummy_funds

# ---------------------------
# Tests
# ---------------------------

def test_create_user_bank_fund(mock_user, mock_db):
    data = CreateUserBankFundsModel(
        user_id="user123",
        bank_fund_id="fund-1",
        name="My Fund",
        amount=1000,
        currency="USD"
    )
    
    # Convertir el modelo a dict antes de pasarlo al controller si el controller usa boto3 real
    data_dict = data.model_dump()  # Pydantic v2
    # o data.dict() si estás usando Pydantic v1

    # Patch al controller para que use nuestra dummy DB
    response: JSONResponse = controller.create_user_bank_fund_controller(mock_user, data_dict)
    
    assert response.status_code == 201
    assert "User bank fund created successfully" in response.body.decode()
    # Verificar que se guardó en dummy DB
    assert any(item["name"] == "My Fund" for item in mock_db.items.values())


def test_get_user_bank_funds(mock_user, mock_db):
    mock_db.put_item({"id": "fund-1", "user_id": "user123", "name": "My Fund", "amount": Decimal("1000")})
    response: JSONResponse = controller.get_user_bank_funds_controller(mock_user)
    body = response.body.decode()
    assert response.status_code == 200
    assert "My Fund" in body

def test_delete_user_bank_fund(mock_user, mock_db):
    mock_db.put_item({"id": "fund-1", "user_id": "user123", "name": "My Fund", "amount": Decimal("1000")})
    response: JSONResponse = controller.delete_user_bank_fund_controller(mock_user, "fund-1")
    assert response.status_code == 200
    assert "User bank fund deleted successfully" in response.body.decode()
    assert "fund-1" not in mock_db.items
