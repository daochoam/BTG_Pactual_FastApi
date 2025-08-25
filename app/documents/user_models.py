from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from typing import Literal

class UserModel(BaseModel):
    name: Optional[str] = Field(None, title="Nombre", json_schema_extra={"example": "Daniel"})
    last_name: Optional[str] = Field(None, title="Apellido", json_schema_extra={"example": "8A"})
    email: Optional[EmailStr] = Field(None, title="Correo electrónico", json_schema_extra={"example": "daniel@example.com"})
    role: Optional[Literal['ADMIN', 'USER']] = Field(None, title="Rol del usuario", json_schema_extra={"example": "USER"})

