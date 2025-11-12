"""
Módulo de Cálculo de Nómina - BusinessSuite
Adaptado del sistema Calculo1.3 para integración con BusinessSuite

Solo accesible para Administradores
"""
import streamlit as st
import pandas as pd
import os
import sys

# Agregar el directorio del módulo al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Importaciones de los componentes del módulo de nómina
payroll_imports_ok = True

try:
    import ui_components
    mostrar_descarga_plantilla = ui_components.mostrar_descarga_plantilla
    mostrar_input_valor_hora = ui_components.mostrar_input_valor_hora
    configurar_feriados = ui_components.configurar_feriados
    mostrar_subida_archivo = ui_components.mostrar_subida_archivo
    mostrar_editor_registros_incompletos = ui_components.mostrar_editor_registros_incompletos
    aplicar_correcciones_a_dataframe = ui_components.aplicar_correcciones_a_dataframe
    mostrar_editor_horarios_ambiguos = ui_components.mostrar_editor_horarios_ambiguos
    aplicar_correcciones_ambiguos_a_dataframe = ui_components.aplicar_correcciones_ambiguos_a_dataframe
    ui_components_available = True
except ImportError as e:
    payroll_imports_ok = False
    ui_components_available = False
    mostrar_descarga_plantilla = mostrar_input_valor_hora = None
    configurar_feriados = mostrar_subida_archivo = None
    mostrar_editor_registros_incompletos = aplicar_correcciones_a_dataframe = None
    mostrar_editor_horarios_ambiguos = aplicar_correcciones_ambiguos_a_dataframe = None
    st.error(f"❌ Error importando ui_components: {e}")

try:
    import data_processor
    validar_archivo_excel = data_processor.validar_archivo_excel
    procesar_datos_excel = data_processor.procesar_datos_excel
    mostrar_resultados = data_processor.mostrar_resultados
    data_processor_available = True
except ImportError as e:
    payroll_imports_ok = False
    data_processor_available = False
    validar_archivo_excel = procesar_datos_excel = mostrar_resultados = None
    st.error(f"❌ Error importando data_processor: {e}")

try:
    import loading_components
    mostrar_loading_excel = loading_components.mostrar_loading_excel
    mostrar_loading_pdf = loading_components.mostrar_loading_pdf
    mostrar_loading_calculos = loading_components.mostrar_loading_calculos
    mostrar_loading_validacion = loading_components.mostrar_loading_validacion
    loading_context = loading_components.loading_context
except ImportError as e:
    payroll_imports_ok = False
    mostrar_loading_excel = mostrar_loading_pdf = None
    mostrar_loading_calculos = mostrar_loading_validacion = loading_context = None
    st.error(f"❌ Error importando loading_components: {e}")

try:
    import pdf_processor
    procesar_pdf_a_dataframe = pdf_processor.procesar_pdf_a_dataframe
    validar_datos_pdf = pdf_processor.validar_datos_pdf
    detectar_registros_incompletos = pdf_processor.detectar_registros_incompletos
    filtrar_registros_sin_asistencia = pdf_processor.filtrar_registros_sin_asistencia
    detectar_horarios_ambiguos = pdf_processor.detectar_horarios_ambiguos
    pdf_processor_available = True
except ImportError as e:
    payroll_imports_ok = False
    pdf_processor_available = False
    procesar_pdf_a_dataframe = validar_datos_pdf = None
    detectar_registros_incompletos = filtrar_registros_sin_asistencia = detectar_horarios_ambiguos = None
    st.error(f"❌ Error importando pdf_processor: {e}")

if not payroll_imports_ok:
    st.error("❌ Error al importar algunos módulos de nómina")
    st.info("Verifica que todos los archivos estén en la carpeta modules/payroll/")
    st.info("Algunos componentes del módulo de nómina no están disponibles. Verifica la instalación.")

def _limpiar_session_state_correcciones():
    """
    Limpia las variables de session_state relacionadas con correcciones de horarios
    """
    keys_to_remove = ['correcciones_horarios', 'decisiones_admin', 'correcciones_ambiguos']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]

def load_payroll_css():
    """Carga los estilos CSS específicos del módulo de nómina con soporte responsive"""
    try:
        css_path = os.path.join(current_dir, "styles.css")
        if os.path.exists(css_path):
            with open(css_path, encoding='utf-8') as f:
                base_css = f.read()
                # Agregar CSS responsive al existente
                responsive_css = base_css + """
                /* Responsive additions for payroll module */
                @media (max-width: 768px) {
                    .main-container {
                        padding: 1rem!important;
                    }
                    
                    .section-card {
                        padding: 1rem!important;
                        margin-bottom: 1rem!important;
                    }
                    
                    .main-title {
                        font-size: clamp(1.5rem, 4vw, 2rem)!important;
                    }
                    
                    .metric-value {
                        font-size: clamp(1.3rem, 4vw, 1.8rem)!important;
                    }
                }
                
                @media (max-width: 480px) {
                    .section-header {
                        font-size: 1rem!important;
                    }
                    
                    .custom-alert {
                        padding: 0.8rem!important;
                        font-size: 0.9rem!important;
                    }
                }
                """
                st.markdown(f"<style>{responsive_css}</style>", unsafe_allow_html=True)
        else:
            # CSS responsive completo si no encuentra el archivo
            st.markdown("""
            <style>
            .payroll-header {
                background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
                padding: clamp(1rem, 3vw, 1.5rem);
                border-radius: 10px;
                margin-bottom: 2rem;
                text-align: center;
                color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                word-break: break-word;
                overflow-wrap: break-word;
            }
            
            .payroll-header h1 {
                font-size: clamp(1.5rem, 4vw, 2.2rem);
                margin: 0.5rem 0;
                line-height: 1.2;
            }
            
            .payroll-header p {
                font-size: clamp(0.9rem, 2.5vw, 1.1rem);
                margin: 0.3rem 0;
            }
            
            .section-card {
                background: white;
                padding: clamp(1rem, 3vw, 1.5rem);
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                margin-bottom: 1.5rem;
                border: 1px solid #e1e5e9;
                word-break: break-word;
                overflow-wrap: break-word;
            }
            
            .section-header {
                font-size: clamp(1rem, 3vw, 1.2rem);
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 1rem;
                border-bottom: 2px solid #28a745;
                padding-bottom: 0.5rem;
                word-break: break-word;
            }
            
            .metric-card {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: clamp(0.8rem, 2.5vw, 1rem);
                border-radius: 8px;
                text-align: center;
                border-left: 4px solid #28a745;
                word-break: break-word;
            }
            
            .metric-value {
                font-size: clamp(1.3rem, 4vw, 1.8rem);
                font-weight: bold;
                color: #28a745;
                word-break: break-word;
            }
            
            .custom-alert {
                padding: clamp(0.8rem, 2.5vw, 1rem);
                border-radius: 8px;
                margin: 1rem 0;
                border-left: 4px solid;
                word-break: break-word;
                overflow-wrap: break-word;
                font-size: clamp(0.85rem, 2.3vw, 0.95rem);
                line-height: 1.4;
            }
            
            .alert-success {
                background-color: #d4edda;
                border-color: #28a745;
                color: #155724;
            }
            
            .alert-error {
                background-color: #f8d7da;
                border-color: #dc3545;
                color: #721c24;
            }
            
            .alert-warning {
                background-color: #fff3cd;
                border-color: #ffc107;
                color: #856404;
            }
            
            .alert-info {
                background-color: #cce7ff;
                border-color: #007bff;
                color: #004085;
            }
            
            /* Responsive específico para móviles */
            @media (max-width: 768px) {
                .payroll-header {
                    padding: 1rem;
                    margin-bottom: 1.5rem;
                    border-radius: 8px;
                }
                
                .section-card {
                    padding: 1rem;
                    margin-bottom: 1rem;
                    border-radius: 8px;
                }
                
                .metric-card {
                    padding: 0.8rem;
                }
                
                .custom-alert {
                    padding: 0.8rem;
                    margin: 0.8rem 0;
                }
                
                /* Inputs más grandes en móvil */
                .stTextInput > div > div > input,
                .stNumberInput > div > div > input {
                    min-height: 44px !important;
                    font-size: 16px !important;
                }
                
                .stSelectbox > div > div {
                    min-height: 44px !important;
                    font-size: 16px !important;
                }
                
                /* Botones optimizados para móvil */
                .stButton > button {
                    min-height: 48px !important;
                    font-size: 0.9rem !important;
                    padding: 0.6rem 1rem !important;
                    word-break: break-word !important;
                    white-space: normal !important;
                }
                
                /* File uploader en móvil */
                .stFileUploader > div {
                    word-break: break-word !important;
                }
                
                /* Dataframes responsive */
                .stDataFrame {
                    overflow-x: auto !important;
                    -webkit-overflow-scrolling: touch !important;
                }
                
                /* Progress bars */
                .stProgress {
                    margin: 1rem 0 !important;
                }
            }
            
            @media (max-width: 480px) {
                .payroll-header {
                    padding: 0.8rem;
                }
                
                .section-card {
                    padding: 0.8rem;
                }
                
                .metric-card {
                    padding: 0.6rem;
                }
                
                .custom-alert {
                    padding: 0.6rem;
                    font-size: 0.85rem;
                }
                
                .stButton > button {
                    min-height: 50px !important;
                    font-size: 0.85rem !important;
                }
            }
            
            /* Landscape móvil */
            @media (max-height: 500px) and (orientation: landscape) {
                .payroll-header {
                    padding: 0.6rem;
                    margin-bottom: 1rem;
                }
                
                .section-card {
                    padding: 0.8rem;
                    margin-bottom: 0.8rem;
                }
                
                .custom-alert {
                    padding: 0.6rem;
                    margin: 0.6rem 0;
                }
            }
            
            /* Optimizaciones táctiles */
            @media (hover: none) {
                .stButton > button {
                    touch-action: manipulation !important;
                }
            }
            </style>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"⚠️ No se pudieron cargar los estilos: {e}")

def show_payroll_header():
    """Muestra el header del módulo de nómina"""
    st.markdown("""
    <div class="payroll-header">
        <h1>💰 Cálculo de Nómina</h1>
        <p><strong>Sistema Avanzado de Cálculo de Sueldos</strong></p>
        <small>Procesamiento Excel & PDF • Feriados Configurables • Corrección Inteligente</small>
    </div>
    """, unsafe_allow_html=True)

def run_payroll_app():
    """Función principal del módulo de cálculo de nómina"""
    
    # Verificar que los imports están disponibles
    if not payroll_imports_ok:
        st.error("❌ **Módulo de Nómina No Disponible**")
        st.warning("Faltan componentes necesarios para el funcionamiento del módulo de nómina.")
        st.info("Verifica que todos los archivos estén en la carpeta modules/payroll/")
        
        if st.button("🔄 Reintentar Carga", use_container_width=True):
            st.rerun()
        return
    
    # Cargar estilos específicos
    load_payroll_css()
    
    # Mostrar header del módulo
    show_payroll_header()
    
    # Verificar permisos (doble verificación)
    user_info = st.session_state.get('user_info', {})
    if user_info.get('role') != 'admin':
        st.error("🔒 **Acceso Denegado**")
        st.warning("Este módulo está restringido solo para Administradores.")
        st.info("Si necesitas acceso, contacta al administrador del sistema.")
        return
    
    # Inicializar session_state específico del módulo
    if "payroll_exit" not in st.session_state:
        st.session_state.payroll_exit = False
    
    # Verificar si se debe salir del módulo
    if st.session_state.payroll_exit:
        st.success("✅ Módulo de nómina cerrado correctamente.")
        st.info("Puedes navegar a otro módulo usando la barra lateral.")
        st.session_state.payroll_exit = False
        return
    
    # Sección de configuración
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    
    # Configuración y valor actual
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div class="section-header">📋 Configuración</div>', unsafe_allow_html=True)
        valor_por_hora = mostrar_input_valor_hora()
        
    with col2:
        st.markdown('<div class="section-header">📊 Valor Actual</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card" style="margin-top: 1rem;">
            <div class="metric-label">Valor por Hora</div>
            <div class="metric-value">${valor_por_hora:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Plantilla y feriados
    st.markdown("---")
    col3, col4 = st.columns([1, 1])
    with col3:
        st.markdown('<div class="section-header">📄 Plantilla Excel</div>', unsafe_allow_html=True)
        mostrar_descarga_plantilla()
        
    with col4:
        st.markdown('<div class="section-header">📅 Configuración de Feriados</div>', unsafe_allow_html=True)
        opcion_feriados, dias_feriados, cantidad_feriados = configurar_feriados()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sección de subida de archivo
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    
    uploaded_file, tipo_archivo = mostrar_subida_archivo()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Procesamiento de datos
    if uploaded_file:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        
        if tipo_archivo == "excel":
            # Procesamiento de Excel
            try:
                # Mostrar loading
                loading_placeholder = st.empty()
                with loading_placeholder:
                    mostrar_loading_excel()
                
                df = pd.read_excel(uploaded_file)
                loading_placeholder.empty()
                
                # Validación
                validation_placeholder = st.empty()
                with validation_placeholder:
                    mostrar_loading_validacion("Validando estructura del archivo...")
                
                es_valido, columnas_faltantes = validar_archivo_excel(df)
                validation_placeholder.empty()
                
                if not es_valido:
                    st.markdown(f'''
                    <div class="custom-alert alert-error">
                        <strong>❌ Archivo Excel Inválido</strong><br>
                        El archivo no contiene las siguientes columnas necesarias: <code>{", ".join(columnas_faltantes)}</code>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    # Procesamiento completo con correcciones
                    process_employee_data(df, valor_por_hora, opcion_feriados, dias_feriados, cantidad_feriados)
                    
            except Exception as e:
                st.error(f"❌ Error al procesar el archivo Excel: {str(e)}")
                
        elif tipo_archivo == "pdf":
            # Procesamiento de PDF
            if pdf_processor_available:
                try:
                    archivos_pdf = uploaded_file if isinstance(uploaded_file, list) else [uploaded_file] if uploaded_file else []
                    
                    if not archivos_pdf:
                        st.warning("⚠️ No se han cargado archivos PDF.")
                    else:
                        # Procesar PDFs
                        df_combinado = process_pdf_files(archivos_pdf)
                        
                        if df_combinado is not None and not df_combinado.empty:
                            # Procesamiento completo con correcciones
                            process_employee_data(df_combinado, valor_por_hora, opcion_feriados, dias_feriados, cantidad_feriados, archivos_pdf)
                        
                except Exception as e:
                    st.error(f"❌ Error al procesar archivos PDF: {str(e)}")
            else:
                st.error("❌ El procesador de PDF no está disponible")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Sección de navegación
    st.markdown("---")
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🏠 Volver al Dashboard", use_container_width=True):
            # Limpiar estado del módulo
            _limpiar_session_state_correcciones()
            if 'current_module' in st.session_state:
                del st.session_state['current_module']
            st.rerun()
    
    with col2:
        if st.button("📦 Ir a Inventario", use_container_width=True):
            st.session_state.current_module = 'inventory'
            st.rerun()
    
    with col3:
        if st.button("🔄 Limpiar Sesión", use_container_width=True):
            _limpiar_session_state_correcciones()
            # Limpiar también datos específicos del módulo
            for key in list(st.session_state.keys()):
                if key.startswith('payroll_') or key in ['uploaded_file', 'tipo_archivo']:
                    del st.session_state[key]
            st.success("✅ Sesión limpiada")
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def process_pdf_files(archivos_pdf):
    """Procesa múltiples archivos PDF y los combina"""
    if not pdf_processor_available:
        st.error("❌ El procesador de PDF no está disponible")
        return pd.DataFrame()
    
    # Loading para PDFs
    pdf_loading_placeholder = st.empty()
    with pdf_loading_placeholder:
        mostrar_loading_pdf(len(archivos_pdf))
    
    dataframes_list = []
    nombres_archivos_pdf = []
    
    # Procesar cada PDF
    for idx, archivo_pdf in enumerate(archivos_pdf, 1):
        df_temp = procesar_pdf_a_dataframe(archivo_pdf)
        
        if df_temp.empty:
            st.warning(f"⚠️ No se pudieron extraer datos del PDF {idx}: {archivo_pdf.name}")
        else:
            # Validar datos
            es_valido, errores = validar_datos_pdf(df_temp)
            
            if not es_valido:
                st.warning(f"⚠️ Errores en PDF {idx} ({archivo_pdf.name}):")
                for error in errores:
                    st.markdown(f'<div class="custom-alert alert-warning">• {error}</div>', unsafe_allow_html=True)
            else:
                st.success(f"✅ PDF {idx} procesado: {archivo_pdf.name} ({len(df_temp)} registros)")
                dataframes_list.append(df_temp)
                nombres_archivos_pdf.append(archivo_pdf.name)
    
    pdf_loading_placeholder.empty()
    
    # Combinar DataFrames
    if not dataframes_list:
        st.error("❌ No se pudieron extraer datos de ningún PDF.")
        return None
    
    # Concatenar y ordenar
    df_combinado = pd.concat(dataframes_list, ignore_index=True)
    df_combinado['Fecha'] = pd.to_datetime(df_combinado['Fecha'], errors='coerce')
    df_combinado = df_combinado.sort_values(['Fecha', 'Empleado'], ascending=[True, True]).reset_index(drop=True)
    
    # Agregar columnas de descuentos si no existen (requeridas para el cálculo)
    if 'Descuento Inventario' not in df_combinado.columns:
        df_combinado['Descuento Inventario'] = 0
    if 'Descuento Caja' not in df_combinado.columns:
        df_combinado['Descuento Caja'] = 0
    if 'Retiro' not in df_combinado.columns:
        df_combinado['Retiro'] = 0
    
    # Mostrar información
    fecha_minima = df_combinado['Fecha'].min()
    fecha_maxima = df_combinado['Fecha'].max()
    st.markdown(f"""
    <div class="custom-alert alert-success">
        <strong>✅ PDFs Combinados Exitosamente</strong><br>
        📅 <strong>Período:</strong> {fecha_minima.strftime('%d/%m/%Y')} - {fecha_maxima.strftime('%d/%m/%Y')}<br>
        📊 <strong>Total de registros:</strong> {len(df_combinado)}<br>
        📄 <strong>Archivos procesados:</strong> {len(nombres_archivos_pdf)}
    </div>
    """, unsafe_allow_html=True)
    
    return df_combinado

def process_employee_data(df, valor_por_hora, opcion_feriados, dias_feriados, cantidad_feriados, archivos_pdf=None):
    """Procesa los datos de empleados con todas las correcciones inteligentes"""
    if not pdf_processor_available or not ui_components_available:
        st.error("❌ Los procesadores necesarios no están disponibles")
        return df
    
    try:
        
        # 1. Filtrar registros sin asistencia
        df_con_asistencia, df_sin_asistencia = filtrar_registros_sin_asistencia(df)
        
        if not df_sin_asistencia.empty:
            st.markdown(f"""
            <div class="custom-alert alert-info">
                <strong>ℹ️ {len(df_sin_asistencia)} registro(s) excluido(s) automáticamente</strong><br>
                Empleados sin entrada ni salida (día libre o falta). No se incluirán en el cálculo.
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("👁️ Ver registros excluidos", expanded=False):
                st.dataframe(df_sin_asistencia[['Empleado', 'Fecha']], use_container_width=True)
        
        # 2. Detectar registros incompletos
        df_incompletos = detectar_registros_incompletos(df_con_asistencia)
        
        if not df_incompletos.empty:
            correcciones_aplicadas = mostrar_editor_registros_incompletos(df_incompletos)
            
            if correcciones_aplicadas:
                df_con_asistencia = aplicar_correcciones_a_dataframe(df_con_asistencia, df_incompletos)
                _limpiar_session_state_correcciones()
            else:
                st.warning("⚠️ Completa los datos faltantes y presiona 'Aplicar Correcciones' para continuar")
                st.stop()
        
        df = df_con_asistencia
        
        # 3. Detectar horarios ambiguos
        df_ambiguos = detectar_horarios_ambiguos(df)
        
        if not df_ambiguos.empty:
            st.markdown(f"""
            <div class="custom-alert alert-info">
                <strong>🤔 {len(df_ambiguos)} registro(s) con horarios sospechosos</strong><br>
                Se detectaron horarios que podrían estar mal asignados.
            </div>
            """, unsafe_allow_html=True)
            
            correcciones_ambiguos_aplicadas, _ = mostrar_editor_horarios_ambiguos(df_ambiguos)
            
            if correcciones_ambiguos_aplicadas:
                df = aplicar_correcciones_ambiguos_a_dataframe(df, df_ambiguos)
        
        # 4. Realizar cálculos
        calc_placeholder = st.empty()
        with calc_placeholder:
            mostrar_loading_calculos()
        
        resultados, total_horas, total_sueldos, total_horas_normales, total_horas_especiales = procesar_datos_excel(
            df, valor_por_hora, opcion_feriados, dias_feriados, cantidad_feriados
        )
        calc_placeholder.empty()
        
        # 5. Mostrar resultados
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
        st.info("Verifica que todos los módulos estén correctamente configurados.")

if __name__ == "__main__":
    run_payroll_app()