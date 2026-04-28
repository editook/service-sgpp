from sqlalchemy import Column, Integer, String, Numeric
from app.core.database import Base

class ComplexityCoefficient(Base):
    __tablename__ = "coeficientes_complejidad"

    id = Column(Integer, primary_key=True, index=True)
    nivel = Column(String(50), unique=True, nullable=False)
    valor_multiplicador = Column(Numeric(5, 2), nullable=False)
