"""
Módulo de componentes de Loading
Proporciona componentes visuales de carga para mejorar la experiencia del usuario
"""
import streamlit as st
import time
import threading
from contextlib import contextmanager
from typing import Callable, Any

def mostrar_loading_simple(texto="Procesando..."):
    """
    Muestra un indicador de carga simple con texto
    
    Args:
        texto: Texto a mostrar durante la carga
    """
    st.markdown(f"""
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <div class="loading-text">{texto}</div>
        <div class="loading-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def mostrar_loading_procesamiento(texto="Procesando datos", subtexto="Por favor espera..."):
    """
    Muestra un indicador de carga para procesamiento de datos
    
    Args:
        texto: Texto principal
        subtexto: Texto secundario explicativo
    """
    st.markdown(f"""
    <div class="processing-loader">
        <div class="icon">🔄</div>
        <div class="loading-text">{texto}</div>
        <div class="loading-subtext">{subtexto}</div>
        <div class="progress-bar-container">
            <div class="progress-bar"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def mostrar_loading_validacion(texto="Validando datos..."):
    """
    Muestra un indicador de carga para validación
    
    Args:
        texto: Texto a mostrar durante la validación
    """
    st.markdown(f"""
    <div class="validation-loader">
        <div class="loading-text">⚠️ {texto}</div>
        <div class="loading-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def mostrar_loading_pdf(cantidad_archivos=1):
    """
    Muestra un indicador de carga específico para procesamiento de PDFs
    
    Args:
        cantidad_archivos: Número de PDFs siendo procesados
    """
    texto = f"Procesando {cantidad_archivos} PDF{'s' if cantidad_archivos > 1 else ''}"
    subtexto = "Extrayendo datos de asistencia automáticamente..."
    
    st.markdown(f"""
    <div class="processing-loader">
        <div class="loading-text">📄 {texto}</div>
        <div class="loading-subtext">{subtexto}</div>
        <div class="progress-bar-container">
            <div class="progress-bar"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def mostrar_loading_excel():
    """
    Muestra un indicador de carga específico para procesamiento de Excel
    """
    st.markdown("""
    <div class="processing-loader">
        <div class="loading-text">📊 Procesando archivo Excel</div>
        <div class="loading-subtext">Leyendo y validando datos...</div>
        <div class="progress-bar-container">
            <div class="progress-bar"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def mostrar_loading_calculos():
    """
    Muestra un indicador de carga para el cálculo de sueldos
    """
    st.markdown("""
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <div class="loading-text">💰 Calculando sueldos</div>
        <div class="loading-subtext">Procesando horas, feriados y descuentos...</div>
        <div class="progress-bar-container">
            <div class="progress-bar"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

@contextmanager
def loading_context(tipo="simple", texto="Procesando..."):
    """
    Context manager para mostrar loading durante operaciones
    
    Uso:
        with loading_context("procesamiento", "Calculando datos"):
            # Tu código aquí
            resultado = procesar_datos()
    
    Args:
        tipo: Tipo de loading ("simple", "procesamiento", "validacion", "calculos")
        texto: Texto a mostrar
    """
    # Crear un placeholder para el loading
    placeholder = st.empty()
    
    with placeholder.container():
        if tipo == "simple":
            mostrar_loading_simple(texto)
        elif tipo == "procesamiento":
            mostrar_loading_procesamiento(texto)
        elif tipo == "validacion":
            mostrar_loading_validacion(texto)
        elif tipo == "calculos":
            mostrar_loading_calculos()
        elif tipo == "pdf":
            mostrar_loading_pdf()
        elif tipo == "excel":
            mostrar_loading_excel()
    
    try:
        yield placeholder
    finally:
        # Limpiar el loading cuando termine la operación
        placeholder.empty()

def mostrar_skeleton_tabla(num_filas=5):
    """
    Muestra un skeleton loader para una tabla mientras se carga
    
    Args:
        num_filas: Número de filas del skeleton
    """
    html_skeleton = "<div style='padding: 1rem;'>"
    for _ in range(num_filas):
        html_skeleton += """
        <div class="skeleton-loader" style="height: 30px; margin: 0.5rem 0;"></div>
        """
    html_skeleton += "</div>"
    
    st.markdown(html_skeleton, unsafe_allow_html=True)

def mostrar_progreso_con_porcentaje(porcentaje, texto="Procesando"):
    """
    Muestra una barra de progreso con porcentaje
    
    Args:
        porcentaje: Valor de 0 a 100
        texto: Texto a mostrar
    """
    st.markdown(get_progress_html(porcentaje, texto), unsafe_allow_html=True)

def get_progress_html(porcentaje, texto="Procesando"):
    """
    Genera el HTML de la barra de progreso para poder renderizarlo desde placeholders.

    Args:
        porcentaje: Valor de 0 a 100
        texto: Texto a mostrar

    Returns:
        str: HTML como cadena
    """
    # Asegurar rango válido
    try:
        porcentaje_int = max(0, min(100, int(porcentaje)))
    except Exception:
        porcentaje_int = 0

    return f"""
    <div class="loading-container">
        <div class="loading-text">{texto}</div>
        <div style="width: 100%; background: #E3F2FD; border-radius: 10px; height: 30px; position: relative; margin-top: 1rem;">
            <div style="width: {porcentaje_int}%; background: linear-gradient(90deg, #4FC3F7, #81D4FA); height: 100%; border-radius: 10px; transition: width 0.3s ease;"></div>
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-weight: 600; color: #000;">
                {porcentaje_int}%
            </div>
        </div>
    </div>
    """

class LoadingManager:
    """
    Gestor de estados de carga para la aplicación
    """
    
    def __init__(self):
        self.loading_states = {}
        self.progress_bars = {}
        self.status_texts = {}
    
    def show_loading(self, key: str, message: str = "Cargando...", show_progress: bool = False):
        """
        Muestra un indicador de carga
        
        Args:
            key (str): Clave única para el indicador
            message (str): Mensaje a mostrar
            show_progress (bool): Si mostrar barra de progreso
        """
        if key not in self.loading_states:
            self.loading_states[key] = True
            
            with st.container():
                if show_progress:
                    self.progress_bars[key] = st.progress(0)
                
                self.status_texts[key] = st.empty()
                self.status_texts[key].info(f"⏳ {message}")
    
    def update_progress(self, key: str, progress: float, message: str = None):
        """
        Actualiza el progreso de una operación
        
        Args:
            key (str): Clave del indicador
            progress (float): Progreso (0.0 a 1.0)
            message (str): Nuevo mensaje opcional
        """
        if key in self.progress_bars:
            self.progress_bars[key].progress(progress)
        
        if message and key in self.status_texts:
            self.status_texts[key].info(f"⏳ {message}")
    
    def hide_loading(self, key: str, success_message: str = None, error_message: str = None):
        """
        Oculta un indicador de carga
        
        Args:
            key (str): Clave del indicador
            success_message (str): Mensaje de éxito opcional
            error_message (str): Mensaje de error opcional
        """
        if key in self.loading_states:
            if key in self.progress_bars:
                self.progress_bars[key].empty()
                del self.progress_bars[key]
            
            if key in self.status_texts:
                if success_message:
                    self.status_texts[key].success(f"✅ {success_message}")
                elif error_message:
                    self.status_texts[key].error(f"❌ {error_message}")
                else:
                    self.status_texts[key].empty()
                
                # Limpiar después de un momento
                time.sleep(2)
                self.status_texts[key].empty()
                del self.status_texts[key]
            
            del self.loading_states[key]

# Instancia global del gestor de carga
loading_manager = LoadingManager()

def mostrar_spinner_personalizado(mensaje: str = "Por favor espere...", duracion: float = None):
    """
    Muestra un spinner personalizado
    
    Args:
        mensaje (str): Mensaje a mostrar
        duracion (float): Duración en segundos (None para manual)
    """
    spinner_placeholder = st.empty()
    
    with spinner_placeholder:
        with st.spinner(mensaje):
            if duracion:
                time.sleep(duracion)
    
    return spinner_placeholder

def ejecutar_con_progreso(
    funcion: Callable,
    args: tuple = (),
    kwargs: dict = None,
    mensaje_inicial: str = "Procesando...",
    mensaje_exito: str = "Completado exitosamente",
    mostrar_tiempo: bool = True
):
    """
    Ejecuta una función mostrando progreso
    
    Args:
        funcion (Callable): Función a ejecutar
        args (tuple): Argumentos posicionales
        kwargs (dict): Argumentos con nombre
        mensaje_inicial (str): Mensaje inicial
        mensaje_exito (str): Mensaje de éxito
        mostrar_tiempo (bool): Si mostrar tiempo transcurrido
    
    Returns:
        Any: Resultado de la función
    """
    if kwargs is None:
        kwargs = {}
    
    inicio = time.time()
    
    # Crear contenedores para progreso
    progress_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        tiempo_text = st.empty() if mostrar_tiempo else None
        
        status_text.info(f"⏳ {mensaje_inicial}")
        
        # Simular progreso mientras la función se ejecuta
        progress_value = 0
        
        def actualizar_progreso():
            nonlocal progress_value
            while progress_value < 0.9:
                progress_value += 0.1
                progress_bar.progress(progress_value)
                
                if mostrar_tiempo and tiempo_text:
                    tiempo_transcurrido = time.time() - inicio
                    tiempo_text.text(f"⏱️ Tiempo: {tiempo_transcurrido:.1f}s")
                
                time.sleep(0.5)
        
        # Ejecutar actualización de progreso en hilo separado
        progress_thread = threading.Thread(target=actualizar_progreso)
        progress_thread.daemon = True
        progress_thread.start()
        
        try:
            # Ejecutar la función principal
            resultado = funcion(*args, **kwargs)
            
            # Completar progreso
            progress_bar.progress(1.0)
            tiempo_final = time.time() - inicio
            
            status_text.success(f"✅ {mensaje_exito}")
            
            if mostrar_tiempo and tiempo_text:
                tiempo_text.success(f"⏱️ Completado en {tiempo_final:.1f}s")
            
            # Limpiar después de un momento
            time.sleep(2)
            progress_container.empty()
            
            return resultado
            
        except Exception as e:
            progress_bar.progress(1.0)
            status_text.error(f"❌ Error: {str(e)}")
            
            if mostrar_tiempo and tiempo_text:
                tiempo_text.error(f"⏱️ Falló después de {time.time() - inicio:.1f}s")
            
            raise e

def mostrar_carga_archivo(mensaje: str = "Procesando archivo..."):
    """
    Muestra indicador de carga específico para archivos
    
    Args:
        mensaje (str): Mensaje a mostrar
    
    Returns:
        tuple: (progress_bar, status_text) para control manual
    """
    st.info("📁 Iniciando procesamiento de archivo...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.info(f"⏳ {mensaje}")
    
    return progress_bar, status_text

def finalizar_carga_archivo(progress_bar, status_text, exito: bool = True, mensaje: str = None):
    """
    Finaliza la carga de archivo
    
    Args:
        progress_bar: Barra de progreso
        status_text: Texto de estado
        exito (bool): Si fue exitoso
        mensaje (str): Mensaje personalizado
    """
    progress_bar.progress(1.0)
    
    if exito:
        mensaje_final = mensaje or "Archivo procesado exitosamente"
        status_text.success(f"✅ {mensaje_final}")
    else:
        mensaje_final = mensaje or "Error procesando archivo"
        status_text.error(f"❌ {mensaje_final}")
    
    # Limpiar después de un momento
    time.sleep(2)
    progress_bar.empty()
    status_text.empty()

def crear_indicador_estado_sistema():
    """
    Crea indicadores de estado del sistema
    
    Returns:
        dict: Diccionario con componentes de estado
    """
    st.subheader("🔍 Estado del Sistema")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Estado de la base de datos
    with col1:
        estado_bd = st.empty()
        estado_bd.success("🗄️ BD: Conectada")
    
    # Estado de la red
    with col2:
        estado_red = st.empty()
        estado_red.success("🌐 Red: Online")
    
    # Estado de memoria
    with col3:
        estado_memoria = st.empty()
        estado_memoria.info("💾 Memoria: 45%")
    
    # Estado general
    with col4:
        estado_general = st.empty()
        estado_general.success("✅ Sistema: OK")
    
    return {
        'base_datos': estado_bd,
        'red': estado_red,
        'memoria': estado_memoria,
        'general': estado_general
    }

def actualizar_estado_sistema(estados: dict, estado_bd: str = "OK", estado_red: str = "OK", 
                            uso_memoria: int = 45, estado_general: str = "OK"):
    """
    Actualiza los indicadores de estado del sistema
    
    Args:
        estados (dict): Diccionario de componentes de estado
        estado_bd (str): Estado de la base de datos
        estado_red (str): Estado de la red
        uso_memoria (int): Porcentaje de uso de memoria
        estado_general (str): Estado general del sistema
    """
    # Actualizar base de datos
    if estado_bd == "OK":
        estados['base_datos'].success("🗄️ BD: Conectada")
    else:
        estados['base_datos'].error(f"🗄️ BD: {estado_bd}")
    
    # Actualizar red
    if estado_red == "OK":
        estados['red'].success("🌐 Red: Online")
    else:
        estados['red'].error(f"🌐 Red: {estado_red}")
    
    # Actualizar memoria
    if uso_memoria < 70:
        estados['memoria'].info(f"💾 Memoria: {uso_memoria}%")
    elif uso_memoria < 90:
        estados['memoria'].warning(f"💾 Memoria: {uso_memoria}%")
    else:
        estados['memoria'].error(f"💾 Memoria: {uso_memoria}%")
    
    # Actualizar estado general
    if estado_general == "OK":
        estados['general'].success("✅ Sistema: OK")
    else:
        estados['general'].error(f"❌ Sistema: {estado_general}")

class ProgressTracker:
    """
    Rastreador de progreso para operaciones largas
    """
    
    def __init__(self, total_pasos: int, titulo: str = "Progreso"):
        self.total_pasos = total_pasos
        self.paso_actual = 0
        self.titulo = titulo
        self.inicio = time.time()
        
        # Crear elementos de UI
        self.container = st.container()
        with self.container:
            st.subheader(f"📊 {titulo}")
            self.progress_bar = st.progress(0)
            self.info_text = st.empty()
            self.tiempo_text = st.empty()
    
    def siguiente_paso(self, descripcion: str = ""):
        """
        Avanza al siguiente paso
        
        Args:
            descripcion (str): Descripción del paso actual
        """
        self.paso_actual += 1
        progreso = self.paso_actual / self.total_pasos
        
        self.progress_bar.progress(progreso)
        
        tiempo_transcurrido = time.time() - self.inicio
        tiempo_estimado = tiempo_transcurrido / progreso if progreso > 0 else 0
        tiempo_restante = tiempo_estimado - tiempo_transcurrido if tiempo_estimado > tiempo_transcurrido else 0
        
        info_msg = f"Paso {self.paso_actual}/{self.total_pasos}"
        if descripcion:
            info_msg += f": {descripcion}"
        
        self.info_text.info(info_msg)
        
        tiempo_msg = f"⏱️ Transcurrido: {tiempo_transcurrido:.1f}s"
        if tiempo_restante > 0:
            tiempo_msg += f" | Restante: {tiempo_restante:.1f}s"
        
        self.tiempo_text.text(tiempo_msg)
    
    def completar(self, mensaje_final: str = "Proceso completado"):
        """
        Completa el progreso
        
        Args:
            mensaje_final (str): Mensaje final a mostrar
        """
        self.progress_bar.progress(1.0)
        tiempo_total = time.time() - self.inicio
        
        self.info_text.success(f"✅ {mensaje_final}")
        self.tiempo_text.success(f"⏱️ Completado en {tiempo_total:.1f}s")
        
        # Limpiar después de un momento
        time.sleep(3)
        self.container.empty()
    
    def error(self, mensaje_error: str):
        """
        Marca el progreso como error
        
        Args:
            mensaje_error (str): Mensaje de error
        """
        tiempo_total = time.time() - self.inicio
        
        self.info_text.error(f"❌ {mensaje_error}")
        self.tiempo_text.error(f"⏱️ Falló después de {tiempo_total:.1f}s")

def mostrar_carga_minimalista(mensaje: str = "Cargando...", color: str = "blue"):
    """
    Muestra un indicador de carga minimalista
    
    Args:
        mensaje (str): Mensaje a mostrar
        color (str): Color del indicador
    
    Returns:
        placeholder para control
    """
    color_map = {
        "blue": "#1f77b4",
        "green": "#2ca02c",
        "red": "#d62728",
        "orange": "#ff7f0e"
    }
    
    color_hex = color_map.get(color, "#1f77b4")
    
    placeholder = st.empty()
    
    with placeholder:
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            background: {color_hex}10;
            border-radius: 0.5rem;
            border-left: 4px solid {color_hex};
        ">
            <div style="
                width: 20px;
                height: 20px;
                border: 3px solid {color_hex}30;
                border-top: 3px solid {color_hex};
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 1rem;
            "></div>
            <span style="color: {color_hex}; font-weight: 500;">{mensaje}</span>
        </div>
        <style>
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
        """, unsafe_allow_html=True)
    
    return placeholder

def ocultar_carga_minimalista(placeholder, mensaje_final: str = None, tipo: str = "success"):
    """
    Oculta el indicador de carga minimalista
    
    Args:
        placeholder: Placeholder del indicador
        mensaje_final (str): Mensaje final opcional
        tipo (str): Tipo de mensaje (success, error, info)
    """
    if mensaje_final:
        if tipo == "success":
            placeholder.success(f"✅ {mensaje_final}")
        elif tipo == "error":
            placeholder.error(f"❌ {mensaje_final}")
        else:
            placeholder.info(f"ℹ️ {mensaje_final}")
        
        time.sleep(2)
    
    placeholder.empty()

def crear_temporizador_automatico(duracion_segundos: int, mensaje: str = "Operación en progreso"):
    """
    Crea un temporizador automático con cuenta regresiva
    
    Args:
        duracion_segundos (int): Duración en segundos
        mensaje (str): Mensaje a mostrar
    """
    container = st.container()
    
    with container:
        st.subheader("⏰ Temporizador")
        progress_bar = st.progress(0)
        tiempo_text = st.empty()
        mensaje_text = st.empty()
        
        mensaje_text.info(f"📋 {mensaje}")
        
        for segundo in range(duracion_segundos + 1):
            progreso = segundo / duracion_segundos
            tiempo_restante = duracion_segundos - segundo
            
            progress_bar.progress(progreso)
            tiempo_text.text(f"⏱️ Tiempo restante: {tiempo_restante}s")
            
            if segundo < duracion_segundos:
                time.sleep(1)
        
        mensaje_text.success("✅ Temporizador completado")
        time.sleep(1)
        container.empty()

def validar_operacion_asincrona(funcion_validacion: Callable, intervalo: float = 1.0, 
                               timeout: float = 30.0, mensaje: str = "Validando..."):
    """
    Valida una operación de forma asíncrona
    
    Args:
        funcion_validacion (Callable): Función que retorna True cuando la validación es exitosa
        intervalo (float): Intervalo entre validaciones
        timeout (float): Tiempo máximo de espera
        mensaje (str): Mensaje a mostrar
    
    Returns:
        bool: True si la validación fue exitosa
    """
    inicio = time.time()
    
    container = st.container()
    
    with container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.info(f"⏳ {mensaje}")
        
        while time.time() - inicio < timeout:
            tiempo_transcurrido = time.time() - inicio
            progreso = tiempo_transcurrido / timeout
            
            progress_bar.progress(progreso)
            
            # Ejecutar validación
            try:
                if funcion_validacion():
                    progress_bar.progress(1.0)
                    status_text.success("✅ Validación exitosa")
                    time.sleep(1)
                    container.empty()
                    return True
            except:
                pass
            
            time.sleep(intervalo)
        
        # Timeout alcanzado
        progress_bar.progress(1.0)
        status_text.error("❌ Timeout: Validación falló")
        time.sleep(2)
        container.empty()
        
        return False