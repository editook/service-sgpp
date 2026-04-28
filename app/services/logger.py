from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Request
from app.models.log import Log

def create_log(
    db: Session,
    accion: str,
    tabla_afectada: str,
    registro_id: Optional[int] = None,
    detalles: Optional[str] = None,
    usuario_id: Optional[int] = None,
    request: Optional[Request] = None
):
    ip_address = None
    if request:
        ip_address = request.client.host if request.client else None
        
    log_entry = Log(
        usuario_id=usuario_id,
        accion=accion,
        tabla_afectada=tabla_afectada,
        registro_id=registro_id,
        detalles=detalles,
        ip_address=ip_address
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
