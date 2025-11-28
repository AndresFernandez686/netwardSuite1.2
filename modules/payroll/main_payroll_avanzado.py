"""
Sistema de Cálculo de Sueldos - BusinessSuite
Módulo principal integrado con todas las funcionalidades avanzadas
"""
import streamlit as st
import pandas as pd
import io
from datetime import datetime
import sys
import os

# Agregar el directorio raíz al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Importar nuevos módulos integrados
try:
    from .calculations import calcular_sueldo_basico, calcular_horas_especiales
    from .data_processor import validar_archivo_excel, procesar_datos_excel, mostrar_resultados, exportar_resultados, crear_plantilla_excel
    from .pdf_processor import mostrar_interface_pdf, verificar_dependencias_pdf
    from .smart_parser import mostrar_interface_smart_parser
    from .ui_components import mostrar_header_aplicacion, crear_tarjeta_metrica, mostrar_tabla_interactiva, crear_selector_periodo
    from .loading_components import loading_manager, ejecutar_con_progreso, ProgressTracker
    MODULOS_AVANZADOS = True
except ImportError:
    MODULOS_AVANZADOS = False

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
        
        # Mostrar header de la aplicación
        if MODULOS_AVANZADOS:
            mostrar_header_aplicacion(
                "Sistema de Cálculo de Sueldos", 
                "Gestión completa de nóminas y cálculos salariales",
                user_info['username']
            )
        else:
            st.title("🏢 Sistema de Cálculo de Sueldos")
            st.markdown("*Gestión completa de nóminas y cálculos salariales*")
            st.info(f"👤 Usuario: {user_info['username']}")
            st.divider()
        
        # Menú de opciones
        if MODULOS_AVANZADOS:
            opciones = [
                "Cálculo Rápido",
                "Procesamiento Excel",
                "Procesamiento PDF", 
                "Análisis Inteligente",
                "Gestión de Empleados",
                "Reportes y Análisis"
            ]
            iconos = ["🧮", "📊", "📄", "🧠", "👥", "📈"]
            
            # Crear tabs en lugar de menú lateral para mejor UX
            tabs = st.tabs([f"{icono} {opcion}" for icono, opcion in zip(iconos, opciones)])
            
            with tabs[0]:
                mostrar_calculo_rapido()
            
            with tabs[1]:
                mostrar_procesamiento_excel()
            
            with tabs[2]:
                mostrar_procesamiento_pdf()
            
            with tabs[3]:
                mostrar_analisis_inteligente()
            
            with tabs[4]:
                mostrar_gestion_empleados()
            
            with tabs[5]:
                mostrar_reportes_analisis()
        
        else:
            # Modo básico sin módulos avanzados
            st.warning("⚠️ Funcionando en modo básico - algunos módulos avanzados no están disponibles")
            mostrar_interfaz_basica_sueldos()
        
    except Exception as e:
        st.error(f"❌ Error en módulo de cálculo de sueldos: {e}")
        st.exception(e)

def mostrar_calculo_rapido():
    """Muestra la interfaz de cálculo rápido de sueldos"""
    st.subheader("🧮 Cálculo Rápido de Sueldo")
    
    with st.form("calculo_rapido"):
        col1, col2 = st.columns(2)
        
        with col1:
            empleado_nombre = st.text_input("👤 Nombre del Empleado", placeholder="Ej: Juan Pérez")
            horas_normales = st.number_input("⏰ Horas Normales", min_value=0.0, max_value=168.0, value=40.0, step=0.5)
            valor_hora_normal = st.number_input("💰 Valor Hora Normal (Gs.)", min_value=0, value=15000, step=1000)
        
        with col2:
            horas_especiales = st.number_input("🌙 Horas Especiales", min_value=0.0, max_value=40.0, value=0.0, step=0.5)
            valor_hora_especial = st.number_input("💸 Valor Hora Especial (Gs.)", min_value=0, value=18000, step=1000)
            descuentos = st.number_input("📉 Descuentos (Gs.)", min_value=0, value=0, step=1000)
        
        calcular_btn = st.form_submit_button("🧮 Calcular Sueldo", type="primary")
        
        if calcular_btn:
            if not empleado_nombre.strip():
                st.error("❌ Por favor ingrese el nombre del empleado")
            else:
                # Realizar cálculo
                if MODULOS_AVANZADOS:
                    calculo = calcular_sueldo_basico(horas_normales, horas_especiales, valor_hora_normal, valor_hora_especial)
                else:
                    # Cálculo básico sin módulo avanzado
                    calculo = {
                        'sueldo_normal': horas_normales * valor_hora_normal,
                        'sueldo_especial': horas_especiales * valor_hora_especial,
                        'sueldo_bruto': (horas_normales * valor_hora_normal) + (horas_especiales * valor_hora_especial),
                        'total_horas': horas_normales + horas_especiales
                    }
                
                sueldo_neto = calculo['sueldo_bruto'] - descuentos
                
                # Mostrar resultados
                st.success("Cálculo completado")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if MODULOS_AVANZADOS:
                        crear_tarjeta_metrica("Total Horas", f"{calculo['total_horas']:.1f}h", color="blue")
                    else:
                        st.metric("Total Horas", f"{calculo['total_horas']:.1f}h")
                
                with col2:
                    if MODULOS_AVANZADOS:
                        crear_tarjeta_metrica("Sueldo Normal", f"Gs. {calculo['sueldo_normal']:,.0f}", color="green")
                    else:
                        st.metric("Sueldo Normal", f"Gs. {calculo['sueldo_normal']:,.0f}")
                
                with col3:
                    if MODULOS_AVANZADOS:
                        crear_tarjeta_metrica("Sueldo Especial", f"Gs. {calculo['sueldo_especial']:,.0f}", color="orange")
                    else:
                        st.metric("Sueldo Especial", f"Gs. {calculo['sueldo_especial']:,.0f}")
                
                with col4:
                    if MODULOS_AVANZADOS:
                        crear_tarjeta_metrica("Sueldo Neto", f"Gs. {sueldo_neto:,.0f}", f"Descuentos: -Gs. {descuentos:,.0f}", color="purple")
                    else:
                        st.metric("Sueldo Neto", f"Gs. {sueldo_neto:,.0f}", delta=f"-Gs. {descuentos:,.0f}")
                
                # Detalles adicionales
                st.subheader("📋 Detalle del Cálculo")
                detalle_df = pd.DataFrame({
                    'Concepto': ['Horas Normales', 'Horas Especiales', 'Sueldo Normal', 'Sueldo Especial', 'Sueldo Bruto', 'Descuentos', 'Sueldo Neto'],
                    'Valor': [
                        f"{horas_normales:.1f}h",
                        f"{horas_especiales:.1f}h", 
                        f"Gs. {calculo['sueldo_normal']:,.0f}",
                        f"Gs. {calculo['sueldo_especial']:,.0f}",
                        f"Gs. {calculo['sueldo_bruto']:,.0f}",
                        f"Gs. {descuentos:,.0f}",
                        f"Gs. {sueldo_neto:,.0f}"
                    ]
                })
                
                st.dataframe(detalle_df, hide_index=True, use_container_width=True)

def mostrar_procesamiento_excel():
    """Muestra la interfaz de procesamiento de archivos Excel"""
    st.subheader("📊 Procesamiento de Archivos Excel")
    
    if not MODULOS_AVANZADOS:
        st.warning("⚠️ Funcionalidad avanzada no disponible en modo básico")
        return
    
    # Opción para descargar plantilla
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("📥 **Plantilla Excel**")
        st.write("Descarga la plantilla para organizar los datos de tus empleados")
        
        plantilla_data = crear_plantilla_excel()
        st.download_button(
            label="📥 Descargar Plantilla",
            data=plantilla_data,
            file_name=f"plantilla_empleados_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col2:
        st.info("📤 **Subir Archivo**")
        archivo_excel = st.file_uploader(
            "Seleccione su archivo Excel",
            type=['xlsx', 'xls'],
            help="Suba un archivo Excel con los datos de empleados siguiendo la plantilla"
        )
    
    if archivo_excel:
        st.info(f"📁 Archivo seleccionado: {archivo_excel.name}")
        
        if st.button("🔄 Procesar Archivo Excel", type="primary"):
            # Validar archivo
            with st.spinner("Validando archivo..."):
                es_valido, resultado = validar_archivo_excel(archivo_excel)
            
            if es_valido:
                st.success("✅ Archivo válido")
                
                # Mostrar vista previa
                st.subheader("👀 Vista Previa de Datos")
                st.dataframe(resultado.head(), use_container_width=True)
                
                # Procesar con barra de progreso
                progress_tracker = ProgressTracker(len(resultado), "Procesando Empleados")
                
                def callback_progreso(progreso, mensaje):
                    progress_tracker.siguiente_paso(mensaje)
                
                try:
                    df_resultados = procesar_datos_excel(resultado, callback_progreso)
                    progress_tracker.completar("Procesamiento completado")
                    
                    # Mostrar resultados
                    mostrar_resultados(df_resultados)
                    
                    # Opción de descarga
                    if not df_resultados.empty:
                        excel_resultados = exportar_resultados(df_resultados)
                        st.download_button(
                            label="📥 Descargar Resultados Excel",
                            data=excel_resultados,
                            file_name=f"resultados_sueldos_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                
                except Exception as e:
                    progress_tracker.error(f"Error procesando: {str(e)}")
                    st.error(f"❌ Error durante el procesamiento: {str(e)}")
            
            else:
                st.error(f"❌ Error en el archivo: {resultado}")

def mostrar_procesamiento_pdf():
    """Muestra la interfaz de procesamiento de PDFs"""
    st.subheader("📄 Procesamiento de Archivos PDF")
    
    if not MODULOS_AVANZADOS:
        st.warning("⚠️ Funcionalidad avanzada no disponible en modo básico")
        return
    
    # Verificar dependencias
    dependencias = verificar_dependencias_pdf()
    
    if not dependencias['funcional']:
        st.error("⚠️ Librerías PDF no disponibles")
        st.info("Para usar esta funcionalidad, instale:")
        st.code("pip install PyPDF2 pdfplumber")
        return
    
    # Mostrar interfaz PDF
    mostrar_interface_pdf()

def mostrar_analisis_inteligente():
    """Muestra la interfaz de análisis inteligente"""
    st.subheader("🧠 Análisis Inteligente de Horarios")
    
    if not MODULOS_AVANZADOS:
        st.warning("⚠️ Funcionalidad avanzada no disponible en modo básico")
        return
    
    mostrar_interface_smart_parser()

def mostrar_gestion_empleados():
    """Muestra la interfaz de gestión de empleados"""
    st.subheader("👥 Gestión de Empleados")
    
    # Datos de ejemplo de empleados (en un sistema real vendrían de la BD)
    empleados_ejemplo = pd.DataFrame({
        'ID': [1, 2, 3, 4],
        'Empleado': ['Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez'],
        'Cargo': ['Cajero', 'Vendedor', 'Supervisor', 'Gerente'],
        'Salario_Base': [2500000, 2800000, 3200000, 4500000],
        'Estado': ['Activo', 'Activo', 'Activo', 'Activo'],
        'Fecha_Ingreso': ['2023-01-15', '2023-02-20', '2022-11-10', '2022-08-05']
    })
    
    # Mostrar tabla de empleados
    if MODULOS_AVANZADOS:
        mostrar_tabla_interactiva(empleados_ejemplo, "Empleados", acciones=True)
    else:
        st.dataframe(empleados_ejemplo, use_container_width=True)
    
    # Opciones de gestión
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Nuevo Empleado"):
            st.info("Funcionalidad de nuevo empleado en desarrollo")
    
    with col2:
        if st.button("📝 Editar Empleado"):
            st.info("Funcionalidad de edición en desarrollo")
    
    with col3:
        if st.button("📊 Ver Detalles"):
            st.info("Funcionalidad de detalles en desarrollo")

def mostrar_reportes_analisis():
    """Muestra la interfaz de reportes y análisis"""
    st.subheader("📈 Reportes y Análisis")
    
    if MODULOS_AVANZADOS:
        # Selector de período
        fecha_inicio, fecha_fin = crear_selector_periodo()
        
        st.info(f"📅 Análisis del período: {fecha_inicio} al {fecha_fin}")
    
    # Datos de ejemplo para reportes
    datos_reporte = pd.DataFrame({
        'Mes': ['Enero', 'Febrero', 'Marzo', 'Abril'],
        'Total_Empleados': [15, 16, 15, 17],
        'Total_Horas': [2400, 2560, 2400, 2720],
        'Total_Sueldos': [45000000, 48000000, 45000000, 51000000],
        'Promedio_Sueldo': [3000000, 3000000, 3000000, 3000000]
    })
    
    # Métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if MODULOS_AVANZADOS:
            crear_tarjeta_metrica("Empleados Promedio", "16", "+1 vs mes anterior", "blue")
        else:
            st.metric("Empleados Promedio", "16", "+1")
    
    with col2:
        if MODULOS_AVANZADOS:
            crear_tarjeta_metrica("Horas Totales", "2,520h", "+120h vs mes anterior", "green")
        else:
            st.metric("Horas Totales", "2,520h", "+120h")
    
    with col3:
        if MODULOS_AVANZADOS:
            crear_tarjeta_metrica("Costo Total", "Gs. 47.3M", "+Gs. 2.3M vs mes anterior", "orange")
        else:
            st.metric("Costo Total", "Gs. 47.3M", "+Gs. 2.3M")
    
    with col4:
        if MODULOS_AVANZADOS:
            crear_tarjeta_metrica("Sueldo Promedio", "Gs. 3.0M", "Sin cambios", "purple")
        else:
            st.metric("Sueldo Promedio", "Gs. 3.0M", "0")
    
    # Tabla de resumen
    st.subheader("📊 Resumen por Período")
    st.dataframe(datos_reporte, use_container_width=True)
    
    # Gráficos básicos
    if len(datos_reporte) > 1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👥 Evolución de Empleados")
            st.line_chart(datos_reporte.set_index('Mes')['Total_Empleados'])
        
        with col2:
            st.subheader("💰 Evolución de Sueldos")
            st.line_chart(datos_reporte.set_index('Mes')['Total_Sueldos'])

def mostrar_interfaz_basica_sueldos():
    """Interfaz básica cuando los módulos avanzados no están disponibles"""
    st.subheader("🧮 Cálculo Básico de Sueldos")
    
    with st.form("calculo_basico"):
        empleado = st.text_input("👤 Empleado", placeholder="Nombre del empleado")
        horas_normales = st.number_input("⏰ Horas Normales", min_value=0.0, value=40.0)
        horas_extras = st.number_input("🌙 Horas Extras", min_value=0.0, value=0.0)
        valor_hora = st.number_input("💰 Valor por Hora (Gs.)", min_value=0, value=15000)
        descuentos = st.number_input("📉 Descuentos (Gs.)", min_value=0, value=0)
        
        calcular = st.form_submit_button("🧮 Calcular", type="primary")
        
        if calcular and empleado:
            sueldo_normal = horas_normales * valor_hora
            sueldo_extra = horas_extras * valor_hora * 1.5  # 50% extra
            sueldo_bruto = sueldo_normal + sueldo_extra
            sueldo_neto = sueldo_bruto - descuentos
            
            st.success("Cálculo completado")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sueldo Bruto", f"Gs. {sueldo_bruto:,.0f}")
            with col2:
                st.metric("Descuentos", f"Gs. {descuentos:,.0f}")
            with col3:
                st.metric("💵 Sueldo Neto", f"Gs. {sueldo_neto:,.0f}")

if __name__ == "__main__":
    main_payroll()