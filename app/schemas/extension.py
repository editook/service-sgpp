from datetime import datetime
from pydantic import BaseModel

class ExtensionBase(BaseModel):
    caso_id: int
    dias_solicitados: int
    motivo: str

class ExtensionCreate(ExtensionBase):
    pass

class ExtensionResponse(ExtensionBase):
    id: int
    estado: str
    evaluado_por: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ExtensionUpdate(BaseModel):
    estado: str # 'Aprobada' o 'Rechazada'
