"""
Módulo de cálculos para la aplicación de sueldos
Contiene funciones para cálculo de horas y conversiones
"""
from datetime import datetime, timedelta

def calcular_horas_especiales(entrada_dt, salida_dt):
    """
    Calcula las horas normales y especiales trabajadas.
    Horas especiales son las trabajadas entre 20:00 y 22:00
    
    Args:
        entrada_dt (datetime): Hora de entrada
        salida_dt (datetime): Hora de salida
    
    Returns:
        tuple: (horas_normales, horas_especiales)
    """
    # Calcular total de horas trabajadas
    total_horas = (salida_dt - entrada_dt).total_seconds() / 3600
    
    # Calcular horas especiales (20:00 - 22:00)
    inicio_especial = entrada_dt.replace(hour=20, minute=0, second=0)
    fin_especial = entrada_dt.replace(hour=22, minute=0, second=0)
    
    inicio_interseccion = max(entrada_dt, inicio_especial)
    fin_interseccion = min(salida_dt, fin_especial)
    
    if inicio_interseccion >= fin_interseccion:
        horas_especiales = 0
    else:
        horas_especiales = (fin_interseccion - inicio_interseccion).total_seconds() / 3600
    
    # Horas normales = total - especiales
    horas_normales = total_horas - horas_especiales
    
    return horas_normales, horas_especiales

def horas_a_horasminutos(horas):
    """
    Convierte horas decimales a formato horas:minutos
    
    Args:
        horas (float): Horas en formato decimal
    
    Returns:
        str: Horas en formato "HH:MM"
    """
    horas_int = int(horas)
    minutos = int(round((horas - horas_int) * 60))
    if minutos >= 60:
        horas_int += minutos // 60
        minutos = minutos % 60
    return f"{horas_int}:{minutos:02d}"

def calcular_sueldo_basico(horas_normales, horas_especiales, valor_hora_normal, valor_hora_especial=None):
    """
    Calcula el sueldo básico basado en horas trabajadas
    
    Args:
        horas_normales (float): Horas normales trabajadas
        horas_especiales (float): Horas especiales trabajadas
        valor_hora_normal (float): Valor por hora normal
        valor_hora_especial (float): Valor por hora especial (opcional)
    
    Returns:
        dict: Diccionario con desglose del sueldo
    """
    if valor_hora_especial is None:
        valor_hora_especial = valor_hora_normal * 1.2  # 20% extra por defecto
    
    sueldo_normal = horas_normales * valor_hora_normal
    sueldo_especial = horas_especiales * valor_hora_especial
    sueldo_bruto = sueldo_normal + sueldo_especial
    
    return {
        'horas_normales': horas_normales,
        'horas_especiales': horas_especiales,
        'valor_hora_normal': valor_hora_normal,
        'valor_hora_especial': valor_hora_especial,
        'sueldo_normal': sueldo_normal,
        'sueldo_especial': sueldo_especial,
        'sueldo_bruto': sueldo_bruto,
        'total_horas': horas_normales + horas_especiales
    }

def aplicar_descuentos(sueldo_bruto, descuentos_dict):
    """
    Aplica descuentos al sueldo bruto
    
    Args:
        sueldo_bruto (float): Sueldo bruto antes de descuentos
        descuentos_dict (dict): Diccionario con tipos y montos de descuentos
    
    Returns:
        dict: Diccionario con sueldo neto y desglose de descuentos
    """
    total_descuentos = sum(descuentos_dict.values())
    sueldo_neto = sueldo_bruto - total_descuentos
    
    return {
        'sueldo_bruto': sueldo_bruto,
        'descuentos': descuentos_dict,
        'total_descuentos': total_descuentos,
        'sueldo_neto': sueldo_neto
    }