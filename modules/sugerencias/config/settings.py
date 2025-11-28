"""
Configuración principal del sistema
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from .productos_completos import PRODUCT_SPECS_COMPLETO, PRODUCT_NAME_MAPPING

load_dotenv()

# Determinar la ruta del módulo
MODULE_DIR = Path(__file__).parent.parent

# APIs y URLs
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', 'demo')
IPAPI_URL = "http://ip-api.com/json/"
OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"
INFOCLIMA_BASE_URL = "https://www.infoclima.com"

# Base de datos - Ajustada para la estructura del módulo
DB_PATH = os.path.join(MODULE_DIR, "data", "stores.db")

# Configuración de logs
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configuración de la aplicación
APP_TITLE = "Grido - Sistema de Sugerencias IA"
APP_ICON = ""

# Timeouts y límites
API_TIMEOUT = 10  # segundos
MAX_FORECAST_DAYS = 7
MIN_ROI_THRESHOLD = 0.85  # 85%

# Configuración específica de Paraguay
PARAGUAY_TIMEZONE = "America/Asuncion"
DEFAULT_LOCATION = {
    "lat": -25.2637,
    "lon": -57.5759,
    "city": "Asunción",
    "country": "Paraguay"
}

# Feriados de Paraguay 2025
PARAGUAY_HOLIDAYS = {
    "2025-01-01": "Año Nuevo",
    "2025-03-01": "Día de los Héroes",
    "2025-04-17": "Jueves Santo",
    "2025-04-18": "Viernes Santo",
    "2025-05-01": "Día del Trabajador",
    "2025-05-15": "Día de la Independencia",
    "2025-06-12": "Día de la Paz del Chaco",
    "2025-08-15": "Fundación de Asunción",
    "2025-09-29": "Día de la Victoria de Boquerón",
    "2025-12-08": "Día de la Virgen de Caacupé",
    "2025-12-25": "Navidad"
}

# Catálogo completo de productos Grido
PRODUCT_SPECS = PRODUCT_SPECS_COMPLETO
# Factores de temperatura para demanda
TEMP_FACTORS = {
    "cold": {"max_temp": 20, "factor": 0.3},
    "normal": {"max_temp": 25, "factor": 1.0},
    "warm": {"max_temp": 30, "factor": 1.8},
    "hot": {"max_temp": float('inf'), "factor": 2.5}
}

# Estrategias de compra
STRATEGIES = {
    "conservadora": {
        "name": "Conservadora",
        "description": "Minimiza riesgo - Inversión ₱5-7M",
        "target_rotation": 0.70,  # Solo 70% de la demanda proyectada
        "risk_tolerance": 0.05
    },
    "balanceada": {
        "name": "Balanceada", 
        "description": "Balance entre ventas y riesgo - Inversión ₱8-10M",
        "target_rotation": 0.80,  # 80% de la demanda proyectada
        "risk_tolerance": 0.10
    },
    "agresiva": {
        "name": "Agresiva",
        "description": "Maximiza ventas - Inversión ₱12-15M",
        "target_rotation": 1.0,  # 100% de la demanda proyectada
        "risk_tolerance": 0.15
    }
}

# Configuración de UI
UI_CONFIG = {
    "theme": {
        "primary_color": "#4ECDC4",
        "secondary_color": "#FF6B6B",
        "background_color": "#FFFFFF",
        "text_color": "#333333"
    },
    "layout": {
        "sidebar_width": 300,
        "main_padding": "2rem",
        "card_border_radius": "10px"
    }
}

# Textos de la aplicación
APP_TEXTS = {
    "navigation": {
        "configure_store": " Configurar Tienda",
        "view_stores": " Ver Tiendas", 
        "generate_suggestion": " Generar Sugerencia",
        "history": " Historial & Analytics"
    },
    "welcome": {
        "title": "Sistema de Sugerencias Inteligente",
        "subtitle": "Heladería Grido - Paraguay",
        "description": "Optimiza tus compras semanales usando IA, pronóstico del clima y análisis de demanda"
    },
    "titles": {
        "main": "Sistema de Sugerencias Inteligente",
        "subtitle": "Heladería Grido - Paraguay",
        "description": "Optimiza tus compras semanales usando IA, pronóstico del clima y análisis de demanda"
    },
    "messages": {
        "success_store_saved": "¡Tienda configurada exitosamente!",
        "error_no_stores": "No hay tiendas registradas aún.",
        "warning_limited_interface": "Interfaz limitada - algunos componentes no están disponibles"
    },
    "features": [
        " Pronóstico climático 7 días",
        " Detección automática ubicación",
        " Feriados y eventos Paraguay", 
        " 3 estrategias de compra",
        " Análisis ROI y capacidad"
    ]
}

# Estrategias de compra (alias para STRATEGIES)
PURCHASE_STRATEGIES = STRATEGIES

# Base de datos de tiendas Grido conocidas en Paraguay
GRIDO_STORES_DATABASE = {
    "asuncion": [
        {
            "name": "Grido Seminario",
            "address": "José Asunción Flores 1102, Asunción",
            "lat": -25.304028,
            "lon": -57.607777,
            "verified": True,
            "phone": "+595 21 555-0102"
        },
        {
            "name": "Grido Palma",
            "address": "Palma, Asunción",
            "lat": -25.283000,
            "lon": -57.633447,
            "verified": True,
            "phone": "+595 21 555-0103"
        },
        {
            "name": "Grido Carlos Antonio Lopez",
            "address": "Carlos Antonio Lopez, Asunción",
            "lat": -25.288962101555896,
            "lon": -57.65469207117073,
            "verified": True,
            "phone": "+595 21 555-0105"
        },
        {
            "name": "Grido Republica Argentina",
            "address": "Republica Argentina, Asunción",
            "lat": -25.322406358855265,
            "lon": -57.594993710760534,
            "verified": True,
            "phone": "+595 21 555-0106"
        },
        {
            "name": "Grido Acuña de Figeroa",
            "address": "Acuña de Figeroa, Asunción",
            "lat": -25.298336576965422,
            "lon": -57.635965169112055,
            "verified": True,
            "phone": "+595 21 555-0107"
        },
        {
            "name": "Grido Mcal. Estigarribia",
            "address": "Mcal. Estigarribia, Asunción",
            "lat": -25.28298041723611,
            "lon": -57.63348090315892,
            "verified": True,
            "phone": "+595 21 555-0108"
        },
        {
            "name": "Grido Shopping del Sol",
            "address": "Shopping del Sol, Asunción",
            "lat": 0,
            "lon": 0,
            "verified": False,
            "phone": "+595 21 555-0100"
        },
        {
            "name": "Grido Villa Morra",
            "address": "Villa Morra Shopping, Asunción", 
            "lat": 0,
            "lon": 0,
            "verified": False,
            "phone": "+595 21 555-0101"
        },
        {
            "name": "Grido Pinedo Shopping",
            "address": "Pinedo Shopping, Asunción",
            "lat": 0,
            "lon": 0,
            "verified": False,
            "phone": "+595 21 555-0104"
        }
    ],
    "san_lorenzo": [
        {
            "name": "Grido San Lorenzo",
            "address": "Av. Eusebio Ayala, San Lorenzo",
            "lat": 0,
            "lon": 0,
            "verified": False,
            "phone": "+595 21 555-0200"
        }
    ],
    "fernando_de_la_mora": [
        {
            "name": "Grido Fernando de la Mora",
            "address": "Av. Mcal. López, Fernando de la Mora",
            "lat": 0,
            "lon": 0,
            "verified": False,
            "phone": "+595 21 555-0300"
        }
    ],
    "luque": [
        {
            "name": "Grido Luque",
            "address": "14 de Mayo, Luque",
            "lat": 0,
            "lon": 0,
            "verified": False,
            "phone": "+595 21 555-0400"
        }
    ]
}

# Función auxiliar para buscar tiendas Grido
def search_grido_stores(query: str) -> list:
    """
    Busca tiendas Grido por nombre o ubicación
    
    Args:
        query: Texto de búsqueda
    
    Returns:
        Lista de tiendas que coinciden
    """
    query_lower = query.lower()
    results = []
    
    for city, stores in GRIDO_STORES_DATABASE.items():
        for store in stores:
            # Buscar en nombre
            if query_lower in store['name'].lower():
                results.append({**store, 'match_type': 'name', 'city': city})
                continue
            
            # Buscar en dirección
            if query_lower in store['address'].lower():
                results.append({**store, 'match_type': 'address', 'city': city})
                continue
                
            # Buscar en ciudad
            if query_lower in city.replace('_', ' '):
                results.append({**store, 'match_type': 'city', 'city': city})
    
    return results