# UI y lógica de empleados (Inventario) - Versión BusinessSuite Corregida
import streamlit as st
from datetime import date, datetime
from .config_tiendas import selector_tienda_empleado, GestorTiendas
from .persistencia import cargar_inventario, guardar_inventario, guardar_historial

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
    },
    "Por Kilos": {
        "Almendras": 0,
        "Brownie": 0,
        "Choco Granita": 0,
        "Cookies": 0,
        "Frutilla a la Crema": 0,
        "Granita de Café": 0,
        "Limón": 0,
        "Menta Granizada": 0,
        "Sambayón": 0,
        "Tiramisu": 0,
        "Tramontana": 0,
        "Vainilla": 0,
    },
    "Extras": {
        "Cobertura Chocolate": 0,
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

def mostrar_interfaz_empleado(inventario=None, usuario="empleado1", opciones_valde=None, tienda_id="T001"):
    """Interfaz principal para empleados con formularios correctos y manejo de errores"""
    st.header("📦 Inventario - BusinessSuite")
    
    # Inicializar estados de sesión
    if 'carrito_temporal' not in st.session_state:
        st.session_state.carrito_temporal = []
    
    if 'esta_guardando' not in st.session_state:
        st.session_state.esta_guardando = False
    
    if 'fecha_ultima_carga' not in st.session_state:
        st.session_state.fecha_ultima_carga = None

    # Selección de fecha y tipo de inventario
    col1, col2 = st.columns([3, 7])
    with col1:
        fecha_carga = st.date_input("Selecciona la fecha de carga", value=date.today(), key="fecha_inv_emp")
    with col2:
        tipo_inventario = st.selectbox(
            "Tipo de inventario", 
            ["Diario", "Semanal", "Quincenal"], 
            key="tipo_inventario_emp"
        )

    # Cargar inventario desde archivo
    try:
        inventario_actual = cargar_inventario(tienda_id, fecha_carga)
        if not inventario_actual or all(not productos for productos in inventario_actual.values()):
            inventario_actual = PRODUCTOS_BASE.copy()
            st.warning("🔄 Usando estructura de productos por defecto")
    except Exception as e:
        st.error(f"Error cargando inventario: {e}")
        inventario_actual = PRODUCTOS_BASE.copy()
        st.warning("🔄 Usando estructura de productos por defecto")

    # Función para agregar al carrito temporal
    def agregar_al_carrito(entrada):
        """Agrega producto al carrito temporal"""
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
            
            total_productos = len(st.session_state.carrito_temporal)
            
            # Crear barra de progreso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Procesar cada producto del carrito
            for idx, entrada in enumerate(st.session_state.carrito_temporal):
                # Actualizar progreso
                progreso = (idx + 1) / total_productos
                progress_bar.progress(progreso)
                status_text.text(f"Guardando {entrada['producto']} ({idx + 1}/{total_productos})")
                
                # Estructurar datos para guardar
                inventario_entrada = {
                    entrada['categoria']: {
                        entrada['producto']: entrada['cantidad']
                    }
                }
                
                # Guardar en inventario
                if not guardar_inventario(inventario_entrada, tienda_id, fecha_carga):
                    st.error(f"❌ Error guardando {entrada['producto']}")
                    continue
                
                # Guardar en historial con más información
                entrada_historial = {
                    'fecha': str(fecha_carga),
                    'hora': datetime.now().strftime("%H:%M:%S"),
                    'usuario': usuario,
                    'tipo_inventario': tipo_inventario,
                    'categoria': entrada['categoria'],
                    'producto': entrada['producto'],
                    'cantidad': entrada['cantidad'],
                    'accion': 'carga_inventario'
                }
                
                guardar_historial(entrada_historial, tienda_id)
            
            # Limpiar progreso
            progress_bar.empty()
            status_text.empty()
            
            # Limpiar carrito después de guardar exitosamente
            st.session_state.carrito_temporal = []
            st.session_state.fecha_ultima_carga = str(fecha_carga)
            
            st.success(f"✅ {total_productos} productos guardados exitosamente")
            return True
            
        except Exception as e:
            st.error(f"❌ Error guardando carrito: {str(e)}")
            return False
        finally:
            st.session_state.esta_guardando = False

    # Función para validar y convertir números
    def validar_numero(valor, tipo="int"):
        """Valida y convierte números de forma segura"""
        try:
            if tipo == "int":
                return max(0, int(float(valor) if valor else 0))
            elif tipo == "float":
                return max(0.0, float(valor if valor else 0))
        except (ValueError, TypeError):
            return 0 if tipo == "int" else 0.0

    # Inicializar valores en session_state si no existen
    if 'valores_impulsivo' not in st.session_state:
        st.session_state.valores_impulsivo = {}
    if 'valores_kilos' not in st.session_state:
        st.session_state.valores_kilos = {}
    if 'valores_extras' not in st.session_state:
        st.session_state.valores_extras = {}

    # Mostrar formularios por categoría
    st.subheader("📋 Cargar Inventario")
    
    # Crear tabs para cada categoría
    tab1, tab2, tab3 = st.tabs(["🍦 Impulsivo", "⚖️ Por Kilos", "🛍️ Extras"])
    
    # TAB IMPULSIVO
    with tab1:
        st.markdown("### 🍦 Productos Impulsivos")
        productos_impulsivo = inventario_actual.get("Impulsivo", {})
        
        st.markdown("**Selecciona productos impulsivos:**")
        
        col1, col2 = st.columns(2)
        productos_seleccionados = {}
        
        productos_lista = list(PRODUCTOS_BASE["Impulsivo"].keys())
        mitad = len(productos_lista) // 2
        
        with col1:
            for producto in productos_lista[:mitad]:
                cantidad_actual = productos_impulsivo.get(producto, 0)
                # Obtener valor guardado o 0
                valor_guardado = st.session_state.valores_impulsivo.get(producto, 0)
                cantidad = st.number_input(
                    f"{producto} (actual: {cantidad_actual})",
                    min_value=0,
                    value=valor_guardado,
                    step=1,
                    key=f"imp_{producto}_emp",
                    help=f"Cantidad actual en inventario: {cantidad_actual}"
                )
                # Guardar valor en session_state
                st.session_state.valores_impulsivo[producto] = cantidad
                if cantidad > 0:
                    productos_seleccionados[producto] = validar_numero(cantidad, "int")
        
        with col2:
            for producto in productos_lista[mitad:]:
                cantidad_actual = productos_impulsivo.get(producto, 0)
                # Obtener valor guardado o 0
                valor_guardado = st.session_state.valores_impulsivo.get(producto, 0)
                cantidad = st.number_input(
                    f"{producto} (actual: {cantidad_actual})",
                    min_value=0,
                    value=valor_guardado,
                    step=1,
                    key=f"imp2_{producto}_emp",
                    help=f"Cantidad actual en inventario: {cantidad_actual}"
                )
                # Guardar valor en session_state
                st.session_state.valores_impulsivo[producto] = cantidad
                if cantidad > 0:
                    productos_seleccionados[producto] = validar_numero(cantidad, "int")
        
        # Botón de envío (fuera del formulario)
        if st.button("➕ Agregar al Carrito", use_container_width=True, key="btn_impulsivo"):
            if productos_seleccionados:
                # Agregar productos seleccionados al carrito
                productos_agregados = 0
                for producto, cantidad in productos_seleccionados.items():
                    if cantidad > 0:
                        entrada = {
                            'categoria': 'Impulsivo',
                            'producto': producto,
                            'cantidad': cantidad,
                            'fecha': str(fecha_carga),
                            'usuario': usuario
                        }
                        if agregar_al_carrito(entrada):
                            productos_agregados += 1
                
                if productos_agregados > 0:
                    st.success(f"✅ {productos_agregados} productos agregados al carrito")
                    st.rerun()
            else:
                st.warning("⚠️ Selecciona al menos un producto con cantidad mayor a 0")

    # TAB POR KILOS
    with tab2:
        st.markdown("### ⚖️ Productos por Kilos")
        productos_kilos = inventario_actual.get("Por Kilos", {})
        
        st.markdown("**Selecciona productos por kilos:**")
        
        col1, col2 = st.columns(2)
        productos_seleccionados_kilos = {}
        
        productos_lista_kilos = list(PRODUCTOS_BASE["Por Kilos"].keys())
        mitad_kilos = len(productos_lista_kilos) // 2
        
        with col1:
            for producto in productos_lista_kilos[:mitad_kilos]:
                cantidad_actual = productos_kilos.get(producto, 0)
                # Obtener valor guardado o 0
                valor_guardado = st.session_state.valores_kilos.get(producto, 0.0)
                cantidad = st.number_input(
                    f"{producto} (actual: {cantidad_actual} kg)",
                    min_value=0.0,
                    value=valor_guardado,
                    step=0.1,
                    format="%.1f",
                    key=f"kilos_{producto}_emp",
                    help=f"Cantidad actual en inventario: {cantidad_actual} kg"
                )
                # Guardar valor en session_state
                st.session_state.valores_kilos[producto] = cantidad
                if cantidad > 0:
                    productos_seleccionados_kilos[producto] = validar_numero(cantidad, "float")
        
        with col2:
            for producto in productos_lista_kilos[mitad_kilos:]:
                cantidad_actual = productos_kilos.get(producto, 0)
                # Obtener valor guardado o 0
                valor_guardado = st.session_state.valores_kilos.get(producto, 0.0)
                cantidad = st.number_input(
                    f"{producto} (actual: {cantidad_actual} kg)",
                    min_value=0.0,
                    value=valor_guardado,
                    step=0.1,
                    format="%.1f",
                    key=f"kilos2_{producto}_emp",
                    help=f"Cantidad actual en inventario: {cantidad_actual} kg"
                )
                # Guardar valor en session_state
                st.session_state.valores_kilos[producto] = cantidad
                if cantidad > 0:
                    productos_seleccionados_kilos[producto] = validar_numero(cantidad, "float")
        
        # Botón de envío (fuera del formulario)
        if st.button("➕ Agregar al Carrito", use_container_width=True, key="btn_kilos"):
            if productos_seleccionados_kilos:
                # Agregar productos seleccionados al carrito
                productos_agregados = 0
                for producto, cantidad in productos_seleccionados_kilos.items():
                    if cantidad > 0:
                        entrada = {
                            'categoria': 'Por Kilos',
                            'producto': producto,
                            'cantidad': cantidad,
                            'fecha': str(fecha_carga),
                            'usuario': usuario
                        }
                        if agregar_al_carrito(entrada):
                            productos_agregados += 1
                
                if productos_agregados > 0:
                    st.success(f"✅ {productos_agregados} productos agregados al carrito")
                    st.rerun()
            else:
                st.warning("⚠️ Selecciona al menos un producto con cantidad mayor a 0")

    # TAB EXTRAS
    with tab3:
        st.markdown("### 🛍️ Productos Extras")
        productos_extras = inventario_actual.get("Extras", {})
        
        st.markdown("**Selecciona productos extras:**")
        
        col1, col2 = st.columns(2)
        productos_seleccionados_extras = {}
        
        productos_lista_extras = list(PRODUCTOS_BASE["Extras"].keys())
        mitad_extras = len(productos_lista_extras) // 2
        
        with col1:
            for producto in productos_lista_extras[:mitad_extras]:
                cantidad_actual = productos_extras.get(producto, 0)
                # Obtener valor guardado o 0
                valor_guardado = st.session_state.valores_extras.get(producto, 0)
                cantidad = st.number_input(
                    f"{producto} (actual: {cantidad_actual})",
                    min_value=0,
                    value=valor_guardado,
                    step=1,
                    key=f"extra_{producto}_emp",
                    help=f"Cantidad actual en inventario: {cantidad_actual}"
                )
                # Guardar valor en session_state
                st.session_state.valores_extras[producto] = cantidad
                if cantidad > 0:
                    productos_seleccionados_extras[producto] = validar_numero(cantidad, "int")
        
        with col2:
            for producto in productos_lista_extras[mitad_extras:]:
                cantidad_actual = productos_extras.get(producto, 0)
                # Obtener valor guardado o 0
                valor_guardado = st.session_state.valores_extras.get(producto, 0)
                cantidad = st.number_input(
                    f"{producto} (actual: {cantidad_actual})",
                    min_value=0,
                    value=valor_guardado,
                    step=1,
                    key=f"extra2_{producto}_emp",
                    help=f"Cantidad actual en inventario: {cantidad_actual}"
                )
                # Guardar valor en session_state
                st.session_state.valores_extras[producto] = cantidad
                if cantidad > 0:
                    productos_seleccionados_extras[producto] = validar_numero(cantidad, "int")
        
        # Botón de envío (fuera del formulario)
        if st.button("➕ Agregar al Carrito", use_container_width=True, key="btn_extras"):
            if productos_seleccionados_extras:
                # Agregar productos seleccionados al carrito
                productos_agregados = 0
                for producto, cantidad in productos_seleccionados_extras.items():
                    if cantidad > 0:
                        entrada = {
                            'categoria': 'Extras',
                            'producto': producto,
                            'cantidad': cantidad,
                            'fecha': str(fecha_carga),
                            'usuario': usuario
                        }
                        if agregar_al_carrito(entrada):
                            productos_agregados += 1
                
                if productos_agregados > 0:
                    st.success(f"✅ {productos_agregados} productos agregados al carrito")
                    st.rerun()
            else:
                st.warning("⚠️ Selecciona al menos un producto con cantidad mayor a 0")

    # Mostrar información del carrito actual (AL FINAL)
    if st.session_state.carrito_temporal:
        st.divider()
        st.subheader("📦 Inventario Cargado")
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.info(f"📦 **{len(st.session_state.carrito_temporal)} productos** listos para guardar")
        
        with col2:
            if st.button("💾 Guardar Todo", type="primary", disabled=st.session_state.esta_guardando):
                if guardar_carrito_completo():
                    st.rerun()
        
        with col3:
            if st.button("🗑️ Limpiar Carrito"):
                st.session_state.carrito_temporal = []
                st.rerun()
        
        # Mostrar productos en el carrito
        with st.expander("👀 Ver productos cargados", expanded=False):
            for item in st.session_state.carrito_temporal:
                st.write(f"- **{item['categoria']}** → {item['producto']}: {item['cantidad']}")

    # Mostrar resumen del inventario actual
    if st.checkbox("📊 Ver resumen del inventario actual"):
        st.subheader("📊 Resumen del Inventario")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🍦 Impulsivo")
            productos_imp = inventario_actual.get("Impulsivo", {})
            productos_con_stock = [v for v in productos_imp.values() if isinstance(v, (int, float)) and v > 0]
            total_imp = sum(productos_con_stock)
            st.metric("Productos con stock", len(productos_con_stock))
            st.metric("Cantidad total", int(total_imp))
        
        with col2:
            st.markdown("#### ⚖️ Por Kilos")
            productos_kg = inventario_actual.get("Por Kilos", {})
            productos_con_stock_kg = [v for v in productos_kg.values() if isinstance(v, (int, float)) and v > 0]
            total_kg = sum(productos_con_stock_kg)
            st.metric("Productos con stock", len(productos_con_stock_kg))
            st.metric("Cantidad total (kg)", f"{total_kg:.1f}")
        
        with col3:
            st.markdown("#### 🛍️ Extras")
            productos_ext = inventario_actual.get("Extras", {})
            productos_con_stock_ext = [v for v in productos_ext.values() if isinstance(v, (int, float)) and v > 0]
            total_ext = sum(productos_con_stock_ext)
            st.metric("Productos con stock", len(productos_con_stock_ext))
            st.metric("Cantidad total", int(total_ext))

    return True