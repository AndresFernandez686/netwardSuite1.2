"""
BusinessSuite - Suite de Aplicaciones de Negocio
Sistema unificado de Gestión de Inventario y Cálculo de Nómina

Versión: 1.0 - Dashboard Completo
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
sys.path.insert(0, os.path.join(current_dir, 'modules', 'sugerencias'))
sys.path.insert(0, os.path.join(current_dir, 'shared'))

# Importar sistema de autenticación
from auth_unified import auth_system

# Configuración de página
st.set_page_config(
    page_title="BusinessSuite - Suite de Negocio",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_dashboard_css():
    """Carga estilos CSS para el dashboard"""
    st.markdown("""
    <style>
    .dashboard-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .dashboard-header h1 {
        font-size: 2.5rem;
        margin: 0.5rem 0;
    }
    
    .module-card {
        background: #1e1e1e;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        border-left: 4px solid #667eea;
        margin-bottom: 1.5rem;
        transition: transform 0.2s;
    }
    
    .module-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        background: #252525;
    }
    
    .module-card h3 {
        color: #8b9dff;
        margin-bottom: 1rem;
        font-size: 1.8rem;
        font-weight: bold;
    }
    
    .module-card p {
        color: #e0e0e0;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    
    .module-card ul {
        color: #cccccc;
    }
    
    .module-card li {
        color: #d0d0d0;
        font-size: 1rem;
    }
    
    .feature-list {
        list-style: none;
        padding-left: 0;
    }
    
    .feature-list li {
        padding: 0.3rem 0;
        font-size: 0.95rem;
    }
    </style>
    """, unsafe_allow_html=True)

def show_dashboard():
    """Muestra el dashboard principal con opciones de módulos"""
    load_dashboard_css()
    
    # Obtener información del usuario
    user_info = st.session_state.get('user_info', {})
    user_name = user_info.get('name', 'Usuario')
    user_role = user_info.get('role', 'employee')
    is_admin = user_role == 'admin'
    
    # Header del dashboard
    st.markdown(f"""
    <div class="dashboard-header">
        <h1>🏢 Netw@rd Suite de Negocios</h1>
        <p><strong>Sistema Integrado de Gestión Empresarial</strong></p>
        <small>Inventario • Nómina • Sugerencias IA</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Bienvenida personalizada
    role_emoji = "👑" if is_admin else "👨‍💼"
    st.markdown(f"## 👋 Bienvenido, {user_name} {role_emoji}")
    st.markdown("---")
    
    # Módulos disponibles
    if is_admin:
        # Admin ve todos los módulos
        col1, col2, col3 = st.columns(3)
    else:
        # Empleado solo ve inventario (columna centrada)
        col1, col2, col3 = st.columns([1, 2, 1])
        col1 = col2  # Usar columna central
    
    with col1:
        st.markdown("""
        <div class="module-card">
            <h3>📦 Gestión de Inventario</h3>
            <p><strong>Sistema Multi-tienda de Control de Stock</strong></p>
            <ul class="feature-list">
                <li>✅ Inventario por tiendas</li>
                <li>✅ Control de productos (Impulsivo, Kilos, Extras)</li>
                <li>✅ Sistema de delivery</li>
                <li>✅ Gestión de mermas</li>
                <li>✅ Historial de movimientos</li>
                <li>✅ Reportes avanzados</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📦 Ir a Inventario", key="btn_inventory", use_container_width=True, type="primary"):
            st.session_state.current_module = 'inventory'
            st.rerun()
    
    # Solo mostrar módulo de nómina para administradores
    if is_admin:
        with col2:
            st.markdown("""
            <div class="module-card">
                <h3>💰 Cálculo de Nómina</h3>
                <p><strong>Sistema de Gestión de Sueldos y Pagos</strong></p>
                <ul class="feature-list">
                    <li>✅ Cálculo automático de sueldos</li>
                    <li>✅ Procesamiento de PDFs</li>
                    <li>✅ Carga de datos desde archivos</li>
                    <li>✅ Generación de reportes</li>
                    <li>✅ Historial de pagos</li>
                    <li>✅ Exportación de datos</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("💰 Ir a Nómina", key="btn_payroll", use_container_width=True, type="primary"):
                st.session_state.current_module = 'payroll'
                st.rerun()
        
        with col3:
            st.markdown("""
            <div class="module-card">
                <h3>🤖 Sugerencias Inteligentes</h3>
                <p><strong>Sistema de Recomendación de Compras con IA</strong></p>
                <ul class="feature-list">
                    <li>✅ Pronóstico del clima</li>
                    <li>✅ Análisis de demanda</li>
                    <li>✅ Sugerencias por tienda</li>
                    <li>✅ Optimización de stock</li>
                    <li>✅ Historial y analytics</li>
                    <li>✅ Reportes detallados</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🤖 Ir a Sugerencias", key="btn_sugerencias", use_container_width=True, type="primary"):
                st.session_state.current_module = 'sugerencias'
                st.rerun()
    else:
        # Para empleados, mostrar mensaje de acceso restringido
        st.info("ℹ️ **Módulo de Nómina**\n\nEste módulo está disponible solo para Administradores.\nContacta al administrador si necesitas acceso.")
    
    # Información adicional
    st.markdown("---")
    st.markdown("### 📋 Información del Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **🎯 Características:**
        - ✅ Sistema modular
        - ✅ Interfaz intuitiva
        - ✅ Datos organizados
        - ✅ Navegación fluida
        """)
    
    with col2:
        st.success("""
        **📦 Inventario:**
        - Multi-tienda
        - 73 productos
        - Carrito temporal
        - Historial completo
        """)
    
    with col3:
        st.success("""
        **💰 Nómina:**
        - Cálculo automático
        - Carga de PDFs
        - Reportes detallados
        - Exportación fácil
        """)

def show_navigation():
    """Muestra navegación en la sidebar"""
    # Mostrar info del usuario
    auth_system.show_user_info()
    
    st.sidebar.markdown("### 🧭 Navegación")
    
    current_module = st.session_state.get('current_module', None)
    user_info = st.session_state.get('user_info', {})
    is_admin = user_info.get('role') == 'admin'
    
    # Botón Dashboard
    if st.sidebar.button("🏠 Dashboard Principal", use_container_width=True):
        if 'current_module' in st.session_state:
            del st.session_state['current_module']
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📱 Módulos")
    
    # Botón Inventario
    if current_module == 'inventory':
        st.sidebar.success("📦 Inventario - ACTIVO")
    else:
        if st.sidebar.button("📦 Gestión de Inventario", use_container_width=True):
            st.session_state.current_module = 'inventory'
            st.rerun()
    
    # Botón Nómina (solo para admin)
    if is_admin:
        if current_module == 'payroll':
            st.sidebar.success("💰 Nómina - ACTIVO")
        else:
            if st.sidebar.button("💰 Cálculo de Nómina", use_container_width=True):
                st.session_state.current_module = 'payroll'
                st.rerun()
    else:
        st.sidebar.info("💰 Nómina\n(Solo Admin)")
    
    # Botón Sugerencias (solo para admin)
    if is_admin:
        if current_module == 'sugerencias':
            st.sidebar.success("🤖 Sugerencias IA - ACTIVO")
        else:
            if st.sidebar.button("🤖 Sugerencias Inteligentes", use_container_width=True):
                st.session_state.current_module = 'sugerencias'
                st.rerun()
    else:
        st.sidebar.info("🤖 Sugerencias\n(Solo Admin)")

def main():
    """Función principal con dashboard y módulos"""
    
    # Verificar autenticación primero
    if not auth_system.is_logged_in():
        auth_system.login_form()
        return
    
    # Usuario autenticado - continuar con la aplicación
    user_info = st.session_state.get('user_info', {})
    
    # Verificar qué módulo mostrar
    current_module = st.session_state.get('current_module', None)
    
    if current_module == 'inventory':
        # Mostrar navegación
        show_navigation()
        
        # Cargar módulo de inventario
        try:
            from modules.inventory.main_inventory import run_inventory_app
            run_inventory_app()
        except ImportError as e:
            st.error(f"❌ Error: No se pudo cargar el módulo de inventario: {e}")
            st.info("Verifica que main_inventory.py esté en modules/inventory/")
            if st.button("🔙 Volver al Dashboard"):
                del st.session_state['current_module']
                st.rerun()
    
    elif current_module == 'payroll':
        # Verificar que el usuario es administrador
        if user_info.get('role') != 'admin':
            st.error("🔒 **Acceso Denegado**")
            st.warning("El módulo de Nómina está restringido solo para Administradores.")
            st.info("Contacta al administrador si necesitas acceso a esta función.")
            
            if st.button("🔙 Volver al Dashboard"):
                del st.session_state['current_module']
                st.rerun()
            return
        
        # Mostrar navegación
        show_navigation()
        
        # Cargar módulo de nómina - Usar versión corregida
        try:
            from modules.payroll.main_payroll import run_payroll_app
            run_payroll_app()
        except ImportError as e:
            st.error("❌ Error al importar módulos de nómina: " + str(e))
            st.info("📋 Verifica que todos los archivos estén en la carpeta modules/payroll/")
            
            with st.expander("🔍 Detalles técnicos del error"):
                st.code(str(e))
                st.markdown("""
                **Archivos requeridos:**
                - main_payroll.py
                - ui_components.py
                - data_processor.py
                - pdf_processor.py
                - loading_components.py
                - calculations.py
                - plantilla_sueldos_feriados_dias.xlsx
                """)
            
            if st.button("🔙 Volver al Dashboard"):
                del st.session_state['current_module']
                st.rerun()
    
    elif current_module == 'sugerencias':
        # Verificar que el usuario es administrador
        if user_info.get('role') != 'admin':
            st.error("🔒 **Acceso Denegado**")
            st.warning("El módulo de Sugerencias Inteligentes está restringido solo para Administradores.")
            st.info("Contacta al administrador si necesitas acceso a esta función.")
            
            if st.button("🔙 Volver al Dashboard"):
                del st.session_state['current_module']
                st.rerun()
            return
        
        # Mostrar navegación
        show_navigation()
        
        # Cargar módulo de sugerencias
        try:
            from modules.sugerencias.main_sugerencias import main as sugerencias_main
            sugerencias_main()
        except ImportError as e:
            st.error("❌ Error al importar módulo de sugerencias: " + str(e))
            st.info("📋 Verifica que todos los archivos estén en la carpeta modules/sugerencias/")
            
            with st.expander("🔍 Detalles técnicos del error"):
                st.code(str(e))
                st.markdown("""
                **Archivos requeridos:**
                - main_sugerencias.py
                - config/settings.py
                - services/database_service.py
                - services/weather_service.py
                - core/suggestion_engine.py
                - ui/pages.py
                - ui/components.py
                - models/data_models.py
                """)
            
            if st.button("🔙 Volver al Dashboard"):
                del st.session_state['current_module']
                st.rerun()
    
    else:
        # Mostrar dashboard principal
        show_dashboard()

if __name__ == "__main__":
    main()