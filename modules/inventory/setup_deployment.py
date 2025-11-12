#!/usr/bin/env python3
"""
Script de configuración para deployment de Netw@rd
Verifica que todo esté listo para Streamlit Cloud
"""

import os
import sys
import json
from pathlib import Path

def check_file_exists(file_path, description):
    """Verifica si un archivo existe"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - NO ENCONTRADO")
        return False

def check_directory_structure():
    """Verifica la estructura de directorios"""
    print("📁 VERIFICANDO ESTRUCTURA DE DIRECTORIOS")
    print("=" * 50)
    
    required_dirs = [
        "core",
        "ui", 
        "ui/admin",
        "ui/employee", 
        "ui/components",
        "data",
        "utils",
        "config",
        ".streamlit"
    ]
    
    all_good = True
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ - NO ENCONTRADO")
            all_good = False
    
    return all_good

def check_required_files():
    """Verifica archivos requeridos para deployment"""
    print("\n📄 VERIFICANDO ARCHIVOS REQUERIDOS")
    print("=" * 50)
    
    required_files = [
        ("main.py", "Aplicación principal"),
        ("requirements.txt", "Dependencias"),
        ("README.md", "Documentación"),
        (".streamlit/config.toml", "Configuración Streamlit"),
        ("inventario.json", "Datos de inventario"),
        ("historial_inventario.json", "Historial"),
    ]
    
    all_good = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    return all_good

def check_json_files():
    """Verifica que los archivos JSON sean válidos"""
    print("\n🔍 VERIFICANDO ARCHIVOS JSON")
    print("=" * 50)
    
    json_files = ["inventario.json", "historial_inventario.json"]
    all_good = True
    
    for json_file in json_files:
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"✅ {json_file}: JSON válido")
            except json.JSONDecodeError as e:
                print(f"❌ {json_file}: JSON inválido - {e}")
                all_good = False
        else:
            # Crear archivo JSON básico si no existe
            if json_file == "inventario.json":
                default_data = {"Impulsivo": {}, "Cigarrillos": {}, "Cervezas": {}}
            else:
                default_data = []
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
            print(f"🔧 {json_file}: Creado archivo por defecto")
    
    return all_good

def test_imports():
    """Prueba las importaciones principales"""
    print("\n🧪 PROBANDO IMPORTACIONES")
    print("=" * 50)
    
    try:
        import main
        print("✅ main.py: Importación exitosa")
        return True
    except Exception as e:
        print(f"❌ main.py: Error de importación - {e}")
        return False

def create_deployment_info():
    """Crea archivo con información de deployment"""
    deployment_info = {
        "name": "Netw@rd v1.5",
        "description": "Sistema de gestión de inventario modular",
        "main_file": "main.py",
        "python_version": "3.9+",
        "streamlit_version": "1.28.0+",
        "deployment_ready": True,
        "urls": {
            "github": "https://github.com/AndresFernandez686/Netward1.4",
            "streamlit_cloud": "https://share.streamlit.io"
        }
    }
    
    with open("deployment_info.json", 'w', encoding='utf-8') as f:
        json.dump(deployment_info, f, ensure_ascii=False, indent=2)
    
    print("\n📋 INFORMACIÓN DE DEPLOYMENT")
    print("=" * 50)
    print(f"✅ deployment_info.json creado")

def main():
    """Función principal de verificación"""
    print("🚀 NETW@RD DEPLOYMENT CHECKER")
    print("=" * 50)
    print("Verificando que el proyecto esté listo para Streamlit Cloud...")
    print()
    
    checks = [
        check_directory_structure(),
        check_required_files(),
        check_json_files(),
        test_imports()
    ]
    
    create_deployment_info()
    
    print("\n🎯 RESULTADO FINAL")
    print("=" * 50)
    
    if all(checks):
        print("🎉 ¡PROYECTO LISTO PARA DEPLOYMENT!")
        print()
        print("📋 PRÓXIMOS PASOS:")
        print("1. Sube el código a GitHub")
        print("2. Ve a https://share.streamlit.io") 
        print("3. Conecta tu repositorio GitHub")
        print("4. Selecciona main.py como archivo principal")
        print("5. ¡Despliega tu aplicación!")
        print()
        print("🌐 URLs importantes:")
        print("   GitHub: https://github.com/AndresFernandez686/Netward1.4")
        print("   Streamlit Cloud: https://share.streamlit.io")
    else:
        print("⚠️  HAY PROBLEMAS QUE CORREGIR")
        print("   Revisa los errores mostrados arriba")
        print("   Ejecuta este script nuevamente después de corregir")
    
    return all(checks)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)