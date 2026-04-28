from typing import Annotated, Any
from datetime import datetime, date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case

from fastapi.responses import StreamingResponse
from app.services.pdf_generator import draw_pdf_report

from app.core.database import get_db
from app.models.case import Case
from app.models.user import User
from app.models.complexity import ComplexityCoefficient
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/ranking")
def get_ranking(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    month: int = datetime.now().month,
    year: int = datetime.now().year
) -> Any:
    """
    Lista el ranking visible de peritos según su productividad mensual.
    Productividad = Suma acumulada de coeficiente_complejidad de casos "Cerrados" este mes.
    """
    
    ranking_query = (
        db.query(
            User.id.label("perito_id"),
            User.nombre_completo.label("perito_nombre"),
            func.count(Case.id).label("casos_cerrados"),
            func.coalesce(func.sum(ComplexityCoefficient.valor_multiplicador), 0).label("productividad_mensual"),
            # Porcentaje de retraso: de los cerrados en el mes, cuales tuvieron retraso > plazo_dias
            func.avg(
                case(
                    ((Case.fecha_cierre - Case.fecha_ingreso) > Case.plazo_dias, 1.0),
                    else_=0.0
                )
            ).label("porcentaje_retraso_decimal")
        )
        .join(Case, Case.perito_id == User.id)
        .join(ComplexityCoefficient, Case.coeficiente_id == ComplexityCoefficient.id)
        .filter(Case.estado == 'Cerrado')
        .filter(extract('month', Case.fecha_cierre) == month)
        .filter(extract('year', Case.fecha_cierre) == year)
        .filter(User.rol == 'PERITO')
        .group_by(User.id, User.nombre_completo)
        .order_by(func.coalesce(func.sum(ComplexityCoefficient.valor_multiplicador), 0).desc())
        .all()
    )
    
    result = []
    for row in ranking_query:
        result.append({
            "perito_id": row.perito_id,
            "perito_nombre": row.perito_nombre,
            "casos_cerrados": row.casos_cerrados,
            "productividad_mensual": float(row.productividad_mensual),
            "porcentaje_retraso": round(float(row.porcentaje_retraso_decimal or 0) * 100, 2)
        })
        
    return result

@router.get("/dashboard-stats")
def get_dashboard_stats(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> Any:
    """Retorna metricas resumidas para la vista principal de DataGrid y Cards"""
    today = date.today()
    if current_user.rol == "ADMIN":
        base_query_activos = db.query(Case).filter(Case.estado == 'Activo')
    else:
        base_query_activos = db.query(Case).filter(Case.estado == 'Activo', Case.perito_id == current_user.id)
        
    casos_activos = base_query_activos.count()
    
    # Retrasados activos: (Hoy - FechaIngreso) > PlazoDias
    retrasados = base_query_activos.filter((today - Case.fecha_ingreso) > Case.plazo_dias).count()
    
    return {
        "casos_activos": casos_activos,
        "casos_retrasados_activos": retrasados,
    }

@router.get("/download-pdf", response_class=StreamingResponse)
def download_institutional_report_pdf(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    month: int = datetime.now().month,
    year: int = datetime.now().year
):
    """
    Exportación de tabla de ranking y productividad a documento PDF Asíncrono en memoria usando ReportLab.
    """
    data_ranking = get_ranking(db=db, current_user=current_user, month=month, year=year)
    
    # Adaptar para headers legibles del PDF
    readable_data = []
    for item in data_ranking:
        readable_data.append({
            "PERITO": item["perito_nombre"],
            "CASOS CERRADOS": item["casos_cerrados"],
            "PRODUCTIVIDAD": item["productividad_mensual"],
            "RETRASO (%)": f'{item["porcentaje_retraso"]}%'
        })
        
    pdf_buffer = draw_pdf_report(readable_data, title=f"Mensual {year}-{month:02d}")
    
    from app.services.logger import create_log
    create_log(
        db=db,
        accion="Exportación PDF",
        tabla_afectada="Reporte Institucional",
        usuario_id=current_user.id
    )
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Reporte_Institucional_{year}_{month}.pdf"}
    )

