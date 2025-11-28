"""
Servicio de base de datos para el sistema
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict
import logging

try:
    from ..models.data_models import Store, WeeklySuggestion, LocationInfo
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    # Definir clases básicas como fallback
    class Store:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class WeeklySuggestion:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class LocationInfo:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
from ..config.settings import DB_PATH

logger = logging.getLogger(__name__)


class DatabaseService:
    """Servicio para manejo de base de datos"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa las tablas de la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabla de tiendas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    lat REAL NOT NULL,
                    lon REAL NOT NULL,
                    city TEXT NOT NULL,
                    country TEXT NOT NULL,
                    base_demand_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Tabla de sugerencias
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    store_id INTEGER NOT NULL,
                    week_start TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    total_investment REAL NOT NULL,
                    expected_revenue REAL NOT NULL,
                    expected_roi REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    suggestion_json TEXT NOT NULL,
                    explanation TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (store_id) REFERENCES stores (id)
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Base de datos inicializada correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            raise
    
    def save_store(self, name: str, lat: float, lon: float, city: str, country: str, base_demand: Dict) -> int:
        """
        Guarda una tienda en la base de datos (versión compatible)
        
        Args:
            name: Nombre de la tienda
            lat: Latitud
            lon: Longitud
            city: Ciudad
            country: País
            base_demand: Demanda base como diccionario
            
        Returns:
            ID de la tienda guardada
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO stores (name, lat, lon, city, country, base_demand_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                name, lat, lon, city, country,
                json.dumps(base_demand),
                datetime.now().isoformat()
            ))
            
            store_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Tienda guardada con ID: {store_id}")
            return store_id
            
        except Exception as e:
            logger.error(f"Error guardando tienda: {e}")
            raise
    
    def get_stores(self) -> List[Dict]:
        """
        Obtiene todas las tiendas
        
        Returns:
            Lista de diccionarios con datos de tiendas
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, lat, lon, city, country, base_demand_json, created_at
                FROM stores
                ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            stores = []
            for row in rows:
                store_data = {
                    'id': row[0],
                    'name': row[1],
                    'lat': row[2],
                    'lon': row[3],
                    'city': row[4],
                    'country': row[5],
                    'base_demand': json.loads(row[6]),
                    'created_at': row[7]
                }
                stores.append(store_data)
            
            return stores
            
        except Exception as e:
            logger.error(f"Error obteniendo tiendas: {e}")
            return []
    
    def save_suggestion(self, store_id: int, week_start: str, strategy: str, suggestion: Dict, explanation: str) -> int:
        """
        Guarda una sugerencia en la base de datos (versión compatible)
        
        Args:
            store_id: ID de la tienda
            week_start: Fecha de inicio de semana
            strategy: Estrategia utilizada
            suggestion: Sugerencia como diccionario
            explanation: Explicación de la sugerencia
            
        Returns:
            ID de la sugerencia guardada
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO suggestions (
                    store_id, week_start, strategy, total_investment,
                    expected_revenue, expected_roi, risk_level,
                    suggestion_json, explanation, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                store_id, week_start, strategy,
                suggestion.get('total_investment', 0),
                suggestion.get('expected_revenue', 0),
                suggestion.get('expected_roi', 0),
                suggestion.get('risk_level', 'MEDIO'),
                json.dumps(suggestion),
                explanation,
                datetime.now().isoformat()
            ))
            
            suggestion_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Sugerencia guardada con ID: {suggestion_id}")
            return suggestion_id
            
        except Exception as e:
            logger.error(f"Error guardando sugerencia: {e}")
            raise
    
    def get_suggestions(self, store_id: Optional[int] = None) -> List[Dict]:
        """
        Obtiene sugerencias, opcionalmente filtradas por tienda
        
        Args:
            store_id: ID de tienda para filtrar (opcional)
            
        Returns:
            Lista de diccionarios con sugerencias
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if store_id:
                cursor.execute("""
                    SELECT s.*, st.name as store_name
                    FROM suggestions s
                    JOIN stores st ON s.store_id = st.id
                    WHERE s.store_id = ?
                    ORDER BY s.created_at DESC
                """, (store_id,))
            else:
                cursor.execute("""
                    SELECT s.*, st.name as store_name
                    FROM suggestions s
                    JOIN stores st ON s.store_id = st.id
                    ORDER BY s.created_at DESC
                """)
            
            rows = cursor.fetchall()
            conn.close()
            
            suggestions = []
            for row in rows:
                suggestion_data = {
                    'id': row[0],
                    'store_id': row[1],
                    'store_name': row[11],  # store_name del JOIN
                    'week_start': row[2],
                    'strategy': row[3],
                    'total_investment': row[4],
                    'expected_revenue': row[5],
                    'expected_roi': row[6],
                    'risk_level': row[7],
                    'suggestion_json': json.loads(row[8]) if row[8] else {},
                    'explanation': row[9],
                    'created_at': row[10]
                }
                suggestions.append(suggestion_data)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error obteniendo sugerencias: {e}")
            return []
    
    def save_inventory_snapshot(self, store_id: int, inventory_data: Dict) -> int:
        """
        Guarda un snapshot del inventario sincronizado
        
        Args:
            store_id: ID de la tienda
            inventory_data: Datos del inventario sincronizado
            
        Returns:
            ID del snapshot guardado
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Crear tabla si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    store_id INTEGER NOT NULL,
                    inventory_json TEXT NOT NULL,
                    total_bultos INTEGER NOT NULL,
                    total_productos INTEGER NOT NULL,
                    stock_ok INTEGER NOT NULL,
                    stock_bajo INTEGER NOT NULL,
                    sin_stock INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (store_id) REFERENCES stores (id)
                )
            """)
            
            metadata = inventory_data.get("metadata", {})
            
            cursor.execute("""
                INSERT INTO inventory_snapshots 
                (store_id, inventory_json, total_bultos, total_productos, 
                 stock_ok, stock_bajo, sin_stock, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                store_id,
                json.dumps(inventory_data),
                metadata.get("total_bultos", 0),
                metadata.get("total_productos", 0),
                metadata.get("stock_ok", 0),
                metadata.get("stock_bajo", 0),
                metadata.get("sin_stock", 0),
                datetime.now().isoformat()
            ))
            
            snapshot_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Snapshot de inventario guardado con ID: {snapshot_id}")
            return snapshot_id
            
        except Exception as e:
            logger.error(f"Error guardando snapshot de inventario: {e}")
            raise
    
    def get_latest_inventory_snapshot(self, store_id: int) -> Optional[Dict]:
        """
        Obtiene el snapshot más reciente del inventario para una tienda
        
        Args:
            store_id: ID de la tienda
            
        Returns:
            Diccionario con datos del inventario o None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT inventory_json, created_at
                FROM inventory_snapshots
                WHERE store_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (store_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "data": json.loads(row[0]),
                    "created_at": row[1]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo snapshot de inventario: {e}")
            return None


# Instancia global del servicio
db_service = DatabaseService()