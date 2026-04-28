import os
import hashlib
from typing import Annotated
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.case import Case
from app.models.user import User
from app.api.deps import get_current_perito

router = APIRouter()

UPLOAD_DIR = "uploads/pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def generate_file_hash(file_bytes: bytes) -> str:
    """Genera un hash SHA-256 inmutable del archivo"""
    return hashlib.sha256(file_bytes).hexdigest()

@router.post("/{case_id}/sign-and-close")
async def sign_and_close_case(
    *,
    case_id: int,
    file: UploadFile = File(...),
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_perito)]
):
    """Sube el dictamen pericial en PDF, genera su firma digital (Hash) y Cierra el caso irrevocablemente"""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="El archivo debé ser un documento PDF")
        
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
        
    if case.perito_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso denegado. No eres el perito asignado a este caso.")
        
    if case.estado == 'Cerrado':
        raise HTTPException(status_code=400, detail="Este caso ya fue cerrado y firmado digitalmente.")

    # Lectura y guardado
    file_bytes = await file.read()
    file_hash = generate_file_hash(file_bytes)
    
    file_path = os.path.join(UPLOAD_DIR, f"{case.codigo_unico}_{file_hash[:8]}.pdf")
    with open(file_path, "wb") as buffer:
        buffer.write(file_bytes)
        
    # Actualizar estado a cerrado y congelar en Base de Datos
    case.estado = 'Cerrado'
    case.fecha_cierre = date.today()
    case.archivo_pdf_url = file_path
    case.firma_digital_hash = file_hash
    
    from app.services.logger import create_log
    create_log(
        db=db,
        accion="Cierre de Caso y Firma Digital",
        tabla_afectada="casos",
        registro_id=case.id,
        detalles=f"Hash: {file_hash}",
        usuario_id=current_user.id
    )
    
    db.commit()
    db.refresh(case)
    
    return {
        "mensaje": "Caso cerrado exitosamente.",
        "codigo_unico": case.codigo_unico,
        "firma_digital_hash": file_hash,
        "fecha_cierre": case.fecha_cierre
    }
