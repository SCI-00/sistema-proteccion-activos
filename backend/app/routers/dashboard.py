"""
Router de Dashboard - KPIs y Estadísticas Principales
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import CEDIS, EventoSeguridad, Gasto, Estado, Extintor, PIPC
from app.models.usuario import Usuario
from app.schemas import DashboardStats, CEDISMapa

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener estadísticas principales del dashboard"""
    
    # Total CEDIS
    cedis_query = db.query(CEDIS)
    if current_user.rol != "Administrador" and current_user.organizacion_id:
        cedis_query = cedis_query.filter(CEDIS.organizacion_id == current_user.organizacion_id)
    total_cedis = cedis_query.count()
    
    # Total eventos
    eventos_query = db.query(EventoSeguridad)
    if current_user.rol != "Administrador" and current_user.organizacion_id:
        eventos_query = eventos_query.filter(EventoSeguridad.organizacion_id == current_user.organizacion_id)
    total_eventos = eventos_query.count()
    
    # Total gastos (mes actual)
    inicio_mes = datetime.now().replace(day=1)
    gastos_query = db.query(Gasto).filter(Gasto.fecha >= inicio_mes.date())
    if current_user.rol != "Administrador" and current_user.organizacion_id:
        gastos_query = gastos_query.filter(Gasto.organizacion_id == current_user.organizacion_id)
    total_gastos = gastos_query.with_entities(func.sum(Gasto.monto_total)).scalar() or Decimal(0)
    
    # Alertas activas (vencimientos próximos)
    fecha_limite = (datetime.now() + timedelta(days=30)).date()
    alertas_query = db.query(PIPC).filter(
        PIPC.fecha_vencimiento <= fecha_limite,
        PIPC.fecha_vencimiento >= datetime.now().date()
    )
    alertas_activas = alertas_query.count()
    
    return {
        "total_cedis": total_cedis,
        "total_eventos": total_eventos,
        "total_gastos": total_gastos,
        "alertas_activas": alertas_activas
    }

@router.get("/mapa")
def get_mapa_cedis(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener CEDIS para mapa con coordenadas"""
    
    cedis_query = db.query(CEDIS, Estado.nombre.label('estado_nombre')).join(Estado)
    
    if current_user.rol != "Administrador" and current_user.organizacion_id:
        cedis_query = cedis_query.filter(CEDIS.organizacion_id == current_user.organizacion_id)
    
    cedis_list = cedis_query.all()
    
    resultado = []
    for cedis, estado_nombre in cedis_list:
        # Calcular compliance score
        extintor = db.query(Extintor).filter(Extintor.cedis_id == cedis.id).first()
        pipc = db.query(PIPC).filter(PIPC.cedis_id == cedis.id).first()
        
        score = 0
        if extintor and extintor.cumple:
            score += 50
        if pipc and pipc.fecha_vencimiento and pipc.fecha_vencimiento >= datetime.now().date():
            score += 50
        
        resultado.append({
            "id": cedis.id,
            "nombre": cedis.nombre,
            "estado": estado_nombre,
            "municipio": cedis.municipio,
            "latitud": float(cedis.latitud) if cedis.latitud else None,
            "longitud": float(cedis.longitud) if cedis.longitud else None,
            "compliance_score": score,
            "personal_total": cedis.personal_total
        })
    
    return resultado

@router.get("/tendencias")
def get_tendencias(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener tendencias de eventos y gastos por mes"""
    
    # Eventos por mes (últimos 6 meses)
    seis_meses_atras = datetime.now() - timedelta(days=180)
    
    eventos_query = db.query(
        func.extract('year', EventoSeguridad.fecha).label('año'),
        func.extract('month', EventoSeguridad.fecha).label('mes'),
        func.count(EventoSeguridad.id).label('count')
    ).filter(EventoSeguridad.fecha >= seis_meses_atras)
    
    if current_user.rol != "Administrador" and current_user.organizacion_id:
        eventos_query = eventos_query.filter(EventoSeguridad.organizacion_id == current_user.organizacion_id)
    
    eventos_por_mes = eventos_query.group_by('año', 'mes').order_by('año', 'mes').all()
    
    # Gastos por mes (últimos 6 meses)
    gastos_query = db.query(
        func.extract('year', Gasto.fecha).label('año'),
        func.extract('month', Gasto.fecha).label('mes'),
        func.sum(Gasto.monto_total).label('total')
    ).filter(Gasto.fecha >= seis_meses_atras.date())
    
    if current_user.rol != "Administrador" and current_user.organizacion_id:
        gastos_query = gastos_query.filter(Gasto.organizacion_id == current_user.organizacion_id)
    
    gastos_por_mes = gastos_query.group_by('año', 'mes').order_by('año', 'mes').all()
    
    return {
        "eventos": [
            {"año": int(año), "mes": int(mes), "count": count}
            for año, mes, count in eventos_por_mes
        ],
        "gastos": [
            {"año": int(año), "mes": int(mes), "total": float(total)}
            for año, mes, total in gastos_por_mes
        ]
    }

@router.get("/resumen-cedis/{cedis_id}")
def get_resumen_cedis(
    cedis_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener resumen completo de un CEDIS"""
    
    cedis = db.query(CEDIS).filter(CEDIS.id == cedis_id).first()
    if not cedis:
        return {"error": "CEDIS no encontrado"}
    
    # Eventos del CEDIS
    total_eventos = db.query(EventoSeguridad).filter(EventoSeguridad.cedis_id == cedis_id).count()
    
    # Gastos del CEDIS (año actual)
    inicio_año = datetime.now().replace(month=1, day=1).date()
    total_gastos = db.query(Gasto).filter(
        Gasto.cedis_id == cedis_id,
        Gasto.fecha >= inicio_año
    ).with_entities(func.sum(Gasto.monto_total)).scalar() or Decimal(0)
    
    # Protección Civil
    extintor = db.query(Extintor).filter(Extintor.cedis_id == cedis_id).first()
    pipc = db.query(PIPC).filter(PIPC.cedis_id == cedis_id).first()
    
    return {
        "cedis": {
            "id": cedis.id,
            "nombre": cedis.nombre,
            "codigo": cedis.codigo,
            "municipio": cedis.municipio,
            "personal": cedis.personal_total
        },
        "estadisticas": {
            "total_eventos": total_eventos,
            "total_gastos_año": float(total_gastos)
        },
        "proteccion_civil": {
            "extintores_cumple": extintor.cumple if extintor else False,
            "pipc_estatus": pipc.estatus if pipc else "Pendiente",
            "pipc_vencimiento": pipc.fecha_vencimiento if pipc else None
        }
    }
