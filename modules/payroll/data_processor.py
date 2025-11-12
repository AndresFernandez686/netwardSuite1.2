"""
Módulo de procesamiento de datos para BusinessSuite
Versión simplificada y funcional para el cálculo de sueldos
"""
import pandas as pd
import streamlit as st
import io
from datetime import datetime, timedelta
import calculations
calcular_horas_especiales = calculations.calcular_horas_especiales
horas_a_horasminutos = calculations.horas_a_horasminutos
calcular_sueldo_basico = calculations.calcular_sueldo_basico

def validar_archivo_excel(file):
    """
    Valida que el archivo Excel tenga la estructura correcta
    
    Args:
        file: Archivo subido por streamlit
    
    Returns:
        tuple: (is_valid, df_or_error_message)
    """
    try:
        df = pd.read_excel(file)
        
        # Columnas requeridas
        required_columns = ['Empleado', 'Horas_Normales', 'Horas_Especiales', 
                          'Valor_Hora_Normal', 'Valor_Hora_Especial', 'Descuentos']
        
        # Verificar que existan las columnas requeridas
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"Faltan las siguientes columnas: {', '.join(missing_columns)}"
        
        # Verificar que haya datos
        if df.empty:
            return False, "El archivo está vacío"
        
        # Verificar tipos de datos básicos
        for col in ['Horas_Normales', 'Horas_Especiales', 'Valor_Hora_Normal', 'Valor_Hora_Especial', 'Descuentos']:
            if col in df.columns:
                try:
                    pd.to_numeric(df[col], errors='coerce')
                except:
                    return False, f"La columna {col} debe contener solo números"
        
        return True, df
        
    except Exception as e:
        return False, f"Error leyendo el archivo: {str(e)}"

def procesar_datos_excel(df, valor_por_hora, opcion_feriados, dias_feriados, cantidad_feriados):
    """
    Procesa los datos del DataFrame y calcula los sueldos
    
    Args:
        df (DataFrame): DataFrame con los datos de empleados
        valor_por_hora (float): Valor por hora para calcular sueldos
        opcion_feriados (str): Opción de feriados ('personalizado' o 'cantidad')
        dias_feriados (list): Lista de fechas de feriados (si opcion es 'personalizado')
        cantidad_feriados (int): Cantidad de feriados (si opcion es 'cantidad')
    
    Returns:
        tuple: (resultados, total_horas, total_sueldos, total_horas_normales, total_horas_especiales)
    """
    from datetime import datetime, timedelta
    import pandas as pd
    
    # Preparar conjunto de fechas de feriados
    if opcion_feriados == "personalizado":
        fechas_feriados = set(dias_feriados) if dias_feriados else set()
    else:
        fechas_feriados = set()
    
    resultados = []
    total_horas = 0
    total_sueldos = 0
    total_horas_normales = 0
    total_horas_especiales = 0
    
    for index, row in df.iterrows():
        try:
            resultado = procesar_fila_empleado(row, valor_por_hora, fechas_feriados)
            
            if resultado:
                resultados.append(resultado["datos"])
                total_horas += resultado["horas"]
                total_sueldos += resultado["sueldo"]
                total_horas_normales += resultado.get("horas_normales", 0)
                total_horas_especiales += resultado.get("horas_especiales", 0)
            else:
                st.warning(f"⚠️ Fila {index+1} no generó resultado")
            
        except Exception as e:
            st.error(f"❌ Error en la fila {index+2}: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
    
    return resultados, total_horas, total_sueldos, total_horas_normales, total_horas_especiales

def procesar_fila_empleado(row, valor_por_hora, fechas_feriados):
    """
    Procesa una fila individual del DataFrame - VERSIÓN SIMPLIFICADA
    Para PDFs: Solo necesita Empleado, Fecha, Entrada, Salida
    Para Excel: Puede incluir descuentos
    
    Args:
        row: Fila del DataFrame
        valor_por_hora: Valor por hora
        fechas_feriados: Fechas completas específicas de feriados
        
    Returns:
        dict: Resultado del procesamiento con datos, horas y sueldo
    """
    try:
        from datetime import datetime, timedelta
        from modules.payroll.calculations import calcular_horas_especiales, horas_a_horasminutos
        
        # Extraer datos básicos
        fecha = pd.to_datetime(row["Fecha"])
        entrada = pd.to_datetime(str(row["Entrada"])).time()
        salida = pd.to_datetime(str(row["Salida"])).time()

        entrada_dt = datetime.combine(fecha.date(), entrada)
        salida_dt = datetime.combine(fecha.date(), salida)
        
        # Si la salida es menor que la entrada, pasó a la madrugada del día siguiente
        if salida_dt < entrada_dt:
            salida_dt += timedelta(days=1)

        # Calcular horas trabajadas en decimal
        horas_trabajadas_decimal = (salida_dt - entrada_dt).total_seconds() / 3600

        # Calcular horas especiales (20:00-22:00 con 30% extra)
        horas_normales, horas_especiales = calcular_horas_especiales(entrada_dt, salida_dt)
        
        # Verificar si es feriado
        es_feriado = fecha.date() in fechas_feriados
        factor_feriado = 2 if es_feriado else 1

        # Cálculo con horas normales y especiales
        sueldo_normal = horas_normales * valor_por_hora
        sueldo_especial = horas_especiales * valor_por_hora * 1.3  # 30% extra
        sueldo_bruto = (sueldo_normal + sueldo_especial) * factor_feriado

        # Descuentos (solo si existen en el DataFrame - para Excel)
        descuento_inventario = 0
        descuento_caja = 0
        retiro = 0
        
        if "Descuento Inventario" in row.index:
            descuento_inventario = float(row["Descuento Inventario"]) if not pd.isnull(row["Descuento Inventario"]) else 0
        if "Descuento Caja" in row.index:
            descuento_caja = float(row["Descuento Caja"]) if not pd.isnull(row["Descuento Caja"]) else 0
        if "Retiro" in row.index:
            retiro = float(row["Retiro"]) if not pd.isnull(row["Retiro"]) else 0

        sueldo_final = sueldo_bruto - descuento_inventario - descuento_caja - retiro

        # Construir resultado
        datos_fila = {
            "Empleado": str(row["Empleado"]),
            "Fecha": fecha.strftime("%Y-%m-%d"),
            "Entrada": entrada.strftime("%H:%M"),
            "Salida": salida.strftime("%H:%M"),
            "Feriado": "Sí" if es_feriado else "No",
            "Horas Trabajadas (h:mm)": horas_a_horasminutos(horas_trabajadas_decimal),
            "Horas Normales": horas_a_horasminutos(horas_normales),
            "Horas Especiales": horas_a_horasminutos(horas_especiales),
            "Descuento Inventario": descuento_inventario,
            "Descuento Caja": descuento_caja,
            "Retiro": retiro,
            "Sueldo Final": round(sueldo_final, 2)
        }

        return {
            "datos": datos_fila,
            "horas": horas_trabajadas_decimal,
            "sueldo": sueldo_final,
            "horas_normales": horas_normales,
            "horas_especiales": horas_especiales
        }
    
    except Exception as e:
        st.error(f"Error procesando fila: {str(e)}")
        return None

def mostrar_resultados(resultados, total_horas, total_sueldos, total_horas_normales=0, total_horas_especiales=0, valor_por_hora=None, fechas_feriados=None, nombre_archivo=None):
    """
    Muestra los resultados en la interfaz y proporciona descarga
    
    Args:
        resultados (list): Lista de resultados procesados
        total_horas (float): Total de horas trabajadas
        total_sueldos (float): Total de sueldos calculados
        total_horas_normales (float): Total de horas normales trabajadas
        total_horas_especiales (float): Total de horas especiales trabajadas
        valor_por_hora (float): Valor por hora utilizado en cálculos
        fechas_feriados (set): Fechas marcadas como feriados
        nombre_archivo (str): Nombre base para el archivo Excel (opcional)
    """
    from modules.payroll.calculations import horas_a_horasminutos
    
    df_result = pd.DataFrame(resultados)
    
    # Mostrar tabla
    st.subheader("📋 Resultados del Cálculo")
    st.dataframe(df_result, use_container_width=True)

    # Resumen General
    st.subheader("📊 Resumen General")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Registros", len(df_result))
    
    with col2:
        st.metric("Horas Normales", horas_a_horasminutos(total_horas_normales))
    
    with col3:
        st.metric("Horas Especiales", horas_a_horasminutos(total_horas_especiales))
    
    with col4:
        st.metric("Total Horas", horas_a_horasminutos(total_horas))
    
    # Mostrar total de sueldos
    st.subheader("💰 Total a Pagar")
    st.metric("Sueldo Total", f"Gs. {total_sueldos:,.0f}")
    
    # Botón de descarga
    st.subheader("📥 Descargar Resultados")
    
    # Preparar Excel para descarga
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_result.to_excel(writer, sheet_name='Resultados', index=False)
    
    excel_data = output.getvalue()
    
    # Generar nombre de archivo
    fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
    if nombre_archivo:
        nombre_descarga = f"{nombre_archivo.replace('.pdf', '')}_{fecha_actual}.xlsx"
    else:
        nombre_descarga = f"calculo_sueldos_{fecha_actual}.xlsx"
    
    st.download_button(
        label="⬇️ Descargar Excel",
        data=excel_data,
        file_name=nombre_descarga,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def exportar_resultados(df_resultados, filename_prefix="resultados_sueldos"):
    """
    Exporta los resultados a Excel
    
    Args:
        df_resultados (DataFrame): DataFrame con los resultados
        filename_prefix (str): Prefijo para el nombre del archivo
    
    Returns:
        bytes: Archivo Excel en bytes para descarga
    """
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Hoja principal con resultados
        df_resultados.to_excel(writer, sheet_name='Resultados', index=False)
        
        # Hoja de resumen
        resumen = {
            'Concepto': ['Total Empleados', 'Total Horas', 'Total Sueldo Bruto', 'Total Descuentos', 'Total Sueldo Neto'],
            'Valor': [
                len(df_resultados),
                df_resultados['Total_Horas'].sum(),
                df_resultados['Sueldo_Bruto'].sum(),
                df_resultados['Descuentos'].sum(),
                df_resultados['Sueldo_Neto'].sum()
            ]
        }
        
        df_resumen = pd.DataFrame(resumen)
        df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
        
        # Formatear las hojas
        workbook = writer.book
        money_format = workbook.add_format({'num_format': '#,##0'})
        
        # Aplicar formato a columnas monetarias en la hoja de resultados
        worksheet_resultados = writer.sheets['Resultados']
        money_cols = ['Valor_Hora_Normal', 'Valor_Hora_Especial', 'Sueldo_Normal', 
                     'Sueldo_Especial', 'Sueldo_Bruto', 'Descuentos', 'Sueldo_Neto']
        
        for col_name in money_cols:
            if col_name in df_resultados.columns:
                col_num = df_resultados.columns.get_loc(col_name)
                worksheet_resultados.set_column(col_num, col_num, 15, money_format)
    
    output.seek(0)
    return output.getvalue()

def crear_plantilla_excel():
    """
    Crea una plantilla Excel para que los usuarios puedan llenar sus datos
    
    Returns:
        bytes: Archivo Excel plantilla en bytes
    """
    # Datos de ejemplo
    datos_ejemplo = {
        'Empleado': ['Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez'],
        'Horas_Normales': [40.0, 35.5, 42.0, 38.0],
        'Horas_Especiales': [5.0, 8.0, 3.5, 6.0],
        'Valor_Hora_Normal': [15000, 16000, 14500, 15500],
        'Valor_Hora_Especial': [18000, 19200, 17400, 18600],
        'Descuentos': [50000, 45000, 30000, 40000]
    }
    
    df_plantilla = pd.DataFrame(datos_ejemplo)
    
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_plantilla.to_excel(writer, sheet_name='Empleados', index=False)
        
        # Agregar hoja de instrucciones
        instrucciones = {
            'Campo': ['Empleado', 'Horas_Normales', 'Horas_Especiales', 'Valor_Hora_Normal', 'Valor_Hora_Especial', 'Descuentos'],
            'Descripción': [
                'Nombre completo del empleado',
                'Horas trabajadas en horario normal',
                'Horas trabajadas en horario especial/nocturno',
                'Valor por hora en horario normal (en guaraníes)',
                'Valor por hora en horario especial (en guaraníes)',
                'Total de descuentos (IPS, adelantos, multas, etc.)'
            ],
            'Tipo': ['Texto', 'Número decimal', 'Número decimal', 'Número entero', 'Número entero', 'Número entero'],
            'Ejemplo': ['Juan Pérez', '40.0', '5.0', '15000', '18000', '50000']
        }
        
        df_instrucciones = pd.DataFrame(instrucciones)
        df_instrucciones.to_excel(writer, sheet_name='Instrucciones', index=False)
        
        # Formatear
        workbook = writer.book
        worksheet_empleados = writer.sheets['Empleados']
        worksheet_instrucciones = writer.sheets['Instrucciones']
        
        # Formato para números
        money_format = workbook.add_format({'num_format': '#,##0'})
        decimal_format = workbook.add_format({'num_format': '0.0'})
        
        # Aplicar formato a la hoja de empleados
        worksheet_empleados.set_column('B:C', 12, decimal_format)  # Horas
        worksheet_empleados.set_column('D:F', 15, money_format)     # Valores monetarios
        
        # Autoajustar ancho de columnas en instrucciones
        worksheet_instrucciones.set_column('A:D', 20)
    
    output.seek(0)
    return output.getvalue()