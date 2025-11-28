"""
Módulo de Cálculo de Sueldos - BusinessSuite
Versión simplificada y funcional integrada desde Calculo 1.3
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

def main_payroll():
    """Función principal del módulo de cálculo de sueldos"""
    try:
        # Verificar si hay usuario autenticado
        if 'user_info' not in st.session_state:
            st.error("❌ No hay usuario autenticado")
            return
        
        user_info = st.session_state.user_info
        
        # Solo administradores pueden acceder
        if user_info['role'] != 'admin':
            st.error("❌ Acceso denegado: Solo administradores pueden acceder al cálculo de sueldos")
            st.info("Este módulo requiere permisos de administrador")
            return
        
        # Mostrar interfaz de cálculo de sueldos
        mostrar_interfaz_calculo_sueldos()
        
    except Exception as e:
        st.error(f"❌ Error en módulo de cálculo de sueldos: {e}")
        st.info("Verifica la configuración del sistema de cálculos.")

def mostrar_interfaz_calculo_sueldos():
    """Interfaz principal para cálculo de sueldos"""
    st.title("💰 Cálculo de Sueldos - BusinessSuite")
    
    # Información del usuario
    user_info = st.session_state.get('user_info', {})
    st.info(f"👤 **Usuario:** {user_info.get('name', 'Administrador')} | 🔑 **Rol:** {user_info.get('role', 'admin').title()}")
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["📊 Cálculo Rápido", "📁 Desde Archivo", "📋 Historial"])
    
    with tab1:
        mostrar_calculo_rapido()
    
    with tab2:
        mostrar_calculo_archivo()
    
    with tab3:
        mostrar_historial_calculos()

def mostrar_calculo_rapido():
    """Cálculo rápido de sueldo individual"""
    st.subheader("⚡ Cálculo Rápido de Sueldo")
    
    with st.form("calculo_rapido", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_empleado = st.text_input("👤 Nombre del empleado", placeholder="Ej: Juan Pérez")
            
            valor_hora_normal = st.number_input(
                "💵 Valor hora normal (Gs.)",
                min_value=0,
                value=15000,
                step=1000,
                help="Valor por hora en guaraníes"
            )
            
            horas_normales = st.number_input(
                "⏰ Horas normales trabajadas",
                min_value=0.0,
                value=0.0,
                step=0.5,
                format="%.1f"
            )
        
        with col2:
            valor_hora_especial = st.number_input(
                "🌙 Valor hora especial (Gs.)",
                min_value=0,
                value=18000,
                step=1000,
                help="Valor por hora nocturna/especial"
            )
            
            horas_especiales = st.number_input(
                "🌙 Horas especiales trabajadas",
                min_value=0.0,
                value=0.0,
                step=0.5,
                format="%.1f"
            )
            
            descuentos = st.number_input(
                "📉 Descuentos (Gs.)",
                min_value=0,
                value=0,
                step=1000,
                help="IPS, multas, adelantos, etc."
            )
        
        # Botón de cálculo
        calcular = st.form_submit_button("🧮 Calcular Sueldo", use_container_width=True)
        
        if calcular:
            if nombre_empleado.strip():
                # Realizar cálculos
                sueldo_normal = horas_normales * valor_hora_normal
                sueldo_especial = horas_especiales * valor_hora_especial
                sueldo_bruto = sueldo_normal + sueldo_especial
                sueldo_neto = sueldo_bruto - descuentos
                
                # Mostrar resultados
                st.success("Cálculo completado")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Sueldo Bruto", f"Gs. {sueldo_bruto:,.0f}")
                    st.metric("⏰ Total Horas", f"{horas_normales + horas_especiales:.1f}")
                
                with col2:
                    st.metric("Descuentos", f"Gs. {descuentos:,.0f}")
                    st.metric("🌙 Horas Especiales", f"{horas_especiales:.1f}")
                
                with col3:
                    st.metric("💵 Sueldo Neto", f"Gs. {sueldo_neto:,.0f}")
                    st.metric("☀️ Horas Normales", f"{horas_normales:.1f}")
                
                # Guardar en historial
                if 'historial_calculos' not in st.session_state:
                    st.session_state.historial_calculos = []
                
                nuevo_calculo = {
                    'fecha': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'empleado': nombre_empleado,
                    'horas_normales': horas_normales,
                    'horas_especiales': horas_especiales,
                    'valor_hora_normal': valor_hora_normal,
                    'valor_hora_especial': valor_hora_especial,
                    'sueldo_bruto': sueldo_bruto,
                    'descuentos': descuentos,
                    'sueldo_neto': sueldo_neto
                }
                
                st.session_state.historial_calculos.append(nuevo_calculo)
                
                # Generar resumen detallado
                with st.expander("📋 Resumen Detallado", expanded=True):
                    st.markdown(f"""
                    **👤 Empleado:** {nombre_empleado}
                    
                    **⏰ Detalle de Horas:**
                    - Horas normales: {horas_normales:.1f} × Gs. {valor_hora_normal:,} = Gs. {sueldo_normal:,.0f}
                    - Horas especiales: {horas_especiales:.1f} × Gs. {valor_hora_especial:,} = Gs. {sueldo_especial:,.0f}
                    
                    **💰 Cálculo Final:**
                    - Sueldo bruto: Gs. {sueldo_bruto:,.0f}
                    - Descuentos: Gs. {descuentos:,.0f}
                    - **Sueldo neto: Gs. {sueldo_neto:,.0f}**
                    """)
            else:
                st.error("❌ Ingresa el nombre del empleado")

def mostrar_calculo_archivo():
    """Cálculo desde archivo Excel"""
    st.subheader("📁 Cálculo desde Archivo Excel")
    
    # Plantilla de ejemplo
    with st.expander("📄 Descargar Plantilla", expanded=False):
        st.info("💡 Descarga la plantilla para cargar múltiples empleados")
        
        # Crear plantilla de ejemplo
        plantilla_data = {
            'Empleado': ['Juan Pérez', 'María García', 'Carlos López'],
            'Horas_Normales': [40.0, 35.5, 42.0],
            'Horas_Especiales': [5.0, 8.0, 3.5],
            'Valor_Hora_Normal': [15000, 16000, 14500],
            'Valor_Hora_Especial': [18000, 19200, 17400],
            'Descuentos': [50000, 45000, 30000]
        }
        
        df_plantilla = pd.DataFrame(plantilla_data)
        
        # Convertir a Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_plantilla.to_excel(writer, sheet_name='Empleados', index=False)
        
        output.seek(0)
        
        st.download_button(
            label="📥 Descargar Plantilla Excel",
            data=output.getvalue(),
            file_name="plantilla_sueldos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # Subir archivo
    archivo_subido = st.file_uploader(
        "📤 Subir archivo Excel",
        type=['xlsx', 'xls'],
        help="Archivo con datos de empleados según la plantilla"
    )
    
    if archivo_subido is not None:
        try:
            # Leer archivo Excel
            df = pd.read_excel(archivo_subido)
            
            st.success("✅ Archivo cargado correctamente")
            st.subheader("👥 Vista Previa de Datos")
            st.dataframe(df, use_container_width=True)
            
            # Validar columnas requeridas
            columnas_requeridas = ['Empleado', 'Horas_Normales', 'Horas_Especiales', 
                                 'Valor_Hora_Normal', 'Valor_Hora_Especial', 'Descuentos']
            
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            
            if columnas_faltantes:
                st.error(f"❌ Faltan las siguientes columnas: {', '.join(columnas_faltantes)}")
                st.info("💡 Asegúrate de usar la plantilla proporcionada")
            else:
                if st.button("🧮 Calcular Sueldos del Archivo", type="primary"):
                    # Realizar cálculos para todos los empleados
                    resultados = []
                    
                    for index, row in df.iterrows():
                        sueldo_normal = row['Horas_Normales'] * row['Valor_Hora_Normal']
                        sueldo_especial = row['Horas_Especiales'] * row['Valor_Hora_Especial']
                        sueldo_bruto = sueldo_normal + sueldo_especial
                        sueldo_neto = sueldo_bruto - row['Descuentos']
                        
                        resultado = {
                            'Empleado': row['Empleado'],
                            'Horas_Normales': row['Horas_Normales'],
                            'Horas_Especiales': row['Horas_Especiales'],
                            'Total_Horas': row['Horas_Normales'] + row['Horas_Especiales'],
                            'Sueldo_Bruto': sueldo_bruto,
                            'Descuentos': row['Descuentos'],
                            'Sueldo_Neto': sueldo_neto
                        }
                        resultados.append(resultado)
                    
                    # Crear DataFrame con resultados
                    df_resultados = pd.DataFrame(resultados)
                    
                    st.success(f"✅ Cálculos completados para {len(df_resultados)} empleados")
                    
                    # Mostrar resumen general
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("👥 Total Empleados", len(df_resultados))
                    
                    with col2:
                        total_bruto = df_resultados['Sueldo_Bruto'].sum()
                        st.metric("Total Bruto", f"Gs. {total_bruto:,.0f}")
                    
                    with col3:
                        total_neto = df_resultados['Sueldo_Neto'].sum()
                        st.metric("💵 Total Neto", f"Gs. {total_neto:,.0f}")
                    
                    # Mostrar tabla de resultados
                    st.subheader("📊 Resultados del Cálculo")
                    st.dataframe(
                        df_resultados.style.format({
                            'Sueldo_Bruto': 'Gs. {:,.0f}',
                            'Descuentos': 'Gs. {:,.0f}',
                            'Sueldo_Neto': 'Gs. {:,.0f}',
                            'Horas_Normales': '{:.1f}',
                            'Horas_Especiales': '{:.1f}',
                            'Total_Horas': '{:.1f}'
                        }),
                        use_container_width=True
                    )
                    
                    # Botón para descargar resultados
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_resultados.to_excel(writer, sheet_name='Resultados', index=False)
                    
                    output.seek(0)
                    
                    st.download_button(
                        label="📥 Descargar Resultados",
                        data=output.getvalue(),
                        file_name=f"resultados_sueldos_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        
        except Exception as e:
            st.error(f"❌ Error procesando archivo: {str(e)}")

def mostrar_historial_calculos():
    """Mostrar historial de cálculos realizados"""
    st.subheader("📋 Historial de Cálculos")
    
    if 'historial_calculos' in st.session_state and st.session_state.historial_calculos:
        # Mostrar estadísticas generales
        historial = st.session_state.historial_calculos
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📊 Total Cálculos", len(historial))
        
        with col2:
            total_empleados = len(set(calc['empleado'] for calc in historial))
            st.metric("👥 Empleados Únicos", total_empleados)
        
        with col3:
            total_neto = sum(calc['sueldo_neto'] for calc in historial)
            st.metric("💵 Total Pagado", f"Gs. {total_neto:,.0f}")
        
        # Convertir a DataFrame para mostrar
        df_historial = pd.DataFrame(historial)
        
        # Mostrar tabla
        st.dataframe(
            df_historial.style.format({
                'sueldo_bruto': 'Gs. {:,.0f}',
                'descuentos': 'Gs. {:,.0f}',
                'sueldo_neto': 'Gs. {:,.0f}',
                'valor_hora_normal': 'Gs. {:,.0f}',
                'valor_hora_especial': 'Gs. {:,.0f}',
                'horas_normales': '{:.1f}',
                'horas_especiales': '{:.1f}'
            }),
            use_container_width=True
        )
        
        # Botón para limpiar historial
        if st.button("🗑️ Limpiar Historial"):
            st.session_state.historial_calculos = []
            st.success("✅ Historial limpiado")
            st.rerun()
    else:
        st.info("📋 No hay cálculos en el historial")
        st.markdown("💡 **Sugerencia:** Realiza algunos cálculos en las pestañas anteriores para ver el historial aquí.")

# Función principal para compatibilidad
if __name__ == "__main__":
    main_payroll()