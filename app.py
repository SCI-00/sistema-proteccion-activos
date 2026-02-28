"""
Dashboard Frontend - Streamlit
Sistema de Protección de Activos
"""

import streamlit as st
import requests
import os
from datetime import datetime

# Configuración
st.set_page_config(
    page_title="Sistema de Protección de Activos",
    page_icon="🛡️",
    layout="wide"
)

# URL del API
API_URL = os.getenv("API_URL", "http://localhost:8000/api")

# CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1e3a8a;
        font-weight: bold;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None

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
        st.info("**Sistema desarrollado para Victor Manuel De La Torre**")

else:
    # Dashboard Principal
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user['nombre']}")
        st.caption(f"**Rol:** {st.session_state.user['rol']}")
        st.markdown("---")
        
        pagina = st.radio(
            "📊 Módulos",
            ["🏠 Dashboard", "📡 Monitoreo", "💰 Presupuesto", "🔥 Protección Civil"]
        )
        
        st.markdown("---")
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()
    
    # Contenido principal
    if "Dashboard" in pagina:
        st.markdown("<h1 class='main-header'>🏠 Dashboard Principal</h1>", unsafe_allow_html=True)
        
        try:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            response = requests.get(f"{API_URL}/dashboard/stats", headers=headers)
            
            if response.status_code == 200:
                stats = response.json()
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("🏢 Total CEDIS", stats['total_cedis'])
                
                with col2:
                    st.metric("📡 Eventos", stats['total_eventos'])
                
                with col3:
                    st.metric("💰 Gastos del Mes", f"${stats['total_gastos']:,.2f}")
                
                with col4:
                    st.metric("⚠️ Alertas", stats['alertas_activas'])
                
                st.success("✅ Sistema funcionando correctamente")
            else:
                st.error("Error al cargar estadísticas")
        
        except Exception as e:
            st.error(f"Error de conexión: {str(e)}")
            st.info(f"Verificando conexión con: {API_URL}")
    
    elif "Monitoreo" in pagina:
        st.markdown("<h1 class='main-header'>📡 Monitoreo de Seguridad</h1>", unsafe_allow_html=True)
        st.info("Módulo en desarrollo")
    
    elif "Presupuesto" in pagina:
        st.markdown("<h1 class='main-header'>💰 Control Presupuestal</h1>", unsafe_allow_html=True)
        st.info("Módulo en desarrollo")
    
    elif "Protección Civil" in pagina:
        st.markdown("<h1 class='main-header'>🔥 Protección Civil</h1>", unsafe_allow_html=True)
        st.info("Módulo en desarrollo")
    
    st.markdown("---")
    st.caption(f"Sistema de Protección de Activos v1.0.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')} | SCI DE OCCIDENTE")
