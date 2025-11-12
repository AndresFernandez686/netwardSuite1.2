# Script de Limpieza de Archivos Duplicados - Netward 1.8
# Ejecutar para eliminar archivos duplicados y limpiar la estructura del proyecto

import os
import shutil
from pathlib import Path

def limpiar_archivos_duplicados():
    """
    Elimina archivos duplicados identificados en el análisis del proyecto
    """
    print("🧹 Iniciando limpieza de archivos duplicados...")
    
    # Directorio base del proyecto
    base_dir = Path(".")
    
    # Lista de archivos/carpetas duplicados a eliminar
    archivos_a_eliminar = [
        # Archivos de UI duplicados
        "ui/employee/inventory_ui.py",
        "ui/employee/inventory_ui_old.py", 
        "ui/employee/delivery_ui.py",
        
        # Archivos de persistencia duplicados
        "data/persistence.py",
        
        # Archivos de modelos duplicados (si existen)
        "core/data_models.py",
        "core/inventory_manager.py", 
        "core/inventory_types.py",
        
        # Archivos de componentes no utilizados
        "ui/components/widgets.py",
        "ui/factory.py",
        
        # Directorio de historial duplicado
        "data/history.py"
    ]
    
    # Carpetas vacías a eliminar después
    carpetas_a_verificar = [
        "ui/employee",
        "ui/admin", 
        "ui/components",
        "core",
        "data",
        "utils"
    ]
    
    archivos_eliminados = 0
    carpetas_eliminadas = 0
    
    # Eliminar archivos duplicados
    for archivo in archivos_a_eliminar:
        archivo_path = base_dir / archivo
        if archivo_path.exists():
            try:
                if archivo_path.is_file():
                    archivo_path.unlink()
                    print(f"✅ Eliminado archivo: {archivo}")
                    archivos_eliminados += 1
                else:
                    print(f"⚠️  No es un archivo: {archivo}")
            except Exception as e:
                print(f"❌ Error eliminando {archivo}: {e}")
        else:
            print(f"ℹ️  No existe: {archivo}")
    
    # Verificar y eliminar carpetas vacías
    for carpeta in reversed(carpetas_a_verificar):  # Reversed para eliminar subcarpetas primero
        carpeta_path = base_dir / carpeta
        if carpeta_path.exists() and carpeta_path.is_dir():
            try:
                # Verificar si la carpeta está vacía o solo contiene __init__.py
                contenido = list(carpeta_path.iterdir())
                archivos_importantes = [f for f in contenido if f.name != "__init__.py" and f.name != "__pycache__"]
                
                if not archivos_importantes:
                    shutil.rmtree(carpeta_path)
                    print(f"✅ Eliminada carpeta vacía: {carpeta}")
                    carpetas_eliminadas += 1
                else:
                    print(f"ℹ️  Carpeta no vacía, conservada: {carpeta}")
            except Exception as e:
                print(f"❌ Error eliminando carpeta {carpeta}: {e}")
    
    print(f"\n📊 Resumen de limpieza:")
    print(f"   - Archivos eliminados: {archivos_eliminados}")
    print(f"   - Carpetas eliminadas: {carpetas_eliminadas}")
    print(f"\n✅ Limpieza completada!")

def verificar_archivos_principales():
    """
    Verifica que los archivos principales del proyecto estén presentes
    """
    print("\n🔍 Verificando archivos principales...")
    
    archivos_principales = [
        "main.py",
        "ui_empleado.py", 
        "ui_admin.py",
        "auth.py",
        "persistencia.py",
        "carrito_persistencia.py",
        "config_tiendas.py",
        "stock_alerts.py",
        "requirements.txt"
    ]
    
    faltantes = []
    for archivo in archivos_principales:
        if not Path(archivo).exists():
            faltantes.append(archivo)
        else:
            print(f"✅ {archivo}")
    
    if faltantes:
        print(f"\n⚠️  Archivos faltantes:")
        for archivo in faltantes:
            print(f"   - {archivo}")
    else:
        print(f"\n✅ Todos los archivos principales están presentes")

def mostrar_estructura_limpia():
    """
    Muestra la estructura limpia del proyecto
    """
    print("\n📁 Estructura del proyecto después de la limpieza:")
    print("""
Netward1.7/
├── main.py                    # Aplicación principal
├── auth.py                    # Sistema de autenticación
├── ui_empleado.py            # UI para empleados (mejorada)
├── ui_admin.py               # UI para administradores  
├── persistencia.py           # Sistema de persistencia principal
├── carrito_persistencia.py   # Sistema de persistencia del carrito (NUEVO)
├── config_tiendas.py         # Configuración de tiendas
├── stock_alerts.py           # Sistema de alertas de stock
├── requirements.txt          # Dependencias
├── inventario.json           # Datos de inventario
├── carritos_temporales.json  # Carritos guardados (se crea automáticamente)
├── historial_inventario.json # Historial de movimientos
└── MEJORAS_PERSISTENCIA_CARRITO.md # Documentación de mejoras
    """)

if __name__ == "__main__":
    print("🚀 Script de Limpieza - Netward 1.8")
    print("=" * 50)
    
    # Confirmar antes de proceder
    respuesta = input("\n¿Desea proceder con la limpieza de archivos duplicados? (s/N): ")
    
    if respuesta.lower() in ['s', 'si', 'yes', 'y']:
        limpiar_archivos_duplicados()
        verificar_archivos_principales() 
        mostrar_estructura_limpia()
        print("\n🎉 ¡Proyecto limpio y optimizado!")
    else:
        print("\n❌ Limpieza cancelada por el usuario")
        verificar_archivos_principales()  # Solo verificar sin limpiar