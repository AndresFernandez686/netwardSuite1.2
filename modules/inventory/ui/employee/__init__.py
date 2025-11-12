"""
Factory para crear componentes de UI de empleados.
"""
from typing import Any, Dict

# Importaciones híbridas
try:
    from ...core.inventory_types import InventoryType
except ImportError:
    try:
        from core.inventory_types import InventoryType
    except ImportError:
        class InventoryType:
            DIARIO = "Diario"
            SEMANAL = "Semanal"
            QUINCENAL = "Quincenal"

from .inventory_ui import EmployeeInventoryUI
from .delivery_ui import EmployeeDeliveryUI

class EmployeeUIFactory:
    """Factory para componentes de empleados"""
    
    _components: Dict[str, type] = {
        "inventory_ui": EmployeeInventoryUI,
        "delivery_ui": EmployeeDeliveryUI
    }
    
    @classmethod
    def create(cls, component_type: str) -> Any:
        """Crea componente de empleado"""
        if component_type not in cls._components:
            raise ValueError(f"Componente desconocido: {component_type}")
        
        component_class = cls._components[component_type]
        return component_class()
    
    @classmethod
    def create_inventory_ui(cls, inventory_type: InventoryType) -> EmployeeInventoryUI:
        """Crea UI de inventario específica para el tipo"""
        ui = cls.create("inventory_ui")
        ui.set_inventory_type(inventory_type)
        return ui
    
    @classmethod
    def register_component(cls, name: str, component_class: type):
        """Registra nuevo componente"""
        cls._components[name] = component_class
    
    @classmethod
    def list_components(cls) -> list:
        """Lista componentes disponibles"""
        return list(cls._components.keys())