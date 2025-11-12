"""
UI modular para inventario de administradores.
Gestión avanzada de inventario con múltiples tipos.
"""
import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import date

# Importaciones híbridas
try:
    from ...core.inventory_types import InventoryType, TypedInventoryManager
    from ...core.inventory_manager import InventoryManager
    from ...core.data_models import InventoryRecord, Product
    from ...data.persistence import DataPersistence
    from ...data.history import HistoryManager
    from ..components.widgets import (
        InventoryTypeSelector, ProductSummary, MetricCards, FilterPanel,
        StatusIndicators, NotificationManager, ActionButtons, LoadingManager
    )
except ImportError:
    try:
        from core.inventory_types import InventoryType, TypedInventoryManager
        from core.inventory_manager import InventoryManager
        from core.data_models import InventoryRecord, Product
        from data.persistence import DataPersistence
        from data.history import HistoryManager
        from ui.components.widgets import (
            InventoryTypeSelector, ProductSummary, MetricCards, FilterPanel,
            StatusIndicators, NotificationManager, ActionButtons, LoadingManager
        )
    except ImportError:
        # Fallback básico para funcionalidad mínima
        class InventoryType:
            DIARIO = "Diario"
            SEMANAL = "Semanal"
            QUINCENAL = "Quincenal"
        
        class TypedInventoryManager:
            pass
        
        class InventoryManager:
            pass
        
        class InventoryRecord:
            pass
        
        class Product:
            pass
        
        class DataPersistence:
            def load_inventory(self):
                return {}
        
        class HistoryManager:
            pass
        
        # Mock widgets básicos
        class InventoryTypeSelector:
            @staticmethod
            def render(key="inventory_type"):
                return st.selectbox("Tipo de Inventario", ["Diario", "Semanal", "Quincenal"], key=key)
        
        class ProductSummary:
            pass
        
        class MetricCards:
            pass
        
        class FilterPanel:
            pass
        
        class StatusIndicators:
            pass
        
        class NotificationManager:
            @staticmethod
            def success(msg):
                st.success(msg)
            
            @staticmethod
            def error(msg):
                st.error(msg)
            
            @staticmethod
            def info(msg):
                st.info(msg)
        
        class ActionButtons:
            pass
        
        class LoadingManager:
            class spinner:
                def __init__(self, text):
                    pass
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    pass

class AdminInventoryUI:
    """UI modular para inventario de administradores"""
    
    def __init__(self):
        self._manager = InventoryManager()
        self._persistence = DataPersistence()
        self._history = HistoryManager()
        self._current_type: InventoryType = InventoryType.DIARIO
        
        # Inicializar en session_state si es necesario
        if "admin_inventory_ui" not in st.session_state:
            st.session_state.admin_inventory_ui = {}
    
    def set_inventory_type(self, inv_type: InventoryType):
        """Establece el tipo de inventario activo"""
        if self._current_type != inv_type:
            old_type = self._current_type
            self._current_type = inv_type
            self._manager.handle_type_change(old_type, inv_type)
            NotificationManager.type_change(inv_type.value)
    
    def render(self, usuario: str):
        """Renderiza la interfaz de inventario para administradores"""
        st.header("🔧 Administración de Inventario")
        
        # Pestañas principales
        tab1, tab2, tab3, tab4 = st.tabs([
            "📦 Vista General", 
            "📝 Edición Masiva", 
            "🔄 Comparación de Tipos",
            "⚙️ Configuración"
        ])
        
        with tab1:
            self._render_overview(usuario)
        
        with tab2:
            self._render_bulk_edit(usuario)
        
        with tab3:
            self._render_type_comparison(usuario)
        
        with tab4:
            self._render_configuration(usuario)
    
    def _render_overview(self, usuario: str):
        """Renderiza vista general del inventario"""
        st.subheader("📊 Vista General del Inventario")
        
        # Selector de tipo
        selected_type = InventoryTypeSelector.render("admin_inv_type")
        
        if selected_type != self._current_type:
            self.set_inventory_type(selected_type)
        
        # Cargar datos
        inventario = self._persistence.load_inventory()
        
        if not inventario:
            NotificationManager.error("No se pudo cargar el inventario")
            return
        
        # Resumen por tipos
        st.markdown("### 📈 Resumen por Tipos de Inventario")
        summary = self._manager.get_type_summary()
        ProductSummary.render_type_summary(summary)
        
        # Métricas generales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_productos = self._manager.get_total_products_count()
            st.metric("🏷️ Total Productos", total_productos)
        
        with col2:
            loaded_count = self._manager.get_loaded_products_count()
            st.metric("📦 Cargados", loaded_count)
        
        with col3:
            empty_count = total_productos - loaded_count
            st.metric("📭 Sin Cargar", empty_count)
        
        with col4:
            coverage = (loaded_count / total_productos * 100) if total_productos > 0 else 0
            st.metric("📊 Cobertura", f"{coverage:.1f}%")
        
        # Vista detallada por categorías
        st.markdown("---")
        st.subheader(f"📂 Inventario {self._current_type.value} - Vista Detallada")
        
        for categoria, productos in inventario.items():
            if productos:
                with st.expander(f"📁 {categoria} ({len(productos)} productos)"):
                    self._render_category_details(categoria, productos)
    
    def _render_category_details(self, categoria: str, productos: Dict[str, Any]):
        """Renderiza detalles de una categoría"""
        # Crear DataFrame para mejor visualización
        data = []
        
        for producto, datos in productos.items():
            # Obtener cantidades por tipo
            diario = self._manager.get_specific_type_quantity(
                InventoryType.DIARIO, categoria, producto
            )
            semanal = self._manager.get_specific_type_quantity(
                InventoryType.SEMANAL, categoria, producto
            )
            quincenal = self._manager.get_specific_type_quantity(
                InventoryType.QUINCENAL, categoria, producto
            )
            
            data.append({
                "Producto": producto,
                "Diario": diario,
                "Semanal": semanal,
                "Quincenal": quincenal,
                "Estado": StatusIndicators.inventory_status(
                    self._manager.get_product_quantity(categoria, producto)
                )
            })
        
        if data:
            try:
                import pandas as pd
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
            except ImportError:
                # Fallback sin pandas
                for item in data:
                    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                    
                    with col1:
                        st.write(item["Producto"])
                    with col2:
                        st.write(item["Diario"])
                    with col3:
                        st.write(item["Semanal"])
                    with col4:
                        st.write(item["Quincenal"])
                    with col5:
                        st.write(item["Estado"])
    
    def _render_bulk_edit(self, usuario: str):
        """Renderiza interfaz de edición masiva"""
        st.subheader("📝 Edición Masiva de Inventario")
        
        # Selector de tipo
        selected_type = InventoryTypeSelector.render("admin_bulk_type")
        
        # Selector de categoría
        inventario = self._persistence.load_inventory()
        if not inventario:
            return
        
        categoria_selected = st.selectbox(
            "📂 Categoría",
            list(inventario.keys()),
            key="admin_bulk_categoria"
        )
        
        if categoria_selected:
            productos = inventario[categoria_selected]
            
            st.markdown(f"**Editando: {categoria_selected} - {selected_type.value}**")
            
            # Formulario de edición masiva
            with st.form(f"bulk_edit_{categoria_selected}_{selected_type.value}"):
                updates = {}
                
                for producto in productos.keys():
                    col1, col2 = st.columns([3, 2])
                    
                    with col1:
                        st.write(producto)
                    
                    with col2:
                        current_value = self._manager.get_specific_type_quantity(
                            selected_type, categoria_selected, producto
                        )
                        
                        if categoria_selected == "Por Kilos":
                            new_value = st.number_input(
                                f"Cantidad (kg)",
                                value=float(current_value) if current_value else 0.0,
                                step=0.1,
                                key=f"bulk_{producto}",
                                format="%.1f"
                            )
                        else:
                            new_value = st.number_input(
                                f"Cantidad",
                                value=int(current_value) if current_value else 0,
                                min_value=0,
                                key=f"bulk_{producto}"
                            )
                        
                        updates[producto] = new_value
                
                # Botón de aplicar cambios
                if st.form_submit_button("💾 Aplicar Cambios Masivos", type="primary"):
                    success_count = 0
                    
                    for producto, cantidad in updates.items():
                        if self._manager.save_specific_type_product(
                            selected_type, categoria_selected, producto, cantidad
                        ):
                            success_count += 1
                    
                    if success_count > 0:
                        NotificationManager.success(
                            f"✅ {success_count} productos actualizados en {selected_type.value}"
                        )
                        
                        # Registrar en historial
                        record = InventoryRecord(
                            fecha=date.today(),
                            usuario=usuario,
                            categoria=categoria_selected,
                            tipo_inventario=selected_type.value,
                            productos_actualizados=success_count,
                            observaciones=f"Edición masiva - {categoria_selected}"
                        )
                        self._history.add_inventory_record(record)
                        
                        st.rerun()
                    else:
                        NotificationManager.error("❌ No se pudieron actualizar los productos")
    
    def _render_type_comparison(self, usuario: str):
        """Renderiza comparación entre tipos de inventario"""
        st.subheader("🔄 Comparación de Tipos de Inventario")
        
        # Cargar datos
        inventario = self._persistence.load_inventory()
        if not inventario:
            return
        
        # Selector de categoría
        categoria_selected = st.selectbox(
            "📂 Categoría para comparar",
            list(inventario.keys()),
            key="admin_compare_categoria"
        )
        
        if categoria_selected:
            st.markdown(f"**Comparando: {categoria_selected}**")
            
            productos = inventario[categoria_selected]
            
            # Crear tabla comparativa
            comparison_data = []
            
            for producto in productos.keys():
                diario = self._manager.get_specific_type_quantity(
                    InventoryType.DIARIO, categoria_selected, producto
                )
                semanal = self._manager.get_specific_type_quantity(
                    InventoryType.SEMANAL, categoria_selected, producto
                )
                quincenal = self._manager.get_specific_type_quantity(
                    InventoryType.QUINCENAL, categoria_selected, producto
                )
                
                comparison_data.append({
                    "Producto": producto,
                    "📅 Diario": diario,
                    "📊 Semanal": semanal,
                    "📈 Quincenal": quincenal,
                    "🔍 Diferencia D-S": abs(diario - semanal) if diario and semanal else "N/A",
                    "🔍 Diferencia S-Q": abs(semanal - quincenal) if semanal and quincenal else "N/A"
                })
            
            # Mostrar tabla
            if comparison_data:
                try:
                    import pandas as pd
                    df = pd.DataFrame(comparison_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Estadísticas básicas
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        diario_total = sum(item["📅 Diario"] for item in comparison_data 
                                         if isinstance(item["📅 Diario"], (int, float)))
                        st.metric("📅 Total Diario", diario_total)
                    
                    with col2:
                        semanal_total = sum(item["📊 Semanal"] for item in comparison_data 
                                          if isinstance(item["📊 Semanal"], (int, float)))
                        st.metric("📊 Total Semanal", semanal_total)
                    
                    with col3:
                        quincenal_total = sum(item["📈 Quincenal"] for item in comparison_data 
                                            if isinstance(item["📈 Quincenal"], (int, float)))
                        st.metric("📈 Total Quincenal", quincenal_total)
                        
                except ImportError:
                    # Fallback sin pandas
                    for item in comparison_data:
                        st.write(f"**{item['Producto']}** - D:{item['📅 Diario']} S:{item['📊 Semanal']} Q:{item['📈 Quincenal']}")
    
    def _render_configuration(self, usuario: str):
        """Renderiza configuración del sistema"""
        st.subheader("⚙️ Configuración del Sistema")
        
        # Gestión de productos
        st.markdown("### 🏷️ Gestión de Productos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reiniciar Inventario Actual"):
                if st.checkbox("Confirmar reinicio", key="confirm_reset"):
                    if self._manager.reset_current_type():
                        NotificationManager.success("Inventario reiniciado")
                        st.rerun()
        
        with col2:
            if st.button("📥 Exportar Configuración"):
                config_data = self._manager.export_configuration()
                if config_data:
                    st.download_button(
                        "💾 Descargar Configuración",
                        config_data,
                        f"inventario_config_{date.today()}.json",
                        "application/json"
                    )
        
        # Backup y restauración
        st.markdown("---")
        st.markdown("### 💾 Backup y Restauración")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Crear Backup"):
                backup_file = self._persistence.create_backup()
                if backup_file:
                    NotificationManager.success(f"Backup creado: {backup_file}")
        
        with col2:
            uploaded_file = st.file_uploader(
                "📤 Restaurar desde Backup", 
                type=['json'],
                key="restore_backup"
            )
            
            if uploaded_file and st.button("🔄 Restaurar"):
                if self._persistence.restore_from_backup(uploaded_file):
                    NotificationManager.success("Backup restaurado exitosamente")
                    st.rerun()
                else:
                    NotificationManager.error("Error al restaurar backup")