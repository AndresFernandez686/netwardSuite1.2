
"""
Páginas de la aplicación Streamlit
"""
import os

# Importaciones seguras
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from typing import List, Optional
from datetime import datetime, timedelta

# Importar modelos y servicios de manera segura
try:
    from ..models.data_models import Store, LocationInfo
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    # Definir clases básicas como fallback
    class Store:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class LocationInfo:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

try:
    from ..services.location_service import location_service
    LOCATION_SERVICE_AVAILABLE = True
except ImportError:
    LOCATION_SERVICE_AVAILABLE = False
from ..services.database_service import db_service
from ..services.weather_service import weather_service
from ..core.suggestion_engine import suggestion_engine
from ..ui.components import ui_components
from ..config.settings import PARAGUAY_HOLIDAYS

# ============================================================================
# FUNCIONES HELPER
# ============================================================================

def _process_inventory_file(uploaded_file, category_name: str):
    """
    Procesa un archivo de inventario cargado
    
    Args:
        uploaded_file: Archivo subido por streamlit
        category_name: Nombre de la categoría (Impulsivos/Granel)
        
    Returns:
        Lista de diccionarios con el inventario o None si hay error
    """
    try:
        if not PANDAS_AVAILABLE:
            st.error("❌ Pandas no está disponible. Instala pandas para cargar archivos Excel.")
            return None
            
        import pandas as pd
        
        try:
            import openpyxl
        except ImportError:
            st.error("❌ openpyxl no está instalado. Ejecuta: pip install openpyxl")
            return None
        
        # Leer el archivo según su extensión
        file_name = uploaded_file.name
        if file_name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        # FORMATO DIFERENTE SEGÚN CATEGORÍA
        if category_name == "Granel":
            # FORMATO GRANEL: Estado | Producto | Cajas Cerradas | Cajas Abiertas | Kgs Abiertas | Total Kgs
            required_columns_granel = {
                'Estado': ['Estado', 'estado', 'ESTADO'],
                'Producto': ['Producto', 'producto', 'PRODUCTO'],
                'Cajas Cerradas': ['Cajas Cerradas', 'cajas cerradas', 'CAJAS CERRADAS', 'Cajas_Cerradas'],
                'Cajas Abiertas': ['Cajas Abiertas', 'cajas abiertas', 'CAJAS ABIERTAS', 'Cajas_Abiertas'],
                'Kgs Abiertas': ['Kgs Abiertas', 'kgs abiertas', 'KGS ABIERTAS', 'Kgs_Abiertas', 'Kgs.Abiertas'],
                'Total Kgs': ['Total Kgs', 'total kgs', 'TOTAL KGS', 'Total_Kgs']
            }
            
            # Buscar columnas
            found_columns = {}
            for req_col, variations in required_columns_granel.items():
                for col in df.columns:
                    clean_col = str(col).strip()
                    if clean_col in variations or any(v.lower() in clean_col.lower() for v in variations):
                        found_columns[req_col] = col
                        break
            
            # Verificar columnas mínimas necesarias
            required_min = ['Estado', 'Producto', 'Cajas Cerradas', 'Cajas Abiertas', 'Kgs Abiertas']
            if all(col in found_columns for col in required_min):
                # Renombrar columnas
                rename_map = {v: k for k, v in found_columns.items()}
                df = df.rename(columns=rename_map)
                
                # Procesar datos de GRANEL
                inventory_data = []
                KG_POR_CAJA_CERRADA = 7.8
                
                for _, row in df.iterrows():
                    # Limpiar y convertir valores (remover "kg" si existe)
                    def clean_value(val):
                        """Limpia valores como '4.6kg', '5,236kg' o '7,5kg' convirtiéndolos a float"""
                        if pd.isna(val) or val == '' or val == 'N/A':
                            return 0
                        # Convertir a string y limpiar
                        val_str = str(val).strip().lower()
                        # Remover 'kg' si existe
                        val_str = val_str.replace('kg', '').replace('kgs', '').strip()
                        # Reemplazar coma por punto (formato europeo: 5,236 → 5.236)
                        val_str = val_str.replace(',', '.')
                        try:
                            return float(val_str)
                        except (ValueError, AttributeError):
                            return 0
                    
                    # Calcular bultos totales (cajas cerradas + cajas abiertas)
                    cajas_cerradas = clean_value(row.get('Cajas Cerradas', 0))
                    cajas_abiertas = clean_value(row.get('Cajas Abiertas', 0))
                    kgs_abiertas = clean_value(row.get('Kgs Abiertas', 0))
                    
                    # Total de bultos = cajas cerradas + cajas abiertas
                    total_bultos = int(cajas_cerradas + cajas_abiertas)
                    
                    # Determinar estado del stock
                    estado_raw = str(row.get('Estado', 'STOCK OK')).upper()
                    
                    # CRÍTICO: Si no hay bultos pero hay kgs (solo caja abierta parcial), es SIN STOCK
                    if total_bultos == 0 and kgs_abiertas > 0:
                        estado_stock = 'SIN STOCK'  # CRÍTICO: solo quedan restos
                    elif 'OK' in estado_raw or 'SUFICIENTE' in estado_raw:
                        estado_stock = 'STOCK OK'
                    elif 'MEDIO' in estado_raw or 'BAJO' in estado_raw:
                        estado_stock = 'STOCK BAJO'
                    elif 'SIN' in estado_raw or estado_raw == 'N/A':
                        estado_stock = 'SIN STOCK'
                    else:
                        estado_stock = 'STOCK OK'
                    
                    # Calcular total de kgs CORRECTAMENTE (7.8kg por caja cerrada)
                    total_kgs = (cajas_cerradas * KG_POR_CAJA_CERRADA) + kgs_abiertas
                    
                    item = {
                        'Producto': str(row.get('Producto', '')),
                        'Bultos': total_bultos,
                        'Unidad': total_kgs,  # TOTAL KGS (no solo abiertas)
                        'Estado Stock': estado_stock,
                        '_tipo_producto': 'granel',
                        '_cajas_cerradas': cajas_cerradas,
                        '_cajas_abiertas': cajas_abiertas,
                        '_kgs_abiertas': kgs_abiertas,
                        '_total_kgs': total_kgs
                    }
                    inventory_data.append(item)
                
                st.success(f"✅ {category_name} cargado: {len(inventory_data)} productos (formato Granel)")
                
                # Mostrar resumen
                with st.expander(f" Ver detalles de {category_name}"):
                    st.dataframe(df, use_container_width=True)
                    
                    # Estadísticas
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(" Total productos", len(inventory_data))
                    with col2:
                        total_cajas = sum(item['Bultos'] for item in inventory_data)
                        st.metric(" Total cajas", f"{total_cajas}")
                    with col3:
                        total_kgs = sum(item['_total_kgs'] for item in inventory_data)
                        st.metric(" Total kg", f"{total_kgs:.1f}kg")
                    with col4:
                        stock_bajo = sum(1 for item in inventory_data if 'BAJO' in item['Estado Stock'] or 'MEDIO' in item['Estado Stock'])
                        st.metric("⚠️ Stock bajo/medio", f"{stock_bajo}")
                
                return inventory_data
            else:
                st.error(f" El archivo de Granel no tiene todas las columnas requeridas")
                st.warning(f"Columnas encontradas: {list(found_columns.keys())}")
                st.warning(f"Columnas necesarias: {required_min}")
                st.info("📋 Columnas disponibles en tu archivo:")
                st.code(list(df.columns))
                return None
        
        else:
            # FORMATO IMPULSIVOS: Producto | Bultos | Unidad | Estado Stock
            required_columns = ['Producto', 'Bultos', 'Unidad', 'Estado Stock']
            
            # Buscar columnas con flexibilidad
            found_columns = {}
            for req_col in required_columns:
                for col in df.columns:
                    clean_col = str(col).strip()
                    if req_col.lower() in clean_col.lower() or clean_col.lower() in req_col.lower():
                        found_columns[req_col] = col
                        break
            
            # Verificar si encontramos todas las columnas
            if len(found_columns) == len(required_columns):
                # Renombrar columnas para estandarizar
                rename_map = {v: k for k, v in found_columns.items()}
                df = df.rename(columns=rename_map)
                inventory_data = df[required_columns].to_dict('records')
                
                # AGREGAR METADATA DE TIPO Y VALIDAR ESTADO CRÍTICO
                for item in inventory_data:
                    item['_tipo_producto'] = 'impulsivo'
                    
                    # CRÍTICO: Si Bultos = 0 pero tiene Unidad > 0, marcar como SIN STOCK
                    bultos = float(item.get('Bultos', 0) or 0)
                    unidad = float(item.get('Unidad', 0) or 0)
                    if bultos == 0 and unidad > 0:
                        item['Estado Stock'] = 'SIN STOCK'  # Solo quedan unidades sueltas
                
                st.success(f"✅ {category_name} cargado: {len(inventory_data)} productos")
                
                # Mostrar resumen
                with st.expander(f" Ver detalles de {category_name}"):
                    st.dataframe(df, use_container_width=True)
                    
                    # Estadísticas
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(" Total productos", len(df))
                    with col2:
                        total_bultos = df['Bultos'].sum()
                        st.metric(" Total bultos", f"{total_bultos:.0f}")
                    with col3:
                        stock_bajo = len(df[df['Estado Stock'] == 'STOCK BAJO'])
                        st.metric("⚠️ Stock bajo", f"{stock_bajo}")
                    with col4:
                        sin_stock = len(df[df['Estado Stock'] == 'SIN STOCK'])
                        st.metric(" Sin stock", f"{sin_stock}")
                
                return inventory_data
            else:
                st.error(f" El archivo no tiene todas las columnas requeridas")
                st.warning(f"Se encontraron {len(found_columns)} de {len(required_columns)} columnas:")
                for req, found in found_columns.items():
                    st.success(f"✓ {req} → encontrada como '{found}'")
                missing = set(required_columns) - set(found_columns.keys())
                for miss in missing:
                    st.error(f"✗ {miss} → NO encontrada")
                st.info("📋 Columnas disponibles en tu archivo:")
                st.code(list(df.columns))
                return None
            
    except Exception as e:
        st.error(f" Error al leer el archivo: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None


class Pages:
    """Páginas de la aplicación"""
    
    @staticmethod
    def configure_store_page():
        """Página para configurar una nueva tienda"""
    
    
        # Guía de búsqueda
        with st.expander(" Guía de Búsqueda Inteligente"):
            st.markdown("""
            ** Búsqueda Geográfica Mejorada:**
            
            Ahora puedes buscar franquicias Grido usando referencias geográficas específicas:
            
            ** Ejemplos de búsqueda efectiva:**
            - **"Grido Seminario"** → Encuentra tiendas cerca de calles/barrios "Seminario"
            - **"Grido Villa Morra"** → Busca en el barrio Villa Morra
            - **"Grido Shopping"** → Encuentra sucursales en centros comerciales
            - **"Grido Aeropuerto"** → Localiza la tienda del aeropuerto
            - **"Grido Centro"** → Busca en el centro de la ciudad
            
            ** Cómo funciona:**
            1. **Búsqueda Local** (93+ tiendas) - Más rápida y precisa
            2. **Matching Geográfico** - Relaciona con calles y barrios
            
            ** Tip:** Solo escribe la referencia geográfica después de "Grido"
            """)
        
        # Sistema de búsqueda local
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_query = st.text_input(
                " Buscar tienda",
                placeholder="Ej: 'Grido Seminario', 'Grido Villa Morra', 'Grido Shopping'",
                help=" Búsqueda geográfica: usa referencias como barrios, calles o lugares conocidos"
            )
        
        with col2:
            search_type = st.selectbox(
                "Tipo de búsqueda",
                [" Solo tiendas Grido", " Dirección general"],
                help="Selecciona el tipo de búsqueda",
                index=0
            )
        
        # Mostrar búsqueda
        if search_query and len(search_query) >= 3:
            with st.spinner(" Buscando tiendas..."):
                try:
                    if search_type == " Solo tiendas Grido":
                        # Usar búsqueda inteligente con contexto geográfico
                        if LOCATION_SERVICE_AVAILABLE:
                            grido_results = location_service.search_grido_with_context(search_query)
                            
                            if grido_results:
                                st.success(f" Encontradas {len(grido_results)} tiendas Grido:")
                                
                                # Mostrar estadísticas de búsqueda
                                exact_matches = len([r for r in grido_results if r.get('match_type') == 'exact'])
                                fuzzy_matches = len([r for r in grido_results if r.get('match_type') == 'fuzzy'])
                                geographic_matches = len([r for r in grido_results if r.get('match_type') == 'geographic'])
                                
                                if exact_matches > 0:
                                    st.info(f" {exact_matches} coincidencias exactas")
                                elif geographic_matches > 0:
                                    st.info(f" {geographic_matches} coincidencias geográficas")
                                elif fuzzy_matches > 0:
                                    st.info(f" {fuzzy_matches} coincidencias similares")
                                
                                for i, store in enumerate(grido_results):
                                    # Usar un contenedor con key única para evitar problemas de renderizado
                                    store_key = f"store_container_{i}_{store.get('name', '').replace(' ', '_')}"
                                    
                                    with st.container():
                                        col1, col2, col3 = st.columns([3, 2, 1])
                                        
                                        with col1:
                                            # Mostrar indicador de calidad de coincidencia
                                            score = store.get('score', 0)
                                            match_type = store.get('match_type', 'unknown')
                                            source = store.get('source', 'unknown')
                                            
                                            # Iconos según tipo de coincidencia
                                            if match_type == 'geographic':
                                                quality_icon = ""
                                                match_desc = "Coincidencia geográfica"
                                            elif score >= 0.9:
                                                quality_icon = ""
                                                match_desc = "Coincidencia exacta"
                                            elif score >= 0.7:
                                                quality_icon = ""
                                                match_desc = "Coincidencia alta"
                                            else:
                                                quality_icon = ""
                                                match_desc = "Coincidencia parcial"
                                            
                                            st.markdown(f"**{quality_icon} {store['name']}**")
                                            st.markdown(f" {store['address']}")
                                            st.markdown(f" {store['city'].replace('_', ' ').title()}")
                                            
                                            # Mostrar términos de coincidencia geográfica si están disponibles
                                            if store.get('matched_terms'):
                                                matched_terms = ', '.join(store['matched_terms'])
                                                st.markdown(f" **Coincidencias:** {matched_terms}")
                                            
                                            # Mostrar teléfono si está disponible
                                            if store.get('phone'):
                                                st.markdown(f" {store['phone']}")
                                        
                                        with col2:
                                            st.markdown(f"** Información:**")
                                            st.markdown(f"Lat: {store['lat']:.4f}")
                                            st.markdown(f"Lon: {store['lon']:.4f}")
                                            
                                            # Mostrar puntaje de relevancia
                                            score_percent = int(score * 100)
                                            st.markdown(f" Relevancia: {score_percent}%")
                                            
                                            # Mostrar tipo de búsqueda usado
                                            source_icons = {
                                                'local_geographic': '',
                                                'local_traditional': '',
                                                'google_maps': '',
                                                'openstreetmap': '',
                                                'online_geographic': ''
                                            }
                                            source_icon = source_icons.get(source, '')
                                            st.markdown(f"{source_icon} {match_desc}")
                                            
                                            # Información adicional para resultados de Google Maps
                                            if source == 'google_maps':
                                                rating = store.get('rating', 0)
                                                if rating > 0:
                                                    stars = '' * int(rating)
                                                    st.markdown(f" **{rating}/5** {stars}")
                                                
                                                total_reviews = store.get('user_ratings_total', 0)
                                                if total_reviews > 0:
                                                    st.markdown(f" {total_reviews} reseñas")
                                        
                                        with col3:
                                            if st.button(f" Usar", key=f"grido_{i}"):
                                                st.session_state.selected_store = {
                                                    'name': store['name'],
                                                    'lat': store['lat'],
                                                    'lon': store['lon'],
                                                    'city': store['city'].replace('_', ' ').title(),
                                                    'country': 'Paraguay',
                                                    'address': store['address']
                                                }
                                                st.success(f" Tienda '{store['name']}' seleccionada!")
                                                st.rerun()
                                    
                                    # Separador entre resultados
                                    st.markdown("---")
                            else:
                                # Sugerencias de búsqueda si no se encuentra nada
                                st.warning(" No se encontraron tiendas Grido con ese término.")
                                st.markdown("""
                                ** Sugerencias de búsqueda:**
                                - Prueba con nombres de ciudades: *Asunción*, *Ciudad del Este*, *Encarnación*
                                - Usa nombres de barrios: *Centro*, *Villa Morra*, *Las Mercedes*
                                - Términos generales: *Shopping*, *Aeropuerto*, *Terminal*
                                - También puedes usar sinónimos: *CDE* por Ciudad del Este, *Asu* por Asunción
                                """)
                        else:
                            st.error(" Servicio de búsqueda no disponible")
                    
                    elif search_type == " Dirección general":
                        # Buscar usando el servicio de ubicación
                        if LOCATION_SERVICE_AVAILABLE:
                            search_results = location_service.search_address(search_query)
                            
                            if search_results:
                                st.success(f" Encontradas {len(search_results)} ubicaciones:")
                                
                                for i, result in enumerate(search_results[:3]):  # Limitar a 3 resultados
                                    with st.container():
                                        col1, col2, col3 = st.columns([3, 2, 1])
                                        
                                        with col1:
                                            st.markdown(f"** {result.get('address', 'Dirección')}**")
                                            st.markdown(f" {result.get('city', '')}, {result.get('country', '')}")
                                        
                                        with col2:
                                            st.markdown(f"** Coordenadas:**")
                                            st.markdown(f"Lat: {result['lat']:.4f}")
                                            st.markdown(f"Lon: {result['lon']:.4f}")
                                        
                                        with col3:
                                            if st.button(f" Usar", key=f"address_{i}"):
                                                st.session_state.selected_store = {
                                                    'name': search_query,
                                                    'lat': result['lat'],
                                                    'lon': result['lon'],
                                                    'city': result.get('city', ''),
                                                    'country': result.get('country', ''),
                                                    'address': result.get('address', '')
                                                }
                                                st.success(f" Ubicación seleccionada!")
                                                st.rerun()
                                        
                                        st.divider()
                            else:
                                st.warning(" No se encontraron resultados. Verifica la dirección o usa coordenadas manuales.")
                        else:
                            st.warning(" Servicio de búsqueda no disponible. Usa coordenadas manuales.")
                
                except Exception as e:
                    st.error(f" Error en la búsqueda: {e}")
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error en búsqueda: {e}")
        
        # Mostrar tienda seleccionada CON MAPA DE CONFIRMACIÓN
        if 'selected_store' in st.session_state:
            st.divider()
            store = st.session_state.selected_store
            
            # Contenedor destacado para la tienda seleccionada
            with st.container():
                st.success(" **¡TIENDA SELECCIONADA!**")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"###  {store['name']}")
                    st.write(f" **Dirección:** {store.get('address', 'N/A')}")
                    st.write(f" **Ciudad:** {store['city']}")
                    st.write(f" **País:** {store['country']}")
                with col2:
                    st.write(f"###  Ubicación")
                    st.write(f"**Latitud:** {store['lat']:.6f}")
                    st.write(f"**Longitud:** {store['lon']:.6f}")
                    
                    # Enlace para abrir en Google Maps
                    google_maps_link = f"https://www.google.com/maps/search/?api=1&query={store['lat']},{store['lon']}"
                    st.markdown(f"[ Ver en Google Maps]({google_maps_link})")
                
                # MAPA DE VISTA PREVIA PARA CONFIRMAR UBICACIÓN
                st.markdown("####  Confirma que esta es tu tienda:")
                
                # Usar mapa de Streamlit
                if PANDAS_AVAILABLE:
                    map_df = pd.DataFrame([[store['lat'], store['lon']]], columns=['lat', 'lon'])
                    st.map(map_df, zoom=17)
                else:
                    st.warning("Mapa no disponible (pandas no instalado)")
                
                # Botones de acción
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(" Confirmar y Continuar", type="primary", use_container_width=True, key="confirm_store"):
                        st.success(" ¡Ubicación confirmada! Completa el formulario abajo.")
                        st.session_state.store_confirmed = True
                with col2:
                    if st.button(" Buscar otra tienda", use_container_width=True, key="search_another"):
                        del st.session_state.selected_store
                        if 'store_confirmed' in st.session_state:
                            del st.session_state.store_confirmed
                        st.rerun()
        
        st.divider()
        
        # Obtener valores para el formulario
        if 'selected_store' in st.session_state:
            default_values = st.session_state.selected_store
            name = default_values.get('name', '')
            city = default_values.get('city', 'Asunción')
            country = default_values.get('country', 'Paraguay')
            lat = float(default_values.get('lat', -25.2637))
            lon = float(default_values.get('lon', -57.5759))
        else:
            name = ''
            city = 'Asunción'
            country = 'Paraguay'
            lat = -25.2637
            lon = -57.5759
        
        # Configuración de capacidad de almacenamiento
        st.subheader(" Capacidad de Almacenamiento")
        
        storage_capacity = st.number_input(
            "¿Cuántos bultos puede almacenar tu franquicia?",
            min_value=1,
            max_value=500,
            value=50,
            step=5,
            help="Número total de bultos que caben en tu espacio de almacenamiento"
        )
        
        st.divider()
        
        # Configuración de demanda base
        st.subheader("Demanda Semanal (Pedido para 7 días)")
        
        st.markdown("""
        Ingresa la cantidad TOTAL de cada producto que vendes en UNA SEMANA (7 días).
        Esta será la demanda base para calcular la sugerencia semanal.
        """)
        
        # USAR FORM PARA EVITAR RE-RENDERS CONSTANTES
        with st.form("demanda_form"):
            # Organizar productos por categorías
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Helado Granel", "Palitos", "Alfajores", "Bombones", "Otros"])
            
            # TAB 1: Helado a Granel y productos que se sirven
            with tab1:
                st.markdown("**Cajas de Helado a Granel**")
                st.caption("Cada caja contiene 7.8 kg - se usa para servir cucuruchos y potes")
                caja_granel = st.number_input("Cajas de helado (cajas/semana)", min_value=0, value=10, step=1, key="caja_granel")
                
                st.divider()
                st.markdown("**Cucuruchos (se sirven del granel)**")
                col1, col2 = st.columns(2)
                with col1:
                    cucurucho_simple = st.number_input("Cucurucho 1 Sabor (und/semana)", min_value=0, value=30, step=5, key="cucurucho_simple")
                    cucurucho_doble = st.number_input("Cucurucho 2 Sabores (und/semana)", min_value=0, value=20, step=5, key="cucurucho_doble")
                with col2:
                    cucurucho_triple = st.number_input("Cucurucho 3 Sabores (und/semana)", min_value=0, value=15, step=5, key="cucurucho_triple")
                    cucurucho_triple_bañado = st.number_input("Cucurucho 3 Sabores Bañado (und/semana)", min_value=0, value=5, step=5, key="cucurucho_triple_bañado")
                
                st.divider()
                st.markdown("**Potes (se sirven del granel)**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    pote_cuarto = st.number_input("Pote 1/4 KG (und/semana)", min_value=0, value=15, step=5, key="pote_cuarto")
                with col2:
                    pote_medio = st.number_input("Pote 1/2 KG (und/semana)", min_value=0, value=10, step=5, key="pote_medio")
                with col3:
                    pote_kilo = st.number_input("Pote 1 KG (und/semana)", min_value=0, value=5, step=5, key="pote_kilo")
                
                st.divider()
                st.markdown("**Batidos (se sirven del granel)**")
                col1, col2 = st.columns(2)
                with col1:
                    batido_capuccino = st.number_input("Batido Capuccino (und/semana)", min_value=0, value=8, step=2, key="batido_capuccino")
                with col2:
                    batido_grido = st.number_input("Batido Grido (und/semana)", min_value=0, value=10, step=2, key="batido_grido")
            
            # TAB 2: Palitos
            with tab2:
                st.markdown("**Palitos por Caja**")
                st.caption("1 Bulto = 10 cajas de 10 unidades c/u")
                col1, col2, col3 = st.columns(3)
                with col1:
                    palito_frutal = st.number_input("Palito Frutal (und/semana)", min_value=0, value=20, step=5, key="palito_frutal")
                with col2:
                    palito_cremoso = st.number_input("Palito Cremoso (und/semana)", min_value=0, value=15, step=5, key="palito_cremoso")
                with col3:
                    palito_bombon = st.number_input("Palito Bombón (und/semana)", min_value=0, value=25, step=5, key="palito_bombon")
            
            # TAB 3: Alfajores (Postres)
            with tab3:
                st.markdown("**Alfajores por Caja**")
                st.caption("1 Bulto = 6 cajas de 6 unidades c/u")
                col1, col2 = st.columns(2)
                with col1:
                    alfajor_crocantino = st.number_input("Crocantino (und/semana)", min_value=0, value=10, step=2, key="alfajor_crocantino")
                    alfajor_delicia = st.number_input("Delicia (und/semana)", min_value=0, value=10, step=2, key="alfajor_delicia")
                with col2:
                    alfajor_casatta = st.number_input("Casatta (und/semana)", min_value=0, value=8, step=2, key="alfajor_casatta")
                    alfajor_almendrado = st.number_input("Almendrado (und/semana)", min_value=0, value=8, step=2, key="alfajor_almendrado")
            
            # TAB 4: Bombones
            with tab4:
                st.markdown("**Bombones por Caja**")
                st.caption("1 Bulto = 6 cajas de 8 unidades c/u")
                col1, col2 = st.columns(2)
                with col1:
                    bombon_escoces = st.number_input("Bombón Escocés (und/semana)", min_value=0, value=6, step=2, key="bombon_escoces")
                    bombon_suizo = st.number_input("Bombón Suizo (und/semana)", min_value=0, value=6, step=2, key="bombon_suizo")
                with col2:
                    bombon_crocante = st.number_input("Bombón Crocante (und/semana)", min_value=0, value=5, step=2, key="bombon_crocante")
                    bombon_vainilla_split = st.number_input("Bombón Vainilla Split (und/semana)", min_value=0, value=5, step=2, key="bombon_vainilla_split")
        
        # TAB 5: Otros productos
        with tab5:
            st.markdown("**Tortas**")
            st.caption("1 Bulto = 8 tortas")
            torta = st.number_input("Tortas (und/semana)", min_value=0, value=3, step=1, key="torta")
            
            st.divider()
            st.markdown("**Tentación**")
            st.caption("1 Bulto = 6 unidades")
            tentacion = st.number_input("Tentación (und/semana)", min_value=0, value=4, step=1, key="tentacion")
            
            st.divider()
            st.markdown("**Familiar**")
            st.caption("1 Bulto = 6 unidades")
            familiar = st.number_input("Familiar (und/semana)", min_value=0, value=5, step=1, key="familiar")
            
            # Botón de submit dentro del form
            st.divider()
            submit_demanda = st.form_submit_button(" Guardar Configuración de Tienda", type="primary", use_container_width=True)
        
        # Crear el diccionario de demanda base con todos los productos
        base_demand = {
            "storage_capacity_bultos": storage_capacity,
            # Granel y derivados
            "caja_granel": float(caja_granel),
            "cucurucho_simple": float(cucurucho_simple),
            "cucurucho_doble": float(cucurucho_doble),
            "cucurucho_triple": float(cucurucho_triple),
            "cucurucho_triple_bañado": float(cucurucho_triple_bañado),
            "pote_cuarto": float(pote_cuarto),
            "pote_medio": float(pote_medio),
            "pote_kilo": float(pote_kilo),
            "batido_capuccino": float(batido_capuccino),
            "batido_grido": float(batido_grido),
            # Palitos
            "palito_frutal": float(palito_frutal),
            "palito_cremoso": float(palito_cremoso),
            "palito_bombon": float(palito_bombon),
            # Alfajores
            "alfajor_crocantino": float(alfajor_crocantino),
            "alfajor_delicia": float(alfajor_delicia),
            "alfajor_casatta": float(alfajor_casatta),
            "alfajor_almendrado": float(alfajor_almendrado),
            # Bombones
            "bombon_escoces": float(bombon_escoces),
            "bombon_suizo": float(bombon_suizo),
            "bombon_crocante": float(bombon_crocante),
            "bombon_vainilla_split": float(bombon_vainilla_split),
            # Otros
            "torta": float(torta),
            "tentacion": float(tentacion),
            "familiar": float(familiar)
        }
        
        st.divider()
        
        # Validación y guardado
        if submit_demanda:
            # Validaciones
            errors = []
            if not name.strip():
                errors.append(" El nombre de la tienda es obligatorio")
            if not city.strip():
                errors.append(" La ciudad es obligatoria")
            if not country.strip():
                errors.append(" El país es obligatorio")
            if not (-90 <= lat <= 90):
                errors.append(" La latitud debe estar entre -90 y 90")
            if not (-180 <= lon <= 180):
                errors.append(" La longitud debe estar entre -180 y 180")
            
            if errors:
                for error in errors:
                    ui_components.render_error_message(error)
            else:
                try:
                    # Guardar tienda en base de datos
                    store_id = db_service.save_store(
                        name=name.strip(),
                        lat=lat,
                        lon=lon,
                        city=city.strip(),
                        country=country.strip(),
                        base_demand=base_demand
                    )
                    ui_components.render_success_message(
                        "Tienda configurada exitosamente"
                    )
                    
                    # Limpiar la ubicación detectada
                    if 'detected_location' in st.session_state:
                        del st.session_state.detected_location
                    
                    ui_components.render_info_message(
                        "Ahora puedes ir a 'Generar Sugerencia' para obtener recomendaciones inteligentes."
                    )
                    
                except Exception as e:
                    ui_components.render_error_message(f" Error al guardar la tienda: {e}")
    
    @staticmethod
    def view_stores_page():
        """Página para ver tiendas registradas"""
        st.header(" Tiendas Registradas")
        
        stores = db_service.get_stores()
        
        if not stores:
            ui_components.render_info_message(" No hay tiendas registradas aún.")
            st.markdown("""
            ###  ¡Parece que es tu primera vez aquí!
            
            Para comenzar a usar el sistema de sugerencias inteligente:
            
            1.  Ve a **"Configurar Tienda"** para registrar tu primera heladería
            2.  Luego podrás generar sugerencias personalizadas
            3.  Y ver el historial de todas tus sugerencias
            
            ¡Es muy fácil y rápido!
            """)
        else:
            st.markdown(f"** Total de tiendas:** {len(stores)}")
            
            # Mostrar tiendas en tarjetas
            for store in stores:
                ui_components.render_store_card(store)
    
    @staticmethod
    def generate_suggestion_page():
        """Página para generar sugerencias con 3 pasos"""
        st.header(" Generar Sugerencia Semanal")
        
        st.markdown("""
        ###  Proceso de Generación de Sugerencias
        Sigue estos 3 simples pasos para obtener tu sugerencia personalizada:
        """)
        
        stores = db_service.get_stores()
        
        if not stores:
            ui_components.render_info_message(" Registra primero una tienda en la sección 'Configurar Tienda'.")
            return
        
        # ==================== PASO 1: SELECCIÓN DE TIENDA Y CAPACIDAD ====================
        st.subheader(" Paso 1: Selecciona tu Tienda y Capacidad")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            store_options = {store['id']: f" {store['name']} - {store['city']}, {store['country']}" for store in stores}
            selected_store_id = st.selectbox(
                "Selecciona tu tienda:",
                options=list(store_options.keys()),
                format_func=lambda x: store_options[x],
                key="store_selector"
            )
        
        with col2:
            storage_capacity = st.number_input(
                " Capacidad de bultos:",
                min_value=1,
                max_value=500,
                value=50,
                step=5,
                help="¿Cuántos bultos puede almacenar esta tienda?",
                key="storage_capacity"
            )
        
        # Obtener tienda seleccionada
        selected_store_dict = next(s for s in stores if s['id'] == selected_store_id)
        
        # Mostrar información de la tienda seleccionada
        with st.container():
            st.markdown(f"""
            <div style='padding: 1rem; border: 2px solid #4CAF50; border-radius: 10px; background: #e8f5e9; margin: 1rem 0;'>
                <h4 style='color: #2e7d32; margin: 0 0 0.5rem 0;'> Tienda Seleccionada</h4>
                <p style='color: #1b5e20; margin: 0.25rem 0; font-size: 0.95rem;'><strong> Ubicación:</strong> {selected_store_dict['city']}, {selected_store_dict['country']}</p>
                <p style='color: #1b5e20; margin: 0.25rem 0; font-size: 0.95rem;'><strong> Capacidad:</strong> {storage_capacity} bultos</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # ==================== PASO 2: CARGA DE INVENTARIO ====================
        st.subheader("📦 Paso 2: Carga tu Inventario Actual")
        
        # Selector de modo de carga
        st.markdown("#### 🔌 Selecciona el Método de Carga")
        
        load_mode = st.radio(
            "¿Cómo deseas cargar el inventario?",
            options=["🔗 Conexión Directa al Inventario (Recomendado)", "📤 Subir Archivo Excel (Manual)"],
            index=0,
            key="inventory_load_mode",
            help="""
            - **Conexión Directa**: Lee automáticamente del módulo de Inventario (sin errores, tiempo real)
            - **Subir Excel**: Método manual tradicional (puede tener errores de formato)
            """
        )
        
        # Variables para almacenar ambos inventarios
        inventory_impulsivos = None
        inventory_granel = None
        current_inventory = None
        
        if load_mode.startswith("🔗"):
            # ==================== MODO: CONEXIÓN DIRECTA ====================
            st.markdown("---")
            st.markdown("### 🔌 Conexión Directa con Módulo de Inventario")
            
            try:
                from ..ui.inventory_connection import inventory_connection_ui
                
                # Determinar tienda_id desde el store seleccionado
                # Mapear el ID del store de sugerencias al ID de tienda del inventario
                # Por ahora usamos "T001" como default, pero idealmente mapearíamos correctamente
                tienda_inventory_id = "T001"  # TODO: Mapear correctamente con configuración
                
                # Mostrar estado de conexión
                is_connected = inventory_connection_ui.render_connection_status(tienda_inventory_id)
                
                if is_connected:
                    st.success("✅ **Inventario conectado exitosamente!**")
                    
                    # Botón para forzar sincronización
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        if st.button("🔄 Sincronizar Ahora", use_container_width=True):
                            with st.spinner("Sincronizando..."):
                                from ..services.inventory_sync_service import inventory_sync_service
                                success, message = inventory_sync_service.force_sync(tienda_inventory_id)
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                    
                    with col2:
                        if st.button("👁️ Ver Detalles", key="toggle_inventory_preview"):
                            st.session_state.show_inventory_preview = not st.session_state.get("show_inventory_preview", False)
                    
                    # Vista previa opcional
                    if st.session_state.get("show_inventory_preview", False):
                        inventory_connection_ui.render_inventory_preview(tienda_inventory_id)
                    
                    # Leer inventario sincronizado
                    from ..services.inventory_sync_service import inventory_sync_service
                    synced_inventory = inventory_sync_service.read_inventory_from_file(tienda_inventory_id)
                    
                    # Convertir inventario sincronizado al formato esperado por el motor de sugerencias
                    inventory_impulsivos = []
                    inventory_granel = []
                    
                    # Procesar impulsivos
                    for producto_key, datos in synced_inventory.get("impulsivo", {}).items():
                        inventory_impulsivos.append({
                            "Producto": datos.get("producto_original", producto_key),
                            "Bultos": datos["bultos"],
                            "Unidad": datos.get("unidad", 0),
                            "Estado Stock": datos["estado"]
                        })
                    
                    # Procesar granel
                    for producto_key, datos in synced_inventory.get("granel", {}).items():
                        # Para granel, el estado ya está calculado
                        inventory_granel.append({
                            "Producto": datos.get("producto_original", producto_key),
                            "Bultos": datos["bultos"],
                            "Estado Stock": datos["estado"],
                            "Kgs": datos.get("kgs_totales", 0)
                        })
                    
                    # Combinar ambos para mostrar resumen
                    if inventory_impulsivos or inventory_granel:
                        st.markdown("---")
                        st.markdown("### 📊 Resumen del Inventario Sincronizado")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            total_productos = len(inventory_impulsivos) + len(inventory_granel)
                            st.metric("📦 Total productos", total_productos)
                        with col2:
                            metadata = synced_inventory.get("metadata", {})
                            st.metric("📦 Total bultos", metadata.get("total_bultos", 0))
                        with col3:
                            st.metric("🍦 Impulsivos", len(inventory_impulsivos))
                        with col4:
                            st.metric("⚖️ Granel", len(inventory_granel))
                        
                        # Auto-seleccionar tipo según lo que hay
                        if inventory_impulsivos and inventory_granel:
                            current_inventory = inventory_impulsivos + inventory_granel
                            tipo_sugerencia = "Completa (Impulsivos + Granel)"
                        elif inventory_impulsivos:
                            current_inventory = inventory_impulsivos
                            tipo_sugerencia = "Solo Impulsivos"
                        elif inventory_granel:
                            current_inventory = inventory_granel
                            tipo_sugerencia = "Solo Granel"
                else:
                    st.warning("""
                    ⚠️ **No se pudo conectar al inventario**
                    
                    Por favor:
                    1. Verifica que el módulo de Inventario tenga datos cargados
                    2. O cambia a modo "Subir Archivo Excel"
                    """)
                    st.stop()
                    
            except ImportError as e:
                st.error(f"❌ Error importando servicio de sincronización: {e}")
                st.info("Cambia a modo 'Subir Archivo Excel' para continuar")
                st.stop()
        
        else:
            # ==================== MODO: UPLOAD MANUAL ====================
            st.markdown("---")
            st.markdown("""
            Carga dos archivos Excel separados para mejor organización:
            - **🍦 Productos Impulsivos**: Palitos, alfajores, bombones, tortas, etc.
            - **⚖️ Productos a Granel (Por Kilos)**: Helados en cajas de 7.8kg
            """)
            
            # Tabs para organizar las dos cargas
            tab1, tab2 = st.tabs(["🍦 Impulsivos", "⚖️ Por Kilos (Granel)"])
            
            # ========== TAB 1: PRODUCTOS IMPULSIVOS ==========
            with tab1:
                st.markdown("### 🍦 Productos Impulsivos")
                st.caption("Palitos, alfajores, bombones, tortas, tentación, familiar, etc.")
                
                # Ejemplo de formato
                with st.expander("📋 Ver ejemplo de formato"):
                    example_data = {
                        'Producto': ['Alfajor Almendrado', 'Palito Bombon', 'Tentacion Chocolate'],
                        'Bultos': [3, 0, 1],
                        'Unidad': [3, 4, 3],
                        'Estado Stock': ['STOCK OK', 'STOCK BAJO', 'STOCK BAJO']
                    }
                    if PANDAS_AVAILABLE:
                        import pandas as pd
                        st.dataframe(pd.DataFrame(example_data), use_container_width=True)
                    else:
                        st.write(example_data)
                
                # Upload de impulsivos
                uploaded_impulsivos = st.file_uploader(
                    "📤 Selecciona archivo de Productos Impulsivos:",
                    type=['xlsx', 'xls', 'csv'],
                    help="Sube un archivo Excel con productos impulsivos",
                    key="inventory_impulsivos_uploader"
                )
                
                if uploaded_impulsivos is not None:
                    inventory_impulsivos = _process_inventory_file(uploaded_impulsivos, "Impulsivos")
            
            # ========== TAB 2: PRODUCTOS A GRANEL ==========
            with tab2:
                st.markdown("### ⚖️ Productos a Granel (Por Kilos)")
                st.caption("Helados en cajas de 7.8kg: vainilla, chocolate, frutilla, etc.")
                
                # Ejemplo de formato
                with st.expander("📋 Ver ejemplo de formato GRANEL"):
                    st.info("**Formato especial para Granel:**\n- Cajas Cerradas: cada una pesa 7.8kg\n- Kgs Abiertas: peso de la caja abierta")
                    example_data_granel = {
                        'Estado': ['STOCK OK', 'MEDIO', 'SIN STOCK'],
                        'Producto': ['Chocolate con Almendra', 'Crema Americana', 'Dulce de Leche con Brownie'],
                        'Cajas Cerradas': [1, 1, 0],
                        'Cajas Abiertas': [1, 1, 0],
                        'Kgs Abiertas': [5.3, 6.2, 0],
                        'Total Kgs': [13.1, 14.0, 0]
                    }
                    if PANDAS_AVAILABLE:
                        import pandas as pd
                        st.dataframe(pd.DataFrame(example_data_granel), use_container_width=True)
                        st.caption("📌 **Total Kgs** = (Cajas Cerradas × 7.8kg) + Kgs Abiertas")
                    else:
                        st.write(example_data_granel)
                
                # Upload de granel
                uploaded_granel = st.file_uploader(
                    "📤 Selecciona archivo de Productos a Granel:",
                    type=['xlsx', 'xls', 'csv'],
                    help="Sube un archivo Excel con productos a granel (por kilos)",
                    key="inventory_granel_uploader"
                )
                
                if uploaded_granel is not None:
                    inventory_granel = _process_inventory_file(uploaded_granel, "Granel")
            
            # Combinar ambos inventarios para modo manual
            if inventory_impulsivos or inventory_granel:
                st.divider()
                st.markdown("### 📊 Resumen y Tipo de Sugerencia")
                
                # Mostrar resumen
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    total_productos = (len(inventory_impulsivos) if inventory_impulsivos else 0) + (len(inventory_granel) if inventory_granel else 0)
                    st.metric("📦 Total productos", total_productos)
                with col2:
                    if PANDAS_AVAILABLE:
                        import pandas as pd
                        total_items = []
                        if inventory_impulsivos:
                            total_items.extend(inventory_impulsivos)
                        if inventory_granel:
                            total_items.extend(inventory_granel)
                        df_total = pd.DataFrame(total_items)
                        total_bultos = df_total['Bultos'].sum()
                        st.metric("📦 Total bultos", f"{total_bultos:.0f}")
                with col3:
                    impulsivos_count = len(inventory_impulsivos) if inventory_impulsivos else 0
                    st.metric("🍦 Impulsivos", impulsivos_count)
                with col4:
                    granel_count = len(inventory_granel) if inventory_granel else 0
                    st.metric("⚖️ Granel", granel_count)
                
                # Selector de tipo de sugerencia
                st.markdown("#### 🎯 ¿Qué tipo de sugerencia deseas generar?")
                
                opciones_disponibles = []
                if inventory_impulsivos:
                    opciones_disponibles.append("🍦 Solo Impulsivos")
                if inventory_granel:
                    opciones_disponibles.append("⚖️ Solo Granel (Por Kilos)")
                if inventory_impulsivos and inventory_granel:
                    opciones_disponibles.append("📦 Ambos (Impulsivos + Granel)")
                
                tipo_seleccionado = st.radio(
                    "Selecciona el tipo:",
                    opciones_disponibles,
                    help="Elige qué productos incluir en la sugerencia",
                    horizontal=True,
                    key="tipo_sugerencia_radio"
                )
                
                # Preparar inventario según selección
                if tipo_seleccionado == "🍦 Solo Impulsivos":
                    current_inventory = inventory_impulsivos
                    tipo_sugerencia = "impulsivo"
                    st.info("📋 Se generarán sugerencias SOLO para productos impulsivos")
                elif tipo_seleccionado == "⚖️ Solo Granel (Por Kilos)":
                    current_inventory = inventory_granel
                    tipo_sugerencia = "granel"
                    st.info("📋 Se generarán sugerencias SOLO para productos a granel")
                else:
                    current_inventory = []
                    if inventory_impulsivos:
                        current_inventory.extend(inventory_impulsivos)
                    if inventory_granel:
                    current_inventory.extend(inventory_granel)
                tipo_sugerencia = "ambos"
                st.info("📋 Se generarán sugerencias para AMBOS tipos de productos")
        else:
            st.info("📋 Esperando que cargues al menos un archivo de inventario...")
        
        st.divider()
        
        # ==================== PASO 3: GENERAR SUGERENCIA ====================
        st.subheader(" Paso 3: Generar Sugerencia Inteligente")
        
        st.markdown("""
        La IA analizará:
        -  **Pronóstico meteorológico** de la próxima semana
        -  **Fechas festivas y feriados** 
        -  **Tu inventario actual**
        -  **Capacidad de almacenamiento**
        -  **Tendencias de demanda**
        """)
        
        # Selector de estrategia (opcional)
        with st.expander(" Opciones Avanzadas"):
            strategy = st.radio(
                "Estrategia de sugerencia:",
                ["conservadora", "balanceada", "agresiva"],
                index=1,
                help="Conservadora: minimiza riesgos | Balanceada: equilibrio | Agresiva: maximiza ganancias"
            )
            
            show_charts = st.checkbox(" Mostrar gráficos detallados", value=True)
        
        # Botón para generar (solo habilitado si hay inventario)
        can_generate = current_inventory is not None
        
        if not can_generate:
            st.warning(" Debes cargar tu inventario (Paso 2) antes de generar la sugerencia.")
        
        if st.button(
            " Generar Sugerencia Inteligente", 
            type="primary", 
            use_container_width=True,
            disabled=not can_generate
        ):
            with st.spinner(" Analizando clima, inventario y generando sugerencias..."):
                try:
                    # Convertir diccionario a objeto Store
                    location = LocationInfo(
                        lat=selected_store_dict['lat'],
                        lon=selected_store_dict['lon'],
                        city=selected_store_dict['city'],
                        country=selected_store_dict['country'],
                        accuracy="database"
                    )
                    
                    # Actualizar base_demand con capacidad de almacenamiento
                    base_demand = selected_store_dict.get('base_demand', {})
                    base_demand['storage_capacity_bultos'] = storage_capacity
                    
                    selected_store = Store(
                        id=selected_store_dict['id'],
                        name=selected_store_dict['name'],
                        location=location,
                        base_demand=base_demand
                    )
                    
                    # Obtener pronóstico meteorológico
                    forecast = weather_service.get_weekly_forecast(selected_store.location.lat, selected_store.location.lon)
                    
                    if not forecast:
                        ui_components.render_error_message(" No se pudo obtener el pronóstico meteorológico")
                        return
                    
                    # Extraer los datos del clima del diccionario
                    weather_data = forecast.get('daily_weather', [])
                    
                    if not weather_data:
                        ui_components.render_error_message(" No hay datos meteorológicos disponibles")
                        return
                    
                    # Generar sugerencia con inventario actual
                    suggestion = suggestion_engine.generate_weekly_suggestion(
                        selected_store, 
                        weather_data,  # Pasar la lista de WeatherData
                        strategy if 'strategy' in locals() else 'balanceada',
                        current_inventory=current_inventory  # Pasar inventario
                    )
                    
                    # Guardar inventario en session_state para usarlo en la visualización
                    st.session_state['last_inventory'] = current_inventory
                    
                    # Guardar en base de datos
                    suggestion_dict = {
                        'total_investment': suggestion.total_investment,
                        'expected_revenue': suggestion.expected_revenue,
                        'expected_roi': suggestion.expected_roi,
                        'risk_level': suggestion.risk_level,
                        'products': [p.__dict__ for p in suggestion.product_suggestions],
                        'storage_capacity': storage_capacity,
                        'inventory_items': len(current_inventory) if current_inventory else 0
                    }
                    
                    suggestion_id = db_service.save_suggestion(
                        selected_store.id,
                        suggestion.week_start,
                        strategy if 'strategy' in locals() else 'balanceada',
                        suggestion_dict,
                        suggestion.explanation
                    )
                    
                    # Mostrar resultados
                    st.success(" ¡Sugerencia generada exitosamente!")
                    st.divider()
                    Pages._display_suggestion_results(suggestion, forecast, show_charts, current_inventory)
                    
                    ui_components.render_success_message(
                        " Sugerencia guardada en el historial"
                    )
                    
                except Exception as e:
                    ui_components.render_error_message(f" Error generando sugerencia: {e}")
                    import traceback
                    st.error(traceback.format_exc())
    
    @staticmethod
    def history_analytics_page():
        """Página de historial y análisis"""
        st.header(" Historial & Analytics")
        
        # Tabs para diferentes vistas
        tab1, tab2, tab3 = st.tabs([" Historial", " Analytics", " Tendencias"])
        
        with tab1:
            Pages._display_suggestions_history()
        
        with tab2:
            Pages._display_analytics()
        
        with tab3:
            Pages._display_trends()
    
    @staticmethod
    def _display_suggestion_results(suggestion, forecast, show_charts=True, current_inventory=None):
        """Muestra los resultados de una sugerencia"""
        # Resumen principal con inventario
        ui_components.render_suggestion_summary(suggestion, current_inventory)
        
        st.divider()
        
        # Productos sugeridos
        st.subheader(" Productos Sugeridos")
        
        # Debug: verificar cantidad de productos
        if hasattr(suggestion, 'product_suggestions'):
            st.caption(f"Total de productos sugeridos: {len(suggestion.product_suggestions)}")
            if suggestion.product_suggestions:
                ui_components.render_products_table(suggestion.product_suggestions)
            else:
                st.warning("No se generaron productos en la sugerencia. Verifica la configuración de demanda base de la tienda.")
        else:
            st.error("La sugerencia no tiene productos.")
        
        st.divider()
        
        # Explicación
        st.subheader(" Explicación de la IA")
        st.markdown(suggestion.explanation)
        
        # Gráficos si están habilitados
        if show_charts:
            st.divider()
            st.subheader(" Análisis Meteorológico")
            
            col1, col2 = st.columns(2)
            with col1:
                ui_components.render_weather_chart(forecast)
            with col2:
                ui_components.render_demand_factors_chart(forecast)
    
    @staticmethod
    def _display_suggestions_history():
        """Muestra el historial de sugerencias"""
        suggestions = db_service.get_suggestions()
        
        if not suggestions:
            ui_components.render_info_message("No hay sugerencias guardadas aún.")
            return
        
        st.markdown(f"** Total de sugerencias:** {len(suggestions)}")
        
        for suggestion in suggestions:
            with st.expander(f" {suggestion['store_name']} - {suggestion['week_start']} - {suggestion['strategy'].title()}"):
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(" Inversión", f"₱{suggestion['total_investment']:,.0f}")
                with col2:
                    st.metric(" ROI", f"{suggestion.get('expected_roi', 0) * 100:.1f}%")
                with col3:
                    st.metric(" Riesgo", suggestion['risk_level'].title())
                
                st.markdown("** Explicación:**")
                st.write(suggestion['explanation'])
                
                st.markdown("** Generada:** " + suggestion['created_at'])
    
    @staticmethod
    def _display_analytics():
        """Muestra analytics generales"""
        suggestions = db_service.get_suggestions()
        stores = db_service.get_stores()
        
        if not suggestions:
            ui_components.render_info_message("No hay datos suficientes para analytics.")
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(" Tiendas Totales", len(stores))
        
        with col2:
            st.metric(" Sugerencias Generadas", len(suggestions))
        
        with col3:
            avg_roi = sum(s.get('expected_roi', 0) * 100 for s in suggestions) / len(suggestions)
            st.metric(" ROI Promedio", f"{avg_roi:.1f}%")
        
        with col4:
            total_investment = sum(s['total_investment'] for s in suggestions)
            st.metric(" Inversión Total", f"₱{total_investment:,.0f}")
    
    @staticmethod
    def _display_trends():
        """Muestra tendencias y análisis avanzados"""
        ui_components.render_info_message(" Análisis de tendencias próximamente disponible")


# Instancia global de páginas
pages = Pages()
