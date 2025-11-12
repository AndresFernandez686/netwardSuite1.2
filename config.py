"""
Configuración global para BusinessSuite
"""
import os

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODULES_DIR = os.path.join(BASE_DIR, 'modules')

# Configuración de datos
PAYROLL_DATA_DIR = os.path.join(DATA_DIR, 'payroll')
INVENTORY_DATA_DIR = os.path.join(DATA_DIR, 'inventory')

# Configuración de la aplicación
APP_CONFIG = {
    'title': 'BusinessSuite',
    'version': '1.0',
    'author': 'Desarrollado con GitHub Copilot',
    'description': 'Suite de Aplicaciones de Negocio'
}

# Configuración de usuarios por defecto
DEFAULT_USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "name": "Administrador",
        "permissions": ["inventory", "payroll", "reports", "user_management"]
    },
    "empleado1": {
        "password": "emp123",
        "role": "employee", 
        "name": "Empleado 1",
        "permissions": ["inventory"]
    }
}

# Crear directorios si no existen
def ensure_directories():
    """Asegura que todos los directorios necesarios existan"""
    directories = [
        DATA_DIR,
        PAYROLL_DATA_DIR,
        INVENTORY_DATA_DIR,
        os.path.join(BASE_DIR, 'assets'),
        os.path.join(BASE_DIR, 'shared')
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

if __name__ == "__main__":
    ensure_directories()
    print("✅ Configuración de BusinessSuite completada")
