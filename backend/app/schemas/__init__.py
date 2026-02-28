"""
Schemas de Pydantic para validación de datos
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

# ============ AUTH ============
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol: str = "Usuario"
    organizacion_id: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
    organizacion_id: Optional[int]
    activo: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# ============ CEDIS ============
class CEDISBase(BaseModel):
    nombre: str
    estado_id: int
    municipio: str
    codigo: str
    superficie_m2: Optional[Decimal] = None
    personal_total: Optional[int] = 0
    gerente: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None

class CEDISCreate(CEDISBase):
    organizacion_id: int

class CEDISResponse(CEDISBase):
    id: int
    organizacion_id: int
    activo: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============ EVENTOS ============
class EventoBase(BaseModel):
    fecha: datetime
    cedis_id: int
    tipo_evento: str
    estado: Optional[str] = None
    descripcion: Optional[str] = None
    observaciones: Optional[str] = None
    responsable: Optional[str] = None
    estatus: Optional[str] = None

class EventoCreate(EventoBase):
    organizacion_id: int

class EventoResponse(EventoBase):
    id: int
    organizacion_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============ GASTOS ============
class GastoBase(BaseModel):
    fecha: date
    cedis_id: int
    categoria_id: Optional[int] = None
    proveedor: Optional[str] = None
    descripcion_completa: Optional[str] = None
    monto_total: Decimal
    metodo_pago: Optional[str] = None
    num_factura: Optional[str] = None
    estado: Optional[str] = "Pendiente"
    notas: Optional[str] = None

class GastoCreate(GastoBase):
    organizacion_id: int

class GastoResponse(GastoBase):
    id: int
    organizacion_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============ PROTECCION CIVIL ============
class ExtintorBase(BaseModel):
    cedis_id: int
    clasificacion_riesgo: Optional[str] = None
    extintores_requeridos: int = 0
    extintores_pqs: int = 0
    extintores_co2: int = 0
    cumple: bool = False
    fecha_recarga: Optional[date] = None
    proveedor: Optional[str] = None
    costo: Optional[Decimal] = None

class ExtintorCreate(ExtintorBase):
    pass

class ExtintorResponse(ExtintorBase):
    id: int
    total_extintores: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PIPCBase(BaseModel):
    cedis_id: int
    fecha_vobo: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    estatus: str = "Pendiente"
    proveedor: Optional[str] = None
    costo: Optional[Decimal] = None

class PIPCCreate(PIPCBase):
    pass

class PIPCResponse(PIPCBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============ DASHBOARD ============
class DashboardStats(BaseModel):
    total_cedis: int
    total_eventos: int
    total_gastos: Decimal
    alertas_activas: int

class CEDISMapa(BaseModel):
    id: int
    nombre: str
    latitud: Optional[Decimal]
    longitud: Optional[Decimal]
    estado: str
    compliance_score: Optional[int] = 0
    
    class Config:
        from_attributes = True
