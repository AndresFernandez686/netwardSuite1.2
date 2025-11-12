"""
Script para reparar el archivo inventario.json corrupto
Elimina anidaciones incorrectas y establece una estructura limpia
"""
import json
import os
from datetime import date

INVENTARIO_FILE = "inventario.json"
BACKUP_FILE = "inventario_backup.json"

def reparar_inventario():
    """Repara la estructura del inventario eliminando anidaciones"""
    
    print("🔧 Iniciando reparación de inventario...")
    
    # Verificar si existe el archivo
    if not os.path.exists(INVENTARIO_FILE):
        print("❌ No se encontró el archivo inventario.json")
        return False
    
    try:
        # Hacer backup del archivo original
        with open(INVENTARIO_FILE, "r", encoding="utf-8") as f:
            data_original = json.load(f)
        
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(data_original, f, ensure_ascii=False, indent=2)
        print(f"✅ Backup creado en {BACKUP_FILE}")
        
        # Extraer datos válidos del archivo corrupto
        productos_extraidos = {
            "T001": {
                "Impulsivo": {},
                "Por Kilos": {},
                "Extras": {}
            },
            "T002": {
                "Impulsivo": {},
                "Por Kilos": {},
                "Extras": {}
            }
        }
        
        # Función recursiva para extraer productos del nivel más profundo
        def extraer_productos(obj, nivel=0):
            """Extrae productos navegando por anidaciones"""
            if isinstance(obj, dict):
                # Si tiene las categorías correctas, es un inventario válido
                if all(k in obj for k in ["Impulsivo", "Por Kilos", "Extras"]):
                    return obj
                
                # Si tiene inventario_por_tienda, seguir navegando
                if "inventario_por_tienda" in obj:
                    return extraer_productos(obj["inventario_por_tienda"], nivel + 1)
                
                # Buscar en cada clave
                for key, value in obj.items():
                    if key in ["T001", "T002"]:
                        resultado = extraer_productos(value, nivel + 1)
                        if resultado:
                            return {key: resultado}
            
            return None
        
        # Intentar extraer datos válidos
        print("🔍 Buscando datos válidos en el archivo corrupto...")
        
        if "inventario_por_tienda" in data_original:
            for tienda_id in ["T001", "T002"]:
                if tienda_id in data_original["inventario_por_tienda"]:
                    datos_tienda = data_original["inventario_por_tienda"][tienda_id]
                    inventario_valido = extraer_productos(datos_tienda)
                    
                    if inventario_valido:
                        # Si encontramos datos válidos, copiarlos
                        for categoria in ["Impulsivo", "Por Kilos", "Extras"]:
                            if categoria in inventario_valido and isinstance(inventario_valido[categoria], dict):
                                productos_extraidos[tienda_id][categoria] = inventario_valido[categoria]
                                print(f"  ✅ Extraídos {len(inventario_valido[categoria])} productos de {categoria} ({tienda_id})")
        
        # Crear estructura limpia y correcta
        estructura_limpia = {
            "inventario_por_tienda": productos_extraidos,
            "inventario_global": {},
            "ultima_fecha_guardado": str(date.today()),
            "configuracion": {
                "tienda_default": "T001",
                "version": "1.6",
                "tiendas": {
                    "T001": {
                        "id": "T001",
                        "nombre": "Seminario",
                        "direccion": "Dirección no especificada",
                        "activa": True,
                        "fecha_creacion": str(date.today())
                    },
                    "T002": {
                        "id": "T002",
                        "nombre": "Mcal Lopez",
                        "direccion": "Dirección no especificada",
                        "activa": True,
                        "fecha_creacion": str(date.today())
                    }
                }
            }
        }
        
        # Guardar estructura limpia
        with open(INVENTARIO_FILE, "w", encoding="utf-8") as f:
            json.dump(estructura_limpia, f, ensure_ascii=False, indent=2)
        
        print("✅ Inventario reparado exitosamente")
        print(f"📊 Estructura limpia guardada en {INVENTARIO_FILE}")
        
        # Mostrar resumen
        print("\n📋 Resumen de productos recuperados:")
        for tienda_id, inventario in productos_extraidos.items():
            print(f"\n  🏪 {tienda_id}:")
            for categoria, productos in inventario.items():
                if productos:
                    print(f"    • {categoria}: {len(productos)} productos")
                    for producto, cantidad in list(productos.items())[:3]:
                        print(f"      - {producto}: {cantidad}")
                    if len(productos) > 3:
                        print(f"      ... y {len(productos) - 3} más")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la reparación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  REPARACIÓN DE INVENTARIO - Netward 1.6")
    print("=" * 60)
    print()
    
    exito = reparar_inventario()
    
    if exito:
        print("\n✅ REPARACIÓN COMPLETADA")
        print("👉 Ahora puedes iniciar la aplicación normalmente")
    else:
        print("\n❌ LA REPARACIÓN FALLÓ")
        print("👉 Revisa el archivo manualmente o contacta soporte")
    
    print()
    input("Presiona ENTER para salir...")
