from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, FetchedValue, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Case(Base):
    __tablename__ = "casos"

    id = Column(Integer, primary_key=True, index=True)
    codigo_unico = Column(String(50), unique=True, index=True, nullable=False)
    nombre_evaluado = Column(String(150), nullable=False)
    tipo_delito = Column(String(100), nullable=False)
    coeficiente_id = Column(Integer, ForeignKey("coeficientes_complejidad.id"), nullable=False)
    perito_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    perito = relationship("User", backref="casos")
    departamento = Column(String(100), nullable=False, index=True)
    fecha_ingreso = Column(Date, nullable=False, index=True)
    plazo_dias = Column(Integer, nullable=False)
    
    fecha_requerimiento = Column(Date, nullable=True)
    tipo_requerimiento = Column(String(50), nullable=True)
    estado_proceso = Column(String(50), nullable=True)
    estado_proceso_detalle = Column(String(255), nullable=True)
    estado_pericia = Column(String(50), nullable=True)
    estado_pericia_fecha_programada = Column(Date, nullable=True)
    estado_pericia_detalle_representacion = Column(Text, nullable=True)
    estado_pericia_fecha_evaluacion = Column(Date, nullable=True)
    estado_pericia_tiempo_entrega = Column(String(100), nullable=True)
    estado_pericia_fecha_entrega = Column(Date, nullable=True)
    sujeto_procesal = Column(String(50), nullable=True)
    sujeto_procesal_detalle = Column(String(150), nullable=True)
    tipo_delito_detalle = Column(String(255), nullable=True)
    sexo = Column(String(20), nullable=True)
    edad = Column(Integer, nullable=True)
    tiene_consultor_tecnico = Column(Boolean, nullable=True)
    
    # Esta columna es calculada por PostgreSQL: GENERATED ALWAYS AS
    fecha_vencimiento = Column(Date, server_default=FetchedValue())
    
    fecha_cierre = Column(Date, nullable=True)
    estado = Column(String(50), default='Activo', index=True, nullable=False)
    ampliacion_solicitada = Column(Boolean, default=False)
    archivo_pdf_url = Column(String(255), nullable=True)
    firma_digital_hash = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
