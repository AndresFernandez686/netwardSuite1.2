"""
Modelos de datos para el sistema de inventario.
Define las estructuras principales del sistema.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union
from datetime import date
from enum import Enum

class ProductCategory(Enum):
    IMPULSIVO = "Impulsivo"
    POR_KILOS = "Por Kilos"
    EXTRAS = "Extras"

@dataclass
class Product:
    """Modelo de producto básico"""
    name: str
    category: ProductCategory
    quantity: Union[int, float, List[Any]]
    
    def is_numeric(self) -> bool:
        """Verifica si el producto tiene cantidad numérica simple"""
        return isinstance(self.quantity, (int, float))
    
    def is_empty(self) -> bool:
        """Verifica si el producto está vacío"""
        if self.is_numeric():
            return self.quantity == 0
        elif isinstance(self.quantity, list):
            return len(self.quantity) == 0 or all(
                item == "Vacío" or item == 0 for item in self.quantity
            )
        return True

@dataclass
class InventoryRecord:
    """Registro de inventario con tipo específico"""
    fecha: date
    usuario: str
    categoria: str
    producto: str
    cantidad: Any
    modo: str
    tipo_inventario: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para persistencia"""
        return {
            "fecha": str(self.fecha),
            "usuario": self.usuario,
            "categoria": self.categoria,
            "producto": self.producto,
            "cantidad": self.cantidad,
            "modo": self.modo,
            "tipo_inventario": self.tipo_inventario
        }

@dataclass
class DeliveryItem:
    """Item de delivery/catálogo"""
    nombre: str
    es_promocion: bool = False
    activo: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para persistencia"""
        return {
            "nombre": self.nombre,
            "es_promocion": self.es_promocion,
            "activo": self.activo
        }

@dataclass
class DeliveryRecord:
    """Registro de venta de delivery"""
    fecha: date
    usuario: str
    producto: str
    cantidad: int
    es_promocion: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para persistencia"""
        return {
            "fecha": str(self.fecha),
            "usuario": self.usuario,
            "producto": self.producto,
            "cantidad": self.cantidad,
            "es_promocion": self.es_promocion
        }

class QuantityFormatter:
    """Formateador de cantidades según el tipo"""
    
    @staticmethod
    def format_kilos_quantity(cantidad: Dict[str, Any]) -> str:
        """Formatea cantidad de tipo kilos"""
        if cantidad.get("tipo") == "Quincenal" and "total_kilos" in cantidad:
            total = cantidad.get("total_kilos", 0)
            kilos_detalle = cantidad.get("kilos_por_balde", [])
            detalle = ', '.join([f'{k:.1f}kg' for k in kilos_detalle])
            return f"Total: {total:.1f} kg ({detalle})"
        elif "estados" in cantidad:
            estados = cantidad.get("estados", [])
            return f"{', '.join(estados)}"
        return str(cantidad)
    
    @staticmethod
    def format_list_quantity(cantidad: List[Any]) -> str:
        """Formatea cantidad de tipo lista"""
        if all(isinstance(x, (int, float)) for x in cantidad):
            # Lista de kilos
            total = sum(cantidad)
            detalle = ', '.join([f'{k:.1f}kg' for k in cantidad])
            return f"Total: {total:.1f} kg ({detalle})"
        else:
            # Lista de estados
            return f"{', '.join([str(x) for x in cantidad])}"
    
    @staticmethod
    def format_quantity(cantidad: Any, categoria: str = "") -> str:
        """Formatea cualquier tipo de cantidad"""
        if categoria == "Por Kilos" and isinstance(cantidad, dict):
            return QuantityFormatter.format_kilos_quantity(cantidad)
        elif isinstance(cantidad, list):
            return QuantityFormatter.format_list_quantity(cantidad)
        else:
            return str(cantidad)