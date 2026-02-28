"""
Configuración de la aplicación
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Sistema Protección Activos API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/proteccion_activos_db"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tu-secret-key-super-seguro-cambiar-en-produccion")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Email (para alertas - fase 2)
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    
    class Config:
        case_sensitive = True

settings = Settings()
