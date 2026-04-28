from datetime import date, datetime
from pydantic import BaseModel

class UserBasic(BaseModel):
    id: int
    nombre_completo: str
    username: str

    class Config:
        from_attributes = True

class CaseBase(BaseModel):
    codigo_unico: str
    nombre_evaluado: str
    tipo_delito: str
    coeficiente_id: int
    perito_id: int
    departamento: str
    fecha_ingreso: date
    plazo_dias: int
    fecha_requerimiento: date | None = None
    tipo_requerimiento: str | None = None
    estado_proceso: str | None = None
    estado_proceso_detalle: str | None = None
    estado_pericia: str | None = None
    estado_pericia_fecha_programada: date | None = None
    estado_pericia_detalle_representacion: str | None = None
    estado_pericia_fecha_evaluacion: date | None = None
    estado_pericia_tiempo_entrega: str | None = None
    estado_pericia_fecha_entrega: date | None = None
    sujeto_procesal: str | None = None
    sujeto_procesal_detalle: str | None = None
    tipo_delito_detalle: str | None = None
    sexo: str | None = None
    edad: int | None = None
    tiene_consultor_tecnico: bool | None = None

class CaseCreate(CaseBase):
    pass

class CaseResponse(CaseBase):
    id: int
    fecha_vencimiento: date | None = None
    fecha_cierre: date | None = None
    estado: str
    ampliacion_solicitada: bool
    archivo_pdf_url: str | None = None
    firma_digital_hash: str | None = None
    created_at: datetime
    updated_at: datetime
    perito: UserBasic | None = None

    class Config:
        from_attributes = True

class CaseUpdateEstadoPericia(BaseModel):
    estado_pericia: str | None = None
    estado_pericia_fecha_programada: date | None = None
    estado_pericia_detalle_representacion: str | None = None
    estado_pericia_fecha_evaluacion: date | None = None
    estado_pericia_tiempo_entrega: str | None = None
    estado_pericia_fecha_entrega: date | None = None
