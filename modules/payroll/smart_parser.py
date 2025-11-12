"""
Módulo de análisis inteligente para BusinessSuite
Funcionalidades para interpretar y procesar horarios de forma inteligente
"""
import re
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, List, Tuple, Optional

class SmartTimeParser:
    """Clase para parsing inteligente de fechas y horas"""
    
    def __init__(self):
        self.patrones_fecha = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{1,2}/\d{1,2}/\d{4})',  # DD/MM/YYYY o MM/DD/YYYY
            r'(\d{1,2}-\d{1,2}-\d{4})',  # DD-MM-YYYY
            r'(\d{1,2}\.\d{1,2}\.\d{4})',  # DD.MM.YYYY
        ]
        
        self.patrones_hora = [
            r'(\d{1,2}:\d{2}:\d{2})',  # HH:MM:SS
            r'(\d{1,2}:\d{2})',  # HH:MM
            r'(\d{1,2}\.\d{2})',  # HH.MM
        ]
        
        self.patrones_fecha_hora = [
            r'(\d{4}-\d{2}-\d{2})\s+(\d{1,2}:\d{2}:\d{2})',  # YYYY-MM-DD HH:MM:SS
            r'(\d{4}-\d{2}-\d{2})\s+(\d{1,2}:\d{2})',  # YYYY-MM-DD HH:MM
            r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}:\d{2})',  # DD/MM/YYYY HH:MM:SS
            r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2})',  # DD/MM/YYYY HH:MM
            r'(\d{1,2}-\d{1,2}-\d{4})\s+(\d{1,2}:\d{2}:\d{2})',  # DD-MM-YYYY HH:MM:SS
            r'(\d{1,2}-\d{1,2}-\d{4})\s+(\d{1,2}:\d{2})',  # DD-MM-YYYY HH:MM
        ]
        
        self.palabras_horario = {
            'entrada': ['entrada', 'ingreso', 'inicio', 'llegada', 'start'],
            'salida': ['salida', 'egreso', 'fin', 'final', 'end'],
            'descanso': ['almuerzo', 'descanso', 'break', 'pausa', 'lunch'],
            'extra': ['extra', 'especial', 'nocturno', 'overtime', 'adicional']
        }
    
    def extraer_fecha_hora(self, texto: str) -> List[Dict]:
        """
        Extrae todas las fechas y horas de un texto
        
        Args:
            texto: Texto a procesar
            
        Returns:
            List[Dict]: Lista de fechas y horas encontradas
        """
        resultados = []
        
        # Buscar patrones de fecha y hora juntas
        for patron in self.patrones_fecha_hora:
            matches = re.finditer(patron, texto)
            for match in matches:
                fecha_str = match.group(1)
                hora_str = match.group(2)
                
                fecha_normalizada = self.normalizar_fecha(fecha_str)
                hora_normalizada = self.normalizar_hora(hora_str)
                
                if fecha_normalizada and hora_normalizada:
                    resultados.append({
                        'fecha': fecha_normalizada,
                        'hora': hora_normalizada,
                        'texto_original': match.group(0),
                        'posicion': match.start()
                    })
        
        return resultados
    
    def normalizar_fecha(self, fecha_str: str) -> Optional[str]:
        """
        Normaliza diferentes formatos de fecha a YYYY-MM-DD
        
        Args:
            fecha_str: String de fecha en formato variable
            
        Returns:
            str: Fecha normalizada o None si no se puede procesar
        """
        try:
            # Formato YYYY-MM-DD (ya normalizado)
            if re.match(r'\d{4}-\d{2}-\d{2}', fecha_str):
                return fecha_str
            
            # Formato DD/MM/YYYY
            if re.match(r'\d{1,2}/\d{1,2}/\d{4}', fecha_str):
                partes = fecha_str.split('/')
                if len(partes) == 3:
                    dia, mes, año = partes
                    return f"{año}-{mes.zfill(2)}-{dia.zfill(2)}"
            
            # Formato DD-MM-YYYY
            if re.match(r'\d{1,2}-\d{1,2}-\d{4}', fecha_str):
                partes = fecha_str.split('-')
                if len(partes) == 3:
                    dia, mes, año = partes
                    return f"{año}-{mes.zfill(2)}-{dia.zfill(2)}"
            
            # Formato DD.MM.YYYY
            if re.match(r'\d{1,2}\.\d{1,2}\.\d{4}', fecha_str):
                partes = fecha_str.split('.')
                if len(partes) == 3:
                    dia, mes, año = partes
                    return f"{año}-{mes.zfill(2)}-{dia.zfill(2)}"
                    
        except Exception:
            pass
            
        return None
    
    def normalizar_hora(self, hora_str: str) -> Optional[str]:
        """
        Normaliza diferentes formatos de hora a HH:MM
        
        Args:
            hora_str: String de hora en formato variable
            
        Returns:
            str: Hora normalizada o None si no se puede procesar
        """
        try:
            # Formato HH:MM:SS -> HH:MM
            if re.match(r'\d{1,2}:\d{2}:\d{2}', hora_str):
                return hora_str[:5]
            
            # Formato HH:MM (ya normalizado)
            if re.match(r'\d{1,2}:\d{2}', hora_str):
                partes = hora_str.split(':')
                return f"{partes[0].zfill(2)}:{partes[1]}"
            
            # Formato HH.MM -> HH:MM
            if re.match(r'\d{1,2}\.\d{2}', hora_str):
                return hora_str.replace('.', ':')
                
        except Exception:
            pass
            
        return None

class SmartScheduleProcessor:
    """
    Procesador inteligente de horarios completos
    """
    
    def __init__(self):
        self.parser = SmartTimeParser()
        self.empleados_detectados = {}
        self.horarios_procesados = []
    
    def procesar_texto_completo(self, texto: str, progress_callback=None) -> pd.DataFrame:
        """
        Procesa un texto completo extrayendo todos los horarios
        
        Args:
            texto (str): Texto a procesar
            progress_callback: Función para mostrar progreso
        
        Returns:
            pd.DataFrame: DataFrame con horarios procesados
        """
        lineas = texto.split('\n')
        total_lineas = len(lineas)
        
        horarios_encontrados = []
        empleado_actual = None
        fecha_actual = None
        
        for i, linea in enumerate(lineas):
            if progress_callback:
                progreso = (i + 1) / total_lineas
                progress_callback(progreso, f"Procesando línea {i + 1}/{total_lineas}")
            
            if not linea.strip():
                continue
            
            resultado = self.parser.parsear_linea_horario(linea)
            
            if resultado['es_valido']:
                # Actualizar empleado actual si se encuentra uno nuevo
                if resultado['empleado_posible']:
                    empleado_actual = resultado['empleado_posible']
                
                # Actualizar fecha actual si se encuentra una nueva
                if resultado['fechas_encontradas']:
                    fecha_actual = resultado['fechas_encontradas'][0]
                
                # Procesar horario
                horario_procesado = self._procesar_horario_individual(
                    resultado, empleado_actual, fecha_actual, i + 1
                )
                
                if horario_procesado:
                    horarios_encontrados.append(horario_procesado)
        
        return pd.DataFrame(horarios_encontrados)
    
    def _procesar_horario_individual(self, resultado: Dict, empleado: str, fecha: str, linea_num: int) -> Optional[Dict]:
        """
        Procesa un horario individual extraído
        
        Args:
            resultado (Dict): Resultado del parser
            empleado (str): Nombre del empleado actual
            fecha (str): Fecha actual
            linea_num (int): Número de línea
        
        Returns:
            Dict: Horario procesado o None
        """
        if not resultado['horas_encontradas']:
            return None
        
        horas = resultado['horas_encontradas']
        
        # Determinar entrada y salida
        if len(horas) >= 2:
            hora_entrada = horas[0]
            hora_salida = horas[1]
        elif len(horas) == 1:
            # Solo una hora, determinar si es entrada o salida por contexto
            if resultado['tipo_horario'] == 'entrada':
                hora_entrada = horas[0]
                hora_salida = None
            elif resultado['tipo_horario'] == 'salida':
                hora_entrada = None
                hora_salida = horas[0]
            else:
                hora_entrada = horas[0]
                hora_salida = None
        else:
            return None
        
        # Calcular horas trabajadas
        horas_trabajadas = 0
        if hora_entrada and hora_salida:
            horas_trabajadas = self._calcular_horas_trabajadas(hora_entrada, hora_salida)
        
        # Clasificar tipo de horas
        tipo_horas = self._clasificar_tipo_horas(hora_entrada, hora_salida, resultado['tipo_horario'])
        
        return {
            'Empleado': empleado or f'Empleado_Linea_{linea_num}',
            'Fecha': fecha or datetime.now().strftime('%d/%m/%Y'),
            'Hora_Entrada': hora_entrada,
            'Hora_Salida': hora_salida,
            'Horas_Trabajadas': horas_trabajadas,
            'Tipo_Horario': tipo_horas,
            'Tipo_Detectado': resultado['tipo_horario'],
            'Linea_Original': resultado['texto_original'],
            'Linea_Numero': linea_num
        }
    
    def _calcular_horas_trabajadas(self, entrada: str, salida: str) -> float:
        """
        Calcula las horas trabajadas entre entrada y salida
        
        Args:
            entrada (str): Hora de entrada en formato HH:MM
            salida (str): Hora de salida en formato HH:MM
        
        Returns:
            float: Horas trabajadas
        """
        try:
            hora_entrada = datetime.strptime(entrada, '%H:%M')
            hora_salida = datetime.strptime(salida, '%H:%M')
            
            # Si la salida es menor que la entrada, asumir que cruza medianoche
            if hora_salida < hora_entrada:
                hora_salida += timedelta(days=1)
            
            diferencia = hora_salida - hora_entrada
            return round(diferencia.total_seconds() / 3600, 2)
        
        except:
            return 0.0
    
    def _clasificar_tipo_horas(self, entrada: str, salida: str, tipo_detectado: str) -> str:
        """
        Clasifica el tipo de horas (normales, especiales, nocturnas)
        
        Args:
            entrada (str): Hora de entrada
            salida (str): Hora de salida
            tipo_detectado (str): Tipo detectado por el parser
        
        Returns:
            str: Clasificación del tipo de horas
        """
        if tipo_detectado == 'extra':
            return 'Especiales'
        
        if not entrada or not salida:
            return 'Normales'
        
        try:
            hora_entrada_int = int(entrada.split(':')[0])
            hora_salida_int = int(salida.split(':')[0])
            
            # Horario nocturno (después de las 22:00 o antes de las 6:00)
            if hora_entrada_int >= 22 or hora_salida_int <= 6:
                return 'Nocturnas'
            
            # Horario de fin de semana o especial (esto requeriría más contexto)
            # Por ahora, clasificar como normales
            return 'Normales'
        
        except:
            return 'Normales'

def procesar_horarios_inteligente(texto: str, mostrar_progreso: bool = True) -> pd.DataFrame:
    """
    Función principal para procesar horarios de forma inteligente
    
    Args:
        texto (str): Texto a procesar
        mostrar_progreso (bool): Si mostrar barra de progreso
    
    Returns:
        pd.DataFrame: DataFrame con horarios procesados
    """
    processor = SmartScheduleProcessor()
    
    if mostrar_progreso:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def callback(progreso, mensaje):
            progress_bar.progress(progreso)
            status_text.text(mensaje)
        
        resultado = processor.procesar_texto_completo(texto, callback)
        
        progress_bar.empty()
        status_text.empty()
    else:
        resultado = processor.procesar_texto_completo(texto)
    
    return resultado

def analizar_patrones_horarios(df_horarios: pd.DataFrame) -> Dict:
    """
    Analiza patrones en los horarios procesados
    
    Args:
        df_horarios (pd.DataFrame): DataFrame con horarios
    
    Returns:
        Dict: Análisis de patrones
    """
    if df_horarios.empty:
        return {'error': 'No hay datos para analizar'}
    
    analisis = {
        'total_registros': len(df_horarios),
        'empleados_unicos': df_horarios['Empleado'].nunique(),
        'fechas_unicas': df_horarios['Fecha'].nunique(),
        'horas_promedio': df_horarios['Horas_Trabajadas'].mean(),
        'horas_total': df_horarios['Horas_Trabajadas'].sum(),
        'tipos_horario': df_horarios['Tipo_Horario'].value_counts().to_dict(),
        'empleado_mas_horas': None,
        'empleado_menos_horas': None
    }
    
    # Análisis por empleado
    if 'Empleado' in df_horarios.columns:
        horas_por_empleado = df_horarios.groupby('Empleado')['Horas_Trabajadas'].sum()
        if not horas_por_empleado.empty:
            analisis['empleado_mas_horas'] = horas_por_empleado.idxmax()
            analisis['empleado_menos_horas'] = horas_por_empleado.idxmin()
    
    return analisis

def mostrar_interface_smart_parser():
    """
    Muestra la interfaz del analizador inteligente en Streamlit
    """
    st.subheader("🧠 Analizador Inteligente de Horarios")
    
    st.info("Esta funcionalidad analiza texto libre y extrae automáticamente información de horarios.")
    
    # Opción 1: Texto manual
    tab1, tab2 = st.tabs(["📝 Texto Manual", "📄 Desde Archivo"])
    
    with tab1:
        texto_input = st.text_area(
            "Pegue aquí el texto con horarios:",
            height=200,
            placeholder="Ejemplo:\nJuan Pérez - 08:00 - 17:00\nMaría García - Entrada: 09:00, Salida: 18:00\n..."
        )
        
        if st.button("🔍 Analizar Texto", type="primary"):
            if texto_input.strip():
                with st.spinner("Analizando texto..."):
                    resultado = procesar_horarios_inteligente(texto_input)
                
                if not resultado.empty:
                    st.success("✅ Análisis completado")
                    
                    # Mostrar resultados
                    st.dataframe(resultado, use_container_width=True)
                    
                    # Análisis de patrones
                    st.subheader("📊 Análisis de Patrones")
                    patrones = analizar_patrones_horarios(resultado)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Registros", patrones['total_registros'])
                    with col2:
                        st.metric("Empleados", patrones['empleados_unicos'])
                    with col3:
                        st.metric("Horas Promedio", f"{patrones['horas_promedio']:.1f}")
                    with col4:
                        st.metric("Total Horas", f"{patrones['horas_total']:.1f}")
                    
                    # Descarga
                    csv_data = resultado.to_csv(index=False)
                    st.download_button(
                        label="📥 Descargar Resultados",
                        data=csv_data,
                        file_name=f"horarios_analizados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("⚠️ No se encontraron horarios en el texto")
            else:
                st.warning("⚠️ Por favor ingrese algún texto para analizar")
    
    with tab2:
        archivo_texto = st.file_uploader(
            "Seleccione un archivo de texto",
            type=['txt', 'csv'],
            help="Archivo con texto plano conteniendo información de horarios"
        )
        
        if archivo_texto:
            if st.button("🔍 Analizar Archivo", type="primary"):
                try:
                    # Leer archivo
                    contenido = archivo_texto.read().decode('utf-8')
                    
                    with st.spinner("Analizando archivo..."):
                        resultado = procesar_horarios_inteligente(contenido)
                    
                    if not resultado.empty:
                        st.success("✅ Archivo analizado exitosamente")
                        st.dataframe(resultado, use_container_width=True)
                        
                        # Descarga
                        csv_data = resultado.to_csv(index=False)
                        st.download_button(
                            label="📥 Descargar Resultados",
                            data=csv_data,
                            file_name=f"horarios_archivo_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("⚠️ No se encontraron horarios en el archivo")
                
                except Exception as e:
                    st.error(f"❌ Error leyendo archivo: {str(e)}")

# Funciones de utilidad adicionales
def validar_formato_horario(horario_str: str) -> bool:
    """
    Valida si una cadena tiene formato de horario válido
    
    Args:
        horario_str (str): Cadena a validar
    
    Returns:
        bool: True si es válido
    """
    patrones = [r'^\d{1,2}:\d{2}$', r'^\d{1,2}\.\d{2}$', r'^\d{1,2}h\d{2}$']
    
    for patron in patrones:
        if re.match(patron, horario_str):
            try:
                # Validar que los números sean correctos
                if ':' in horario_str:
                    hora, minuto = map(int, horario_str.split(':'))
                elif '.' in horario_str:
                    hora, minuto = map(int, horario_str.split('.'))
                elif 'h' in horario_str:
                    hora, minuto = map(int, horario_str.replace('h', ':').split(':'))
                else:
                    return False
                
                return 0 <= hora <= 23 and 0 <= minuto <= 59
            except:
                return False
    
    return False

def normalizar_formato_horario(horario_str: str) -> str:
    """
    Normaliza diferentes formatos de horario a HH:MM
    
    Args:
        horario_str (str): Horario en cualquier formato
    
    Returns:
        str: Horario en formato HH:MM
    """
    # Limpiar espacios
    horario_str = horario_str.strip()
    
    # Convertir diferentes formatos
    if '.' in horario_str:
        horario_str = horario_str.replace('.', ':')
    elif 'h' in horario_str.lower():
        horario_str = horario_str.lower().replace('h', ':')
    
    # Asegurar formato HH:MM
    if ':' in horario_str:
        partes = horario_str.split(':')
        if len(partes) >= 2:
            hora = partes[0].zfill(2)
            minuto = partes[1][:2].zfill(2)
            return f"{hora}:{minuto}"
    
    return horario_str

class EntradaSalidaDetector:
    """Clase para detectar automáticamente entrada y salida"""
    
    def __init__(self):
        self.palabras_entrada = [
            'entrada', 'entry', 'in', 'inicio', 'start', 'llegada', 'ingreso'
        ]
        self.palabras_salida = [
            'salida', 'exit', 'out', 'fin', 'end', 'partida', 'egreso'
        ]
    
    def detectar_tipo(self, texto: str, hora: str, context: List[str] = None) -> str:
        """
        Detecta si una hora es entrada o salida
        
        Args:
            texto: Texto que contiene la hora
            hora: Hora en formato HH:MM
            context: Contexto adicional (líneas anteriores/posteriores)
            
        Returns:
            str: 'Entrada' o 'Salida'
        """
        texto_lower = texto.lower()
        
        # Búsqueda por palabras clave
        for palabra in self.palabras_entrada:
            if palabra in texto_lower:
                return 'Entrada'
        
        for palabra in self.palabras_salida:
            if palabra in texto_lower:
                return 'Salida'
        
        # Detección por hora (heurística)
        try:
            hora_obj = datetime.strptime(hora, '%H:%M').time()
            
            # Antes de las 12:00 probablemente sea entrada
            if hora_obj.hour < 12:
                return 'Entrada'
            # Después de las 15:00 probablemente sea salida
            elif hora_obj.hour >= 15:
                return 'Salida'
            # Entre 12:00 y 15:00 es ambiguo, usar contexto
            else:
                if context:
                    return self._analizar_contexto(context, hora)
                return 'Entrada'  # Por defecto
                
        except Exception:
            return 'Entrada'  # Por defecto
    
    def _analizar_contexto(self, context: List[str], hora: str) -> str:
        """Analiza el contexto para determinar tipo"""
        # Si hay otras horas en el contexto, comparar
        for linea in context:
            parser = SmartTimeParser()
            fecha_horas = parser.extraer_fecha_hora(linea)
            
            for fh in fecha_horas:
                if fh['hora'] != hora:
                    try:
                        hora_ctx = datetime.strptime(fh['hora'], '%H:%M').time()
                        hora_actual = datetime.strptime(hora, '%H:%M').time()
                        
                        # Si hay una hora anterior, esta probablemente sea salida
                        if hora_ctx < hora_actual:
                            return 'Salida'
                        # Si hay una hora posterior, esta probablemente sea entrada
                        elif hora_ctx > hora_actual:
                            return 'Entrada'
                    except:
                        continue
        
        return 'Entrada'  # Por defecto

class DataGrouper:
    """Clase para agrupar datos por empleado y fecha"""
    
    def agrupar_por_empleado_fecha(self, datos: List[Dict]) -> List[Dict]:
        """
        Agrupa datos por empleado y fecha, combinando entradas y salidas
        
        LÓGICA CORREGIDA:
        - Primera hora del día = Entrada
        - Segunda hora del día = Salida
        
        Args:
            datos: Lista de datos con empleado, fecha, hora, tipo
            
        Returns:
            List[Dict]: Datos agrupados
        """
        # Agrupar por empleado y fecha
        grupos = {}
        
        for item in datos:
            clave = f"{item.get('empleado', 'Unknown')}_{item.get('fecha', 'Unknown')}"
            
            if clave not in grupos:
                grupos[clave] = {
                    'empleado': item.get('empleado', 'Unknown'),
                    'fecha': item.get('fecha', 'Unknown'),
                    'horas': [],  # Todas las horas del día
                    'registros': []
                }
            
            grupos[clave]['registros'].append(item)
            grupos[clave]['horas'].append(item.get('hora'))
        
        # Procesar grupos usando lógica: primera hora = entrada, segunda = salida
        resultado = []
        for grupo in grupos.values():
            # Ordenar horas para asegurar el orden correcto
            horas_ordenadas = sorted(set(grupo['horas']))  # Eliminar duplicados y ordenar
            
            # Primera hora = Entrada, Segunda hora = Salida
            entrada_final = horas_ordenadas[0] if len(horas_ordenadas) >= 1 else '08:00'
            
            # Si solo hay UNA hora, significa que falta la salida
            if len(horas_ordenadas) == 1:
                salida_final = '0:00'  # Marcar como faltante
            else:
                salida_final = horas_ordenadas[1]  # Segunda hora
            
            resultado.append({
                'Empleado': grupo['empleado'],
                'Fecha': grupo['fecha'],
                'Entrada': entrada_final,
                'Salida': salida_final,
                'Registros_Originales': len(grupo['registros'])
            })
        
        return resultado
    
    def _obtener_entrada_definitiva(self, entradas: List[str]) -> str:
        """Obtiene la entrada definitiva (primera del día)"""
        if not entradas:
            return '08:00'  # Por defecto
        
        # Ordenar y tomar la primera
        entradas_ordenadas = sorted(entradas)
        return entradas_ordenadas[0]
    
    def _obtener_salida_definitiva(self, salidas: List[str]) -> str:
        """Obtiene la salida definitiva (última del día)"""
        if not salidas:
            return '17:00'  # Por defecto
        
        # Ordenar y tomar la última
        salidas_ordenadas = sorted(salidas)
        return salidas_ordenadas[-1]