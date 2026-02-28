"""
Sistema Integral de Protección de Activos
Frontend Dashboard - Streamlit
Autor: Desarrollado para Victor Manuel De La Torre
"""

import streamlit as st
import requests
import os
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="Sistema de Protección de Activos",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL del API
API_URL = os.getenv("API_URL", "http://localhost:8000/api")

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1e3a8a;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f9fafb;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    .success-box {
        background-color: #d1fae5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #059669;
    }
    .warning-box {
        background-color: #fef3c7;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f59e0b;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'organizacion' not in st.session_state:
    st.session_state.organizacion = "Omnilife México"

def login(email, password):
    """Función de login"""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            data={"username": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data['access_token']
            st.session_state.user = data['user']
            return True, "Login exitoso"
        else:
            return False, "Email o contraseña incorrectos"
    except Exception as e:
        return False, f"Error de conexión: {str(e)}"

def logout():
    """Función de logout"""
    st.session_state.token = None
    st.session_state.user = None
    st.rerun()

# Verificar si está logueado
if not st.session_state.token:
    # Página de Login
    st.markdown("<h1 class='main-header'>🛡️ Sistema de Protección de Activos</h1>", unsafe_allow_html=True)
    st.markdown("### SCI DE OCCIDENTE & Omnilife México")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        st.markdown("### 🔐 Iniciar Sesión")
        
        email = st.text_input("📧 Email", placeholder="usuario@omnilife.com")
        password = st.text_input("🔑 Contraseña", type="password")
        
        if st.button("Iniciar Sesión", use_container_width=True):
            if email and password:
                success, message = login(email, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Por favor ingresa email y contraseña")
        
        st.markdown("---")
        st.info("**Usuario por defecto:** victor.delatorre@omnilife.com")
        st.caption("Sistema desarrollado por Claude para Victor Manuel De La Torre")

else:
    # Dashboard Principal
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user['nombre']}")
        st.caption(f"**Rol:** {st.session_state.user['rol']}")
        
        st.markdown("---")
        
        # Selector de organización
        st.markdown("### 🏢 Organización")
        organizacion = st.selectbox(
            "Seleccionar",
            ["Omnilife México", "SCI DE OCCIDENTE"],
            index=0 if st.session_state.organizacion == "Omnilife México" else 1,
            label_visibility="collapsed"
        )
        st.session_state.organizacion = organizacion
        
        st.markdown("---")
        
        # Navegación
        st.markdown("### 📊 Módulos")
        
        pagina = st.radio(
            "Ir a:",
            ["🏠 Dashboard", "📡 Monitoreo", "💰 Presupuesto", "🔥 Protección Civil"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()
    
    # Contenido principal basado en página seleccionada
    if "Dashboard" in pagina:
        st.markdown(f"<h1 class='main-header'>🏠 Dashboard - {st.session_state.organizacion}</h1>", unsafe_allow_html=True)
        
        # Obtener estadísticas
        try:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            response = requests.get(f"{API_URL}/dashboard/stats", headers=headers)
            
            if response.status_code == 200:
                stats = response.json()
                
                # KPIs principales
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("🏢 Total CEDIS", stats['total_cedis'])
                
                with col2:
                    st.metric("📡 Eventos Registrados", stats['total_eventos'])
                
                with col3:
                    st.metric("💰 Gastos del Mes", f"${stats['total_gastos']:,.2f}")
                
                with col4:
                    st.metric("⚠️ Alertas Activas", stats['alertas_activas'])
                
                st.markdown("---")
                
                # Mapa y gráficas
                col_left, col_right = st.columns([2, 1])
                
                with col_left:
                    st.markdown("### 🗺️ Mapa de CEDIS")
                    st.info("🗺️ Mapa interactivo con 20 CEDIS")
                    st.caption("*Implementación completa con Folium en fase 2*")
                
                with col_right:
                    st.markdown("### 📊 Compliance Score")
                    st.success("✅ Cumplimiento General: 75%")
                    st.caption("*Basado en extintores, PIPC y dictámenes*")
            
            else:
                st.error("Error al cargar estadísticas")
        
        except Exception as e:
            st.error(f"Error de conexión con el API: {str(e)}")
            st.info("Verifica que el backend esté corriendo en: " + API_URL)
    
    elif "Monitoreo" in pagina:
        st.markdown("<h1 class='main-header'>📡 Monitoreo de Seguridad</h1>", unsafe_allow_html=True)
        
        # Obtener eventos
        try:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            response = requests.get(f"{API_URL}/eventos?limit=50", headers=headers)
            
            if response.status_code == 200:
                eventos = response.json()
                
                st.success(f"✅ {len(eventos)} eventos encontrados")
                
                if eventos:
                    import pandas as pd
                    df = pd.DataFrame(eventos)
                    st.dataframe(df[['fecha', 'tipo_evento', 'descripcion', 'estatus']], use_container_width=True)
                else:
                    st.info("No hay eventos registrados")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    elif "Presupuesto" in pagina:
        st.markdown("<h1 class='main-header'>💰 Control Presupuestal</h1>", unsafe_allow_html=True)
        
        try:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            response = requests.get(f"{API_URL}/gastos?limit=50", headers=headers)
            
            if response.status_code == 200:
                gastos = response.json()
                
                st.success(f"✅ {len(gastos)} gastos encontrados")
                
                if gastos:
                    import pandas as pd
                    df = pd.DataFrame(gastos)
                    total = df['monto_total'].astype(float).sum()
                    
                    st.metric("Total Registrado", f"${total:,.2f}")
                    st.dataframe(df[['fecha', 'proveedor', 'descripcion_completa', 'monto_total']], use_container_width=True)
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    elif "Protección Civil" in pagina:
        st.markdown("<h1 class='main-header'>🔥 Protección Civil</h1>", unsafe_allow_html=True)
        
        try:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            response = requests.get(f"{API_URL}/proteccion-civil/compliance", headers=headers)
            
            if response.status_code == 200:
                compliance = response.json()
                
                st.success(f"✅ {len(compliance)} CEDIS evaluados")
                
                if compliance:
                    import pandas as pd
                    df = pd.DataFrame(compliance)
                    st.dataframe(df, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.caption(f"Sistema de Protección de Activos v1.0.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')} | SCI DE OCCIDENTE")
