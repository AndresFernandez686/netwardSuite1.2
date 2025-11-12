"""
UI modular para historial de administradores.
Análisis avanzado y gestión de historial de inventarios.
"""
import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
import json

from ...core.inventory_types import InventoryType
from ...core.data_models import InventoryRecord
from ...data.persistence import DataPersistence
from ...data.history import HistoryManager, HistoryFilter, HistoryAnalyzer
from ..components.widgets import (
    FilterPanel, MetricCards, StatusIndicators, 
    NotificationManager, ActionButtons, LoadingManager
)

class AdminHistoryUI:
    """UI modular para historial de administradores"""
    
    def __init__(self):
        self._persistence = DataPersistence()
        self._history = HistoryManager()
        self._filter = HistoryFilter()
        self._analyzer = HistoryAnalyzer()
        
        # Inicializar en session_state
        if "admin_history_ui" not in st.session_state:
            st.session_state.admin_history_ui = {
                "filters_applied": False,
                "selected_records": []
            }
    
    def render(self, usuario: str):
        """Renderiza la interfaz de historial para administradores"""
        st.header("📊 Análisis de Historial")
        
        # Pestañas principales
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Historial General",
            "🔍 Análisis Detallado", 
            "📈 Tendencias",
            "🛠️ Gestión"
        ])
        
        with tab1:
            self._render_general_history(usuario)
        
        with tab2:
            self._render_detailed_analysis(usuario)
        
        with tab3:
            self._render_trends_analysis(usuario)
        
        with tab4:
            self._render_history_management(usuario)
    
    def _render_general_history(self, usuario: str):
        """Renderiza historial general con filtros"""
        st.subheader("📋 Historial General de Inventarios")
        
        # Panel de filtros
        with st.expander("🔧 Filtros de Búsqueda", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Filtro por usuario
                all_users = self._history.get_all_users()
                selected_user = FilterPanel.render_user_filter(
                    all_users, "history_user_filter"
                )
            
            with col2:
                # Filtro por tipo de inventario
                selected_type = FilterPanel.render_type_filter("history_type_filter")
            
            with col3:
                # Filtro por período
                period = st.selectbox(
                    "📅 Período", 
                    ["Última semana", "Último mes", "Últimos 3 meses", "Personalizado"],
                    key="history_period_filter"
                )
            
            # Rango de fechas personalizado
            if period == "Personalizado":
                start_date, end_date = FilterPanel.render_date_range("history_custom")
            else:
                end_date = date.today()
                if period == "Última semana":
                    start_date = end_date - timedelta(days=7)
                elif period == "Último mes":
                    start_date = end_date - timedelta(days=30)
                else:  # Últimos 3 meses
                    start_date = end_date - timedelta(days=90)
        
        # Aplicar filtros
        filters = {
            "user": selected_user if selected_user != "Todos" else None,
            "inventory_type": selected_type if selected_type != "Todos" else None,
            "start_date": start_date,
            "end_date": end_date
        }
        
        # Cargar registros filtrados
        with LoadingManager.spinner("Cargando historial..."):
            records = self._filter.apply_filters(filters)
        
        if not records:
            st.info("No se encontraron registros con los filtros aplicados")
            return
        
        # Métricas del período
        st.markdown("### 📊 Métricas del Período")
        
        total_records = len(records)
        unique_users = len(set(r.get('usuario', '') for r in records))
        unique_products = len(set(r.get('producto', '') for r in records if r.get('producto')))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📝 Total Registros", total_records)
        
        with col2:
            st.metric("👥 Usuarios Activos", unique_users)
        
        with col3:
            st.metric("🏷️ Productos Únicos", unique_products)
        
        with col4:
            avg_per_day = total_records / max((end_date - start_date).days, 1)
            st.metric("📅 Promedio/Día", f"{avg_per_day:.1f}")
        
        # Tabla de registros
        st.markdown("---")
        st.subheader("📋 Registros Detallados")
        
        # Opciones de visualización
        col1, col2 = st.columns([3, 1])
        
        with col1:
            show_details = st.checkbox("Mostrar detalles completos", key="show_full_details")
        
        with col2:
            sort_order = st.selectbox("Ordenar por", ["Más recientes", "Más antiguos"], key="sort_order")
        
        # Mostrar registros
        sorted_records = sorted(
            records, 
            key=lambda x: x.get('fecha', ''),
            reverse=(sort_order == "Más recientes")
        )
        
        for i, record in enumerate(sorted_records[:50]):  # Limitar a 50 registros
            with st.expander(
                f"{record.get('fecha', 'Sin fecha')} - "
                f"{record.get('usuario', 'Usuario desconocido')} - "
                f"{record.get('tipo_inventario', 'Sin tipo')}"
            ):
                if show_details:
                    self._render_record_details(record)
                else:
                    self._render_record_summary(record)
        
        if len(sorted_records) > 50:
            st.info(f"Mostrando 50 de {len(sorted_records)} registros. Use filtros para refinar la búsqueda.")
    
    def _render_record_details(self, record: Dict[str, Any]):
        """Renderiza detalles completos de un registro"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Usuario:** {record.get('usuario', 'N/A')}")
            st.write(f"**Fecha:** {record.get('fecha', 'N/A')}")
            st.write(f"**Hora:** {record.get('hora', 'N/A')}")
            st.write(f"**Tipo:** {record.get('tipo_inventario', 'N/A')}")
        
        with col2:
            st.write(f"**Categoría:** {record.get('categoria', 'N/A')}")
            st.write(f"**Producto:** {record.get('producto', 'N/A')}")
            st.write(f"**Cantidad:** {record.get('cantidad', 'N/A')}")
            
            if record.get('observaciones'):
                st.write(f"**Observaciones:** {record['observaciones']}")
        
        # Mostrar datos adicionales si existen
        if 'datos_adicionales' in record:
            st.json(record['datos_adicionales'])
    
    def _render_record_summary(self, record: Dict[str, Any]):
        """Renderiza resumen de un registro"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.write(f"**{record.get('usuario', 'N/A')}**")
        
        with col2:
            st.write(record.get('tipo_inventario', 'N/A'))
        
        with col3:
            st.write(record.get('categoria', 'N/A'))
        
        with col4:
            producto = record.get('producto', 'N/A')
            cantidad = record.get('cantidad', 'N/A')
            st.write(f"{producto}: {cantidad}")
    
    def _render_detailed_analysis(self, usuario: str):
        """Renderiza análisis detallado del historial"""
        st.subheader("🔍 Análisis Detallado")
        
        # Análisis por usuario
        st.markdown("### 👥 Análisis por Usuario")
        
        user_analysis = self._analyzer.analyze_by_user()
        
        if user_analysis:
            # Crear gráfico de barras de actividad por usuario
            try:
                import pandas as pd
                
                df_users = pd.DataFrame([
                    {"Usuario": user, "Registros": data["total_records"], 
                     "Productos": data["unique_products"]}
                    for user, data in user_analysis.items()
                ])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.bar_chart(df_users.set_index("Usuario")["Registros"])
                
                with col2:
                    st.bar_chart(df_users.set_index("Usuario")["Productos"])
                    
            except ImportError:
                # Fallback sin pandas
                for user, data in user_analysis.items():
                    st.write(f"**{user}:** {data['total_records']} registros, {data['unique_products']} productos únicos")
        
        # Análisis por tipo de inventario
        st.markdown("---")
        st.markdown("### 📊 Análisis por Tipo de Inventario")
        
        type_analysis = self._analyzer.analyze_by_inventory_type()
        
        if type_analysis:
            col1, col2, col3 = st.columns(3)
            
            for i, (inv_type, data) in enumerate(type_analysis.items()):
                with [col1, col2, col3][i % 3]:
                    st.metric(
                        f"📋 {inv_type}",
                        data["total_records"],
                        f"{data['unique_products']} productos"
                    )
        
        # Análisis temporal
        st.markdown("---")
        st.markdown("### 📅 Análisis Temporal")
        
        temporal_analysis = self._analyzer.analyze_temporal_patterns()
        
        if temporal_analysis:
            # Mostrar patrones por día de la semana
            if "weekday_patterns" in temporal_analysis:
                st.markdown("**Actividad por día de la semana:**")
                weekdays = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                
                for i, day in enumerate(weekdays):
                    if i in temporal_analysis["weekday_patterns"]:
                        count = temporal_analysis["weekday_patterns"][i]
                        st.write(f"{day}: {count} registros")
            
            # Mostrar patrones por hora
            if "hourly_patterns" in temporal_analysis:
                st.markdown("**Actividad por hora:**")
                
                try:
                    import pandas as pd
                    
                    hourly_data = pd.DataFrame([
                        {"Hora": f"{hour:02d}:00", "Registros": count}
                        for hour, count in temporal_analysis["hourly_patterns"].items()
                    ])
                    
                    st.line_chart(hourly_data.set_index("Hora"))
                    
                except ImportError:
                    for hour, count in temporal_analysis["hourly_patterns"].items():
                        st.write(f"{hour:02d}:00 - {count} registros")
    
    def _render_trends_analysis(self, usuario: str):
        """Renderiza análisis de tendencias"""
        st.subheader("📈 Análisis de Tendencias")
        
        # Configuración del período de análisis
        col1, col2 = st.columns(2)
        
        with col1:
            period_days = st.selectbox(
                "Período de análisis",
                [7, 30, 90, 180],
                format_func=lambda x: f"Últimos {x} días",
                key="trends_period"
            )
        
        with col2:
            analysis_type = st.selectbox(
                "Tipo de análisis",
                ["Actividad general", "Por usuario", "Por tipo de inventario", "Por producto"],
                key="trends_analysis_type"
            )
        
        # Obtener datos de tendencia
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)
        
        trend_data = self._analyzer.analyze_trends(start_date, end_date, analysis_type)
        
        if not trend_data:
            st.info("No hay suficientes datos para el análisis de tendencias")
            return
        
        # Mostrar gráfico de tendencias
        try:
            import pandas as pd
            
            if analysis_type == "Actividad general":
                df_trend = pd.DataFrame(trend_data)
                st.line_chart(df_trend.set_index("fecha"))
            
            elif analysis_type == "Por usuario":
                # Crear gráfico multi-línea por usuario
                df_users = pd.DataFrame(trend_data)
                st.line_chart(df_users.set_index("fecha"))
            
            elif analysis_type == "Por tipo de inventario":
                # Gráfico por tipo
                df_types = pd.DataFrame(trend_data)
                st.area_chart(df_types.set_index("fecha"))
            
            else:  # Por producto
                # Top productos más activos
                df_products = pd.DataFrame(trend_data)
                st.bar_chart(df_products.set_index("producto")["registros"])
                
        except ImportError:
            st.warning("Instala pandas para ver gráficos de tendencias")
            st.json(trend_data)
        
        # Estadísticas de tendencia
        st.markdown("---")
        st.markdown("### 📊 Estadísticas de Tendencia")
        
        stats = self._analyzer.calculate_trend_statistics(trend_data, analysis_type)
        
        if stats:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📈 Tendencia", stats.get("trend", "N/A"))
            
            with col2:
                st.metric("📊 Promedio", f"{stats.get('average', 0):.1f}")
            
            with col3:
                st.metric("🎯 Pico máximo", stats.get("peak", "N/A"))
    
    def _render_history_management(self, usuario: str):
        """Renderiza herramientas de gestión del historial"""
        st.subheader("🛠️ Gestión del Historial")
        
        # Estadísticas generales
        st.markdown("### 📊 Estadísticas Generales")
        
        total_records = self._history.get_total_records_count()
        oldest_record = self._history.get_oldest_record_date()
        file_size = self._persistence.get_history_file_size()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📝 Total Registros", total_records)
        
        with col2:
            st.metric("📅 Registro más antiguo", oldest_record or "N/A")
        
        with col3:
            st.metric("💾 Tamaño archivo", f"{file_size / 1024:.1f} KB" if file_size else "N/A")
        
        # Herramientas de mantenimiento
        st.markdown("---")
        st.markdown("### 🧹 Mantenimiento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Limpieza de datos:**")
            
            if st.button("🧽 Eliminar duplicados"):
                removed_count = self._history.remove_duplicates()
                if removed_count > 0:
                    NotificationManager.success(f"Eliminados {removed_count} duplicados")
                else:
                    NotificationManager.info("No se encontraron duplicados")
            
            if st.button("🗑️ Limpiar registros antiguos"):
                cutoff_days = st.number_input(
                    "Días a conservar", 
                    min_value=30, 
                    value=365, 
                    key="cleanup_days"
                )
                
                if st.checkbox("Confirmar limpieza", key="confirm_cleanup"):
                    removed_count = self._history.cleanup_old_records(cutoff_days)
                    NotificationManager.success(f"Eliminados {removed_count} registros antiguos")
        
        with col2:
            st.markdown("**Exportación y backup:**")
            
            if st.button("📥 Exportar historial completo"):
                export_data = self._history.export_complete_history()
                
                if export_data:
                    st.download_button(
                        "💾 Descargar historial",
                        export_data,
                        f"historial_completo_{date.today()}.json",
                        "application/json"
                    )
            
            if st.button("📋 Generar reporte resumido"):
                report_data = self._analyzer.generate_summary_report()
                
                if report_data:
                    st.download_button(
                        "📄 Descargar reporte",
                        report_data,
                        f"reporte_historial_{date.today()}.txt",
                        "text/plain"
                    )
        
        # Importación de datos
        st.markdown("---")
        st.markdown("### 📤 Importación de Datos")
        
        uploaded_file = st.file_uploader(
            "Importar historial desde archivo JSON",
            type=['json'],
            key="import_history"
        )
        
        if uploaded_file:
            col1, col2 = st.columns(2)
            
            with col1:
                merge_option = st.radio(
                    "Modo de importación",
                    ["Agregar al existente", "Reemplazar completamente"],
                    key="import_mode"
                )
            
            with col2:
                if st.button("📥 Importar datos", type="primary"):
                    try:
                        imported_data = json.load(uploaded_file)
                        
                        if merge_option == "Agregar al existente":
                            success = self._history.merge_history_data(imported_data)
                        else:
                            success = self._history.replace_history_data(imported_data)
                        
                        if success:
                            NotificationManager.success("Historial importado exitosamente")
                        else:
                            NotificationManager.error("Error al importar historial")
                            
                    except Exception as e:
                        NotificationManager.error(f"Error al procesar archivo: {str(e)}")