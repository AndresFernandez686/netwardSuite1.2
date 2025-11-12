# UI y lógica de administrador (Inventario) - Adaptado para BusinessSuite
import streamlit as st
from datetime import date, datetime
import json
import os

try:
    from config_tiendas import GestorTiendas, obtener_nombre_tienda
except ImportError:
    def obtener_nombre_tienda(tienda_id):
        return f"Tienda {tienda_id}"
    GestorTiendas = None

try:
    from persistencia import cargar_inventario, guardar_inventario, cargar_historial
except ImportError:
    def cargar_inventario(tienda_id=None, fecha_carga=None):
        return {"Impulsivo": {}, "Por Kilos": {}, "Extras": {}}
    def guardar_inventario(inventario, tienda_id=None, fecha_carga=None):
        pass
    def cargar_historial(tienda_id=None):
        return []

def mostrar_interfaz_admin():
    """Interfaz principal del administrador para inventario"""
    
    st.header("🏢 Sistema de Inventario - Administrador")
    
    # Información del usuario
    user_info = st.session_state.get('user_info', {})
    st.info(f"👤 Usuario: {user_info.get('username', 'Admin')} (Administrador)")
    
    # Tabs del administrador
    tab1, tab2, tab3 = st.tabs(["📋 Gestión", "📊 Reportes", "⚙️ Configuración"])
    
    with tab1:
        mostrar_gestion_inventario_admin()
    
    with tab2:
        mostrar_reportes_admin()
    
    with tab3:
        mostrar_configuracion_admin()

def mostrar_gestion_inventario_admin():
    """Gestión de inventario para administrador"""
    
    st.subheader("Gestión de Inventario Multi-Tienda")
    
    # Selector de tienda
    tiendas_disponibles = {
        "T001": "Seminario",
        "T002": "Mcal Lopez"
    }
    
    tienda_seleccionada = st.selectbox(
        "Selecciona la tienda:",
        options=list(tiendas_disponibles.keys()),
        format_func=lambda x: f"{tiendas_disponibles[x]} ({x})"
    )
    
    # Selector de fecha
    fecha_carga = st.date_input("Fecha:", value=date.today())
    
    # Cargar inventario de la tienda seleccionada
    inventario_tienda = cargar_inventario(tienda_seleccionada, fecha_carga)
    
    # Mostrar resumen del inventario
    st.write(f"**Inventario de {tiendas_disponibles[tienda_seleccionada]}** - {fecha_carga}")
    
    if inventario_tienda:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Productos Impulsivos", 
                len([p for p, c in inventario_tienda.get("Impulsivo", {}).items() if c > 0])
            )
        
        with col2:
            st.metric(
                "Productos Por Kilos", 
                len([p for p, c in inventario_tienda.get("Por Kilos", {}).items() if c > 0])
            )
            
        with col3:
            st.metric(
                "Productos Extras", 
                len([p for p, c in inventario_tienda.get("Extras", {}).items() if c > 0])
            )
        
        # Mostrar detalles por categoría
        for categoria, productos in inventario_tienda.items():
            if productos:
                with st.expander(f"📦 {categoria} ({len(productos)} productos)"):
                    # Mostrar productos con stock
                    productos_con_stock = {p: c for p, c in productos.items() if c > 0}
                    
                    if productos_con_stock:
                        for producto, cantidad in productos_con_stock.items():
                            st.write(f"• **{producto}**: {cantidad}")
                    else:
                        st.info("No hay productos con stock en esta categoría")
    else:
        st.info("No hay datos de inventario para esta tienda y fecha")
    
    # Botón para exportar datos
    if st.button("📥 Exportar Inventario"):
        if inventario_tienda:
            # Crear JSON para descarga
            datos_export = {
                "tienda": tienda_seleccionada,
                "fecha": str(fecha_carga),
                "inventario": inventario_tienda
            }
            
            st.download_button(
                label="💾 Descargar JSON",
                data=json.dumps(datos_export, indent=2, ensure_ascii=False),
                file_name=f"inventario_{tienda_seleccionada}_{fecha_carga}.json",
                mime="application/json"
            )
        else:
            st.warning("No hay datos para exportar")

def mostrar_reportes_admin():
    """Reportes avanzados para administrador"""
    
    st.subheader("📊 Reportes y Análisis")
    
    # Selector de tipo de reporte
    tipo_reporte = st.selectbox(
        "Tipo de reporte:",
        ["Resumen General", "Historial de Movimientos", "Comparativa por Tiendas"]
    )
    
    if tipo_reporte == "Resumen General":
        mostrar_resumen_general()
    elif tipo_reporte == "Historial de Movimientos":
        mostrar_historial_movimientos()
    elif tipo_reporte == "Comparativa por Tiendas":
        mostrar_comparativa_tiendas()

def mostrar_resumen_general():
    """Muestra resumen general de todas las tiendas"""
    
    st.write("**Resumen General de Inventarios**")
    
    tiendas = ["T001", "T002"]
    fecha_actual = date.today()
    
    resumen_data = []
    
    for tienda_id in tiendas:
        inventario = cargar_inventario(tienda_id, fecha_actual)
        nombre_tienda = obtener_nombre_tienda(tienda_id)
        
        total_productos = 0
        categorias_info = {}
        
        for categoria, productos in inventario.items():
            productos_con_stock = len([p for p, c in productos.items() if c > 0])
            categorias_info[categoria] = productos_con_stock
            total_productos += productos_con_stock
        
        resumen_data.append({
            "Tienda": f"{nombre_tienda} ({tienda_id})",
            "Total Productos": total_productos,
            "Impulsivos": categorias_info.get("Impulsivo", 0),
            "Por Kilos": categorias_info.get("Por Kilos", 0),
            "Extras": categorias_info.get("Extras", 0)
        })
    
    # Mostrar tabla de resumen
    import pandas as pd
    df_resumen = pd.DataFrame(resumen_data)
    st.dataframe(df_resumen, use_container_width=True)

def mostrar_historial_movimientos():
    """Muestra el historial de movimientos"""
    
    st.write("**Historial de Movimientos**")
    
    # Selector de tienda para filtrar
    tienda_filtro = st.selectbox(
        "Filtrar por tienda:",
        ["Todas", "T001", "T002"],
        key="historial_tienda"
    )
    
    # Cargar historial
    if tienda_filtro == "Todas":
        historial = cargar_historial()
    else:
        historial = cargar_historial(tienda_filtro)
    
    if historial:
        # Mostrar últimos 20 movimientos
        historial_reciente = historial[-20:] if len(historial) > 20 else historial
        
        for movimiento in reversed(historial_reciente):
            fecha = movimiento.get("fecha", "N/A")
            usuario = movimiento.get("usuario", "N/A")
            tienda = movimiento.get("tienda_id", "N/A")
            categoria = movimiento.get("categoria", "N/A")
            producto = movimiento.get("producto", "N/A")
            cantidad = movimiento.get("cantidad", "N/A")
            tipo = movimiento.get("tipo_inventario", "Diario")
            
            st.write(f"**{fecha}** | {usuario} | {obtener_nombre_tienda(tienda)} | {categoria} | {producto}: {cantidad} ({tipo})")
    else:
        st.info("No hay movimientos registrados")

def mostrar_comparativa_tiendas():
    """Muestra comparativa entre tiendas"""
    
    st.write("**Comparativa por Tiendas**")
    
    fecha_comparativa = st.date_input("Fecha para comparar:", value=date.today())
    
    tiendas = ["T001", "T002"]
    datos_comparativa = {}
    
    for tienda_id in tiendas:
        inventario = cargar_inventario(tienda_id, fecha_comparativa)
        nombre_tienda = obtener_nombre_tienda(tienda_id)
        
        datos_comparativa[nombre_tienda] = {}
        
        for categoria, productos in inventario.items():
            productos_con_stock = [p for p, c in productos.items() if c > 0]
            datos_comparativa[nombre_tienda][categoria] = len(productos_con_stock)
    
    # Mostrar comparativa
    if datos_comparativa:
        col1, col2 = st.columns(2)
        
        for i, (tienda, data) in enumerate(datos_comparativa.items()):
            col = col1 if i == 0 else col2
            
            with col:
                st.write(f"**{tienda}**")
                for categoria, cantidad in data.items():
                    st.metric(categoria, cantidad)

def mostrar_configuracion_admin():
    """Configuración avanzada para administrador"""
    
    st.subheader("⚙️ Configuración del Sistema")
    
    # Configuración de tiendas
    with st.expander("🏪 Gestión de Tiendas"):
        st.info("Configuración de tiendas disponible")
        
        if st.button("Agregar Nueva Tienda"):
            st.info("🚧 Funcionalidad en desarrollo")
    
    # Configuración de productos
    with st.expander("📦 Gestión de Productos"):
        st.info("Configuración de catálogo de productos")
        
        if st.button("Actualizar Catálogo"):
            st.info("🚧 Funcionalidad en desarrollo")
    
    # Herramientas de mantenimiento
    with st.expander("🔧 Herramientas de Mantenimiento"):
        st.warning("⚠️ Estas acciones son irreversibles")
        
        if st.button("Limpiar Historial", type="secondary"):
            st.warning("Esta acción eliminaría todo el historial")
        
        if st.button("Reiniciar Inventarios", type="secondary"):
            st.warning("Esta acción reinicializaría todos los inventarios")

# Funciones de compatibilidad con sistema original
def admin_inventario_ui(inventario, usuario, opciones_valde, guardar_inventario_func, guardar_historial_func, tienda_id="T001"):
    """Función de compatibilidad con el sistema original"""
    mostrar_interfaz_admin()

def admin_historial_ui():
    """Función de compatibilidad - historial admin"""
    mostrar_historial_movimientos()

def admin_mermas_ui():
    """Función de compatibilidad - mermas admin"""
    st.info("🚧 Módulo de mermas en desarrollo")

if __name__ == "__main__":
    mostrar_interfaz_admin()