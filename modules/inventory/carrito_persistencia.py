# Sistema de Persistencia del Carrito Temporal
# Soluciona el problema de pérdida de datos al cerrar sesión accidentalmente

import json
import os
from datetime import datetime, date
from typing import Dict, List, Any, Optional

# Archivo donde se almacenarán los carritos temporales
CARRITOS_FILE = "carritos_temporales.json"

class CarritoPersistencia:
    """
    Maneja la persistencia de carritos temporales por usuario y tienda.
    Permite que los datos del carrito sobrevivan al cierre de sesión.
    """
    
    def __init__(self):
        self.archivo_carritos = CARRITOS_FILE
        self._asegurar_archivo_existe()
    
    def _asegurar_archivo_existe(self):
        """Crea el archivo de carritos si no existe"""
        if not os.path.exists(self.archivo_carritos):
            data_inicial = {
                "version": "1.0",
                "carritos": {},
                "ultima_actualizacion": datetime.now().isoformat()
            }
            with open(self.archivo_carritos, 'w', encoding='utf-8') as f:
                json.dump(data_inicial, f, indent=2, ensure_ascii=False)
    
    def _cargar_datos(self) -> Dict[str, Any]:
        """Carga todos los datos de carritos desde el archivo"""
        try:
            with open(self.archivo_carritos, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Si hay error, recrear archivo
            self._asegurar_archivo_existe()
            with open(self.archivo_carritos, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def _guardar_datos(self, data: Dict[str, Any]) -> bool:
        """Guarda todos los datos de carritos en el archivo"""
        try:
            data["ultima_actualizacion"] = datetime.now().isoformat()
            with open(self.archivo_carritos, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando carritos: {e}")
            return False
    
    def _generar_clave_carrito(self, usuario: str, tienda_id: str, fecha: str) -> str:
        """Genera clave única para identificar un carrito específico"""
        return f"{usuario}_{tienda_id}_{fecha}"
    
    def guardar_carrito(self, usuario: str, tienda_id: str, fecha: date, carrito: List[Dict]) -> bool:
        """
        Guarda el carrito temporal para un usuario, tienda y fecha específicos
        
        Args:
            usuario: Nombre del usuario
            tienda_id: ID de la tienda (ej: "T001")
            fecha: Fecha del carrito
            carrito: Lista de productos en el carrito
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            data = self._cargar_datos()
            fecha_str = fecha.strftime("%Y-%m-%d") if isinstance(fecha, date) else str(fecha)
            clave_carrito = self._generar_clave_carrito(usuario, tienda_id, fecha_str)
            
            # Crear estructura del carrito con metadatos
            carrito_completo = {
                "usuario": usuario,
                "tienda_id": tienda_id,
                "fecha": fecha_str,
                "productos": carrito,
                "total_productos": len(carrito),
                "ultima_modificacion": datetime.now().isoformat(),
                "activo": True
            }
            
            # Guardar en la estructura principal
            data["carritos"][clave_carrito] = carrito_completo
            
            return self._guardar_datos(data)
            
        except Exception as e:
            print(f"Error guardando carrito para {usuario}: {e}")
            return False
    
    def cargar_carrito(self, usuario: str, tienda_id: str, fecha: date) -> List[Dict]:
        """
        Carga el carrito temporal para un usuario, tienda y fecha específicos
        
        Args:
            usuario: Nombre del usuario
            tienda_id: ID de la tienda
            fecha: Fecha del carrito
            
        Returns:
            List[Dict]: Lista de productos del carrito, vacía si no existe
        """
        try:
            data = self._cargar_datos()
            fecha_str = fecha.strftime("%Y-%m-%d") if isinstance(fecha, date) else str(fecha)
            clave_carrito = self._generar_clave_carrito(usuario, tienda_id, fecha_str)
            
            if clave_carrito in data["carritos"]:
                carrito_data = data["carritos"][clave_carrito]
                
                # Verificar que esté activo y sea de la fecha correcta
                if carrito_data.get("activo", True) and carrito_data.get("fecha") == fecha_str:
                    return carrito_data.get("productos", [])
            
            return []
            
        except Exception as e:
            print(f"Error cargando carrito para {usuario}: {e}")
            return []
    
    def limpiar_carrito(self, usuario: str, tienda_id: str, fecha: date) -> bool:
        """
        Marca un carrito como inactivo (limpiado)
        
        Args:
            usuario: Nombre del usuario
            tienda_id: ID de la tienda
            fecha: Fecha del carrito
            
        Returns:
            bool: True si se limpió exitosamente
        """
        try:
            data = self._cargar_datos()
            fecha_str = fecha.strftime("%Y-%m-%d") if isinstance(fecha, date) else str(fecha)
            clave_carrito = self._generar_clave_carrito(usuario, tienda_id, fecha_str)
            
            if clave_carrito in data["carritos"]:
                data["carritos"][clave_carrito]["activo"] = False
                data["carritos"][clave_carrito]["fecha_limpieza"] = datetime.now().isoformat()
                return self._guardar_datos(data)
            
            return True  # Si no existe, consideramos que ya está "limpio"
            
        except Exception as e:
            print(f"Error limpiando carrito para {usuario}: {e}")
            return False
    
    def obtener_resumen_carritos(self, usuario: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene un resumen de todos los carritos activos
        
        Args:
            usuario: Si se especifica, filtrar solo por este usuario
            
        Returns:
            Dict con estadísticas de carritos
        """
        try:
            data = self._cargar_datos()
            carritos_activos = []
            total_productos = 0
            
            for clave, carrito in data["carritos"].items():
                if carrito.get("activo", True):
                    if usuario is None or carrito.get("usuario") == usuario:
                        carritos_activos.append({
                            "clave": clave,
                            "usuario": carrito.get("usuario"),
                            "tienda_id": carrito.get("tienda_id"),
                            "fecha": carrito.get("fecha"),
                            "total_productos": carrito.get("total_productos", 0),
                            "ultima_modificacion": carrito.get("ultima_modificacion")
                        })
                        total_productos += carrito.get("total_productos", 0)
            
            return {
                "carritos_activos": len(carritos_activos),
                "total_productos": total_productos,
                "detalles": carritos_activos
            }
            
        except Exception as e:
            print(f"Error obteniendo resumen de carritos: {e}")
            return {"carritos_activos": 0, "total_productos": 0, "detalles": []}
    
    def limpiar_carritos_antiguos(self, dias_antiguedad: int = 7) -> int:
        """
        Limpia carritos más antiguos que el número de días especificado
        
        Args:
            dias_antiguedad: Número de días para considerar un carrito como antiguo
            
        Returns:
            int: Número de carritos limpiados
        """
        try:
            from datetime import timedelta
            
            data = self._cargar_datos()
            fecha_limite = datetime.now() - timedelta(days=dias_antiguedad)
            carritos_eliminados = 0
            
            claves_a_eliminar = []
            
            for clave, carrito in data["carritos"].items():
                try:
                    fecha_carrito = datetime.fromisoformat(carrito.get("ultima_modificacion", ""))
                    if fecha_carrito < fecha_limite:
                        claves_a_eliminar.append(clave)
                except:
                    # Si no se puede parsear la fecha, eliminar por seguridad
                    claves_a_eliminar.append(clave)
            
            # Eliminar carritos antiguos
            for clave in claves_a_eliminar:
                del data["carritos"][clave]
                carritos_eliminados += 1
            
            if carritos_eliminados > 0:
                self._guardar_datos(data)
            
            return carritos_eliminados
            
        except Exception as e:
            print(f"Error limpiando carritos antiguos: {e}")
            return 0

# Instancia global del gestor de persistencia
carrito_persistencia = CarritoPersistencia()