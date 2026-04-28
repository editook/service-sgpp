from datetime import datetime
from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    rol: str
    nombre_completo: str
    departamento: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: str | None = None
    rol: str | None = None
    nombre_completo: str | None = None
    departamento: str | None = None
    password: str | None = None
    is_active: bool | None = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
