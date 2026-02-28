"""
Modelos principales del sistema
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ARRAY, JSON, Float, Date, ForeignKey, Text, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Organizacion(Base):
    __tablename__ = "organizaciones"
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text)
    logo_url = Column(Text)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Estado(Base):
    __tablename__ = "estados"
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    codigo = Column(String(10))
    zona_sismica = Column(Boolean, default=False)
    zona_costera = Column(Boolean, default=False)

class CEDIS(Base):
    __tablename__ = "cedis"
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    estado_id = Column(Integer, ForeignKey("estados.id"))
    municipio = Column(String(100), nullable=False)
    direccion = Column(Text)
    cp = Column(String(10))
    superficie_m2 = Column(DECIMAL(10, 2))
    personal_total = Column(Integer, default=0)
    gerente = Column(String(150))
    correo = Column(String(150))
    telefono = Column(String(20))
    latitud = Column(DECIMAL(10, 6))
    longitud = Column(DECIMAL(10, 6))
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"))
    activo = Column(Boolean, default=True)
    notas = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class EventoSeguridad(Base):
    __tablename__ = "eventos_seguridad"
    
    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, nullable=False)
    cedis_id = Column(Integer, ForeignKey("cedis.id"))
    tipo_evento = Column(String(100), nullable=False)
    estado = Column(String(50))
    descripcion = Column(Text)
    observaciones = Column(Text)
    datos_especificos = Column(JSON)
    hora = Column(String(10))
    mes = Column(String(20))
    dia_semana = Column(String(20))
    responsable = Column(String(150))
    estatus = Column(String(50))
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"))
    usuario_registro_id = Column(Integer)
    archivos_adjuntos = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class CategoriaGasto(Base):
    __tablename__ = "categorias_gasto"
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text)
    color = Column(String(20))
    icono = Column(String(50))
    orden = Column(Integer, default=999)
    activo = Column(Boolean, default=True)

class Gasto(Base):
    __tablename__ = "gastos"
    
    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False)
    cedis_id = Column(Integer, ForeignKey("cedis.id"))
    categoria_id = Column(Integer, ForeignKey("categorias_gasto.id"))
    subcategoria_id = Column(Integer)
    proveedor = Column(String(200))
    descripcion_completa = Column(Text)
    monto_total = Column(DECIMAL(10, 2), nullable=False)
    metodo_pago = Column(String(50))
    num_factura = Column(String(100))
    estado = Column(String(50), default='Pendiente')
    notas = Column(Text)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"))
    usuario_registro_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Extintor(Base):
    __tablename__ = "extintores"
    
    id = Column(Integer, primary_key=True)
    cedis_id = Column(Integer, ForeignKey("cedis.id"), unique=True)
    clasificacion_riesgo = Column(String(50))
    extintores_requeridos = Column(Integer, default=0)
    extintores_pqs = Column(Integer, default=0)
    extintores_co2 = Column(Integer, default=0)
    total_extintores = Column(Integer, default=0)
    cumple = Column(Boolean, default=False)
    fecha_recarga = Column(Date)
    proveedor = Column(String(200))
    costo = Column(DECIMAL(10, 2))
    observaciones = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class PIPC(Base):
    __tablename__ = "pipc"
    
    id = Column(Integer, primary_key=True)
    cedis_id = Column(Integer, ForeignKey("cedis.id"), unique=True)
    fecha_vobo = Column(Date)
    fecha_vencimiento = Column(Date)
    estatus = Column(String(50), default='Pendiente')
    proveedor = Column(String(200))
    costo = Column(DECIMAL(10, 2))
    archivo_url = Column(Text)
    observaciones = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Dictamen(Base):
    __tablename__ = "dictamenes"
    
    id = Column(Integer, primary_key=True)
    cedis_id = Column(Integer, ForeignKey("cedis.id"))
    tipo = Column(String(50), nullable=False)  # 'Estructural' o 'Eléctrico'
    tiene_dictamen = Column(Boolean, default=False)
    estatus = Column(String(50))
    fecha_emision = Column(Date)
    fecha_vencimiento = Column(Date)
    proveedor = Column(String(200))
    costo = Column(DECIMAL(10, 2))
    archivo_url = Column(Text)
    observaciones = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
