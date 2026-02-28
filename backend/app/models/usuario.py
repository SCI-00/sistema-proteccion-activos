"""
Modelo de Usuario
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    
    rol = Column(String(50), nullable=False, default="Usuario")
    # Roles: Administrador, Supervisor, Gerente CEDIS, Consulta
    
    organizacion_id = Column(Integer, nullable=True)
    cedis_asignados = Column(String, nullable=True)
    permisos = Column(String, nullable=True)
    
    activo = Column(Boolean, default=True)
    ultimo_login = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
