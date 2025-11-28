"""
Componentes de interfaz de usuario para BusinessSuite
Elementos reutilizables y widgets personalizados
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
import calendar
import os

def _safe_session_state_update(key, value):
    """
    Actualiza el session_state de forma segura para evitar conflictos del DOM
    """
    if key not in st.session_state or st.session_state[key] != value:
        st.session_state[key] = value

def mostrar_input_valor_hora():
    """
    Muestra el input para el valor por hora con estilo mejorado
    
    Returns:
        float: Valor por hora ingresado
    """
    st.markdown("### 💲 Valor por Hora")
    return st.number_input(
        "Ingrese el valor por hora:", 
        min_value=0.0, 
        value=13937.0,
        step=100.0,
        format="%.0f",
        help="Este valor se aplicará a todas las horas trabajadas por los empleados"
    )

def mostrar_descarga_plantilla():
    """
    Muestra el botón de descarga de la plantilla Excel con estilo personalizado
    """
    st.markdown("""
    <div class="custom-alert alert-info">
        <strong>📥 Descarga la plantilla de Excel</strong><br>
        Completa la plantilla con los datos de tus empleados y súbela para calcular automáticamente los sueldos.
    </div>
    """, unsafe_allow_html=True)
    
    # Obtener la ruta del archivo de plantilla
    plantilla_path = os.path.join(os.path.dirname(__file__), "plantilla_sueldos_feriados_dias.xlsx")
    
    # Verificar si el archivo existe
    if os.path.exists(plantilla_path):
        with open(plantilla_path, "rb") as f:
            st.download_button(
                "📥 Descargar Plantilla Excel", 
                f, 
                file_name="plantilla_sueldo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Descarga la plantilla oficial para cargar datos de empleados"
            )
    else:
        st.warning("⚠️ Archivo de plantilla no encontrado. Usa el formato estándar de Excel con las columnas: Empleado, Fecha, Entrada, Salida, Descuento Inventario, Descuento Caja, Retiro")

def configurar_feriados():
    """
    Muestra la configuración de feriados de forma simple
    
    Returns:
        tuple: (opcion_feriados, fechas_feriados, cantidad_feriados)
    """
    st.markdown("""
    <div class="custom-alert alert-info">
        <strong>📅 Selecciona hasta 3 fechas de feriados</strong><br>
        Los días feriados reciben doble pago automáticamente.
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar session state para feriados si no existe
    if 'feriados_list' not in st.session_state:
        st.session_state.feriados_list = []
    
    # Mostrar selector de fecha simple
    st.markdown("### Agregar Fecha de Feriado")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fecha_seleccionada = st.date_input(
            "Selecciona una fecha:",
            value=datetime.now(),
            min_value=datetime(2020, 1, 1),
            max_value=datetime(2030, 12, 31),
            help="Haz clic para abrir el calendario y seleccionar una fecha",
            key="date_picker_feriado"
        )
    
    with col2:
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        if st.button("➕ Agregar", use_container_width=True):
            if len(st.session_state.feriados_list) >= 3:
                st.error("❌ Máximo 3 fechas de feriados permitidas")
            elif fecha_seleccionada in st.session_state.feriados_list:
                st.warning("Esta fecha ya está agregada")
            else:
                st.session_state.feriados_list.append(fecha_seleccionada)
                st.success(f"Feriado agregado: {fecha_seleccionada.strftime('%d/%m/%Y')}")
    
    # Mostrar feriados seleccionados con opción de eliminar
    if st.session_state.feriados_list:
        st.markdown("### 📋 Feriados Seleccionados:")
        
        for idx, fecha in enumerate(sorted(st.session_state.feriados_list)):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                <div class="custom-alert alert-success" style="margin: 0.2rem 0; padding: 0.8rem;">
                    <strong>📅 {fecha.strftime('%d/%m/%Y - %A')}</strong>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("🗑️", key=f"delete_{idx}", help="Eliminar este feriado"):
                    st.session_state.feriados_list.remove(fecha)
                    st.rerun()
        
        # Botón para limpiar todos
        if st.button("🗑️ Limpiar Todos", help="Eliminar todas las fechas de feriados"):
            st.session_state.feriados_list = []
            st.rerun()
    
    # Convertir lista a set para compatibilidad con el resto del código
    fechas_feriados = set(st.session_state.feriados_list)
    opcion_feriados = "✅ Seleccionar fechas específicas"
    cantidad_feriados = len(fechas_feriados)
    
    return opcion_feriados, fechas_feriados, cantidad_feriados

def mostrar_subida_archivo():
    """
    Muestra el widget de subida de archivo Excel o PDF con estilo mejorado
    
    Returns:
        tuple: (archivo_subido, tipo_archivo) o (lista_archivos, tipo_archivo) para PDFs
    """
    st.markdown("### 📂 Selecciona el tipo de archivo")
    
    # Selector de tipo de archivo con botones mejorados
    col1, col2 = st.columns(2)
    
    with col1:
        excel_selected = st.button("📊 Archivo Excel", use_container_width=True, help="Datos estructurados tradicionales")
    
    with col2:
        pdf_selected = st.button("📄 Archivos PDF (Hasta 2)", use_container_width=True, help="Procesamiento inteligente automático - Períodos quincenales")
    
    # Mantener selección en session state
    if excel_selected:
        st.session_state.file_type = "excel"
    elif pdf_selected:
        st.session_state.file_type = "pdf"
    
    # Valor por defecto
    if "file_type" not in st.session_state:
        st.session_state.file_type = "excel"
    
    tipo_archivo = st.session_state.file_type
    
    if tipo_archivo == "excel":
        st.markdown("""
        <div class="custom-alert alert-info">
            <strong>📊 Modo Excel Tradicional</strong><br>
            Sube tu archivo Excel completado con todos los datos de empleados.
        </div>
        """, unsafe_allow_html=True)
        
        archivo = st.file_uploader(
            "Sube tu archivo Excel completado:",
            type=["xlsx"],
            help="Archivo Excel con columnas: Empleado, Fecha, Entrada, Salida, Descuento Inventario, Descuento Caja, Retiro",
            key="excel_uploader"
        )
        return archivo, "excel"
    
    else:  # PDF
        st.markdown("""
        <div class="custom-alert alert-warning">
            <strong>⚡ Modo Inteligente PDF Activado - Períodos Quincenales</strong><br>
            Sube hasta 2 PDFs (uno por cada quincena). El sistema los ordenará automáticamente por fecha.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="custom-alert alert-info">
            <strong>💡</strong> Añade por orden los PDFs (primera a segunda quincena). 
        </div>
        """, unsafe_allow_html=True)
        
        # Subida de archivos múltiples
        archivos = st.file_uploader(
            "Sube tus archivos PDF (máximo 2 quincenas):",
            type=["pdf"],
            accept_multiple_files=True,
            help="PDFs con información de empleados y horarios. Ejemplo: 1-15 octubre y 16-31 octubre",
            key="pdf_uploader"
        )
        
        # Validar que no se suban más de 2 archivos
        if archivos and len(archivos) > 2:
            st.error("❌ Máximo 2 archivos PDF permitidos (uno por cada quincena)")
            return None, "pdf"
        
        # Mostrar información de archivos subidos de forma compacta
        if archivos:
            # Crear lista compacta de archivos
            nombres_archivos = [f"PDF {idx}: {archivo.name}" for idx, archivo in enumerate(archivos, 1)]
            archivos_texto = " | ".join(nombres_archivos)
            
            st.markdown(f"""
            <div style="
                background-color: #d4edda; 
                border: 1px solid #c3e6cb; 
                border-radius: 6px; 
                padding: 8px 12px; 
                margin: 8px 0;
                font-size: 14px;
                color: #155724;
                display: flex;
                align-items: center;
                flex-wrap: wrap;
                gap: 8px;
            ">
                <span style="font-weight: 600;">📁 Cargados:</span>
                <span style="word-break: break-all;">{archivos_texto}</span>
            </div>
            """, unsafe_allow_html=True)
        
        return archivos, "pdf"

def mostrar_header_aplicacion(titulo: str, subtitulo: str = None, usuario: str = None):
    """
    Muestra el header principal de la aplicación
    
    Args:
        titulo (str): Título principal
        subtitulo (str): Subtítulo opcional
        usuario (str): Usuario actual
    """
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title(f"🏢 {titulo}")
        if subtitulo:
            st.markdown(f"*{subtitulo}*")
    
    with col2:
        if usuario:
            st.info(f"👤 **Usuario:** {usuario}")
    
    with col3:
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        hora_actual = datetime.now().strftime("%H:%M")
        st.info(f"📅 {fecha_actual}\n🕐 {hora_actual}")
    
    st.divider()

def mostrar_menu_lateral(opciones: List[str], iconos: List[str] = None) -> str:
    """
    Muestra un menú lateral con opciones
    
    Args:
        opciones (List[str]): Lista de opciones del menú
        iconos (List[str]): Lista de iconos para cada opción
    
    Returns:
        str: Opción seleccionada
    """
    st.sidebar.title("📋 Menú")
    
    if iconos and len(iconos) == len(opciones):
        opciones_con_iconos = [f"{icono} {opcion}" for icono, opcion in zip(iconos, opciones)]
    else:
        opciones_con_iconos = opciones
    
    seleccion = st.sidebar.radio("Seleccione una opción:", opciones_con_iconos)
    
    # Extraer la opción sin el icono
    if iconos:
        indice = opciones_con_iconos.index(seleccion)
        return opciones[indice]
    
    return seleccion

def crear_tarjeta_metrica(titulo: str, valor: Any, delta: Any = None, color: str = "blue"):
    """
    Crea una tarjeta de métrica personalizada
    
    Args:
        titulo (str): Título de la métrica
        valor (Any): Valor principal
        delta (Any): Cambio o diferencia
        color (str): Color de la tarjeta
    """
    color_map = {
        "blue": "#1f77b4",
        "green": "#2ca02c",
        "red": "#d62728",
        "orange": "#ff7f0e",
        "purple": "#9467bd"
    }
    
    color_hex = color_map.get(color, "#1f77b4")
    
    with st.container():
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, {color_hex}15 0%, {color_hex}05 100%);
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid {color_hex};
            margin: 0.5rem 0;
        ">
            <h4 style="margin: 0; color: {color_hex};">{titulo}</h4>
            <h2 style="margin: 0.5rem 0;">{valor}</h2>
            {f'<p style="margin: 0; color: #666;"><small>{delta}</small></p>' if delta else ''}
        </div>
        """, unsafe_allow_html=True)

def mostrar_dashboard_empleados(df_datos: pd.DataFrame):
    """
    Muestra un dashboard con información de empleados
    
    Args:
        df_datos (pd.DataFrame): DataFrame con datos de empleados
    """
    if df_datos.empty:
        st.warning("No hay datos de empleados para mostrar")
        return
    
    st.subheader("👥 Dashboard de Empleados")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_empleados = len(df_datos)
        crear_tarjeta_metrica("Total Empleados", total_empleados, color="blue")
    
    with col2:
        if 'Horas_Trabajadas' in df_datos.columns:
            promedio_horas = df_datos['Horas_Trabajadas'].mean()
            crear_tarjeta_metrica("Promedio Horas", f"{promedio_horas:.1f}", color="green")
    
    with col3:
        if 'Sueldo_Neto' in df_datos.columns:
            total_sueldos = df_datos['Sueldo_Neto'].sum()
            crear_tarjeta_metrica("Total Sueldos", f"Gs. {total_sueldos:,.0f}", color="orange")
    
    with col4:
        empleados_activos = len(df_datos[df_datos.get('Estado', 'Activo') == 'Activo'])
        crear_tarjeta_metrica("Empleados Activos", empleados_activos, color="purple")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Sueldo_Neto' in df_datos.columns and len(df_datos) > 1:
            st.subheader("💰 Distribución de Sueldos")
            fig = px.bar(df_datos.head(10), x='Empleado', y='Sueldo_Neto',
                        title="Top 10 Sueldos por Empleado")
            fig.update_xaxis(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'Horas_Trabajadas' in df_datos.columns and len(df_datos) > 1:
            st.subheader("⏰ Distribución de Horas")
            fig = px.histogram(df_datos, x='Horas_Trabajadas', nbins=20,
                             title="Distribución de Horas Trabajadas")
            st.plotly_chart(fig, use_container_width=True)

def crear_formulario_empleado(empleado_data: Dict = None) -> Dict:
    """
    Crea un formulario para agregar/editar empleado
    
    Args:
        empleado_data (Dict): Datos del empleado para edición
    
    Returns:
        Dict: Datos del formulario
    """
    st.subheader("👤 Información del Empleado")
    
    with st.form("formulario_empleado"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input(
                "Nombre Completo *",
                value=empleado_data.get('nombre', '') if empleado_data else '',
                placeholder="Ej: Juan Pérez"
            )
            
            cedula = st.text_input(
                "Cédula de Identidad",
                value=empleado_data.get('cedula', '') if empleado_data else '',
                placeholder="Ej: 1.234.567"
            )
            
            telefono = st.text_input(
                "Teléfono",
                value=empleado_data.get('telefono', '') if empleado_data else '',
                placeholder="Ej: 0981-123456"
            )
        
        with col2:
            cargo = st.selectbox(
                "Cargo",
                ["Cajero", "Vendedor", "Supervisor", "Gerente", "Administrativo", "Otro"],
                index=0 if not empleado_data else ["Cajero", "Vendedor", "Supervisor", "Gerente", "Administrativo", "Otro"].index(empleado_data.get('cargo', 'Cajero'))
            )
            
            salario_base = st.number_input(
                "Salario Base (Gs.)",
                min_value=0,
                value=int(empleado_data.get('salario_base', 0)) if empleado_data else 0,
                step=10000
            )
            
            fecha_ingreso = st.date_input(
                "Fecha de Ingreso",
                value=datetime.strptime(empleado_data.get('fecha_ingreso', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date() if empleado_data else datetime.now().date()
            )
        
        # Horario de trabajo
        st.subheader("⏰ Horario de Trabajo")
        col3, col4 = st.columns(2)
        
        with col3:
            hora_entrada = st.time_input(
                "Hora de Entrada",
                value=datetime.strptime(empleado_data.get('hora_entrada', '08:00'), '%H:%M').time() if empleado_data else datetime.strptime('08:00', '%H:%M').time()
            )
        
        with col4:
            hora_salida = st.time_input(
                "Hora de Salida",
                value=datetime.strptime(empleado_data.get('hora_salida', '17:00'), '%H:%M').time() if empleado_data else datetime.strptime('17:00', '%H:%M').time()
            )
        
        # Observaciones
        observaciones = st.text_area(
            "Observaciones",
            value=empleado_data.get('observaciones', '') if empleado_data else '',
            placeholder="Notas adicionales sobre el empleado..."
        )
        
        # Botones
        col5, col6, col7 = st.columns([1, 1, 1])
        
        with col5:
            submitted = st.form_submit_button("💾 Guardar", type="primary")
        
        with col6:
            if empleado_data:
                cancelar = st.form_submit_button("❌ Cancelar")
        
        with col7:
            limpiar = st.form_submit_button("🧹 Limpiar")
        
        if submitted:
            # Validaciones
            if not nombre.strip():
                st.error("❌ El nombre es obligatorio")
                return None
            
            empleado_dict = {
                'nombre': nombre.strip(),
                'cedula': cedula.strip(),
                'telefono': telefono.strip(),
                'cargo': cargo,
                'salario_base': salario_base,
                'fecha_ingreso': fecha_ingreso.strftime('%Y-%m-%d'),
                'hora_entrada': hora_entrada.strftime('%H:%M'),
                'hora_salida': hora_salida.strftime('%H:%M'),
                'observaciones': observaciones.strip(),
                'fecha_modificacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return empleado_dict
    
    return None

def mostrar_tabla_interactiva(df: pd.DataFrame, titulo: str = "Datos", acciones: bool = True):
    """
    Muestra una tabla interactiva con opciones de filtrado y búsqueda
    
    Args:
        df (pd.DataFrame): DataFrame a mostrar
        titulo (str): Título de la tabla
        acciones (bool): Si mostrar botones de acción
    """
    if df.empty:
        st.warning(f"⚠️ No hay {titulo.lower()} para mostrar")
        return
    
    st.subheader(f"📊 {titulo}")
    
    # Controles de filtrado
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        busqueda = st.text_input(
            "🔍 Buscar:",
            placeholder="Escriba para filtrar los datos..."
        )
    
    with col2:
        if acciones:
            exportar_csv = st.button("📥 Exportar CSV")
    
    with col3:
        if acciones:
            actualizar = st.button("🔄 Actualizar")
    
    # Filtrar datos si hay búsqueda
    df_filtrado = df.copy()
    if busqueda:
        # Buscar en todas las columnas de texto
        mask = df_filtrado.astype(str).apply(
            lambda x: x.str.contains(busqueda, case=False, na=False)
        ).any(axis=1)
        df_filtrado = df_filtrado[mask]
    
    # Mostrar información de la tabla
    col4, col5 = st.columns(2)
    with col4:
        st.info(f"📈 Mostrando {len(df_filtrado)} de {len(df)} registros")
    
    # Mostrar tabla
    st.dataframe(df_filtrado, use_container_width=True, height=400)
    
    # Manejar exportación
    if acciones and exportar_csv:
        csv_data = df_filtrado.to_csv(index=False)
        st.download_button(
            label="📥 Descargar CSV Filtrado",
            data=csv_data,
            file_name=f"{titulo.lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

def crear_selector_periodo():
    """
    Crea un selector de período temporal
    
    Returns:
        tuple: (fecha_inicio, fecha_fin)
    """
    st.subheader("📅 Seleccionar Período")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        periodo_tipo = st.selectbox(
            "Tipo de Período",
            ["Personalizado", "Última Semana", "Último Mes", "Últimos 3 Meses", "Año Actual"]
        )
    
    if periodo_tipo == "Personalizado":
        with col2:
            fecha_inicio = st.date_input(
                "Fecha Inicio",
                value=datetime.now().date() - timedelta(days=30)
            )
        
        with col3:
            fecha_fin = st.date_input(
                "Fecha Fin",
                value=datetime.now().date()
            )
    
    elif periodo_tipo == "Última Semana":
        fecha_fin = datetime.now().date()
        fecha_inicio = fecha_fin - timedelta(days=7)
        
        with col2:
            st.info(f"📅 Desde: {fecha_inicio}")
        
        with col3:
            st.info(f"📅 Hasta: {fecha_fin}")
    
    elif periodo_tipo == "Último Mes":
        fecha_fin = datetime.now().date()
        fecha_inicio = fecha_fin - timedelta(days=30)
        
        with col2:
            st.info(f"📅 Desde: {fecha_inicio}")
        
        with col3:
            st.info(f"📅 Hasta: {fecha_fin}")
    
    elif periodo_tipo == "Últimos 3 Meses":
        fecha_fin = datetime.now().date()
        fecha_inicio = fecha_fin - timedelta(days=90)
        
        with col2:
            st.info(f"📅 Desde: {fecha_inicio}")
        
        with col3:
            st.info(f"📅 Hasta: {fecha_fin}")
    
    elif periodo_tipo == "Año Actual":
        fecha_inicio = datetime(datetime.now().year, 1, 1).date()
        fecha_fin = datetime.now().date()
        
        with col2:
            st.info(f"📅 Desde: {fecha_inicio}")
        
        with col3:
            st.info(f"📅 Hasta: {fecha_fin}")
    
    return fecha_inicio, fecha_fin

def mostrar_progreso_personalizado(porcentaje: float, titulo: str = "Progreso", color: str = "blue"):
    """
    Muestra una barra de progreso personalizada
    
    Args:
        porcentaje (float): Porcentaje completado (0-100)
        titulo (str): Título del progreso
        color (str): Color de la barra
    """
    color_map = {
        "blue": "#1f77b4",
        "green": "#2ca02c",
        "red": "#d62728",
        "orange": "#ff7f0e",
        "purple": "#9467bd"
    }
    
    color_hex = color_map.get(color, "#1f77b4")
    porcentaje_normalizado = min(max(porcentaje, 0), 100)
    
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <h4 style="margin-bottom: 0.5rem;">{titulo}</h4>
        <div style="
            background-color: #f0f0f0;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
        ">
            <div style="
                background-color: {color_hex};
                height: 100%;
                width: {porcentaje_normalizado}%;
                border-radius: 10px;
                transition: width 0.3s ease;
            "></div>
        </div>
        <p style="margin-top: 0.5rem; color: #666;">
            {porcentaje_normalizado:.1f}% completado
        </p>
    </div>
    """, unsafe_allow_html=True)

def crear_alertas_sistema(alertas: List[Dict]):
    """
    Muestra alertas del sistema
    
    Args:
        alertas (List[Dict]): Lista de alertas con tipo, título y mensaje
    """
    if not alertas:
        return
    
    st.subheader("🚨 Alertas del Sistema")
    
    for alerta in alertas:
        tipo = alerta.get('tipo', 'info')
        titulo = alerta.get('titulo', 'Alerta')
        mensaje = alerta.get('mensaje', '')
        
        if tipo == 'error':
            st.error(f"❌ **{titulo}**: {mensaje}")
        elif tipo == 'warning':
            st.warning(f"⚠️ **{titulo}**: {mensaje}")
        elif tipo == 'success':
            st.success(f"✅ **{titulo}**: {mensaje}")
        else:
            st.info(f"ℹ️ **{titulo}**: {mensaje}")

def validar_numero(valor_str: str, nombre_campo: str = "campo") -> tuple:
    """
    Valida y convierte un string a número
    
    Args:
        valor_str (str): Valor a validar
        nombre_campo (str): Nombre del campo para mensajes de error
    
    Returns:
        tuple: (es_valido, valor_numerico_o_error)
    """
    if not valor_str or not valor_str.strip():
        return False, f"{nombre_campo} no puede estar vacío"
    
    try:
        # Limpiar el string
        valor_limpio = valor_str.strip().replace(',', '').replace('.', '')
        
        # Intentar convertir a float
        valor_numerico = float(valor_limpio)
        
        if valor_numerico < 0:
            return False, f"{nombre_campo} no puede ser negativo"
        
        return True, valor_numerico
    
    except ValueError:
        return False, f"{nombre_campo} debe ser un número válido"

def formatear_moneda(valor: float, simbolo: str = "Gs.") -> str:
    """
    Formatea un valor como moneda
    
    Args:
        valor (float): Valor a formatear
        simbolo (str): Símbolo de la moneda
    
    Returns:
        str: Valor formateado
    """
    return f"{simbolo} {valor:,.0f}"

def formatear_horas(horas: float) -> str:
    """
    Formatea horas como texto legible
    
    Args:
        horas (float): Horas a formatear
    
    Returns:
        str: Horas formateadas
    """
    horas_enteras = int(horas)
    minutos = int((horas - horas_enteras) * 60)
    
    if minutos == 0:
        return f"{horas_enteras}h"
    else:
        return f"{horas_enteras}h {minutos}m"

def aplicar_correcciones_a_dataframe(df: pd.DataFrame, df_correcciones: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica correcciones al dataframe principal desde el dataframe de correcciones
    
    Args:
        df (pd.DataFrame): DataFrame principal
        df_correcciones (pd.DataFrame): DataFrame con las correcciones aplicadas
    
    Returns:
        pd.DataFrame: DataFrame con correcciones aplicadas
    """
    try:
        # Crear una copia para no modificar el original
        df_resultado = df.copy()
        
        # Iterar sobre las correcciones
        for idx, row in df_correcciones.iterrows():
            # Buscar el registro correspondiente en el dataframe principal
            mascara = (
                (df_resultado['Empleado'] == row['Empleado']) & 
                (df_resultado['Fecha'] == row['Fecha'])
            )
            
            # Aplicar correcciones
            if mascara.any():
                if 'Entrada' in row and pd.notna(row['Entrada']):
                    df_resultado.loc[mascara, 'Entrada'] = row['Entrada']
                if 'Salida' in row and pd.notna(row['Salida']):
                    df_resultado.loc[mascara, 'Salida'] = row['Salida']
        
        return df_resultado
        
    except Exception as e:
        st.error(f"Error aplicando correcciones: {str(e)}")
        return df

def aplicar_correcciones_ambiguos_a_dataframe(df: pd.DataFrame, df_ambiguos: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica correcciones de horarios ambiguos al dataframe principal
    
    Args:
        df (pd.DataFrame): DataFrame principal
        df_ambiguos (pd.DataFrame): DataFrame con horarios ambiguos corregidos
    
    Returns:
        pd.DataFrame: DataFrame con correcciones aplicadas
    """
    try:
        # Crear una copia para no modificar el original
        df_resultado = df.copy()
        
        # Iterar sobre los registros ambiguos corregidos
        for idx, row in df_ambiguos.iterrows():
            # Buscar el registro correspondiente
            mascara = (
                (df_resultado['Empleado'] == row['Empleado']) & 
                (df_resultado['Fecha'] == row['Fecha'])
            )
            
            # Aplicar correcciones de entrada y salida
            if mascara.any():
                if 'Entrada' in row and pd.notna(row['Entrada']):
                    df_resultado.loc[mascara, 'Entrada'] = row['Entrada']
                if 'Salida' in row and pd.notna(row['Salida']):
                    df_resultado.loc[mascara, 'Salida'] = row['Salida']
                
                # Si hay columnas de turno o decisión, también aplicarlas
                if 'Turno' in row and pd.notna(row['Turno']):
                    df_resultado.loc[mascara, 'Turno'] = row['Turno']
        
        return df_resultado
        
    except Exception as e:
        st.error(f"Error aplicando correcciones de horarios ambiguos: {str(e)}")
        return df

def mostrar_editor_registros_incompletos(df_incompletos: pd.DataFrame) -> bool:
    """
    Muestra un editor mejorado para corregir registros incompletos con marcación única
    Permite al administrador decidir si la marcación fue entrada o salida
    
    Args:
        df_incompletos (pd.DataFrame): DataFrame con registros incompletos
    
    Returns:
        bool: True si se aplicaron correcciones, False si no
    """
    if df_incompletos.empty:
        return True
    
    st.markdown(f"""
    <div class="custom-alert alert-warning">
        <strong>⚠️ {len(df_incompletos)} registro(s) incompleto(s) detectado(s)</strong><br>
        El empleado marcó solamente una vez. Determine si fue entrada o salida e ingrese el horario faltante.
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar session_state para decisiones si no existe
    if 'decisiones_admin' not in st.session_state:
        st.session_state.decisiones_admin = {}
    
    # Mostrar editor mejorado para cada registro
    st.markdown("### 👨‍💼 Panel Administrativo - Completar Horarios")
    
    for idx, row in df_incompletos.iterrows():
        entrada_actual = row.get('Entrada', '')
        salida_actual = row.get('Salida', '')
        
        # Determinar qué campo tiene valor
        hora_registrada = entrada_actual if (pd.notna(entrada_actual) and entrada_actual != '') else salida_actual
        
        with st.expander(f"� {row['Empleado']} - 📅 {row['Fecha']} - 🕐 {hora_registrada}", expanded=True):
            # Panel de información
            tiene_entrada = pd.notna(entrada_actual) and entrada_actual != ''
            st.markdown(f"""
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #ffc107;">
                <strong>📊 Situación:</strong> Solo marcó {'entrada' if tiene_entrada else 'salida'}<br>
                <strong>🕐 Horario registrado:</strong> {hora_registrada}<br>
                <strong>💡 Decisión:</strong> El administrador decide si fue entrada o salida
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ❓ ¿Qué tipo de marca fue?")
                tipo_marca = st.selectbox(
                    f"El horario {hora_registrada} fue:",
                    ["Entrada", "Salida"],
                    key=f"tipo_{idx}",
                    help="Seleccione si el horario registrado corresponde a entrada o salida"
                )
                
                # Guardar decisión en session_state
                st.session_state.decisiones_admin[idx] = tipo_marca
            
            with col2:
                st.markdown("#### ✏️ Completar horario faltante")
                if tipo_marca == "Entrada":
                    # La marca fue entrada, pedir salida
                    st.markdown(f"<div style='background-color: #d4edda; padding: 8px; border-radius: 4px; margin-bottom: 8px;'>✅ <strong>Entrada:</strong> {hora_registrada}</div>", unsafe_allow_html=True)
                    
                    hora_faltante = st.time_input(
                        "Ingresa la hora de salida:",
                        key=f"completar_{idx}",
                        help="Ingrese la hora de salida que faltó registrar"
                    )
                    
                    if hora_faltante:
                        df_incompletos.at[idx, 'Entrada'] = hora_registrada
                        df_incompletos.at[idx, 'Salida'] = hora_faltante.strftime("%H:%M")
                        st.markdown(f"<div style='background-color: #f8d7da; padding: 8px; border-radius: 4px;'>❌ <strong>Salida:</strong> Faltante → {hora_faltante.strftime('%H:%M')}</div>", unsafe_allow_html=True)
                else:
                    # La marca fue salida, pedir entrada
                    hora_faltante = st.time_input(
                        "Ingresa la hora de entrada:",
                        key=f"completar_{idx}",
                        help="Ingrese la hora de entrada que faltó registrar"
                    )
                    
                    st.markdown(f"<div style='background-color: #f8d7da; padding: 8px; border-radius: 4px; margin-top: 8px;'>❌ <strong>Salida:</strong> Faltante</div>", unsafe_allow_html=True)
                    
                    if hora_faltante:
                        df_incompletos.at[idx, 'Entrada'] = hora_faltante.strftime("%H:%M")
                        df_incompletos.at[idx, 'Salida'] = hora_registrada
            
            # Botón de confirmación individual
            if st.button(f"✅ Confirmar Registro {idx + 1}", key=f"confirmar_{idx}", use_container_width=True):
                st.success(f"Registro de {row['Empleado']} confirmado correctamente")
    
    st.markdown("---")
    
    # Botón para aplicar todas las correcciones
    if st.button("✅ Aplicar Todas las Correcciones", use_container_width=True, type="primary"):
        # Verificar que todos los campos estén completos
        campos_vacios = df_incompletos[
            (df_incompletos['Entrada'].isna()) | 
            (df_incompletos['Salida'].isna()) |
            (df_incompletos['Entrada'] == '') |
            (df_incompletos['Salida'] == '')
        ]
        
        if not campos_vacios.empty:
            st.error("⚠️ Todos los horarios deben ser completados antes de continuar")
            return False
        else:
            return True
    
    return False

def mostrar_editor_horarios_ambiguos(df_ambiguos: pd.DataFrame) -> tuple:
    """
    Muestra un editor para resolver horarios ambiguos
    
    Args:
        df_ambiguos (pd.DataFrame): DataFrame con horarios ambiguos
    
    Returns:
        tuple: (bool correcciones_aplicadas, pd.DataFrame df_corregido)
    """
    if df_ambiguos.empty:
        return True, df_ambiguos
    
    st.markdown("### 🤔 Resolver Horarios Ambiguos")
    st.info("Algunos horarios detectados podrían estar invertidos (Entrada/Salida). Revisa y corrige si es necesario.")
    
    # Crear columnas para editar
    for idx, row in df_ambiguos.iterrows():
        with st.expander(f"📝 {row['Empleado']} - {row['Fecha']}", expanded=False):
            st.markdown(f"**Horarios detectados:** Entrada: {row.get('Entrada', 'N/A')} - Salida: {row.get('Salida', 'N/A')}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                entrada = st.text_input(
                    "Hora de Entrada Correcta (HH:MM)",
                    value=str(row.get('Entrada', '')),
                    key=f"entrada_amb_{idx}"
                )
                df_ambiguos.at[idx, 'Entrada'] = entrada
            
            with col2:
                salida = st.text_input(
                    "Hora de Salida Correcta (HH:MM)",
                    value=str(row.get('Salida', '')),
                    key=f"salida_amb_{idx}"
                )
                df_ambiguos.at[idx, 'Salida'] = salida
    
    # Botón para aplicar correcciones
    if st.button("✅ Confirmar Correcciones de Horarios", use_container_width=True, type="primary"):
        return True, df_ambiguos
    
    return False, df_ambiguos