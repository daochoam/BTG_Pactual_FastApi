from pydantic import BaseModel, Field, field_validator
from typing import Optional

class CreateCategoryModel(BaseModel):
    name: str = Field(..., title="Nombre de la categoría", json_schema_extra={"example": "Inversiones"})
    description: Optional[str] = Field(None, title="Descripción de la categoría", json_schema_extra={"example": "Fondos de inversión a largo plazo"})

    @field_validator('*', mode='before')
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class UpdateCategoryModel(BaseModel):
    name: Optional[str] = Field(None, title="Nuevo nombre", json_schema_extra={"example": "Inversiones"})
    description: Optional[str] = Field(None, title="Nueva descripción", json_schema_extra={"example": "Fondos de inversión a largo plazo"})

    @field_validator('*', mode='before')
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v
