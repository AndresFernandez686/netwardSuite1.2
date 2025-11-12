"""
Módulo de procesamiento de PDFs para BusinessSuite
Funcionalidades para extraer y procesar información de archivos PDF
"""
import streamlit as st
import pandas as pd
import io
from datetime import datetime
import re
import sys
import os

# Agregar la ruta del módulo actual al path para importar smart_parser
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Nota: PyPDF2 y pdfplumber son opcionales, se maneja su ausencia
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

# Importar smart_parser
try:
    from smart_parser import SmartTimeParser, EntradaSalidaDetector
    SMART_PARSER_AVAILABLE = True
except ImportError:
    SMART_PARSER_AVAILABLE = False
    SmartTimeParser = None
    EntradaSalidaDetector = None

def verificar_dependencias_pdf():
    """
    Verifica si las dependencias para PDF están disponibles
    
    Returns:
        dict: Estado de las dependencias
    """
    estado = {
        'PyPDF2': PDF_AVAILABLE,
        'pdfplumber': PDFPLUMBER_AVAILABLE,
        'funcional': PDF_AVAILABLE or PDFPLUMBER_AVAILABLE
    }
    return estado

def extraer_texto_pdf_simple(file):
    """
    Extrae texto de un PDF usando PyPDF2 (método simple)
    
    Args:
        file: Archivo PDF subido
    
    Returns:
        tuple: (success, text_or_error)
    """
    if not PDF_AVAILABLE:
        return False, "PyPDF2 no está instalado. Use: pip install PyPDF2"
    
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        texto_completo = ""
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            texto_completo += page.extract_text() + "\n"
        
        return True, texto_completo
    
    except Exception as e:
        return False, f"Error extrayendo texto del PDF: {str(e)}"

def extraer_texto_pdf_avanzado(file):
    """
    Extrae texto de un PDF usando pdfplumber (método avanzado)
    
    Args:
        file: Archivo PDF subido
    
    Returns:
        tuple: (success, text_or_error)
    """
    if not PDFPLUMBER_AVAILABLE:
        return False, "pdfplumber no está instalado. Use: pip install pdfplumber"
    
    try:
        with pdfplumber.open(file) as pdf:
            texto_completo = ""
            for page in pdf.pages:
                texto_pagina = page.extract_text()
                if texto_pagina:
                    texto_completo += texto_pagina + "\n"
        
        return True, texto_completo
    
    except Exception as e:
        return False, f"Error extrayendo texto del PDF: {str(e)}"

def extraer_texto_pdf_con_estructura(file):
    """
    Extrae texto de un PDF preservando la estructura (tablas, columnas)
    Usa pdfplumber para mejor detección de estructura
    
    Args:
        file: Archivo PDF subido
    
    Returns:
        tuple: (success, text_or_error)
    """
    if not PDFPLUMBER_AVAILABLE:
        # Fallback a método simple
        return extraer_texto_pdf_simple(file)
    
    try:
        texto_estructurado = ""
        
        with pdfplumber.open(file) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Intentar extraer tablas primero
                tablas = page.extract_tables()
                
                if tablas:
                    # Si hay tablas, procesarlas
                    for tabla in tablas:
                        for fila in tabla:
                            if fila:
                                linea = " | ".join([str(celda) if celda else "" for celda in fila])
                                texto_estructurado += linea + "\n"
                        texto_estructurado += "\n"
                else:
                    # Si no hay tablas, extraer texto normal
                    texto_pagina = page.extract_text()
                    if texto_pagina:
                        texto_estructurado += texto_pagina + "\n"
                
                texto_estructurado += f"\n--- Página {page_num + 1} ---\n\n"
        
        return True, texto_estructurado
    
    except Exception as e:
        # Si falla, intentar método simple
        return extraer_texto_pdf_simple(file)

def procesar_pdf_horarios(file, progress_callback=None):
    """
    Procesa un PDF buscando información de horarios de trabajo
    
    Args:
        file: Archivo PDF
        progress_callback: Función para mostrar progreso
    
    Returns:
        tuple: (success, data_or_error)
    """
    # Intentar extraer texto
    if progress_callback:
        progress_callback(0.2, "Extrayendo texto del PDF...")
    
    # Probar primero con pdfplumber, luego con PyPDF2
    success, texto = extraer_texto_pdf_avanzado(file)
    if not success:
        success, texto = extraer_texto_pdf_simple(file)
    
    if not success:
        return False, texto
    
    if progress_callback:
        progress_callback(0.5, "Analizando contenido...")
    
    # Buscar patrones de horarios
    horarios_encontrados = buscar_patrones_horarios(texto)
    
    if progress_callback:
        progress_callback(0.8, "Estructurando datos...")
    
    # Convertir a DataFrame
    if horarios_encontrados:
        df_horarios = pd.DataFrame(horarios_encontrados)
        if progress_callback:
            progress_callback(1.0, "Completado")
        return True, df_horarios
    else:
        return False, "No se encontraron patrones de horarios reconocibles en el PDF"

def buscar_patrones_horarios(texto):
    """
    Busca patrones comunes de horarios en el texto extraído
    
    Args:
        texto (str): Texto extraído del PDF
    
    Returns:
        list: Lista de diccionarios con horarios encontrados
    """
    horarios = []
    lineas = texto.split('\n')
    
    # Patrones comunes para buscar
    patron_hora = r'(\d{1,2}):(\d{2})'
    patron_nombre = r'([A-Za-záéíóúñÁÉÍÓÚÑ\s]+)'
    patron_fecha = r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})'
    
    for i, linea in enumerate(lineas):
        linea_limpia = linea.strip()
        if not linea_limpia:
            continue
        
        # Buscar horas en la línea
        horas_encontradas = re.findall(patron_hora, linea_limpia)
        
        if len(horas_encontradas) >= 2:  # Al menos entrada y salida
            # Buscar nombre en líneas cercanas
            nombre_empleado = extraer_nombre_empleado(lineas, i)
            
            # Buscar fecha
            fecha_encontrada = re.search(patron_fecha, linea_limpia)
            fecha = fecha_encontrada.group(1) if fecha_encontrada else datetime.now().strftime("%d/%m/%Y")
            
            # Asumir primer hora como entrada, segunda como salida
            hora_entrada = f"{horas_encontradas[0][0]}:{horas_encontradas[0][1]}"
            hora_salida = f"{horas_encontradas[1][0]}:{horas_encontradas[1][1]}"
            
            # Calcular horas trabajadas (aproximado)
            horas_trabajadas = calcular_horas_diferencia(hora_entrada, hora_salida)
            
            horario = {
                'Empleado': nombre_empleado,
                'Fecha': fecha,
                'Hora_Entrada': hora_entrada,
                'Hora_Salida': hora_salida,
                'Horas_Trabajadas': horas_trabajadas,
                'Linea_Original': linea_limpia
            }
            
            horarios.append(horario)
    
    return horarios

def extraer_nombre_empleado(lineas, indice_actual):
    """
    Intenta extraer el nombre del empleado de líneas cercanas
    
    Args:
        lineas (list): Lista de líneas del texto
        indice_actual (int): Índice de la línea actual
    
    Returns:
        str: Nombre del empleado o "Empleado X"
    """
    # Buscar en líneas anteriores y posteriores
    rango_busqueda = 3
    inicio = max(0, indice_actual - rango_busqueda)
    fin = min(len(lineas), indice_actual + rango_busqueda + 1)
    
    patron_nombre = r'^[A-Za-záéíóúñÁÉÍÓÚÑ\s]{3,30}$'
    
    for i in range(inicio, fin):
        if i == indice_actual:
            continue
        
        linea_candidata = lineas[i].strip()
        
        # Verificar si la línea parece un nombre
        if re.match(patron_nombre, linea_candidata) and len(linea_candidata.split()) >= 2:
            return linea_candidata
    
    return f"Empleado {indice_actual + 1}"

def calcular_horas_diferencia(hora_entrada, hora_salida):
    """
    Calcula la diferencia en horas entre entrada y salida
    
    Args:
        hora_entrada (str): Hora en formato HH:MM
        hora_salida (str): Hora en formato HH:MM
    
    Returns:
        float: Horas trabajadas
    """
    try:
        entrada_hora, entrada_min = map(int, hora_entrada.split(':'))
        salida_hora, salida_min = map(int, hora_salida.split(':'))
        
        minutos_entrada = entrada_hora * 60 + entrada_min
        minutos_salida = salida_hora * 60 + salida_min
        
        # Si la salida es menor que la entrada, asumir que cruza medianoche
        if minutos_salida < minutos_entrada:
            minutos_salida += 24 * 60
        
        diferencia_minutos = minutos_salida - minutos_entrada
        return round(diferencia_minutos / 60, 2)
    
    except:
        return 0.0

def procesar_pdf_general(file, tipo_busqueda="horarios"):
    """
    Función general para procesar PDFs según el tipo solicitado
    
    Args:
        file: Archivo PDF
        tipo_busqueda (str): Tipo de información a buscar
    
    Returns:
        tuple: (success, result_or_error)
    """
    estado_deps = verificar_dependencias_pdf()
    
    if not estado_deps['funcional']:
        return False, "No hay librerías PDF disponibles. Instale: pip install PyPDF2 pdfplumber"
    
    if tipo_busqueda == "horarios":
        return procesar_pdf_horarios(file)
    elif tipo_busqueda == "texto":
        # Extraer solo texto
        success, texto = extraer_texto_pdf_avanzado(file)
        if not success:
            success, texto = extraer_texto_pdf_simple(file)
        return success, texto
    else:
        return False, f"Tipo de búsqueda '{tipo_busqueda}' no soportado"

def mostrar_interface_pdf():
    """
    Muestra la interfaz para procesar PDFs en Streamlit
    """
    st.subheader("📄 Procesador de PDFs")
    
    # Verificar dependencias
    estado_deps = verificar_dependencias_pdf()
    
    if not estado_deps['funcional']:
        st.error("⚠️ Librerías PDF no disponibles")
        st.info("Para usar esta funcionalidad, instale las dependencias:")
        st.code("pip install PyPDF2 pdfplumber")
        return
    
    # Estado de dependencias
    st.success(f"✅ Dependencias PDF: PyPDF2={estado_deps['PyPDF2']}, pdfplumber={estado_deps['pdfplumber']}")
    
    # Subir archivo
    archivo_pdf = st.file_uploader(
        "Seleccione un archivo PDF",
        type=['pdf'],
        help="Suba un PDF con información de horarios o empleados"
    )
    
    if archivo_pdf:
        st.info(f"📁 Archivo seleccionado: {archivo_pdf.name}")
        
        # Opciones de procesamiento
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_procesamiento = st.selectbox(
                "Tipo de procesamiento",
                ["horarios", "texto"],
                help="Seleccione qué información extraer del PDF"
            )
        
        with col2:
            procesar_btn = st.button("🔄 Procesar PDF", type="primary")
        
        if procesar_btn:
            with st.spinner("Procesando PDF..."):
                success, resultado = procesar_pdf_general(archivo_pdf, tipo_procesamiento)
            
            if success:
                if tipo_procesamiento == "horarios":
                    st.success("✅ PDF procesado exitosamente")
                    st.dataframe(resultado, use_container_width=True)
                    
                    # Opción de descarga
                    if not resultado.empty:
                        csv_data = resultado.to_csv(index=False)
                        st.download_button(
                            label="📥 Descargar como CSV",
                            data=csv_data,
                            file_name=f"horarios_extraidos_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv"
                        )
                
                elif tipo_procesamiento == "texto":
                    st.success("✅ Texto extraído exitosamente")
                    st.text_area("Texto extraído:", resultado, height=300)
                    
                    # Estadísticas del texto
                    palabras = len(resultado.split())
                    caracteres = len(resultado)
                    lineas = len(resultado.split('\n'))
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Palabras", palabras)
                    with col2:
                        st.metric("Caracteres", caracteres)
                    with col3:
                        st.metric("Líneas", lineas)
            
            else:
                st.error(f"❌ Error procesando PDF: {resultado}")

# Funciones de utilidad adicionales
def limpiar_texto_pdf(texto):
    """
    Limpia el texto extraído de PDFs removiendo caracteres extraños
    
    Args:
        texto (str): Texto a limpiar
    
    Returns:
        str: Texto limpio
    """
    # Remover caracteres de control
    texto_limpio = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', texto)
    
    # Normalizar espacios
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio)
    
    # Remover líneas vacías múltiples
    texto_limpio = re.sub(r'\n\s*\n', '\n\n', texto_limpio)
    
    return texto_limpio.strip()

def detectar_estructura_pdf(texto):
    """
    Intenta detectar la estructura del contenido del PDF
    
    Args:
        texto (str): Texto del PDF
    
    Returns:
        dict: Información sobre la estructura detectada
    """
    estructura = {
        'tipo_documento': 'desconocido',
        'tiene_horarios': False,
        'tiene_empleados': False,
        'tiene_fechas': False,
        'tiene_numeros': False
    }
    
    # Detectar patrones
    if re.search(r'\d{1,2}:\d{2}', texto):
        estructura['tiene_horarios'] = True
    
    if re.search(r'[A-Za-záéíóúñÁÉÍÓÚÑ\s]{3,}\s+[A-Za-záéíóúñÁÉÍÓÚÑ\s]{3,}', texto):
        estructura['tiene_empleados'] = True
    
    if re.search(r'\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}', texto):
        estructura['tiene_fechas'] = True
    
    if re.search(r'\d+[.,]\d+', texto):
        estructura['tiene_numeros'] = True
    
    # Determinar tipo probable
    if estructura['tiene_horarios'] and estructura['tiene_empleados']:
        estructura['tipo_documento'] = 'planilla_horarios'
    elif estructura['tiene_empleados'] and estructura['tiene_numeros']:
        estructura['tipo_documento'] = 'planilla_sueldos'
    elif estructura['tiene_horarios']:
        estructura['tipo_documento'] = 'registro_horarios'
    
    return estructura

def procesar_pdf_a_dataframe(archivo_pdf):
    """
    Procesa un archivo PDF y lo convierte a DataFrame usando smart_parser
    
    Args:
        archivo_pdf: Archivo PDF subido
    
    Returns:
        pd.DataFrame: DataFrame con los datos extraídos
    """
    try:
        # Extraer texto del PDF
        texto_pdf = ""
        
        # Intentar con pdfplumber primero (mejor para tablas)
        if PDFPLUMBER_AVAILABLE:
            try:
                import pdfplumber
                with pdfplumber.open(archivo_pdf) as pdf:
                    for pagina in pdf.pages:
                        texto_pagina = pagina.extract_text()
                        if texto_pagina:
                            texto_pdf += texto_pagina + "\n"
            except Exception as e:
                st.warning(f"pdfplumber falló: {str(e)}. Intentando con PyPDF2...")
        
        # Fallback a PyPDF2 si pdfplumber no funcionó
        if not texto_pdf and PDF_AVAILABLE:
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(archivo_pdf)
                for page in pdf_reader.pages:
                    texto_pdf += page.extract_text() + "\n"
            except Exception as e:
                st.error(f"PyPDF2 falló: {str(e)}")
        
        if not texto_pdf:
            st.error("❌ No se pudo extraer texto del PDF")
            return pd.DataFrame()
        
        # Usar smart_parser para procesamiento inteligente
        if SMART_PARSER_AVAILABLE:
            try:
                lineas = texto_pdf.split('\n')
                
                # Analizar estructura
                estructura = analizar_estructura_pdf(lineas)
                
                # Extraer datos con smart_parser
                datos_brutos = extraer_datos_segun_estructura(lineas, estructura)
                
                # Convertir a DataFrame estándar
                if datos_brutos:
                    df = convertir_a_dataframe_estandar(datos_brutos)
                    if not df.empty:
                        st.success("✅ Datos extraídos con smart_parser")
                        return df
                
                st.warning("⚠️ No se pudieron extraer datos estructurados, usando método básico")
                
            except Exception as e:
                st.warning(f"⚠️ Error con smart_parser: {str(e)}, usando método básico")
        else:
            st.warning("⚠️ smart_parser no disponible, usando método básico")
        
        # Fallback al método básico
        return convertir_texto_a_dataframe(texto_pdf)
        
    except Exception as e:
        st.error(f"❌ Error procesando PDF: {str(e)}")
        import traceback
        st.error(f"Detalles: {traceback.format_exc()}")
        return pd.DataFrame()

def validar_datos_pdf(df):
    """
    Valida que el DataFrame extraído del PDF tenga la estructura correcta
    
    Args:
        df (pd.DataFrame): DataFrame a validar
    
    Returns:
        tuple: (es_valido, lista_errores)
    """
    errores = []
    
    # Verificar columnas necesarias
    columnas_requeridas = ['Empleado', 'Fecha', 'Entrada', 'Salida']
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
    
    if columnas_faltantes:
        errores.append(f"Faltan columnas: {', '.join(columnas_faltantes)}")
    
    # Verificar que no esté vacío
    if df.empty:
        errores.append("El DataFrame está vacío")
    
    # Verificar tipos de datos
    if 'Fecha' in df.columns:
        try:
            pd.to_datetime(df['Fecha'], errors='coerce')
        except:
            errores.append("Formato de fecha inválido")
    
    return (len(errores) == 0, errores)

def detectar_registros_incompletos(df):
    """
    Detecta registros con datos faltantes (entrada o salida sin valor)
    
    Args:
        df (pd.DataFrame): DataFrame con registros
    
    Returns:
        pd.DataFrame: DataFrame con registros incompletos
    """
    try:
        # Detectar registros donde falta entrada o salida
        mascara_incompletos = (
            (df['Entrada'].isna() | (df['Entrada'] == '')) |
            (df['Salida'].isna() | (df['Salida'] == ''))
        )
        
        df_incompletos = df[mascara_incompletos].copy()
        
        return df_incompletos
        
    except Exception as e:
        st.warning(f"Error detectando registros incompletos: {str(e)}")
        return pd.DataFrame()

def filtrar_registros_sin_asistencia(df):
    """
    Filtra y separa registros sin entrada NI salida (días libres/faltas)
    
    Args:
        df (pd.DataFrame): DataFrame con todos los registros
    
    Returns:
        tuple: (df_con_asistencia, df_sin_asistencia)
    """
    try:
        # Registros sin entrada NI salida (ambos vacíos)
        mascara_sin_asistencia = (
            (df['Entrada'].isna() | (df['Entrada'] == '')) &
            (df['Salida'].isna() | (df['Salida'] == ''))
        )
        
        df_sin_asistencia = df[mascara_sin_asistencia].copy()
        df_con_asistencia = df[~mascara_sin_asistencia].copy()
        
        return df_con_asistencia, df_sin_asistencia
        
    except Exception as e:
        st.warning(f"Error filtrando registros: {str(e)}")
        return df, pd.DataFrame()

def detectar_horarios_ambiguos(df):
    """
    Detecta registros donde la entrada podría ser salida y viceversa
    (ej: entrada en la tarde y salida en la mañana)
    
    Args:
        df (pd.DataFrame): DataFrame con registros
    
    Returns:
        pd.DataFrame: DataFrame con registros ambiguos
    """
    try:
        registros_ambiguos = []
        
        for idx, row in df.iterrows():
            try:
                # Convertir a formato de hora
                entrada_str = str(row.get('Entrada', ''))
                salida_str = str(row.get('Salida', ''))
                
                if not entrada_str or not salida_str or entrada_str == 'nan' or salida_str == 'nan':
                    continue
                
                # Parsear horas
                entrada_match = re.search(r'(\d{1,2}):(\d{2})', entrada_str)
                salida_match = re.search(r'(\d{1,2}):(\d{2})', salida_str)
                
                if not entrada_match or not salida_match:
                    continue
                
                hora_entrada = int(entrada_match.group(1))
                hora_salida = int(salida_match.group(1))
                
                # Detectar casos ambiguos:
                # 1. Entrada después de las 18:00 (posible turno tarde)
                # 2. Salida antes de las 12:00 (posible turno mañana)
                # 3. Entrada > Salida (posible inversión)
                
                es_ambiguo = False
                
                if hora_entrada > hora_salida:
                    es_ambiguo = True  # Entrada después de salida
                elif hora_entrada > 18 and hora_salida < 12:
                    es_ambiguo = True  # Posible turno nocturno mal registrado
                elif hora_entrada < 6:
                    es_ambiguo = True  # Entrada muy temprano (posible error)
                
                if es_ambiguo:
                    registros_ambiguos.append(row)
                    
            except Exception as e:
                continue
        
        if registros_ambiguos:
            return pd.DataFrame(registros_ambiguos)
        else:
            return pd.DataFrame()
        
    except Exception as e:
        st.warning(f"Error detectando horarios ambiguos: {str(e)}")
        return pd.DataFrame()

def convertir_texto_a_dataframe(texto):
    """
    Convierte texto extraído del PDF en un DataFrame estructurado
    Detecta automáticamente diferentes formatos de PDF
    
    Args:
        texto (str): Texto extraído del PDF
    
    Returns:
        pd.DataFrame: DataFrame con los datos estructurados
    """
    try:
        lineas = texto.strip().split('\n')
        datos = []
        
        # Mostrar preview del texto extraído para debugging
        st.info(f"📄 Texto extraído del PDF ({len(lineas)} líneas)")
        with st.expander("🔍 Ver contenido extraído (primeras 30 líneas)"):
            preview_lines = '\n'.join(lineas[:30])
            st.code(preview_lines, language='text')
        
        # PATRÓN 1: Formato tabla con | separadores
        # Ejemplo: Empleado | Fecha | Entrada | Salida
        if '|' in texto:
            st.info("📋 Detectado formato tabla con separadores |")
            for linea in lineas:
                if '|' in linea:
                    partes = [p.strip() for p in linea.split('|')]
                    if len(partes) >= 4:
                        # Verificar si tiene horas (formato HH:MM)
                        tiene_horas = any(re.match(r'\d{1,2}:\d{2}', p) for p in partes)
                        if tiene_horas:
                            # Encontrar índices de entrada y salida
                            entrada = next((p for p in partes if re.match(r'\d{1,2}:\d{2}', p)), '')
                            salida = next((p for p in partes[partes.index(entrada)+1:] if re.match(r'\d{1,2}:\d{2}', p)), '') if entrada else ''
                            
                            # Encontrar fecha
                            fecha = next((p for p in partes if re.search(r'\d{1,2}[\/\-]\d{1,2}', p)), '')
                            
                            # Empleado es típicamente la primera columna no numérica
                            empleado = partes[0] if partes[0] and not re.match(r'^\d+$', partes[0]) else 'Empleado'
                            
                            if entrada or salida:
                                datos.append({
                                    'Empleado': empleado,
                                    'Fecha': fecha if fecha else datetime.now().strftime("%d/%m/%Y"),
                                    'Entrada': entrada,
                                    'Salida': salida
                                })
        
        # PATRÓN 2: Formato espaciado
        # Ejemplo: Juan Perez 01/11/2025 08:00 17:00
        if not datos:
            st.info("📋 Intentando formato con espacios")
            for linea in lineas:
                # Buscar patrones de: Nombre Fecha Entrada Salida
                match = re.search(
                    r'([A-Za-záéíóúñÁÉÍÓÚÑ\s]+?)\s+(\d{1,2}[\/\-]\d{1,2}[\/\-]?\d{0,4})\s+(\d{1,2}:\d{2})\s+(\d{1,2}:\d{2})',
                    linea
                )
                
                if match:
                    datos.append({
                        'Empleado': match.group(1).strip(),
                        'Fecha': match.group(2),
                        'Entrada': match.group(3),
                        'Salida': match.group(4)
                    })
        
        # PATRÓN 3: Líneas con múltiples horas
        # Buscar cualquier línea que tenga al menos 2 horas
        if not datos:
            st.info("📋 Buscando patrones de horarios en texto libre")
            empleado_actual = None
            fecha_actual = None
            
            for i, linea in enumerate(lineas):
                linea_limpia = linea.strip()
                if not linea_limpia or len(linea_limpia) < 5:
                    continue
                
                # Buscar nombre (líneas con solo letras y espacios, 3-40 chars)
                if re.match(r'^[A-Za-záéíóúñÁÉÍÓÚÑ\s]{3,40}$', linea_limpia):
                    empleado_actual = linea_limpia
                    continue
                
                # Buscar fecha
                match_fecha = re.search(r'(\d{1,2}[\/\-]\d{1,2}[\/\-]?\d{0,4})', linea_limpia)
                if match_fecha:
                    fecha_actual = match_fecha.group(1)
                
                # Buscar horas
                horas = re.findall(r'(\d{1,2}:\d{2})', linea_limpia)
                if len(horas) >= 2:
                    datos.append({
                        'Empleado': empleado_actual if empleado_actual else f'Empleado_{i}',
                        'Fecha': fecha_actual if fecha_actual else datetime.now().strftime("%d/%m/%Y"),
                        'Entrada': horas[0],
                        'Salida': horas[1]
                    })
        
        if datos:
            st.success(f"✅ Se extrajeron {len(datos)} registros del PDF")
            df = pd.DataFrame(datos)
            
            # Limpiar y convertir fecha
            df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y', errors='coerce')
            if df['Fecha'].isna().all():
                # Intentar otro formato
                df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
            
            # Mostrar preview de datos extraídos
            with st.expander("👀 Ver datos extraídos"):
                st.dataframe(df.head(10))
            
            return df
        else:
            st.error("❌ No se pudieron extraer datos del PDF")
            st.warning("""
            **Posibles causas:**
            - El PDF no contiene texto extraíble (es una imagen escaneada)
            - El formato del PDF no es compatible con los patrones de búsqueda
            - Los datos no están en formato tabular
            
            **Soluciones:**
            - Usa un PDF con texto seleccionable (no escaneos)
            - Verifica que el PDF contenga: Empleado, Fecha, Hora Entrada, Hora Salida
            - Considera usar el formato Excel en su lugar
            """)
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Error convirtiendo texto a DataFrame: {str(e)}")
        import traceback
        with st.expander("🔍 Ver detalles del error"):
            st.code(traceback.format_exc())
        return pd.DataFrame()

# ============================================================================
# FUNCIONES AUXILIARES PARA SMART_PARSER
# ============================================================================

def analizar_estructura_pdf(lineas):
    """
    Analiza la estructura del PDF para identificar patrones
    
    Args:
        lineas: Lista de líneas del texto extraído
        
    Returns:
        Dict: Información sobre la estructura identificada
    """
    estructura = {
        "tipo": "desconocido",
        "patron_empleado": None,
        "patron_fecha_hora": None,
        "columnas_detectadas": [],
        "separador": None
    }
    
    # Detectar patrones comunes
    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue
            
        # Patrón: Empleado: Nombre
        if re.match(r'Empleado:', linea, re.IGNORECASE):
            estructura["patron_empleado"] = "empleado_prefijo"
            
        # Patrón: Fecha y hora juntas (YYYY-MM-DD HH:MM:SS)
        if re.search(r'\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}:\d{2}', linea):
            estructura["patron_fecha_hora"] = "fecha_hora_completa"
            
        # Patrón: Fecha y hora juntas (YYYY-MM-DD HH:MM)
        if re.search(r'\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}', linea):
            estructura["patron_fecha_hora"] = "fecha_hora_separada"
            
        # Patrón: Fecha y hora juntas (DD/MM/YYYY HH:MM)
        if re.search(r'\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}', linea):
            estructura["patron_fecha_hora"] = "fecha_hora_barras"
            
        # Detectar si hay columnas tabulares
        if '\t' in linea or '|' in linea or '  ' in linea:
            estructura["tipo"] = "tabular"
            
    return estructura

def extraer_datos_segun_estructura(lineas, estructura):
    """
    Extrae datos según la estructura identificada usando el parser inteligente
    """
    if not SMART_PARSER_AVAILABLE:
        return []
    
    try:
        parser = SmartTimeParser()
        detector = EntradaSalidaDetector()
        
        datos = []
        empleado_actual = None
        
        # Buscar nombres en todo el documento primero
        posibles_nombres = _buscar_nombres_en_documento(lineas)
        
        for i, linea in enumerate(lineas):
            linea = linea.strip()
            if not linea:
                continue
                
            # Detectar nombre de empleado (varios patrones)
            if re.match(r'Empleado:', linea, re.IGNORECASE):
                empleado_actual = linea.split(':', 1)[1].strip()
                continue
            elif re.match(r'Nombre:', linea, re.IGNORECASE):
                empleado_actual = linea.split(':', 1)[1].strip()
                continue
            elif re.match(r'^[A-ZÁÉÍÓÚ][a-záéíóú]+ [A-ZÁÉÍÓÚ][a-záéíóú]+.*$', linea):
                # Patrón de nombre completo (Nombre Apellido)
                if not any(char.isdigit() for char in linea) and len(linea.split()) >= 2:
                    empleado_actual = linea.strip()
                    continue
            elif re.match(r'^[A-ZÁÉÍÓÚ][a-záéíóúñ]+$', linea):
                # Patrón de nombre simple (solo una palabra, como "Paz")
                if len(linea.strip()) >= 2 and linea.strip().isalpha():
                    empleado_actual = linea.strip()
                    continue
            elif re.match(r'^[A-ZÁÉÍÓÚ][a-záéíóúñ]+\s*$', linea.strip()):
                # Patrón de nombre con posibles espacios al final
                nombre_limpio = linea.strip()
                if len(nombre_limpio) >= 2 and nombre_limpio.isalpha():
                    empleado_actual = nombre_limpio
                    continue
            
            # Extraer fechas y horas de la línea
            fechas_horas = parser.extraer_fecha_hora(linea)
            
            for fh in fechas_horas:
                # Si no hay empleado actual, usar el primer nombre encontrado o "Empleado 1"
                if not empleado_actual and posibles_nombres:
                    nombre_empleado = posibles_nombres[0]
                else:
                    nombre_empleado = empleado_actual if empleado_actual else "Empleado 1"
                
                # Detectar tipo (entrada/salida)
                contexto = lineas[max(0, i-2):i+3] if i > 0 else [linea]
                tipo = detector.detectar_tipo(linea, fh['hora'], contexto)
                
                datos.append({
                    "empleado": nombre_empleado,
                    "fecha": fh['fecha'],
                    "hora": fh['hora'],
                    "tipo": tipo,
                    "linea_original": linea,
                    "confianza": _calcular_confianza(linea, fh)
                })
        
        return datos
    except ImportError as e:
        st.error(f"Error: smart_parser no disponible: {str(e)}")
        return []

def _buscar_nombres_en_documento(lineas):
    """
    Busca posibles nombres de empleados en todo el documento
    Optimizado para PDFs de marcaciones donde el nombre aparece solo (ej: "Yanina")
    """
    nombres_encontrados = []
    frecuencia_nombres = {}
    
    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue
            
        # Buscar patrones de nombres
        # Nombre con "Nombre:" o "Empleado:"
        if re.match(r'(Nombre|Empleado):', linea, re.IGNORECASE):
            nombre = linea.split(':', 1)[1].strip()
            if nombre:
                frecuencia_nombres[nombre] = frecuencia_nombres.get(nombre, 0) + 1
        
        # Nombre simple (una palabra alfabética, primera letra mayúscula)
        # Este es el patrón más común en PDFs de marcaciones
        elif re.match(r'^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+$', linea):
            if len(linea) >= 3:  # Al menos 3 letras
                # Evitar palabras que claramente no son nombres
                palabras_excluir = ['Hora', 'Fecha', 'Entrada', 'Salida', 'Total', 'Reporte', 
                                   'Asistencia', 'Estado', 'Nada', 'Nombre', 'Departamento']
                if linea not in palabras_excluir:
                    frecuencia_nombres[linea] = frecuencia_nombres.get(linea, 0) + 1
        
        # Nombre completo (dos o más palabras)
        elif re.match(r'^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+ [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+.*$', linea):
            if not any(char.isdigit() for char in linea):
                frecuencia_nombres[linea] = frecuencia_nombres.get(linea, 0) + 1
    
    # Ordenar por frecuencia (los nombres aparecen muchas veces en el PDF)
    # El nombre del empleado aparecerá en cada registro
    nombres_ordenados = sorted(frecuencia_nombres.items(), key=lambda x: x[1], reverse=True)
    
    # Tomar los nombres más frecuentes (probablemente son empleados)
    for nombre, frecuencia in nombres_ordenados:
        if frecuencia >= 2:  # Apareció al menos 2 veces
            nombres_encontrados.append(nombre)
    
    return nombres_encontrados

def _calcular_confianza(linea, fecha_hora):
    """
    Calcula un nivel de confianza para la extracción
    """
    confianza = 0.5
    
    # Aumentar confianza si hay palabras clave
    if re.search(r'entrada|ingreso', linea, re.IGNORECASE):
        confianza += 0.2
    if re.search(r'salida|egreso', linea, re.IGNORECASE):
        confianza += 0.2
    
    # Aumentar confianza si la fecha está completa
    if fecha_hora.get('fecha'):
        confianza += 0.1
    
    return min(confianza, 1.0)

def convertir_a_dataframe_estandar(datos_brutos):
    """
    Convierte los datos brutos extraídos a DataFrame estándar
    LÓGICA: Primera hora del día = Entrada, Segunda hora = Salida
    Si solo hay una marcación, se marca como incompleto para revisión administrativa
    """
    if not datos_brutos:
        return pd.DataFrame()
    
    # Agrupar por empleado y fecha, guardando todas las horas
    registros_por_dia = {}
    
    for dato in datos_brutos:
        empleado = dato['empleado']
        fecha = dato['fecha']
        hora = dato['hora']
        
        clave = (empleado, fecha)
        
        if clave not in registros_por_dia:
            registros_por_dia[clave] = {
                'empleado': empleado,
                'fecha': fecha,
                'horas': []
            }
        
        registros_por_dia[clave]['horas'].append(hora)
    
    # Convertir a formato final: Primera hora = Entrada, Segunda hora = Salida
    registros_finales = []
    
    for (empleado, fecha), info in registros_por_dia.items():
        # CRÍTICO: Eliminar duplicados primero (el parser puede leer la misma hora múltiples veces)
        horas_unicas = list(set(info['horas']))  # Eliminar duplicados
        horas_ordenadas = sorted(horas_unicas)  # Ordenar alfabéticamente (funciona para HH:MM:SS)
        
        if len(horas_ordenadas) >= 2:
            # Caso normal: dos marcaciones
            entrada = horas_ordenadas[0]
            salida = horas_ordenadas[1]
            
            registros_finales.append({
                'Empleado': empleado,
                'Fecha': fecha,
                'Entrada': entrada,
                'Salida': salida
            })
        elif len(horas_ordenadas) == 1:
            # Caso incompleto: solo una marcación - requiere decisión administrativa
            registros_finales.append({
                'Empleado': empleado,
                'Fecha': fecha,
                'Entrada': horas_ordenadas[0],  # Temporalmente como entrada
                'Salida': ''  # Vacío para que sea detectado como incompleto
            })
    
    # Convertir a DataFrame
    df = pd.DataFrame(registros_finales)
    
    # Ordenar por empleado y fecha
    if not df.empty:
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df = df.sort_values(['Empleado', 'Fecha']).reset_index(drop=True)
    
    return df