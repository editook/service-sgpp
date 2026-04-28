from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Log(Base):
    __tablename__ = "bitacora"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    accion = Column(String(100), nullable=False)
    tabla_afectada = Column(String(50), nullable=False)
    registro_id = Column(Integer, nullable=True)
    detalles = Column(String, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=func.now())
