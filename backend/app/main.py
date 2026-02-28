"""
Sistema Integral de Protección de Activos
Backend API - FastAPI
Autor: Desarrollado para Victor Manuel De La Torre
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import engine, Base
from app.routers import auth, cedis, eventos, gastos, proteccion_civil, dashboard

# Crear tablas al inicio
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Iniciando Sistema de Protección de Activos API...")
    yield
    # Shutdown
    print("👋 Cerrando Sistema de Protección de Activos API...")

app = FastAPI(
    title="Sistema Integral de Protección de Activos API",
    description="API para gestión de seguridad, presupuesto y protección civil - SCI DE OCCIDENTE",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(cedis.router, prefix="/api/cedis", tags=["CEDIS"])
app.include_router(eventos.router, prefix="/api/eventos", tags=["Eventos Seguridad"])
app.include_router(gastos.router, prefix="/api/gastos", tags=["Gastos"])
app.include_router(proteccion_civil.router, prefix="/api/proteccion-civil", tags=["Protección Civil"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

@app.get("/")
async def root():
    return {
        "mensaje": "Sistema Integral de Protección de Activos API",
        "version": "1.0.0",
        "cliente": "Victor Manuel De La Torre - SCI DE OCCIDENTE",
        "status": "✅ Operativo",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
