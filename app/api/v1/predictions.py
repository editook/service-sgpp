from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.case import Case
from app.models.user import User
from app.models.complexity import ComplexityCoefficient
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/estimate-time")
def predict_case_resolution_time(
    coeficiente_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> Any:
    """
    Módulo Predictivo MVP: Estima la cantidad de días que tomará resolver un caso nuevo,
    basado en el promedio histórico de días reales de resolución para casos similares 
    (mismo nivel de complejidad) cerrados en el sistema.
    """
    # Validar coeficiente
    coef = db.query(ComplexityCoefficient).filter(ComplexityCoefficient.id == coeficiente_id).first()
    if not coef:
        raise HTTPException(status_code=404, detail="Coeficiente de complejidad no encontrado")
        
    # Obtener el promedio de días reales de resolución (fecha_cierre - fecha_ingreso)
    # para todos los casos cerrados que tengan ese mismo coeficiente de complejidad.
    avg_days_query = db.query(
        func.avg(Case.fecha_cierre - Case.fecha_ingreso).label("promedio_dias")
    ).filter(
        Case.estado == 'Cerrado',
        Case.coeficiente_id == coeficiente_id
    ).first()
    
    # Extraer el valor promedio
    promedio_dias_timedelta = avg_days_query.promedio_dias
    
    # Si hay suficientes datos históricos
    if promedio_dias_timedelta is not None:
        estimated_days = round(promedio_dias_timedelta.days)
        confidence = "Alta (Basada en métricas históricas del sistema)"
    else:
        # Fallback si el sistema es nuevo o no hay casos cerrados de ese tipo
        # Usaremos el multiplicador predictivo base * un valor nominal (ej: 10 días base)
        estimated_days = int(10 * float(coef.valor_multiplicador))
        confidence = "Baja (Estimación estándar teórica, faltan datos locales)"
        
    return {
        "complejidad": coef.nivel,
        "dias_estimados_resolucion": estimated_days,
        "nivel_confianza": confidence
    }
