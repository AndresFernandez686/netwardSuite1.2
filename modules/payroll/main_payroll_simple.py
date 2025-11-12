"""
Módulo de Cálculo de Nómina - BusinessSuite
Sistema de gestión de sueldos integrado
"""
import streamlit as st
import pandas as pd
import sys
import os

# Configurar path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def run_payroll_app():
    """Función principal del módulo de cálculo de nómina"""
    
    # Importar componentes localmente para evitar errores
    try:
        from ui_components import (
            mostrar_descarga_plantilla, 
            mostrar_input_valor_hora, 
            configurar_feriados, 
            mostrar_subida_archivo
        )
        from data_processor import (
            validar_archivo_excel, 
            procesar_datos_excel, 
            mostrar_resultados
        )
        from loading_components import (
            mostrar_loading_excel,
            mostrar_loading_pdf,
            mostrar_loading_calculos,
            mostrar_loading_validacion,
            loading_context
        )
        
        imports_ok = True
    except ImportError as e:
        imports_ok = False
        st.error(f"❌ **Error al importar módulos de nómina:** {e}")
        st.info("Verifica que todos los archivos estén en la carpeta modules/payroll/")
        
        if st.button("🔄 Reintentar Carga", use_container_width=True):
            st.rerun()
        return
    
    # Función para limpiar session state
    def _limpiar_session_state_correcciones():
        keys_to_remove = ['correcciones_horarios', 'decisiones_admin', 'correcciones_ambiguos']
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
    
    # Cargar CSS
    def load_css():
        try:
            css_path = os.path.join(current_dir, "styles.css")
            if os.path.exists(css_path):
                with open(css_path, encoding='utf-8') as f:
                    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except Exception as e:
            # CSS básico si falla
            st.markdown("""
            <style>
            .payroll-header {
                background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
                padding: 2rem;
                border-radius: 10px;
                margin-bottom: 2rem;
                text-align: center;
                color: white;
            }
            .section-card {
                background: white;
                padding: 1.5rem;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                margin-bottom: 1.5rem;
            }
            </style>
            """, unsafe_allow_html=True)
    
    # Cargar estilos
    load_css()
    
    # Header del módulo
    st.markdown("""
    <div class="payroll-header">
        <h1>💰 Cálculo de Nómina</h1>
        <p><strong>Sistema de Gestión de Sueldos y Pagos</strong></p>
        <small>Procesamiento de PDFs • Cálculo Automático • Reportes Detallados</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar session_state si es necesario
    if "exit_app" not in st.session_state:
        st.session_state.exit_app = False
    
    # Sección de configuración
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📋 Configuración")
        mostrar_descarga_plantilla()
        valor_por_hora = mostrar_input_valor_hora()
    
    with col2:
        st.markdown("### 📅 Feriados")
        opcion_feriados, dias_feriados, cantidad_feriados = configurar_feriados()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sección de carga de archivo
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 📤 Cargar Archivo")
    
    archivo_excel, archivos_pdf = mostrar_subida_archivo()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Procesamiento
    if archivo_excel is not None or archivos_pdf:
        try:
            # 1. Validar y cargar datos
            if archivo_excel:
                with loading_context(mostrar_loading_excel):
                    df = validar_archivo_excel(archivo_excel)
                    if df is None:
                        st.stop()
            elif archivos_pdf:
                # Importar procesador de PDF
                try:
                    from pdf_processor import (
                        procesar_pdf_a_dataframe, 
                        validar_datos_pdf,
                        detectar_registros_incompletos, 
                        filtrar_registros_sin_asistencia, 
                        detectar_horarios_ambiguos
                    )
                    from ui_components import (
                        mostrar_editor_registros_incompletos, 
                        aplicar_correcciones_a_dataframe,
                        mostrar_editor_horarios_ambiguos,
                        mostrar_validacion_datos,
                        mostrar_informacion_archivo,
                        generar_resumen_empleados,
                        mostrar_resumen_empleados_corregido,
                        crear_dataframe_visualizacion,
                        aplicar_correcciones_ambiguos_a_dataframe
                    )
                except ImportError as e:
                    st.error(f"❌ Error importando procesador de PDF: {e}")
                    st.stop()
                
                with loading_context(mostrar_loading_pdf):
                    df = procesar_pdf_a_dataframe(archivos_pdf)
                
                if df is None or df.empty:
                    st.error("❌ No se pudieron procesar los archivos PDF")
                    st.stop()
                
                # Mostrar información del archivo
                mostrar_informacion_archivo(df, archivos_pdf)
                
                # Validación de datos
                val_placeholder = st.empty()
                with val_placeholder:
                    mostrar_loading_validacion()
                
                validacion_exitosa, mensaje_validacion = validar_datos_pdf(df)
                val_placeholder.empty()
                
                if not validacion_exitosa:
                    st.error(f"❌ {mensaje_validacion}")
                    st.stop()
                
                # Filtrar registros sin asistencia
                df_con_asistencia = filtrar_registros_sin_asistencia(df)
                
                # Detectar registros incompletos
                df_incompletos = detectar_registros_incompletos(df_con_asistencia)
                
                if not df_incompletos.empty:
                    st.markdown(f"""
                    <div class="custom-alert alert-warning">
                        <strong>⚠️ {len(df_incompletos)} registro(s) incompleto(s)</strong><br>
                        Algunos registros necesitan información adicional.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    correcciones_aplicadas, _ = mostrar_editor_registros_incompletos(df_incompletos)
                    
                    if correcciones_aplicadas:
                        df_con_asistencia = aplicar_correcciones_a_dataframe(df_con_asistencia, df_incompletos)
                        st.success(f"✅ {len(df_incompletos)} registro(s) corregido(s) exitosamente")
                        _limpiar_session_state_correcciones()
                    else:
                        st.warning("⚠️ Completa los datos faltantes y presiona 'Aplicar Correcciones' para continuar")
                        st.stop()
                
                df = df_con_asistencia
                
                # Detectar horarios ambiguos
                df_ambiguos = detectar_horarios_ambiguos(df)
                
                if not df_ambiguos.empty:
                    st.markdown(f"""
                    <div class="custom-alert alert-info">
                        <strong>🤔 {len(df_ambiguos)} registro(s) con horarios sospechosos</strong><br>
                        Se detectaron horarios que podrían estar mal asignados.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    try:
                        correcciones_ambiguos_aplicadas, _ = mostrar_editor_horarios_ambiguos(df_ambiguos)
                        
                        if correcciones_ambiguos_aplicadas:
                            df = aplicar_correcciones_ambiguos_a_dataframe(df, df_ambiguos)
                            st.success(f"✅ Se corrigieron {len(df_ambiguos)} registro(s) con horarios ambiguos")
                    except Exception as e:
                        st.warning(f"No se pudieron procesar horarios ambiguos: {e}")
            
            # Realizar cálculos
            calc_placeholder = st.empty()
            with calc_placeholder:
                mostrar_loading_calculos()
            
            resultados, total_horas, total_sueldos, total_horas_normales, total_horas_especiales = procesar_datos_excel(
                df, valor_por_hora, opcion_feriados, dias_feriados, cantidad_feriados
            )
            calc_placeholder.empty()
            
            # Mostrar resultados
            nombre_archivo = None
            if archivos_pdf:
                if len(archivos_pdf) == 1:
                    nombre_archivo = archivos_pdf[0].name
                else:
                    nombre_archivo = f"combinado_{len(archivos_pdf)}_pdfs"
            
            mostrar_resultados(resultados, total_horas, total_sueldos, total_horas_normales, 
                             total_horas_especiales, valor_por_hora, dias_feriados, nombre_archivo)
            
        except Exception as e:
            st.error(f"❌ Error en el procesamiento: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            st.info("Verifica que todos los módulos estén correctamente configurados.")

if __name__ == "__main__":
    run_payroll_app()
