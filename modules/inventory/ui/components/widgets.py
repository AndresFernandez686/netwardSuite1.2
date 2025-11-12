"""
Componentes reutilizables para la UI.
Widgets y elementos comunes del sistema.
"""
import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import date

# Importaciones híbridas para compatibilidad
try:
    from ...core.inventory_types import InventoryType
    from ...core.data_models import QuantityFormatter
except ImportError:
    try:
        from core.inventory_types import InventoryType
        from core.data_models import QuantityFormatter
    except ImportError:
        # Fallback para funcionalidad básica
        class InventoryType:
            DIARIO = "Diario"
            SEMANAL = "Semanal"
            QUINCENAL = "Quincenal"
        
        class QuantityFormatter:
            @staticmethod
            def format_quantity(value):
                return str(value)

class InventoryTypeSelector:
    """Selector de tipo de inventario"""
    
    @staticmethod
    def render(key: str = "tipo_inventario") -> InventoryType:
        """Renderiza selector y retorna InventoryType"""
        tipo_str = st.selectbox(
            "📋 Tipo de inventario",
            ["Diario", "Semanal", "Quincenal"],
            key=key
        )
        return InventoryType.from_string(tipo_str)

class ProductSummary:
    """Componente para mostrar resumen de productos"""
    
    @staticmethod
    def render_type_summary(summary: Dict[str, Dict[str, Any]]):
        """Renderiza resumen por tipos"""
        if not summary:
            st.info("No hay productos cargados.")
            return
        
        for tipo, productos in summary.items():
            if productos:
                st.markdown(f"**🔹 Inventario {tipo}:**")
                for producto_info, cantidad in productos.items():
                    if isinstance(cantidad, (int, float)) and cantidad > 0:
                        st.write(f"   • {producto_info}: **{cantidad}** unidades")
    
    @staticmethod
    def render_session_summary(summary: Dict[str, Dict[str, Any]], current_type: str):
        """Renderiza resumen de sesión actual"""
        if not summary:
            return
        
        st.markdown(f"**🔸 Cargados en esta sesión ({current_type}):**")
        for categoria, productos_cat in summary.items():
            for producto, datos in productos_cat.items():
                if isinstance(datos, dict) and "cantidad" in datos:
                    cantidad = datos["cantidad"]
                    tipo_inv = datos.get("tipo_inventario", current_type)
                    if cantidad > 0:
                        st.write(f"   • {producto} ({categoria}): **{cantidad}** - {tipo_inv}")

class FilterPanel:
    """Panel de filtros reutilizable"""
    
    @staticmethod
    def render_user_filter(users: List[str], key: str = "user_filter") -> str:
        """Renderiza filtro de usuario"""
        return st.selectbox("👤 Usuario", ["Todos"] + users, key=key)
    
    @staticmethod
    def render_type_filter(key: str = "type_filter") -> str:
        """Renderiza filtro de tipo de inventario"""
        return st.selectbox(
            "📋 Tipo de inventario", 
            ["Todos", "Diario", "Semanal", "Quincenal"], 
            key=key
        )
    
    @staticmethod
    def render_date_range(key_prefix: str = "date") -> tuple[date, date]:
        """Renderiza selector de rango de fechas"""
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "📅 Fecha inicio", 
                value=date.today().replace(day=1),
                key=f"{key_prefix}_start"
            )
        
        with col2:
            # Último día del mes
            import calendar
            ultimo_dia = calendar.monthrange(date.today().year, date.today().month)[1]
            end_date = st.date_input(
                "📅 Fecha fin",
                value=date.today().replace(day=ultimo_dia),
                key=f"{key_prefix}_end"
            )
        
        return start_date, end_date

class MetricCards:
    """Componente para mostrar métricas"""
    
    @staticmethod
    def render_inventory_metrics(loaded: int, empty: int):
        """Renderiza métricas de inventario"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("📦 Productos cargados", loaded)
        
        with col2:
            st.metric("📭 Productos sin cargar", empty)
    
    @staticmethod
    def render_user_metrics(total_records: int, unique_products: int, 
                           last_activity: Optional[str] = None):
        """Renderiza métricas de usuario"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📝 Total registros", total_records)
        
        with col2:
            st.metric("🏷️ Productos únicos", unique_products)
        
        with col3:
            if last_activity:
                st.metric("🕐 Última actividad", last_activity)

class StatusIndicators:
    """Indicadores de estado"""
    
    @staticmethod
    def inventory_status(quantity: Any) -> str:
        """Retorna emoji de estado según cantidad"""
        if isinstance(quantity, (int, float)):
            return "🟢" if quantity > 0 else "🔴"
        elif isinstance(quantity, list):
            non_empty = [x for x in quantity if x not in ["Vacío", 0]]
            return "🟢" if non_empty else "🔴"
        return "🟡"  # Desconocido
    
    @staticmethod
    def render_status_badge(status: str, text: str):
        """Renderiza badge de estado"""
        color_map = {
            "success": "🟢",
            "warning": "🟡", 
            "error": "🔴",
            "info": "🔵"
        }
        
        emoji = color_map.get(status, "⚪")
        st.markdown(f"{emoji} **{text}**")

class QuantityDisplay:
    """Componente para mostrar cantidades formateadas"""
    
    @staticmethod
    def render_quantity(cantidad: Any, categoria: str = "") -> str:
        """Renderiza cantidad formateada"""
        formatted = QuantityFormatter.format_quantity(cantidad, categoria)
        return formatted
    
    @staticmethod
    def render_quantity_with_status(cantidad: Any, categoria: str = ""):
        """Renderiza cantidad con indicador de estado"""
        status = StatusIndicators.inventory_status(cantidad)
        formatted = QuantityDisplay.render_quantity(cantidad, categoria)
        
        st.markdown(f"{status} {formatted}")

class ActionButtons:
    """Botones de acción estandarizados"""
    
    @staticmethod
    def update_button(product: str, category: str, inv_type: str, 
                     key: str) -> bool:
        """Botón de actualización estándar"""
        return st.button(
            f"✅ Actualizar {product} ({category}) - {inv_type}",
            key=key,
            type="primary"
        )
    
    @staticmethod
    def delete_button(item: str, key: str) -> bool:
        """Botón de eliminación con confirmación"""
        if st.button(f"🗑️ Eliminar {item}", key=key, type="secondary"):
            return st.checkbox(f"Confirmar eliminación de {item}", key=f"{key}_confirm")
        return False
    
    @staticmethod
    def download_button(data: bytes, filename: str, mime_type: str, 
                       label: str = "📥 Descargar") -> bool:
        """Botón de descarga estándar"""
        return st.download_button(
            label=label,
            data=data,
            file_name=filename,
            mime=mime_type
        )

class NotificationManager:
    """Gestor de notificaciones"""
    
    @staticmethod
    def success(message: str):
        """Notificación de éxito"""
        st.success(f"✅ {message}")
    
    @staticmethod
    def warning(message: str):
        """Notificación de advertencia"""
        st.warning(f"⚠️ {message}")
    
    @staticmethod
    def error(message: str):
        """Notificación de error"""
        st.error(f"❌ {message}")
    
    @staticmethod
    def info(message: str):
        """Notificación informativa"""
        st.info(f"ℹ️ {message}")
    
    @staticmethod
    def type_change(inv_type: str):
        """Notificación específica de cambio de tipo"""
        st.info(f"🔄 Cambiado a inventario **{inv_type}**")

class LoadingManager:
    """Gestor de estados de carga"""
    
    @staticmethod
    def spinner(text: str = "Cargando..."):
        """Spinner de carga"""
        return st.spinner(text)
    
    @staticmethod
    def progress_bar(progress: float, text: str = ""):
        """Barra de progreso"""
        bar = st.progress(progress)
        if text:
            st.text(text)
        return bar