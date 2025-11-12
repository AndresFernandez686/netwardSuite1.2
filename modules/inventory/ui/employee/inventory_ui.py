"""
UI modular para inventario de empleados.
Reemplaza la funcionalidad de ui_empleado.py relacionada con inventarios.
"""
import streamlit as st
from typing import Dict, Any, Optional
from datetime import date

from ...core.inventory_types import InventoryType, TypedInventoryManager
from ...core.inventory_manager import InventoryManager
from ...core.data_models import InventoryRecord
from ...data.persistence import DataPersistence
from ...data.history import HistoryManager
from ..components.widgets import (
    InventoryTypeSelector, ProductSummary, MetricCards, 
    StatusIndicators, NotificationManager, ActionButtons
)

class EmployeeInventoryUI:
    """UI modular para inventario de empleados"""
    
    def __init__(self):
        self._manager = InventoryManager()
        self._persistence = DataPersistence()
        self._history = HistoryManager()
        self._current_type: InventoryType = InventoryType.DIARIO
        
        # Inicializar en session_state si es necesario
        if "employee_inventory_ui" not in st.session_state:
            st.session_state.employee_inventory_ui = {}
    
    def set_inventory_type(self, inv_type: InventoryType):
        """Establece el tipo de inventario activo"""
        if self._current_type != inv_type:
            old_type = self._current_type
            self._current_type = inv_type
            self._manager.handle_type_change(old_type, inv_type)
            NotificationManager.type_change(inv_type.value)
    
    def render(self, usuario: str):
        """Renderiza la interfaz de inventario para empleados"""
        st.header("📦 Gestión de Inventario")
        
        # Selector de tipo de inventario
        selected_type = InventoryTypeSelector.render("employee_inv_type")
        
        # Cambiar tipo si es necesario
        if selected_type != self._current_type:
            self.set_inventory_type(selected_type)
        
        # Cargar datos
        inventario = self._persistence.load_inventory()
        
        if not inventario:
            NotificationManager.error("No se pudo cargar el inventario")
            return
        
        # Mostrar resumen de tipos
        st.subheader("📊 Resumen por Tipos")
        summary = self._manager.get_type_summary()
        ProductSummary.render_type_summary(summary)
        
        # Separador
        st.markdown("---")
        
        # Renderizar por categorías
        st.subheader(f"📝 Cargar Inventario {self._current_type.value}")
        
        for categoria, productos in inventario.items():
            if productos:  # Solo mostrar categorías con productos
                with st.expander(f"📂 {categoria}", expanded=True):
                    if categoria in ["Por Kilos"]:
                        self._render_kilos_category(categoria, productos)
                    else:
                        self._render_numeric_category(categoria, productos)
        
        # Resumen de sesión
        st.markdown("---")
        st.subheader("📋 Resumen de Esta Sesión")
        session_summary = self._manager.get_session_summary()
        ProductSummary.render_session_summary(session_summary, self._current_type.value)
        
        # Métricas
        loaded_count = self._manager.get_loaded_products_count()
        total_count = self._manager.get_total_products_count() 
        MetricCards.render_inventory_metrics(loaded_count, total_count - loaded_count)
    
    def _render_numeric_category(self, categoria: str, productos: Dict[str, Any]):
        """Renderiza categoría numérica (ej: Bebidas con unidades)"""
        st.markdown(f"**{categoria}**")
        
        for producto, datos in productos.items():
            col1, col2, col3 = st.columns([3, 2, 2])
            
            with col1:
                st.write(producto)
            
            with col2:
                # Widget para cantidad
                widget_key = self._manager.get_widget_key(categoria, producto)
                cantidad_actual = self._manager.get_product_quantity(categoria, producto)
                
                cantidad = st.number_input(
                    f"Cantidad",
                    min_value=0,
                    value=cantidad_actual,
                    key=widget_key,
                    label_visibility="collapsed"
                )
            
            with col3:
                # Botón de actualización
                update_key = f"update_{categoria}_{producto}_{self._current_type.value}"
                if ActionButtons.update_button(
                    producto, categoria, self._current_type.value, update_key
                ):
                    if self._manager.save_product(categoria, producto, cantidad):
                        NotificationManager.success(
                            f"{producto} actualizado: {cantidad} unidades"
                        )
                        st.rerun()
    
    def _render_kilos_category(self, categoria: str, productos: Dict[str, Any]):
        """Renderiza categoría de productos que se miden en kilos"""
        st.markdown(f"**{categoria}**")
        
        for producto, datos in productos.items():
            col1, col2, col3 = st.columns([3, 2, 2])
            
            with col1:
                st.write(producto)
            
            with col2:
                # Widget para peso en kilos
                widget_key = self._manager.get_widget_key(categoria, producto)
                peso_actual = self._manager.get_product_quantity(categoria, producto)
                
                peso = st.number_input(
                    f"Kilos",
                    min_value=0.0,
                    step=0.1,
                    value=float(peso_actual) if peso_actual else 0.0,
                    key=widget_key,
                    label_visibility="collapsed",
                    format="%.1f"
                )
            
            with col3:
                # Botón de actualización
                update_key = f"update_{categoria}_{producto}_{self._current_type.value}"
                if ActionButtons.update_button(
                    producto, categoria, self._current_type.value, update_key
                ):
                    if self._manager.save_product(categoria, producto, peso):
                        NotificationManager.success(
                            f"{producto} actualizado: {peso} kg"
                        )
                        st.rerun()