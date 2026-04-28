from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.case import Case
from app.models.user import User
from app.api.deps import get_current_user, get_current_admin
from app.schemas.case import CaseCreate, CaseResponse, CaseUpdateEstadoPericia

router = APIRouter()

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
    limit: int = 100
):
    """Listar casos. ADMIN ve todos. PERITO ve solo los suyos."""
    if current_user.rol == "ADMIN":
        casos = db.query(Case).options(joinedload(Case.perito)).offset(skip).limit(limit).all()
    else:
        casos = db.query(Case).options(joinedload(Case.perito)).filter(Case.perito_id == current_user.id).offset(skip).limit(limit).all()
    return casos

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
        
    # Solo el perito asignado o un ADMIN puede modificar el caso
    if current_user.rol != "ADMIN" and case_db.perito_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos para modificar este caso")
        
    update_data = case_in.model_dump(exclude_unset=True)
    
    # Vaciar/limpiar campos según el nuevo estado para no mantener datos viejos
    if "estado_pericia" in update_data:
        nuevo_estado = update_data["estado_pericia"]
        
        if nuevo_estado == "Se programo":
            update_data["estado_pericia_detalle_representacion"] = None
            update_data["estado_pericia_fecha_evaluacion"] = None
            update_data["estado_pericia_tiempo_entrega"] = None
            update_data["estado_pericia_fecha_entrega"] = None
        elif nuevo_estado == "Se represento":
            update_data["estado_pericia_fecha_programada"] = None
            update_data["estado_pericia_fecha_evaluacion"] = None
            update_data["estado_pericia_tiempo_entrega"] = None
            update_data["estado_pericia_fecha_entrega"] = None
        elif nuevo_estado == "Se evaluó":
            update_data["estado_pericia_fecha_programada"] = None
            update_data["estado_pericia_detalle_representacion"] = None
            update_data["estado_pericia_tiempo_entrega"] = None
            update_data["estado_pericia_fecha_entrega"] = None
        elif nuevo_estado == "En proceso de elaboracion":
            update_data["estado_pericia_fecha_programada"] = None
            update_data["estado_pericia_detalle_representacion"] = None
            update_data["estado_pericia_fecha_evaluacion"] = None
            update_data["estado_pericia_fecha_entrega"] = None
        elif nuevo_estado == "Entregado":
            update_data["estado_pericia_fecha_programada"] = None
            update_data["estado_pericia_detalle_representacion"] = None
            update_data["estado_pericia_fecha_evaluacion"] = None
            update_data["estado_pericia_tiempo_entrega"] = None
            
    for field, value in update_data.items():
        setattr(case_db, field, value)
        
    db.add(case_db)
    db.commit()
    db.refresh(case_db)
    
    from app.services.logger import create_log
    create_log(
        db=db,
        accion="Actualizar Estado Pericia",
        tabla_afectada="casos",
        registro_id=case_db.id,
        detalles=f"Estado de pericia actualizado a {case_db.estado_pericia}",
        usuario_id=current_user.id
    )
    
    return case_db
