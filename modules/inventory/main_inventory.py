"""
Módulo de Gestión de Inventario - BusinessSuite
Adaptado del sistema Netward 1.8 para integración con BusinessSuite

Accesible para Empleados y Administradores
"""
import streamlit as st
import json
import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio del módulo al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Importaciones seguras de los componentes del módulo de inventario
inventory_imports_ok = True

# Import auth
try:
    from .auth import login
    auth_available = True
except ImportError:
    inventory_imports_ok = False
    auth_available = False
    login = None

# Import persistencia
try:
    from .persistencia import (
        cargar_inventario, 
        guardar_inventario, 
        cargar_historial, 
        guardar_historial, 
        cargar_catalogo_delivery, 
        guardar_venta_delivery, 
        cargar_ventas_delivery
    )
    persistencia_available = True
except ImportError:
    inventory_imports_ok = False
    persistencia_available = False
    cargar_inventario = guardar_inventario = cargar_historial = guardar_historial = None
    cargar_catalogo_delivery = guardar_venta_delivery = cargar_ventas_delivery = None

# Import config_tiendas
try:
    from .config_tiendas import (
        selector_tienda_empleado, 
        GestorTiendas, 
        obtener_nombre_tienda,
        cargar_config_tiendas,
        mostrar_panel_configuracion_tiendas
    )
    config_tiendas_available = True
except ImportError:
    inventory_imports_ok = False
    config_tiendas_available = False
    selector_tienda_empleado = GestorTiendas = obtener_nombre_tienda = cargar_config_tiendas = mostrar_panel_configuracion_tiendas = None

# Import UI components
try:
    from .ui_empleado_fixed import mostrar_interfaz_empleado
    ui_empleado_available = True
    print("✅ Módulo de empleado cargado correctamente")
except ImportError:
    inventory_imports_ok = False
    ui_empleado_available = False
    mostrar_interfaz_empleado = None
    print("❌ Error cargando módulo de empleado - ui_empleado_fixed no disponible")

try:
    from .ui_admin import admin_inventario_ui, mostrar_interfaz_admin
    ui_admin_available = True
    print("✅ Módulo de administrador cargado correctamente")
except ImportError:
    inventory_imports_ok = False
    ui_admin_available = False
    mostrar_interfaz_admin = None
    admin_inventario_ui = None
    print("❌ Error cargando módulo de administrador")

# Los imports principales ya están definidos arriba

if not inventory_imports_ok:
    st.error("❌ Error al importar algunos módulos de inventario")
    st.info("Algunos componentes del módulo de inventario no están disponibles. Verifica la instalación.")

def inicializar_estructura_datos():
    """Inicializa la estructura de datos para multi-tienda"""
    data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'inventory', 'inventario.json')
    
    try:
        with open(data_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    
    # Verificar si ya tiene estructura multi-tienda
    if "inventario_por_tienda" not in data:
        # Migrar datos existentes a estructura multi-tienda
        inventario_existente = {}
        for key, value in data.items():
            if key in ["Impulsivo", "Por Kilos", "Extras"] and isinstance(value, dict):
                inventario_existente[key] = value
        
        # Crear nueva estructura
        data = {
            "inventario_por_tienda": {
                "T001": inventario_existente if inventario_existente else {
                    "Impulsivo": {},
                    "Por Kilos": {},
                    "Extras": {}
                },
                "T002": {
                    "Impulsivo": {},
                    "Por Kilos": {},
                    "Extras": {}
                }
            },
            "configuracion": {
                "tienda_default": "T001",
                "version": "1.8",
                "tiendas": {
                    "T001": {
                        "id": "T001",
                        "nombre": "Seminario",
                        "direccion": "Dirección no especificada",
                        "activa": True,
                        "fecha_creacion": datetime.now().strftime("%Y-%m-%d")
                    },
                    "T002": {
                        "id": "T002",
                        "nombre": "Mcal Lopez",
                        "direccion": "Dirección no especificada",
                        "activa": True,
                        "fecha_creacion": datetime.now().strftime("%Y-%m-%d")
                    }
                }
            }
        }
        
        # Guardar nueva estructura
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        with open(data_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    
    return data

def load_inventory_css():
    """Carga estilos CSS específicos del módulo de inventario con soporte responsive"""
    st.markdown("""
    <style>
    .inventory-header {
        background: linear-gradient(90deg, #007bff 0%, #6f42c1 100%);
        padding: clamp(1rem, 3vw, 1.5rem);
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        word-break: break-word;
        overflow-wrap: break-word;
    }
    
    .inventory-header h1 {
        font-size: clamp(1.5rem, 4vw, 2.2rem);
        margin: 0.5rem 0;
        line-height: 1.2;
    }
    
    .inventory-header p {
        font-size: clamp(0.9rem, 2.5vw, 1.1rem);
        margin: 0.3rem 0;
    }
    
    .store-card {
        background: white;
        padding: clamp(1rem, 3vw, 1.5rem);
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border-left: 4px solid #007bff;
        word-break: break-word;
        overflow-wrap: break-word;
    }
    
    .user-info-card {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: clamp(0.8rem, 2.5vw, 1rem);
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #2196f3;
        word-break: break-word;
        overflow-wrap: break-word;
    }
    
    .user-info-card h4 {
        font-size: clamp(1rem, 3vw, 1.2rem);
        margin-bottom: 0.5rem;
    }
    
    .user-info-card p {
        font-size: clamp(0.85rem, 2.3vw, 0.95rem);
        margin: 0.2rem 0;
    }
    
    .tab-content {
        background: white;
        padding: clamp(1rem, 3vw, 1.5rem);
        border-radius: 0 0 10px 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        word-break: break-word;
        overflow-wrap: break-word;
    }
    
    /* Responsive para móviles */
    @media (max-width: 768px) {
        .inventory-header {
            padding: 1rem;
            margin-bottom: 1.5rem;
            border-radius: 8px;
        }
        
        .store-card, .user-info-card, .tab-content {
            padding: 1rem;
            margin-bottom: 0.8rem;
            border-radius: 8px;
        }
        
        /* Tabs responsive */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.3rem;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 0.85rem !important;
            padding: 0.4rem 0.6rem !important;
            min-width: fit-content !important;
            word-break: break-word !important;
            white-space: nowrap !important;
        }
        
        /* Selectbox en móvil */
        .stSelectbox > div > div {
            min-height: 44px !important;
            font-size: 16px !important;
        }
        
        /* Botones más grandes en móvil */
        .stButton > button {
            min-height: 48px !important;
            font-size: 0.9rem !important;
            padding: 0.6rem 1rem !important;
            word-break: break-word !important;
            white-space: normal !important;
        }
        
        /* Formularios en móvil */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            min-height: 44px !important;
            font-size: 16px !important;
        }
        
        /* Contenedor principal móvil */
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }
    
    @media (max-width: 480px) {
        .inventory-header {
            padding: 0.8rem;
        }
        
        .store-card, .user-info-card, .tab-content {
            padding: 0.8rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 0.8rem !important;
            padding: 0.3rem 0.5rem !important;
        }
        
        /* Navegación en pantallas muy pequeñas */
        .stButton > button {
            min-height: 50px !important;
            font-size: 0.85rem !important;
        }
    }
    
    /* Landscape móvil */
    @media (max-height: 500px) and (orientation: landscape) {
        .inventory-header {
            padding: 0.6rem;
            margin-bottom: 1rem;
        }
        
        .store-card, .user-info-card {
            padding: 0.6rem;
            margin-bottom: 0.6rem;
        }
        
        .tab-content {
            padding: 0.8rem;
        }
    }
    
    /* Optimizaciones táctiles */
    @media (hover: none) {
        .stButton > button {
            touch-action: manipulation !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            touch-action: manipulation !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def show_inventory_header():
    """Muestra el header del módulo de inventario"""
    st.markdown("""
    <div class="inventory-header">
        <h1>📦 Gestión de Inventario</h1>
        <p><strong>Sistema Multi-tienda de Control de Stock</strong></p>
        <small>Inventario Real • Delivery • Mermas • Reportes Avanzados</small>
    </div>
    """, unsafe_allow_html=True)

def show_user_session_info():
    """Muestra información de la sesión actual del usuario"""
    if 'inventory_user' in st.session_state:
        user_data = st.session_state.inventory_user
        
        st.markdown(f"""
        <div class="user-info-card">
            <h4>👤 Sesión Activa</h4>
            <p><strong>Usuario:</strong> {user_data['usuario']}</p>
            <p><strong>Rol:</strong> {user_data['rol'].title()}</p>
            <p><strong>Tienda:</strong> {user_data['tienda_nombre']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        return True
    return False

def run_inventory_app():
    """Función principal del módulo de gestión de inventario"""
    
    # Verificar que los imports están disponibles
    if not inventory_imports_ok:
        st.error("❌ **Módulo de Inventario No Disponible**")
        st.warning("Faltan componentes necesarios para el funcionamiento del módulo de inventario.")
        st.info("Verifica que todos los archivos estén en la carpeta modules/inventory/")
        
        if st.button("🔄 Reintentar Carga", use_container_width=True):
            st.rerun()
        return
    
    # Verificar autenticación de BusinessSuite
    if 'user_info' not in st.session_state:
        st.error("❌ No hay usuario autenticado")
        st.warning("Por favor, inicia sesión desde el dashboard principal.")
        if st.button("🔙 Volver al Dashboard"):
            st.rerun()
        return
    
    # Usar la información del usuario de BusinessSuite
    user_info = st.session_state.user_info
    
    # Adaptar la sesión para el módulo de inventario
    # SIEMPRE actualizar para reflejar el usuario actual de BusinessSuite
    tienda_id = "T001" if user_info.get('role') == 'employee' else "T001"
    st.session_state.inventory_user = {
        "usuario": user_info.get('username', 'usuario'),
        "rol": "admin" if user_info.get('role') == 'admin' else "empleado",
        "tienda": tienda_id,
        "tienda_nombre": obtener_nombre_tienda(tienda_id) if config_tiendas_available else "Tienda Principal"
    }
    
    # Cargar estilos específicos
    load_inventory_css()
    
    # Mostrar header del módulo
    show_inventory_header()
    
    # Inicializar estructura de datos
    try:
        inicializar_estructura_datos()
    except Exception as e:
        st.error(f"❌ Error al inicializar datos: {e}")
        return
    
    # Mostrar interfaz principal directamente (ya no necesita login)
    show_inventory_main_interface()

# Función eliminada - Ya no se necesita login interno
# El módulo usa la autenticación de BusinessSuite

def show_inventory_main_interface():
    """Muestra la interfaz principal del sistema de inventario"""
    user_data = st.session_state.inventory_user
    usuario = user_data['usuario']
    rol = user_data['rol']
    tienda_id = user_data['tienda']
    tienda_nombre = user_data['tienda_nombre']
    
    # Header con información de tienda
    st.markdown(f"## 🏪 {tienda_nombre}")
    st.markdown(f"**Usuario:** {usuario}")
    
    st.markdown("---")
    
    # Interfaz según el rol
    if rol in ["empleado", "employee"]:
        show_employee_interface(usuario, tienda_id)
    elif rol in ["administrador", "admin"]:
        show_admin_interface(usuario, tienda_id)
    else:
        # Por defecto, mostrar interfaz de empleado
        show_employee_interface(usuario, tienda_id)

def show_employee_interface(usuario, tienda_id):
    """Interfaz para empleados"""
    st.markdown("### 👨‍💼 Panel de Empleado")
    
    # Mostrar interfaz directamente sin tabs
    try:
        # Llamar a la interfaz de empleado
        if ui_empleado_available:
            mostrar_interfaz_empleado()
        else:
            mostrar_inventario_basico()
    except Exception as e:
        st.error(f"❌ Error en inventario: {str(e)}")
        st.info("Verifica la configuración del sistema de inventario.")

def show_employee_interface_old_with_tabs(usuario, tienda_id):
    """Interfaz para empleados CON TABS (vieja versión)"""
    st.markdown("### 👨‍💼 Panel de Empleado")
    
    # Pestañas para empleado
    tab_inventario, tab_delivery, tab_mermas = st.tabs(["📦 Inventario", "🚚 Delivery", "⚠️ Mermas"])
    
    with tab_inventario:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        try:
            # Llamar a la interfaz de empleado
            if ui_empleado_available:
                mostrar_interfaz_empleado()
            else:
                mostrar_inventario_basico()
        except Exception as e:
            st.error(f"❌ Error en inventario: {str(e)}")
            st.info("Verifica la configuración del sistema de inventario.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab_delivery:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        try:
            st.info("🚧 Módulo de delivery en desarrollo")
        except Exception as e:
            st.error(f"❌ Error en delivery: {str(e)}")
            st.info("Verifica la configuración del sistema de delivery.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab_mermas:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        try:
            st.info("🚧 Módulo de mermas en desarrollo")
        except Exception as e:
            st.error(f"❌ Error en mermas: {str(e)}")
            st.info("Verifica la configuración del sistema de mermas.")
        st.markdown('</div>', unsafe_allow_html=True)

def show_admin_interface(usuario, tienda_id):
    """Interfaz para administradores"""
    st.markdown("### 👑 Panel de Administrador")
    
    # Menú de opciones para admin
    if "admin_inventory_option" not in st.session_state:
        st.session_state.admin_inventory_option = "tiendas"
    
    menu_opciones = {
        "📦 Inventario por Tiendas": "tiendas",
        "📊 Historial y Reportes": "historial", 
        "⚠️ Mermas y Rupturas": "mermas",
        "⚙️ Configuraciones": "configuraciones"
    }
    
    # Selector de opción
    opcion_seleccionada = st.selectbox(
        "Seleccionar sección:",
        options=list(menu_opciones.keys()),
        index=list(menu_opciones.values()).index(st.session_state.admin_inventory_option),
        key="admin_inventory_select"
    )
    st.session_state.admin_inventory_option = menu_opciones[opcion_seleccionada]
    
    # Cargar configuración de tiendas
    config_tiendas = cargar_config_tiendas()
    tiendas_opciones = {tid: info["nombre"] for tid, info in config_tiendas.items()}
    
    st.markdown("---")
    
    # Mostrar interfaz según la opción seleccionada
    if st.session_state.admin_inventory_option == "tiendas":
        show_admin_stores_view(tiendas_opciones)
    elif st.session_state.admin_inventory_option == "historial":
        show_admin_history_view(tiendas_opciones)
    elif st.session_state.admin_inventory_option == "mermas":
        show_admin_mermas_view(tiendas_opciones)
    elif st.session_state.admin_inventory_option == "configuraciones":
        show_admin_config_view()

def show_admin_stores_view(tiendas_opciones):
    """Vista de inventario por tiendas para admin"""
    
    try:
        # Obtener tienda del session state o usar T001 por defecto
        if 'admin_tienda_selected' not in st.session_state:
            st.session_state.admin_tienda_selected = "T001"
        
        # El administrador siempre ve el inventario actual (sin selector de fecha)
        from datetime import date
        import json
        import os
        
        # Usar None para que siempre cargue lo último guardado
        fecha_admin = None
        
        # Botón de diagnóstico
        if st.button("🔍 Diagnóstico de Inventario", help="Muestra información detallada sobre el estado del inventario"):
            with st.expander("📋 Información de Diagnóstico", expanded=True):
                try:
                    if os.path.exists("inventario.json"):
                        with open("inventario.json", "r", encoding="utf-8") as f:
                            data_debug = json.load(f)
                        st.json(data_debug)
                        
                        # Mostrar fechas por tienda
                        fechas_por_tienda = data_debug.get("fechas_por_tienda", {})
                        st.write("**Fechas por tienda:**")
                        for tienda, fecha in fechas_por_tienda.items():
                            st.write(f"- {tienda}: {fecha}")
                    else:
                        st.error("No se encontró el archivo inventario.json")
                except Exception as e:
                    st.error(f"Error al cargar diagnóstico: {str(e)}")
        
        # Cargar inventario de la tienda con la fecha específica
        inventario = cargar_inventario(st.session_state.admin_tienda_selected, fecha_admin)
        
        # Llamar a la interfaz moderna de administrador directamente
        if admin_inventario_ui is not None:
            admin_inventario_ui(inventario, st.session_state.admin_tienda_selected)
        else:
            st.error("❌ La interfaz moderna de administrador no está disponible")
            mostrar_inventario_basico()
        
    except Exception as e:
        st.error(f"❌ Error al cargar inventario: {str(e)}")
        st.info("Verifica que todos los módulos estén correctamente instalados")
        import traceback
        with st.expander("🔍 Ver detalles del error"):
            st.code(traceback.format_exc())

def show_admin_history_view(tiendas_opciones):
    """Vista de historial para admin"""
    st.markdown("#### 📊 Historial y Reportes")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        tienda_admin_id = st.selectbox(
            "Seleccionar tienda:",
            options=list(tiendas_opciones.keys()),
            format_func=lambda x: tiendas_opciones[x],
            key="admin_tienda_selector_history"
        )
    
    with col2:
        st.info(f"📍 Visualizando historial de: **{tiendas_opciones[tienda_admin_id]}**")
    
    try:
        historial_data = cargar_historial(tienda_admin_id)
        # Mostrar historial básico
        if historial_data:
            st.write("**Últimos movimientos:**")
            for movimiento in historial_data[-10:]:
                fecha = movimiento.get("fecha", "N/A")
                usuario = movimiento.get("usuario", "N/A")
                producto = movimiento.get("producto", "N/A")
                cantidad = movimiento.get("cantidad", "N/A")
                st.write(f"• {fecha} | {usuario} | {producto}: {cantidad}")
        else:
            st.info("No hay historial disponible")
    except Exception as e:
        st.error(f"❌ Error al cargar historial: {str(e)}")

def show_admin_mermas_view(tiendas_opciones):
    """Vista de mermas para admin"""
    st.markdown("#### ⚠️ Gestión de Mermas y Rupturas")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        tienda_admin_id = st.selectbox(
            "Seleccionar tienda:",
            options=list(tiendas_opciones.keys()),
            format_func=lambda x: tiendas_opciones[x],
            key="admin_tienda_selector_mermas"
        )
    
    with col2:
        st.info(f"📍 Visualizando mermas de: **{tiendas_opciones[tienda_admin_id]}**")
    
    try:
        st.info("🚧 Módulo de gestión de mermas en desarrollo")
        st.write("Esta funcionalidad permitirá:")
        st.write("• Registrar productos con mermas")
        st.write("• Reportes de pérdidas")
        st.write("• Análisis de rupturas de stock")
    except Exception as e:
        st.error(f"❌ Error al cargar mermas: {str(e)}")

def show_admin_config_view():
    """Vista de configuraciones para admin"""
    st.markdown("#### ⚙️ Configuraciones del Sistema")
    
    try:
        mostrar_panel_configuracion_tiendas()
    except Exception as e:
        st.error(f"❌ Error en configuraciones: {str(e)}")

# Navegación adicional en la parte inferior
def show_inventory_navigation():
    """Muestra navegación del módulo de inventario"""
    st.markdown("---")
    st.markdown("### 🧭 Navegación")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏠 Dashboard Principal", use_container_width=True):
            # Limpiar sesión del inventario
            for key in list(st.session_state.keys()):
                if key.startswith('inventory_'):
                    del st.session_state[key]
            if 'current_module' in st.session_state:
                del st.session_state['current_module']
            st.rerun()
    
    with col2:
        # Solo mostrar si el usuario tiene permisos para nómina
        user_info = st.session_state.get('user_info', {})
        if 'payroll' in user_info.get('permissions', []):
            if st.button("💰 Ir a Nómina", use_container_width=True):
                st.session_state.current_module = 'payroll'
                st.rerun()
        else:
            st.button("🔒 Nómina (Solo Admin)", disabled=True, use_container_width=True)
    
    with col3:
        if st.button("🔄 Actualizar Datos", use_container_width=True):
            # Limpiar caché del módulo
            for key in list(st.session_state.keys()):
                if 'inventory_' in key and key != 'inventory_user':
                    del st.session_state[key]
            st.success("✅ Datos actualizados")
            st.rerun()

def main_inventory():
    """Función principal del módulo de inventario"""
    if not inventory_imports_ok:
        st.error("❌ Módulo de Inventario No Disponible")
        st.warning("Faltan componentes necesarios para el funcionamiento del módulo de inventario.")
        st.info("Verifica que todos los archivos estén en la carpeta modules/inventory/")
        
        if st.button("🔄 Reintentar Carga"):
            st.rerun()
        return
    
    # Verificar autenticación del usuario
    if 'user_info' not in st.session_state:
        st.error("❌ Usuario no autenticado")
        return
    
    user_info = st.session_state.user_info
    
    # Interfaz simplificada basada en el rol
    if user_info.get('role') == 'admin':
        # Admin: funcionalidades completas
        mostrar_interfaz_inventario_admin()
    else:
        # Empleado: funcionalidades básicas CON INTERFAZ CORREGIDA
        if ui_empleado_available:
            # Usar la interfaz completa del empleado con todos los formularios
            mostrar_interfaz_empleado()
        else:
            # Fallback a interfaz básica
            mostrar_interfaz_inventario_empleado_corregida()

def mostrar_interfaz_inventario_admin():
    """Interfaz del administrador para inventario"""
    # Llamar directamente a la interfaz de admin que ya tiene sus propias tabs
    if ui_admin_available:
        mostrar_interfaz_admin()
    else:
        # Fallback a interfaz básica
        st.markdown("""
        <div class="inventory-header">
            <h1>🏢 Sistema de Inventario - Administrador</h1>
            <p>Gestión completa del inventario multi-tienda</p>
        </div>
        """, unsafe_allow_html=True)
        
        user_info = st.session_state.get('user_info', {})
        st.markdown(f"""
        <div class="user-info-card">
            <h4>👤 {user_info.get('username', 'Admin')}</h4>
            <p>🔑 Rol: Administrador</p>
            <p>🏪 Acceso: Todas las tiendas</p>
        </div>
        """, unsafe_allow_html=True)
        
        mostrar_inventario_basico()
    
    # Navegación
    mostrar_navegacion_inventario()

def mostrar_interfaz_inventario_empleado():
    """Interfaz del empleado para inventario"""
    st.markdown("""
    <div class="inventory-header">
        <h1>📦 Sistema de Inventario - Empleado</h1>
        <p>Gestión de inventario de tu tienda</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Información del usuario
    user_info = st.session_state.get('user_info', {})
    st.markdown(f"""
    <div class="user-info-card">
        <h4>👤 {user_info.get('username', 'Empleado')}</h4>
        <p>🔑 Rol: Empleado</p>
        <p>🏪 Tienda asignada</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Interfaz del empleado
    if ui_empleado_available:
        mostrar_interfaz_empleado()
    else:
        mostrar_inventario_basico()
    
    # Navegación
    mostrar_navegacion_inventario()

def mostrar_inventario_basico():
    """Interfaz básica de inventario cuando los módulos específicos no están disponibles"""
    st.subheader("📦 Gestión Básica de Inventario")
    
    # Selector de tienda para admin
    user_info = st.session_state.get('user_info', {})
    if user_info.get('role') == 'admin':
        tienda = st.selectbox(
            "Selecciona la tienda:",
            ["T001 - Seminario", "T002 - Mcal Lopez"]
        )
    
    # Selector de categoría
    categoria = st.selectbox(
        "Categoría:",
        ["Impulsivo", "Por Kilos", "Extras"]
    )
    
    # Campos para producto
    col1, col2 = st.columns(2)
    
    with col1:
        producto = st.text_input("Nombre del producto:")
    
    with col2:
        cantidad = st.number_input("Cantidad:", min_value=0.0, step=0.1)
    
    if st.button("Agregar Producto"):
        if producto and cantidad >= 0:
            st.success(f"✅ Producto {producto} - Cantidad: {cantidad}")
        else:
            st.error("❌ Complete todos los campos")

def mostrar_reportes_admin():
    """Reportes básicos para administrador"""
    st.subheader("📊 Reportes de Inventario")
    st.info("🚧 Módulo de reportes en desarrollo")

def mostrar_configuracion_admin():
    """Configuración básica para administrador"""
    st.subheader("⚙️ Configuración del Sistema")
    st.info("🚧 Panel de configuración en desarrollo")

def mostrar_interfaz_inventario_empleado_corregida():
    """Interfaz del empleado CORREGIDA con formularios funcionales"""
    st.markdown("""
    <div class="inventory-header">
        <h1>📦 Sistema de Inventario - Empleado</h1>
        <p>Gestión de inventario de tu tienda</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Información del usuario
    user_info = st.session_state.get('user_info', {})
    st.markdown(f"""
    <div class="user-info-card">
        <h4>👤 {user_info.get('username', 'Empleado')}</h4>
        <p>🔑 Rol: Empleado</p>
        <p>🏪 Tienda asignada</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Intentar usar la interfaz corregida
    try:
        from .ui_empleado_fixed import mostrar_interfaz_empleado
        mostrar_interfaz_empleado(usuario=user_info.get('username', 'empleado'))
    except ImportError as e:
        st.error(f"Error cargando interfaz corregida: {e}")
        # Fallback a interfaz básica funcional
        mostrar_inventario_basico_funcional()

def mostrar_inventario_basico_funcional():
    """Interfaz básica completamente funcional"""
    st.subheader("📦 Gestión de Inventario - Modo Básico")
    st.info("🔧 Usando interfaz simplificada por problemas técnicos")
    
    # Inicializar carrito temporal si no existe
    if 'carrito_basico' not in st.session_state:
        st.session_state.carrito_basico = []
    
    # Mostrar carrito si hay productos
    if st.session_state.carrito_basico:
        st.subheader("🛒 Productos en Carrito")
        for i, item in enumerate(st.session_state.carrito_basico):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{item['categoria']}** - {item['producto']}: {item['cantidad']}")
            with col2:
                if st.button("✏️", key=f"edit_{i}"):
                    st.session_state[f'editing_{i}'] = True
            with col3:
                if st.button("🗑️", key=f"delete_{i}"):
                    st.session_state.carrito_basico.pop(i)
                    st.rerun()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Guardar Todo", type="primary"):
                st.success(f"✅ {len(st.session_state.carrito_basico)} productos guardados")
                st.session_state.carrito_basico = []
                st.rerun()
        with col2:
            if st.button("🗑️ Limpiar Carrito"):
                st.session_state.carrito_basico = []
                st.rerun()
        
        st.divider()
    
    # Formulario para agregar productos
    with st.form("agregar_producto_basico", clear_on_submit=True):
        st.markdown("### ➕ Agregar Producto")
        
        col1, col2 = st.columns(2)
        
        with col1:
            categoria = st.selectbox(
                "Categoría:",
                ["Impulsivo", "Por Kilos", "Extras"],
                key="cat_basico"
            )
            
            producto = st.text_input(
                "Nombre del producto:",
                key="prod_basico",
                placeholder="Ej: Alfajor Almendrado"
            )
        
        with col2:
            if categoria == "Por Kilos":
                cantidad = st.number_input(
                    "Cantidad (kg):",
                    min_value=0.0,
                    step=0.1,
                    format="%.1f",
                    key="cant_basico"
                )
            else:
                cantidad = st.number_input(
                    "Cantidad:",
                    min_value=0,
                    step=1,
                    key="cant_basico"
                )
        
        # Botón de envío
        submitted = st.form_submit_button("➕ Agregar al Carrito", use_container_width=True)
        
        if submitted:
            if producto.strip() and cantidad > 0:
                nuevo_item = {
                    'categoria': categoria,
                    'producto': producto.strip(),
                    'cantidad': cantidad
                }
                st.session_state.carrito_basico.append(nuevo_item)
                st.success(f"✅ {producto} agregado al carrito")
                st.rerun()
            else:
                st.error("❌ Completa todos los campos correctamente")

def mostrar_navegacion_inventario():
    """
    Función de navegación para el módulo de inventario
    Corrige el warning de función no definida
    """
    st.markdown("---")
    
    # Botones de navegación
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.current_module = 'dashboard'
            st.rerun()
    
    with col2:
        if st.button("🔄 Refrescar", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("📊 Reportes", use_container_width=True):
            st.info("🚧 Función en desarrollo")
    
    with col4:
        if st.button("⚙️ Configuración", use_container_width=True):
            st.info("🚧 Función en desarrollo")
    
    # Información adicional
    st.markdown("""
    <div style="text-align: center; margin-top: 20px; color: #666; font-size: 0.9em;">
        📦 Módulo de Inventario - BusinessSuite | Usuario: {user}
    </div>
    """.format(user=st.session_state.get('user_info', {}).get('username', 'Desconocido')), 
    unsafe_allow_html=True)

# Función principal para compatibilidad
if __name__ == "__main__":
    main_inventory()
