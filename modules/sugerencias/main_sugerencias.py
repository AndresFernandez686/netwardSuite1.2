"""
Sistema de Sugerencias Inteligente - Heladería Grido Paraguay
Módulo integrado en BusinessSuite
"""
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Configurar rutas para el módulo dentro de BusinessSuite
module_root = Path(__file__).parent
if str(module_root) not in sys.path:
    sys.path.insert(0, str(module_root))

# Importar dependencias de manera segura
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print(" Warning: streamlit no está disponible")

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print(" Warning: python-dotenv no está disponible")
    def load_dotenv():
        pass  # Función vacía como fallback

# Importar módulos de la aplicación
try:
    from config.settings import PARAGUAY_HOLIDAYS
    SETTINGS_AVAILABLE = True
except ImportError:
    SETTINGS_AVAILABLE = False
    PARAGUAY_HOLIDAYS = {}
    print(" Warning: configuraciones no disponibles")

# Definir APP_TEXTS si no está disponible
APP_TEXTS = {
    'navigation': {
        'configure_store': ' Configurar Tienda',
        'view_stores': ' Ver Tiendas', 
        'generate_suggestion': ' Generar Sugerencia',
        'history': ' Historial & Analytics'
    }
}

# Importar servicios de manera condicional
try:
    from services.database_service import db_service
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print(" Warning: database_service no disponible")
    
try:
    from ui.components import ui_components
    from ui.pages import pages
    UI_AVAILABLE = True
except ImportError:
    UI_AVAILABLE = False
    print(" Warning: UI components no disponibles")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

def init_app():
    """Inicializa la aplicación Streamlit"""
    if not STREAMLIT_AVAILABLE:
        print(" Streamlit no está disponible. Instala con: pip install streamlit")
        return False
        
    # Configuración de la página
    st.set_page_config(
        page_title=" Grido - Sistema de Sugerencias IA",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/tu-usuario/sugerencia-grido',
            'Report a bug': 'https://github.com/tu-usuario/sugerencia-grido/issues',
            'About': """
            # Sistema de Sugerencias Inteligente
            
            **Heladería Grido - Paraguay**
            
            Optimiza tus compras semanales usando:
            -  Inteligencia Artificial
            -  Pronóstico del clima
            -  Análisis de demanda
            -  Estrategias personalizadas
            
            Desarrollado para maximizar ventas y minimizar merma.
            """
        }
    )
    
    # CSS personalizado
    st.markdown("""
    <style>
    /* =========================
       ESTILOS GENERALES
       ========================= */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    .success-message {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
    
    /* Mejorar el aspecto de las tablas */
    .dataframe {
        border: none !important;
    }
    
    .dataframe thead th {
        background: #4ECDC4 !important;
        color: white !important;
    }
    
    /* Botones personalizados */
    .stButton > button {
        border-radius: 20px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* =========================
       RESPONSIVE MÓVIL
       ========================= */
    @media only screen and (max-width: 768px) {
        /* Ajustar padding y márgenes para móvil */
        .main-header {
            padding: 1rem 0.5rem;
            font-size: 0.9rem;
        }
        
        /* Hacer columnas apilables */
        .row-widget.stHorizontal {
            flex-direction: column !important;
        }
        
        /* Ajustar tamaño de texto */
        h1 {
            font-size: 1.8rem !important;
        }
        
        h2 {
            font-size: 1.5rem !important;
        }
        
        h3 {
            font-size: 1.2rem !important;
        }
        
        /* Mejorar inputs en móvil */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            font-size: 16px !important; /* Evita zoom automático en iOS */
        }
        
        /* Botones más grandes en móvil */
        .stButton > button {
            width: 100% !important;
            padding: 0.75rem 1rem !important;
            font-size: 1rem !important;
        }
        
        /* Tarjetas responsive */
        div[style*='padding: 1rem'] {
            padding: 0.75rem !important;
            margin: 0.5rem 0 !important;
        }
        
        /* Tablas scrolleables horizontalmente */
        .dataframe {
            overflow-x: auto !important;
            display: block !important;
            max-width: 100% !important;
        }
        
        /* Métricas apiladas */
        [data-testid="metric-container"] {
            min-width: 100% !important;
        }
        
        /* Sidebar más compacto */
        [data-testid="stSidebar"] {
            min-width: 250px !important;
        }
        
        /* Gráficos responsive */
        .plotly {
            width: 100% !important;
            height: auto !important;
        }
        
        /* Tabs más compactos */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.25rem !important;
            flex-wrap: wrap !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 0.85rem !important;
            padding: 0.5rem 0.75rem !important;
        }
        
        /* Forms más compactos */
        .stForm {
            padding: 0.5rem !important;
        }
        
        /* Expanders */
        .streamlit-expanderHeader {
            font-size: 0.95rem !important;
        }
    }
    
    /* Tablets (768px - 1024px) */
    @media only screen and (min-width: 769px) and (max-width: 1024px) {
        .main-header {
            padding: 1.5rem 1rem;
        }
        
        h1 {
            font-size: 2rem !important;
        }
        
        .stButton > button {
            padding: 0.6rem 1.5rem !important;
        }
    }
    
    /* Mejorar accesibilidad táctil */
    @media (hover: none) and (pointer: coarse) {
        /* Dispositivos táctiles */
        .stButton > button,
        a,
        [role="button"] {
            min-height: 44px !important; /* Tamaño mínimo recomendado para táctil */
            min-width: 44px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Inicializar base de datos
    if DATABASE_AVAILABLE:
        try:
            db_service.init_database()
            logger.info("Base de datos inicializada correctamente")
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            st.error(" Error inicializando el sistema. Contacte al administrador.")
            st.stop()
    else:
        st.warning(" Base de datos no disponible. Algunas funciones estarán limitadas.")
        
    return True

def get_upcoming_holidays():
    """Obtiene los próximos feriados de Paraguay"""
    today = datetime.now().date()
    upcoming_holidays = []
    
    for date_str, holiday_name in PARAGUAY_HOLIDAYS.items():
        try:
            holiday_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if holiday_date >= today:
                days_until = (holiday_date - today).days
                if days_until <= 30:  # Solo próximos 30 días
                    upcoming_holidays.append({
                        'date': holiday_date,
                        'name': holiday_name,
                        'days_until': days_until
                    })
        except ValueError:
            continue
    
    # Ordenar por fecha
    upcoming_holidays.sort(key=lambda x: x['date'])
    return upcoming_holidays

def render_basic_configure_store():
    """Página básica para configurar tienda cuando UI no está disponible"""
    st.header(" Configurar Nueva Tienda")
    
    st.warning(" Interfaz limitada - algunos componentes no están disponibles")
    
    st.markdown("""
    ### ¡Bienvenido! Configuremos tu heladería Grido
    
    Para generar sugerencias precisas, necesitamos algunos datos básicos de tu tienda.
    """)
    
    name = st.text_input(" Nombre de la tienda", placeholder="Ej: Grido Asunción Centro")
    
    col1, col2 = st.columns(2)
    with col1:
        city = st.text_input(" Ciudad", placeholder="Ej: Asunción")
        country = st.text_input(" País", value="Paraguay")
    
    with col2:
        lat = st.number_input(" Latitud", value=-25.2637, format="%.6f")
        lon = st.number_input(" Longitud", value=-57.5759, format="%.6f")
    
    st.subheader(" Configuración de Demanda Base")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        palitos_per_day = st.number_input("Palitos/día", value=3.4, min_value=0.1, step=0.1)
        conos_per_day = st.number_input("Conos/día", value=3.0, min_value=0.1, step=0.1)
    
    with col2:
        vasitos_per_day = st.number_input("Vasitos/día", value=2.0, min_value=0.1, step=0.1)
        potes_kg_per_day = st.number_input("Potes (kg)/día", value=1.1, min_value=0.1, step=0.1)
    
    with col3:
        helado_premium_kg_per_day = st.number_input("Premium (kg)/día", value=0.6, min_value=0.1, step=0.1)
    
    if st.button(" Guardar Configuración de Tienda", type="primary"):
        if not name.strip():
            st.error(" El nombre de la tienda es obligatorio")
        else:
            st.success(" ¡Tienda configurada exitosamente!")
            st.info(" Funcionalidad completa disponible cuando todos los módulos estén cargados.")

def render_basic_view_stores():
    """Página básica para ver tiendas cuando UI no está disponible"""
    st.header(" Tiendas Registradas")
    
    st.warning(" Interfaz limitada - algunos componentes no están disponibles")
    
    if DATABASE_AVAILABLE:
        try:
            stores = db_service.list_stores()
            if stores:
                st.markdown(f"** Total de tiendas:** {len(stores)}")
                for store in stores:
                    with st.container():
                        st.markdown(f"###  {store.name}")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f" Ubicación: {store.location.city}, {store.location.country}")
                            st.write(f" Coordenadas: {store.location.lat:.4f}, {store.location.lon:.4f}")
                        with col2:
                            if store.base_demand:
                                st.write(" Demanda Base:")
                                for product, demand in store.base_demand.items():
                                    st.write(f"  • {product}: {demand}")
                        st.divider()
            else:
                st.info(" No hay tiendas registradas aún.")
        except Exception as e:
            st.error(f" Error cargando tiendas: {e}")
    else:
        st.info(" Base de datos no disponible. Configura el sistema para ver las tiendas.")

def render_basic_generate_suggestion():
    """Página básica para generar sugerencias cuando UI no está disponible"""
    st.header(" Generar Sugerencia Semanal")
    
    st.warning(" Interfaz limitada - algunos componentes no están disponibles")
    
    st.markdown("""
    ### Generador de Sugerencias Inteligente
    
    Esta funcionalidad permite generar sugerencias de compra basadas en:
    -  Pronóstico del clima
    -  Feriados y eventos especiales
    -  Análisis de demanda histórica
    -  Estrategias personalizadas
    """)
    
    strategy = st.selectbox("Estrategia", ["conservadora", "balanceada", "agresiva"])
    
    if st.button(" Generar Sugerencia"):
        st.info(" Funcionalidad completa disponible cuando todos los módulos estén cargados.")
        st.markdown("""
        ** Sugerencia de ejemplo:**
        -  Palitos: 25 unidades
        -  Conos: 20 unidades  
        -  Vasitos: 15 unidades
        -  Potes: 8 kg
        -  Premium: 5 kg
        """)

def render_basic_history():
    """Página básica para historial cuando UI no está disponible"""
    st.header(" Historial & Analytics")
    
    st.warning(" Interfaz limitada - algunos componentes no están disponibles")
    
    st.markdown("""
    ### Análisis y Estadísticas
    
    Esta sección incluye:
    -  Historial de sugerencias
    -  Análisis de rendimiento
    -  ROI y rentabilidad
    -  Precisión de predicciones
    """)
    
    if DATABASE_AVAILABLE:
        st.info(" Historial disponible cuando el sistema esté completamente configurado.")
    else:
        st.info(" Base de datos no disponible. Configura el sistema para ver el historial.")

def main():
    """Función principal de la aplicación"""
    if not STREAMLIT_AVAILABLE:
        print(" No se puede ejecutar: Streamlit no está disponible")
        print(" Solución: pip install streamlit")
        return
        
    if not init_app():
        return
    
    # Header principal
    if UI_AVAILABLE:
        ui_components.render_header()
    else:
        st.title(" Sistema de Sugerencias Inteligente")
        st.subheader("Heladería Grido - Paraguay")
        st.markdown("*Optimiza tus compras semanales usando IA, pronóstico del clima y análisis de demanda*")
    
    # Navegación en sidebar
    if UI_AVAILABLE:
        tab = ui_components.render_sidebar_navigation()
        upcoming_holidays = get_upcoming_holidays()
        ui_components.render_holidays_sidebar(upcoming_holidays)
    else:
        # Fallback navigation
        with st.sidebar:
            st.markdown("###  Panel de Control")
            tab = st.radio(
                "Navegación",
                [" Configurar Tienda", " Ver Tiendas", " Generar Sugerencia", " Historial & Analytics"],
                index=0
            )
            
            st.markdown("###  Características")
            st.markdown("""
            -  Pronóstico climático 7 días
            -  Detección automática ubicación  
            -  Feriados y eventos Paraguay
            -  3 estrategias de compra
            -  Análisis ROI y capacidad
            """)
            
            # Mostrar próximos feriados
            upcoming_holidays = get_upcoming_holidays()
            if upcoming_holidays:
                st.markdown("###  Próximos Feriados")
                for holiday in upcoming_holidays[:3]:
                    days = holiday['days_until']
                    name = holiday['name']
                    if days == 0:
                        st.markdown(f" **{name}** - ¡Hoy!")
                    elif days == 1:
                        st.markdown(f" **{name}** - Mañana")
                    else:
                        st.markdown(f" **{name}** - En {days} días")
    
    # Información adicional en sidebar
    with st.sidebar:
        st.divider()
        st.markdown("### ℹ Información")
        st.markdown("""
        ** Versión:** 2.0.0  
        ** Última actualización:** Nov 2025  
        ** Fuente clima:** OpenWeatherMap  
        ** Ubicación:** IP Geolocation  
        """)
        
        # Estado del sistema
        st.markdown("###  Estado del Sistema")
        if DATABASE_AVAILABLE:
            try:
                stores_count = len(db_service.get_stores())
                suggestions_count = len(db_service.get_all_suggestions(limit=1000))
                
                st.success(" Sistema operativo")
                st.metric(" Tiendas", stores_count)
                st.metric(" Sugerencias", suggestions_count)
                
            except Exception as e:
                st.error(" Error de sistema")
                logger.error(f"Error obteniendo estadísticas: {e}")
        else:
            st.warning(" Base de datos no disponible")
            st.info(" Algunas funciones están limitadas")
    
    # Contenido principal basado en la navegación
    try:
        if UI_AVAILABLE:
            # Usar páginas completas
            if tab == APP_TEXTS['navigation']['configure_store']:
                pages.configure_store_page()
            elif tab == APP_TEXTS['navigation']['view_stores']:
                pages.view_stores_page()
            elif tab == APP_TEXTS['navigation']['generate_suggestion']:
                pages.generate_suggestion_page()
            elif tab == APP_TEXTS['navigation']['history']:
                pages.history_analytics_page()
            else:
                st.error(f"Página no encontrada: {tab}")
        else:
            # Páginas de fallback básicas
            if "Configurar Tienda" in tab:
                render_basic_configure_store()
            elif "Ver Tiendas" in tab:
                render_basic_view_stores()
            elif "Generar Sugerencia" in tab:
                render_basic_generate_suggestion()
            elif "Historial" in tab:
                render_basic_history()
            else:
                st.error(f"Página no encontrada: {tab}")
            
    except Exception as e:
        logger.error(f"Error en página {tab}: {e}")
        st.error(f" Error cargando la página. Por favor, intenta de nuevo.")
        st.exception(e)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p> <strong>Sistema de Sugerencias Inteligente</strong> - Heladería Grido Paraguay</p>
        <p>Desarrollado con  usando Streamlit, Python y tecnologías de IA</p>
        <p><small>© 2025 Grido Paraguay. Optimizando heladerías con inteligencia artificial.</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Error crítico en la aplicación: {e}")
        st.error(" Error crítico del sistema. Contacte al administrador.")
        st.exception(e)