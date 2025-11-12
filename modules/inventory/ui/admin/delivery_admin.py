"""
UI modular para gestión avanzada de delivery de administradores.
Análisis, configuración y administración del sistema de entregas.
"""
import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
import json

from ...core.data_models import DeliveryRecord, Product
from ...data.persistence import DataPersistence
from ...data.history import HistoryManager
from ..components.widgets import (
    FilterPanel, MetricCards, StatusIndicators, 
    NotificationManager, ActionButtons, LoadingManager
)

class AdminDeliveryUI:
    """UI modular para gestión avanzada de delivery de administradores"""
    
    def __init__(self):
        self._persistence = DataPersistence()
        self._history = HistoryManager()
        
        # Inicializar en session_state
        if "admin_delivery_ui" not in st.session_state:
            st.session_state.admin_delivery_ui = {
                "selected_delivery_ids": [],
                "filters_applied": False,
                "bulk_operations": {}
            }
    
    def render(self, usuario: str):
        """Renderiza la interfaz de delivery para administradores"""
        st.header("🚚 Administración de Delivery")
        
        # Pestañas principales
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Dashboard General",
            "📋 Gestión de Entregas", 
            "🏪 Catálogo de Productos",
            "📈 Análisis y Reportes"
        ])
        
        with tab1:
            self._render_dashboard(usuario)
        
        with tab2:
            self._render_delivery_management(usuario)
        
        with tab3:
            self._render_product_catalog(usuario)
        
        with tab4:
            self._render_analytics_reports(usuario)
    
    def _render_dashboard(self, usuario: str):
        """Renderiza dashboard general con métricas clave"""
        st.subheader("📊 Dashboard General de Entregas")
        
        # Cargar datos de entregas
        today = date.today()
        week_start = today - timedelta(days=7)
        month_start = today - timedelta(days=30)
        
        # Métricas principales
        with LoadingManager.spinner("Cargando métricas..."):
            today_deliveries = self._get_deliveries_by_date(today)
            week_deliveries = self._get_deliveries_period(week_start, today)
            month_deliveries = self._get_deliveries_period(month_start, today)
        
        # Mostrar métricas en cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            today_count = len(today_deliveries) if today_deliveries else 0
            st.metric("🚚 Entregas Hoy", today_count)
        
        with col2:
            week_count = len(week_deliveries) if week_deliveries else 0
            st.metric("📅 Esta Semana", week_count)
        
        with col3:
            month_count = len(month_deliveries) if month_deliveries else 0
            st.metric("📊 Este Mes", month_count)
        
        with col4:
            if week_deliveries:
                week_revenue = sum(d.get('total', 0) for d in week_deliveries)
                st.metric("💰 Ingresos Semana", f"${week_revenue:.2f}")
            else:
                st.metric("💰 Ingresos Semana", "$0.00")
        
        # Gráficos de tendencias
        st.markdown("---")
        st.subheader("📈 Tendencias de Entregas")
        
        if month_deliveries:
            self._render_delivery_trends(month_deliveries)
        else:
            st.info("No hay datos suficientes para mostrar tendencias")
        
        # Productos más vendidos
        st.markdown("---")
        st.subheader("🏆 Productos Más Vendidos (Este Mes)")
        
        if month_deliveries:
            self._render_top_products(month_deliveries)
        else:
            st.info("No hay ventas registradas este mes")
        
        # Estado de repartidores/empleados
        st.markdown("---")
        st.subheader("👥 Rendimiento por Empleado")
        
        if week_deliveries:
            self._render_employee_performance(week_deliveries)
        else:
            st.info("No hay entregas registradas esta semana")
    
    def _render_delivery_management(self, usuario: str):
        """Renderiza gestión de entregas individuales"""
        st.subheader("📋 Gestión de Entregas")
        
        # Panel de filtros
        with st.expander("🔧 Filtros de Búsqueda", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Filtro por estado
                status_filter = st.selectbox(
                    "📊 Estado",
                    ["Todas", "Pendiente", "En Proceso", "Entregado", "Cancelado"],
                    key="delivery_status_filter"
                )
            
            with col2:
                # Filtro por empleado
                all_employees = self._get_all_delivery_employees()
                employee_filter = FilterPanel.render_user_filter(
                    all_employees, "delivery_employee_filter"
                )
            
            with col3:
                # Filtro por período
                period = st.selectbox(
                    "📅 Período",
                    ["Hoy", "Esta semana", "Este mes", "Personalizado"],
                    key="delivery_period_filter"
                )
            
            # Rango de fechas personalizado
            if period == "Personalizado":
                start_date, end_date = FilterPanel.render_date_range("delivery_custom")
            else:
                end_date = date.today()
                if period == "Hoy":
                    start_date = end_date
                elif period == "Esta semana":
                    start_date = end_date - timedelta(days=7)
                else:  # Este mes
                    start_date = end_date - timedelta(days=30)
        
        # Cargar entregas filtradas
        filtered_deliveries = self._get_filtered_deliveries(
            start_date, end_date, employee_filter, status_filter
        )
        
        if not filtered_deliveries:
            st.info("No se encontraron entregas con los filtros aplicados")
            return
        
        # Operaciones masivas
        st.markdown("### 🛠️ Operaciones Masivas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Marcar como Entregado"):
                self._bulk_update_status("Entregado")
        
        with col2:
            if st.button("🔄 Cambiar a En Proceso"):
                self._bulk_update_status("En Proceso")
        
        with col3:
            if st.button("❌ Cancelar Seleccionadas"):
                self._bulk_update_status("Cancelado")
        
        # Lista de entregas con selección múltiple
        st.markdown("---")
        st.subheader("📋 Lista de Entregas")
        
        # Headers
        col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 2, 1, 1, 2])
        
        with col1:
            select_all = st.checkbox("Todas", key="select_all_deliveries")
        
        with col2:
            st.write("**Cliente**")
        
        with col3:
            st.write("**Empleado**")
        
        with col4:
            st.write("**Fecha**")
        
        with col5:
            st.write("**Total**")
        
        with col6:
            st.write("**Estado**")
        
        # Filas de entregas
        selected_deliveries = []
        
        for i, delivery in enumerate(filtered_deliveries):
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 2, 1, 1, 2])
            
            with col1:
                selected = st.checkbox(
                    "", 
                    value=select_all,
                    key=f"delivery_select_{i}"
                )
                
                if selected:
                    selected_deliveries.append(delivery)
            
            with col2:
                st.write(delivery.get('cliente', 'N/A'))
            
            with col3:
                st.write(delivery.get('usuario', 'N/A'))
            
            with col4:
                st.write(delivery.get('fecha', 'N/A'))
            
            with col5:
                total = delivery.get('total', 0)
                st.write(f"${total:.2f}")
            
            with col6:
                status = delivery.get('estado', 'Pendiente')
                color = {
                    'Pendiente': '🟡',
                    'En Proceso': '🔵', 
                    'Entregado': '🟢',
                    'Cancelado': '🔴'
                }.get(status, '⚪')
                
                st.write(f"{color} {status}")
            
            # Expandir detalles
            if st.button(f"Ver detalles", key=f"details_{i}"):
                with st.expander(f"Detalles - {delivery.get('cliente', 'N/A')}", expanded=True):
                    self._render_delivery_details(delivery)
        
        # Guardar selecciones en session_state
        st.session_state.admin_delivery_ui["selected_delivery_ids"] = [
            d.get('id', i) for i, d in enumerate(selected_deliveries)
        ]
    
    def _render_product_catalog(self, usuario: str):
        """Renderiza gestión del catálogo de productos"""
        st.subheader("🏪 Gestión de Catálogo de Productos")
        
        # Cargar catálogo actual
        try:
            catalog = self._persistence.load_delivery_catalog()
        except:
            catalog = {}
        
        # Pestañas de catálogo
        cat_tab1, cat_tab2, cat_tab3 = st.tabs([
            "📦 Productos Actuales",
            "➕ Agregar Producto", 
            "📊 Estadísticas"
        ])
        
        with cat_tab1:
            self._render_current_catalog(catalog)
        
        with cat_tab2:
            self._render_add_product_form()
        
        with cat_tab3:
            self._render_catalog_statistics(catalog)
    
    def _render_analytics_reports(self, usuario: str):
        """Renderiza análisis y reportes avanzados"""
        st.subheader("📈 Análisis y Reportes Avanzados")
        
        # Configuración del período de análisis
        col1, col2 = st.columns(2)
        
        with col1:
            analysis_period = st.selectbox(
                "Período de análisis",
                ["Última semana", "Último mes", "Últimos 3 meses", "Último año"],
                key="analytics_period"
            )
        
        with col2:
            report_type = st.selectbox(
                "Tipo de reporte",
                ["Ventas por producto", "Rendimiento empleados", "Análisis temporal", "Reporte completo"],
                key="analytics_type"
            )
        
        # Generar análisis según configuración
        end_date = date.today()
        
        if analysis_period == "Última semana":
            start_date = end_date - timedelta(days=7)
        elif analysis_period == "Último mes":
            start_date = end_date - timedelta(days=30)
        elif analysis_period == "Últimos 3 meses":
            start_date = end_date - timedelta(days=90)
        else:  # Último año
            start_date = end_date - timedelta(days=365)
        
        # Cargar datos del período
        period_data = self._get_deliveries_period(start_date, end_date)
        
        if not period_data:
            st.warning(f"No hay datos disponibles para el período seleccionado")
            return
        
        # Generar reporte según tipo
        if report_type == "Ventas por producto":
            self._render_product_sales_analysis(period_data)
        elif report_type == "Rendimiento empleados":
            self._render_employee_analysis(period_data)
        elif report_type == "Análisis temporal":
            self._render_temporal_analysis(period_data, start_date, end_date)
        else:  # Reporte completo
            self._render_complete_report(period_data, start_date, end_date)
        
        # Botones de exportación
        st.markdown("---")
        st.subheader("📥 Exportar Reportes")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Exportar PDF"):
                self._export_pdf_report(period_data, report_type)
        
        with col2:
            if st.button("📊 Exportar Excel"):
                self._export_excel_report(period_data, report_type)
        
        with col3:
            if st.button("📋 Exportar CSV"):
                csv_data = self._export_csv_report(period_data)
                if csv_data:
                    st.download_button(
                        "💾 Descargar CSV",
                        csv_data,
                        f"reporte_delivery_{start_date}_{end_date}.csv",
                        "text/csv"
                    )
    
    def _render_delivery_trends(self, deliveries: List[Dict[str, Any]]):
        """Renderiza gráfico de tendencias de entregas"""
        try:
            import pandas as pd
            
            # Preparar datos por día
            daily_data = {}
            for delivery in deliveries:
                fecha = delivery.get('fecha', '')
                if fecha:
                    if fecha not in daily_data:
                        daily_data[fecha] = {'count': 0, 'revenue': 0}
                    daily_data[fecha]['count'] += 1
                    daily_data[fecha]['revenue'] += delivery.get('total', 0)
            
            # Crear DataFrame
            df = pd.DataFrame([
                {'Fecha': fecha, 'Entregas': data['count'], 'Ingresos': data['revenue']}
                for fecha, data in sorted(daily_data.items())
            ])
            
            # Mostrar gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Entregas por día**")
                st.line_chart(df.set_index('Fecha')['Entregas'])
            
            with col2:
                st.markdown("**Ingresos por día**")
                st.line_chart(df.set_index('Fecha')['Ingresos'])
                
        except ImportError:
            st.warning("Instala pandas para ver gráficos de tendencias")
    
    def _render_top_products(self, deliveries: List[Dict[str, Any]]):
        """Renderiza productos más vendidos"""
        product_stats = {}
        
        for delivery in deliveries:
            productos = delivery.get('productos', [])
            for producto in productos:
                nombre = producto.get('producto', 'Desconocido')
                cantidad = producto.get('cantidad', 0)
                subtotal = producto.get('subtotal', 0)
                
                if nombre not in product_stats:
                    product_stats[nombre] = {'cantidad': 0, 'revenue': 0, 'count': 0}
                
                product_stats[nombre]['cantidad'] += cantidad
                product_stats[nombre]['revenue'] += subtotal
                product_stats[nombre]['count'] += 1
        
        # Ordenar por ingresos
        top_products = sorted(
            product_stats.items(),
            key=lambda x: x[1]['revenue'],
            reverse=True
        )[:10]
        
        # Mostrar tabla
        for i, (producto, stats) in enumerate(top_products):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**{i+1}. {producto}**")
            
            with col2:
                st.write(f"Cantidad: {stats['cantidad']}")
            
            with col3:
                st.write(f"Ventas: {stats['count']}")
            
            with col4:
                st.write(f"Ingresos: ${stats['revenue']:.2f}")
    
    def _render_employee_performance(self, deliveries: List[Dict[str, Any]]):
        """Renderiza rendimiento por empleado"""
        employee_stats = {}
        
        for delivery in deliveries:
            usuario = delivery.get('usuario', 'Desconocido')
            total = delivery.get('total', 0)
            
            if usuario not in employee_stats:
                employee_stats[usuario] = {'deliveries': 0, 'revenue': 0}
            
            employee_stats[usuario]['deliveries'] += 1
            employee_stats[usuario]['revenue'] += total
        
        # Mostrar métricas por empleado
        for usuario, stats in employee_stats.items():
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**{usuario}**")
            
            with col2:
                st.metric("Entregas", stats['deliveries'])
            
            with col3:
                st.metric("Ingresos", f"${stats['revenue']:.2f}")
    
    # Métodos auxiliares para carga de datos
    def _get_deliveries_by_date(self, target_date: date) -> List[Dict[str, Any]]:
        """Obtiene entregas de una fecha específica"""
        return self._history.get_deliveries_by_date(target_date)
    
    def _get_deliveries_period(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Obtiene entregas de un período"""
        return self._history.get_deliveries_period(start_date, end_date)
    
    def _get_all_delivery_employees(self) -> List[str]:
        """Obtiene lista de todos los empleados que han hecho entregas"""
        return self._history.get_delivery_employees()
    
    def _get_filtered_deliveries(self, start_date: date, end_date: date, 
                                employee: str, status: str) -> List[Dict[str, Any]]:
        """Obtiene entregas filtradas"""
        deliveries = self._get_deliveries_period(start_date, end_date)
        
        if employee and employee != "Todos":
            deliveries = [d for d in deliveries if d.get('usuario') == employee]
        
        if status and status != "Todas":
            deliveries = [d for d in deliveries if d.get('estado', 'Pendiente') == status]
        
        return deliveries
    
    def _render_delivery_details(self, delivery: Dict[str, Any]):
        """Renderiza detalles de una entrega específica"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Cliente:** {delivery.get('cliente', 'N/A')}")
            st.write(f"**Teléfono:** {delivery.get('telefono', 'N/A')}")
            st.write(f"**Dirección:** {delivery.get('direccion', 'N/A')}")
        
        with col2:
            st.write(f"**Empleado:** {delivery.get('usuario', 'N/A')}")
            st.write(f"**Fecha:** {delivery.get('fecha', 'N/A')}")
            st.write(f"**Hora:** {delivery.get('hora', 'N/A')}")
        
        if delivery.get('observaciones'):
            st.write(f"**Observaciones:** {delivery['observaciones']}")
        
        # Productos
        productos = delivery.get('productos', [])
        if productos:
            st.markdown("**Productos:**")
            for producto in productos:
                st.write(
                    f"• {producto.get('producto', 'N/A')} - "
                    f"{producto.get('cantidad', 0)} {producto.get('unidad', 'unidades')} - "
                    f"${producto.get('subtotal', 0):.2f}"
                )
        
        st.write(f"**Total:** ${delivery.get('total', 0):.2f}")
    
    def _bulk_update_status(self, new_status: str):
        """Actualiza estado de entregas seleccionadas"""
        selected_ids = st.session_state.admin_delivery_ui.get("selected_delivery_ids", [])
        
        if not selected_ids:
            NotificationManager.warning("No hay entregas seleccionadas")
            return
        
        # Aquí iría la lógica para actualizar el estado en la base de datos
        NotificationManager.success(f"Estado actualizado a '{new_status}' para {len(selected_ids)} entregas")
    
    def _render_current_catalog(self, catalog: Dict[str, Any]):
        """Renderiza catálogo actual de productos"""
        if not catalog:
            st.info("No hay productos en el catálogo")
            return
        
        for categoria, productos in catalog.items():
            st.markdown(f"### 📂 {categoria}")
            
            for producto, datos in productos.items():
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.write(f"**{producto}**")
                
                with col2:
                    precio = datos.get('precio', 0)
                    st.write(f"${precio:.2f}")
                
                with col3:
                    disponible = datos.get('disponible', True)
                    status = "✅ Disponible" if disponible else "❌ No disponible"
                    st.write(status)
                
                with col4:
                    if st.button(f"Editar", key=f"edit_{categoria}_{producto}"):
                        st.session_state[f"edit_product_{categoria}_{producto}"] = True
    
    def _render_add_product_form(self):
        """Renderiza formulario para agregar producto"""
        st.markdown("### ➕ Agregar Nuevo Producto")
        
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                categoria = st.text_input("Categoría")
                producto = st.text_input("Nombre del Producto")
            
            with col2:
                precio = st.number_input("Precio", min_value=0.0, step=0.01, format="%.2f")
                disponible = st.checkbox("Disponible", value=True)
            
            descripcion = st.text_area("Descripción (opcional)")
            
            if st.form_submit_button("➕ Agregar Producto"):
                if categoria and producto:
                    # Aquí iría la lógica para agregar al catálogo
                    NotificationManager.success(f"Producto '{producto}' agregado a '{categoria}'")
                else:
                    NotificationManager.error("Categoria y nombre del producto son obligatorios")
    
    def _render_catalog_statistics(self, catalog: Dict[str, Any]):
        """Renderiza estadísticas del catálogo"""
        if not catalog:
            st.info("No hay datos para mostrar estadísticas")
            return
        
        total_products = sum(len(productos) for productos in catalog.values())
        total_categories = len(catalog)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("📦 Total Productos", total_products)
        
        with col2:
            st.metric("📂 Categorías", total_categories)
        
        # Productos por categoría
        st.markdown("### 📊 Productos por Categoría")
        
        for categoria, productos in catalog.items():
            st.write(f"**{categoria}:** {len(productos)} productos")
    
    # Métodos de análisis (simplificados para el ejemplo)
    def _render_product_sales_analysis(self, data: List[Dict[str, Any]]):
        """Renderiza análisis de ventas por producto"""
        st.markdown("### 📊 Análisis de Ventas por Producto")
        # Implementación del análisis
        
    def _render_employee_analysis(self, data: List[Dict[str, Any]]):
        """Renderiza análisis de rendimiento de empleados"""
        st.markdown("### 👥 Análisis de Rendimiento de Empleados")
        # Implementación del análisis
        
    def _render_temporal_analysis(self, data: List[Dict[str, Any]], start_date: date, end_date: date):
        """Renderiza análisis temporal"""
        st.markdown("### 📅 Análisis Temporal")
        # Implementación del análisis
        
    def _render_complete_report(self, data: List[Dict[str, Any]], start_date: date, end_date: date):
        """Renderiza reporte completo"""
        st.markdown("### 📋 Reporte Completo")
        # Implementación del reporte completo
    
    # Métodos de exportación (simplificados)
    def _export_pdf_report(self, data: List[Dict[str, Any]], report_type: str):
        """Exporta reporte en PDF"""
        NotificationManager.info("Funcionalidad de exportación PDF próximamente")
    
    def _export_excel_report(self, data: List[Dict[str, Any]], report_type: str):
        """Exporta reporte en Excel"""
        NotificationManager.info("Funcionalidad de exportación Excel próximamente")
    
    def _export_csv_report(self, data: List[Dict[str, Any]]) -> str:
        """Exporta reporte en CSV"""
        # Implementación básica de CSV
        if not data:
            return ""
        
        csv_lines = ["Cliente,Empleado,Fecha,Total,Estado"]
        
        for delivery in data:
            line = f"{delivery.get('cliente', '')},{delivery.get('usuario', '')},{delivery.get('fecha', '')},{delivery.get('total', 0)},{delivery.get('estado', 'Pendiente')}"
            csv_lines.append(line)
        
        return "\n".join(csv_lines)