"""
Factory para crear UIs específicas.
Centraliza la creación de componentes de interfaz.
"""
from typing import Type, Dict, Any
from ...core.inventory_types import InventoryType
from .employee import EmployeeUIFactory
try:
    from .admin import AdminUIFactory
except ImportError:
    AdminUIFactory = None

class UIFactory:
    """Factory principal para crear componentes de UI"""
    
    @staticmethod
    def create_employee_ui(component_type: str) -> Any:
        """Crea componente de UI para empleados"""
        return EmployeeUIFactory.create(component_type)
    
    @staticmethod
    def create_admin_ui(component_type: str) -> Any:
        """Crea componente de UI para administradores"""
        if AdminUIFactory is None:
            return None
        return AdminUIFactory.create(component_type)
    
    @staticmethod
    def get_inventory_ui(inventory_type: InventoryType, user_role: str) -> Any:
        """Obtiene UI específica para tipo de inventario y rol"""
        if user_role == "empleado":
            return EmployeeUIFactory.create_inventory_ui(inventory_type)
        elif user_role == "admin":
            if AdminUIFactory is None:
                return None
            return AdminUIFactory.create_inventory_ui(inventory_type)
        else:
            raise ValueError(f"Rol desconocido: {user_role}")

class UIRegistry:
    """Registro de componentes UI disponibles"""
    
    EMPLOYEE_COMPONENTS = {
        "inventory": "inventory_ui",
        "delivery": "delivery_ui"
    }
    
    ADMIN_COMPONENTS = {
        "inventory": "inventory_admin",
        "history": "history_admin", 
        "delivery": "delivery_admin",
        "reports": "reports_admin"
    }
    
    @classmethod
    def get_component_name(cls, role: str, component: str) -> str:
        """Obtiene nombre del componente según rol"""
        if role == "empleado":
            return cls.EMPLOYEE_COMPONENTS.get(component, component)
        elif role == "admin":
            return cls.ADMIN_COMPONENTS.get(component, component)
        else:
            raise ValueError(f"Rol desconocido: {role}")
    
    @classmethod
    def list_components(cls, role: str) -> Dict[str, str]:
        """Lista componentes disponibles por rol"""
        if role == "empleado":
            return cls.EMPLOYEE_COMPONENTS.copy()
        elif role == "admin":
            return cls.ADMIN_COMPONENTS.copy()
        else:
            return {}