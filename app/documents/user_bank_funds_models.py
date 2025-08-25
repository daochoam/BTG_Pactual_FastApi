from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional

class CreateUserBankFundsModel(BaseModel):
    name: str = Field(..., example="User Fund A")
    bank_fund_id: str = Field(..., example="fund-1")
    amount: Decimal = Field(..., example=1000)
    currency: Optional[str] = Field(None, example="USD")


class UpdateUserBankFundsModel(BaseModel):
    name: Optional[str] = None
    bank_fund_id: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
