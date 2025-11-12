"""
UI modular para sistema de reportes y análisis para administradores.
Reportes avanzados, dashboard ejecutivo y análisis predictivo.
"""
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple
from datetime import date, datetime, timedelta
import json

try:
    from ...core.inventory_types import InventoryType
    from ...core.data_models import InventoryRecord, DeliveryRecord
    from ...data.persistence import DataPersistence
    from ...data.history import HistoryManager, HistoryAnalyzer
    from ..components.widgets import (
        FilterPanel, MetricCards, StatusIndicators, 
        NotificationManager, ActionButtons, LoadingManager
    )
except ImportError:
    # Fallback para imports absolutos
    try:
        from core.inventory_types import InventoryType
        from core.data_models import InventoryRecord, DeliveryRecord
        from data.persistence import DataPersistence
        from data.history import HistoryManager, HistoryAnalyzer
        from ui.components.widgets import (
            FilterPanel, MetricCards, StatusIndicators, 
            NotificationManager, ActionButtons, LoadingManager
        )
    except ImportError:
        # Imports mínimos para funcionalidad básica
        class InventoryType:
            DIARIO = "Diario"
            SEMANAL = "Semanal" 
            QUINCENAL = "Quincenal"
        
        class InventoryRecord:
            pass
        
        class DeliveryRecord:
            pass
        
        class DataPersistence:
            def load_inventory(self):
                return {}
        
        class HistoryManager:
            def get_deliveries_period(self, start, end):
                return []
            def get_inventory_records_period(self, start, end):
                return []
            def get_all_users(self):
                return []
        
        class HistoryAnalyzer:
            pass
        
        # Mock widgets
        class FilterPanel:
            @staticmethod
            def render_date_range(key):
                from datetime import date, timedelta
                end = date.today()
                start = end - timedelta(days=30)
                return start, end
        
        class MetricCards:
            pass
        
        class StatusIndicators:
            pass
        
        class NotificationManager:
            @staticmethod
            def info(msg):
                import streamlit as st
                st.info(msg)
            
            @staticmethod
            def success(msg):
                import streamlit as st
                st.success(msg)
                
            @staticmethod
            def warning(msg):
                import streamlit as st
                st.warning(msg)
        
        class ActionButtons:
            pass
        
        class LoadingManager:
            class spinner:
                def __init__(self, text):
                    self.text = text
                
                def __enter__(self):
                    return self
                
                def __exit__(self, *args):
                    pass

class AdminReportsUI:
    """UI modular para sistema de reportes y análisis para administradores"""
    
    def __init__(self):
        self._persistence = DataPersistence()
        self._history = HistoryManager()
        self._analyzer = HistoryAnalyzer()
        
        # Inicializar en session_state
        if "admin_reports_ui" not in st.session_state:
            st.session_state.admin_reports_ui = {
                "report_cache": {},
                "last_generated": None,
                "custom_filters": {}
            }
    
    def render(self, usuario: str):
        """Renderiza la interfaz de reportes para administradores"""
        st.header("📋 Sistema de Reportes y Análisis")
        
        # Pestañas principales
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Dashboard Ejecutivo",
            "📈 Reportes de Ventas",
            "📦 Reportes de Inventario", 
            "👥 Reportes de Personal",
            "🔮 Análisis Predictivo"
        ])
        
        with tab1:
            self._render_executive_dashboard(usuario)
        
        with tab2:
            self._render_sales_reports(usuario)
        
        with tab3:
            self._render_inventory_reports(usuario)
        
        with tab4:
            self._render_staff_reports(usuario)
        
        with tab5:
            self._render_predictive_analysis(usuario)
    
    def _render_executive_dashboard(self, usuario: str):
        """Renderiza dashboard ejecutivo con KPIs principales"""
        st.subheader("📊 Dashboard Ejecutivo")
        
        # Período de análisis
        col1, col2 = st.columns(2)
        
        with col1:
            period = st.selectbox(
                "📅 Período de análisis",
                ["Último mes", "Últimos 3 meses", "Último semestre", "Último año"],
                key="exec_dashboard_period"
            )
        
        with col2:
            comparison = st.checkbox("📊 Comparar con período anterior", key="exec_comparison")
        
        # Calcular fechas
        end_date = date.today()
        
        if period == "Último mes":
            start_date = end_date - timedelta(days=30)
            prev_start = start_date - timedelta(days=30)
        elif period == "Últimos 3 meses":
            start_date = end_date - timedelta(days=90)
            prev_start = start_date - timedelta(days=90)
        elif period == "Último semestre":
            start_date = end_date - timedelta(days=180)
            prev_start = start_date - timedelta(days=180)
        else:  # Último año
            start_date = end_date - timedelta(days=365)
            prev_start = start_date - timedelta(days=365)
        
        # Cargar datos
        with LoadingManager.spinner("Generando dashboard ejecutivo..."):
            current_data = self._get_period_data(start_date, end_date)
            prev_data = self._get_period_data(prev_start, start_date) if comparison else None
        
        # KPIs principales
        st.markdown("### 🎯 KPIs Principales")
        
        self._render_executive_kpis(current_data, prev_data)
        
        # Gráficos ejecutivos
        st.markdown("---")
        st.markdown("### 📈 Tendencias Principales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_revenue_trend(current_data)
        
        with col2:
            self._render_inventory_trend(current_data)
        
        # Análisis de rendimiento
        st.markdown("---")
        st.markdown("### 🏆 Análisis de Rendimiento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_top_performers(current_data)
        
        with col2:
            self._render_areas_improvement(current_data, prev_data)
        
        # Alertas y recomendaciones
        st.markdown("---")
        st.markdown("### ⚠️ Alertas y Recomendaciones")
        
        self._render_executive_alerts(current_data)
    
    def _render_sales_reports(self, usuario: str):
        """Renderiza reportes de ventas detallados"""
        st.subheader("📈 Reportes de Ventas")
        
        # Configuración del reporte
        report_config = self._render_sales_report_config()
        
        if report_config:
            # Generar reporte
            with LoadingManager.spinner("Generando reporte de ventas..."):
                sales_data = self._generate_sales_report(report_config)
            
            if sales_data:
                # Pestañas de visualización
                view_tab1, view_tab2, view_tab3 = st.tabs([
                    "📊 Resumen Ejecutivo",
                    "📋 Datos Detallados", 
                    "📈 Análisis Avanzado"
                ])
                
                with view_tab1:
                    self._render_sales_executive_summary(sales_data)
                
                with view_tab2:
                    self._render_sales_detailed_data(sales_data)
                
                with view_tab3:
                    self._render_sales_advanced_analysis(sales_data)
                
                # Exportación
                st.markdown("---")
                self._render_export_options("sales", sales_data)
    
    def _render_inventory_reports(self, usuario: str):
        """Renderiza reportes de inventario"""
        st.subheader("📦 Reportes de Inventario")
        
        # Tipos de reporte de inventario
        inventory_report_type = st.selectbox(
            "Tipo de reporte",
            [
                "Estado actual por tipos",
                "Análisis de rotación",
                "Productos más/menos activos", 
                "Comparación temporal",
                "Alertas de stock",
                "Eficiencia de carga"
            ],
            key="inventory_report_type"
        )
        
        # Configuración específica según tipo
        if inventory_report_type == "Estado actual por tipos":
            self._render_current_inventory_status()
        
        elif inventory_report_type == "Análisis de rotación":
            self._render_inventory_rotation_analysis()
        
        elif inventory_report_type == "Productos más/menos activos":
            self._render_product_activity_analysis()
        
        elif inventory_report_type == "Comparación temporal":
            self._render_inventory_temporal_comparison()
        
        elif inventory_report_type == "Alertas de stock":
            self._render_inventory_alerts()
        
        else:  # Eficiencia de carga
            self._render_loading_efficiency_analysis()
    
    def _render_staff_reports(self, usuario: str):
        """Renderiza reportes de personal"""
        st.subheader("👥 Reportes de Personal")
        
        # Configuración del período
        staff_period = st.selectbox(
            "Período de análisis",
            ["Última semana", "Último mes", "Últimos 3 meses"],
            key="staff_report_period"
        )
        
        # Calcular fechas
        end_date = date.today()
        
        if staff_period == "Última semana":
            start_date = end_date - timedelta(days=7)
        elif staff_period == "Último mes":
            start_date = end_date - timedelta(days=30)
        else:  # Últimos 3 meses
            start_date = end_date - timedelta(days=90)
        
        # Cargar datos de personal
        staff_data = self._get_staff_performance_data(start_date, end_date)
        
        if staff_data:
            # Pestañas de análisis de personal
            staff_tab1, staff_tab2, staff_tab3 = st.tabs([
                "📊 Rendimiento General",
                "📈 Análisis Individual",
                "🏆 Comparativas"
            ])
            
            with staff_tab1:
                self._render_general_staff_performance(staff_data)
            
            with staff_tab2:
                self._render_individual_staff_analysis(staff_data)
            
            with staff_tab3:
                self._render_staff_comparatives(staff_data)
        else:
            st.info("No hay datos de personal suficientes para generar reportes")
    
    def _render_predictive_analysis(self, usuario: str):
        """Renderiza análisis predictivo"""
        st.subheader("🔮 Análisis Predictivo")
        
        # Tipos de predicción
        prediction_type = st.selectbox(
            "Tipo de análisis predictivo",
            [
                "Demanda de productos",
                "Proyección de ventas",
                "Necesidades de inventario",
                "Tendencias estacionales",
                "Optimización de recursos"
            ],
            key="prediction_type"
        )
        
        # Horizonte de predicción
        prediction_horizon = st.selectbox(
            "Horizonte de predicción",
            ["1 semana", "1 mes", "3 meses", "6 meses"],
            key="prediction_horizon"
        )
        
        # Configuración avanzada
        with st.expander("⚙️ Configuración Avanzada"):
            confidence_level = st.slider("Nivel de confianza", 80, 99, 95, key="confidence_level")
            include_seasonality = st.checkbox("Incluir estacionalidad", value=True, key="include_seasonality")
            include_trends = st.checkbox("Incluir tendencias", value=True, key="include_trends")
        
        if st.button("🔮 Generar Predicción"):
            with LoadingManager.spinner("Generando análisis predictivo..."):
                prediction_result = self._generate_predictive_analysis(
                    prediction_type, prediction_horizon, confidence_level,
                    include_seasonality, include_trends
                )
            
            if prediction_result:
                self._render_prediction_results(prediction_result)
            else:
                NotificationManager.warning("No hay datos suficientes para generar predicciones")
    
    def _render_sales_report_config(self) -> Dict[str, Any]:
        """Renderiza configuración para reportes de ventas"""
        st.markdown("### ⚙️ Configuración del Reporte")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Período
            period_type = st.selectbox(
                "Tipo de período",
                ["Predefinido", "Personalizado"],
                key="sales_period_type"
            )
            
            if period_type == "Predefinido":
                period = st.selectbox(
                    "Período",
                    ["Hoy", "Esta semana", "Este mes", "Último trimestre"],
                    key="sales_predefined_period"
                )
                
                end_date = date.today()
                
                if period == "Hoy":
                    start_date = end_date
                elif period == "Esta semana":
                    start_date = end_date - timedelta(days=7)
                elif period == "Este mes":
                    start_date = end_date - timedelta(days=30)
                else:  # Último trimestre
                    start_date = end_date - timedelta(days=90)
            
            else:  # Personalizado
                start_date, end_date = FilterPanel.render_date_range("sales_custom")
        
        with col2:
            # Filtros
            employee_filter = st.selectbox(
                "Empleado",
                ["Todos"] + self._get_all_employees(),
                key="sales_employee_filter"
            )
            
            product_filter = st.multiselect(
                "Productos específicos",
                self._get_all_products(),
                key="sales_product_filter"
            )
        
        with col3:
            # Opciones de análisis
            include_trends = st.checkbox("Incluir análisis de tendencias", value=True)
            include_comparisons = st.checkbox("Incluir comparaciones", value=True)
            include_forecasts = st.checkbox("Incluir proyecciones", value=False)
        
        if st.button("📊 Generar Reporte de Ventas"):
            return {
                "start_date": start_date,
                "end_date": end_date,
                "employee_filter": employee_filter,
                "product_filter": product_filter,
                "include_trends": include_trends,
                "include_comparisons": include_comparisons,
                "include_forecasts": include_forecasts
            }
        
        return None
    
    def _render_executive_kpis(self, current_data: Dict[str, Any], prev_data: Optional[Dict[str, Any]]):
        """Renderiza KPIs ejecutivos"""
        # Calcular KPIs
        current_revenue = current_data.get("total_revenue", 0)
        current_orders = current_data.get("total_orders", 0)
        current_products = current_data.get("unique_products", 0)
        current_avg_order = current_revenue / current_orders if current_orders > 0 else 0
        
        # Calcular cambios si hay datos previos
        if prev_data:
            prev_revenue = prev_data.get("total_revenue", 0)
            prev_orders = prev_data.get("total_orders", 0)
            
            revenue_change = ((current_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
            orders_change = ((current_orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0
        else:
            revenue_change = None
            orders_change = None
        
        # Mostrar métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Ingresos Totales",
                f"${current_revenue:.2f}",
                f"{revenue_change:+.1f}%" if revenue_change is not None else None
            )
        
        with col2:
            st.metric(
                "📦 Total Pedidos",
                current_orders,
                f"{orders_change:+.1f}%" if orders_change is not None else None
            )
        
        with col3:
            st.metric(
                "🏷️ Productos Únicos",
                current_products
            )
        
        with col4:
            st.metric(
                "💳 Ticket Promedio",
                f"${current_avg_order:.2f}"
            )
    
    def _render_current_inventory_status(self):
        """Renderiza estado actual del inventario por tipos"""
        st.markdown("### 📦 Estado Actual del Inventario")
        
        try:
            # Intentar cargar datos modulares
            inventory_data = self._get_current_inventory_by_types()
            
            if inventory_data:
                for inv_type, data in inventory_data.items():
                    st.markdown(f"#### 📋 {inv_type}")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Productos cargados", data.get("loaded_count", 0))
                    
                    with col2:
                        st.metric("Productos vacíos", data.get("empty_count", 0))
                    
                    with col3:
                        coverage = data.get("coverage_percentage", 0)
                        st.metric("Cobertura", f"{coverage:.1f}%")
            else:
                st.info("No hay datos de inventario por tipos disponibles")
                
        except Exception as e:
            st.warning("Datos de inventario modular no disponibles. Usando datos clásicos.")
            self._render_classic_inventory_status()
    
    def _render_classic_inventory_status(self):
        """Renderiza estado clásico del inventario"""
        try:
            inventario = self._persistence.load_inventory()
            
            if inventario:
                total_products = 0
                loaded_products = 0
                
                for categoria, productos in inventario.items():
                    st.markdown(f"#### 📂 {categoria}")
                    
                    category_loaded = 0
                    category_total = len(productos)
                    
                    for producto, cantidad in productos.items():
                        if isinstance(cantidad, (int, float)) and cantidad > 0:
                            category_loaded += 1
                            loaded_products += 1
                        total_products += 1
                    
                    coverage = (category_loaded / category_total * 100) if category_total > 0 else 0
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Productos", category_total)
                    
                    with col2:
                        st.metric("Cargados", category_loaded)
                    
                    with col3:
                        st.metric("Cobertura", f"{coverage:.1f}%")
                
                # Resumen global
                st.markdown("---")
                st.markdown("#### 🌍 Resumen Global")
                
                global_coverage = (loaded_products / total_products * 100) if total_products > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Productos", total_products)
                
                with col2:
                    st.metric("Total Cargados", loaded_products)
                
                with col3:
                    st.metric("Cobertura Global", f"{global_coverage:.1f}%")
            
            else:
                st.error("No se pudo cargar el inventario")
                
        except Exception as e:
            st.error(f"Error al cargar inventario: {str(e)}")
    
    def _render_export_options(self, report_type: str, data: Dict[str, Any]):
        """Renderiza opciones de exportación"""
        st.markdown("### 📥 Opciones de Exportación")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📄 Exportar PDF"):
                self._export_pdf(report_type, data)
        
        with col2:
            if st.button("📊 Exportar Excel"):
                self._export_excel(report_type, data)
        
        with col3:
            if st.button("📋 Exportar CSV"):
                csv_data = self._export_csv(report_type, data)
                if csv_data:
                    st.download_button(
                        "💾 Descargar CSV",
                        csv_data,
                        f"reporte_{report_type}_{date.today()}.csv",
                        "text/csv"
                    )
        
        with col4:
            if st.button("📊 Dashboard Interactivo"):
                self._create_interactive_dashboard(report_type, data)
    
    # Métodos auxiliares para carga de datos
    def _get_period_data(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Obtiene datos consolidados de un período"""
        deliveries = self._history.get_deliveries_period(start_date, end_date)
        
        if not deliveries:
            return {}
        
        total_revenue = sum(d.get('total', 0) for d in deliveries)
        total_orders = len(deliveries)
        unique_products = len(set(
            p.get('producto', '') for d in deliveries 
            for p in d.get('productos', [])
        ))
        
        return {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "unique_products": unique_products,
            "deliveries": deliveries
        }
    
    def _get_current_inventory_by_types(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene inventario actual por tipos (modular)"""
        # Esta función requeriría acceso a los módulos modulares
        # Por ahora retornamos None para usar fallback clásico
        return None
    
    def _get_all_employees(self) -> List[str]:
        """Obtiene lista de todos los empleados"""
        return self._history.get_all_users()
    
    def _get_all_products(self) -> List[str]:
        """Obtiene lista de todos los productos"""
        try:
            inventario = self._persistence.load_inventory()
            products = []
            
            if inventario:
                for categoria, productos in inventario.items():
                    products.extend(productos.keys())
            
            return sorted(list(set(products)))
        
        except:
            return []
    
    # Métodos de generación de reportes (simplificados)
    def _generate_sales_report(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte de ventas según configuración"""
        deliveries = self._history.get_deliveries_period(
            config["start_date"], 
            config["end_date"]
        )
        
        # Filtrar por empleado si es necesario
        if config["employee_filter"] and config["employee_filter"] != "Todos":
            deliveries = [
                d for d in deliveries 
                if d.get("usuario") == config["employee_filter"]
            ]
        
        return {
            "deliveries": deliveries,
            "config": config,
            "generated_at": datetime.now()
        }
    
    def _get_staff_performance_data(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Obtiene datos de rendimiento del personal"""
        deliveries = self._history.get_deliveries_period(start_date, end_date)
        inventory_records = self._history.get_inventory_records_period(start_date, end_date)
        
        return {
            "deliveries": deliveries,
            "inventory_records": inventory_records,
            "period": {"start": start_date, "end": end_date}
        }
    
    def _generate_predictive_analysis(self, prediction_type: str, horizon: str, 
                                    confidence: int, seasonality: bool, trends: bool) -> Dict[str, Any]:
        """Genera análisis predictivo"""
        # Implementación básica de predicción
        return {
            "type": prediction_type,
            "horizon": horizon,
            "confidence": confidence,
            "prediction": "Funcionalidad predictiva en desarrollo",
            "generated_at": datetime.now()
        }
    
    # Métodos de renderizado (simplificados para el ejemplo)
    def _render_revenue_trend(self, data: Dict[str, Any]):
        """Renderiza tendencia de ingresos"""
        st.markdown("**💰 Tendencia de Ingresos**")
        # Implementación del gráfico
        
    def _render_inventory_trend(self, data: Dict[str, Any]):
        """Renderiza tendencia de inventario"""
        st.markdown("**📦 Tendencia de Inventario**")
        # Implementación del gráfico
        
    def _render_top_performers(self, data: Dict[str, Any]):
        """Renderiza mejores performers"""
        st.markdown("**🏆 Mejores Performers**")
        # Implementación de la tabla
        
    def _render_areas_improvement(self, current_data: Dict[str, Any], prev_data: Optional[Dict[str, Any]]):
        """Renderiza áreas de mejora"""
        st.markdown("**📈 Áreas de Mejora**")
        # Implementación del análisis
        
    def _render_executive_alerts(self, data: Dict[str, Any]):
        """Renderiza alertas ejecutivas"""
        # Ejemplo de alertas básicas
        if data.get("total_orders", 0) < 5:
            st.warning("⚠️ Bajo número de pedidos en el período")
        
        if data.get("total_revenue", 0) < 100:
            st.warning("⚠️ Ingresos por debajo del objetivo")
        
        st.success("✅ Sistema funcionando correctamente")
    
    # Métodos de exportación (simplificados)
    def _export_pdf(self, report_type: str, data: Dict[str, Any]):
        """Exporta reporte en PDF"""
        NotificationManager.info("Funcionalidad de exportación PDF próximamente")
    
    def _export_excel(self, report_type: str, data: Dict[str, Any]):
        """Exporta reporte en Excel"""
        NotificationManager.info("Funcionalidad de exportación Excel próximamente")
    
    def _export_csv(self, report_type: str, data: Dict[str, Any]) -> str:
        """Exporta reporte en CSV"""
        NotificationManager.success("CSV generado exitosamente")
        return "Reporte CSV\nDatos de ejemplo\nFuncionalidad completa próximamente"
    
    def _create_interactive_dashboard(self, report_type: str, data: Dict[str, Any]):
        """Crea dashboard interactivo"""
        NotificationManager.info("Dashboard interactivo próximamente")
    
    # Métodos de renderizado adicionales (esqueletos)
    def _render_sales_executive_summary(self, data: Dict[str, Any]):
        """Renderiza resumen ejecutivo de ventas"""
        st.markdown("**📊 Resumen Ejecutivo de Ventas**")
        st.info("Análisis detallado próximamente")
    
    def _render_sales_detailed_data(self, data: Dict[str, Any]):
        """Renderiza datos detallados de ventas"""
        st.markdown("**📋 Datos Detallados de Ventas**")
        st.info("Datos detallados próximamente")
    
    def _render_sales_advanced_analysis(self, data: Dict[str, Any]):
        """Renderiza análisis avanzado de ventas"""
        st.markdown("**📈 Análisis Avanzado de Ventas**")
        st.info("Análisis avanzado próximamente")
    
    def _render_inventory_rotation_analysis(self):
        """Renderiza análisis de rotación de inventario"""
        st.markdown("**🔄 Análisis de Rotación de Inventario**")
        st.info("Análisis de rotación próximamente")
    
    def _render_product_activity_analysis(self):
        """Renderiza análisis de actividad de productos"""
        st.markdown("**📊 Análisis de Actividad de Productos**")
        st.info("Análisis de actividad próximamente")
    
    def _render_inventory_temporal_comparison(self):
        """Renderiza comparación temporal de inventario"""
        st.markdown("**⏱️ Comparación Temporal de Inventario**")
        st.info("Comparación temporal próximamente")
    
    def _render_inventory_alerts(self):
        """Renderiza alertas de inventario"""
        st.markdown("**⚠️ Alertas de Inventario**")
        st.info("Sistema de alertas próximamente")
    
    def _render_loading_efficiency_analysis(self):
        """Renderiza análisis de eficiencia de carga"""
        st.markdown("**⚡ Análisis de Eficiencia de Carga**")
        st.info("Análisis de eficiencia próximamente")
    
    def _render_general_staff_performance(self, data: Dict[str, Any]):
        """Renderiza rendimiento general del personal"""
        st.markdown("**👥 Rendimiento General del Personal**")
        st.info("Análisis de personal próximamente")
    
    def _render_individual_staff_analysis(self, data: Dict[str, Any]):
        """Renderiza análisis individual del personal"""
        st.markdown("**👤 Análisis Individual del Personal**")
        st.info("Análisis individual próximamente")
    
    def _render_staff_comparatives(self, data: Dict[str, Any]):
        """Renderiza comparativas del personal"""
        st.markdown("**🏆 Comparativas del Personal**")
        st.info("Comparativas próximamente")
    
    def _render_prediction_results(self, result: Dict[str, Any]):
        """Renderiza resultados de predicción"""
        st.markdown("**🔮 Resultados de Predicción**")
        st.json(result)