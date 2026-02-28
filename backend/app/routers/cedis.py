"""
Router de CEDIS
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import CEDIS, Estado
from app.models.usuario import Usuario
from app.schemas import CEDISCreate, CEDISResponse

router = APIRouter()

@router.get("/", response_model=List[CEDISResponse])
def get_cedis(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener lista de CEDIS"""
    query = db.query(CEDIS)
    
    # Filtrar por organización si no es admin
    if current_user.rol != "Administrador" and current_user.organizacion_id:
        query = query.filter(CEDIS.organizacion_id == current_user.organizacion_id)
    
    # Filtrar por CEDIS asignados
    if current_user.cedis_asignados:
        query = query.filter(CEDIS.id.in_(current_user.cedis_asignados))
    
    cedis = query.offset(skip).limit(limit).all()
    return cedis

@router.get("/{cedis_id}", response_model=CEDISResponse)
def get_cedis_detail(
    cedis_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener detalle de un CEDIS"""
    cedis = db.query(CEDIS).filter(CEDIS.id == cedis_id).first()
    if not cedis:
        raise HTTPException(status_code=404, detail="CEDIS no encontrado")
    
    # Verificar permisos
    if current_user.rol != "Administrador":
        if current_user.organizacion_id != cedis.organizacion_id:
            raise HTTPException(status_code=403, detail="Sin permisos")
        if current_user.cedis_asignados and cedis_id not in current_user.cedis_asignados:
            raise HTTPException(status_code=403, detail="Sin permisos")
    
    return cedis

@router.post("/", response_model=CEDISResponse)
def create_cedis(
    cedis_data: CEDISCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crear nuevo CEDIS"""
    if current_user.rol not in ["Administrador", "Supervisor"]:
        raise HTTPException(status_code=403, detail="Sin permisos")
    
    db_cedis = CEDIS(**cedis_data.dict())
    db.add(db_cedis)
    db.commit()
    db.refresh(db_cedis)
    
    return db_cedis
