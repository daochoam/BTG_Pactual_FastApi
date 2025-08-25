from pydantic import BaseModel, Field, field_validator
from typing import Optional

class UserBankFundAuditModel(BaseModel):
    id: Optional[str] = Field(None, title="ID del registro de auditoría", json_schema_extra={"example": "123456789"})
    user_id: Optional[str] = Field(None, title="ID del usuario", json_schema_extra={"example": "123456789"})
    bank_funds_id: Optional[str] = Field(None, title="ID del fondo bancario asociado", json_schema_extra={"example": "123456789"})

    @field_validator('*', mode='before')
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v