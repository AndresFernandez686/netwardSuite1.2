import streamlit as st
from datetime import date, datetime, timedelta
import pandas as pd

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
    from .ui_empleado import PRODUCTOS_BASE
except ImportError:
    try:
        from ui_empleado import PRODUCTOS_BASE
    except ImportError:
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
        st.subheader(f"Categoría: {categoria}")
        
        productos = inventario[categoria]
        
        # Para mostrar productos no cargados, incluir también productos base que no están en inventario
        productos_completos = productos.copy()
        if categoria in PRODUCTOS_BASE:
            for producto_base in PRODUCTOS_BASE[categoria]:
                if producto_base not in productos_completos:
                    productos_completos[producto_base] = 0  # Agregar como no cargado
        
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
            st.warning(f" No se encontraron productos en '{categoria}' con el término '{busqueda}'")
            continue
        
        # Usar orden alfabético simple para todas las categorías
        productos_ordenados = sorted(productos_filtrados.keys())
        
        # Limitar a los últimos 3 resultados cuando hay búsqueda
        if busqueda and len(productos_ordenados) > 3:
            productos_ordenados = productos_ordenados[-3:]
        
        # Crear DataFrame según la categoría y agregar indicadores de stock
        if categoria == "Por Kilos":
            productos_csv = []
            # Crear tabla específica para productos por kilos
            for producto in productos_ordenados:
                baldes = productos_filtrados[producto]
                
                # Calcular cantidad total para determinar el estado de alerta
                if isinstance(baldes, list):
                    cantidad_total = sum(baldes) if all(isinstance(x, (int, float)) for x in baldes) else len([b for b in baldes if str(b) != "Vacío"])
                else:
                    cantidad_total = baldes if isinstance(baldes, (int, float)) else 0
                
                # Obtener indicador de alerta
                if stock_alert_system:
                    emoji, status, desc = stock_alert_system.get_stock_status(producto, cantidad_total)
                    estado_alerta = f"{emoji} {desc}"
                    color_css = stock_alert_system.get_stock_color_css(status)
                else:
                    emoji, status, desc, estado_alerta = "📦", "unknown", "N/A", "📦 N/A"
                    color_css = "background: #f8f9fa; color: #333;"
                
                # Obtener último modo (UME) usado
                modo = obtener_ultimo_modo(producto, categoria, tienda_id)
                
                if isinstance(baldes, list):
                    # Verificar si son kilos (números) o estados (strings)
                    if all(isinstance(x, (int, float)) for x in baldes):
                        # Formato quincenal con kilos
                        total_kilos = sum(baldes)
                        kilos_detalle = ", ".join([f'{k:.1f}kg' for k in baldes])
                        estado = "🟢 Cargado" if total_kilos > 0 else "🔴 No cargado"
                        productos_csv.append({
                            "🚨 Estado": estado_alerta,
                            "📦 Producto": producto, 
                            "📊 Detalle": f"Total: {total_kilos:.1f} kg",
                            "🏪 Baldes": kilos_detalle, 
                            "⚖️ Cantidad": total_kilos,
                            "📅 Tipo": "Quincenal",
                            "📌 Modo": modo,
                            "✅ Estado": estado
                        })
                    else:
                        # Formato diario/semanal con estados
                        estado_baldes = ", ".join([str(b) for b in baldes])
                        llenos = sum(1 for b in baldes if str(b) != "Vacío")
                        estado = "🟢 Cargado" if llenos > 0 else "🔴 No cargado"
                        productos_csv.append({
                            "🚨 Estado": estado_alerta,
                            "📦 Producto": producto, 
                            "📊 Detalle": f"{llenos} baldes llenos",
                            "🏪 Baldes": estado_baldes, 
                            "⚖️ Cantidad": llenos,
                            "📅 Tipo": "Diario/Semanal",
                            "📌 Modo": modo,
                            "✅ Estado": estado
                        })
                else:
                    estado = "🟢 Cargado" if baldes > 0 else "🔴 No cargado"
                    productos_csv.append({
                        "🚨 Estado": estado_alerta,
                        "📦 Producto": producto, 
                        "📊 Detalle": str(baldes),
                        "🏪 Baldes": str(baldes), 
                        "⚖️ Cantidad": baldes if isinstance(baldes, (int, float)) else 0,
                        "📅 Tipo": "Diario/Semanal",
                        "📌 Modo": modo,
                        "✅ Estado": estado
                    })
        else:
            # Para otras categorías (Impulsivo, Extras)
            productos_csv = []
            for producto in productos_ordenados:
                if producto not in productos_filtrados:
                    continue
                    
                cantidad_data = productos_filtrados[producto]
                
                # Extraer la cantidad según la estructura
                if categoria == "Impulsivo" and isinstance(cantidad_data, dict):
                    cantidad = cantidad_data.get("stock", 0)
                else:
                    cantidad = cantidad_data
                
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
        
        # Crear DataFrame
        df = pd.DataFrame(productos_csv)
        
        # Filtros adicionales para categorías específicas
        if categoria in ["Por Kilos", "Impulsivo", "Extras"]:
            # Agregar filtro por estado de carga
            col_estado, col_info = st.columns([1, 2])
            with col_estado:
                estados = ["Todos", "🟢 Cargado", "🔴 No cargado"]
                estado_seleccionado = st.selectbox(f"Estado en {categoria}", estados)
                
                if estado_seleccionado != "Todos":
                    df = df[df["✅ Estado"] == estado_seleccionado]
            
            with col_info:
                if not df.empty:
                    st.info(f"📋 Mostrando {len(df)} productos de {categoria}")
        
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
                    label=f"📥 Descargar Excel de {categoria}",
                    data=excel_bytes,
                    file_name=f"inventario_{categoria.lower().replace(' ', '_')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.warning(f"Error preparando descarga: {e}")
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
                if cantidad.get("tipo") == "Quincenal" and "total_kilos" in cantidad:
                    total = cantidad.get("total_kilos", 0)
                    kilos_detalle = cantidad.get("kilos_por_balde", [])
                    detalle = ', '.join([f'{k:.1f}kg' for k in kilos_detalle])
                    return f"Total: {total:.1f} kg ({detalle})"
                elif "estados" in cantidad:
                    estados = cantidad.get("estados", [])
                    return f"{', '.join(estados)}"
            elif isinstance(cantidad, list):
                if all(isinstance(x, (int, float)) for x in cantidad):
                    # Lista de kilos
                    total = sum(cantidad)
                    detalle = ', '.join([f'{k:.1f}kg' for k in cantidad])
                    return f"Total: {total:.1f} kg ({detalle})"
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
        
        # Cargar inventario
        inventario = cargar_inventario(tienda_id)
        
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