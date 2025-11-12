"""
Demostración de Reportes - Netw@rd v1.5
Muestra ejemplos de lo que pueden hacer los reportes para tu negocio
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import random

def crear_datos_ejemplo():
    """Crea datos de ejemplo para mostrar cómo funcionan los reportes"""
    
    # Productos populares
    productos = [
        "Cerveza Corona", "Marlboro Box", "Coca Cola 600ml", 
        "Pall Mall Box", "Cerveza Quilmes", "Pepsi 500ml",
        "Lucky Strike", "Fernet Branca", "Red Bull", "Agua Villavicencio"
    ]
    
    # Generar datos de los últimos 30 días
    datos_ventas = []
    fecha_inicio = datetime.now() - timedelta(days=30)
    
    for dia in range(30):
        fecha = fecha_inicio + timedelta(days=dia)
        
        # Más ventas en fines de semana
        factor_finde = 1.5 if fecha.weekday() >= 5 else 1.0
        
        # Generar entre 5-20 ventas por día
        num_ventas = int(random.uniform(5, 20) * factor_finde)
        
        for _ in range(num_ventas):
            producto = random.choice(productos)
            cantidad = random.randint(1, 5)
            precio = random.uniform(100, 800)
            
            datos_ventas.append({
                'fecha': fecha.strftime('%Y-%m-%d'),
                'producto': producto,
                'cantidad': cantidad,
                'precio_total': precio * cantidad,
                'dia_semana': fecha.strftime('%A'),
                'hora': random.randint(8, 22)
            })
    
    return pd.DataFrame(datos_ventas)

def mostrar_reporte_ventas_top(df):
    """Muestra los productos más vendidos"""
    st.markdown("#### Productos Más Vendidos (Últimos 30 días)")
    
    top_productos = df.groupby('producto').agg({
        'cantidad': 'sum',
        'precio_total': 'sum'
    }).sort_values('cantidad', ascending=False).head(5)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Por Cantidad:**")
        for idx, (producto, datos) in enumerate(top_productos.iterrows(), 1):
            st.write(f"{idx}. **{producto}**: {int(datos['cantidad'])} unidades")
    
    with col2:
        st.markdown("**Por Ingresos:**")
        top_ingresos = top_productos.sort_values('precio_total', ascending=False)
        for idx, (producto, datos) in enumerate(top_ingresos.iterrows(), 1):
            st.write(f"{idx}. **{producto}**: ${datos['precio_total']:,.0f}")

def mostrar_analisis_temporal(df):
    """Muestra análisis por días de la semana"""
    st.markdown("#### Análisis por Días de la Semana")
    
    ventas_por_dia = df.groupby('dia_semana').agg({
        'cantidad': 'sum',
        'precio_total': 'sum'
    })
    
    # Ordenar días de la semana
    orden_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dias_español = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Mejor día para ventas:**")
        mejor_dia_idx = ventas_por_dia['precio_total'].idxmax()
        mejor_dia_es = dias_español[orden_dias.index(mejor_dia_idx)]
        ingresos_mejor = ventas_por_dia.loc[mejor_dia_idx, 'precio_total']
        st.success(f"**{mejor_dia_es}**: ${ingresos_mejor:,.0f}")
    
    with col2:
        st.markdown("**Promedio por día:**")
        promedio_diario = ventas_por_dia['precio_total'].mean()
        st.info(f"**Promedio**: ${promedio_diario:,.0f}")

def mostrar_alertas_inventario():
    """Muestra alertas y recomendaciones"""
    st.markdown("#### Alertas y Recomendaciones")
    
    alertas = [
        {"tipo": "warning", "mensaje": "Stock bajo: Marlboro Box (quedan 5 unidades)"},
        {"tipo": "error", "mensaje": "Sin stock: Red Bull (0 unidades)"},
        {"tipo": "success", "mensaje": "Producto estrella: Cerveza Corona (+45% vs mes pasado)"},
        {"tipo": "info", "mensaje": "Recomendación: Aumentar stock de cervezas para el fin de semana"}
    ]
    
    for alerta in alertas:
        if alerta["tipo"] == "warning":
            st.warning(f"{alerta['mensaje']}")
        elif alerta["tipo"] == "error":
            st.error(f"{alerta['mensaje']}")
        elif alerta["tipo"] == "success":
            st.success(f"{alerta['mensaje']}")
        else:
            st.info(f"{alerta['mensaje']}")

def mostrar_predicciones():
    """Muestra predicciones simples"""
    st.markdown("#### Predicciones para la Próxima Semana")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Ventas Estimadas",
            value="$45,200",
            delta="+12% vs semana pasada"
        )
    
    with col2:
        st.metric(
            label="Producto + Demandado",
            value="Cerveza Corona",
            delta="85 unidades estimadas"
        )
    
    with col3:
        st.metric(
            label="Mejor Día",
            value="Sábado",
            delta="$8,500 estimados"
        )

def demo_reportes_completos():
    """Función principal de la demo"""
    st.title("Demo: ¿Qué hacen los Reportes?")
    
    st.markdown("""
    ### **Los reportes te ayudan a entender tu negocio**
    
    Imagina que tienes estos datos de los últimos 30 días:
    """)
    
    # Crear datos de ejemplo
    df_ventas = crear_datos_ejemplo()
    
    # Mostrar resumen general
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_ventas = len(df_ventas)
        st.metric("Total Ventas", total_ventas)
    
    with col2:
        total_ingresos = df_ventas['precio_total'].sum()
        st.metric("Ingresos", f"${total_ingresos:,.0f}")
    
    with col3:
        productos_unicos = df_ventas['producto'].nunique()
        st.metric("Productos Vendidos", productos_unicos)
    
    with col4:
        promedio_venta = df_ventas['precio_total'].mean()
        st.metric("Ticket Promedio", f"${promedio_venta:.0f}")
    
    st.markdown("---")
    
    # Mostrar diferentes tipos de análisis
    tab1, tab2, tab3, tab4 = st.tabs([
        "Top Productos", "Análisis Temporal", 
        "Alertas", "Predicciones"
    ])
    
    with tab1:
        mostrar_reporte_ventas_top(df_ventas)
        st.markdown("""
        **¿Para qué sirve esto?**
        - Saber qué productos pedir más
        - Identificar tus productos estrella
        - Optimizar el espacio de tu local
        """)
    
    with tab2:
        mostrar_analisis_temporal(df_ventas)
        st.markdown("""
        **¿Para qué sirve esto?**
        - Planificar horarios de trabajo
        - Preparar stock para días ocupados
        - Optimizar promociones
        """)
    
    with tab3:
        mostrar_alertas_inventario()
        st.markdown("""
        **¿Para qué sirve esto?**
        - Evitar quedarte sin productos populares
        - No perder ventas por falta de stock
        - Tomar decisiones rápidas
        """)
    
    with tab4:
        mostrar_predicciones()
        st.markdown("""
        **¿Para qué sirve esto?**
        - Planificar compras futuras
        - Prepararte para días ocupados
        - Maximizar ganancias
        """)
    
    st.markdown("---")
    st.success("""
    ### **¡Esto es lo que pueden hacer los Reportes Completos!**
    
    **Con el modo modular activado tendrás:**
    - **Gráficos interactivos** en tiempo real
    - **Análisis de tendencias** automáticos  
    - **Recomendaciones personalizadas** para tu negocio
    - **Exportación** a Excel/PDF para compartir
    - **Predicciones avanzadas** con inteligencia artificial
    """)

if __name__ == "__main__":
    demo_reportes_completos()