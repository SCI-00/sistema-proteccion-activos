"""
Router de Eventos de Seguridad
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import EventoSeguridad, CEDIS
from app.models.usuario import Usuario
from app.schemas import EventoCreate, EventoResponse

router = APIRouter()

@router.get("/", response_model=List[EventoResponse])
def get_eventos(
    skip: int = 0,
    limit: int = 100,
    cedis_id: Optional[int] = None,
    tipo_evento: Optional[str] = None,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener lista de eventos"""
    query = db.query(EventoSeguridad)
    
    # Filtros
    if current_user.rol != "Administrador" and current_user.organizacion_id:
        query = query.filter(EventoSeguridad.organizacion_id == current_user.organizacion_id)
    
    if cedis_id:
        query = query.filter(EventoSeguridad.cedis_id == cedis_id)
    
    if tipo_evento:
        query = query.filter(EventoSeguridad.tipo_evento == tipo_evento)
    
    if fecha_inicio:
        query = query.filter(EventoSeguridad.fecha >= fecha_inicio)
    
    if fecha_fin:
        query = query.filter(EventoSeguridad.fecha <= fecha_fin)
    
    eventos = query.order_by(EventoSeguridad.fecha.desc()).offset(skip).limit(limit).all()
    return eventos

@router.post("/", response_model=EventoResponse)
def create_evento(
    evento_data: EventoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crear nuevo evento"""
    # Extraer fecha para campos adicionales
    fecha = evento_data.fecha
    
    db_evento = EventoSeguridad(
        **evento_data.dict(),
        usuario_registro_id=current_user.id,
        mes=fecha.strftime("%B"),
        dia_semana=fecha.strftime("%A"),
        hora=fecha.strftime("%H:%M")
    )
    
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    
    return db_evento

@router.get("/stats")
def get_eventos_stats(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener estadísticas de eventos"""
    query = db.query(EventoSeguridad)
    
    if current_user.rol != "Administrador" and current_user.organizacion_id:
        query = query.filter(EventoSeguridad.organizacion_id == current_user.organizacion_id)
    
    total = query.count()
    
    # Por tipo
    por_tipo = db.query(
        EventoSeguridad.tipo_evento,
        func.count(EventoSeguridad.id).label('count')
    ).group_by(EventoSeguridad.tipo_evento).all()
    
    # Por mes
    por_mes = db.query(
        extract('month', EventoSeguridad.fecha).label('mes'),
        func.count(EventoSeguridad.id).label('count')
    ).group_by('mes').all()
    
    return {
        "total": total,
        "por_tipo": [{"tipo": t, "count": c} for t, c in por_tipo],
        "por_mes": [{"mes": int(m), "count": c} for m, c in por_mes]
    }
