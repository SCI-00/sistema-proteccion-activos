"""
Router de Protección Civil
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Extintor, PIPC, Dictamen, CEDIS
from app.models.usuario import Usuario
from app.schemas import ExtintorCreate, ExtintorResponse, PIPCCreate, PIPCResponse

router = APIRouter()

@router.get("/extintores", response_model=List[ExtintorResponse])
def get_extintores(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener lista de extintores por CEDIS"""
    query = db.query(Extintor)
    extintores = query.all()
    return extintores

@router.get("/extintores/{cedis_id}", response_model=ExtintorResponse)
def get_extintor_cedis(
    cedis_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener extintores de un CEDIS"""
    extintor = db.query(Extintor).filter(Extintor.cedis_id == cedis_id).first()
    if not extintor:
        raise HTTPException(status_code=404, detail="No se encontraron extintores para este CEDIS")
    return extintor

@router.post("/extintores", response_model=ExtintorResponse)
def create_extintor(
    extintor_data: ExtintorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crear/actualizar registro de extintores"""
    # Verificar si ya existe
    existing = db.query(Extintor).filter(Extintor.cedis_id == extintor_data.cedis_id).first()
    
    if existing:
        # Actualizar
        for key, value in extintor_data.dict().items():
            setattr(existing, key, value)
        existing.total_extintores = existing.extintores_pqs + existing.extintores_co2
        existing.cumple = existing.total_extintores >= existing.extintores_requeridos
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Crear
        db_extintor = Extintor(**extintor_data.dict())
        db_extintor.total_extintores = db_extintor.extintores_pqs + db_extintor.extintores_co2
        db_extintor.cumple = db_extintor.total_extintores >= db_extintor.extintores_requeridos
        db.add(db_extintor)
        db.commit()
        db.refresh(db_extintor)
        return db_extintor

@router.get("/pipc", response_model=List[PIPCResponse])
def get_pipcs(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener lista de PIPC"""
    pipcs = db.query(PIPC).all()
    return pipcs

@router.post("/pipc", response_model=PIPCResponse)
def create_pipc(
    pipc_data: PIPCCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crear/actualizar PIPC"""
    existing = db.query(PIPC).filter(PIPC.cedis_id == pipc_data.cedis_id).first()
    
    if existing:
        for key, value in pipc_data.dict().items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        db_pipc = PIPC(**pipc_data.dict())
        db.add(db_pipc)
        db.commit()
        db.refresh(db_pipc)
        return db_pipc

@router.get("/compliance")
def get_compliance_summary(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener resumen de compliance por CEDIS"""
    # Obtener todos los CEDIS
    cedis_list = db.query(CEDIS).all()
    
    resultado = []
    for cedis in cedis_list:
        # Extintores
        extintor = db.query(Extintor).filter(Extintor.cedis_id == cedis.id).first()
        extintores_ok = extintor.cumple if extintor else False
        
        # PIPC
        pipc = db.query(PIPC).filter(PIPC.cedis_id == cedis.id).first()
        pipc_vigente = False
        if pipc and pipc.fecha_vencimiento:
            from datetime import date
            pipc_vigente = pipc.fecha_vencimiento >= date.today()
        
        # Dictámenes
        dictamenes = db.query(Dictamen).filter(Dictamen.cedis_id == cedis.id).all()
        dictamen_estructural = any(d.tipo == "Estructural" and d.estatus == "Vigente" for d in dictamenes)
        dictamen_electrico = any(d.tipo == "Eléctrico" and d.estatus == "Vigente" for d in dictamenes)
        
        # Score de compliance (0-100)
        score = 0
        if extintores_ok:
            score += 25
        if pipc_vigente:
            score += 25
        if dictamen_estructural:
            score += 25
        if dictamen_electrico:
            score += 25
        
        resultado.append({
            "cedis_id": cedis.id,
            "cedis_nombre": cedis.nombre,
            "extintores_cumple": extintores_ok,
            "pipc_vigente": pipc_vigente,
            "dictamen_estructural": dictamen_estructural,
            "dictamen_electrico": dictamen_electrico,
            "compliance_score": score
        })
    
    return resultado
