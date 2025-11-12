# UI y lógica de empleados (Inventario) - Adaptado para BusinessSuite
import streamlit as st
from datetime import date, datetime
import json
import os

try:
    from config_tiendas import selector_tienda_empleado, GestorTiendas
except ImportError:
    def selector_tienda_empleado():
        return "T001"
    GestorTiendas = None

try:
    from persistencia import cargar_inventario, guardar_inventario, guardar_historial
except ImportError:
    def cargar_inventario(tienda_id=None, fecha_carga=None):
        return {"Impulsivo": {}, "Por Kilos": {}, "Extras": {}}
    def guardar_inventario(inventario, tienda_id=None, fecha_carga=None):
        pass
    def guardar_historial(fecha, usuario, categoria, producto, cantidad, modo, tipo_inventario="Diario", tienda_id=None):
        pass

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

def mostrar_interfaz_empleado():
    """Interfaz principal del empleado para inventario"""
    
    st.header("📦 Sistema de Inventario - Empleado")
    
    # Información del usuario
    user_info = st.session_state.get('user_info', {})
    st.info(f"👤 Usuario: {user_info.get('username', 'Empleado')}")
    
    # Selector de tienda
    tienda_id = selector_tienda_empleado() if 'selector_tienda_empleado' in globals() else "T001"
    
    # Selector de fecha
    fecha_carga = st.date_input("Fecha de carga:", value=date.today())
    
    # Selector de tipo de inventario
    tipo_inventario = st.selectbox(
        "Tipo de inventario:",
        ["Diario", "Semanal", "Quincenal"]
    )
    
    # Cargar inventario actual
    inventario_actual = cargar_inventario(tienda_id, fecha_carga)
    
    # Mergear con estructura base de forma segura
    inventario_completo = {}
    for categoria, productos_base in PRODUCTOS_BASE.items():
        inventario_completo[categoria] = {}
        
        for producto, valor_default in productos_base.items():
            # Intentar obtener valor del inventario actual
            try:
                if (categoria in inventario_actual and 
                    isinstance(inventario_actual[categoria], dict) and
                    producto in inventario_actual[categoria]):
                    
                    valor_actual = inventario_actual[categoria][producto]
                    
                    # Para categoría "Por Kilos" y tipo "Semanal", mantener strings
                    if categoria == "Por Kilos" and tipo_inventario == "Semanal":
                        if isinstance(valor_actual, str):
                            inventario_completo[categoria][producto] = valor_actual
                        else:
                            inventario_completo[categoria][producto] = "Vacío"
                    else:
                        # Para otros casos, convertir a número
                        try:
                            inventario_completo[categoria][producto] = float(valor_actual) if valor_actual is not None else valor_default
                        except (ValueError, TypeError):
                            inventario_completo[categoria][producto] = valor_default
                else:
                    inventario_completo[categoria][producto] = valor_default
                    
            except Exception as e:
                # En caso de cualquier error, usar valor por defecto
                inventario_completo[categoria][producto] = valor_default
    
    # Tabs por categoría
    tab_impulsivo, tab_kilos, tab_extras = st.tabs(["🍦 Impulsivo", "⚖️ Por Kilos", "🛠️ Extras"])
    
    with tab_impulsivo:
        mostrar_categoria_inventario("Impulsivo", inventario_completo["Impulsivo"], user_info.get('username', 'empleado'), tienda_id, fecha_carga, tipo_inventario)
    
    with tab_kilos:
        mostrar_categoria_inventario("Por Kilos", inventario_completo["Por Kilos"], user_info.get('username', 'empleado'), tienda_id, fecha_carga, tipo_inventario)
    
    with tab_extras:
        mostrar_categoria_inventario("Extras", inventario_completo["Extras"], user_info.get('username', 'empleado'), tienda_id, fecha_carga, tipo_inventario)

def mostrar_categoria_inventario(categoria, productos, usuario, tienda_id, fecha_carga, tipo_inventario):
    """Muestra la interfaz para una categoría específica"""
    
    st.subheader(f"Categoría: {categoria}")
    
    # Crear formulario para la categoría
    with st.form(f"form_{categoria}_{tienda_id}", clear_on_submit=False):
        productos_modificados = {}
        
        # Crear columnas para mejor organización
        num_cols = 3
        productos_lista = list(productos.items())
        
        for i in range(0, len(productos_lista), num_cols):
            cols = st.columns(num_cols)
            
            for j, col in enumerate(cols):
                if i + j < len(productos_lista):
                    producto, cantidad_actual = productos_lista[i + j]
                    
                    with col:
                        if categoria == "Por Kilos" and tipo_inventario == "Semanal":
                            # Para inventario semanal, usar opciones descriptivas
                            opciones = ["Vacío", "Cuarto", "Medio", "Tres Cuartos", "Lleno", "1 y Cuarto", "1 y Medio", "1 y Tres Cuartos", "2 Baldes"]
                            valor_actual = "Vacío"
                            if isinstance(cantidad_actual, str) and cantidad_actual in opciones:
                                valor_actual = cantidad_actual
                            
                            nueva_cantidad = st.selectbox(
                                producto,
                                opciones,
                                index=opciones.index(valor_actual),
                                key=f"{categoria}_{producto}"
                            )
                        else:
                            # Para otros casos, usar input numérico
                            step = 0.1 if categoria == "Por Kilos" else 1
                            
                            # Convertir cantidad_actual de forma segura
                            try:
                                valor_inicial = float(cantidad_actual) if cantidad_actual is not None else 0.0
                            except (ValueError, TypeError):
                                valor_inicial = 0.0
                            
                            nueva_cantidad = st.number_input(
                                producto,
                                min_value=0.0,
                                value=valor_inicial,
                                step=step,
                                key=f"{categoria}_{producto}"
                            )
                        
                        productos_modificados[producto] = nueva_cantidad
        
        # Botón para guardar la categoría
        if st.form_submit_button(f"💾 Guardar {categoria}"):
            try:
                # Cargar inventario completo actual
                inventario_completo = cargar_inventario(tienda_id, fecha_carga)
                
                # Actualizar la categoría específica
                inventario_completo[categoria] = productos_modificados
                
                # Guardar inventario actualizado
                guardar_inventario(inventario_completo, tienda_id, fecha_carga)
                
                # Guardar en historial
                productos_cambiados = []
                for producto, nueva_cantidad in productos_modificados.items():
                    cantidad_anterior = productos.get(producto, 0)
                    
                    # Normalizar tipos para comparación
                    try:
                        if isinstance(nueva_cantidad, str):
                            # Si nueva_cantidad es string, mantener como string
                            cantidad_anterior_norm = str(cantidad_anterior) if cantidad_anterior is not None else "Vacío"
                            nueva_cantidad_norm = nueva_cantidad
                        else:
                            # Si nueva_cantidad es numérica, convertir ambos a float
                            cantidad_anterior_norm = float(cantidad_anterior) if cantidad_anterior is not None else 0.0
                            nueva_cantidad_norm = float(nueva_cantidad)
                    except (ValueError, TypeError):
                        # En caso de error, usar valores por defecto
                        cantidad_anterior_norm = 0
                        nueva_cantidad_norm = nueva_cantidad
                    
                    if nueva_cantidad_norm != cantidad_anterior_norm:
                        guardar_historial(
                            fecha_carga, 
                            usuario, 
                            categoria, 
                            producto, 
                            nueva_cantidad, 
                            "actualización",
                            tipo_inventario,
                            tienda_id
                        )
                        productos_cambiados.append(producto)
                
                if productos_cambiados:
                    st.success(f"✅ {categoria} actualizado exitosamente! Productos modificados: {len(productos_cambiados)}")
                else:
                    st.info(f"ℹ️ No se detectaron cambios en {categoria}")
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error al guardar {categoria}: {str(e)}")

# Función principal para empleado (compatibilidad con sistema original)
def empleado_inventario_ui(inventario, usuario, opciones_valde, guardar_inventario_func, guardar_historial_func, tienda_id="T001"):
    """Función de compatibilidad con el sistema original"""
    mostrar_interfaz_empleado()

if __name__ == "__main__":
    mostrar_interfaz_empleado()