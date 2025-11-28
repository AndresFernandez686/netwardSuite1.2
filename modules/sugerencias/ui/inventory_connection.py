"""
Componentes UI para Sincronización de Inventario en Tiempo Real
Reemplaza el uploader de Excel por conexión directa al módulo de inventario
"""
import streamlit as st
from datetime import datetime
from typing import Dict, Optional
import pandas as pd

try:
    from ..services.inventory_sync_service import inventory_sync_service
    from ..services.inventory_scheduler import InventorySyncScheduler, InventorySyncUI
    SYNC_AVAILABLE = True
except ImportError:
    SYNC_AVAILABLE = False
    st.error("⚠️ Servicio de sincronización no disponible")


class InventoryConnectionUI:
    """Componente UI para conexión al inventario en tiempo real"""
    
    def __init__(self):
        self.sync_service = inventory_sync_service if SYNC_AVAILABLE else None
        self._initialize_scheduler()
    
    def _initialize_scheduler(self):
        """Inicializa el scheduler en session_state"""
        if "inventory_scheduler" not in st.session_state and SYNC_AVAILABLE:
            st.session_state.inventory_scheduler = InventorySyncScheduler(
                sync_service=self.sync_service,
                interval_minutes=5
            )
            st.session_state.scheduler_ui = InventorySyncUI(
                scheduler=st.session_state.inventory_scheduler
            )
    
    def render_connection_status(self, tienda_id: str = "T001"):
        """Renderiza el estado de conexión con el inventario"""
        st.markdown("### 🔌 Conexión con Inventario")
        
        # Intentar leer inventario
        inventory = self.sync_service.read_inventory_from_file(tienda_id)
        metadata = inventory["metadata"]
        
        if metadata["total_productos"] == 0:
            st.warning("""
            ⚠️ **No hay inventario disponible**
            
            El módulo de Inventario no tiene datos para la tienda seleccionada.
            
            **Opciones:**
            1. Ve al módulo de Inventario y carga productos
            2. Selecciona otra tienda
            3. O usa el modo manual (subir Excel)
            """)
            return False
        
        # Mostrar estado de conexión
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🏪 Tienda",
                tienda_id,
                delta="Conectada",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                "📦 Total Productos",
                metadata["total_productos"]
            )
        
        with col3:
            st.metric(
                "📊 Total Bultos",
                metadata["total_bultos"]
            )
        
        with col4:
            # Tiempo desde última actualización
            fecha_sync = datetime.fromisoformat(metadata["fecha_sync"])
            ago = datetime.now() - fecha_sync
            seconds_ago = int(ago.total_seconds())
            
            if seconds_ago < 60:
                time_str = f"{seconds_ago}s"
            elif seconds_ago < 3600:
                time_str = f"{seconds_ago // 60}m"
            else:
                time_str = f"{seconds_ago // 3600}h"
            
            st.metric(
                "🕒 Última Sync",
                time_str,
                delta="Reciente" if seconds_ago < 300 else "Antigua",
                delta_color="normal" if seconds_ago < 300 else "inverse"
            )
        
        return True
    
    def render_inventory_preview(self, tienda_id: str = "T001"):
        """Muestra vista previa del inventario sincronizado"""
        inventory = self.sync_service.read_inventory_from_file(tienda_id)
        
        if not inventory or inventory["metadata"]["total_productos"] == 0:
            return
        
        st.markdown("### 👁️ Vista Previa del Inventario")
        
        # Tabs para Impulsivos y Granel
        tab1, tab2, tab3 = st.tabs(["📦 Impulsivos", "⚖️ Granel", "📊 Estadísticas"])
        
        with tab1:
            self._render_impulsivos_preview(inventory["impulsivo"])
        
        with tab2:
            self._render_granel_preview(inventory["granel"])
        
        with tab3:
            self._render_statistics(inventory)
    
    def _render_impulsivos_preview(self, impulsivos: Dict):
        """Renderiza preview de productos impulsivos"""
        if not impulsivos:
            st.info("No hay productos impulsivos en inventario")
            return
        
        # Convertir a DataFrame
        data = []
        for key, producto in impulsivos.items():
            data.append({
                "Producto": producto.get("producto_original", key),
                "Bultos": producto["bultos"],
                "Unidades": producto.get("unidad", 0),
                "Estado": producto["estado"]
            })
        
        df = pd.DataFrame(data)
        
        # Aplicar colores según estado
        def color_estado(val):
            if val == "SIN STOCK":
                return 'background-color: #ffcccc'
            elif val == "STOCK BAJO":
                return 'background-color: #fff3cd'
            elif val == "STOCK OK":
                return 'background-color: #d4edda'
            return ''
        
        styled_df = df.style.applymap(color_estado, subset=['Estado'])
        
        st.dataframe(styled_df, use_container_width=True, height=400)
        
        # Resumen
        col1, col2, col3 = st.columns(3)
        with col1:
            stock_ok = len([p for p in impulsivos.values() if p["estado"] == "STOCK OK"])
            st.metric("🟢 Stock OK", stock_ok)
        with col2:
            stock_bajo = len([p for p in impulsivos.values() if p["estado"] == "STOCK BAJO"])
            st.metric("🟡 Stock Bajo", stock_bajo)
        with col3:
            sin_stock = len([p for p in impulsivos.values() if p["estado"] == "SIN STOCK"])
            st.metric("🔴 Sin Stock", sin_stock)
    
    def _render_granel_preview(self, granel: Dict):
        """Renderiza preview de productos a granel"""
        if not granel:
            st.info("No hay productos a granel en inventario")
            return
        
        # Convertir a DataFrame
        data = []
        for key, producto in granel.items():
            data.append({
                "Producto": producto.get("producto_original", key),
                "Bultos": producto["bultos"],
                "Cajas Cerradas": producto.get("cajas_cerradas", 0),
                "Cajas Abiertas": producto.get("cajas_abiertas", 0),
                "Kg Totales": round(producto.get("kgs_totales", 0), 2),
                "Estado": producto["estado"]
            })
        
        df = pd.DataFrame(data)
        
        # Aplicar colores según estado
        def color_estado(val):
            if val == "SIN STOCK":
                return 'background-color: #ffcccc'
            elif val == "STOCK BAJO":
                return 'background-color: #fff3cd'
            elif val == "STOCK OK":
                return 'background-color: #d4edda'
            return ''
        
        styled_df = df.style.applymap(color_estado, subset=['Estado'])
        
        st.dataframe(styled_df, use_container_width=True, height=400)
        
        # Resumen
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            stock_ok = len([p for p in granel.values() if p["estado"] == "STOCK OK"])
            st.metric("🟢 Stock OK", stock_ok)
        with col2:
            stock_bajo = len([p for p in granel.values() if p["estado"] == "STOCK BAJO"])
            st.metric("🟡 Stock Bajo", stock_bajo)
        with col3:
            sin_stock = len([p for p in granel.values() if p["estado"] == "SIN STOCK"])
            st.metric("🔴 Sin Stock", sin_stock)
        with col4:
            total_kgs = sum(p.get("kgs_totales", 0) for p in granel.values())
            st.metric("⚖️ Total Kg", round(total_kgs, 1))
    
    def _render_statistics(self, inventory: Dict):
        """Renderiza estadísticas generales del inventario"""
        metadata = inventory["metadata"]
        
        st.markdown("#### 📊 Estadísticas Generales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Distribución por Categoría:**")
            st.metric("Impulsivos", len(inventory["impulsivo"]))
            st.metric("Granel", len(inventory["granel"]))
        
        with col2:
            st.markdown("**Distribución por Estado:**")
            
            # Calcular distribución
            total = metadata["total_productos"]
            if total > 0:
                # Contar estados
                all_products = list(inventory["impulsivo"].values()) + list(inventory["granel"].values())
                stock_ok = len([p for p in all_products if p["estado"] == "STOCK OK"])
                stock_bajo = len([p for p in all_products if p["estado"] == "STOCK BAJO"])
                sin_stock = len([p for p in all_products if p["estado"] == "SIN STOCK"])
                
                st.metric("🟢 Stock OK", f"{stock_ok} ({stock_ok/total*100:.1f}%)")
                st.metric("🟡 Stock Bajo", f"{stock_bajo} ({stock_bajo/total*100:.1f}%)")
                st.metric("🔴 Sin Stock", f"{sin_stock} ({sin_stock/total*100:.1f}%)")
        
        # Información de sincronización
        st.markdown("---")
        st.markdown("**Información de Sincronización:**")
        st.info(f"""
        - **Fecha:** {metadata['fecha_sync']}
        - **Tienda:** {metadata['tienda_id']}
        - **Total Bultos:** {metadata['total_bultos']}
        - **Productos con Stock:** {metadata.get('productos_con_stock', 0)}
        - **Productos sin Stock:** {metadata.get('productos_sin_stock', 0)}
        """)
    
    def render_sync_controls(self, tienda_id: str = "T001"):
        """Renderiza controles de sincronización"""
        st.markdown("### ⚙️ Controles de Sincronización")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Forzar Sincronización Manual", use_container_width=True):
                with st.spinner("Sincronizando..."):
                    success, message = self.sync_service.force_sync(tienda_id)
                    
                    if success:
                        st.success(message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(message)
        
        with col2:
            if st.button("📊 Ver Resumen", use_container_width=True):
                summary = self.sync_service.get_inventory_summary(tienda_id)
                st.json(summary)
        
        # Scheduler automático
        st.markdown("---")
        if "scheduler_ui" in st.session_state:
            st.session_state.scheduler_ui.render_status_widget()
            st.session_state.scheduler_ui.render_controls(tienda_id)
    
    def render_full_page(self, tienda_id: str = "T001"):
        """Renderiza la página completa de conexión al inventario"""
        st.title("🔌 Conexión Directa con Inventario")
        
        st.markdown("""
        Este módulo se conecta automáticamente al **Módulo de Inventario** de BusinessSuite
        para obtener los datos en tiempo real, sin necesidad de subir archivos Excel.
        """)
        
        st.markdown("---")
        
        # Estado de conexión
        is_connected = self.render_connection_status(tienda_id)
        
        if not is_connected:
            st.stop()
        
        st.markdown("---")
        
        # Vista previa
        self.render_inventory_preview(tienda_id)
        
        st.markdown("---")
        
        # Controles
        self.render_sync_controls(tienda_id)
        
        st.markdown("---")
        
        # Información adicional
        with st.expander("ℹ️ Cómo funciona la sincronización"):
            st.markdown("""
            ### 🔄 Sincronización Automática
            
            El sistema sincroniza automáticamente el inventario desde el módulo de Inventario:
            
            1. **Lectura Directa**: Lee los datos directamente del archivo `inventario.json`
            2. **Mapeo Inteligente**: Convierte productos del inventario al formato de sugerencias
            3. **Cálculo de Estados**: Determina automáticamente STOCK OK/BAJO/SIN STOCK
            4. **Cache Local**: Guarda una copia para consultas rápidas
            5. **Actualización Automática**: Sincroniza cada X minutos (configurable)
            
            ### 📊 Estados de Stock
            
            - **SIN STOCK** (🔴): 0 bultos
            - **STOCK BAJO** (🟡): 1-2 bultos (impulsivo) o 1-3 bultos (granel)
            - **STOCK OK** (🟢): 3+ bultos
            
            ### 🎯 Ventajas
            
            - ✅ **Sin errores manuales**: No hay necesidad de subir Excel
            - ✅ **Tiempo real**: Siempre tienes los datos más recientes
            - ✅ **Automatización**: Se sincroniza solo, sin intervención
            - ✅ **Consistencia**: Misma fuente de verdad para todo
            - ✅ **Transparencia**: Ves exactamente qué hay en inventario
            """)


# Instancia global del componente
inventory_connection_ui = InventoryConnectionUI()
