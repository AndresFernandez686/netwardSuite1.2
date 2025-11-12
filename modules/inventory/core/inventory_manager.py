"""
Gestor central del sistema de inventario.
Coordina las operaciones principales del inventario.
"""
from typing import Dict, Any, List, Optional
from datetime import date
import streamlit as st

from .inventory_types import InventoryType, TypedInventoryManager, InventoryTypeDetector
from .data_models import InventoryRecord, Product, ProductCategory, QuantityFormatter

class InventoryManager:
    """Gestor principal del sistema de inventario"""
    
    def __init__(self):
        self.typed_manager = TypedInventoryManager()
        self.type_detector = InventoryTypeDetector()
        self.session_key_loaded = "productos_cargados_sesion"
        self._initialize_session()
    
    def _initialize_session(self):
        """Inicializa estructuras de sesión"""
        if self.session_key_loaded not in st.session_state:
            st.session_state[self.session_key_loaded] = {}
    
    def handle_type_change(self, new_type: InventoryType) -> bool:
        """Maneja cambio de tipo de inventario"""
        if self.type_detector.detect_type_change(new_type):
            self.typed_manager.clear_widgets_for_type_change()
            st.info(f"🔄 Cambiado a inventario **{new_type.value}**")
            return True
        return False
    
    def get_product_value(self, inv_type: InventoryType, category: str, 
                         product: str, default: Any = 0) -> Any:
        """Obtiene valor de producto para el tipo actual"""
        return self.typed_manager.get_product_quantity(inv_type, category, product, default)
    
    def save_product(self, inv_type: InventoryType, category: str, product: str, 
                    quantity: Any, usuario: str, fecha: date, 
                    save_to_inventory: callable, save_to_history: callable):
        """Guarda producto en inventario y registra en historial"""
        
        # Guardar en el gestor tipificado
        self.typed_manager.set_product_quantity(inv_type, category, product, quantity)
        
        # Guardar en inventario principal (compatibilidad)
        # Esta función será llamada desde la UI con el inventario cargado
        
        # Registrar en historial
        record = InventoryRecord(
            fecha=fecha,
            usuario=usuario,
            categoria=category,
            producto=product,
            cantidad=quantity,
            modo="Modificar",
            tipo_inventario=inv_type.value
        )
        
        save_to_history(record)
        
        # Registrar en productos cargados de la sesión
        self._register_session_product(category, product, quantity, inv_type)
    
    def _register_session_product(self, category: str, product: str, 
                                 quantity: Any, inv_type: InventoryType):
        """Registra producto en la sesión actual"""
        if category not in st.session_state[self.session_key_loaded]:
            st.session_state[self.session_key_loaded][category] = {}
        
        st.session_state[self.session_key_loaded][category][product] = {
            "cantidad": quantity,
            "tipo_inventario": inv_type.value
        }
    
    def get_session_summary(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene resumen de productos cargados en la sesión"""
        return st.session_state[self.session_key_loaded].copy()
    
    def get_type_summary(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene resumen completo por tipos"""
        return self.typed_manager.get_summary()
    
    def get_widget_key(self, inv_type: InventoryType, category: str, 
                      product: str, widget_type: str = "cant") -> str:
        """Genera key única para widgets de Streamlit"""
        return f"{widget_type}_{inv_type.value}_{category}_{product}"

class BaldeManager:
    """Gestor específico para productos 'Por Kilos' con baldes"""
    
    @staticmethod
    def get_balde_key(inv_type: InventoryType, product: str, balde_num: int, 
                     fecha: date, usuario: str, is_kilos: bool = False) -> str:
        """Genera key para balde específico"""
        suffix = "_kilos" if is_kilos else ""
        return f"{product}_balde_{balde_num}_{fecha}_{usuario}{suffix}_{inv_type.value}"
    
    @staticmethod
    def initialize_balde_value(key: str, default_value: Any, 
                              productos: Dict[str, Any], product: str, 
                              balde_index: int):
        """Inicializa valor de balde si no existe"""
        if key not in st.session_state:
            # Intentar cargar valor guardado
            valor_inicial = default_value
            if (isinstance(productos.get(product), list) and 
                len(productos[product]) > balde_index):
                saved_value = productos[product][balde_index]
                if isinstance(saved_value, type(default_value)):
                    valor_inicial = saved_value
            
            st.session_state[key] = valor_inicial

class ValidationManager:
    """Gestor de validaciones del sistema"""
    
    @staticmethod
    def validate_quantity(quantity: Any, category: str) -> tuple[bool, str]:
        """Valida cantidad según categoría"""
        if category in ["Impulsivo", "Extras"]:
            if not isinstance(quantity, (int, float)) or quantity < 0:
                return False, "La cantidad debe ser un número mayor o igual a 0"
        
        return True, ""
    
    @staticmethod
    def validate_product_name(name: str) -> tuple[bool, str]:
        """Valida nombre de producto"""
        if not name or not name.strip():
            return False, "El nombre del producto no puede estar vacío"
        
        if len(name.strip()) < 2:
            return False, "El nombre debe tener al menos 2 caracteres"
        
        return True, ""