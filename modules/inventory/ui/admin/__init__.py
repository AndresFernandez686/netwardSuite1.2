"""
Factory para crear componentes de UI de administradores.
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

from .inventory_admin import AdminInventoryUI
from .history_admin import AdminHistoryUI
from .delivery_admin import AdminDeliveryUI
from .reports_admin import AdminReportsUI

class AdminUIFactory:
    """Factory para componentes de administradores"""
    
    _components: Dict[str, type] = {
        "inventory_admin": AdminInventoryUI,
        "history_admin": AdminHistoryUI,
        "delivery_admin": AdminDeliveryUI,
        "reports_admin": AdminReportsUI
    }
    
    @classmethod
    def create(cls, component_type: str) -> Any:
        """Crea componente de administrador"""
        if component_type not in cls._components:
            raise ValueError(f"Componente desconocido: {component_type}")
        
        component_class = cls._components[component_type]
        return component_class()
    
    @classmethod
    def create_inventory_ui(cls, inventory_type: InventoryType) -> AdminInventoryUI:
        """Crea UI de inventario específica para el tipo"""
        ui = cls.create("inventory_admin")
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