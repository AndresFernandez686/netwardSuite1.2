"""
BusinessSuite - Suite de Aplicaciones de Negocio
Sistema unificado de Gestión de Inventario y Cálculo de Nómina

Autor: Desarrollado con GitHub Copilot
Versión: 1.0
Fecha: Noviembre 2025
"""

import streamlit as st
import sys
import os

# Configurar paths para importar módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'modules'))
sys.path.insert(0, os.path.join(current_dir, 'modules', 'inventory'))
sys.path.insert(0, os.path.join(current_dir, 'modules', 'payroll'))
sys.path.insert(0, os.path.join(current_dir, 'shared'))

# Sistema de autenticación no necesario - va directo al módulo de inventario
# El módulo de inventario tiene su propio sistema de login

# Configuración de página responsive
st.set_page_config(
    page_title="BusinessSuite - Suite de Negocio",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="auto",  # Auto se adapta mejor a móviles
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "BusinessSuite v1.0 - Sistema empresarial responsive"
    }
)

def detect_mobile_device():
    """Detecta si el usuario está en un dispositivo móvil"""
    # Usar JavaScript para detectar el tamaño de pantalla
    mobile_js = """
    <script>
    function detectMobile() {
        const isMobile = window.innerWidth <= 768;
        const isTouch = 'ontouchstart' in window;
        return isMobile || isTouch;
    }
    
    // Enviar información al servidor
    if (detectMobile()) {
        document.body.classList.add('mobile-device');
    }
    
    // Ajustar viewport para móviles
    const viewport = document.querySelector('meta[name=viewport]');
    if (!viewport) {
        const meta = document.createElement('meta');
        meta.name = 'viewport';
        meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=5.0';
        document.getElementsByTagName('head')[0].appendChild(meta);
    }
    </script>
    """
    st.markdown(mobile_js, unsafe_allow_html=True)

def load_custom_css():
    """Carga estilos CSS personalizados con soporte responsive completo"""
    st.markdown("""
    <style>
    /* Reset y configuración base */
    * {
        box-sizing: border-box;
    }
    
    /* Estilos principales responsive */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        word-break: break-word;
        overflow-wrap: break-word;
    }
    
    .main-header h1 {
        font-size: clamp(1.5rem, 4vw, 2.5rem);
        margin: 0.5rem 0;
        line-height: 1.2;
    }
    
    .main-header p {
        font-size: clamp(0.9rem, 2.5vw, 1.1rem);
        margin: 0.3rem 0;
    }
    
    .main-header small {
        font-size: clamp(0.8rem, 2vw, 0.9rem);
    }
    
    .metric-card {
        background: white;
        padding: clamp(1rem, 3vw, 1.5rem);
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        word-break: break-word;
        overflow-wrap: break-word;
        min-height: auto;
    }
    
    .metric-card h2, .metric-card h3 {
        font-size: clamp(1rem, 3vw, 1.3rem);
        margin: 0.5rem 0;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: clamp(1rem, 3vw, 1.5rem);
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #e1e5e9;
        transition: transform 0.2s;
        word-break: break-word;
        overflow-wrap: break-word;
    }
    
    .feature-card h3 {
        font-size: clamp(1.1rem, 3.5vw, 1.4rem);
        margin-bottom: 0.8rem;
    }
    
    .feature-card p {
        font-size: clamp(0.9rem, 2.5vw, 1rem);
        line-height: 1.4;
    }
    
    .feature-card ul {
        padding-left: 1.2rem;
    }
    
    .feature-card li {
        font-size: clamp(0.85rem, 2.3vw, 0.95rem);
        margin-bottom: 0.3rem;
        line-height: 1.3;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .permission-badge, .restricted-badge {
        color: white;
        padding: 0.3rem 0.7rem;
        border-radius: 15px;
        font-size: clamp(0.7rem, 2vw, 0.8rem);
        margin: 0.2rem;
        display: inline-block;
        word-break: normal;
        white-space: nowrap;
    }
    
    .permission-badge {
        background: #28a745;
    }
    
    .restricted-badge {
        background: #dc3545;
    }
    
    /* Responsive para botones */
    .stButton > button {
        width: 100% !important;
        padding: 0.6rem 1rem !important;
        font-size: clamp(0.9rem, 2.5vw, 1rem) !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        word-break: break-word !important;
        white-space: normal !important;
        height: auto !important;
        min-height: 44px !important;
    }
    
    /* Sidebar responsive */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Animaciones */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Media queries para dispositivos móviles */
    @media (max-width: 768px) {
        .main-header {
            padding: 0.8rem;
            margin-bottom: 1.5rem;
        }
        
        .metric-card {
            padding: 1rem;
            margin-bottom: 0.8rem;
        }
        
        .feature-card {
            padding: 1rem;
            margin-bottom: 0.8rem;
        }
        
        .feature-card ul {
            padding-left: 1rem;
        }
        
        /* Ajustes para texto largo en móviles */
        h1, h2, h3, h4, h5, h6 {
            word-break: break-word !important;
            overflow-wrap: break-word !important;
            hyphens: auto !important;
        }
        
        p, span, div {
            word-break: break-word !important;
            overflow-wrap: break-word !important;
            hyphens: auto !important;
        }
        
        /* Botones más grandes en móvil */
        .stButton > button {
            min-height: 48px !important;
            padding: 0.8rem 1rem !important;
        }
        
        /* Selectbox responsive */
        .stSelectbox > div > div {
            word-break: break-word !important;
        }
        
        /* Tabs responsive */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 0.9rem !important;
            padding: 0.5rem !important;
            word-break: break-word !important;
        }
    }
    
    @media (max-width: 480px) {
        .main-header {
            padding: 0.6rem;
            border-radius: 8px;
        }
        
        .metric-card, .feature-card {
            padding: 0.8rem;
            border-radius: 8px;
        }
        
        .permission-badge, .restricted-badge {
            font-size: 0.7rem;
            padding: 0.2rem 0.5rem;
        }
        
        /* Ajustes adicionales para pantallas muy pequeñas */
        .stButton > button {
            min-height: 50px !important;
            font-size: 0.9rem !important;
        }
        
        /* Sidebar en móvil */
        .sidebar .sidebar-content {
            width: 100% !important;
        }
    }
    
    /* Mejoras adicionales para accesibilidad móvil */
    @media (hover: none) and (pointer: coarse) {
        .feature-card:hover {
            transform: none;
        }
        
        .stButton > button:hover {
            transform: scale(0.98);
        }
    }
    
    /* Soporte para orientación */
    @media (orientation: portrait) and (max-width: 768px) {
        .main-header h1 {
            font-size: clamp(1.3rem, 5vw, 2rem);
        }
    }
    
    @media (orientation: landscape) and (max-height: 500px) {
        .main-header {
            padding: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .metric-card, .feature-card {
            padding: 0.8rem;
            margin-bottom: 0.6rem;
        }
    }
    
    /* Optimización para carga en dispositivos lentos */
    .feature-card, .metric-card {
        will-change: auto;
    }
    
    /* Evitar overflow horizontal */
    .main > div {
        max-width: 100vw;
        overflow-x: hidden;
    }
    
    /* Mejorar legibilidad en pantallas pequeñas */
    @media (max-width: 600px) {
        .stMarkdown {
            line-height: 1.5 !important;
        }
        
        .stMarkdown p {
            margin-bottom: 1rem !important;
        }
        
        .stMarkdown ul, .stMarkdown ol {
            padding-left: 1.2rem !important;
        }
        
        /* Hacer que las columnas se stackeen en móvil */
        .element-container .stColumns {
            flex-direction: column !important;
        }
        
        .element-container .stColumns > div {
            width: 100% !important;
            margin-bottom: 1rem !important;
        }
    }
    
    /* Mejoras adicionales para UX móvil */
    @media (max-width: 768px) {
        /* Espaciado optimizado para móvil */
        .block-container {
            padding-top: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        /* Headers más compactos en móvil */
        .stMarkdown h1 {
            font-size: 1.8rem !important;
            margin-bottom: 1rem !important;
        }
        
        .stMarkdown h2 {
            font-size: 1.5rem !important;
            margin-bottom: 0.8rem !important;
        }
        
        .stMarkdown h3 {
            font-size: 1.3rem !important;
            margin-bottom: 0.6rem !important;
        }
        
        /* Inputs más grandes en móvil */
        .stTextInput > div > div > input {
            min-height: 44px !important;
            font-size: 16px !important; /* Previene zoom en iOS */
        }
        
        .stSelectbox > div > div {
            min-height: 44px !important;
        }
        
        /* Expandir elementos en móvil */
        .stExpander {
            border-radius: 8px !important;
        }
        
        .stExpander > div > div {
            padding: 1rem !important;
        }
    }
    
    /* Optimizaciones para touch */
    @media (hover: none) {
        .stButton > button {
            min-height: 48px !important;
            touch-action: manipulation !important;
        }
        
        .feature-card {
            cursor: default !important;
        }
    }
    
    /* Landscape móvil */
    @media (max-height: 500px) and (orientation: landscape) {
        .main-header {
            padding: 0.5rem !important;
            margin-bottom: 0.8rem !important;
        }
        
        .main-header h1 {
            font-size: 1.5rem !important;
        }
        
        .metric-card, .feature-card {
            padding: 0.7rem !important;
            margin-bottom: 0.5rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def show_main_dashboard():
    """Muestra el dashboard principal del BusinessSuite"""
    
    # Header principal
    st.markdown("""
    <div class="main-header fade-in">
        <h1>🏢 BusinessSuite</h1>
        <p>Suite Completo de Aplicaciones de Negocio</p>
        <small>Gestión de Inventario • Cálculo de Nómina • Reportes Avanzados</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Obtener información del usuario
    user_info = st.session_state.get('user_info', {})
    user_role = user_info.get('role', 'guest')
    user_permissions = user_info.get('permissions', [])
    
    # Sección de métricas del sistema
    st.markdown("### 📊 **Panel de Control**")
    
    # Responsive columns: 4 en desktop, 2 en tablet, 1 en móvil
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>👤 Usuario Activo</h3>
            <h2 style="color: #667eea;">{}</h2>
            <p>{}</p>
        </div>
        """.format(user_info.get('name', 'Invitado'), 
                  "👑 Administrador" if user_role == 'admin' else "👨‍💼 Empleado"), 
        unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📦 Módulos</h3>
            <h2 style="color: #28a745;">2</h2>
            <p>Inventario y Nómina</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🔐 Permisos</h3>
            <h2 style="color: #ffc107;">{}</h2>
            <p>Funciones disponibles</p>
        </div>
        """.format(len(user_permissions)), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>⏰ Sesión</h3>
            <h2 style="color: #17a2b8;">Activa</h2>
            <p>Sistema operativo</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sección de módulos disponibles
    st.markdown("### 🚀 **Módulos Disponibles**")
    
    # Responsive: 2 columnas en desktop, 1 en móvil
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Módulo de Inventario
        inventory_available = 'inventory' in user_permissions
        
        st.markdown(f"""
        <div class="feature-card">
            <h3>📦 Gestión de Inventario</h3>
            <p><strong>Sistema completo de inventario multi-tienda</strong></p>
            <ul>
                <li>📊 Control de stock en tiempo real</li>
                <li>🏪 Gestión multi-tienda</li>
                <li>🚚 Sistema de delivery</li>
                <li>📈 Reportes y métricas</li>
                <li>⚠️ Alertas de stock bajo</li>
            </ul>
            {"<span class='permission-badge'>✅ Disponible</span>" if inventory_available else "<span class='restricted-badge'>🔒 Sin acceso</span>"}
        </div>
        """, unsafe_allow_html=True)
        
        if inventory_available:
            if st.button("🚀 Acceder a Inventario", key="inventory_btn", use_container_width=True):
                st.session_state.current_module = 'inventory'
                st.rerun()
        else:
            st.button("🔒 Sin Acceso", disabled=True, use_container_width=True)
    
    with col2:
        # Módulo de Nómina (solo para admin)
        payroll_available = 'payroll' in user_permissions
        
        if payroll_available:
            st.markdown(f"""
            <div class="feature-card">
                <h3>💰 Cálculo de Nómina</h3>
                <p><strong>Sistema avanzado de cálculo de sueldos</strong></p>
                <ul>
                    <li>📊 Procesamiento de Excel y PDF</li>
                    <li>⏰ Cálculo automático de horas</li>
                    <li>🎯 Gestión de horas especiales</li>
                    <li>📋 Reportes detallados</li>
                    <li>🔧 Corrección de horarios</li>
                </ul>
                <span class='permission-badge'>✅ Disponible</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Acceder a Nómina", key="payroll_btn", use_container_width=True):
                st.session_state.current_module = 'payroll'
                st.rerun()
        else:
            # No mostrar el módulo de nómina para empleados
            st.markdown(f"""
            <div class="feature-card" style="opacity: 0.6;">
                <h3>📊 Reportes y Métricas</h3>
                <p><strong>Próximamente disponible</strong></p>
                <ul>
                    <li>📈 Métricas de inventario</li>
                    <li>📊 Análisis de ventas</li>
                    <li>� Reportes personalizados</li>
                    <li>🎯 Dashboard ejecutivo</li>
                    <li>📱 Notificaciones</li>
                </ul>
                <span class='restricted-badge'>🚧 En desarrollo</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.button("🚧 Próximamente", disabled=True, use_container_width=True)
    
    # Información adicional responsive
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📋 **Información del Sistema**")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.info("""
        **🎯 Características Principales:**
        - ✅ Autenticación por roles
        - ✅ Sistema modular escalable  
        - ✅ Interfaz intuitiva
        - ✅ Datos seguros y organizados
        - ✅ Navegación fluida entre módulos
        """)
    
    with col2:
        # Información personalizada según el rol
        if user_role == 'admin':
            st.success("""
            **� Panel de Administrador:**
            - ✅ Gestión completa de inventario
            - ✅ Cálculo de nóminas y sueldos
            - ✅ Reportes y métricas avanzadas
            - ✅ Configuración del sistema
            
            **🔐 Privilegios completos activados**
            """)
        else:
            st.info("""
            **👨‍💼 Panel de Empleado:**
            - ✅ Gestión de inventario por tienda
            - ✅ Control de stock y productos
            - ✅ Sistema de delivery
            - ✅ Registro de mermas
            
            **📦 Enfocado en operaciones diarias**
            """)

def show_employee_navigation():
    """Muestra navegación simplificada para empleados"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📦 **Sistema de Inventario**")
    
    # Solo mostrar el botón de inventario ya que es lo único que pueden usar
    current_module = st.session_state.get('current_module', 'inventory')
    
    if current_module == 'inventory':
        st.sidebar.success("📦 Gestión de Inventario - Activo")
    else:
        if st.sidebar.button("📦 Ir al Inventario", use_container_width=True):
            st.session_state.current_module = 'inventory'
            st.rerun()

def show_module_selector():
    """Muestra el selector de módulos en la sidebar para administradores"""
    if not auth_system.is_logged_in():
        return
    
    user_info = st.session_state.get('user_info', {})
    permissions = user_info.get('permissions', [])
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📱 **Aplicaciones**")
    
    # Botón Dashboard
    if st.sidebar.button("🏠 Dashboard Principal", use_container_width=True):
        if 'current_module' in st.session_state:
            del st.session_state['current_module']
        st.rerun()
    
    # Botón Inventario
    if 'inventory' in permissions:
        if st.sidebar.button("📦 Gestión de Inventario", use_container_width=True):
            st.session_state.current_module = 'inventory'
            st.rerun()
    
    # Botón Nómina (solo admin)
    if 'payroll' in permissions:
        if st.sidebar.button("💰 Cálculo de Nómina", use_container_width=True):
            st.session_state.current_module = 'payroll'
            st.rerun()

def main():
    """Función principal - Redirige directamente al módulo de inventario"""
    
    # Configurar responsive básico
    detect_mobile_device()
    
    # IR DIRECTAMENTE AL MÓDULO DE INVENTARIO
    try:
        from modules.inventory.main_inventory import run_inventory_app
        run_inventory_app()
    except ImportError:
        st.error("❌ Error: No se pudo cargar el módulo de inventario")
        st.info("Verifica que main_inventory.py esté en modules/inventory/")
        st.stop()

if __name__ == "__main__":
    main()