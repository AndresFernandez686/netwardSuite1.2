import streamlit as st
from datetime import date, datetime, timedelta
import pandas as pd

# Configuración para mejorar rendimiento
if 'admin_page_config' not in st.session_state:
    st.session_state.admin_page_config = True

# Importar utilidades con manejo de errores
try:
    from .utils import df_to_csv_bytes
except ImportError:
    try:
        from utils import df_to_csv_bytes
    except ImportError:
        def df_to_csv_bytes(df):
            return df.to_csv(index=False).encode('utf-8')

# Importar productos base para mostrar productos no cargados
try:
    from .ui_empleado_fixed import PRODUCTOS_BASE
except ImportError:
    try:
        from ui_empleado_fixed import PRODUCTOS_BASE
    except ImportError:
        # Estructura base
        PRODUCTOS_BASE = {
            "Impulsivo": {},
            "Por Kilos": {},
            "Extras": {}
        }

# Importar sistema de alertas de stock
try:
    from .stock_alerts import stock_alert_system
except ImportError:
    try:
        from stock_alerts import stock_alert_system
    except ImportError:
        stock_alert_system = None

# Importar sistema de mermas
try:
    from .mermas_manager import mermas_manager
except ImportError:
    try:
        from mermas_manager import mermas_manager
    except ImportError:
        mermas_manager = None

@st.cache_data(ttl=300)  # Cache por 5 minutos
def obtener_ultimo_modo(producto: str, categoria: str, tienda_id: str = "T001") -> str:
    """Obtiene el último UME (Unidad, Caja, Tira) usado para un producto del historial"""
    try:
        try:
            from .persistencia import cargar_historial
        except ImportError:
            from persistencia import cargar_historial
        historial = cargar_historial(tienda_id)
        
        # Buscar el último registro de este producto en esta categoría
        for registro in reversed(historial):
            if registro.get("producto") == producto and registro.get("categoria") == categoria:
                modo = registro.get("modo", "N/A")
                # El modo guarda el UME (Unidad, Caja, Tira) o "Modificar"
                if modo in ["Unidad", "Caja", "Tira"]:
                    return modo
        return "N/A"
    except Exception as e:
        return "N/A"

def admin_inventario_ui(inventario, tienda_id="T001"):
    """Interfaz de administración de inventario con validación mejorada"""
    
    # Validación de inventario mejorada
    categorias_validas = ["Impulsivo", "Por Kilos", "Extras"]
    
    # Verificar si el inventario es válido
    if not isinstance(inventario, dict):
        st.error("Error al cargar inventario: datos no válidos")
        return
    
    # Filtrar solo categorías válidas del inventario
    inventario_filtrado = {}
    for categoria in categorias_validas:
        if categoria in inventario and isinstance(inventario[categoria], dict):
            inventario_filtrado[categoria] = inventario[categoria]
        else:
            inventario_filtrado[categoria] = {}
    
    # Usar el inventario filtrado para el resto de la función
    inventario = inventario_filtrado
    
    # Muestra tablas para cada categoría y botones de descarga
    st.header("🏪 Gestión de Inventario")
    
    # Las estadísticas ya se muestran en cada categoría individualmente
    
    # Controles de visualización en columnas
    col_filter, col_search = st.columns([1, 1])
    
    with col_filter:
        # Añadir filtro por categoría
        categorias = ["Todas"] + list(inventario.keys())
        categoria_seleccionada = st.selectbox("Filtrar por categoría", categorias)
    
    with col_search:
        # Campo de búsqueda
        busqueda = st.text_input("Buscar producto", "", placeholder="Escribe el nombre del producto...")
    
    # Determinar categorías a mostrar
    if categoria_seleccionada == "Todas":
        categorias_a_mostrar = inventario.keys()
    else:
        categorias_a_mostrar = [categoria_seleccionada]
    
    # Mostrar inventario filtrado
    for categoria in categorias_a_mostrar:
        # Validar que la categoría existe y es un diccionario
        if categoria not in inventario or not isinstance(inventario[categoria], dict):
            st.warning(f" Categoría '{categoria}' no válida o vacía")
            continue
            
        # Header de categoría simple
        productos = inventario[categoria]
        
        # Para mostrar productos no cargados, incluir también productos base que no están en inventario
        productos_completos = productos.copy()
        if categoria in PRODUCTOS_BASE:
            for producto_base in PRODUCTOS_BASE[categoria]:
                if producto_base not in productos_completos:
                    productos_completos[producto_base] = 0  # Agregar como no cargado
        
        # NUEVO: Mostrar header y filtro de estado para todas las categorías con estructura moderna
        if categoria in ["Por Kilos", "Extras", "Impulsivo"]:
            st.subheader(f"Categoría: {categoria}")
            
            # Crear columnas para filtros
            col_estado, col_info = st.columns([1, 2])
            
            with col_estado:
                estado_filtro = st.selectbox(
                    f"Estado en {categoria}",
                    ["Todos", "Cargado", "No cargado"],
                    key=f"filtro_estado_{categoria}_{tienda_id}"
                )
            
            with col_info:
                # Contar productos por estado
                productos_cargados = 0
                productos_no_cargados = 0
                
                for producto, datos in productos_completos.items():
                    if categoria == "Por Kilos":
                        if isinstance(datos, dict) and all(key in datos for key in ["cajas_cerradas", "cajas_abiertas", "kgs_cajas_abiertas"]):
                            total_kgs = (datos.get("cajas_cerradas", 0) * 7.8) + datos.get("kgs_cajas_abiertas", 0.0)
                            if total_kgs > 0:
                                productos_cargados += 1
                            else:
                                productos_no_cargados += 1
                        elif isinstance(datos, (int, float)) and datos > 0:
                            productos_cargados += 1
                        else:
                            productos_no_cargados += 1
                    else:  # Extras e Impulsivo
                        if isinstance(datos, dict) and all(key in datos for key in ["bultos", "unidad"]):
                            total = datos.get("bultos", 0) + datos.get("unidad", 0)
                            if total > 0:
                                productos_cargados += 1
                            else:
                                productos_no_cargados += 1
                        elif isinstance(datos, (int, float)) and datos > 0:
                            productos_cargados += 1
                        else:
                            productos_no_cargados += 1
                
                st.info(f"📈 Mostrando {len(productos_completos)} productos: 🟢 {productos_cargados} cargados, 🔴 {productos_no_cargados} sin cargar")
            
            # Aplicar filtro de estado
            if estado_filtro == "Cargado":
                productos_filtrados_estado = {}
                for producto, datos in productos_completos.items():
                    if categoria == "Por Kilos":
                        if isinstance(datos, dict) and all(key in datos for key in ["cajas_cerradas", "cajas_abiertas", "kgs_cajas_abiertas"]):
                            total_kgs = (datos.get("cajas_cerradas", 0) * 7.8) + datos.get("kgs_cajas_abiertas", 0.0)
                            if total_kgs > 0:
                                productos_filtrados_estado[producto] = datos
                        elif isinstance(datos, (int, float)) and datos > 0:
                            productos_filtrados_estado[producto] = datos
                    else:  # Extras e Impulsivo
                        if isinstance(datos, dict) and all(key in datos for key in ["bultos", "unidad"]):
                            total = datos.get("bultos", 0) + datos.get("unidad", 0)
                            if total > 0:
                                productos_filtrados_estado[producto] = datos
                        elif isinstance(datos, (int, float)) and datos > 0:
                            productos_filtrados_estado[producto] = datos
                productos_completos = productos_filtrados_estado
            elif estado_filtro == "No cargado":
                productos_filtrados_estado = {}
                for producto, datos in productos_completos.items():
                    if categoria == "Por Kilos":
                        if isinstance(datos, dict) and all(key in datos for key in ["cajas_cerradas", "cajas_abiertas", "kgs_cajas_abiertas"]):
                            total_kgs = (datos.get("cajas_cerradas", 0) * 7.8) + datos.get("kgs_cajas_abiertas", 0.0)
                            if total_kgs == 0:
                                productos_filtrados_estado[producto] = datos
                        elif not isinstance(datos, dict) and (not datos or datos == 0):
                            productos_filtrados_estado[producto] = datos
                    else:  # Extras e Impulsivo
                        if isinstance(datos, dict) and all(key in datos for key in ["bultos", "unidad"]):
                            total = datos.get("bultos", 0) + datos.get("unidad", 0)
                            if total == 0:
                                productos_filtrados_estado[producto] = datos
                        elif not isinstance(datos, dict) and (not datos or datos == 0):
                            productos_filtrados_estado[producto] = datos
                productos_completos = productos_filtrados_estado
        else:
            st.subheader(f"Categoría: {categoria}")
        
        # Filtrar por búsqueda
        productos_filtrados = {}
        if busqueda:
            busqueda_lower = busqueda.lower()
            for producto, cantidad in productos_completos.items():
                if busqueda_lower in producto.lower():
                    productos_filtrados[producto] = cantidad
        else:
            productos_filtrados = productos_completos
        
        # Si no hay resultados con el filtro actual
        if not productos_filtrados:
            if busqueda:
                st.warning(f" No se encontraron productos en '{categoria}' con el término '{busqueda}'")
            else:
                st.info(f" No hay productos para mostrar en '{categoria}' con el filtro de estado seleccionado")
            continue
        
        # Usar orden alfabético simple para todas las categorías
        productos_ordenados = sorted(productos_filtrados.keys())
        
        # Limitar a los últimos 3 resultados cuando hay búsqueda
        if busqueda and len(productos_ordenados) > 3:
            productos_ordenados = productos_ordenados[-3:]
        
        # Info ya se muestra en el filtro de estado, no duplicar
        
        # Crear DataFrame según la categoría y agregar indicadores de stock
        if categoria == "Por Kilos":
            productos_csv = []
            # Crear tabla específica para productos por kilos con nueva estructura de 4 columnas
            for producto in productos_ordenados:
                datos_producto = productos_filtrados[producto]
                
                # Verificar si es la nueva estructura de 4 columnas
                if isinstance(datos_producto, dict) and all(key in datos_producto for key in ["cajas_cerradas", "cajas_abiertas", "kgs_cajas_abiertas"]):
                    # Nueva estructura de 4 columnas
                    cajas_cerradas = datos_producto.get("cajas_cerradas", 0)
                    cajas_abiertas = datos_producto.get("cajas_abiertas", 0)
                    kgs_abiertas = datos_producto.get("kgs_cajas_abiertas", 0.0)
                    
                    # Calcular totales
                    total_kgs = (cajas_cerradas * 7.8) + kgs_abiertas
                    total_cajas = cajas_cerradas + cajas_abiertas
                    
                    # Obtener indicador de alerta
                    if stock_alert_system:
                        emoji, status, desc = stock_alert_system.get_stock_status(producto, total_kgs)
                        estado_alerta = f"{emoji} {desc}"
                        color_css = stock_alert_system.get_stock_color_css(status)
                    else:
                        emoji, status, desc, estado_alerta = "📦", "unknown", "N/A", "📦 N/A"
                        color_css = "background: #f8f9fa; color: #333;"
                    
                    # Determinar estado
                    estado = "🟢 Cargado" if total_kgs > 0 else "🔴 No cargado"
                    
                    # Obtener último modo (UME) usado
                    modo = obtener_ultimo_modo(producto, categoria, tienda_id)
                    
                    productos_csv.append({
                        "🚨 Estado": estado_alerta,
                        "📦 Producto": producto, 
                        "🔒 Cajas Cerradas": cajas_cerradas,
                        "📂 Cajas Abiertas": cajas_abiertas,
                        "⚖️ Kgs Abiertas": f"{kgs_abiertas:.3f}".replace(".", ",") + " kg",
                        "📊 Total Kgs": f"{total_kgs:.3f}".replace(".", ",") + " kg",
                        "📅 Tipo": "Estructura Nueva",
                        "📌 Modo": modo,
                        "✅ Estado": estado
                    })
                    
                # Mantener compatibilidad con estructura antigua
                elif isinstance(datos_producto, list):
                    # Estructura antigua con listas
                    if all(isinstance(x, (int, float)) for x in datos_producto):
                        # Formato quincenal con kilos
                        total_kilos = sum(datos_producto)
                        kilos_detalle = ", ".join([f'{k:.3f}'.replace(".", ",") + " kg" for k in datos_producto])
                        estado = "🟢 Cargado" if total_kilos > 0 else "🔴 No cargado"
                        
                        if stock_alert_system:
                            emoji, status, desc = stock_alert_system.get_stock_status(producto, total_kilos)
                            estado_alerta = f"{emoji} {desc}"
                        else:
                            estado_alerta = "📦 N/A"
                        
                        modo = obtener_ultimo_modo(producto, categoria, tienda_id)
                        
                        productos_csv.append({
                            "🚨 Estado": estado_alerta,
                            "📦 Producto": producto, 
                            "🔒 Cajas Cerradas": "N/A",
                            "📂 Cajas Abiertas": "N/A", 
                            "⚖️ Kgs Abiertas": "N/A",
                            "📊 Total Kgs": f"{total_kilos:.3f}".replace(".", ",") + " kg",
                            "📅 Tipo": "Estructura Antigua",
                            "📌 Modo": modo,
                            "✅ Estado": estado
                        })
                    else:
                        # Formato diario/semanal con estados
                        estado_baldes = ", ".join([str(b) for b in datos_producto])
                        llenos = sum(1 for b in datos_producto if str(b) != "Vacío")
                        estado = "🟢 Cargado" if llenos > 0 else "🔴 No cargado"
                        
                        if stock_alert_system:
                            emoji, status, desc = stock_alert_system.get_stock_status(producto, llenos)
                            estado_alerta = f"{emoji} {desc}"
                        else:
                            estado_alerta = "📦 N/A"
                        
                        modo = obtener_ultimo_modo(producto, categoria, tienda_id)
                        
                        productos_csv.append({
                            "🚨 Estado": estado_alerta,
                            "📦 Producto": producto, 
                            "🔒 Cajas Cerradas": "N/A",
                            "📂 Cajas Abiertas": "N/A",
                            "⚖️ Kgs Abiertas": estado_baldes,
                            "📊 Total Kgs": f"{llenos} baldes",
                            "📅 Tipo": "Estados Antiguos",
                            "📌 Modo": modo,
                            "✅ Estado": estado
                        })
                        
                else:
                    # Estructura muy antigua (solo número)
                    cantidad = datos_producto if isinstance(datos_producto, (int, float)) else 0
                    estado = "🟢 Cargado" if cantidad > 0 else "🔴 No cargado"
                    
                    if stock_alert_system:
                        emoji, status, desc = stock_alert_system.get_stock_status(producto, cantidad)
                        estado_alerta = f"{emoji} {desc}"
                    else:
                        estado_alerta = "📦 N/A"
                    
                    modo = obtener_ultimo_modo(producto, categoria, tienda_id)
                    
                    productos_csv.append({
                        "🚨 Estado": estado_alerta,
                        "📦 Producto": producto, 
                        "🔒 Cajas Cerradas": "N/A",
                        "📂 Cajas Abiertas": "N/A",
                        "⚖️ Kgs Abiertas": "N/A",
                        "📊 Total Kgs": f"{cantidad}kg",
                        "📅 Tipo": "Estructura Muy Antigua",
                        "📌 Modo": modo,
                        "✅ Estado": estado
                    })
        else:
            # Para otras categorías (Impulsivo, Extras) - NUEVA ESTRUCTURA BULTOS/UNIDAD
            productos_csv = []
            for producto in productos_ordenados:
                if producto not in productos_filtrados:
                    continue
                    
                cantidad_data = productos_filtrados[producto]
                
                # Manejar nueva estructura bultos/unidad para Impulsivo y Extras
                if isinstance(cantidad_data, dict) and "bultos" in cantidad_data and "unidad" in cantidad_data:
                    # Nueva estructura: {"bultos": X, "unidad": Y}
                    bultos = cantidad_data.get("bultos", 0)
                    unidad = cantidad_data.get("unidad", 0)
                    cantidad_total = bultos + unidad  # Total para alertas
                    
                    # Obtener estado de alerta del producto
                    if stock_alert_system:
                        emoji, status, desc = stock_alert_system.get_stock_status(producto, cantidad_total)
                        estado_alerta = f"{emoji} {desc}"
                    else:
                        emoji = "📦"
                        estado_alerta = "📦 N/A"
                    
                    # Obtener último modo (UME) usado
                    modo = obtener_ultimo_modo(producto, categoria, tienda_id)
                    
                    estado = "🟢 Cargado" if cantidad_total > 0 else "🔴 No cargado"
                    productos_csv.append({
                        "📦 Producto": producto,
                        "📦 Bultos": bultos,
                        "🔢 Unidad": unidad,
                        "📌 Modo": modo,
                        "🚨 Estado Stock": estado_alerta,
                        "✅ Estado": estado
                    })
                elif isinstance(cantidad_data, dict):
                    # Estructura antigua con "stock" (compatibilidad)
                    cantidad = cantidad_data.get("stock", 0)
                    
                    # Obtener estado de alerta del producto
                    if stock_alert_system:
                        emoji, status, desc = stock_alert_system.get_stock_status(producto, cantidad)
                        estado_alerta = f"{emoji} {desc}"
                    else:
                        emoji = "📦"
                        estado_alerta = "📦 N/A"
                    
                    # Obtener último modo (UME) usado
                    modo = obtener_ultimo_modo(producto, categoria, tienda_id)
                    
                    estado = "🟢 Cargado" if cantidad > 0 else "🔴 No cargado"
                    productos_csv.append({
                        "📦 Producto": producto,
                        "📊 Cantidad": cantidad,
                        "📌 Modo": modo,
                        "🚨 Estado Stock": estado_alerta,
                        "✅ Estado": estado
                    })
                else:
                    # Estructura simple (número directo) - migrar a nueva estructura
                    cantidad = cantidad_data if isinstance(cantidad_data, (int, float)) else 0
                    
                    # Obtener estado de alerta del producto
                    if stock_alert_system:
                        emoji, status, desc = stock_alert_system.get_stock_status(producto, cantidad)
                        estado_alerta = f"{emoji} {desc}"
                    else:
                        emoji = "📦"
                        estado_alerta = "📦 N/A"
                    
                    # Obtener último modo (UME) usado
                    modo = obtener_ultimo_modo(producto, categoria, tienda_id)
                    
                    estado = "🟢 Cargado" if cantidad > 0 else "🔴 No cargado"
                    productos_csv.append({
                        "📦 Producto": producto,
                        "📦 Bultos": 0,  # Migrar a nueva estructura
                        "🔢 Unidad": cantidad,  # Poner cantidad antigua en unidad
                        "📌 Modo": modo,
                        "🚨 Estado Stock": estado_alerta,
                        "✅ Estado": estado,
                        "⚠️ Migración": "Datos migrados automáticamente"
                    })
        
        # Crear DataFrame
        df = pd.DataFrame(productos_csv)
        
        # El filtro de estado ya se aplicó arriba, no duplicar filtros aquí
        
        # Mostrar tabla si hay datos
        if not df.empty:
            # Usar styled dataframe para mejor presentación
            st.markdown("### 📊 Tabla de Productos")
            st.dataframe(df, use_container_width=True, height=400)
            
            # Métricas de resumen - Proporción optimizada 25-25-25-25
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                cargados = len(df[df["✅ Estado"] == "🟢 Cargado"]) if "✅ Estado" in df.columns else 0
                st.metric("✅ Cargados", cargados)
            with col2:
                no_cargados = len(df[df["✅ Estado"] == "🔴 No cargado"]) if "✅ Estado" in df.columns else 0
                st.metric("❌ Sin cargar", no_cargados)
            with col3:
                total_categoria = len(df)
                st.metric("📦 Total", total_categoria)
            with col4:
                porcentaje = round((cargados / total_categoria * 100), 1) if total_categoria > 0 else 0
                st.metric("📈 % Cargado", f"{porcentaje}%")
            
            # Botón de descarga (Excel)
            try:
                try:
                    from .utils import df_to_excel_bytes
                except ImportError:
                    from utils import df_to_excel_bytes
                excel_bytes = df_to_excel_bytes(df)
                st.download_button(
                    label=f"📥 Descargar Excel de {categoria} (Formato Plantilla Tienda)",
                    data=excel_bytes,
                    file_name=f"inventario_{categoria.lower().replace(' ', '_')}_{tienda_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    help=f"Excel con formato plantilla de tienda - Bultos/Unidad separados para {categoria}"
                )
            except Exception as e:
                st.warning(f"Error preparando descarga: {e}")
            
            # Botón especial para generar reporte en formato de plantilla de tienda
            if categoria in ["Impulsivo", "Extras", "Por Kilos"] and not df.empty:
                if st.button(f"📋 Generar Reporte Formato Plantilla Tienda - {categoria}", use_container_width=True, type="secondary"):
                    generar_reporte_plantilla_tienda(df, categoria, tienda_id)
        else:
            st.warning(f"❌ No hay productos en estado '{estado_seleccionado}' para la categoría '{categoria}'")

def admin_historial_ui(historial_json):
    st.header("Historial de cargas (por empleado / mes)")
    import pandas as pd

    # Validación robusta para evitar error DataFrame constructor not properly called!
    if not historial_json or not isinstance(historial_json, list) or not all(isinstance(e, dict) for e in historial_json):
        st.info("Aún no hay registros en el historial.")
        return

    historial = pd.DataFrame(historial_json)
    # Normaliza nombres columna
    if "fecha" in historial.columns:
        historial["Fecha"] = pd.to_datetime(historial["fecha"])
    if "usuario" in historial.columns:
        historial["Usuario"] = historial["usuario"]
    if "producto" in historial.columns:
        historial["Producto"] = historial["producto"]
    
    # Asegurar que tenemos una columna para agrupar por fecha
    historial["Fecha_solo"] = historial["Fecha"].dt.date

    # Filtros principales - Proporción optimizada 40-60
    col1, col2 = st.columns([4, 6])
    with col1:
        empleados = ["Todos"] + sorted(historial["Usuario"].dropna().unique().tolist())
        empleado_sel = st.selectbox("Empleado", empleados)
    with col2:
        # Filtro por tipo de inventario
        tipos_inventario = ["Todos"] + ["Diario", "Semanal", "Quincenal"]
        if "tipo_inventario" in historial.columns:
            tipos_disponibles = historial["tipo_inventario"].dropna().unique().tolist()
            tipos_inventario = ["Todos"] + sorted(set(["Diario", "Semanal", "Quincenal"] + tipos_disponibles))
        tipo_inventario_sel = st.selectbox("Tipo de inventario", tipos_inventario)
    
    # Selector de fecha con calendario - Proporción optimizada 50-50
    col3, col4 = st.columns([1, 1])
    with col3:
        fecha_inicio = st.date_input("Fecha de inicio", value=date.today().replace(day=1))
    with col4:
        # Último día del mes actual
        import calendar
        ultimo_dia = calendar.monthrange(date.today().year, date.today().month)[1]
        fecha_fin = st.date_input("Fecha de fin", value=date.today().replace(day=ultimo_dia))

    filtro = historial[(historial["Fecha"].dt.date >= fecha_inicio) & (historial["Fecha"].dt.date <= fecha_fin)]
    if empleado_sel != "Todos":
        filtro = filtro[filtro["Usuario"] == empleado_sel]
    if tipo_inventario_sel != "Todos":
        # Si no existe la columna tipo_inventario, asumimos que son registros antiguos (Diario)
        if "tipo_inventario" in filtro.columns:
            filtro = filtro[filtro["tipo_inventario"] == tipo_inventario_sel]
        elif tipo_inventario_sel == "Diario":
            # Mantener todos los registros si buscamos "Diario" y no hay columna tipo_inventario
            pass
        else:
            # Si buscamos Semanal/Quincenal pero no hay columna, no hay resultados
            filtro = filtro.iloc[0:0]  # DataFrame vacío

    if not filtro.empty:
        # Eliminar duplicados, manteniendo solo la última entrada de cada producto por día
        if "Producto" in filtro.columns and "Fecha_solo" in filtro.columns:
            # Ordenamos por fecha (más reciente al final) antes de eliminar duplicados
            filtro = filtro.sort_values("Fecha")
            # Mantenemos solo la última entrada de cada producto por día
            filtro = filtro.drop_duplicates(subset=["Producto", "Fecha_solo", "Usuario"], keep="last")
        
        # Procesar la columna cantidad para mostrar mejor información
        def formatear_cantidad(row):
            cantidad = row.get("cantidad", "")
            categoria = row.get("categoria", "")
            tipo_inventario = row.get("tipo_inventario", "Diario")
            
            if categoria == "Por Kilos" and isinstance(cantidad, dict):
                # Nueva estructura de 4 columnas
                if all(key in cantidad for key in ["cajas_cerradas", "cajas_abiertas", "kgs_cajas_abiertas"]):
                    cajas_cerradas = cantidad.get("cajas_cerradas", 0)
                    cajas_abiertas = cantidad.get("cajas_abiertas", 0)
                    kgs_abiertas = cantidad.get("kgs_cajas_abiertas", 0.0)
                    total_kgs = (cajas_cerradas * 7.8) + kgs_abiertas
                    kgs_fmt = f"{kgs_abiertas:.3f}".replace(".", ",")
                    total_fmt = f"{total_kgs:.3f}".replace(".", ",")
                    return f"🔒{cajas_cerradas} cerradas, 📂{cajas_abiertas} abiertas, ⚖️{kgs_fmt} kg → Total: {total_fmt} kg"
                # Estructuras antiguas
                elif cantidad.get("tipo") == "Quincenal" and "total_kilos" in cantidad:
                    total = cantidad.get("total_kilos", 0)
                    kilos_detalle = cantidad.get("kilos_por_balde", [])
                    detalle = ', '.join([f'{k:.3f}'.replace(".", ",") + " kg" for k in kilos_detalle])
                    total_fmt = f"{total:.3f}".replace(".", ",")
                    return f"Total: {total_fmt} kg ({detalle})"
                elif "estados" in cantidad:
                    estados = cantidad.get("estados", [])
                    return f"{', '.join(estados)}"
            elif isinstance(cantidad, list):
                if all(isinstance(x, (int, float)) for x in cantidad):
                    # Lista de kilos
                    total = sum(cantidad)
                    detalle = ', '.join([f'{k:.3f}'.replace(".", ",") + " kg" for k in cantidad])
                    total_fmt = f"{total:.3f}".replace(".", ",")
                    return f"Total: {total_fmt} kg ({detalle})"
                else:
                    # Lista de estados
                    return f"{', '.join([str(x) for x in cantidad])}"
            else:
                return str(cantidad)
        
        # Agregar columnas formateadas para mejor visualización
        filtro_mostrar = filtro.copy()
        filtro_mostrar["Cantidad_Formateada"] = filtro.apply(formatear_cantidad, axis=1)
        filtro_mostrar["Tipo_Inventario"] = filtro_mostrar["tipo_inventario"].fillna("Diario")
        
        # Reordenar columnas para mejor visualización
        columnas_mostrar = ["Fecha", "Usuario", "Producto", "categoria", "Cantidad_Formateada", "Tipo_Inventario", "modo"]
        columnas_existentes = [col for col in columnas_mostrar if col in filtro_mostrar.columns]
        
        # Mostrar la tabla ordenada por fecha
        st.dataframe(filtro_mostrar[columnas_existentes].sort_values("Fecha"))
        
        # Cambiado a Excel
        try:
            from .utils import df_to_excel_bytes
        except ImportError:
            from utils import df_to_excel_bytes
        excel_bytes = df_to_excel_bytes(filtro)
        # Nombre de archivo más descriptivo
        tipo_archivo = tipo_inventario_sel if tipo_inventario_sel != "Todos" else "todos_tipos"
        nombre_archivo = f"historial_{empleado_sel}_{tipo_archivo}_{fecha_inicio.strftime('%Y%m%d')}_{fecha_fin.strftime('%Y%m%d')}.xlsx".replace(" ", "_")
        
        st.download_button(
            label="Descargar historial filtrado (Excel)",
            data=excel_bytes,
            file_name=nombre_archivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No hay registros con ese filtro.")

def admin_delivery_ui(cargar_catalogo_delivery, guardar_catalogo_delivery, cargar_ventas_delivery):
    st.header("Gestión de Delivery (catálogo y ventas)")
    st.subheader("Catálogo de productos de delivery")
    catalogo = cargar_catalogo_delivery()

    with st.expander("Agregar nuevo producto de delivery"):
        nombre = st.text_input("Nombre del producto (ej: Promo 2x1 Chocolate)")
        es_promocion = st.checkbox("¿Es promoción?", value=False)
        activo = st.checkbox("Activo", value=True)
        if st.button("Guardar producto"):
            if not nombre.strip():
                st.error("El nombre no puede estar vacío.")
            else:
                if any(p["nombre"].lower() == nombre.strip().lower() for p in catalogo):
                    st.warning("Ya existe un producto con ese nombre.")
                else:
                    catalogo.append({
                        "nombre": nombre.strip(),
                        "es_promocion": bool(es_promocion),
                        "activo": bool(activo)
                    })
                    guardar_catalogo_delivery(catalogo)
                    st.success("Producto agregado al catálogo.")

    if catalogo:
        st.write("Productos actuales:")
        df_cat = pd.DataFrame(catalogo)
        st.dataframe(df_cat)

        st.subheader("Editar / Eliminar")
        nombres = [c["nombre"] for c in catalogo]
        sel = st.selectbox("Selecciona un producto", nombres)
        idx = nombres.index(sel)
        # Distribución de columnas optimizada 20-20-30-30
        col1, col2, col3, col4 = st.columns([2, 2, 3, 3])
        with col1:
            nuevo_activo = st.checkbox("Activo", value=catalogo[idx].get("activo", True), key=f"edit_activo_{idx}")
        with col2:
            nuevo_promo = st.checkbox("Promoción", value=catalogo[idx].get("es_promocion", False), key=f"edit_promo_{idx}")
        with col3:
            if st.button("Guardar cambios", key=f"save_{idx}"):
                catalogo[idx]["activo"] = nuevo_activo
                catalogo[idx]["es_promocion"] = nuevo_promo
                guardar_catalogo_delivery(catalogo)
                st.success("Cambios guardados.")
        with col4:
            if st.button("Eliminar producto", key=f"delete_{idx}"):
                catalogo.pop(idx)
                guardar_catalogo_delivery(catalogo)
                st.success("Producto eliminado del catálogo.")
    else:
        st.info("No hay productos en el catálogo.")

    st.divider()
    st.subheader("Ventas registradas de delivery")
    ventas_json = cargar_ventas_delivery()
    # Validación robusta para evitar error DataFrame constructor not properly called!
    if not ventas_json or not isinstance(ventas_json, list) or not all(isinstance(e, dict) for e in ventas_json):
        st.info("Aún no hay ventas registradas.")
        return

    ventas = pd.DataFrame(ventas_json)
    # Normaliza columnas
    if "fecha" in ventas.columns:
        ventas["Fecha"] = pd.to_datetime(ventas["fecha"])
    if "usuario" in ventas.columns:
        ventas["Usuario"] = ventas["usuario"]

    empleados = ["Todos"] + sorted(ventas["Usuario"].dropna().unique().tolist())
    año = st.number_input("Año (ventas)", min_value=2000, max_value=2100, value=date.today().year, key="anio_deliv")
    mes = st.number_input("Mes (ventas)", min_value=1, max_value=12, value=date.today().month, key="mes_deliv")

    filtro = ventas[(ventas["Fecha"].dt.year == año) & (ventas["Fecha"].dt.month == mes)]
    empleado_sel = st.selectbox("Empleado (ventas)", empleados)
    if empleado_sel != "Todos":
        filtro = filtro[filtro["Usuario"] == empleado_sel]

    if not filtro.empty:
        st.dataframe(filtro.sort_values("Fecha"))

def admin_mermas_ui(tienda_id, tiendas_opciones):
    """Interfaz de administración para gestionar mermas y rupturas"""
    
    if mermas_manager is None:
        st.error("❌ Sistema de mermas no disponible")
        return
    
    st.markdown("### ⚠️ Gestión de Mermas y Rupturas")
    st.info("💡 **Información**: Las mermas son productos averiados/dañados registrados por los empleados, separados del inventario normal.")
    
    # Filtros de fecha
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        fecha_inicio = st.date_input(
            "Fecha inicio",
            value=date.today() - timedelta(days=7),
            key="mermas_fecha_inicio"
        )
    
    with col2:
        fecha_fin = st.date_input(
            "Fecha fin",
            value=date.today(),
            key="mermas_fecha_fin"
        )
    
    with col3:
        mostrar_todas = st.checkbox(
            "Todas las tiendas",
            value=False,
            key="mermas_todas_tiendas"
        )
    
    # Obtener datos según filtros
    if mostrar_todas:
        mermas_data = mermas_manager.obtener_todas_las_mermas(fecha_inicio, fecha_fin)
        titulo_tienda = "Todas las Tiendas"
    else:
        mermas_data = mermas_manager.obtener_mermas_tienda(tienda_id, fecha_inicio, fecha_fin)
        titulo_tienda = tiendas_opciones.get(tienda_id, tienda_id)
    
    if mermas_data:
        # Tabla de datos detallados
        st.markdown("---")
        st.markdown("#### 📋 Registros Detallados")
        
        # Crear DataFrame para mostrar
        df_mermas = pd.DataFrame([
            {
                'ID': m.get('id', ''),
                'Fecha': m.get('fecha', ''),
                'Hora': m.get('hora', ''),
                'Tienda': m.get('tienda_id', ''),
                'Usuario': m.get('usuario', ''),
                'Categoría': m.get('categoria', ''),
                'Producto': m.get('producto', ''),
                'Cantidad': m.get('cantidad', 0),
                'Motivo': m.get('motivo', '')
            }
            for m in mermas_data
        ])
        
        # Filtros adicionales para la tabla
        col_filtro1, col_filtro2 = st.columns(2)
        
        with col_filtro1:
            categoria_filtro = st.selectbox(
                "Filtrar por categoría:",
                options=["Todas"] + list(set(df_mermas['Categoría'].tolist())),
                key="filtro_categoria_mermas"
            )
        
        with col_filtro2:
            motivo_filtro = st.selectbox(
                "Filtrar por motivo:",
                options=["Todos"] + list(set(df_mermas['Motivo'].tolist())),
                key="filtro_motivo_mermas"
            )
        
        # Aplicar filtros
        df_filtrado = df_mermas.copy()
        if categoria_filtro != "Todas":
            df_filtrado = df_filtrado[df_filtrado['Categoría'] == categoria_filtro]
        if motivo_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Motivo'] == motivo_filtro]
        
        # Mostrar tabla
        if not df_filtrado.empty:
            st.dataframe(
                df_filtrado.sort_values(['Fecha', 'Hora'], ascending=[False, False]),
                use_container_width=True,
                height=400
            )
            
            # Estadísticas de la tabla filtrada
            if len(df_filtrado) != len(df_mermas):
                st.info(f"📊 Mostrando {len(df_filtrado)} de {len(df_mermas)} registros (filtrado)")
        else:
            st.warning("⚠️ No hay registros que coincidan con los filtros seleccionados")
        
        # Botón de descarga Excel
        st.markdown("---")
        st.markdown("#### 📥 Exportar Datos")
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            if st.button("📊 Descargar Excel - Datos Filtrados", key="download_excel_filtered"):
                try:
                    # Exportar datos según filtros
                    tienda_export = None if mostrar_todas else tienda_id
                    excel_data = mermas_manager.exportar_a_excel(tienda_export, fecha_inicio, fecha_fin)
                    
                    # Nombre del archivo
                    nombre_archivo = f"mermas_{titulo_tienda.replace(' ', '_')}_{fecha_inicio}_{fecha_fin}.xlsx"
                    
                    st.download_button(
                        label="💾 Descargar archivo Excel",
                        data=excel_data,
                        file_name=nombre_archivo,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_excel_button"
                    )
                except Exception as e:
                    st.error(f"Error generando Excel: {str(e)}")
        
        with col_export2:
            st.info("💡 **Tip**: El archivo Excel incluye una hoja de resumen con estadísticas adicionales")
    
    else:
        st.info(f"📭 No hay registros de mermas para {titulo_tienda} en el período seleccionado ({fecha_inicio} - {fecha_fin})")
        st.markdown("### 💡 Sugerencias:")
        st.write("• Verifica que las fechas sean correctas")
        st.write("• Los empleados pueden registrar mermas desde la pestaña 'Merma/Ruptura'")
        st.write("• Las mermas se guardan automáticamente por fecha y tienda")

# Instancia global del sistema de alertas
if 'stock_alert_system' not in locals():
    try:
        from .stock_alerts import StockAlertSystem
        stock_alert_system = StockAlertSystem()
    except ImportError:
        try:
            from stock_alerts import StockAlertSystem
            stock_alert_system = StockAlertSystem()
        except ImportError:
            stock_alert_system = None

def mostrar_interfaz_admin():
    """
    Función wrapper para compatibilidad con main_inventory.py de BusinessSuite
    Llama a la interfaz moderna de administrador
    """
    try:
        # Cargar inventario de la tienda seleccionada
        try:
            from .persistencia import cargar_inventario
        except ImportError:
            from persistencia import cargar_inventario
        
        # Obtener tienda seleccionada del session_state
        tienda_id = st.session_state.get('inventory_user', {}).get('tienda', 'T001')
        
        # Cargar inventario actual (sin selector de fecha)
        st.info(f"📊 Mostrando inventario actual de la tienda")
        
        # Cargar inventario sin fecha (siempre lo último guardado)
        inventario = cargar_inventario(tienda_id, None)
        
        # Mostrar interfaz moderna
        admin_inventario_ui(inventario, tienda_id)
        
    except Exception as e:
        st.error(f"❌ Error al cargar interfaz de administrador: {str(e)}")
        st.info("Verifica que todos los módulos estén correctamente instalados")
        
        # Mostrar traceback para depuración
        import traceback
        with st.expander("🔍 Ver detalles del error"):
            st.code(traceback.format_exc())
        
        # Interfaz básica de respaldo
        st.markdown("### 📦 Gestión de Inventario (Modo Básico)")
        st.warning("⚠️ Usando interfaz simplificada por problemas técnicos")
        
        try:
            from .config_tiendas import cargar_config_tiendas
        except ImportError:
            from config_tiendas import cargar_config_tiendas
        
        config_tiendas = cargar_config_tiendas()
        tiendas_opciones = {tid: info["nombre"] for tid, info in config_tiendas.items()}
        
        tienda_id = st.selectbox(
            "Seleccionar tienda:",
            options=list(tiendas_opciones.keys()),
            format_func=lambda x: tiendas_opciones[x]
        )
        
        st.info(f"Inventario de: {tiendas_opciones[tienda_id]}")

def generar_reporte_plantilla_tienda(df, categoria, tienda_id):
    """Genera un reporte en formato de plantilla de tienda con columnas Bultos/Unidad separadas"""
    
    st.markdown("---")
    st.markdown(f"### 📋 Reporte Formato Plantilla Tienda - {categoria}")
    st.info("🏪 **Este reporte imita exactamente el formato de la plantilla utilizada en la tienda**")
    
    # Crear encabezado informativo
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    st.markdown(f"**SUCURSAL:** {tienda_id} | **FECHA:** {fecha_actual}")
    
    # Crear DataFrame para mostrar en formato de tabla limpia
    tabla_data = []
    
    if categoria == "Por Kilos":
        # Formato especial para Por Kilos con 4 columnas
        for _, row in df.iterrows():
            producto = row.get("📦 Producto", "N/A")
            cajas_cerradas = row.get("🔒 Cajas Cerradas", 0)
            cajas_abiertas = row.get("📂 Cajas Abiertas", 0)
            kgs_abiertas = row.get("⚖️ Kgs Abiertas", "0.0kg")
            total_kgs = row.get("📊 Total Kgs", "0.0kg")
            
            # Limpiar formato de kgs
            kgs_num = float(kgs_abiertas.replace("kg", "")) if isinstance(kgs_abiertas, str) else kgs_abiertas
            total_num = float(total_kgs.replace("kg", "")) if isinstance(total_kgs, str) else total_kgs
            
            tabla_data.append({
                "ARTICULO": producto,
                "CAJAS_CERRADAS": int(cajas_cerradas) if isinstance(cajas_cerradas, (int, float)) else 0,
                "CAJAS_ABIERTAS": int(cajas_abiertas) if isinstance(cajas_abiertas, (int, float)) else 0,
                "KGS_ABIERTAS": f"{kgs_num:.3f}".replace(".", ",") + " kg",
                "TOTAL_KGS": f"{total_num:.3f}".replace(".", ",") + " kg"
            })
        
        # Crear DataFrame para la tabla de Por Kilos
        df_tabla = pd.DataFrame(tabla_data)
        
        # Mostrar la tabla con formato específico para Por Kilos
        st.dataframe(
            df_tabla,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ARTICULO": st.column_config.TextColumn("🍦 ARTICULO", width="large"),
                "CAJAS_CERRADAS": st.column_config.NumberColumn("🔒 CAJAS CERRADAS", width="small"),
                "CAJAS_ABIERTAS": st.column_config.NumberColumn("📂 CAJAS ABIERTAS", width="small"),
                "KGS_ABIERTAS": st.column_config.TextColumn("⚖️ KGS ABIERTAS", width="small"),
                "TOTAL_KGS": st.column_config.TextColumn("📊 TOTAL KGS", width="small")
            }
        )
        
    else:
        # Formato tradicional para Impulsivo y Extras
        for _, row in df.iterrows():
            producto = row.get("📦 Producto", "N/A")
            bultos = row.get("📦 Bultos", 0)
            unidad = row.get("🔢 Unidad", 0)
            tabla_data.append({
                "ARTICULO": producto,
                "BULTOS": int(bultos),
                "UNIDAD": int(unidad)
            })
        
        # Crear DataFrame para la tabla
        df_tabla = pd.DataFrame(tabla_data)
        
        # Mostrar la tabla con formato limpio
        st.dataframe(
            df_tabla,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ARTICULO": st.column_config.TextColumn("🏷️ ARTICULO", width="large"),
                "BULTOS": st.column_config.NumberColumn("📦 BULTOS", width="small"),
                "UNIDAD": st.column_config.NumberColumn("🔢 UNIDAD", width="small")
            }
        )
    
    # Estadísticas del reporte
    if categoria == "Por Kilos":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_productos = len(df)
            st.metric("🍦 Total Productos", total_productos)
        
        with col2:
            total_cajas = 0
            if "🔒 Cajas Cerradas" in df.columns and "📂 Cajas Abiertas" in df.columns:
                total_cajas = df["🔒 Cajas Cerradas"].sum() + df["📂 Cajas Abiertas"].sum()
            st.metric("📦 Total Cajas", int(total_cajas))
        
        with col3:
            productos_cargados = len(df[df["✅ Estado"] == "🟢 Cargado"]) if "✅ Estado" in df.columns else 0
            st.metric("✅ Productos Cargados", productos_cargados)
        
        # Preparar DataFrame para descarga con formato de plantilla Para Kilos
        df_plantilla = pd.DataFrame(tabla_data)
        
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_productos = len(df)
            st.metric("📦 Total Productos", total_productos)
        
        with col2:
            total_bultos = df["📦 Bultos"].sum() if "📦 Bultos" in df.columns else 0
            st.metric("📦 Total Bultos", int(total_bultos))
        
        with col3:
            productos_cargados = len(df[df["✅ Estado"] == "🟢 Cargado"]) if "✅ Estado" in df.columns else 0
            st.metric("✅ Productos Cargados", productos_cargados)
        
        # Preparar DataFrame para descarga con formato de plantilla tradicional
        df_plantilla = pd.DataFrame({
            "ARTICULO": df["📦 Producto"] if "📦 Producto" in df.columns else df.get("📦 Producto", []),
            "BULTOS": df["📦 Bultos"] if "📦 Bultos" in df.columns else [0] * len(df),
            "UNIDAD": df["🔢 Unidad"] if "🔢 Unidad" in df.columns else [0] * len(df)
        })
    
    # Botón de descarga en formato plantilla
    try:
        try:
            from .utils import df_to_excel_bytes
        except ImportError:
            from utils import df_to_excel_bytes
        
        excel_bytes = df_to_excel_bytes(df_plantilla)
        
        st.download_button(
            label="📥 Descargar Formato Plantilla Tienda (Excel)",
            data=excel_bytes,
            file_name=f"plantilla_tienda_{categoria}_{tienda_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            help="Descarga en formato exacto de plantilla de tienda: ARTICULO | BULTOS | UNIDAD"
        )
        
        # También ofrecer descarga en CSV
        csv_data = df_plantilla.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Descargar Formato Plantilla Tienda (CSV)",
            data=csv_data,
            file_name=f"plantilla_tienda_{categoria}_{tienda_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"❌ Error generando descarga: {e}")
    
    st.success("✅ Reporte generado en formato de plantilla de tienda")
    st.info("💡 **Tip:** Este formato es idéntico al que se usa en la tienda físicamente")