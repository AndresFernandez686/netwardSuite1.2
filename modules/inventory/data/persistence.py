"""
Sistema de persistencia de datos.
Maneja el guardado y carga de inventarios y configuraciones.
"""
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

# Importaciones híbridas
try:
    from ..core.data_models import InventoryRecord, DeliveryItem, DeliveryRecord
except ImportError:
    try:
        from core.data_models import InventoryRecord, DeliveryItem, DeliveryRecord
    except ImportError:
        # Fallback básico
        class InventoryRecord:
            pass
        
        class DeliveryItem:
            pass
        
        class DeliveryRecord:
            pass

class DataPersistence:
    """Gestor principal de persistencia de datos"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.inventory_file = self.base_path / "inventario.json"
        self.delivery_catalog_file = self.base_path / "catalogo_delivery.json"
        self.config_file = self.base_path / "config.json"
        
        # Asegurar que el directorio base existe
        self.base_path.mkdir(exist_ok=True)
    
    def load_inventory(self) -> Dict[str, Any]:
        """Carga inventario desde archivo"""
        if not self.inventory_file.exists():
            return self._create_default_inventory()
        
        try:
            with open(self.inventory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return self._create_default_inventory()
    
    def save_inventory(self, inventory: Dict[str, Any]) -> bool:
        """Guarda inventario en archivo"""
        try:
            with open(self.inventory_file, "w", encoding="utf-8") as f:
                json.dump(inventory, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando inventario: {e}")
            return False
    
    def _create_default_inventory(self) -> Dict[str, Any]:
        """Crea inventario por defecto"""
        default = {
            "Impulsivo": {
                "Caja almendrado": 0,
                "Caja vainilla": 0,
                "Caja chocolate": 0,
                "Caja fresa": 0
            },
            "Por Kilos": {
                "Almendrado": [],
                "Vainilla": [],
                "Chocolate": [],
                "Fresa": []
            },
            "Extras": {
                "Conos": 0,
                "Vasos": 0,
                "Servilletas": 0,
                "Cucharitas": 0
            }
        }
        
        # Guardar inventario por defecto
        self.save_inventory(default)
        return default
    
    def load_delivery_catalog(self) -> List[Dict[str, Any]]:
        """Carga catálogo de delivery"""
        if not self.delivery_catalog_file.exists():
            return []
        
        try:
            with open(self.delivery_catalog_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def save_delivery_catalog(self, catalog: List[Dict[str, Any]]) -> bool:
        """Guarda catálogo de delivery"""
        try:
            with open(self.delivery_catalog_file, "w", encoding="utf-8") as f:
                json.dump(catalog, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando catálogo delivery: {e}")
            return False
    
    def load_config(self) -> Dict[str, Any]:
        """Carga configuración del sistema"""
        if not self.config_file.exists():
            return self._create_default_config()
        
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return self._create_default_config()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Guarda configuración del sistema"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando configuración: {e}")
            return False
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Crea configuración por defecto"""
        default = {
            "opciones_valde": {
                "Vacío": "🔴",
                "Medio": "🟡", 
                "Lleno": "🟢"
            },
            "usuarios": ["admin", "empleado1", "empleado2"],
            "version": "2.0.0"
        }
        
        self.save_config(default)
        return default

class FileValidator:
    """Validador de archivos de datos"""
    
    @staticmethod
    def validate_inventory_structure(data: Dict[str, Any]) -> bool:
        """Valida estructura de inventario"""
        required_categories = ["Impulsivo", "Por Kilos", "Extras"]
        
        if not isinstance(data, dict):
            return False
        
        for category in required_categories:
            if category not in data:
                return False
            
            if not isinstance(data[category], dict):
                return False
        
        return True
    
    @staticmethod
    def validate_delivery_catalog(data: List[Dict[str, Any]]) -> bool:
        """Valida estructura de catálogo delivery"""
        if not isinstance(data, list):
            return False
        
        required_fields = ["nombre", "es_promocion", "activo"]
        
        for item in data:
            if not isinstance(item, dict):
                return False
            
            for field in required_fields:
                if field not in item:
                    return False
        
        return True

class BackupManager:
    """Gestor de copias de seguridad"""
    
    def __init__(self, data_persistence: DataPersistence):
        self.persistence = data_persistence
        self.backup_dir = self.persistence.base_path / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self) -> bool:
        """Crea copia de seguridad completa"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = self.backup_dir / f"backup_{timestamp}"
        backup_subdir.mkdir(exist_ok=True)
        
        try:
            # Backup de inventario
            inventory = self.persistence.load_inventory()
            with open(backup_subdir / "inventario.json", "w", encoding="utf-8") as f:
                json.dump(inventory, f, indent=2, ensure_ascii=False)
            
            # Backup de catálogo delivery
            catalog = self.persistence.load_delivery_catalog()
            with open(backup_subdir / "catalogo_delivery.json", "w", encoding="utf-8") as f:
                json.dump(catalog, f, indent=2, ensure_ascii=False)
            
            # Backup de configuración
            config = self.persistence.load_config()
            with open(backup_subdir / "config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            print(f"Error creando backup: {e}")
            return False
    
    def list_backups(self) -> List[str]:
        """Lista copias de seguridad disponibles"""
        backups = []
        if self.backup_dir.exists():
            for item in self.backup_dir.iterdir():
                if item.is_dir() and item.name.startswith("backup_"):
                    backups.append(item.name)
        
        return sorted(backups, reverse=True)  # Más recientes primero