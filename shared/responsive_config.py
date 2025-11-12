"""
Configuración Responsive para BusinessSuite
Optimizaciones específicas para dispositivos móviles y tablets
"""

import streamlit as st

def inject_responsive_config():
    """Inyecta configuraciones responsive globales"""
    
    # Meta tags para dispositivos móviles
    mobile_meta = """
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="theme-color" content="#667eea">
    """
    
    st.markdown(mobile_meta, unsafe_allow_html=True)

def add_mobile_optimizations():
    """Agrega optimizaciones específicas para móviles"""
    
    mobile_js = """
    <script>
    // Función para detectar dispositivo móvil
    function isMobileDevice() {
        return (typeof window.orientation !== "undefined") || (navigator.userAgent.indexOf('IEMobile') !== -1);
    }
    
    // Función para obtener el tamaño de pantalla
    function getScreenSize() {
        return {
            width: window.innerWidth,
            height: window.innerHeight,
            isMobile: window.innerWidth <= 768,
            isTablet: window.innerWidth > 768 && window.innerWidth <= 1024,
            isDesktop: window.innerWidth > 1024
        };
    }
    
    // Agregar clase CSS según el dispositivo
    function addDeviceClass() {
        const screen = getScreenSize();
        const body = document.body;
        
        // Limpiar clases previas
        body.classList.remove('mobile-device', 'tablet-device', 'desktop-device');
        
        if (screen.isMobile) {
            body.classList.add('mobile-device');
        } else if (screen.isTablet) {
            body.classList.add('tablet-device');
        } else {
            body.classList.add('desktop-device');
        }
    }
    
    // Optimización para inputs en iOS (prevenir zoom)
    function preventIOSZoom() {
        if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
            const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], select, textarea');
            inputs.forEach(input => {
                if (input.style.fontSize === '' || parseFloat(input.style.fontSize) < 16) {
                    input.style.fontSize = '16px';
                }
            });
        }
    }
    
    // Mejorar scrolling en móviles
    function improveScrolling() {
        if (isMobileDevice()) {
            document.body.style.webkitOverflowScrolling = 'touch';
            document.body.style.overflowScrolling = 'touch';
        }
    }
    
    // Manejar orientación de pantalla
    function handleOrientationChange() {
        setTimeout(() => {
            addDeviceClass();
            preventIOSZoom();
        }, 100);
    }
    
    // Inicializar optimizaciones
    document.addEventListener('DOMContentLoaded', function() {
        addDeviceClass();
        preventIOSZoom();
        improveScrolling();
    });
    
    // Manejar cambios de tamaño de ventana
    window.addEventListener('resize', addDeviceClass);
    window.addEventListener('orientationchange', handleOrientationChange);
    
    // Actualizar clases periódicamente (para contenido dinámico)
    setInterval(function() {
        preventIOSZoom();
    }, 2000);
    </script>
    """
    
    st.markdown(mobile_js, unsafe_allow_html=True)

def get_responsive_columns(mobile_cols=1, tablet_cols=2, desktop_cols=4):
    """
    Retorna configuración de columnas responsive
    
    Args:
        mobile_cols: Número de columnas en móvil
        tablet_cols: Número de columnas en tablet  
        desktop_cols: Número de columnas en desktop
    
    Returns:
        Lista de proporciones para st.columns()
    """
    
    # Por defecto usar configuración de desktop
    # Streamlit manejará automáticamente el responsive con CSS
    return [1] * desktop_cols

def add_responsive_dataframe_css():
    """Agrega CSS específico para hacer las tablas responsive"""
    
    dataframe_css = """
    <style>
    /* Tablas responsive */
    @media (max-width: 768px) {
        .stDataFrame {
            font-size: 0.8rem !important;
        }
        
        .stDataFrame > div {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }
        
        .stDataFrame table {
            min-width: 600px !important;
        }
        
        .stDataFrame th, .stDataFrame td {
            white-space: nowrap !important;
            padding: 0.3rem !important;
        }
    }
    
    @media (max-width: 480px) {
        .stDataFrame {
            font-size: 0.7rem !important;
        }
        
        .stDataFrame th, .stDataFrame td {
            padding: 0.2rem !important;
        }
    }
    </style>
    """
    
    st.markdown(dataframe_css, unsafe_allow_html=True)

def configure_mobile_sidebar():
    """Configura la sidebar para móviles"""
    
    sidebar_css = """
    <style>
    /* Sidebar responsive */
    @media (max-width: 768px) {
        .css-1d391kg {
            width: 280px !important;
        }
        
        .css-1d391kg .stButton > button {
            width: 100% !important;
            margin-bottom: 0.5rem !important;
            font-size: 0.9rem !important;
            padding: 0.6rem !important;
        }
        
        .css-1d391kg .stMarkdown {
            font-size: 0.9rem !important;
        }
        
        .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
            font-size: 1.1rem !important;
        }
    }
    
    @media (max-width: 480px) {
        .css-1d391kg {
            width: 260px !important;
        }
        
        .css-1d391kg .stButton > button {
            font-size: 0.85rem !important;
            padding: 0.5rem !important;
        }
    }
    </style>
    """
    
    st.markdown(sidebar_css, unsafe_allow_html=True)

def add_touch_optimizations():
    """Agrega optimizaciones para dispositivos táctiles"""
    
    touch_css = """
    <style>
    /* Optimizaciones táctiles */
    @media (hover: none) and (pointer: coarse) {
        .stButton > button {
            min-height: 44px !important;
            min-width: 44px !important;
            touch-action: manipulation !important;
            -webkit-tap-highlight-color: rgba(0,0,0,0.1) !important;
        }
        
        .stSelectbox > div > div,
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            min-height: 44px !important;
            touch-action: manipulation !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            min-height: 44px !important;
            touch-action: manipulation !important;
        }
        
        /* Eliminar hover effects en táctiles */
        .feature-card:hover {
            transform: none !important;
        }
        
        .stButton > button:hover {
            transform: scale(0.98) !important;
        }
    }
    </style>
    """
    
    st.markdown(touch_css, unsafe_allow_html=True)

def setup_responsive_environment():
    """Configura todo el entorno responsive"""
    
    inject_responsive_config()
    add_mobile_optimizations()
    add_responsive_dataframe_css()
    configure_mobile_sidebar()
    add_touch_optimizations()

# Función principal para usar en los módulos
def make_responsive():
    """Función principal para hacer responsive cualquier página"""
    setup_responsive_environment()