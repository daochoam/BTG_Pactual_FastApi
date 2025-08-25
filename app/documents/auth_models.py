from pydantic import BaseModel, Field, field_validator
from typing import Literal

class RegisterUserModel(BaseModel):
    nit: str = Field(..., title="NIT del usuario", json_schema_extra={"example": "123456789"})
    name: str = Field(..., title="Nombre", json_schema_extra={"example": "Daniel"})
    last_name: str = Field(..., title="Apellido", json_schema_extra={"example": "8A"})
    email: str = Field(..., title="Correo electrónico", json_schema_extra={"example": "daniel@example.com"})
    phone: str = Field(..., title="Teléfono", json_schema_extra={"example": "+573001234567"})
    role: Literal['USER', 'ADMIN'] = Field(None, title="Rol del usuario", json_schema_extra={"example": "USER"})
    password: str = Field(..., title="Contraseña", json_schema_extra={"example": "MiContraseñaSegura123"})

    @field_validator('*', mode='before')
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class LoginUserModel(BaseModel):
    email: str = Field(..., title="Correo electrónico", json_schema_extra={"example": "daniel@example.com"})
    password: str = Field(..., title="Contraseña", json_schema_extra={"example": "MiContraseñaSegura123"})

    @field_validator('*', mode='before')
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class SessionUserModel(BaseModel):
    user_id: str = Field(..., title="ID del usuario", example="123456789")
    role: Literal['USER', 'ADMIN'] = Field(..., title="Rol del usuario", example="USER")
