from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Extension(Base):
    __tablename__ = "ampliaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("casos.id", ondelete="CASCADE"), nullable=False)
    dias_solicitados = Column(Integer, nullable=False)
    motivo = Column(String, nullable=False)
    estado = Column(String(50), default='Pendiente')
    evaluado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
