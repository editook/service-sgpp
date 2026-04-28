from typing import Annotated, List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case, text

from app.core.database import get_db
from app.models.case import Case
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.statistics import DashboardStatsResponse, KPIData, NameCount, TimelineCount

router = APIRouter()

@router.get("/", response_model=DashboardStatsResponse)
def get_dashboard_statistics(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Obtener datos estadísticos de todos los casos, usado para el Dashboard."""
    
    # Filtro base: si es admin ve todo, si es perito solo lo suyo.
    base_query = db.query(Case)
    if current_user.rol != "ADMIN":
        base_query = base_query.filter(Case.perito_id == current_user.id)
        
    # 1. KPIs
    # SQLite logic para calcular porcentaje/totales
    # Nota: usamos SQLite date('now') para la comparación de retrasos
    total_casos = base_query.count()
    activos = base_query.filter(Case.estado == "Activo").count()
    cerrados = base_query.filter(Case.estado == "Cerrado").count()
    
    # Retraso (simplificado: fecha_ingreso + plazo_dias < current_date y estado == Activo)
    retrasos_query = base_query.filter(Case.estado == "Activo").filter(
        text("date(fecha_ingreso, '+' || plazo_dias || ' days') < date('now')")
    ).count()
    
    kpis = KPIData(
        total=total_casos,
        activos=activos,
        cerrados=cerrados,
        con_retraso=retrasos_query
    )
    
    # 2. Por Departamento
    dept_query = base_query.with_entities(
        Case.departamento, func.count(Case.id).label('total')
    ).group_by(Case.departamento).all()
    
    por_departamento = [NameCount(name=dept[0], value=dept[1]) for dept in dept_query]
    
    # 3. Por Tipo de Delito
    delito_query = base_query.with_entities(
        Case.tipo_delito, func.count(Case.id).label('total')
    ).group_by(Case.tipo_delito).order_by(text('total DESC')).limit(5).all()
    
    por_delito = [NameCount(name=delito[0], value=delito[1]) for delito in delito_query]
    
    # 4. Timeline
    # Extraemos el mes y año en SQLite
    timeline_query = base_query.with_entities(
        func.strftime('%Y-%m', Case.fecha_ingreso).label('mes'),
        func.count(Case.id).label('total')
    ).group_by('mes').order_by('mes').all()
    
    timeline = [TimelineCount(mes=row[0], cantidad=row[1]) for row in timeline_query]

    # 5. Por Perito
    perito_query = base_query.join(User, Case.perito_id == User.id).with_entities(
        User.nombre_completo.label('nombre'),
        func.count(Case.id).label('total')
    ).group_by(User.nombre_completo).order_by(text('total DESC')).all()
    
    por_perito = [NameCount(name=row[0], value=row[1]) for row in perito_query]

    return DashboardStatsResponse(
        kpis=kpis,
        por_departamento=por_departamento,
        por_delito=por_delito,
        timeline=timeline,
        por_perito=por_perito
    )
