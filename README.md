# 🛡️ Sistema Integral de Protección de Activos
## SCI DE OCCIDENTE & Omnilife México

**Cliente:** Victor Manuel De La Torre  
**Zona:** Sureste de México (20 CEDIS)  
**Versión:** 1.0.0  
**Status:** ✅ Listo para Deploy  

---

## 🚀 INICIO RÁPIDO

**Para deploy inmediato, lee:** `DEPLOYMENT_SIMPLE.md`

**Tiempo de deployment:** ~20 minutos  
**Dificultad:** 🟢 Fácil  

---

## 📊 Módulos del Sistema

### 1. **Dashboard Principal**
- KPIs en tiempo real (CEDIS, eventos, gastos, alertas)
- Mapa interactivo de 20 CEDIS
- Selector Omnilife/SCI
- Gráficas de tendencias

### 2. **Monitoreo de Seguridad**
- Registro de eventos (alarmas ADT, actas, servicios)
- Estadísticas por tipo
- Historial completo
- Exportación de datos

### 3. **Control Presupuestal**
- Registro de gastos multi-producto
- Análisis por CEDIS y categoría
- Gráficas de gastos
- Tracking de proveedores

### 4. **Protección Civil**
- Gestión de extintores (cumplimiento NOM)
- PIPC (Programa Interno)
- Dictámenes estructurales/eléctricos
- Score de compliance por CEDIS

---

## 🏗️ Arquitectura Técnica

### Backend (API REST)
```
FastAPI 0.109.0
├── SQLAlchemy (ORM)
├── PostgreSQL 15
├── JWT Authentication
├── Pydantic (Validación)
└── 6 Routers principales
```

### Frontend (Dashboard)
```
Streamlit 1.30.0
├── Plotly (Gráficas)
├── Pandas (Datos)
├── Requests (HTTP)
└── Interface responsiva
```

### Infraestructura
```
Hosting: Render.com ($0/mes - Free Tier)
Base de Datos: Supabase ($0/mes - Free Tier)
Total: $0/mes
```

---

## 📁 Estructura del Proyecto

```
sistema-proteccion-activos/
├── backend/
│   ├── app/
│   │   ├── main.py                 # Aplicación FastAPI
│   │   ├── core/
│   │   │   ├── config.py          # Configuración
│   │   │   ├── database.py        # Conexión BD
│   │   │   └── security.py        # Auth JWT
│   │   ├── models/                # Modelos SQLAlchemy
│   │   ├── schemas/               # Schemas Pydantic
│   │   └── routers/               # Endpoints API
│   │       ├── auth.py            # Login/Logout
│   │       ├── cedis.py           # CRUD CEDIS
│   │       ├── eventos.py         # Eventos
│   │       ├── gastos.py          # Gastos
│   │       ├── proteccion_civil.py
│   │       └── dashboard.py       # KPIs
│   ├── init_database.sql          # Script SQL
│   └── requirements.txt           # Dependencias
│
├── frontend/
│   ├── app.py                     # Dashboard Streamlit
│   └── requirements.txt           # Dependencias
│
├── scripts/
│   └── migrate_data.py            # Migración de Excel
│
├── docs/
│   ├── DEPLOYMENT_SIMPLE.md       # 🚀 GUÍA DE DEPLOY
│   └── SETUP_COMPLETO.md          # Guía detallada
│
├── render.yaml                    # Config Render
├── .env.example                   # Variables de entorno
└── README.md                      # Este archivo
```

---

## 🔧 Deployment

### Opción 1: Render (Recomendado)

**Lee:** `DEPLOYMENT_SIMPLE.md`

**Pasos:**
1. Subir código a GitHub (5 min)
2. Inicializar BD en Supabase (2 min)
3. Deploy en Render (3 min)
4. Crear usuario admin (1 min)
5. ¡Listo! Sistema funcionando

### Opción 2: Local (Desarrollo)

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (nueva terminal)
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

**Requisitos locales:**
- Python 3.11+
- PostgreSQL 15

---

## 🗄️ Base de Datos

### Tablas Principales (32 total):

**Maestras:**
- `organizaciones` - Omnilife & SCI
- `estados` - 6 estados zona sureste
- `cedis` - 20 centros de distribución
- `usuarios` - Control de acceso

**Operativas:**
- `eventos_seguridad` - Monitoreo
- `gastos` - Control presupuestal
- `extintores` - Inventario
- `pipc` - Programa Interno
- `dictamenes` - Estructurales/Eléctricos

**Ver esquema completo:** `backend/init_database.sql`

---

## 🔐 Seguridad

- ✅ Autenticación JWT
- ✅ Passwords hasheados (bcrypt)
- ✅ HTTPS en producción
- ✅ CORS configurado
- ✅ SQL injection prevenida
- ✅ Roles y permisos

**Roles disponibles:**
- Administrador (acceso completo)
- Supervisor (gestión)
- Gerente CEDIS (solo su CEDIS)
- Consulta (solo lectura)

---

## 📊 API Endpoints

**Documentación completa:** `/docs` (Swagger UI)

**Principales endpoints:**
```
POST   /api/auth/login           # Login
POST   /api/auth/register        # Registro
GET    /api/cedis                # Lista CEDIS
GET    /api/eventos              # Lista eventos
POST   /api/eventos              # Crear evento
GET    /api/gastos               # Lista gastos
POST   /api/gastos               # Crear gasto
GET    /api/dashboard/stats      # KPIs
GET    /api/proteccion-civil/compliance  # Compliance
```

---

## 🎨 Características de UI

- ✅ Login/Logout funcional
- ✅ Selector Omnilife/SCI
- ✅ Dashboard con 4 KPIs
- ✅ Tablas interactivas con datos reales
- ✅ Diseño responsivo
- ✅ Colores corporativos
- ✅ Navegación intuitiva

---

## 📦 Migración de Datos

**Script:** `scripts/migrate_data.py`

**Migra desde Excel:**
- 20 CEDIS con todos los datos
- Eventos de seguridad
- Gastos históricos
- Extintores/PIPC/Dictámenes

**Uso:**
```bash
# Configurar DATABASE_URL
export DATABASE_URL="postgresql://..."

# Ejecutar
python scripts/migrate_data.py
```

---

## 🎯 Roadmap

### ✅ Fase 1 - MVP (Semanas 1-2) - COMPLETADA
- Backend API funcional
- Frontend dashboard básico
- Autenticación
- CRUD CEDIS, eventos, gastos
- Protección civil básica
- Deploy en Render

### 🔨 Fase 2 - Inteligencia (Semanas 3-4)
- Monitoreo automatizado 24/7
- Integración SSN, CONAGUA, Atlas Riesgos
- Análisis delictivo SESNSP
- Sistema de alertas email
- Mapas de calor

### 🔨 Fase 3 - Predictivo (Semanas 5-6)
- Machine Learning
- Predicción de riesgos
- Dashboards analíticos avanzados
- Early warning system

### 🔨 Fase 4 - Reportes (Semanas 7-8)
- Generación automática de informes
- Templates personalizados
- Export multi-formato
- Capacitación final

---

## 👥 Equipo

**Cliente:** Victor Manuel De La Torre  
**Empresa:** SCI DE OCCIDENTE  
**Desarrollado por:** Claude (Anthropic AI)  
**Fecha:** Febrero 2026  

---

## 📞 Soporte

**Documentación:**
- DEPLOYMENT_SIMPLE.md - Guía de deploy
- SETUP_COMPLETO.md - Setup detallado
- PORTABILIDAD_Y_PROPIEDAD.md - Migración

**Para problemas:**
1. Ver logs en Render
2. Revisar DEPLOYMENT_SIMPLE.md → Troubleshooting
3. Consultar con Claude en el chat

---

## 📄 Licencia

**Propiedad:** Victor Manuel De La Torre  
**Uso:** Ilimitado para SCI DE OCCIDENTE y Omnilife  
**Código:** Abierto para modificaciones  

---

## 🎉 Estado del Proyecto

```
┌─────────────────────────────────────────┐
│  PROGRESO: 100% ✅                     │
├─────────────────────────────────────────┤
│  ✅ Backend API (100%)                 │
│  ✅ Frontend Dashboard (100%)          │
│  ✅ Base de datos SQL (100%)           │
│  ✅ Scripts migración (100%)           │
│  ✅ Deployment configs (100%)          │
│  ✅ Documentación (100%)               │
└─────────────────────────────────────────┘

STATUS: 🚀 LISTO PARA DEPLOY
PRÓXIMO PASO: Seguir DEPLOYMENT_SIMPLE.md
```

---

**🚀 ¡Sistema completo y listo para producción!**
