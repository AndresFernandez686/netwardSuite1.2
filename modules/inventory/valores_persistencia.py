# Sistema de Persistencia de Valores de Formularios
# Mantiene los valores de inputs por 1 día para evitar recargarlos

import json
import os
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional

VALORES_FILE = "valores_formularios.json"

class ValoresPersistencia:
    """
    Maneja la persistencia de valores de formularios por usuario y tienda.
    Los valores se mantienen por 1 día para facilitar la carga de inventario.
    """
    
    def __init__(self):
        self.archivo_valores = VALORES_FILE
        self._asegurar_archivo_existe()
    
    def _asegurar_archivo_existe(self):
        """Crea el archivo de valores si no existe"""
        if not os.path.exists(self.archivo_valores):
            data_inicial = {
                "version": "1.0",
                "valores": {},
                "ultima_actualizacion": datetime.now().isoformat()
            }
            with open(self.archivo_valores, 'w', encoding='utf-8') as f:
                json.dump(data_inicial, f, indent=2, ensure_ascii=False)
    
    def _cargar_datos(self) -> Dict[str, Any]:
        """Carga todos los datos de valores desde el archivo"""
        try:
            with open(self.archivo_valores, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._asegurar_archivo_existe()
            with open(self.archivo_valores, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def _guardar_datos(self, data: Dict[str, Any]) -> bool:
        """Guarda todos los datos de valores en el archivo"""
        try:
            data["ultima_actualizacion"] = datetime.now().isoformat()
            with open(self.archivo_valores, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando valores: {e}")
            return False
    
    def _generar_clave(self, usuario: str, tienda_id: str, fecha: str) -> str:
        """Genera clave única para identificar valores específicos"""
        return f"{usuario}_{tienda_id}_{fecha}"
    
    def _valores_vigentes(self, fecha_guardado: str) -> bool:
        """Verifica si los valores aún están vigentes (menos de 1 día)"""
        try:
            fecha_guardado_dt = datetime.fromisoformat(fecha_guardado)
            ahora = datetime.now()
            diferencia = ahora - fecha_guardado_dt
            return diferencia < timedelta(days=1)
        except:
            return False
    
    def guardar_valores(self, usuario: str, tienda_id: str, fecha: date, 
                       valores_impulsivo: Dict = None, 
                       valores_kilos: Dict = None, 
                       valores_extras: Dict = None) -> bool:
        """
        Guarda los valores de los formularios
        
        Args:
            usuario: Nombre del usuario
            tienda_id: ID de la tienda
            fecha: Fecha de la carga
            valores_impulsivo: Diccionario con valores de productos impulsivos
            valores_kilos: Diccionario con valores de productos por kilos
            valores_extras: Diccionario con valores de productos extras
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            data = self._cargar_datos()
            fecha_str = fecha.strftime("%Y-%m-%d") if isinstance(fecha, date) else str(fecha)
            clave = self._generar_clave(usuario, tienda_id, fecha_str)
            
            valores_completos = {
                "usuario": usuario,
                "tienda_id": tienda_id,
                "fecha": fecha_str,
                "fecha_guardado": datetime.now().isoformat(),
                "valores_impulsivo": valores_impulsivo or {},
                "valores_kilos": valores_kilos or {},
                "valores_extras": valores_extras or {}
            }
            
            data["valores"][clave] = valores_completos
            return self._guardar_datos(data)
            
        except Exception as e:
            print(f"Error guardando valores para {usuario}: {e}")
            return False
    
    def cargar_valores(self, usuario: str, tienda_id: str, fecha: date) -> Dict[str, Dict]:
        """
        Carga los valores de los formularios si aún están vigentes
        
        Args:
            usuario: Nombre del usuario
            tienda_id: ID de la tienda
            fecha: Fecha de la carga
            
        Returns:
            Dict con tres claves: valores_impulsivo, valores_kilos, valores_extras
        """
        try:
            data = self._cargar_datos()
            fecha_str = fecha.strftime("%Y-%m-%d") if isinstance(fecha, date) else str(fecha)
            clave = self._generar_clave(usuario, tienda_id, fecha_str)
            
            if clave in data["valores"]:
                valores_data = data["valores"][clave]
                
                # Verificar que los valores estén vigentes (menos de 1 día)
                if self._valores_vigentes(valores_data.get("fecha_guardado", "")):
                    return {
                        "valores_impulsivo": valores_data.get("valores_impulsivo", {}),
                        "valores_kilos": valores_data.get("valores_kilos", {}),
                        "valores_extras": valores_data.get("valores_extras", {})
                    }
            
            return {
                "valores_impulsivo": {},
                "valores_kilos": {},
                "valores_extras": {}
            }
            
        except Exception as e:
            print(f"Error cargando valores para {usuario}: {e}")
            return {
                "valores_impulsivo": {},
                "valores_kilos": {},
                "valores_extras": {}
            }
    
    def limpiar_valores(self, usuario: str, tienda_id: str, fecha: date) -> bool:
        """Elimina los valores guardados"""
        try:
            data = self._cargar_datos()
            fecha_str = fecha.strftime("%Y-%m-%d") if isinstance(fecha, date) else str(fecha)
            clave = self._generar_clave(usuario, tienda_id, fecha_str)
            
            if clave in data["valores"]:
                del data["valores"][clave]
                return self._guardar_datos(data)
            
            return True
            
        except Exception as e:
            print(f"Error limpiando valores para {usuario}: {e}")
            return False
    
    def limpiar_valores_antiguos(self, dias_antiguedad: int = 1) -> int:
        """
        Limpia valores más antiguos que el número de días especificado
        
        Args:
            dias_antiguedad: Número de días (por defecto 1)
            
        Returns:
            int: Número de registros limpiados
        """
        try:
            data = self._cargar_datos()
            fecha_limite = datetime.now() - timedelta(days=dias_antiguedad)
            registros_eliminados = 0
            
            claves_a_eliminar = []
            
            for clave, valores in data["valores"].items():
                try:
                    fecha_guardado = datetime.fromisoformat(valores.get("fecha_guardado", ""))
                    if fecha_guardado < fecha_limite:
                        claves_a_eliminar.append(clave)
                except:
                    claves_a_eliminar.append(clave)
            
            for clave in claves_a_eliminar:
                del data["valores"][clave]
                registros_eliminados += 1
            
            if registros_eliminados > 0:
                self._guardar_datos(data)
            
            return registros_eliminados
            
        except Exception as e:
            print(f"Error limpiando valores antiguos: {e}")
            return 0

# Instancia global del gestor de persistencia de valores
valores_persistencia = ValoresPersistencia()
