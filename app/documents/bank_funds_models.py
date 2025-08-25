from pydantic import BaseModel, Field, field_validator
from typing import Optional

class CreateBankFundsModel(BaseModel):
    name: str = Field(..., title="Nombre del fondo", json_schema_extra={"example": "Fondo de Inversión"})
    category_id: str = Field(..., title="Categoría del fondo", json_schema_extra={"example": "Renta Variable"})
    min_amount: float = Field(..., title="Monto mínimo", json_schema_extra={"example": 1000.0})
    currency: Optional[str] = Field(None, title="Moneda", json_schema_extra={"example": "USD"})

    @field_validator('*', mode='before')
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class UpdateBankFundsModel(BaseModel):
    name: Optional[str] = Field(None, title="Nuevo nombre", json_schema_extra={"example": "Fondo de Inversión"})
    category_id: Optional[str] = Field(None, title="Nueva categoría", json_schema_extra={"example": "Renta Variable"})
    min_amount: Optional[float] = Field(None, title="Nuevo monto mínimo", json_schema_extra={"example": 1000.0})
    currency: Optional[str] = Field(None, title="Nueva moneda", json_schema_extra={"example": "USD"})

    @field_validator('*', mode='before')
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v