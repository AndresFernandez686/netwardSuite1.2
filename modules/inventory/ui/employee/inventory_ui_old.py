"""
UI de inventario para empleados.
Interfaz modular y limpia para gestión de inventario.
"""
import streamlit as st
from datetime import date
from typing import Dict, Any, Callable

from ...core.inventory_manager import InventoryManager, BaldeManager
from ...core.inventory_types import InventoryType
from ...core.data_models import QuantityFormatter
from ..components.widgets import InventoryTypeSelector, ProductSummary

class EmployeeInventoryUI:
    """Interfaz de inventario para empleados"""
    
    def __init__(self):
        self.inventory_manager = InventoryManager()
        self.balde_manager = BaldeManager()
    
    def render(self, inventario: Dict[str, Any], usuario: str, opciones_valde: Dict[str, str],
              guardar_inventario: Callable, guardar_historial: Callable):
        """Renderiza la interfaz completa de inventario"""
        
        st.header("📦 Inventario")
        
        # Selector de tipo y fecha
        fecha_carga, tipo_inventario = self._render_header()
        
        # Manejar cambio de tipo
        inv_type = InventoryType.from_string(tipo_inventario)
        self.inventory_manager.handle_type_change(inv_type)
        
        # Mostrar información del tipo seleccionado
        self._show_type_info(tipo_inventario)
        
        # Tabs por categoría
        self._render_category_tabs(
            inventario, usuario, opciones_valde, fecha_carga, 
            inv_type, guardar_inventario, guardar_historial
        )
        
        # Resumen de productos cargados
        self._render_summary(inv_type)
    
    def _render_header(self) -> tuple[date, str]:
        """Renderiza cabecera con fecha y tipo"""
        col1, col2 = st.columns(2)
        
        with col1:
            fecha_carga = st.date_input(
                "📅 Fecha de carga", 
                value=date.today(), 
                key="fecha_inv"
            )
        
        with col2:
            tipo_inventario = st.selectbox(
                "📋 Tipo de inventario",
                ["Diario", "Semanal", "Quincenal"],
                key="tipo_inventario"
            )
        
        return fecha_carga, tipo_inventario
    
    def _show_type_info(self, tipo_inventario: str):
        """Muestra información específica del tipo"""
        if tipo_inventario == "Quincenal":
            st.info("📊 **Inventario Quincenal**: En 'Por Kilos' registrarás la cantidad exacta en kilos de cada balde.")
    
    def _render_category_tabs(self, inventario: Dict[str, Any], usuario: str, 
                            opciones_valde: Dict[str, str], fecha_carga: date, 
                            inv_type: InventoryType, guardar_inventario: Callable, 
                            guardar_historial: Callable):
        """Renderiza tabs por categoría"""
        
        tabs = st.tabs(list(inventario.keys()))
        
        for i, categoria in enumerate(inventario.keys()):
            with tabs[i]:
                productos = inventario[categoria]
                
                producto_seleccionado = st.selectbox(
                    f"Producto de {categoria}",
                    list(productos.keys()),
                    key=f"sel_{categoria}_{inv_type.value}"
                )
                
                # Renderizar según categoría
                if categoria == "Por Kilos":
                    self._render_kilos_category(
                        productos, producto_seleccionado, categoria, usuario,
                        opciones_valde, fecha_carga, inv_type, 
                        guardar_inventario, guardar_historial
                    )
                else:
                    self._render_numeric_category(
                        productos, producto_seleccionado, categoria, usuario,
                        fecha_carga, inv_type, guardar_inventario, guardar_historial
                    )
    
    def _render_numeric_category(self, productos: Dict[str, Any], producto: str, 
                               categoria: str, usuario: str, fecha_carga: date, 
                               inv_type: InventoryType, guardar_inventario: Callable, 
                               guardar_historial: Callable):
        """Renderiza categorías numéricas (Impulsivo, Extras)"""
        
        # Obtener valor específico del tipo
        valor_actual = self.inventory_manager.get_product_value(
            inv_type, categoria, producto, 0
        )
        
        # Widget con key específica por tipo
        widget_key = self.inventory_manager.get_widget_key(
            inv_type, categoria, producto, "cant"
        )
        
        cantidad = st.number_input(
            "Cantidad (unidades)",
            min_value=0,
            value=valor_actual,
            step=1,
            key=widget_key
        )
        
        # Botón de actualización
        btn_key = f"btn_{inv_type.value}_{categoria}_{producto}"
        
        if st.button(f"✅ Actualizar {producto} ({categoria}) - {inv_type.value}", key=btn_key):
            # Guardar en inventario principal
            productos[producto] = cantidad
            guardar_inventario(productos)
            
            # Usar inventory manager para coordinar guardado
            def save_to_history(record):
                guardar_historial(
                    record.fecha, record.usuario, record.categoria,
                    record.producto, record.cantidad, record.modo, record.tipo_inventario
                )
            
            self.inventory_manager.save_product(
                inv_type, categoria, producto, cantidad, usuario, fecha_carga,
                guardar_inventario, save_to_history
            )
            
            st.success(f"✅ {producto}: **{cantidad}** unidades ({inv_type.value})")
    
    def _render_kilos_category(self, productos: Dict[str, Any], producto: str, 
                             categoria: str, usuario: str, opciones_valde: Dict[str, str],
                             fecha_carga: date, inv_type: InventoryType, 
                             guardar_inventario: Callable, guardar_historial: Callable):
        """Renderiza categoría Por Kilos"""
        
        if inv_type == InventoryType.QUINCENAL:
            self._render_quincenal_kilos(
                productos, producto, categoria, usuario, fecha_carga, 
                inv_type, guardar_inventario, guardar_historial
            )
        else:
            self._render_estados_kilos(
                productos, producto, categoria, usuario, opciones_valde, 
                fecha_carga, inv_type, guardar_inventario, guardar_historial
            )
    
    def _render_quincenal_kilos(self, productos: Dict[str, Any], producto: str, 
                              categoria: str, usuario: str, fecha_carga: date, 
                              inv_type: InventoryType, guardar_inventario: Callable, 
                              guardar_historial: Callable):
        """Renderiza modo quincenal con kilos exactos"""
        
        st.markdown("### ⚖️ Registrar cantidad exacta en kilos por balde:")
        
        num_baldes = st.number_input(
            "Cantidad de baldes",
            min_value=1,
            max_value=10,
            value=1,
            step=1,
            key=f"num_baldes_{producto}_{fecha_carga}_{usuario}_{inv_type.value}"
        )
        
        st.markdown(f"### Kilos en cada balde (hasta {num_baldes} baldes):")
        
        kilos_baldes = []
        total_kilos = 0.0
        
        for n in range(1, num_baldes + 1):
            key_balde = self.balde_manager.get_balde_key(
                inv_type, producto, n, fecha_carga, usuario, is_kilos=True
            )
            
            # Inicializar valor
            self.balde_manager.initialize_balde_value(
                key_balde, 0.0, productos, producto, n-1
            )
            
            kilos = st.number_input(
                f"🪣 Balde {n} (kg)",
                min_value=0.0,
                max_value=50.0,
                value=st.session_state[key_balde],
                step=0.1,
                format="%.1f",
                key=key_balde
            )
            
            kilos_actual = st.session_state[key_balde]
            kilos_baldes.append(round(kilos_actual, 1))
            total_kilos += kilos_actual
        
        st.markdown(f"**📊 Total: {total_kilos:.1f} kg**")
        
        # Botón de actualización
        btn_key = f"btn_{categoria}_{producto}_quincenal_{inv_type.value}"
        
        if st.button(f"✅ Actualizar {producto} ({categoria}) - Quincenal", key=btn_key):
            productos[producto] = kilos_baldes.copy()
            guardar_inventario(productos)
            
            cantidad_data = {
                "kilos_por_balde": kilos_baldes,
                "total_kilos": total_kilos,
                "tipo": "Quincenal"
            }
            
            guardar_historial(
                fecha_carga, usuario, categoria, producto, 
                cantidad_data, "Modificar", inv_type.value
            )
            
            st.success(f"✅ {producto}: **{total_kilos:.1f} kg** (Quincenal)")
    
    def _render_estados_kilos(self, productos: Dict[str, Any], producto: str, 
                            categoria: str, usuario: str, opciones_valde: Dict[str, str],
                            fecha_carga: date, inv_type: InventoryType, 
                            guardar_inventario: Callable, guardar_historial: Callable):
        """Renderiza modo diario/semanal con estados"""
        
        st.markdown("### 🪣 Selecciona la cantidad de baldes a registrar:")
        
        num_baldes = st.number_input(
            "Cantidad de baldes",
            min_value=1,
            max_value=10,
            value=1,
            step=1,
            key=f"num_baldes_{producto}_{fecha_carga}_{usuario}_{inv_type.value}"
        )
        
        st.markdown(f"### Estado de hasta {num_baldes} baldes:")
        
        estados_baldes = []
        
        for n in range(1, num_baldes + 1):
            key_balde = self.balde_manager.get_balde_key(
                inv_type, producto, n, fecha_carga, usuario, is_kilos=False
            )
            
            # Inicializar valor
            self.balde_manager.initialize_balde_value(
                key_balde, "Vacío", productos, producto, n-1
            )
            
            opcion = st.selectbox(
                f"🪣 Balde {n}",
                list(opciones_valde.keys()),
                index=list(opciones_valde.keys()).index(st.session_state[key_balde]) 
                      if st.session_state[key_balde] in opciones_valde else 0,
                key=key_balde
            )
            
            estado_actual = st.session_state[key_balde]
            estados_baldes.append(estado_actual)
        
        # Botón de actualización
        btn_key = f"btn_{categoria}_{producto}_estados_{inv_type.value}"
        
        if st.button(f"✅ Actualizar {producto} ({categoria}) - {inv_type.value}", key=btn_key):
            productos[producto] = estados_baldes.copy()
            guardar_inventario(productos)
            
            cantidad_data = {
                "estados": estados_baldes,
                "tipo": inv_type.value
            }
            
            guardar_historial(
                fecha_carga, usuario, categoria, producto, 
                cantidad_data, "Modificar", inv_type.value
            )
            
            st.success(f"✅ {producto}: {', '.join(estados_baldes)} ({inv_type.value})")
    
    def _render_summary(self, inv_type: InventoryType):
        """Renderiza resumen de productos cargados"""
        st.subheader("📋 Resumen de inventarios cargados")
        
        # Resumen por tipos
        type_summary = self.inventory_manager.get_type_summary()
        session_summary = self.inventory_manager.get_session_summary()
        
        if not type_summary and not session_summary:
            st.info("Aún no has cargado ningún producto en ningún tipo de inventario.")
            return
        
        # Mostrar por cada tipo
        for tipo in ["Diario", "Semanal", "Quincenal"]:
            if tipo in type_summary and type_summary[tipo]:
                st.markdown(f"**🔹 Inventario {tipo}:**")
                for producto_info, cantidad in type_summary[tipo].items():
                    if cantidad > 0:
                        st.write(f"   • {producto_info}: **{cantidad}** unidades")
        
        # Mostrar sesión actual
        if session_summary:
            st.markdown(f"**🔸 Cargados en esta sesión ({inv_type.value}):**")
            for categoria, productos_cat in session_summary.items():
                for producto, datos in productos_cat.items():
                    if isinstance(datos, dict) and "cantidad" in datos:
                        cantidad = datos["cantidad"]
                        tipo_inv = datos.get("tipo_inventario", inv_type.value)
                        if cantidad > 0:
                            st.write(f"   • {producto} ({categoria}): **{cantidad}** - {tipo_inv}")

def create_employee_inventory_ui() -> EmployeeInventoryUI:
    """Factory function para crear la UI"""
    return EmployeeInventoryUI()