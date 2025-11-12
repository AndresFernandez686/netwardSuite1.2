# UI y lógica de empleados (Inventario, delivery, mermas) - Versión Limpia
import streamlit as st
from datetime import date, datetime
from config_tiendas import selector_tienda_empleado, GestorTiendas
from mermas_manager import MermasManager
try:
    from utils import df_to_csv_bytes
except ImportError:
    def df_to_csv_bytes(df):
        return df.to_csv(index=False).encode('utf-8')

# Estructura completa de productos por defecto
PRODUCTOS_BASE = {
    "Impulsivo": {
        "Alfajor Almendrado": 0,
        "Alfajor Bombon Crocante": 0,
        "Alfajor Bombon Escoces": 0,
        "Alfajor Bombon Suizo": 0,
        "Alfajor Bombon Cookies and Crema": 0,
        "Alfajor Bombon Vainilla": 0,
        "Alfajor Casatta": 0,
        "Crocantino": 0,
        "Delicia": 0,
        "Pizza": 0,
        "Familiar 1": 0,
        "Familiar 2": 0,
        "Familiar 3": 0,
        "Familiar 4": 0,
        "Palito Bombon": 0,
        "Palito Crema Americana": 0,
        "Palito Crema Frutilla": 0,
        "Palito Frutal Frutilla": 0,
        "Palito Frutal Limon": 0,
        "Palito Frutal Naranja": 0,
        "Tentacion Chocolate": 0,
        "Tentacion Chocolate con Almendra": 0,
        "Tentacion Cookies": 0,
        "Tentacion Crema Americana": 0,
        "Tentacion Dulce de Leche Granizado": 0,
        "Tentacion Dulce de Leche": 0,
        "Tentacion Frutilla": 0,
        "Tentacion Granizado": 0,
        "Tentacion Menta Granizada": 0,
        "Tentacion Mascarpone": 0,
        "Tentacion Vainilla": 0,
        "Tentacion Limon": 0,
        "Tentacion Toddy": 0,
        "Yogurt Helado Frutilla sin Tacc": 0,
        "Yogurt Helado Mango Maracuya": 0,
        "Yogurt Helado Frutos del Bosque sin Tacc": 0,
        "Helado sin Azucar Frutilla a la Crema": 0,
        "Helado sin Azucar Durazno a la Crema": 0,
        "Helado sin Azucar chocolate sin Tacc": 0,
        "Torta Grido Rellena": 0,
        "Torta Milka": 0,
        "Torta Helada Cookies Mousse": 0
    },
    "Por Kilos": {
        "Vainilla": 0.0,
        "Chocolate": 0.0,
        "Fresa": 0.0,
        "Anana a la crema": 0.0,
        "Banana con Dulce de leche": 0.0,
        "Capuccino Granizado": 0.0,
        "Cereza": 0.0,
        "Chocolate Blanco": 0.0,
        "Chocolate con Almendra": 0.0,
        "Chocolate Mani Crunch": 0.0,
        "Chocolate Suizo": 0.0,
        "Crema Americana": 0.0,
        "Crema Cookie": 0.0,
        "Crema Rusa": 0.0,
        "Dulce de Leche": 0.0,
        "Dulce de Leche con Brownie": 0.0,
        "Dulce de Leche con Nuez": 0.0,
        "Dulce de Leche Especial": 0.0,
        "Dulce de Leche Granizado": 0.0,
        "Durazno a la Crema": 0.0,
        "Flan": 0.0,
        "Frutos Rojos al Agua": 0.0,
        "Granizado": 0.0,
        "Kinotos al Whisky": 0.0,
        "Limon al Agua": 0.0,
        "Maracuya": 0.0,
        "Marroc Grido": 0.0,
        "Mascarpone con Frutos del Bosque": 0.0,
        "Menta Granizada": 0.0,
        "Naranja Helado al Agua": 0.0,
        "Pistacho": 0.0,
        "Super Gridito": 0.0,
        "Tiramisu": 0.0,
        "Tramontana": 0.0,
        "Candy": 0.0,
    },
    "Extras": {
        "Cinta Grido": 0,
        "Cobertura Chocolate": 0,
        "Bolsa 40x50": 0,
        "Cobertura Frutilla": 0,
        "Cobertura Dulce de Leche": 0,
        "Leche": 0,
        "Cuchara Sunday": 0,
        "Cucharita Grido": 0,
        "Cucurucho Biscoito Dulce x300": 0,
        "Cucurucho Cascao x120": 0,
        "Cucurucho Nacional x54": 0,
        "Garrafita de Gas": 0,
        "Isopor 1 kilo": 0,
        "Isopor 1/2 kilo": 0,
        "Isopor 1/4": 0,
        "Mani tostado": 0,
        "Pajita con Funda": 0,
        "Servilleta Grido": 0,
        "Tapa Burbuja Capuccino": 0,
        "Tapa Burbuja Batido": 0,
        "Vaso capuccino": 0,
        "Vaso Batido": 0,
        "Vasito de una Bocha": 0,
        "Vaso Termico 240gr": 0,
        "Vaso Sundae": 0,
        "Rollo Termico": 0
    }
}

def empleado_inventario_ui(inventario, usuario, opciones_valde, guardar_inventario, guardar_historial, tienda_id="T001"):
    st.header("📦 Inventario - Netw@rd")
    
    # Inicializar carrito temporal en session_state
    if 'carrito_temporal' not in st.session_state:
        st.session_state.carrito_temporal = []
    
    # Inicializar flag de cargando
    if 'esta_guardando' not in st.session_state:
        st.session_state.esta_guardando = False
    
    # Inicializar fecha de última carga
    if 'fecha_ultima_carga' not in st.session_state:
        st.session_state.fecha_ultima_carga = None
    
    # Selector de tipo de inventario - Proporción optimizada 30-70
    col1, col2 = st.columns([3, 7])
    with col1:
        fecha_carga = st.date_input("Selecciona la fecha de carga", value=date.today(), key="fecha_inv")
    with col2:
        tipo_inventario = st.selectbox(
            "Tipo de inventario", 
            ["Diario", "Semanal", "Quincenal"], 
            key="tipo_inventario"
        )
    
    # Detectar cambio de fecha y limpiar carrito
    fecha_actual_str = fecha_carga.strftime("%Y-%m-%d")
    if st.session_state.fecha_ultima_carga is None:
        st.session_state.fecha_ultima_carga = fecha_actual_str
    elif st.session_state.fecha_ultima_carga != fecha_actual_str:
        # La fecha cambió - limpiar carrito y reiniciar inventario
        if st.session_state.carrito_temporal:
            st.warning(f"⚠️ Fecha cambiada de {st.session_state.fecha_ultima_carga} a {fecha_actual_str}. Carrito limpiado.")
            st.session_state.carrito_temporal = []
        st.session_state.fecha_ultima_carga = fecha_actual_str
        
        # Reiniciar inventario para la nueva fecha
        from persistencia import cargar_inventario as cargar_inv_local, guardar_inventario as guardar_inv_local
        inventario_vacio = {
            "Impulsivo": {},
            "Por Kilos": {},
            "Extras": {}
        }
        guardar_inv_local(inventario_vacio, tienda_id)
        st.info(f"🔄 Inventario reiniciado para la fecha {fecha_actual_str}")
    
    # Mostrar información sobre el tipo seleccionado
    if tipo_inventario == "Quincenal":
        st.info("**Inventario Quincenal**: En la categoría 'Por Kilos' registrarás la cantidad exacta en kilos de cada balde.")
    elif tipo_inventario == "Semanal":
        st.info("**Inventario Semanal**: En la categoría 'Por Kilos' usa opciones descriptivas como 'Lleno', 'Medio lleno', etc.")

    # Pestañas por categoría
    tab_impulsivo, tab_kilos, tab_extras = st.tabs(["🍦 Impulsivo", "⚖️ Por Kilos", "🛠️ Extras"])
    
    # Cargar inventario actual de forma robusta
    try:
        # Siempre usar la estructura completa de productos como base
        inventario_actual = PRODUCTOS_BASE.copy()
        
        # Si inventario tiene datos válidos, mergearlos
        if isinstance(inventario, dict):
            for categoria in inventario_actual.keys():
                if categoria in inventario and isinstance(inventario[categoria], dict):
                    # Actualizar solo los productos que existen en el inventario cargado
                    for producto in inventario_actual[categoria].keys():
                        if producto in inventario[categoria]:
                            inventario_actual[categoria][producto] = inventario[categoria][producto]
        
        st.success("✅ Inventario cargado correctamente")
        
    except Exception as e:
        st.error(f"Error cargando inventario: {str(e)}")
        # En caso de error, usar la estructura base completa
        inventario_actual = PRODUCTOS_BASE.copy()
        st.warning("🔄 Usando estructura de productos por defecto")
    
    # Función para agregar al carrito temporal
    def agregar_al_carrito(entrada):
        """Agrega producto al carrito temporal sin guardar inmediatamente"""
        try:
            # Verificar si el producto ya está en el carrito
            producto_existente = False
            for i, item in enumerate(st.session_state.carrito_temporal):
                if (item['categoria'] == entrada['categoria'] and 
                    item['producto'] == entrada['producto']):
                    # Actualizar cantidad si ya existe
                    st.session_state.carrito_temporal[i] = entrada
                    producto_existente = True
                    break
            
            if not producto_existente:
                # Agregar nuevo producto al carrito
                st.session_state.carrito_temporal.append(entrada)
            
            return True
        except Exception as e:
            st.error(f"Error agregando al carrito: {str(e)}")
            return False
    
    # Función para guardar todo el carrito
    def guardar_carrito_completo():
        """Guarda todos los productos del carrito en el inventario"""
        if not st.session_state.carrito_temporal:
            st.warning("⚠️ No hay productos en el carrito para guardar")
            return False
        
        try:
            st.session_state.esta_guardando = True
            
            # Cargar inventario actual desde archivo para la tienda
            from persistencia import cargar_inventario as cargar_inv_local
            inventario_completo = cargar_inv_local(tienda_id)
            
            total_productos = len(st.session_state.carrito_temporal)
            
            # Crear barra de progreso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Procesar cada producto del carrito
            for idx, entrada in enumerate(st.session_state.carrito_temporal):
                # Actualizar progreso
                progreso = (idx + 1) / total_productos
                progress_bar.progress(progreso)
                status_text.text(f"Guardando {idx + 1} de {total_productos}: {entrada['producto']}...")
                
                categoria = entrada["categoria"]
                producto = entrada["producto"]
                cantidad = entrada["cantidad"]
                
                # Asegurar que existe la estructura de la categoría
                if categoria not in inventario_completo:
                    inventario_completo[categoria] = {}
                
                # Actualizar el producto específico
                inventario_completo[categoria][producto] = cantidad
                
                # Guardar en historial
                guardar_historial(
                    entrada["fecha"],
                    entrada["usuario"],
                    categoria,
                    producto,
                    cantidad,
                    entrada["ume"],
                    entrada["tipo_inventario"],
                    tienda_id
                )
                
                # Pequeña pausa para simular carga (opcional)
                import time
                time.sleep(0.1)
            
            # Guardar el inventario completo actualizado con la fecha
            from persistencia import guardar_inventario as guardar_inv_local
            guardar_inv_local(inventario_completo, tienda_id, fecha_carga)
            
            # Limpiar barra de progreso
            progress_bar.empty()
            status_text.empty()
            
            # Limpiar carrito
            productos_guardados = len(st.session_state.carrito_temporal)
            st.session_state.carrito_temporal = []
            st.session_state.esta_guardando = False
            
            st.success(f"✅ {productos_guardados} productos guardados exitosamente!")
            return True
            
        except Exception as e:
            st.session_state.esta_guardando = False
            st.error(f"Error guardando carrito: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            return False
    
    # Función para limpiar el carrito
    def limpiar_carrito():
        """Limpia todos los productos del carrito sin guardar"""
        st.session_state.carrito_temporal = []
        st.info("🗑️ Inventario limpiado")
    
    # Función para eliminar un producto específico del carrito
    def eliminar_producto_carrito(indice):
        """Elimina un producto específico del carrito"""
        if 0 <= indice < len(st.session_state.carrito_temporal):
            producto_eliminado = st.session_state.carrito_temporal.pop(indice)
            st.success(f"🗑️ {producto_eliminado['producto']} eliminado del carrito")
            return True
        return False
    
    with tab_impulsivo:
        manejar_categoria_simple("Impulsivo", inventario_actual, tienda_id, fecha_carga, usuario, tipo_inventario, agregar_al_carrito, guardar_historial)
    
    with tab_kilos:
        manejar_categoria_kilos_simple("Por Kilos", inventario_actual, tienda_id, fecha_carga, usuario, tipo_inventario, agregar_al_carrito, guardar_historial, opciones_valde)
    
    with tab_extras:
        manejar_categoria_simple("Extras", inventario_actual, tienda_id, fecha_carga, usuario, tipo_inventario, agregar_al_carrito, guardar_historial)
    
    # --- SECCIÓN DEL CARRITO AL FINAL ---
    st.markdown("---")
    st.markdown("---")  # Doble línea para mayor separación
    
    # Mostrar resumen del carrito
    if st.session_state.carrito_temporal:
        st.markdown("### 🛒 Productos Cargados")
        st.success(f"**{len(st.session_state.carrito_temporal)} producto(s)** listo(s) para actualizar")
        
        # Tabla de productos con opción de eliminar
        st.markdown("#### Listado de Productos:")
        
        for idx, item in enumerate(st.session_state.carrito_temporal):
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
            
            with col1:
                st.write(f"**{item['producto']}**")
            
            with col2:
                st.write(f"📦 {item['categoria']}")
            
            with col3:
                st.write(f"{item['cantidad']} {item['ume']}")
            
            with col4:
                st.write(f"🕐 {item['hora']}")
            
            with col5:
                if st.button("❌", key=f"eliminar_{idx}", help="Eliminar este producto"):
                    eliminar_producto_carrito(idx)
                    st.rerun()
        
        # Botones de acción
        st.markdown("---")
        col_actualizar, col_limpiar = st.columns(2)
        
        with col_actualizar:
            if st.button(
                "✅ ACTUALIZAR INVENTARIO", 
                disabled=st.session_state.esta_guardando,
                use_container_width=True,
                type="primary",
                key="btn_actualizar_final"
            ):
                if guardar_carrito_completo():
                    st.rerun()
        
        with col_limpiar:
            if st.button(
                "🗑️ Limpiar Inventario", 
                disabled=st.session_state.esta_guardando,
                use_container_width=True,
                key="btn_limpiar_final"
            ):
                limpiar_carrito()
                st.rerun()
    else:
        st.info("🛒 No hay productos cargados - Agrega productos usando las pestañas de arriba")

def manejar_categoria_simple(categoria, inventario_tienda, tienda_id, fecha_carga, usuario, tipo_inventario, guardar_entrada_inventario, guardar_historial):
    """Maneja categorías con selector simple y robusto"""
    
    st.markdown(f"### Producto de {categoria}")
    
    # Obtener productos de la categoría de forma segura
    try:
        productos_categoria = inventario_tienda.get(categoria, {})
        if not productos_categoria:
            # Usar la estructura base completa si no hay datos
            productos_categoria = PRODUCTOS_BASE.get(categoria, {"Producto Genérico": 0})
        
        # Extraer nombres de productos de cualquier tipo de estructura
        productos_nombres = list(productos_categoria.keys())
        
        if not productos_nombres:
            st.warning(f"No hay productos disponibles en {categoria}")
            return
            
        # st.info(f"📦 {len(productos_nombres)} productos disponibles en {categoria}")  # Comentado según solicitud
            
    except Exception as e:
        st.error(f"Error accediendo a productos de {categoria}: {str(e)}")
        # En caso de error, usar productos base
        productos_categoria = PRODUCTOS_BASE.get(categoria, {"Producto Genérico": 0})
        productos_nombres = list(productos_categoria.keys())
        st.warning(f"Usando productos por defecto para {categoria}")
    
    # Etiqueta para indicar que es un buscador
    st.markdown("**🔍 Buscar...**")
    
    # Agregar opción vacía al inicio
    opciones = [""] + productos_nombres
    
    # Selector de producto
    producto_seleccionado = st.selectbox(
        f"Producto de {categoria}",
        opciones,
        key=f"producto_{categoria}_{tienda_id}",
        label_visibility="collapsed"
    )
    
    # Si no hay selección, no continuar
    if not producto_seleccionado:
        return
    
    # Campos de entrada en una línea horizontal
    col1, col2, col3 = st.columns([2, 2, 3])
    
    with col1:
        cantidad = st.number_input(
            "Cantidad (unidades)", 
            min_value=0, 
            value=0, 
            step=1,
            key=f"cantidad_{categoria}_{tienda_id}"
        )
    
    with col2:
        # UME por defecto
        opciones_ume = ["Unidad", "Caja", "Tira"]
        ume = st.selectbox(
            "UME",
            opciones_ume,
            key=f"ume_{categoria}_{tienda_id}"
        )
    
    with col3:
        if st.button(f"➕ CARGAR {producto_seleccionado}", key=f"btn_{categoria}_{tienda_id}", use_container_width=True):
            if cantidad > 0:
                entrada_inventario = {
                    "fecha": fecha_carga.strftime("%Y-%m-%d"),
                    "hora": datetime.now().strftime("%H:%M:%S"),
                    "producto": producto_seleccionado,
                    "categoria": categoria,
                    "cantidad": cantidad,
                    "ume": ume,
                    "usuario": usuario,
                    "tienda": tienda_id,
                    "tipo_inventario": tipo_inventario
                }
                
                # Agregar al carrito temporal (no guardar todavía)
                if guardar_entrada_inventario(entrada_inventario):
                    st.success(f"✅ {producto_seleccionado} agregado al carrito: {cantidad} {ume}")
                    # No hacer rerun aquí para que el usuario pueda seguir agregando
            else:
                st.warning("⚠️ Ingresa una cantidad válida")

def manejar_categoria_kilos_simple(categoria, inventario_tienda, tienda_id, fecha_carga, usuario, tipo_inventario, guardar_entrada_inventario, guardar_historial, opciones_valde):
    """Maneja categoría Por Kilos con lógica simple"""
    
    st.markdown(f"### Producto de {categoria}")
    
    # Obtener productos de la categoría de forma segura
    try:
        productos_categoria = inventario_tienda.get(categoria, {})
        if not productos_categoria:
            # Productos por defecto para Por Kilos
            productos_categoria = {
                "Vainilla": 0.0, "Chocolate": 0.0, "Fresa": 0.0, 
                "Dulce de Leche": 0.0, "Crema Americana": 0.0
            }
        
        # Extraer nombres de productos
        productos_nombres = list(productos_categoria.keys())
        
        if not productos_nombres:
            st.warning(f"No hay productos disponibles en {categoria}")
            return
            
    except Exception as e:
        st.error(f"Error accediendo a productos de {categoria}: {str(e)}")
        return
    
    # Etiqueta para indicar que es un buscador
    st.markdown("**🔍 Buscar...**")
    
    # Agregar opción vacía al inicio
    opciones = [""] + productos_nombres
    
    # Selector de producto
    producto_seleccionado = st.selectbox(
        f"Producto de {categoria}",
        opciones,
        key=f"producto_kilos_{tienda_id}",
        label_visibility="collapsed"
    )
    
    # Si no hay selección, no continuar
    if not producto_seleccionado:
        return
    
    # Lógica diferenciada según tipo de inventario
    if tipo_inventario == "Quincenal":
        # QUINCENAL: Sistema de múltiples baldes con kilos exactos
        st.markdown("### Registrar cantidad exacta en kilos por balde:")
        
        # Selector de cantidad de baldes
        cantidad_baldes = st.number_input(
            "Cantidad de baldes", 
            min_value=1, 
            max_value=10, 
            value=1, 
            step=1,
            key=f"cantidad_baldes_{tienda_id}"
        )
        
        st.markdown(f"### Kilos en cada balde (hasta {cantidad_baldes} baldes):")
        
        # Crear inputs dinámicos para cada balde
        kilos_por_balde = []
        total_kilos = 0.0
        
        for i in range(cantidad_baldes):
            kilos = st.number_input(
                f"Balde {i+1} (kg)",
                min_value=0.0,
                value=0.0,
                step=0.1,
                key=f"balde_{i+1}_kilos_{tienda_id}"
            )
            kilos_por_balde.append(kilos)
            total_kilos += kilos
        
        # Mostrar total
        st.markdown(f"**Total: {total_kilos:.1f} kg**")
        
        # Botón para cargar (Quincenal)
        if st.button(f"➕ CARGAR {producto_seleccionado}", key=f"btn_kilos_{tienda_id}", use_container_width=True):
            if total_kilos > 0:
                # Crear detalle de baldes para el historial
                detalle_baldes = ", ".join([f"Balde {i+1}: {kilos:.1f}kg" for i, kilos in enumerate(kilos_por_balde) if kilos > 0])
                
                entrada_inventario = {
                    "fecha": fecha_carga.strftime("%Y-%m-%d"),
                    "hora": datetime.now().strftime("%H:%M:%S"),
                    "producto": producto_seleccionado,
                    "categoria": categoria,
                    "cantidad": total_kilos,
                    "ume": "Kg",
                    "baldes": cantidad_baldes,
                    "detalle_baldes": detalle_baldes,
                    "usuario": usuario,
                    "tienda": tienda_id,
                    "tipo_inventario": tipo_inventario
                }
                
                # Agregar al carrito temporal (no guardar todavía)
                if guardar_entrada_inventario(entrada_inventario):
                    st.success(f"✅ {producto_seleccionado} agregado al carrito: {total_kilos:.1f} Kg ({cantidad_baldes} baldes)")
            else:
                st.warning("⚠️ Ingresa al menos algunos kilos en los baldes")
    
    else:
        # DIARIO/SEMANAL: Solo Estados descriptivos + Cantidad de baldes
        st.markdown("### Registrar inventario por baldes:")
        
        # Selector de cantidad de baldes
        cantidad_baldes = st.number_input(
            "Cantidad de baldes", 
            min_value=1, 
            max_value=10, 
            value=1, 
            step=1,
            key=f"cantidad_baldes_{tienda_id}"
        )
        
        col1, col2 = st.columns([2, 3])
        
        with col1:
            estados = ["Lleno", "Medio lleno", "Vacío"]
            ume = st.selectbox(
                "Estado",
                estados,
                key=f"estado_kilos_{tienda_id}"
            )
        
        with col2:
            if st.button(f"➕ CARGAR {producto_seleccionado}", key=f"btn_kilos_{tienda_id}", use_container_width=True):
                if cantidad_baldes > 0:
                    # Crear detalle de baldes para el historial
                    detalle_baldes = f"{cantidad_baldes} balde{'s' if cantidad_baldes > 1 else ''} - {ume}"
                    
                    entrada_inventario = {
                        "fecha": fecha_carga.strftime("%Y-%m-%d"),
                        "hora": datetime.now().strftime("%H:%M:%S"),
                        "producto": producto_seleccionado,
                        "categoria": categoria,
                        "cantidad": cantidad_baldes,
                        "ume": ume,
                        "baldes": cantidad_baldes,
                        "detalle_baldes": detalle_baldes,
                        "usuario": usuario,
                        "tienda": tienda_id,
                        "tipo_inventario": tipo_inventario
                    }
                    
                    # Agregar al carrito temporal (no guardar todavía)
                    if guardar_entrada_inventario(entrada_inventario):
                        st.success(f"✅ {producto_seleccionado} agregado al carrito: {cantidad_baldes} balde{'s' if cantidad_baldes > 1 else ''} - {ume}")
                else:
                    st.warning("⚠️ Ingresa al menos 1 balde")

def empleado_delivery_ui(usuario, cargar_catalogo_delivery, guardar_venta_delivery, cargar_ventas_delivery):
    st.header("Delivery")
    catalogo = cargar_catalogo_delivery()
    activos = [item for item in catalogo if item.get("activo", True)]

    if not activos:
        st.info("No hay productos de delivery activos. Pide al administrador que agregue opciones.")
        return

    fecha_venta = st.date_input("Fecha de la venta", value=date.today(), key="fecha_deliv")
    
    # Registro de venta
    st.subheader("Registrar nueva venta")
    producto_sel = st.selectbox("Producto", [item["nombre"] for item in activos], key="prod_deliv")
    precio_prod = next(item["precio"] for item in activos if item["nombre"] == producto_sel)
    
    cantidad = st.number_input("Cantidad", min_value=1, value=1, key="cant_deliv")
    total = precio_prod * cantidad
    
    st.write(f"Total: ${total}")
    
    if st.button("Registrar venta", key="reg_venta"):
        venta = {
            "fecha": fecha_venta.strftime("%Y-%m-%d"),
            "hora": datetime.now().strftime("%H:%M:%S"),
            "producto": producto_sel,
            "cantidad": cantidad,
            "precio_unitario": precio_prod,
            "total": total,
            "usuario": usuario
        }
        
        guardar_venta_delivery(venta)
        st.success(f"✅ Venta registrada: {cantidad}x {producto_sel} = ${total}")
        st.rerun()
    
    # Mostrar ventas del día
    st.divider()
    st.subheader("Ventas de hoy")
    ventas_hoy = [v for v in cargar_ventas_delivery() 
                  if v.get("fecha") == fecha_venta.strftime("%Y-%m-%d")]
    
    if ventas_hoy:
        total_dia = sum(v.get("total", 0) for v in ventas_hoy)
        st.metric("Total del día", f"${total_dia}")
        
        for venta in ventas_hoy[-5:]:  # Últimas 5 ventas
            st.write(f"• {venta.get('hora', '')} - {venta.get('cantidad', 0)}x {venta.get('producto', '')} = ${venta.get('total', 0)}")
    else:
        st.info("No hay ventas registradas hoy")

def empleado_mermas_ui(usuario, tienda_id="T001"):
    """Interfaz de mermas y rupturas para empleados"""
    st.header("⚠️ Mermas y Rupturas")
    
    # Inicializar el gestor de mermas
    mermas_manager = MermasManager()
    
    # Información sobre el sistema
    with st.expander("ℹ️ ¿Qué es una merma/ruptura?"):
        st.markdown("""
        **Mermas** son productos que se pierden o dañan y deben ser registrados separadamente del inventario normal.
        
        **Motivos comunes:**
        - 🍦 **Ruptura**: Producto roto o dañado
        - 📅 **Vencimiento**: Producto vencido
        - 🧊 **Derretimiento**: Helado derretido
        - 🔧 **Defecto**: Producto defectuoso
        - 💢 **Accidente**: Caída o accidente
        """)
    
    # Fecha del registro
    fecha_merma = st.date_input("📅 Fecha de la merma", value=date.today(), key="fecha_merma")
    
    # Selector de categoría y producto
    st.markdown("### 📦 Seleccionar Producto")
    
    col1, col2 = st.columns(2)
    
    with col1:
        categoria = st.selectbox(
            "Categoría",
            ["Impulsivo", "Por Kilos", "Extras"],
            key="categoria_merma"
        )
    
    with col2:
        # Obtener productos de la categoría seleccionada
        productos_categoria = PRODUCTOS_BASE.get(categoria, {})
        productos_nombres = list(productos_categoria.keys()) if productos_categoria else ["No hay productos"]
        
        producto = st.selectbox(
            "Producto",
            productos_nombres,
            key="producto_merma"
        )
    
    # Campos de la merma
    st.markdown("### 📝 Detalles de la Merma")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Para Por Kilos usar decimales, para otros enteros
        if categoria == "Por Kilos":
            cantidad = st.number_input(
                "Cantidad (kg)",
                min_value=0.0,
                value=0.0,
                step=0.1,
                key="cantidad_merma"
            )
        else:
            cantidad = st.number_input(
                "Cantidad (unidades)",
                min_value=0,
                value=0,
                step=1,
                key="cantidad_merma"
            )
    
    with col2:
        motivos = ["Ruptura", "Vencimiento", "Derretimiento", "Defecto", "Accidente", "Otro"]
        motivo = st.selectbox(
            "Motivo",
            motivos,
            key="motivo_merma"
        )
    
    # Mostrar resumen antes de guardar
    if cantidad > 0:
        st.markdown("### 📋 Resumen de la Merma")
        
        unidad = "kg" if categoria == "Por Kilos" else "unidades"
        
        col_resumen1, col_resumen2 = st.columns(2)
        
        with col_resumen1:
            st.info(f"""
            **📦 Producto:** {producto}  
            **📂 Categoría:** {categoria}  
            **📊 Cantidad:** {cantidad} {unidad}
            """)
        
        with col_resumen2:
            st.warning(f"""
            **⚠️ Motivo:** {motivo}  
            **👤 Usuario:** {usuario}  
            **📅 Fecha:** {fecha_merma.strftime('%d/%m/%Y')}
            """)
        
        # Botón para registrar merma
    if st.button("🔴 REGISTRAR MERMA", type="primary", disabled=(cantidad <= 0)):
        if cantidad > 0:
            # Registrar la merma
            exito = mermas_manager.registrar_merma(
                tienda_id=tienda_id,
                usuario=usuario,
                fecha=fecha_merma,
                categoria=categoria,
                producto=producto,
                cantidad=cantidad,
                motivo=motivo
            )
            
            if exito:
                st.success(f"✅ Merma registrada exitosamente!")
                st.success(f"🔍 {producto}: {cantidad} {'kg' if categoria == 'Por Kilos' else 'unidades'} por {motivo}")
                
                # Limpiar formulario
                st.session_state.cantidad_merma = 0.0 if categoria == "Por Kilos" else 0
                
                # Rerun para limpiar
                st.rerun()
            else:
                st.error("❌ Error al registrar la merma. Intenta nuevamente.")
        else:
            st.warning("⚠️ Ingresa una cantidad válida mayor a 0")
    
    # Mostrar mermas del día
    st.markdown("---")
    st.markdown("### 📊 Mermas de Hoy")
    
    # Obtener mermas del día actual
    mermas_hoy = mermas_manager.obtener_mermas_tienda(
        tienda_id=tienda_id,
        fecha_inicio=date.today(),
        fecha_fin=date.today()
    )
    
    if mermas_hoy:
        st.info(f"📈 Total de mermas registradas hoy: **{len(mermas_hoy)}**")
        
        # Mostrar últimas 5 mermas
        for merma in mermas_hoy[-5:]:
            with st.expander(f"⚠️ {merma.get('producto', 'N/A')} - {merma.get('cantidad', 0)} {'kg' if merma.get('categoria') == 'Por Kilos' else 'unidades'}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**🕐 Hora:** {merma.get('hora', 'N/A')}")
                    st.write(f"**📂 Categoría:** {merma.get('categoria', 'N/A')}")
                    st.write(f"**⚠️ Motivo:** {merma.get('motivo', 'N/A')}")
                
                with col2:
                    st.write(f"**👤 Usuario:** {merma.get('usuario', 'N/A')}")
                    st.write(f"**📅 Fecha:** {merma.get('fecha', 'N/A')}")
    else:
        st.info("🎉 No hay mermas registradas hoy")