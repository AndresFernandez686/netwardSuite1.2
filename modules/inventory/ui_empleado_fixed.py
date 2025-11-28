# UI y lógica de empleados (Inventario) - Versión BusinessSuite Corregida
import streamlit as st
from datetime import date, datetime
from .config_tiendas import selector_tienda_empleado, GestorTiendas, obtener_nombre_tienda
from .persistencia import cargar_inventario, guardar_inventario, guardar_historial
from .valores_persistencia import valores_persistencia

# Configuración para mejorar rendimiento
st.set_page_config(page_title="Inventario", layout="wide")

# Estructura completa de productos por defecto - CATÁLOGO CONSOLIDADO CON BULTOS Y UNIDADES
PRODUCTOS_BASE = {
    "Impulsivo": {
        # Alfajores - Individuales con sus cajas
        "Alfajor Almendrado": {"bultos": 0, "unidad": 0},
        "Almendrado en Caja x 8": {"bultos": 0, "unidad": 0},
        "Alfajor Bombon Cookies and Crema": {"bultos": 0, "unidad": 0},
        "Bombon cookies and cream caja x 8": {"bultos": 0, "unidad": 0},
        "Alfajor Bombon Crocante": {"bultos": 0, "unidad": 0},
        "Bombon Crocante Caja x 8": {"bultos": 0, "unidad": 0},
        "Alfajor Bombon Escoces": {"bultos": 0, "unidad": 0},
        "Bombon Escoces en Caja x 8": {"bultos": 0, "unidad": 0},
        "Alfajor Bombon Suizo": {"bultos": 0, "unidad": 0},
        "Bombon Suizo en Caja x 8": {"bultos": 0, "unidad": 0},
        "Alfajor Bombon Vainilla": {"bultos": 0, "unidad": 0},
        "Alfajor Casatta": {"bultos": 0, "unidad": 0},
        # Bocaditos
        "Bocaditos Frambuesa": {"bultos": 0, "unidad": 0},
        "Bocaditos Frutilla": {"bultos": 0, "unidad": 0},
        # Productos especiales
        "Crocantino": {"bultos": 0, "unidad": 0},
        "Delicia": {"bultos": 0, "unidad": 0},
        "Familiar 1": {"bultos": 0, "unidad": 0},
        "Familiar 2": {"bultos": 0, "unidad": 0},
        "Familiar 3": {"bultos": 0, "unidad": 0},
        "Familiar 4": {"bultos": 0, "unidad": 0},
        "Grido Toy": {"bultos": 0, "unidad": 0},
        # Helados sin azúcar
        "Helado sin Azucar chocolate sin Tacc": {"bultos": 0, "unidad": 0},
        "Helado sin Azucar Durazno a la Crema": {"bultos": 0, "unidad": 0},
        "Helado sin Azucar Frutilla a la Crema": {"bultos": 0, "unidad": 0},
        # Palitos - Individuales con sus cajas
        "Palito Bombon": {"bultos": 0, "unidad": 0},
        "Palito Bombon Caja x10": {"bultos": 0, "unidad": 0},
        "Palito Crema Americana": {"bultos": 0, "unidad": 0},
        "Palito Crema Americana Caja x10": {"bultos": 0, "unidad": 0},
        "Palito Crema Frutilla": {"bultos": 0, "unidad": 0},
        "Palito Crema Frutilla Caja x10": {"bultos": 0, "unidad": 0},
        "Palito Frutal Frutilla": {"bultos": 0, "unidad": 0},
        "Palito Frutal Frutilla Caja x10": {"bultos": 0, "unidad": 0},
        "Palito Frutal Limon": {"bultos": 0, "unidad": 0},
        "Palito Frutal Limon Caja x10": {"bultos": 0, "unidad": 0},
        "Palito Frutal Naranja": {"bultos": 0, "unidad": 0},
        "Palito Frutal Naranja Caja x10": {"bultos": 0, "unidad": 0},
        "Pizza": {"bultos": 0, "unidad": 0},
        # Tentaciones
        "Tentacion Chocolate": {"bultos": 0, "unidad": 0},
        "Tentacion Chocolate con Almendra": {"bultos": 0, "unidad": 0},
        "Tentacion Cookies": {"bultos": 0, "unidad": 0},
        "Tentacion Crema Americana": {"bultos": 0, "unidad": 0},
        "Tentacion Dulce de Leche": {"bultos": 0, "unidad": 0},
        "Tentacion Dulce de Leche Granizado": {"bultos": 0, "unidad": 0},
        "Tentacion Frutilla": {"bultos": 0, "unidad": 0},
        "Tentacion Granizado": {"bultos": 0, "unidad": 0},
        "Tentacion Limon": {"bultos": 0, "unidad": 0},
        "Tentacion Mascarpone": {"bultos": 0, "unidad": 0},
        "Tentacion Menta Granizada": {"bultos": 0, "unidad": 0},
        "Tentacion Toddy": {"bultos": 0, "unidad": 0},
        "Tentacion Vainilla": {"bultos": 0, "unidad": 0},
        # Tortas
        "Torta Grido Rellena": {"bultos": 0, "unidad": 0},
        "Torta Milka": {"bultos": 0, "unidad": 0},
        # Yogurt helado
        "Yogurt Helado Frutos del Bosque sin Tacc": {"bultos": 0, "unidad": 0},
        "Yogurt Helado Frutilla sin Tacc": {"bultos": 0, "unidad": 0},
        "Yogurt Helado Mango Maracuya": {"bultos": 0, "unidad": 0},
    },
    "Por Kilos": {
        # Ordenados alfabéticamente
        "Almendras": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Anana a la crema": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Banana con Dulce de leche": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Brownie": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Candy": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Capuccino Granizado": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Cereza": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Choco Granita": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Chocolate": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Chocolate Blanco": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Chocolate con Almendra": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Chocolate Mani Crunch": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Chocolate Suizo": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Cookies": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Crema Americana": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Crema Cookie": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Crema Rusa": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Dulce de Leche": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Dulce de Leche con Brownie": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Dulce de Leche con Nuez": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Dulce de Leche Especial": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Dulce de Leche Granizado": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Durazno a la Crema": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Flan": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Fresa": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Frutilla a la Crema": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Frutos Rojos al Agua": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Granita de Café": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Granizado": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Kinotos al Whisky": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Limón": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Limon al Agua": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Maracuya": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Marroc Grido": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Mascarpone con Frutos del Bosque": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Menta Granizada": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Naranja Helado al Agua": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Pistacho": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Sambayón": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Super Gridito": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Tiramisu": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Tramontana": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
        "Vainilla": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0},
    },
    "Extras": {
        # Coberturas
        "Cobertura Chocolate": {"bultos": 0, "unidad": 0},
        "Cobertura Dulce de Leche": {"bultos": 0, "unidad": 0},
        "Cobertura Frutilla": {"bultos": 0, "unidad": 0},
        # Productos básicos
        "Leche": {"bultos": 0, "unidad": 0},
        "Cuchara Sunday": {"bultos": 0, "unidad": 0},
        "Cucharita Grido": {"bultos": 0, "unidad": 0},
        # Cucuruchos
        "Cucurucho Biscoito Dulce x300": {"bultos": 0, "unidad": 0},
        "Cucurucho Cascao x120": {"bultos": 0, "unidad": 0},
        "Cucurucho Nacional x54": {"bultos": 0, "unidad": 0},
        # Gas e isopor
        "Garrafita de Gas": {"bultos": 0, "unidad": 0},
        "Isopor 1 kilo": {"bultos": 0, "unidad": 0},
        "Isopor 1/2 kilo": {"bultos": 0, "unidad": 0},
        "Isopor 1/4": {"bultos": 0, "unidad": 0},
        # Accesorios
        "Mani tostado": {"bultos": 0, "unidad": 0},
        "Pajita con Funda": {"bultos": 0, "unidad": 0},
        "Servilleta Grido": {"bultos": 0, "unidad": 0},
        # Tapas
        "Tapa Burbuja Capuccino": {"bultos": 0, "unidad": 0},
        "Tapa Burbuja Batido": {"bultos": 0, "unidad": 0},
        # Vasos
        "Vaso capuccino": {"bultos": 0, "unidad": 0},
        "Vaso Batido": {"bultos": 0, "unidad": 0},
        "Vasito de una Bocha": {"bultos": 0, "unidad": 0},
        "Vaso Termico 240gr": {"bultos": 0, "unidad": 0},
        "Vaso Sundae": {"bultos": 0, "unidad": 0},
        # Otros
        "Rollo Termico": {"bultos": 0, "unidad": 0},
        "Cinta Grido": {"bultos": 0, "unidad": 0},
        "Bolsa 40x50": {"bultos": 0, "unidad": 0},
    }
}

def mostrar_interfaz_empleado(inventario=None, usuario="empleado1", opciones_valde=None, tienda_id="T001"):
    """Interfaz principal para empleados con formularios correctos y manejo de errores"""
    
    # Agregar estilos CSS profesionales
    st.markdown("""
    <style>
    .producto-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .producto-guardado {
        border-left: 4px solid #28a745;
        background-color: #d4edda;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .producto-carrito {
        border-left: 4px solid #ffa500;
        background-color: #fff3cd;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .producto-vacio {
        border-left: 4px solid #6c757d;
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .carrito-badge {
        background-color: #dc3545;
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Obtener nombre de la tienda
    nombre_tienda = obtener_nombre_tienda(tienda_id)
    
    st.header(f"📦 Inventario - 🏪 {nombre_tienda}")
    st.caption(f"Usuario: {usuario} | Tienda ID: {tienda_id}")
    
    # Inicializar estados de sesión
    if 'carrito_temporal' not in st.session_state:
        st.session_state.carrito_temporal = []
    
    if 'esta_guardando' not in st.session_state:
        st.session_state.esta_guardando = False
    
    if 'fecha_ultima_carga' not in st.session_state:
        st.session_state.fecha_ultima_carga = None
    
    # Cargar valores persistidos del formulario (vigentes por 1 día)
    if 'valores_cargados' not in st.session_state:
        fecha_carga = date.today()
        valores_guardados = valores_persistencia.cargar_valores(usuario, tienda_id, fecha_carga)
        st.session_state.valores_impulsivo = valores_guardados.get('valores_impulsivo', {})
        st.session_state.valores_kilos = valores_guardados.get('valores_kilos', {})
        st.session_state.valores_extras = valores_guardados.get('valores_extras', {})
        st.session_state.valores_cargados = True
        
        # Mostrar mensaje si se cargaron valores
        if valores_guardados.get('valores_impulsivo') or valores_guardados.get('valores_kilos') or valores_guardados.get('valores_extras'):
            st.success("✅ Se recuperaron los valores del último inventario cargado (vigente por 24 horas)")

    # Tipo de inventario (sin selector de fecha)
    tipo_inventario = st.selectbox(
        "Tipo de inventario", 
        ["Diario", "Semanal", "Quincenal"], 
        key="tipo_inventario_emp"
    )
    
    # Usar fecha actual automáticamente
    fecha_carga = date.today()

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
                # La función guardar_historial espera: fecha, usuario, categoria, producto, cantidad, modo, tipo_inventario, tienda_id
                guardar_historial(
                    fecha=str(fecha_carga),
                    usuario=usuario,
                    categoria=entrada['categoria'],
                    producto=entrada['producto'],
                    cantidad=str(entrada['cantidad']),
                    modo='carga_inventario',
                    tipo_inventario=tipo_inventario,
                    tienda_id=tienda_id
                )
            
            # Limpiar progreso
            progress_bar.empty()
            status_text.empty()
            
            # NO limpiar carrito - mantener productos visibles
            # Guardar fecha de última carga para verificación
            st.session_state.fecha_ultima_carga = str(fecha_carga)
            
            # Marcar que los productos fueron guardados
            for entrada in st.session_state.carrito_temporal:
                entrada['guardado'] = True
                entrada['fecha_guardado'] = str(fecha_carga)
            
            st.success(f"✅ {total_productos} productos guardados y actualizados")
            return True
            
        except Exception as e:
            st.error(f"❌ Error guardando carrito: {str(e)}")
            return False
        finally:
            st.session_state.esta_guardando = False

    # SISTEMA DE VALORES LÓGICO PARA SUGERENCIAS:
    # ============================================
    # None = Producto NO se carga en la tienda (no se compra)
    # 0    = Producto se carga pero SIN STOCK (se compra, está agotado)
    # > 0  = Cantidad en stock del producto
    # 
    # Esto permite el sistema de sugerencias diferenciar:
    # - Productos que deberían comprarse pero no hay (sugerir reorden)
    # - Productos que nunca se compran en esa tienda (ignorar en sugerencias)

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

    # Mostrar formularios por categoría
    st.subheader("📋 Cargar Inventario")
    
    # Crear tabs para cada categoría
    tab1, tab2, tab3 = st.tabs(["🍦 Impulsivo", "⚖️ Por Kilos", "🛍️ Extras"])
    
    # TAB IMPULSIVO
    with tab1:
        st.markdown("### 🍦 Productos Impulsivos")
        productos_impulsivo = inventario_actual.get("Impulsivo", {})
        
        st.markdown("**Carga por Bultos y Unidades:**")
        
        # Usar form para agrupar inputs y evitar re-renders constantes
        with st.form("form_impulsivo", clear_on_submit=False):
            col1, sep, col2 = st.columns([10, 0.5, 10])
            productos_seleccionados = {}
            
            productos_lista = list(PRODUCTOS_BASE["Impulsivo"].keys())
            mitad = len(productos_lista) // 2
            
            with sep:
                st.markdown(
                    "<div style='height: 100%; border-left: 2px solid #333; margin: 0 auto;'></div>",
                    unsafe_allow_html=True
                )
            
            with col1:
                for producto in productos_lista[:mitad]:
                    # Obtener valores actuales
                    valores_actuales = productos_impulsivo.get(producto, {"bultos": 0, "unidad": 0})
                    if isinstance(valores_actuales, (int, float)):
                        valores_actuales = {"bultos": 0, "unidad": int(valores_actuales)}
                    
                    bultos_actual = valores_actuales.get("bultos", 0)
                    unidad_actual = valores_actuales.get("unidad", 0)
                    
                    # Obtener valores guardados en sesión
                    if producto not in st.session_state.valores_impulsivo:
                        st.session_state.valores_impulsivo[producto] = {"bultos": None, "unidad": None}
                    
                    st.markdown(f"**{producto}** (📦: {bultos_actual}, 📋: {unidad_actual})")
                    col_bultos, col_unidad = st.columns(2)
                    
                    with col_bultos:
                        # Usar None para campo vacío, no 0
                        valor_actual = st.session_state.valores_impulsivo[producto]["bultos"]
                        bultos = st.number_input(
                            "📦 Bultos",
                            min_value=0,
                            value=valor_actual if valor_actual is not None else 0,
                            step=1,
                            key=f"imp_bultos_{producto}_emp",
                            placeholder="Bultos"
                        )
                        # Guardar: si usuario cambió de 0, guardar el valor; si dejó 0, mantener None
                        if st.session_state.valores_impulsivo[producto]["bultos"] is None and bultos == 0:
                            st.session_state.valores_impulsivo[producto]["bultos"] = None  # Sigue siendo "no cargado"
                        else:
                            st.session_state.valores_impulsivo[producto]["bultos"] = bultos if bultos > 0 else 0
                    
                    with col_unidad:
                        # Usar None para campo vacío, no 0
                        valor_actual = st.session_state.valores_impulsivo[producto]["unidad"]
                        unidad = st.number_input(
                            "📋 Unidad",
                            min_value=0,
                            value=valor_actual if valor_actual is not None else 0,
                            step=1,
                            key=f"imp_unidad_{producto}_emp",
                            placeholder="Unidades"
                        )
                        if st.session_state.valores_impulsivo[producto]["unidad"] is None and unidad == 0:
                            st.session_state.valores_impulsivo[producto]["unidad"] = None
                        else:
                            st.session_state.valores_impulsivo[producto]["unidad"] = unidad if unidad > 0 else 0
                    
                    # Agregar si NO es None (puede ser 0 = sin stock)
                    if st.session_state.valores_impulsivo[producto]["bultos"] is not None or st.session_state.valores_impulsivo[producto]["unidad"] is not None:
                        productos_seleccionados[producto] = {"bultos": st.session_state.valores_impulsivo[producto]["bultos"] or 0, "unidad": st.session_state.valores_impulsivo[producto]["unidad"] or 0}
                    
                    st.markdown("---")
            
            with col2:
                for producto in productos_lista[mitad:]:
                    # Obtener valores actuales
                    valores_actuales = productos_impulsivo.get(producto, {"bultos": 0, "unidad": 0})
                    if isinstance(valores_actuales, (int, float)):
                        valores_actuales = {"bultos": 0, "unidad": int(valores_actuales)}
                    
                    bultos_actual = valores_actuales.get("bultos", 0)
                    unidad_actual = valores_actuales.get("unidad", 0)
                    
                    # Obtener valores guardados en sesión
                    if producto not in st.session_state.valores_impulsivo:
                        st.session_state.valores_impulsivo[producto] = {"bultos": None, "unidad": None}
                    
                    st.markdown(f"**{producto}** (📦: {bultos_actual}, 📋: {unidad_actual})")
                    col_bultos, col_unidad = st.columns(2)
                    
                    with col_bultos:
                        valor_actual = st.session_state.valores_impulsivo[producto]["bultos"]
                        bultos = st.number_input(
                            "📦 Bultos",
                            min_value=0,
                            value=valor_actual if valor_actual is not None else 0,
                            step=1,
                            key=f"imp2_bultos_{producto}_emp",
                            placeholder="Bultos"
                        )
                        # Guardar: si usuario cambió de 0, guardar el valor; si dejó 0, mantener None
                        if st.session_state.valores_impulsivo[producto]["bultos"] is None and bultos == 0:
                            st.session_state.valores_impulsivo[producto]["bultos"] = None
                        else:
                            st.session_state.valores_impulsivo[producto]["bultos"] = bultos if bultos > 0 else 0
                    
                    with col_unidad:
                        valor_actual = st.session_state.valores_impulsivo[producto]["unidad"]
                        unidad = st.number_input(
                            "📋 Unidad",
                            min_value=0,
                            value=valor_actual if valor_actual is not None else 0,
                            step=1,
                            key=f"imp2_unidad_{producto}_emp",
                            placeholder="Unidades"
                        )
                        # Guardar: si usuario cambió de 0, guardar el valor; si dejó 0, mantener None
                        if st.session_state.valores_impulsivo[producto]["unidad"] is None and unidad == 0:
                            st.session_state.valores_impulsivo[producto]["unidad"] = None
                        else:
                            st.session_state.valores_impulsivo[producto]["unidad"] = unidad if unidad > 0 else 0
                    
                    # Agregar si NO es None (puede ser 0 = sin stock)
                    if st.session_state.valores_impulsivo[producto]["bultos"] is not None or st.session_state.valores_impulsivo[producto]["unidad"] is not None:
                        productos_seleccionados[producto] = {"bultos": st.session_state.valores_impulsivo[producto]["bultos"] or 0, "unidad": st.session_state.valores_impulsivo[producto]["unidad"] or 0}
                    
                    st.markdown("---")
            
            # Botón de envío dentro del formulario
            submitted = st.form_submit_button("➕ Agregar al Carrito", use_container_width=True)
        
        # Procesar el formulario cuando se envía
        if submitted:
            if productos_seleccionados:
                # Agregar productos seleccionados al carrito
                productos_agregados = 0
                for producto, valores in productos_seleccionados.items():
                    entrada = {
                        'categoria': 'Impulsivo',
                        'producto': producto,
                        'cantidad': valores,  # Ahora es un dict con bultos y unidad
                        'fecha': str(fecha_carga),
                        'usuario': usuario
                    }
                    if agregar_al_carrito(entrada):
                        productos_agregados += 1
                
                if productos_agregados > 0:
                    # Guardar valores para persistencia (vigente por 1 día)
                    valores_persistencia.guardar_valores(
                        usuario, tienda_id, fecha_carga,
                        st.session_state.valores_impulsivo,
                        st.session_state.valores_kilos,
                        st.session_state.valores_extras
                    )
                    st.success(f"✅ {productos_agregados} productos agregados al carrito")
                    st.rerun()
            else:
                st.warning("⚠️ Selecciona al menos un producto con algún valor cargado")

    # TAB POR KILOS
    with tab2:
        st.markdown("### ⚖️ Productos Por Kilos")
        productos_kilos = inventario_actual.get("Por Kilos", {})
        
        st.markdown("**Carga: Cajas Cerradas | Cajas Abiertas | Kgs Cajas Abiertas**")
        
        # Usar form para mejorar rendimiento
        with st.form("form_kilos", clear_on_submit=False):
            col1, sep, col2 = st.columns([10, 0.5, 10])
            productos_seleccionados_kilos = {}
            productos_lista_kilos = sorted(list(PRODUCTOS_BASE["Por Kilos"].keys()))
            mitad_kilos = len(productos_lista_kilos) // 2
            
            with sep:
                st.markdown(
                    "<div style='height: 100%; border-left: 2px solid #333; margin: 0 auto;'></div>",
                    unsafe_allow_html=True
                )
            
            # Columna 1
            with col1:
                for producto in productos_lista_kilos[:mitad_kilos]:
                    # Obtener valores actuales
                    valores_actuales = productos_kilos.get(producto, {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0})
                    if isinstance(valores_actuales, (int, float)):
                        valores_actuales = {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": float(valores_actuales)}
                    
                    cajas_cerradas_actual = valores_actuales.get("cajas_cerradas", 0)
                    cajas_abiertas_actual = valores_actuales.get("cajas_abiertas", 0)
                    kgs_abiertas_actual = valores_actuales.get("kgs_cajas_abiertas", 0.0)
                    
                    # Obtener valores guardados en sesión
                    if producto not in st.session_state.valores_kilos:
                        st.session_state.valores_kilos[producto] = {"cajas_cerradas": None, "cajas_abiertas": None, "kgs_cajas_abiertas": None}
                    
                    # Total en kg
                    total_kg = (cajas_cerradas_actual * 7.8) + kgs_abiertas_actual
                    # Formato europeo: reemplazar punto por coma
                    total_kg_formatted = f"{total_kg:.3f}".replace(".", ",")
                    
                    st.markdown(f"**{producto}** (Total: {total_kg_formatted} kg)")
                    col_cerradas, col_abiertas, col_kgs = st.columns([1, 1, 1.2])
                    
                    with col_cerradas:
                        st.markdown("<div style='text-align: center; font-size: 12px; color: #666;'>Cajas Cerradas</div>", unsafe_allow_html=True)
                        val_cc = st.session_state.valores_kilos[producto]["cajas_cerradas"]
                        cajas_cerradas = st.number_input(
                            "Cajas Cerradas",
                            min_value=0,
                            value=val_cc if val_cc is not None else 0,
                            step=1,
                            key=f"kilos_cerradas_{producto}_emp",
                            label_visibility="collapsed",
                            placeholder="Cajas"
                        )
                        if st.session_state.valores_kilos[producto]["cajas_cerradas"] is None and cajas_cerradas == 0:
                            st.session_state.valores_kilos[producto]["cajas_cerradas"] = None
                        else:
                            st.session_state.valores_kilos[producto]["cajas_cerradas"] = cajas_cerradas
                    
                    with col_abiertas:
                        st.markdown("<div style='text-align: center; font-size: 12px; color: #666;'>Cajas Abiertas</div>", unsafe_allow_html=True)
                        val_ca = st.session_state.valores_kilos[producto]["cajas_abiertas"]
                        cajas_abiertas = st.number_input(
                            "Cajas Abiertas",
                            min_value=0,
                            value=val_ca if val_ca is not None else 0,
                            step=1,
                            key=f"kilos_abiertas_{producto}_emp",
                            label_visibility="collapsed",
                            placeholder="Cajas"
                        )
                        if st.session_state.valores_kilos[producto]["cajas_abiertas"] is None and cajas_abiertas == 0:
                            st.session_state.valores_kilos[producto]["cajas_abiertas"] = None
                        else:
                            st.session_state.valores_kilos[producto]["cajas_abiertas"] = cajas_abiertas
                    
                    with col_kgs:
                        st.markdown("<div style='text-align: center; font-size: 12px; color: #666;'>Kgs Cajas Abiertas</div>", unsafe_allow_html=True)
                        val_kg = st.session_state.valores_kilos[producto]["kgs_cajas_abiertas"]
                        kgs_abiertas = st.number_input(
                            "Kgs Cajas Abiertas",
                            min_value=0.0,
                            max_value=7.8 * (st.session_state.valores_kilos[producto]["cajas_abiertas"] or 0) if st.session_state.valores_kilos[producto]["cajas_abiertas"] else 7.8,
                            value=val_kg if val_kg is not None else 0.0,
                            step=0.1,
                            format="%.3f",
                            key=f"kilos_kgs_{producto}_emp",
                            label_visibility="collapsed",
                            placeholder="Kgs"
                        )
                        if st.session_state.valores_kilos[producto]["kgs_cajas_abiertas"] is None and kgs_abiertas == 0.0:
                            st.session_state.valores_kilos[producto]["kgs_cajas_abiertas"] = None
                        else:
                            st.session_state.valores_kilos[producto]["kgs_cajas_abiertas"] = kgs_abiertas
                    
                    # Agregar si cualquiera de los valores no es None (puede ser 0 = sin stock)
                    if (st.session_state.valores_kilos[producto]["cajas_cerradas"] is not None or 
                        st.session_state.valores_kilos[producto]["cajas_abiertas"] is not None or 
                        st.session_state.valores_kilos[producto]["kgs_cajas_abiertas"] is not None):
                        productos_seleccionados_kilos[producto] = {
                            "cajas_cerradas": st.session_state.valores_kilos[producto]["cajas_cerradas"] or 0,
                            "cajas_abiertas": st.session_state.valores_kilos[producto]["cajas_abiertas"] or 0,
                            "kgs_cajas_abiertas": st.session_state.valores_kilos[producto]["kgs_cajas_abiertas"] or 0.0
                        }
                    
                    st.markdown("---")
        
            # Columna 2
            with col2:
                for producto in productos_lista_kilos[mitad_kilos:]:
                    # Obtener valores actuales
                    valores_actuales = productos_kilos.get(producto, {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": 0.0})
                    if isinstance(valores_actuales, (int, float)):
                        valores_actuales = {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs_cajas_abiertas": float(valores_actuales)}
                    
                    cajas_cerradas_actual = valores_actuales.get("cajas_cerradas", 0)
                    cajas_abiertas_actual = valores_actuales.get("cajas_abiertas", 0)
                    kgs_abiertas_actual = valores_actuales.get("kgs_cajas_abiertas", 0.0)
                    
                    # Obtener valores guardados en sesión
                    if producto not in st.session_state.valores_kilos:
                        st.session_state.valores_kilos[producto] = {"cajas_cerradas": None, "cajas_abiertas": None, "kgs_cajas_abiertas": None}
                    
                    # Total en kg
                    total_kg = (cajas_cerradas_actual * 7.8) + kgs_abiertas_actual
                    # Formato europeo: reemplazar punto por coma
                    total_kg_formatted = f"{total_kg:.3f}".replace(".", ",")
                    
                    st.markdown(f"**{producto}** (Total: {total_kg_formatted} kg)")
                    col_cerradas, col_abiertas, col_kgs = st.columns([1, 1, 1.2])
                    
                    with col_cerradas:
                        st.markdown("<div style='text-align: center; font-size: 12px; color: #666;'>Cajas Cerradas</div>", unsafe_allow_html=True)
                        val_cc = st.session_state.valores_kilos[producto]["cajas_cerradas"]
                        cajas_cerradas = st.number_input(
                            "Cajas Cerradas",
                            min_value=0,
                            value=val_cc if val_cc is not None else 0,
                            step=1,
                            key=f"kilos2_cerradas_{producto}_emp",
                            label_visibility="collapsed",
                            placeholder="Cajas"
                        )
                        if st.session_state.valores_kilos[producto]["cajas_cerradas"] is None and cajas_cerradas == 0:
                            st.session_state.valores_kilos[producto]["cajas_cerradas"] = None
                        else:
                            st.session_state.valores_kilos[producto]["cajas_cerradas"] = cajas_cerradas
                    
                    with col_abiertas:
                        st.markdown("<div style='text-align: center; font-size: 12px; color: #666;'>Cajas Abiertas</div>", unsafe_allow_html=True)
                        val_ca = st.session_state.valores_kilos[producto]["cajas_abiertas"]
                        cajas_abiertas = st.number_input(
                            "Cajas Abiertas",
                            min_value=0,
                            value=val_ca if val_ca is not None else 0,
                            step=1,
                            key=f"kilos2_abiertas_{producto}_emp",
                            label_visibility="collapsed",
                            placeholder="Cajas"
                        )
                        if st.session_state.valores_kilos[producto]["cajas_abiertas"] is None and cajas_abiertas == 0:
                            st.session_state.valores_kilos[producto]["cajas_abiertas"] = None
                        else:
                            st.session_state.valores_kilos[producto]["cajas_abiertas"] = cajas_abiertas
                    
                    with col_kgs:
                        st.markdown("<div style='text-align: center; font-size: 12px; color: #666;'>Kgs Cajas Abiertas</div>", unsafe_allow_html=True)
                        val_kg = st.session_state.valores_kilos[producto]["kgs_cajas_abiertas"]
                        kgs_abiertas = st.number_input(
                            "Kgs Cajas Abiertas",
                            min_value=0.0,
                            max_value=7.8 * (st.session_state.valores_kilos[producto]["cajas_abiertas"] or 0) if st.session_state.valores_kilos[producto]["cajas_abiertas"] else 7.8,
                            value=val_kg if val_kg is not None else 0.0,
                            step=0.1,
                            format="%.3f",
                            key=f"kilos2_kgs_{producto}_emp",
                            label_visibility="collapsed",
                            placeholder="Kgs"
                        )
                        if st.session_state.valores_kilos[producto]["kgs_cajas_abiertas"] is None and kgs_abiertas == 0.0:
                            st.session_state.valores_kilos[producto]["kgs_cajas_abiertas"] = None
                        else:
                            st.session_state.valores_kilos[producto]["kgs_cajas_abiertas"] = kgs_abiertas
                    
                    # Agregar si cualquiera de los valores no es None (puede ser 0 = sin stock)
                    if (st.session_state.valores_kilos[producto]["cajas_cerradas"] is not None or 
                        st.session_state.valores_kilos[producto]["cajas_abiertas"] is not None or 
                        st.session_state.valores_kilos[producto]["kgs_cajas_abiertas"] is not None):
                        productos_seleccionados_kilos[producto] = {
                            "cajas_cerradas": st.session_state.valores_kilos[producto]["cajas_cerradas"] or 0,
                            "cajas_abiertas": st.session_state.valores_kilos[producto]["cajas_abiertas"] or 0,
                            "kgs_cajas_abiertas": st.session_state.valores_kilos[producto]["kgs_cajas_abiertas"] or 0.0
                        }
                    
                    st.markdown("---")
            
            # Botón de envío dentro del formulario
            submitted_kilos = st.form_submit_button("➕ Agregar al Carrito", use_container_width=True)
        
        # Procesar el formulario cuando se envía
        if submitted_kilos:
            if productos_seleccionados_kilos:
                # Agregar productos seleccionados al carrito
                productos_agregados = 0
                for producto, valores in productos_seleccionados_kilos.items():
                    entrada = {
                        'categoria': 'Por Kilos',
                        'producto': producto,
                        'cantidad': valores,  # Ahora es un dict con las 3 columnas
                        'fecha': str(fecha_carga),
                        'usuario': usuario
                    }
                    if agregar_al_carrito(entrada):
                        productos_agregados += 1
                
                if productos_agregados > 0:
                    # Guardar valores para persistencia (vigente por 1 día)
                    valores_persistencia.guardar_valores(
                        usuario, tienda_id, fecha_carga,
                        st.session_state.valores_impulsivo,
                        st.session_state.valores_kilos,
                        st.session_state.valores_extras
                    )
                    st.success(f"✅ {productos_agregados} productos agregados al carrito")
                    st.rerun()
            else:
                st.warning("⚠️ Selecciona al menos un producto con algún valor cargado")

    # TAB EXTRAS
    with tab3:
        st.markdown("### 🛍️ Productos Extras")
        productos_extras = inventario_actual.get("Extras", {})
        
        st.markdown("**Carga por Bultos y Unidades:**")
        
        # Usar form para mejorar rendimiento
        with st.form("form_extras", clear_on_submit=False):
            col1, sep, col2 = st.columns([10, 0.5, 10])
            productos_seleccionados_extras = {}
            
            productos_lista_extras = list(PRODUCTOS_BASE["Extras"].keys())
            mitad_extras = len(productos_lista_extras) // 2
            
            with sep:
                st.markdown(
                    "<div style='height: 100%; border-left: 2px solid #333; margin: 0 auto;'></div>",
                    unsafe_allow_html=True
                )
            
            with col1:
                for producto in productos_lista_extras[:mitad_extras]:
                    # Obtener valores actuales
                    valores_actuales = productos_extras.get(producto, {"bultos": 0, "unidad": 0})
                    if isinstance(valores_actuales, (int, float)):
                        valores_actuales = {"bultos": 0, "unidad": int(valores_actuales)}
                    
                    bultos_actual = valores_actuales.get("bultos", 0)
                    unidad_actual = valores_actuales.get("unidad", 0)
                    
                    # Obtener valores guardados en sesión
                    if producto not in st.session_state.valores_extras:
                        st.session_state.valores_extras[producto] = {"bultos": None, "unidad": None}
                    
                    st.markdown(f"**{producto}** (📦: {bultos_actual}, 📋: {unidad_actual})")
                    col_bultos, col_unidad = st.columns(2)
                    
                    with col_bultos:
                        valor_actual = st.session_state.valores_extras[producto]["bultos"]
                        bultos = st.number_input(
                            "📦 Bultos",
                            min_value=0,
                            value=valor_actual if valor_actual is not None else 0,
                            step=1,
                            key=f"extra_bultos_{producto}_emp",
                            placeholder="Bultos"
                        )
                        if st.session_state.valores_extras[producto]["bultos"] is None and bultos == 0:
                            st.session_state.valores_extras[producto]["bultos"] = None
                        else:
                            st.session_state.valores_extras[producto]["bultos"] = bultos if bultos > 0 else 0
                    
                    with col_unidad:
                        valor_actual = st.session_state.valores_extras[producto]["unidad"]
                        unidad = st.number_input(
                            "📋 Unidad",
                            min_value=0,
                            value=valor_actual if valor_actual is not None else 0,
                            step=1,
                            key=f"extra_unidad_{producto}_emp",
                            placeholder="Unidades"
                        )
                        if st.session_state.valores_extras[producto]["unidad"] is None and unidad == 0:
                            st.session_state.valores_extras[producto]["unidad"] = None
                        else:
                            st.session_state.valores_extras[producto]["unidad"] = unidad if unidad > 0 else 0
                    
                    # Agregar si NO es None (puede ser 0 = sin stock)
                    if st.session_state.valores_extras[producto]["bultos"] is not None or st.session_state.valores_extras[producto]["unidad"] is not None:
                        productos_seleccionados_extras[producto] = {"bultos": st.session_state.valores_extras[producto]["bultos"] or 0, "unidad": st.session_state.valores_extras[producto]["unidad"] or 0}
                    
                    st.markdown("---")
        
            with col2:
                for producto in productos_lista_extras[mitad_extras:]:
                    # Obtener valores actuales
                    valores_actuales = productos_extras.get(producto, {"bultos": 0, "unidad": 0})
                    if isinstance(valores_actuales, (int, float)):
                        valores_actuales = {"bultos": 0, "unidad": int(valores_actuales)}
                    
                    bultos_actual = valores_actuales.get("bultos", 0)
                    unidad_actual = valores_actuales.get("unidad", 0)
                    
                    # Obtener valores guardados en sesión
                    if producto not in st.session_state.valores_extras:
                        st.session_state.valores_extras[producto] = {"bultos": None, "unidad": None}
                    
                    st.markdown(f"**{producto}** (📦: {bultos_actual}, 📋: {unidad_actual})")
                    col_bultos, col_unidad = st.columns(2)
                    
                    with col_bultos:
                        valor_actual = st.session_state.valores_extras[producto]["bultos"]
                        bultos = st.number_input(
                            "📦 Bultos",
                            min_value=0,
                            value=valor_actual if valor_actual is not None else 0,
                            step=1,
                            key=f"extra2_bultos_{producto}_emp",
                            placeholder="Bultos"
                        )
                        if st.session_state.valores_extras[producto]["bultos"] is None and bultos == 0:
                            st.session_state.valores_extras[producto]["bultos"] = None
                        else:
                            st.session_state.valores_extras[producto]["bultos"] = bultos if bultos > 0 else 0
                    
                    with col_unidad:
                        valor_actual = st.session_state.valores_extras[producto]["unidad"]
                        unidad = st.number_input(
                            "📋 Unidad",
                            min_value=0,
                            value=valor_actual if valor_actual is not None else 0,
                            step=1,
                            key=f"extra2_unidad_{producto}_emp",
                            placeholder="Unidades"
                        )
                        if st.session_state.valores_extras[producto]["unidad"] is None and unidad == 0:
                            st.session_state.valores_extras[producto]["unidad"] = None
                        else:
                            st.session_state.valores_extras[producto]["unidad"] = unidad if unidad > 0 else 0
                    
                    # Agregar si NO es None (puede ser 0 = sin stock)
                    if st.session_state.valores_extras[producto]["bultos"] is not None or st.session_state.valores_extras[producto]["unidad"] is not None:
                        productos_seleccionados_extras[producto] = {"bultos": st.session_state.valores_extras[producto]["bultos"] or 0, "unidad": st.session_state.valores_extras[producto]["unidad"] or 0}
                    
                    st.markdown("---")
            
            # Botón de envío dentro del formulario
            submitted_extras = st.form_submit_button("➕ Agregar al Carrito", use_container_width=True)
        
        # Procesar el formulario cuando se envía
        if submitted_extras:
            if productos_seleccionados_extras:
                # Agregar productos seleccionados al carrito
                productos_agregados = 0
                for producto, valores in productos_seleccionados_extras.items():
                    entrada = {
                        'categoria': 'Extras',
                        'producto': producto,
                        'cantidad': valores,  # Ahora es un dict con bultos y unidad
                        'fecha': str(fecha_carga),
                        'usuario': usuario
                    }
                    if agregar_al_carrito(entrada):
                        productos_agregados += 1
                
                if productos_agregados > 0:
                    # Guardar valores para persistencia (vigente por 1 día)
                    valores_persistencia.guardar_valores(
                        usuario, tienda_id, fecha_carga,
                        st.session_state.valores_impulsivo,
                        st.session_state.valores_kilos,
                        st.session_state.valores_extras
                    )
                    st.success(f"✅ {productos_agregados} productos agregados al carrito")
                    st.rerun()
            else:
                st.warning("⚠️ Selecciona al menos un producto con algún valor cargado")

    # Mostrar información del carrito actual (AL FINAL) - CON MEJORAS VISUALES
    if st.session_state.carrito_temporal:
        st.divider()
        
        # Header del carrito con badge
        total_carrito = len(st.session_state.carrito_temporal)
        st.markdown(f"""
        <div class='producto-header'>
            <h3 style='margin:0;'>🛒 Carrito de Inventario 
            <span class='carrito-badge'>{total_carrito} productos</span></h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            items_guardados = sum(1 for item in st.session_state.carrito_temporal if item.get('guardado', False))
            items_pendientes = total_carrito - items_guardados
            if items_guardados == total_carrito:
                st.success(f"✅ **{total_carrito} productos guardados** - Inventario actualizado")
            elif items_guardados > 0:
                st.warning(f"⏳ **{items_pendientes} productos pendientes** de guardar")
            else:
                st.info(f"📦 **{total_carrito} productos** listos para guardar")
        
        with col2:
            if st.button("💾 Guardar Todo", type="primary", disabled=st.session_state.esta_guardando):
                if guardar_carrito_completo():
                    st.rerun()
        
        with col3:
            if st.button("🗑️ Limpiar Carrito"):
                st.session_state.carrito_temporal = []
                # Limpiar también los valores guardados en sesión
                st.session_state.valores_impulsivo = {}
                st.session_state.valores_kilos = {}
                st.session_state.valores_extras = {}
                # Limpiar valores persistidos en archivo
                valores_persistencia.limpiar_valores(usuario, tienda_id, fecha_carga)
                st.rerun()
        
        # Mostrar productos en el carrito con diseño mejorado
        with st.expander("👀 Ver productos cargados", expanded=True):
            if st.session_state.carrito_temporal:
                # Agrupar por categoría
                por_categoria = {}
                for item in st.session_state.carrito_temporal:
                    cat = item['categoria']
                    if cat not in por_categoria:
                        por_categoria[cat] = []
                    por_categoria[cat].append(item)
                
                # Mostrar por categoría
                for categoria, items in por_categoria.items():
                    # Icono por categoría
                    icono_cat = "🍦" if categoria == "Impulsivo" else ("⚖️" if categoria == "Por Kilos" else "🛍️")
                    st.markdown(f"**{icono_cat} {categoria}** ({len(items)} productos)")
                    
                    for item in items:
                        guardado = item.get('guardado', False)
                        cantidad = item['cantidad']
                        
                        # Determinar clase CSS según estado
                        if guardado:
                            clase = "producto-guardado"
                            estado_text = "✅ Guardado"
                            color = "#28a745"
                            bg_color = "#d4edda"
                        else:
                            clase = "producto-carrito"
                            estado_text = "⏳ Pendiente"
                            color = "#000000"
                            bg_color = "#fff3cd"
                        
                        # Formatear cantidad según tipo y categoría
                        if isinstance(cantidad, dict):
                            if categoria == "Por Kilos":
                                # Formato para kilos: cajas cerradas, cajas abiertas, kgs
                                cerradas = cantidad.get('cajas_cerradas', 0)
                                abiertas = cantidad.get('cajas_abiertas', 0)
                                kgs = cantidad.get('kgs_cajas_abiertas', 0.0)
                                total_kg = (cerradas * 7.8) + kgs
                                cantidad_texto = f"📦 {cerradas} C.Cerradas | 📂 {abiertas} C.Abiertas | ⚖️ {kgs:.1f}kg ({total_kg:.1f}kg total)"
                            else:
                                # Formato bultos y unidades para Impulsivo y Extras
                                bultos = cantidad.get('bultos', 0)
                                unidad = cantidad.get('unidad', 0)
                                cantidad_texto = f"📦 {bultos} Bultos, 📋 {unidad} Unidades"
                        else:
                            cantidad_texto = f"{cantidad}"
                        
                        # Mostrar producto con estilo
                        st.markdown(f"""
                        <div style='background-color:{bg_color};padding:12px;border-radius:8px;margin-bottom:8px;border-left:4px solid {color};'>
                            <strong style='font-size:14px;'>{item['producto']}</strong><br>
                            <span style='color:{color};font-weight:bold;font-size:13px;'>{estado_text}</span> | 
                            <span style='color:#333;font-size:12px;'>{cantidad_texto}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                
                # Mostrar resumen final
                total_items = len(st.session_state.carrito_temporal)
                items_guardados = sum(1 for item in st.session_state.carrito_temporal if item.get('guardado', False))
                
                col_res1, col_res2, col_res3 = st.columns(3)
                with col_res1:
                    st.metric("📦 Total", total_items)
                with col_res2:
                    st.metric("✅ Guardados", items_guardados)
                with col_res3:
                    st.metric("⏳ Pendientes", total_items - items_guardados)
            else:
                st.info("🛒 Carrito vacío")

    # Mostrar resumen del inventario actual
    if st.checkbox("📊 Ver resumen del inventario actual"):
        st.subheader("📊 Resumen del Inventario")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🍦 Impulsivo")
            productos_imp = inventario_actual.get("Impulsivo", {})
            productos_con_stock = []
            total_bultos = 0
            total_unidades = 0
            for v in productos_imp.values():
                if isinstance(v, dict):
                    bultos = v.get('bultos', 0)
                    unidad = v.get('unidad', 0)
                    if bultos > 0 or unidad > 0:
                        productos_con_stock.append(v)
                        total_bultos += bultos
                        total_unidades += unidad
                elif isinstance(v, (int, float)) and v > 0:
                    productos_con_stock.append(v)
                    total_unidades += v
            st.metric("Productos con stock", len(productos_con_stock))
            st.metric("Total Bultos", int(total_bultos))
            st.metric("Total Unidades", int(total_unidades))
        
        with col2:
            st.markdown("#### ⚖️ Por Kilos")
            productos_kg = inventario_actual.get("Por Kilos", {})
            productos_con_stock_kg = []
            total_kg = 0.0
            for v in productos_kg.values():
                if isinstance(v, dict):
                    cerradas = v.get('cajas_cerradas', 0)
                    kgs = v.get('kgs_cajas_abiertas', 0.0)
                    total_producto = (cerradas * 7.8) + kgs
                    if total_producto > 0:
                        productos_con_stock_kg.append(v)
                        total_kg += total_producto
                elif isinstance(v, (int, float)) and v > 0:
                    productos_con_stock_kg.append(v)
                    total_kg += v
            st.metric("Productos con stock", len(productos_con_stock_kg))
            st.metric("Cantidad total (kg)", f"{total_kg:.1f}")
        
        with col3:
            st.markdown("#### 🛍️ Extras")
            productos_ext = inventario_actual.get("Extras", {})
            productos_con_stock_ext = []
            total_bultos_ext = 0
            total_unidades_ext = 0
            for v in productos_ext.values():
                if isinstance(v, dict):
                    bultos = v.get('bultos', 0)
                    unidad = v.get('unidad', 0)
                    if bultos > 0 or unidad > 0:
                        productos_con_stock_ext.append(v)
                        total_bultos_ext += bultos
                        total_unidades_ext += unidad
                elif isinstance(v, (int, float)) and v > 0:
                    productos_con_stock_ext.append(v)
                    total_unidades_ext += v
            st.metric("Productos con stock", len(productos_con_stock_ext))
            st.metric("Total Bultos", int(total_bultos_ext))
            st.metric("Total Unidades", int(total_unidades_ext))

    return True