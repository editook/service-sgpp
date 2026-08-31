from datetime import date
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import case as sa_case

from app.core.database import get_db
from app.models.case import Case
from app.models.user import User
from app.api.deps import get_current_user, get_current_admin
from app.schemas.case import CaseCreate, CaseResponse, CaseUpdate, CaseUpdateEstadoPericia

router = APIRouter()

@router.get("/check-cud")
def check_cud(
    cud: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Verifica si existe un CUD idéntico o similar en la base de datos."""
    if not cud or len(cud.strip()) < 2:
        return {"exists": False, "matches": []}
        
    cleaned_cud = cud.strip()
    # Buscar coincidencia exacta
    exact = db.query(Case).filter(Case.codigo_unico.ilike(cleaned_cud)).first()
    
    # Buscar similares (contiene parte del código)
    similares = db.query(Case).filter(Case.codigo_unico.ilike(f"%{cleaned_cud}%")).limit(4).all()
    
    matches = [{"codigo_unico": c.codigo_unico, "evaluado": c.nombre_evaluado} for c in similares]
    return {
        "exists": exact is not None,
        "exact_match": exact.codigo_unico if exact else None,
        "matches": matches
    }

@router.post("/", response_model=CaseResponse)
def create_case(
    *,
    db: Annotated[Session, Depends(get_db)],
    case_in: CaseCreate,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Crear un nuevo caso. Admin elige perito, Perito se auto-asigna."""
    # Si es perito, ignoramos a quién intentó asignar el caso en el frontend y forzamos su propio ID
    if current_user.rol != "ADMIN":
        case_in.perito_id = current_user.id
        
    case_db = Case(**case_in.model_dump())
    
    # Automatización de Estado General
    if case_db.estado_pericia == "Entregado":
        case_db.estado = "Cerrado"
        case_db.fecha_cierre = case_db.estado_pericia_fecha_entrega or date.today()
    else:
        case_db.estado = "Activo"
        
    db.add(case_db)
    db.commit()
    db.refresh(case_db)
    
    from app.services.logger import create_log
    create_log(
        db=db,
        accion="Crear Caso",
        tabla_afectada="casos",
        registro_id=case_db.id,
        detalles=f"Caso {case_db.codigo_unico} creado asignado al perito {case_db.perito_id}",
        usuario_id=current_user.id
    )
    
    return case_db

@router.get("/", response_model=List[CaseResponse])
def get_cases(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 200
):
    """Listar casos ordenados: en curso arriba (Se programó, En elaboración), representados y entregados abajo."""
    order_priority = sa_case(
        (Case.estado_pericia.in_(["Se programo", "Se programó"]), 1),
        (Case.estado_pericia.in_(["En proceso de elaboracion", "En proceso de elaboración"]), 2),
        (Case.estado_pericia.in_(["Se represento", "Se representó"]), 4),
        (Case.estado_pericia == "Entregado", 5),
        else_=3
    )
    
    query = db.query(Case).options(joinedload(Case.perito))
    if current_user.rol != "ADMIN":
        query = query.filter(Case.perito_id == current_user.id)
        
    casos = query.order_by(order_priority, Case.id.desc()).offset(skip).limit(limit).all()
    return casos

@router.put("/{case_id}", response_model=CaseResponse)
@router.patch("/{case_id}", response_model=CaseResponse)
def update_case(
    *,
    db: Annotated[Session, Depends(get_db)],
    case_id: int,
    case_in: CaseUpdate,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Actualizar todos los campos del caso."""
    case_db = db.query(Case).filter(Case.id == case_id).first()
    if not case_db:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
        
    # Solo el perito asignado al caso o un admin puede modificarlo
    if current_user.rol != "ADMIN" and case_db.perito_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acceso denegado: Solo el perito asignado a este caso puede modificarlo.")

    update_data = case_in.model_dump(exclude_unset=True)

    # No validamos colisión de CUD ya que se permiten múltiples casos con el mismo CUD
    if "codigo_unico" in update_data and update_data["codigo_unico"]:
        update_data["codigo_unico"] = update_data["codigo_unico"].strip()

    # Limpieza inteligente de campos y automatización de Estado General según el estado de pericia
    if "estado_pericia" in update_data:
        nuevo_estado = update_data["estado_pericia"]
        if nuevo_estado == "Se programo":
            update_data["estado_pericia_detalle_representacion"] = None
            update_data["estado_pericia_fecha_evaluacion"] = None
            update_data["estado_pericia_tiempo_entrega"] = None
            update_data["estado_pericia_fecha_entrega"] = None
            case_db.estado = "Activo"
            case_db.fecha_cierre = None
        elif nuevo_estado == "Se represento":
            update_data["estado_pericia_fecha_programada"] = None
            update_data["estado_pericia_fecha_evaluacion"] = None
            update_data["estado_pericia_tiempo_entrega"] = None
            update_data["estado_pericia_fecha_entrega"] = None
        elif nuevo_estado == "En proceso de elaboracion":
            update_data["estado_pericia_fecha_programada"] = None
            update_data["estado_pericia_detalle_representacion"] = None
            update_data["estado_pericia_fecha_entrega"] = None
            case_db.estado = "Activo"
            case_db.fecha_cierre = None
        elif nuevo_estado == "Entregado":
            update_data["estado_pericia_fecha_programada"] = None
            update_data["estado_pericia_detalle_representacion"] = None
            update_data["estado_pericia_fecha_evaluacion"] = None
            update_data["estado_pericia_tiempo_entrega"] = None
            case_db.estado = "Cerrado"
            case_db.fecha_cierre = update_data.get("estado_pericia_fecha_entrega") or date.today()

    for field, value in update_data.items():
        setattr(case_db, field, value)
        
    db.commit()
    db.refresh(case_db)
    
    from app.services.logger import create_log
    create_log(
        db=db,
        accion="Modificar Caso Completo",
        tabla_afectada="casos",
        registro_id=case_db.id,
        detalles=f"Caso {case_db.codigo_unico} modificado (Estado General: {case_db.estado})",
        usuario_id=current_user.id
    )
    
    return case_db

@router.patch("/{case_id}/estado_pericia", response_model=CaseResponse)
def update_estado_pericia(
    *,
    db: Annotated[Session, Depends(get_db)],
    case_id: int,
    case_in: CaseUpdateEstadoPericia,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Actualizar únicamente el estado de la pericia y sus campos relacionados."""
    case_db = db.query(Case).filter(Case.id == case_id).first()
    if not case_db:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
        
    # Solo el perito asignado al caso puede modificar su estado
    if case_db.perito_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acceso denegado: Solo el perito asignado a este caso puede modificar su estado.")
        
    update_data = case_in.model_dump(exclude_unset=True)
    
    # Vaciar/limpiar campos según el nuevo estado para no mantener datos viejos
    if "estado_pericia" in update_data:
        nuevo_estado = update_data["estado_pericia"]
        
        if nuevo_estado == "Se programo":
            update_data["estado_pericia_detalle_representacion"] = None
            update_data["estado_pericia_fecha_evaluacion"] = None
            update_data["estado_pericia_tiempo_entrega"] = None
            update_data["estado_pericia_fecha_entrega"] = None
            case_db.estado = "Activo"
            case_db.fecha_cierre = None
        elif nuevo_estado == "Se represento":
            update_data["estado_pericia_fecha_programada"] = None
            update_data["estado_pericia_fecha_evaluacion"] = None
            update_data["estado_pericia_tiempo_entrega"] = None
            update_data["estado_pericia_fecha_entrega"] = None
        elif nuevo_estado == "En proceso de elaboracion":
            update_data["estado_pericia_fecha_programada"] = None
            update_data["estado_pericia_detalle_representacion"] = None
            update_data["estado_pericia_fecha_entrega"] = None
            case_db.estado = "Activo"
            case_db.fecha_cierre = None
        elif nuevo_estado == "Entregado":
            update_data["estado_pericia_fecha_programada"] = None
            update_data["estado_pericia_detalle_representacion"] = None
            update_data["estado_pericia_fecha_evaluacion"] = None
            update_data["estado_pericia_tiempo_entrega"] = None
            case_db.estado = "Cerrado"
            case_db.fecha_cierre = update_data.get("estado_pericia_fecha_entrega") or date.today()
            
    for field, value in update_data.items():
        setattr(case_db, field, value)
        
    db.commit()
    db.refresh(case_db)
    
    from app.services.logger import create_log
    create_log(
        db=db,
        accion="Actualizar Estado Pericia",
        tabla_afectada="casos",
        registro_id=case_db.id,
        detalles=f"Caso {case_db.codigo_unico} actualizado a '{case_db.estado_pericia}' (Estado General: {case_db.estado})",
        usuario_id=current_user.id
    )
    
    return case_db
