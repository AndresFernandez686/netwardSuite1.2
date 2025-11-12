"""
Sistema de gestión de historial.
Maneja el registro y consulta del historial de operaciones.
"""
import json
import os
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from pathlib import Path
import pandas as pd

from ..core.data_models import InventoryRecord, DeliveryRecord

class HistoryManager:
    """Gestor del historial de operaciones"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.history_file = self.base_path / "historial_inventario.json"
        self.delivery_history_file = self.base_path / "historial_delivery.json"
        
        # Asegurar que el directorio base existe
        self.base_path.mkdir(exist_ok=True)
    
    def add_inventory_record(self, record: InventoryRecord) -> bool:
        """Añade registro al historial de inventario"""
        try:
            history = self.load_inventory_history()
            history.append(record.to_dict())
            
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            print(f"Error guardando en historial: {e}")
            return False
    
    def add_inventory_record_legacy(self, fecha: date, usuario: str, categoria: str, 
                                  producto: str, cantidad: Any, modo: str, 
                                  tipo_inventario: str = "Diario") -> bool:
        """Método legacy para compatibilidad con código existente"""
        record = InventoryRecord(
            fecha=fecha,
            usuario=usuario,
            categoria=categoria,
            producto=producto,
            cantidad=cantidad,
            modo=modo,
            tipo_inventario=tipo_inventario
        )
        return self.add_inventory_record(record)
    
    def load_inventory_history(self) -> List[Dict[str, Any]]:
        """Carga historial de inventario"""
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def add_delivery_record(self, record: DeliveryRecord) -> bool:
        """Añade registro al historial de delivery"""
        try:
            history = self.load_delivery_history()
            history.append(record.to_dict())
            
            with open(self.delivery_history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            print(f"Error guardando venta delivery: {e}")
            return False
    
    def add_delivery_record_legacy(self, fecha: date, usuario: str, producto: str, 
                                 cantidad: int, es_promocion: bool = False) -> bool:
        """Método legacy para compatibilidad"""
        record = DeliveryRecord(
            fecha=fecha,
            usuario=usuario,
            producto=producto,
            cantidad=cantidad,
            es_promocion=es_promocion
        )
        return self.add_delivery_record(record)
    
    def load_delivery_history(self) -> List[Dict[str, Any]]:
        """Carga historial de delivery"""
        if not self.delivery_history_file.exists():
            return []
        
        try:
            with open(self.delivery_history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def get_inventory_dataframe(self) -> pd.DataFrame:
        """Obtiene historial de inventario como DataFrame"""
        history = self.load_inventory_history()
        
        if not history:
            return pd.DataFrame()
        
        df = pd.DataFrame(history)
        
        # Normalizar columnas
        if "fecha" in df.columns:
            df["Fecha"] = pd.to_datetime(df["fecha"])
        if "usuario" in df.columns:
            df["Usuario"] = df["usuario"]
        if "producto" in df.columns:
            df["Producto"] = df["producto"]
        
        return df
    
    def get_delivery_dataframe(self) -> pd.DataFrame:
        """Obtiene historial de delivery como DataFrame"""
        history = self.load_delivery_history()
        
        if not history:
            return pd.DataFrame()
        
        df = pd.DataFrame(history)
        
        # Normalizar columnas
        if "fecha" in df.columns:
            df["Fecha"] = pd.to_datetime(df["fecha"])
        if "usuario" in df.columns:
            df["Usuario"] = df["usuario"]
        
        return df

class HistoryFilter:
    """Filtros para consultas de historial"""
    
    @staticmethod
    def filter_by_date_range(df: pd.DataFrame, start_date: date, 
                           end_date: date) -> pd.DataFrame:
        """Filtra por rango de fechas"""
        if df.empty or "Fecha" not in df.columns:
            return df
        
        mask = (df["Fecha"].dt.date >= start_date) & (df["Fecha"].dt.date <= end_date)
        return df[mask]
    
    @staticmethod
    def filter_by_user(df: pd.DataFrame, user: str) -> pd.DataFrame:
        """Filtra por usuario"""
        if df.empty or "Usuario" not in df.columns or user == "Todos":
            return df
        
        return df[df["Usuario"] == user]
    
    @staticmethod
    def filter_by_inventory_type(df: pd.DataFrame, inv_type: str) -> pd.DataFrame:
        """Filtra por tipo de inventario"""
        if df.empty or inv_type == "Todos":
            return df
        
        # Si no existe la columna tipo_inventario, asumimos registros antiguos (Diario)
        if "tipo_inventario" in df.columns:
            return df[df["tipo_inventario"] == inv_type]
        elif inv_type == "Diario":
            # Mantener todos los registros si buscamos "Diario" y no hay columna
            return df
        else:
            # Si buscamos Semanal/Quincenal pero no hay columna, no hay resultados
            return df.iloc[0:0]  # DataFrame vacío
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
        """Elimina duplicados manteniendo la última entrada por día"""
        if df.empty:
            return df
        
        # Añadir columna de fecha solo
        if "Fecha" in df.columns:
            df = df.copy()
            df["Fecha_solo"] = df["Fecha"].dt.date
            
            # Ordenar por fecha y mantener solo la última entrada
            if all(col in df.columns for col in ["Producto", "Fecha_solo", "Usuario"]):
                df = df.sort_values("Fecha")
                df = df.drop_duplicates(subset=["Producto", "Fecha_solo", "Usuario"], keep="last")
                df = df.drop("Fecha_solo", axis=1)
        
        return df

class HistoryAnalyzer:
    """Analizador de patrones en el historial"""
    
    @staticmethod
    def get_user_activity_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """Obtiene resumen de actividad por usuario"""
        if df.empty or "Usuario" not in df.columns:
            return {}
        
        summary = {}
        for user in df["Usuario"].unique():
            user_data = df[df["Usuario"] == user]
            summary[user] = {
                "total_registros": len(user_data),
                "productos_unicos": user_data["Producto"].nunique() if "Producto" in user_data.columns else 0,
                "ultimo_registro": user_data["Fecha"].max() if "Fecha" in user_data.columns else None
            }
        
        return summary
    
    @staticmethod
    def get_product_frequency(df: pd.DataFrame) -> Dict[str, int]:
        """Obtiene frecuencia de productos registrados"""
        if df.empty or "Producto" not in df.columns:
            return {}
        
        return df["Producto"].value_counts().to_dict()
    
    @staticmethod
    def get_inventory_type_distribution(df: pd.DataFrame) -> Dict[str, int]:
        """Obtiene distribución por tipo de inventario"""
        if df.empty:
            return {}
        
        if "tipo_inventario" in df.columns:
            return df["tipo_inventario"].value_counts().to_dict()
        else:
            # Asumir que todos son "Diario" si no hay columna
            return {"Diario": len(df)}