"""
Utilidades compartidas para BusinessSuite
"""
import os
import sys

def setup_paths():
    """Configura los paths para que los módulos puedan encontrar sus dependencias"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Agregar paths necesarios
    paths_to_add = [
        base_dir,
        os.path.join(base_dir, 'modules'),
        os.path.join(base_dir, 'modules', 'payroll'),
        os.path.join(base_dir, 'modules', 'inventory'),
        os.path.join(base_dir, 'shared'),
        os.path.join(base_dir, 'data')
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.append(path)

def get_data_path(module_name, filename):
    """Obtiene la ruta correcta para archivos de datos"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'data', module_name, filename)

def ensure_data_directory(module_name):
    """Asegura que el directorio de datos del módulo exista"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data', module_name)
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_module_path(module_name):
    """Obtiene la ruta del módulo"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'modules', module_name)

# Función de validación numérica crítica para evitar errores int.step
def validar_numero(valor_str, nombre_campo="valor"):
    """
    Valida y convierte un string a número, evitando errores int.step
    
    Args:
        valor_str: String a convertir
        nombre_campo: Nombre del campo para mensajes de error
    
    Returns:
        tuple: (es_valido, valor_o_mensaje_error)
    """
    if not valor_str:
        return False, f"{nombre_campo} no puede estar vacío"
    
    try:
        # Convertir a string por si acaso
        valor_str = str(valor_str)
        
        # Limpiar espacios
        valor_limpio = valor_str.strip()
        
        # Si está vacío después de limpiar
        if not valor_limpio:
            return False, f"{nombre_campo} no puede estar vacío"
        
        # Intentar convertir a float
        valor_numerico = float(valor_limpio)
        
        # Validar que no sea negativo
        if valor_numerico < 0:
            return False, f"{nombre_campo} no puede ser negativo"
        
        return True, valor_numerico
        
    except ValueError:
        return False, f"{nombre_campo} debe ser un número válido"
    except Exception as e:
        return False, f"Error en {nombre_campo}: {str(e)}"

# Funciones de conversión de datos para Excel y CSV
import pandas as pd
import io

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convierte un DataFrame a bytes en formato CSV"""
    return df.to_csv(index=False).encode("utf-8")

def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Convierte un DataFrame a bytes en formato Excel (xlsx)"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# Configurar paths automáticamente al importar
setup_paths()