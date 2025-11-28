"""
Componentes de interfaz de usuario para la aplicación Streamlit
"""
# Importaciones seguras
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True  
except ImportError:
    PANDAS_AVAILABLE = False

from typing import List, Dict, Optional
from datetime import datetime

try:
    from ..models.data_models import Store, WeeklySuggestion
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    # Definir clases básicas como fallback
    class Store:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class WeeklySuggestion:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
from ..config.settings import UI_CONFIG, APP_TEXTS, PURCHASE_STRATEGIES


class UIComponents:
    """Componentes reutilizables de la interfaz de usuario"""
    
    @staticmethod
    def render_header():
        """Renderiza el header principal de la aplicación"""
        st.markdown(f"""
        # {APP_TEXTS['titles']['main']}
        ## {APP_TEXTS['titles']['subtitle']}
        
        *{APP_TEXTS['titles']['description']}*
        """)
    
    @staticmethod
    def render_sidebar_navigation() -> str:
        """
        Renderiza la navegación en el sidebar
        
        Returns:
            Tab seleccionado
        """
        with st.sidebar:
            st.markdown("###  Panel de Control")
            
            tab = st.radio(
                "Navegación",
                [
                    APP_TEXTS['navigation']['configure_store'],
                    APP_TEXTS['navigation']['view_stores'], 
                    APP_TEXTS['navigation']['generate_suggestion'],
                    APP_TEXTS['navigation']['history']
                ],
                index=0
            )
            
            return tab
    
    @staticmethod
    def render_holidays_sidebar(holidays: List[Dict]):
        """
        Renderiza próximos feriados en el sidebar
        
        Args:
            holidays: Lista de feriados próximos
        """
        with st.sidebar:
            st.markdown("###  Próximos Feriados")
            
            if not holidays:
                st.info("No hay feriados próximos")
                return
            
            for holiday in holidays[:3]:
                days = holiday['days_until']
                name = holiday['name']
                
                if days == 0:
                    st.markdown(f" **{name}** - ¡Hoy!")
                elif days == 1:
                    st.markdown(f" **{name}** - Mañana")
                else:
                    st.markdown(f" **{name}** - En {days} días")
    
    @staticmethod
    def render_store_card(store) -> None:
        """
        Renderiza una tarjeta de tienda
        
        Args:
            store: Diccionario o Store a renderizar
        """
        # Manejar tanto diccionarios como objetos
        store_id = store.get('id') if isinstance(store, dict) else store.id
        store_name = store.get('name') if isinstance(store, dict) else store.name
        store_city = store.get('city') if isinstance(store, dict) else store.city
        store_country = store.get('country') if isinstance(store, dict) else store.country
        store_lat = store.get('lat') if isinstance(store, dict) else store.lat
        store_lon = store.get('lon') if isinstance(store, dict) else store.lon
        store_demand = store.get('base_demand') if isinstance(store, dict) else store.base_demand
        
        with st.container():
            # Header de la tarjeta
            st.markdown(f"""
            <div style='padding: 1rem; border: 1px solid #ddd; border-radius: 10px; margin: 1rem 0;'>
                <h3> {store_name}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("** Ubicación:**")
                st.write(f" {store_city}, {store_country}")
                st.write(f" Lat: {store_lat:.4f}, Lon: {store_lon:.4f}")
            
            with col2:
                st.markdown(f"** ID: {store_id}**")
                if st.button(f" Ver en Mapa", key=f"map_{store_id}"):
                    st.session_state[f"show_map_{store_id}"] = True
            
            # Mostrar mapa si fue solicitado
            if st.session_state.get(f"show_map_{store_id}", False):
                UIComponents.render_store_map(store)
                if st.button(f" Ocultar Mapa", key=f"hide_map_{store_id}"):
                    st.session_state[f"show_map_{store_id}"] = False
                    st.rerun()
            
            st.divider()
    
    @staticmethod
    def render_store_map(store):
        """
        Renderiza mapa de una tienda
        
        Args:
            store: Diccionario o Store a mostrar en el mapa
        """
        store_lat = store.get('lat') if isinstance(store, dict) else store.lat
        store_lon = store.get('lon') if isinstance(store, dict) else store.lon
        map_df = pd.DataFrame([[store_lat, store_lon]], columns=['lat', 'lon'])
        st.map(map_df, zoom=13)
    
    @staticmethod
    def render_weather_chart(forecast: dict) -> None:
        """
        Renderiza gráfico del pronóstico meteorológico
        
        Args:
            forecast: Pronóstico semanal
        """
        daily_weather = forecast.get('daily_weather', [])
        if not daily_weather:
            st.warning("No hay datos meteorológicos disponibles")
            return
        
        # Preparar datos
        dates = [day.date for day in daily_weather]
        temp_max = [day.temp_max for day in daily_weather]
        temp_min = [day.temp_min for day in daily_weather]
        temp_avg = [day.temp_avg for day in daily_weather]
        
        # Crear gráfico
        fig = go.Figure()
        
        # Temperatura máxima
        fig.add_trace(go.Scatter(
            x=dates, y=temp_max,
            mode='lines+markers',
            name='Temp Máxima',
            line=dict(color='red', width=2),
            marker=dict(size=8)
        ))
        
        # Temperatura mínima
        fig.add_trace(go.Scatter(
            x=dates, y=temp_min,
            mode='lines+markers', 
            name='Temp Mínima',
            line=dict(color='blue', width=2),
            marker=dict(size=8)
        ))
        
        # Temperatura promedio
        fig.add_trace(go.Scatter(
            x=dates, y=temp_avg,
            mode='lines+markers',
            name='Temp Promedio',
            line=dict(color='orange', width=2, dash='dash'),
            marker=dict(size=6)
        ))
        
        # Configurar layout
        fig.update_layout(
            title=' Pronóstico de Temperatura Semanal',
            xaxis_title='Fecha',
            yaxis_title='Temperatura (°C)',
            hovermode='x unified',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def render_demand_factors_chart(forecast: dict) -> None:
        """
        Renderiza gráfico de factores de demanda
        
        Args:
            forecast: Pronóstico semanal
        """
        daily_weather = forecast.get('daily_weather', [])
        if not daily_weather:
            st.warning("No hay datos para mostrar factores de demanda")
            return
        
        # Preparar datos
        dates = [day.date for day in daily_weather]
        factors = [day.get_temp_factor() for day in daily_weather]
        colors = ['red' if f > 2.0 else 'orange' if f > 1.5 else 'green' if f >= 1.0 else 'blue' for f in factors]
        
        # Crear gráfico de barras
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=dates, y=factors,
            name='Factor de Demanda',
            text=[f"{f:.1f}x" for f in factors],
            textposition='outside',
            marker_color=colors
        ))
        
        # Línea de referencia (demanda normal)
        fig.add_hline(y=1.0, line_dash="dash", line_color="gray", 
                     annotation_text="Demanda Normal")
        
        fig.update_layout(
            title=' Factores de Demanda por Día',
            xaxis_title='Fecha',
            yaxis_title='Factor de Multiplicación',
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    @staticmethod
    @staticmethod
    def render_suggestion_summary(suggestion: WeeklySuggestion, current_inventory: List[Dict] = None) -> None:
        """
        Renderiza resumen de sugerencia con formato detallado en tablas tipo Excel
        
        Args:
            suggestion: Sugerencia semanal
            current_inventory: Inventario actual (opcional, para mostrar verificación de lógica)
        """
        from ..config.productos_completos import PRODUCT_SPECS_COMPLETO
        
        # ========== CAPACIDAD ==========
        st.subheader("📦 CAPACIDAD")
        
        if suggestion.capacidad_total > 0:
            # Determinar emoji y texto para factor climático
            if suggestion.factor_climatico > 0:
                factor_texto = f"+{suggestion.factor_climatico} bulto"
                factor_emoji = "🔥"
            elif suggestion.factor_climatico < 0:
                factor_texto = f"{suggestion.factor_climatico} bulto"
                factor_emoji = "❄️"
            else:
                factor_texto = "sin cambio"
                factor_emoji = "🌤️"
            
            # Crear DataFrame para capacidad
            capacidad_df = pd.DataFrame([
                {"Métrica": "Capacidad Total", "Valor": f"{suggestion.capacidad_total} bultos"},
                {"Métrica": "Bultos Actuales", "Valor": f"{suggestion.capacidad_actual} bultos"},
                {"Métrica": "Espacio Disponible", "Valor": f"{suggestion.capacidad_disponible} bultos"},
                {"Métrica": f"{factor_emoji} Factor Climático Semanal", "Valor": f"Promedio 7 días: {suggestion.temperatura_promedio_semana:.1f}°C → {factor_texto}"},
                {"Métrica": "Bultos Sugeridos", "Valor": f"{suggestion.total_bultos} bultos"},
                {"Métrica": "Total Final", "Valor": f"{suggestion.capacidad_actual + suggestion.total_bultos} / {suggestion.capacidad_total} bultos"},
                {"Métrica": "Ocupación Final", "Valor": f"{((suggestion.capacidad_actual + suggestion.total_bultos) / suggestion.capacidad_total * 100):.1f}%"},
            ])
            
            st.dataframe(
                capacidad_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Métrica": st.column_config.TextColumn("Métrica", width="medium"),
                    "Valor": st.column_config.TextColumn("Valor", width="medium"),
                }
            )
            
            # Verificar sobrecarga
            if suggestion.capacidad_actual + suggestion.total_bultos > suggestion.capacidad_total:
                st.error("❌ ERROR: Sobrecarga de capacidad detectada")
            else:
                st.success("✅ CAPACIDAD RESPETADA: No hay sobrecarga")
            
            # Mostrar desglose de temperaturas día por día
            if suggestion.daily_analysis and len(suggestion.daily_analysis) > 0:
                with st.expander("📊 Ver desglose de temperaturas por día", expanded=False):
                    temps_dia = []
                    for day in suggestion.daily_analysis:
                        # Calcular temp_avg desde temp_factor si es necesario
                        # temp_factor: <20°C=0.3, 20-25°C=1.0, 25-30°C=1.8, >30°C=2.5
                        if day.temp_factor >= 2.5:
                            temp_est = ">30°C"
                        elif day.temp_factor >= 1.8:
                            temp_est = "25-30°C"
                        elif day.temp_factor >= 1.0:
                            temp_est = "20-25°C"
                        else:
                            temp_est = "<20°C"
                        
                        temps_dia.append({
                            "Fecha": day.date,
                            "Temperatura": temp_est,
                            "Factor": f"{day.temp_factor:.1f}x"
                        })
                    
                    temps_df = pd.DataFrame(temps_dia)
                    st.dataframe(
                        temps_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Fecha": st.column_config.TextColumn("Fecha", width="medium"),
                            "Temperatura": st.column_config.TextColumn("Temperatura", width="medium"),
                            "Factor": st.column_config.TextColumn("Factor Demanda", width="small"),
                        }
                    )
                    st.caption(f"Promedio semanal: {suggestion.temperatura_promedio_semana:.1f}°C basado en {len(temps_dia)} días")
        
        st.divider()
        
        # ========== INVERSIÓN ==========
        st.subheader("💰 INVERSIÓN")
        
        # Crear DataFrame para inversión
        inversion_df = pd.DataFrame([
            {"Métrica": "Total", "Valor": f"₱{suggestion.total_investment:,.0f}"},
            {"Métrica": "ROI Esperado", "Valor": f"{suggestion.expected_roi*100:.1f}%"},
        ])
        
        st.dataframe(
            inversion_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Métrica": st.column_config.TextColumn("Métrica", width="medium"),
                "Valor": st.column_config.TextColumn("Valor", width="medium"),
            }
        )
        
        st.divider()
        
        # ========== PRODUCTOS SUGERIDOS (DETALLADO) ==========
        st.subheader("📋 PRODUCTOS SUGERIDOS (DETALLADO)")
        
        if suggestion.product_suggestions:
            # Ordenar productos alfabéticamente
            productos_ordenados = sorted(
                suggestion.product_suggestions, 
                key=lambda x: x.product_name
            )
            
            # Crear DataFrame con todos los productos
            productos_data = []
            for prod in productos_ordenados:
                inversion = prod.suggested_bulks * PRODUCT_SPECS_COMPLETO.get(prod.product_id, {}).get('price_cost_box', 0)
                productos_data.append({
                    "Producto": prod.product_name,
                    "Bultos": prod.suggested_bulks,
                    "Unidades": int(prod.suggested_quantity),
                    "Inversión": f"₱{inversion:,.0f}"
                })
            
            # Agregar fila de total
            total_unidades = sum(p.suggested_quantity for p in productos_ordenados)
            productos_data.append({
                "Producto": "TOTAL",
                "Bultos": suggestion.total_bultos,
                "Unidades": int(total_unidades),
                "Inversión": f"₱{suggestion.total_investment:,.0f}"
            })
            
            productos_df = pd.DataFrame(productos_data)
            
            # Mostrar tabla con formato Excel
            st.dataframe(
                productos_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Producto": st.column_config.TextColumn("Producto", width="large"),
                    "Bultos": st.column_config.NumberColumn("Bultos", width="small"),
                    "Unidades": st.column_config.NumberColumn("Unidades", width="medium"),
                    "Inversión": st.column_config.TextColumn("Inversión", width="medium"),
                }
            )
        else:
            st.warning("⚠️  No se generaron sugerencias")
        
        st.divider()
        
        # ========== VERIFICACIÓN DE LÓGICA DE ESTADOS ==========
        if current_inventory and suggestion.product_suggestions:
            st.subheader("🔍 VERIFICACIÓN DE LÓGICA DE ESTADOS")
            
            # Crear diccionario de inventario
            inv_dict = {item['Producto']: item for item in current_inventory}
            
            # Determinar texto del factor climático
            if suggestion.factor_climatico > 0:
                factor_clima_texto = f"+{suggestion.factor_climatico}"
            elif suggestion.factor_climatico < 0:
                factor_clima_texto = f"{suggestion.factor_climatico}"
            else:
                factor_clima_texto = "0"
            
            # Crear DataFrame para verificación
            verificacion_data = []
            
            productos_ordenados = sorted(
                suggestion.product_suggestions, 
                key=lambda x: x.product_name
            )
            
            for prod in productos_ordenados:
                # Buscar en inventario
                inv_item = None
                for inv_name, inv_data in inv_dict.items():
                    if inv_name.lower() in prod.product_name.lower() or prod.product_name.lower() in inv_name.lower():
                        inv_item = inv_data
                        break
                
                if inv_item:
                    estado = inv_item['Estado Stock']
                    bultos_actual = inv_item['Bultos']
                    bultos_sugerido = prod.suggested_bulks
                    
                    # Determinar lógica esperada BASE (sin clima)
                    if 'OK' in estado.upper():
                        if bultos_actual <= 3:
                            base_bultos = 1
                            logica_base = "STOCK OK (≤3): +1"
                        else:
                            base_bultos = 0
                            logica_base = "STOCK OK (>3): NO sugerir"
                    elif 'BAJO' in estado.upper():
                        base_bultos = 2
                        logica_base = "STOCK BAJO: +2"
                    elif 'SIN' in estado.upper():
                        base_bultos = 3
                        logica_base = "SIN STOCK: +3"
                    else:
                        base_bultos = 0
                        logica_base = "Estado desconocido"
                    
                    # Calcular con factor climático
                    bultos_con_clima = max(0, base_bultos + suggestion.factor_climatico)
                    
                    verificacion_data.append({
                        "Producto": prod.product_name,
                        "Estado": estado,
                        "Actual": bultos_actual,
                        "Base": base_bultos,
                        "Factor Climático": factor_clima_texto,
                        "Sugerido": bultos_sugerido,
                        "Lógica": f"✓ {logica_base}"
                    })
            
            verificacion_df = pd.DataFrame(verificacion_data)
            
            # Mostrar tabla con formato Excel
            st.dataframe(
                verificacion_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Producto": st.column_config.TextColumn("Producto", width="large"),
                    "Estado": st.column_config.TextColumn("Estado", width="small"),
                    "Actual": st.column_config.NumberColumn("Actual", width="small"),
                    "Base": st.column_config.NumberColumn("Base", width="small"),
                    "Factor Climático": st.column_config.TextColumn("Factor Climático", width="small"),
                    "Sugerido": st.column_config.NumberColumn("Sugerido", width="small"),
                    "Lógica": st.column_config.TextColumn("Lógica", width="medium"),
                }
            )
            
            st.divider()
            
            # ========== PRODUCTOS NO SUGERIDOS (Sobremercadería) ==========
            st.subheader("⊗ PRODUCTOS NO SUGERIDOS (Sobremercadería)")
            
            productos_sugeridos_nombres = {p.product_name.lower() for p in suggestion.product_suggestions}
            
            no_sugeridos_data = []
            
            for item in current_inventory:
                producto = item['Producto']
                bultos = item['Bultos']
                estado = item['Estado Stock']
                
                # Buscar si fue sugerido
                fue_sugerido = any(producto.lower() in nombre or nombre in producto.lower() for nombre in productos_sugeridos_nombres)
                
                if not fue_sugerido and 'OK' in estado.upper() and bultos > 3:
                    no_sugeridos_data.append({
                        "Producto": producto,
                        "Bultos": bultos,
                        "Razón": "SOBREMERCADERÍA, correctamente NO sugerido"
                    })
            
            if no_sugeridos_data:
                no_sugeridos_df = pd.DataFrame(no_sugeridos_data)
                st.dataframe(
                    no_sugeridos_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Producto": st.column_config.TextColumn("Producto", width="large"),
                        "Bultos": st.column_config.NumberColumn("Bultos", width="small"),
                        "Razón": st.column_config.TextColumn("Razón", width="large"),
                    }
                )
            else:
                st.info("No hay productos con sobremercadería")
            
            st.divider()
        
        # ========== RESUMEN FINAL ==========
        st.subheader("📊 RESUMEN FINAL")
        
        if current_inventory:
            productos_inventario = len(current_inventory)
            productos_sugeridos = len(suggestion.product_suggestions)
            productos_no_sugeridos = productos_inventario - productos_sugeridos
            
            # Crear DataFrame para resumen
            resumen_df = pd.DataFrame([
                {"Concepto": "✅ Productos en inventario", "Cantidad": productos_inventario},
                {"Concepto": "✅ Productos sugeridos", "Cantidad": productos_sugeridos},
                {"Concepto": "⊗ Productos NO sugeridos", "Cantidad": f"{productos_no_sugeridos} (sobremercadería o sin match)"},
                {"Concepto": "📊 Capacidad", "Cantidad": f"{suggestion.capacidad_actual} actual + {suggestion.total_bultos} sugeridos = {suggestion.capacidad_actual + suggestion.total_bultos} / {suggestion.capacidad_total} total"},
            ])
        else:
            resumen_df = pd.DataFrame([
                {"Concepto": "✅ Productos sugeridos", "Cantidad": len(suggestion.product_suggestions)},
                {"Concepto": "💰 Inversión total", "Cantidad": f"₱{suggestion.total_investment:,.0f}"},
                {"Concepto": "📈 ROI esperado", "Cantidad": f"{suggestion.expected_roi*100:.1f}%"},
            ])
        
        st.dataframe(
            resumen_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Concepto": st.column_config.TextColumn("Concepto", width="large"),
                "Cantidad": st.column_config.TextColumn("Cantidad", width="large"),
            }
        )

    @staticmethod
    def render_products_table(products: List[Dict]) -> None:
        """
        Renderiza tabla de productos sugeridos
        
        Args:
            products: Lista de productos
        """
        if not products:
            st.warning("No hay productos sugeridos")
            return
        
        # Preparar datos para la tabla
        df_data = []
        for product in products:
            df_data.append({
                " Producto": product.product_name,
                " Bultos": f"{product.suggested_bulks}",
                " Cantidad": f"{product.suggested_quantity:.0f} {product.unit}",
                " Demanda Base": f"{product.base_daily_demand:.1f}/semana",
                " Proyección Semanal": f"{product.projected_weekly_demand:.0f}",
                " Confianza": f"{product.confidence * 100:.0f}%"
            })
        
        df = pd.DataFrame(df_data)
        
        # Configurar el dataframe para mejor visualización
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
    
    @staticmethod
    def render_strategy_selector() -> str:
        """
        Renderiza selector de estrategia
        
        Returns:
            Estrategia seleccionada
        """
        st.subheader(" Selecciona tu Estrategia de Compra")
        
        strategy_options = list(PURCHASE_STRATEGIES.keys())
        strategy_names = [PURCHASE_STRATEGIES[s]['name'] for s in strategy_options]
        strategy_descriptions = [PURCHASE_STRATEGIES[s]['description'] for s in strategy_options]
        
        # Mostrar opciones con descripciones
        for i, (name, desc) in enumerate(zip(strategy_names, strategy_descriptions)):
            st.markdown(f"**{name}**: {desc}")
        
        # Selector
        selected_index = st.radio(
            "Elige tu estrategia:",
            range(len(strategy_options)),
            format_func=lambda x: strategy_names[x],
            horizontal=True
        )
        
        return strategy_options[selected_index]
    
    @staticmethod
    def render_loading_spinner(message: str = "Procesando..."):
        """
        Renderiza spinner de carga
        
        Args:
            message: Mensaje a mostrar
        """
        with st.spinner(message):
            st.empty()
    
    @staticmethod
    def render_success_message(message: str):
        """
        Renderiza mensaje de éxito
        
        Args:
            message: Mensaje a mostrar
        """
        st.success(message)
    
    @staticmethod
    def render_error_message(message: str):
        """
        Renderiza mensaje de error
        
        Args:
            message: Mensaje de error
        """
        st.error(message)
    
    @staticmethod
    def render_info_message(message: str):
        """
        Renderiza mensaje informativo
        
        Args:
            message: Mensaje informativo
        """
        st.info(message)


# Instancia global de componentes UI
ui_components = UIComponents()
