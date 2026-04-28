from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.extension import Extension
from app.models.case import Case
from app.models.user import User
from app.api.deps import get_current_user, get_current_admin, get_current_perito
from app.schemas.extension import ExtensionCreate, ExtensionResponse, ExtensionUpdate

router = APIRouter()

@router.post("/", response_model=ExtensionResponse)
def apply_extension(
    *,
    db: Annotated[Session, Depends(get_db)],
    extension_in: ExtensionCreate,
    current_user: Annotated[User, Depends(get_current_perito)]
):
    """Solicitar ampliación (Solo Perito dueño del caso)"""
    case = db.query(Case).filter(Case.id == extension_in.caso_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    if case.perito_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos sobre este caso")
    if case.estado == 'Cerrado':
        raise HTTPException(status_code=400, detail="El caso está cerrado")
    if case.ampliacion_solicitada:
        raise HTTPException(status_code=400, detail="Ya se ha solicitado una ampliación para este caso")
        
    ext_db = Extension(**extension_in.model_dump())
    db.add(ext_db)
    
    # Marcar el caso como con ampliación en proceso
    case.ampliacion_solicitada = True
    
    db.commit()
    db.refresh(ext_db)
    return ext_db

@router.get("/", response_model=List[ExtensionResponse])
def get_extensions(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100
):
    """Listar ampliaciones"""
    if current_user.rol == "ADMIN":
        return db.query(Extension).offset(skip).limit(limit).all()
    else:
        # Peritos ven las de sus propios casos
        return db.query(Extension).join(Case).filter(Case.perito_id == current_user.id).offset(skip).limit(limit).all()

@router.put("/{ext_id}/evaluar", response_model=ExtensionResponse)
def evaluate_extension(
    *,
    db: Annotated[Session, Depends(get_db)],
    ext_id: int,
    ext_update: ExtensionUpdate,
    current_user: Annotated[User, Depends(get_current_admin)]
):
    """Admin aprueba o rechaza ampliación"""
    if ext_update.estado not in ['Aprobada', 'Rechazada']:
        raise HTTPException(status_code=400, detail="Estado inválido")
        
    ext = db.query(Extension).filter(Extension.id == ext_id).first()
    if not ext:
        raise HTTPException(status_code=404, detail="Ampliación no encontrada")
    if ext.estado != 'Pendiente':
        raise HTTPException(status_code=400, detail="Esta solicitud ya fue evaluada")
        
    ext.estado = ext_update.estado
    ext.evaluado_por = current_user.id
    
    # Si se aprueba, actualizar los días de vencimiento sumando al plazo inicial
    case = db.query(Case).filter(Case.id == ext.caso_id).first()
    if case and ext_update.estado == 'Aprobada':
        case.plazo_dias += ext.dias_solicitados
    
    # Restablecer el flag de ampliacion, para que pueda volver a pedir otra si lo necesita (o no dependiendo de lógica de negocio)
    # según requerimiento no impide múltiples ampliaciones si fue evaluada pero al fin es decisión
    if case:
        case.ampliacion_solicitada = False 
        
    db.commit()
    db.refresh(ext)
    return ext
