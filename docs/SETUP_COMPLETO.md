# 🚀 GUÍA DE SETUP COMPLETA
## Sistema Integral de Protección de Activos

**Para:** Victor Manuel De La Torre  
**Fecha:** 28 Febrero 2026  
**Tiempo estimado:** 2-4 horas  

---

## ✅ LO QUE YA TIENES LISTO

En este repositorio ya está TODO el código necesario:

```
sistema-proteccion-activos/
├── 📂 backend/              ✅ API FastAPI completa
├── 📂 frontend/             ✅ Dashboard Streamlit
├── 📂 scripts/              ✅ Scripts de migración y utilidades
├── 📂 docs/                 ✅ Documentación
├── 📄 init_database.sql     ✅ Script de base de datos
├── 📄 docker-compose.yml    ✅ Configuración Docker
└── 📄 README.md             ✅ Información del proyecto
```

---

## 📋 PRERREQUISITOS

Antes de empezar, necesitas:

- ✅ Una cuenta de email (Gmail - ya tienes: delatorrev0@gmail.com)
- ✅ Conexión a internet
- ✅ Navegador web (Chrome/Edge/Firefox)
- ⏰ 2-4 horas de tiempo

**NO necesitas:**
- ❌ Saber programar
- ❌ Instalar nada en tu computadora (todo es en la nube)
- ❌ Conocimientos técnicos avanzados

---

## 🎯 OPCIÓN 1: SETUP RÁPIDO EN LA NUBE (RECOMENDADO)

**Tiempo:** 1-2 horas  
**Costo:** $200 MXN/mes  
**Dificultad:** 🟢 Fácil  

### PASO 1: Crear Cuenta en Supabase (Base de Datos)

1. **Ir a:** https://supabase.com
2. **Click en:** "Start your project"
3. **Crear cuenta con:** delatorrev0@gmail.com
4. **Crear nuevo proyecto:**
   - Name: `proteccion-activos-db`
   - Database Password: *Crear un password fuerte y guardarlo*
   - Region: South America (São Paulo)
   - Plan: Free (suficiente para empezar)
5. **Click:** "Create new project"
6. **Esperar:** 2-3 minutos mientras se crea

7. **Obtener credenciales:**
   - Ir a: Settings → Database
   - Copiar: Connection String (URI)
   - Se verá así: `postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres`
   - **GUARDAR ESTO** - Lo necesitarás después

### PASO 2: Inicializar Base de Datos

1. **En Supabase**, ir a: SQL Editor
2. **Copiar TODO el contenido** del archivo `backend/init_database.sql`
3. **Pegar** en el editor SQL de Supabase
4. **Click:** "Run"
5. **Esperar:** 10-30 segundos
6. **Verificar:** Deberías ver "Success. No rows returned"

7. **Verificar tablas creadas:**
   - Ir a: Table Editor
   - Deberías ver: `cedis`, `eventos_seguridad`, `gastos`, etc.
   - Si ves las tablas: ✅ ¡Éxito!

### PASO 3: Crear Cuenta en Render.com (Hosting)

1. **Ir a:** https://render.com
2. **Click:** "Get Started"
3. **Crear cuenta con:** GitHub (o email delatorrev0@gmail.com)
4. **Verificar** email si es necesario

### PASO 4: Subir Código a GitHub

**Opción A - Vía Web (Más fácil):**

1. **Ir a:** https://github.com
2. **Crear cuenta** si no tienes (o login)
3. **Click:** "+" → "New repository"
4. **Configurar:**
   - Repository name: `sistema-proteccion-activos`
   - Private: ✅ (seleccionar)
   - Click: "Create repository"

5. **Subir archivos:**
   - Click: "uploading an existing file"
   - **Arrastrar TODA la carpeta** `sistema-proteccion-activos`
   - Click: "Commit changes"

**Opción B - Vía Git (Si sabes usar Git):**

```bash
cd sistema-proteccion-activos
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TU-USUARIO/sistema-proteccion-activos.git
git push -u origin main
```

### PASO 5: Deploy del Backend en Render

1. **En Render.com**, click: "New +" → "Web Service"
2. **Conectar** tu repositorio de GitHub
3. **Seleccionar:** `sistema-proteccion-activos`
4. **Configurar:**
   - Name: `proteccion-activos-api`
   - Environment: Python 3
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Plan: Free (suficiente para empezar)

5. **Variables de Entorno** (Environment Variables):
   - Click: "Advanced" → "Add Environment Variable"
   - Agregar estas variables:

   ```
   DATABASE_URL = [Tu connection string de Supabase]
   SECRET_KEY = [Generar un string random de 32 caracteres]
   SMTP_USER = delatorrev0@gmail.com
   SMTP_PASSWORD = [App Password de Gmail - ver instrucciones abajo]
   ```

6. **Click:** "Create Web Service"
7. **Esperar:** 5-10 minutos mientras hace el deploy
8. **Verificar:**
   - Status debe decir: "Live"
   - Copiar la URL (ej: https://proteccion-activos-api.onrender.com)

### PASO 6: Deploy del Frontend en Render

1. **En Render**, click: "New +" → "Web Service" (otra vez)
2. **Seleccionar** el mismo repositorio
3. **Configurar:**
   - Name: `proteccion-activos-dashboard`
   - Environment: Python 3
   - Build Command: `pip install -r frontend/requirements.txt`
   - Start Command: `cd frontend && streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
   - Plan: Free

4. **Variables de Entorno:**
   ```
   API_URL = [URL del backend del paso anterior]
   ```

5. **Click:** "Create Web Service"
6. **Esperar:** 5-10 minutos
7. **Verificar:**
   - Status: "Live"
   - Copiar URL (ej: https://proteccion-activos-dashboard.onrender.com)
   - **ESTA ES TU URL DEL SISTEMA** ✅

### PASO 7: Crear Usuario Administrador

1. **En tu navegador**, ir a la URL del backend + `/docs`
   - Ejemplo: https://proteccion-activos-api.onrender.com/docs

2. **Buscar:** POST `/auth/register`
3. **Click:** "Try it out"
4. **Llenar:**
   ```json
   {
     "nombre": "Victor Manuel De La Torre",
     "email": "victor.delatorre@omnilife.com",
     "password": "[TU PASSWORD SEGURO]",
     "rol": "Administrador"
   }
   ```

5. **Click:** "Execute"
6. **Verificar:** Response Code 200

### PASO 8: Migrar Tus Datos

**Opción A - Desde tu computadora local:**

1. **Instalar Python** (si no lo tienes): https://python.org
2. **Abrir terminal/CMD**
3. **Navegar** a la carpeta del proyecto:
   ```bash
   cd sistema-proteccion-activos
   ```

4. **Instalar dependencias:**
   ```bash
   pip install pandas openpyxl psycopg2-binary
   ```

5. **Configurar DATABASE_URL:**
   ```bash
   # Windows CMD:
   set DATABASE_URL="[Tu connection string de Supabase]"
   
   # Windows PowerShell:
   $env:DATABASE_URL="[Tu connection string]"
   
   # Mac/Linux:
   export DATABASE_URL="[Tu connection string]"
   ```

6. **Ejecutar migración:**
   ```bash
   python scripts/migrate_data.py
   ```

7. **Ver progreso:**
   - Deberías ver mensajes de "✅ X CEDIS migrados"
   - "✅ X gastos migrados"
   - etc.

**Opción B - Desde Render (más simple pero requiere upload de archivos):**

1. En Render, ir a tu Backend Service
2. Shell → Connect
3. Subir archivos Excel al servicio
4. Ejecutar script de migración

### PASO 9: ¡Acceder al Sistema!

1. **Ir a:** La URL de tu dashboard (del Paso 6)
2. **Login con:**
   - Email: victor.delatorre@omnilife.com
   - Password: [El que creaste en Paso 7]

3. **¡LISTO! Deberías ver el dashboard funcionando** ✅

---

## 🎯 OPCIÓN 2: SETUP LOCAL (Para Desarrollo/Testing)

**Tiempo:** 2-3 horas  
**Costo:** $0  
**Dificultad:** 🟡 Media  

### PASO 1: Instalar Prerrequisitos

1. **Python 3.11+**
   - Descargar: https://python.org
   - Verificar: `python --version`

2. **PostgreSQL 15**
   - Descargar: https://www.postgresql.org/download/
   - Instalar con las opciones por defecto
   - Recordar el password que configures

3. **Git** (opcional pero recomendado)
   - Descargar: https://git-scm.com

### PASO 2: Configurar Base de Datos Local

1. **Abrir pgAdmin** (se instala con PostgreSQL)
2. **Crear nueva base de datos:**
   - Right-click: Databases → Create → Database
   - Name: `proteccion_activos_db`
   - Owner: postgres
   - Save

3. **Ejecutar script de inicialización:**
   - Right-click en tu nueva base de datos
   - Query Tool
   - Abrir archivo: `backend/init_database.sql`
   - Click: Execute (▶️)

### PASO 3: Instalar Dependencias Python

```bash
cd sistema-proteccion-activos

# Backend
cd backend
pip install -r requirements.txt

# Frontend  
cd ../frontend
pip install -r requirements.txt
```

### PASO 4: Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# .env
DATABASE_URL=postgresql://postgres:TU_PASSWORD@localhost:5432/proteccion_activos_db
SECRET_KEY=tu-secret-key-super-seguro-de-32-caracteres
SMTP_USER=delatorrev0@gmail.com
SMTP_PASSWORD=tu-app-password-gmail
```

### PASO 5: Migrar Datos

```bash
cd sistema-proteccion-activos
export DATABASE_URL="postgresql://postgres:PASSWORD@localhost:5432/proteccion_activos_db"
python scripts/migrate_data.py
```

### PASO 6: Iniciar Backend

```bash
cd backend
uvicorn app.main:app --reload
```

Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### PASO 7: Iniciar Frontend (Nueva terminal)

```bash
cd frontend
streamlit run app.py
```

Deberías ver:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### PASO 8: Acceder al Sistema

1. **Abrir navegador:** http://localhost:8501
2. **Login** con credenciales de administrador
3. **¡Listo!**

---

## 📧 CONFIGURAR GMAIL PARA ALERTAS

### Obtener App Password de Gmail:

1. **Ir a:** https://myaccount.google.com/security
2. **Buscar:** "App passwords" o "Contraseñas de aplicaciones"
3. **Crear** nueva app password:
   - App: Mail
   - Device: Other (Sistema Protección Activos)
4. **Google te da un password de 16 caracteres**
5. **Copiar** este password
6. **Usar** este password en la variable `SMTP_PASSWORD`

---

## 🐛 TROUBLESHOOTING

### Problema: "No se puede conectar a la base de datos"

**Solución:**
- Verificar que DATABASE_URL esté correctamente configurada
- Verificar que PostgreSQL esté corriendo
- Verificar usuario/password

### Problema: "ModuleNotFoundError"

**Solución:**
```bash
pip install -r requirements.txt
```

### Problema: "El frontend no carga"

**Solución:**
- Verificar que el backend esté corriendo primero
- Verificar que API_URL esté correctamente configurada
- Ver logs en la terminal

### Problema: "No puedo hacer login"

**Solución:**
- Crear usuario admin primero (Paso 7 de Opción 1)
- Verificar credenciales
- Ver logs del backend para más detalles

---

## 📞 SIGUIENTE PASO

Una vez que tengas el sistema funcionando:

1. **Probar todas las funcionalidades**
2. **Reportar cualquier bug o sugerencia**
3. **Preparar para la demo del Lunes 3 Marzo - 10:00 AM**

---

## 🎁 ARCHIVOS ÚTILES

```
docs/
├── API.md                  # Documentación de API
├── MANUAL_USUARIO.md       # Manual de usuario  
└── TROUBLESHOOTING.md      # Solución de problemas

scripts/
├── migrate_data.py         # Migración de datos
├── backup_db.py            # Backup de base de datos
└── export_everything.py    # Exportar todo el sistema
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

Marca cada paso cuando lo completes:

**Setup en la Nube:**
- [ ] Cuenta en Supabase creada
- [ ] Base de datos inicializada
- [ ] Cuenta en Render creada
- [ ] Código subido a GitHub
- [ ] Backend desplegado en Render
- [ ] Frontend desplegado en Render
- [ ] Usuario administrador creado
- [ ] Datos migrados
- [ ] Sistema accesible vía web
- [ ] Login funciona

**Verificación Final:**
- [ ] Dashboard carga correctamente
- [ ] Puedo ver los CEDIS en el mapa
- [ ] Puedo ver eventos de seguridad
- [ ] Puedo ver gastos
- [ ] Puedo registrar nuevo evento
- [ ] Las gráficas se muestran correctamente

---

**¡ESTÁS LISTO PARA LA DEMO DEL LUNES!** 🚀

---

**Creado:** 28 Febrero 2026  
**Para:** Victor Manuel De La Torre  
**Soporte:** Este chat de Claude
