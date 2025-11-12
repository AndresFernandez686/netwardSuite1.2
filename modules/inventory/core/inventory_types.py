"""
Módulo para el manejo de tipos de inventario.
Centraliza la lógica de Diario, Semanal y Quincenal.
"""
from enum import Enum
from typing import Dict, Any, Optional
import streamlit as st

class InventoryType(Enum):
    DIARIO = "Diario"
    SEMANAL = "Semanal"
    QUINCENAL = "Quincenal"
    
    @classmethod
    def from_string(cls, value: str) -> 'InventoryType':
        """Convierte string a InventoryType"""
        for item in cls:
            if item.value == value:
                return item
        return cls.DIARIO  # Default

class TypedInventoryManager:
    """Maneja inventarios separados por tipo"""
    
    def __init__(self):
        self.session_key = "inventario_por_tipo"
        self._initialize_session()
    
    def _initialize_session(self):
        """Inicializa la estructura en session_state"""
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = {
                InventoryType.DIARIO.value: {},
                InventoryType.SEMANAL.value: {},
                InventoryType.QUINCENAL.value: {}
            }
    
    def get_product_key(self, inv_type: InventoryType, category: str, product: str) -> str:
        """Genera key única para un producto específico"""
        return f"{inv_type.value}_{category}_{product}"
    
    def set_product_quantity(self, inv_type: InventoryType, category: str, 
                           product: str, quantity: Any) -> None:
        """Guarda cantidad de producto para un tipo específico"""
        key = self.get_product_key(inv_type, category, product)
        st.session_state[self.session_key][inv_type.value][key] = quantity
    
    def get_product_quantity(self, inv_type: InventoryType, category: str, 
                           product: str, default: Any = 0) -> Any:
        """Obtiene cantidad de producto para un tipo específico"""
        key = self.get_product_key(inv_type, category, product)
        return st.session_state[self.session_key][inv_type.value].get(key, default)
    
    def get_all_products_by_type(self, inv_type: InventoryType) -> Dict[str, Any]:
        """Obtiene todos los productos de un tipo específico"""
        return st.session_state[self.session_key][inv_type.value].copy()
    
    def clear_widgets_for_type_change(self):
        """Limpia widgets de Streamlit cuando cambia el tipo"""
        keys_to_clear = [
            k for k in st.session_state.keys() 
            if any(prefix in k for prefix in ["cant_", "_balde_", "num_baldes_"])
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    def get_summary(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene resumen de todos los tipos de inventario"""
        summary = {}
        for tipo in InventoryType:
            products = self.get_all_products_by_type(tipo)
            if products:
                summary[tipo.value] = {}
                for key, quantity in products.items():
                    # Extraer categoría y producto del key
                    parts = key.split('_', 2)
                    if len(parts) >= 3:
                        category = parts[1]
                        product = parts[2]
                        if quantity > 0:
                            summary[tipo.value][f"{product} ({category})"] = quantity
        return summary

class InventoryTypeDetector:
    """Detecta cambios de tipo de inventario"""
    
    def __init__(self):
        self.session_key = "tipo_inventario_actual"
    
    def detect_type_change(self, new_type: InventoryType) -> bool:
        """Detecta si cambió el tipo de inventario"""
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = new_type.value
            return False
        
        if st.session_state[self.session_key] != new_type.value:
            st.session_state[self.session_key] = new_type.value
            return True
        
        return False
    
    def get_current_type(self) -> InventoryType:
        """Obtiene el tipo actual"""
        current = st.session_state.get(self.session_key, InventoryType.DIARIO.value)
        return InventoryType.from_string(current)