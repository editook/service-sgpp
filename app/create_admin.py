import sys
import os

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.user import User
from app.models.complexity import ComplexityCoefficient
from app.core.security import get_password_hash
from app.core.database import Base
from app.models.case import Case

def init_db():
    print("Creando tablas en PostgreSQL si no existen...")
    print("DATABASE URL:", settings.SQLALCHEMY_DATABASE_URI)
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente")
    db: Session = SessionLocal()
    
    # 1. Crear Coeficientes de Complejidad base si no existen
    coeficientes = [
        {"nivel": "Baja", "valor_multiplicador": 1.0},
        {"nivel": "Media", "valor_multiplicador": 1.5},
        {"nivel": "Alta", "valor_multiplicador": 2.0},
        {"nivel": "Muy Alta", "valor_multiplicador": 3.0}
    ]
    
    print("Inyectando Coeficientes de Complejidad...")
    for coef in coeficientes:
        existing = db.query(ComplexityCoefficient).filter(ComplexityCoefficient.nivel == coef["nivel"]).first()
        if not existing:
            new_coef = ComplexityCoefficient(
                nivel=coef["nivel"],
                valor_multiplicador=coef["valor_multiplicador"]
            )
            db.add(new_coef)
            
    # 2. Crear usuario ADMIN por defecto
    print("Verificando existencia del usuario administrador...")
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        new_admin = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            rol="ADMIN",
            nombre_completo="Administrador del Sistema",
            departamento="Sistemas Central"
        )
        db.add(new_admin)
        print("Usuario 'admin' creado exitosamente con contraseña")
    else:
        print("Usuario 'admin' ya existe en PostgreSQL.")
        
    db.commit()
    db.close()
    print("Poblado de Base de Datos completado!")

if __name__ == "__main__":
    init_db()
