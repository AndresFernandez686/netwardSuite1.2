"""
Servicio para manejo de base de datos SQLite
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Optional
import logging
from pathlib import Path

from ..models import Store, WeeklySuggestion
from ..config.settings import DB_PATH

logger = logging.getLogger(__name__)


class DatabaseService:
    """Servicio para operaciones de base de datos"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_db_directory()
        self.init_database()
    
    def _ensure_db_directory(self):
        """Asegura que el directorio de la base de datos exista"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def init_database(self):
        """Inicializa las tablas de la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
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
                    created_at TEXT NOT NULL,
                    updated_at TEXT
                )""")
                
                # Tabla de sugerencias
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    store_id INTEGER NOT NULL,
                    week_start TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    suggestion_json TEXT NOT NULL,
                    explanation TEXT,
                    total_investment REAL,
                    expected_revenue REAL,
                    roi_percentage REAL,
                    risk_level TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (store_id) REFERENCES stores (id)
                )""")
                
                # Tabla de historial de clima (opcional, para análisis futuros)
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lat REAL NOT NULL,
                    lon REAL NOT NULL,
                    date TEXT NOT NULL,
                    temp_min REAL,
                    temp_max REAL,
                    temp_avg REAL,
                    description TEXT,
                    humidity REAL,
                    wind_speed REAL,
                    precipitation REAL,
                    created_at TEXT NOT NULL
                )""")
                
                conn.commit()
                logger.info("Base de datos inicializada correctamente")
                
        except sqlite3.Error as e:
            logger.error(f"Error inicializando base de datos: {e}")
            raise
    
    # === OPERACIONES DE TIENDAS ===
    
    def save_store(self, store: Store) -> int:
        """
        Guarda una tienda en la base de datos
        
        Args:
            store: Store a guardar
            
        Returns:
            ID de la tienda guardada
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                INSERT INTO stores (name, lat, lon, city, country, base_demand_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    store.name,
                    store.lat,
                    store.lon,
                    store.city,
                    store.country,
                    json.dumps(store.base_demand),
                    store.created_at.isoformat() if store.created_at else datetime.utcnow().isoformat()
                ))
                
                store_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Tienda guardada con ID: {store_id}")
                return store_id
                
        except sqlite3.Error as e:
            logger.error(f"Error guardando tienda: {e}")
            raise
    
    def get_store(self, store_id: int) -> Optional[Store]:
        """
        Obtiene una tienda por ID
        
        Args:
            store_id: ID de la tienda
            
        Returns:
            Store o None si no existe
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT id, name, lat, lon, city, country, base_demand_json, created_at
                FROM stores WHERE id = ?
                """, (store_id,))
                
                row = cursor.fetchone()
                
                if row:
                    return Store(
                        id=row[0],
                        name=row[1],
                        lat=row[2],
                        lon=row[3],
                        city=row[4],
                        country=row[5],
                        base_demand=json.loads(row[6]),
                        created_at=datetime.fromisoformat(row[7]) if row[7] else None
                    )
                
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo tienda {store_id}: {e}")
            return None
    
    def list_stores(self) -> List[Store]:
        """
        Lista todas las tiendas
        
        Returns:
            Lista de todas las tiendas
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT id, name, lat, lon, city, country, base_demand_json, created_at
                FROM stores ORDER BY created_at DESC
                """)
                
                stores = []
                for row in cursor.fetchall():
                    stores.append(Store(
                        id=row[0],
                        name=row[1],
                        lat=row[2],
                        lon=row[3],
                        city=row[4],
                        country=row[5],
                        base_demand=json.loads(row[6]),
                        created_at=datetime.fromisoformat(row[7]) if row[7] else None
                    ))
                
                return stores
                
        except sqlite3.Error as e:
            logger.error(f"Error listando tiendas: {e}")
            return []
    
    def update_store(self, store: Store) -> bool:
        """
        Actualiza una tienda existente
        
        Args:
            store: Store con los datos actualizados (debe tener ID)
            
        Returns:
            True si se actualizó correctamente
        """
        if not store.id:
            logger.error("Store debe tener ID para actualizar")
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                UPDATE stores 
                SET name=?, lat=?, lon=?, city=?, country=?, base_demand_json=?, updated_at=?
                WHERE id=?
                """, (
                    store.name,
                    store.lat,
                    store.lon,
                    store.city,
                    store.country,
                    json.dumps(store.base_demand),
                    datetime.utcnow().isoformat(),
                    store.id
                ))
                
                success = cursor.rowcount > 0
                conn.commit()
                
                if success:
                    logger.info(f"Tienda {store.id} actualizada")
                else:
                    logger.warning(f"No se encontró tienda con ID {store.id}")
                
                return success
                
        except sqlite3.Error as e:
            logger.error(f"Error actualizando tienda {store.id}: {e}")
            return False
    
    def delete_store(self, store_id: int) -> bool:
        """
        Elimina una tienda y sus sugerencias asociadas
        
        Args:
            store_id: ID de la tienda a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Eliminar sugerencias asociadas primero
                cursor.execute("DELETE FROM suggestions WHERE store_id = ?", (store_id,))
                
                # Eliminar tienda
                cursor.execute("DELETE FROM stores WHERE id = ?", (store_id,))
                
                success = cursor.rowcount > 0
                conn.commit()
                
                if success:
                    logger.info(f"Tienda {store_id} eliminada")
                else:
                    logger.warning(f"No se encontró tienda con ID {store_id}")
                
                return success
                
        except sqlite3.Error as e:
            logger.error(f"Error eliminando tienda {store_id}: {e}")
            return False
    
    # === OPERACIONES DE SUGERENCIAS ===
    
    def save_suggestion(self, suggestion: WeeklySuggestion) -> int:
        """
        Guarda una sugerencia en la base de datos
        
        Args:
            suggestion: WeeklySuggestion a guardar
            
        Returns:
            ID de la sugerencia guardada
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                INSERT INTO suggestions (
                    store_id, week_start, strategy, suggestion_json, explanation,
                    total_investment, expected_revenue, roi_percentage, risk_level, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    suggestion.store_id,
                    suggestion.week_start,
                    suggestion.strategy,
                    json.dumps(suggestion.to_dict()),
                    suggestion.explanation,
                    suggestion.total_investment,
                    suggestion.expected_revenue,
                    suggestion.roi_percentage,
                    suggestion.risk_level,
                    suggestion.created_at.isoformat() if suggestion.created_at else datetime.utcnow().isoformat()
                ))
                
                suggestion_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Sugerencia guardada con ID: {suggestion_id}")
                return suggestion_id
                
        except sqlite3.Error as e:
            logger.error(f"Error guardando sugerencia: {e}")
            raise
    
    def get_suggestions_by_store(self, store_id: int, limit: int = 50) -> List[dict]:
        """
        Obtiene sugerencias por tienda
        
        Args:
            store_id: ID de la tienda
            limit: Número máximo de sugerencias a retornar
            
        Returns:
            Lista de sugerencias
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT s.*, st.name as store_name
                FROM suggestions s
                JOIN stores st ON s.store_id = st.id
                WHERE s.store_id = ?
                ORDER BY s.created_at DESC
                LIMIT ?
                """, (store_id, limit))
                
                suggestions = []
                for row in cursor.fetchall():
                    suggestions.append({
                        'id': row[0],
                        'store_id': row[1],
                        'week_start': row[2],
                        'strategy': row[3],
                        'suggestion_data': json.loads(row[4]),
                        'explanation': row[5],
                        'total_investment': row[6],
                        'expected_revenue': row[7],
                        'roi_percentage': row[8],
                        'risk_level': row[9],
                        'created_at': row[10],
                        'store_name': row[11]
                    })
                
                return suggestions
                
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo sugerencias para tienda {store_id}: {e}")
            return []
    
    def get_all_suggestions(self, limit: int = 100) -> List[dict]:
        """
        Obtiene todas las sugerencias
        
        Args:
            limit: Número máximo de sugerencias a retornar
            
        Returns:
            Lista de todas las sugerencias
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT s.*, st.name as store_name, st.city
                FROM suggestions s
                JOIN stores st ON s.store_id = st.id
                ORDER BY s.created_at DESC
                LIMIT ?
                """, (limit,))
                
                suggestions = []
                for row in cursor.fetchall():
                    suggestions.append({
                        'id': row[0],
                        'store_id': row[1],
                        'week_start': row[2],
                        'strategy': row[3],
                        'suggestion_data': json.loads(row[4]),
                        'explanation': row[5],
                        'total_investment': row[6],
                        'expected_revenue': row[7],
                        'roi_percentage': row[8],
                        'risk_level': row[9],
                        'created_at': row[10],
                        'store_name': row[11],
                        'store_city': row[12]
                    })
                
                return suggestions
                
        except sqlite3.Error as e:
            logger.error(f"Error obteniendo todas las sugerencias: {e}")
            return []


# Instancia global del servicio
db_service = DatabaseService()