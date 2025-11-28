import os
import json
from datetime import date

INVENTARIO_FILE = "inventario.json"
HISTORIAL_FILE = "historial_inventario.json"
CATALOGO_DELIVERY_FILE = "catalogo_delivery.json"
VENTAS_DELIVERY_FILE = "ventas_delivery.json"

def migrar_estructura_inventario(inventario):
    """Migra inventario de estructura antigua a nueva estructura"""
    if not isinstance(inventario, dict):
        return {"Impulsivo": {}, "Por Kilos": {}, "Extras": {}}
    
    for categoria in ["Impulsivo", "Extras"]:
        if categoria in inventario and isinstance(inventario[categoria], dict):
            for producto, valor in list(inventario[categoria].items()):
                if isinstance(valor, (int, float)):
                    # Convertir estructura antigua (número) a nueva (bultos/unidad)
                    inventario[categoria][producto] = {
                        "bultos": int(valor),
                        "unidad": 0
                    }
    
    if "Por Kilos" in inventario and isinstance(inventario["Por Kilos"], dict):
        for producto, valor in list(inventario["Por Kilos"].items()):
            if isinstance(valor, (int, float)):
                # Convertir estructura antigua (número) a nueva (4 columnas)
                inventario["Por Kilos"][producto] = {
                    "cajas_cerradas": 0,
                    "cajas_abiertas": 1 if valor > 0 else 0,
                    "kgs_cajas_abiertas": float(valor)
                }
    
    return inventario

def cargar_inventario(tienda_id=None, fecha_carga=None):
    """Carga inventario específico de una tienda - SIEMPRE carga lo último guardado"""
    productos_base = {
        "Impulsivo": {},
        "Por Kilos": {},
        "Extras": {}
    }
    
    if os.path.exists(INVENTARIO_FILE):
        with open(INVENTARIO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            if tienda_id:
                print(f"🔍 Cargando inventario para tienda {tienda_id}")
                
                # Cargar inventario específico de la tienda - SIN VALIDAR FECHAS
                inventario_tiendas = data.get("inventario_por_tienda", {})
                inventario = inventario_tiendas.get(tienda_id, productos_base.copy())
                
                # Migrar datos antiguos a nueva estructura automáticamente
                inventario = migrar_estructura_inventario(inventario)
                
                # Debug: contar productos cargados
                total_productos = sum(
                    len(cat) if isinstance(cat, dict) else 0 
                    for cat in inventario.values() 
                    if isinstance(cat, dict)
                )
                print(f"✅ Inventario cargado: {total_productos} productos en tienda {tienda_id}")
                
                return inventario
            else:
                # Cargar inventario global (para compatibilidad)
                return data.get("inventario_global", productos_base.copy())
    
    print(f"⚠️ Archivo {INVENTARIO_FILE} no existe, retornando estructura vacía")
    return productos_base.copy()

def guardar_inventario(inventario, tienda_id=None, fecha_carga=None):
    """Guarda inventario - ACUMULATIVO Y SIMPLE, sin validación de fechas"""
    try:
        fecha_str = str(date.today())
        
        # Cargar datos existentes del archivo
        if os.path.exists(INVENTARIO_FILE):
            with open(INVENTARIO_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {
                "inventario_por_tienda": {},
                "inventario_global": {},
                "ultima_fecha_guardado": fecha_str
            }
        
        # Verificar y limpiar estructura anidada incorrecta (fix para datos corruptos)
        if "inventario_por_tienda" in data:
            inventario_tiendas = data["inventario_por_tienda"]
            # Verificar si hay anidación incorrecta
            for tid in list(inventario_tiendas.keys()):
                if isinstance(inventario_tiendas[tid], dict):
                    # Si la estructura de la tienda tiene "inventario_por_tienda" dentro, está mal
                    if "inventario_por_tienda" in inventario_tiendas[tid]:
                        # Extraer el inventario correcto del nivel más profundo
                        try:
                            # Navegar hasta el nivel más profundo
                            temp = inventario_tiendas[tid]
                            while "inventario_por_tienda" in temp:
                                temp = temp["inventario_por_tienda"][tid]
                            # Ahora temp debería tener Impulsivo, Por Kilos, Extras
                            if all(k in temp for k in ["Impulsivo", "Por Kilos", "Extras"]):
                                inventario_tiendas[tid] = temp
                        except:
                            # Si falla, inicializar vacío
                            inventario_tiendas[tid] = {
                                "Impulsivo": {},
                                "Por Kilos": {},
                                "Extras": {}
                            }
            data["inventario_por_tienda"] = inventario_tiendas
        
        # Inicializar fechas_por_tienda si no existe
        if "fechas_por_tienda" not in data:
            data["fechas_por_tienda"] = {}
        
        if tienda_id:
            # Asegurar que existe la estructura base
            if "inventario_por_tienda" not in data:
                data["inventario_por_tienda"] = {}
            
            # Obtener o crear inventario actual de la tienda
            if tienda_id not in data["inventario_por_tienda"]:
                data["inventario_por_tienda"][tienda_id] = {
                    "Impulsivo": {},
                    "Por Kilos": {},
                    "Extras": {}
                }
            
            inventario_actual = data["inventario_por_tienda"][tienda_id]
            
            # Actualizar ACUMULATIVAMENTE cada categoría
            for categoria in ["Impulsivo", "Por Kilos", "Extras"]:
                if categoria not in inventario_actual:
                    inventario_actual[categoria] = {}
                
                if categoria in inventario and isinstance(inventario[categoria], dict):
                    # Actualizar/agregar productos nuevos
                    for producto, cantidad in inventario[categoria].items():
                        inventario_actual[categoria][producto] = cantidad
                        print(f"💾 Guardando: {categoria} -> {producto} = {cantidad}")
            
            # Guardar el inventario actualizado
            data["inventario_por_tienda"][tienda_id] = inventario_actual
            
            # Debug: verificar que se guardó correctamente
            productos_guardados = sum(len(cat.values()) if isinstance(cat, dict) else 0 for cat in inventario_actual.values() if isinstance(cat, dict))
            print(f"✅ Total guardado: {productos_guardados} productos para tienda {tienda_id}")
        else:
            # Guardar inventario global (para compatibilidad)
            data["inventario_global"] = inventario
        
        # Actualizar fecha de guardado general
        data["ultima_fecha_guardado"] = fecha_str
        
        # Guardar en archivo
        with open(INVENTARIO_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Archivo guardado exitosamente en {INVENTARIO_FILE}")
        return True
            
    except Exception as e:
        print(f"❌ Error guardando inventario: {e}")
        import traceback
        traceback.print_exc()
        return False

def guardar_historial(fecha, usuario, categoria, producto, cantidad, modo, tipo_inventario="Diario", tienda_id=None):
    """Guarda un registro detallado del movimiento de inventario."""
    # Crear registro con tipo de inventario explícito y tienda
    registro = {
        "fecha": str(fecha),
        "usuario": usuario,
        "categoria": categoria,
        "producto": producto,
        "cantidad": cantidad,
        "modo": modo,
        "tipo_inventario": tipo_inventario,
        "tienda_id": tienda_id or "T001"  # Default por compatibilidad
    }
    historial = []
    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
            historial = json.load(f)
    historial.append(registro)
    with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)

def cargar_historial(tienda_id=None):
    """Carga historial global o filtrado por tienda"""
    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
            historial_completo = json.load(f)
            
        if tienda_id:
            # Filtrar por tienda específica
            return [registro for registro in historial_completo 
                   if registro.get("tienda_id") == tienda_id]
        else:
            # Retornar historial completo
            return historial_completo
    return []

def cargar_catalogo_delivery():
    if os.path.exists(CATALOGO_DELIVERY_FILE):
        with open(CATALOGO_DELIVERY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_catalogo_delivery(catalogo):
    with open(CATALOGO_DELIVERY_FILE, "w", encoding="utf-8") as f:
        json.dump(catalogo, f, ensure_ascii=False, indent=2)

def guardar_venta_delivery(usuario, venta):
    hoy = str(date.today())
    registro = {
        "fecha": hoy,
        "usuario": usuario,
        "venta": venta
    }
    ventas = []
    if os.path.exists(VENTAS_DELIVERY_FILE):
        with open(VENTAS_DELIVERY_FILE, "r", encoding="utf-8") as f:
            ventas = json.load(f)
    ventas.append(registro)
    with open(VENTAS_DELIVERY_FILE, "w", encoding="utf-8") as f:
        json.dump(ventas, f, ensure_ascii=False, indent=2)

def cargar_ventas_delivery():
    if os.path.exists(VENTAS_DELIVERY_FILE):
        with open(VENTAS_DELIVERY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
