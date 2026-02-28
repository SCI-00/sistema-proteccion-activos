"""
Router de Gastos
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import date
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Gasto, CategoriaGasto, CEDIS
from app.models.usuario import Usuario
from app.schemas import GastoCreate, GastoResponse

router = APIRouter()

@router.get("/", response_model=List[GastoResponse])
def get_gastos(
    skip: int = 0,
    limit: int = 100,
    cedis_id: Optional[int] = None,
    categoria_id: Optional[int] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener lista de gastos"""
    query = db.query(Gasto)
    
    # Filtros
    if current_user.rol != "Administrador" and current_user.organizacion_id:
        query = query.filter(Gasto.organizacion_id == current_user.organizacion_id)
    
    if cedis_id:
        query = query.filter(Gasto.cedis_id == cedis_id)
    
    if categoria_id:
        query = query.filter(Gasto.categoria_id == categoria_id)
    
    if fecha_inicio:
        query = query.filter(Gasto.fecha >= fecha_inicio)
    
    if fecha_fin:
        query = query.filter(Gasto.fecha <= fecha_fin)
    
    gastos = query.order_by(Gasto.fecha.desc()).offset(skip).limit(limit).all()
    return gastos

@router.post("/", response_model=GastoResponse)
def create_gasto(
    gasto_data: GastoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crear nuevo gasto"""
    db_gasto = Gasto(
        **gasto_data.dict(),
        usuario_registro_id=current_user.id
    )
    
    db.add(db_gasto)
    db.commit()
    db.refresh(db_gasto)
    
    return db_gasto

@router.get("/stats")
def get_gastos_stats(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener estadísticas de gastos"""
    query = db.query(Gasto)
    
    if current_user.rol != "Administrador" and current_user.organizacion_id:
        query = query.filter(Gasto.organizacion_id == current_user.organizacion_id)
    
    # Total
    total = query.with_entities(func.sum(Gasto.monto_total)).scalar() or Decimal(0)
    
    # Por categoría
    por_categoria = db.query(
        CategoriaGasto.nombre,
        func.sum(Gasto.monto_total).label('total')
    ).join(Gasto).group_by(CategoriaGasto.nombre).all()
    
    # Por CEDIS
    por_cedis = db.query(
        CEDIS.nombre,
        func.sum(Gasto.monto_total).label('total')
    ).join(Gasto).group_by(CEDIS.nombre).order_by(func.sum(Gasto.monto_total).desc()).limit(10).all()
    
    # Por mes
    por_mes = db.query(
        extract('month', Gasto.fecha).label('mes'),
        func.sum(Gasto.monto_total).label('total')
    ).group_by('mes').all()
    
    return {
        "total": float(total),
        "por_categoria": [{"categoria": c, "total": float(t)} for c, t in por_categoria],
        "por_cedis": [{"cedis": c, "total": float(t)} for c, t in por_cedis],
        "por_mes": [{"mes": int(m), "total": float(t)} for m, t in por_mes]
    }

@router.get("/categorias", response_model=List[dict])
def get_categorias(db: Session = Depends(get_db)):
    """Obtener categorías de gasto"""
    categorias = db.query(CategoriaGasto).filter(CategoriaGasto.activo == True).all()
    return [{"id": c.id, "nombre": c.nombre, "color": c.color} for c in categorias]
