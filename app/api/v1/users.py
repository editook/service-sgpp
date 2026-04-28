from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_admin
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.core.security import get_password_hash

router = APIRouter()

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    *,
    db: Annotated[Session, Depends(get_db)],
    user_id: int,
    user_in: UserUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)]
):
    """
    Actualizar un usuario existente. Si se proporciona contraseña, se resetea.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = user_in.model_dump(exclude_unset=True)
    
    if "password" in update_data and update_data["password"]:
        update_data["password_hash"] = get_password_hash(update_data["password"])
        del update_data["password"]
    elif "password" in update_data:
        del update_data["password"] # Ignore empty passwords

    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)

    from app.services.logger import create_log
    create_log(
        db=db, accion="Actualizar Usuario", tabla_afectada="usuarios",
        registro_id=user.id, detalles=f"Usuario modificado por admin", usuario_id=current_admin.id
    )
    return user

@router.post("/", response_model=UserResponse)
def create_user(
    *,
    db: Annotated[Session, Depends(get_db)],
    user_in: UserCreate,
    current_admin: Annotated[User, Depends(get_current_admin)]
):
    """
    Crear un nuevo usuario (Perito o Admin). Solo el Administrador puede hacer esto.
    """
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado en el sistema.",
        )
    
    user_db = User(
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        nombre_completo=user_in.nombre_completo,
        departamento=user_in.departamento,
        rol=user_in.rol
    )
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    
    from app.services.logger import create_log
    create_log(
        db=db,
        accion="Crear Usuario",
        tabla_afectada="usuarios",
        registro_id=user_db.id,
        detalles=f"Usuario {user_db.username} con rol {user_db.rol} creado",
        usuario_id=current_admin.id
    )
    
    return user_db

@router.get("/", response_model=List[UserResponse])
def get_users(
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(get_current_admin)],
    skip: int = 0,
    limit: int = 100
):
    """
    Listar usuarios. Solo el Administrador puede hacer esto.
    """
    return db.query(User).offset(skip).limit(limit).all()
