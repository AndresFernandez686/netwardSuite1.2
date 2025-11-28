"""
Servicio de Sincronización de Inventario en Tiempo Real
Conecta el módulo de Inventario con el módulo de Sugerencias
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import streamlit as st

class InventorySyncService:
    """Servicio para sincronizar inventario entre módulos"""
    
    def __init__(self):
        # Rutas de archivos
        self.business_root = Path(__file__).parent.parent.parent
        self.inventory_file = self.business_root / "data" / "inventory" / "inventario.json"
        self.sugerencias_cache = self.business_root / "modules" / "sugerencias" / "data" / "inventory_cache.json"
        
        # Mapeo de productos del inventario a sugerencias
        self.product_mapping = self._initialize_product_mapping()
    
    def _initialize_product_mapping(self) -> Dict[str, Dict]:
        """
        Mapea productos del inventario (Netward) al formato de sugerencias (Grido)
        
        Inventario usa:
        - Impulsivo: {producto: {bultos: int, unidad: int}}
        - Por Kilos: {producto: {cajas_cerradas: int, cajas_abiertas: int, kgs_cajas_abiertas: float}}
        - Extras: {producto: {bultos: int, unidad: int}}
        
        Sugerencias usa:
        - producto: {bultos: int, estado: str}
        """
        return {
            # === PALITOS ===
            "Palito Frutal Frutilla": "palito_frutal_frutilla",
            "Palito Frutal Limon": "palito_frutal_limon",
            "Palito Frutal Naranja": "palito_frutal_naranja",
            "Palito Frutal Crema Americana": "palito_frutal_crema_americana",
            "Palito Frutal Crema Frutilla": "palito_frutal_crema_frutilla",
            "Palito Bombon": "palito_bombon",
            
            # === ALFAJORES ===
            "Alfajor Crocantino": "alfajor_crocantino",
            "Alfajor Delicia": "alfajor_delicia",
            "Alfajor Casatta": "alfajor_casatta",
            "Alfajor Almendrado": "alfajor_almendrado",
            
            # === BOMBONES ===
            "Bombon Escoses": "bombon_escoses",
            "Bombon Suizo": "bombon_suizo",
            "Bombon Crocante": "bombon_crocante",
            "Bombon Vainilla Split": "bombon_vainilla_split",
            
            # === FAMILIARES ===
            "Familiar 1": "familiar_1",
            "Familiar 2": "familiar_2",
            "Familiar 3": "familiar_3",
            "Familiar 4": "familiar_4",
            
            # === TORTAS (mapeo genérico) ===
            "Torta 1kg": "torta_1kg",
            "Torta 1.5kg": "torta_1_5kg",
            "Torta 2kg": "torta_2kg",
            
            # === GRANEL - CREMAS ===
            "Crema Americana": "crema_americana",
            "Crema Tramontana": "crema_tramontana",
            "Dulce de Leche": "dulce_de_leche",
            "Granizado": "granizado",
            "Mascarpone": "mascarpone",
            "Chocolate": "chocolate",
            "Frutilla a la Crema": "frutilla_a_la_crema",
            "Durazno a la Crema": "durazno_a_la_crema",
            "Ananá a la Crema": "anana_a_la_crema",
            "Sambayón": "sambayon",
            "Menta Granizada": "menta_granizada",
            "Tiramisú": "tiramisu",
            "Crema del Cielo": "crema_del_cielo",
            "Mousse de Limón": "mousse_de_limon",
            "Vainilla": "vainilla",
            "Banana Split": "banana_split",
            "Crema Rusa": "crema_rusa",
            "Flan con Dulce de Leche": "flan_con_dulce_de_leche",
            
            # === GRANEL - AGUA ===
            "Frutilla": "frutilla",
            "Limón": "limon",
            "Ananá": "anana",
            "Naranja": "naranja",
            "Cereza": "cereza",
            "Kiwi": "kiwi",
            "Melón": "melon",
            "Sandía": "sandia",
            "Durazno": "durazno",
            "Frambuesa": "frambuesa",
            "Mango": "mango",
            "Maracuyá": "maracuya",
            "Uva": "uva",
            "Mandarina": "mandarina",
            "Coco": "coco",
            "Pomelo": "pomelo",
            "Mora": "mora",
            "Limón Menta": "limon_menta"
        }
    
    def _calculate_stock_status(self, bultos: int, categoria: str) -> str:
        """
        Calcula el estado del stock basado en cantidad de bultos
        
        Lógica:
        - SIN STOCK: 0 bultos
        - STOCK BAJO: 1-2 bultos (impulsivo) o 1-3 bultos (granel)
        - STOCK OK: 3+ bultos
        """
        if bultos == 0:
            return "SIN STOCK"
        elif categoria == "Por Kilos":
            # Granel: más tolerante
            if bultos <= 3:
                return "STOCK BAJO"
            else:
                return "STOCK OK"
        else:
            # Impulsivo/Extras: más estricto
            if bultos <= 2:
                return "STOCK BAJO"
            else:
                return "STOCK OK"
    
    def read_inventory_from_file(self, tienda_id: str = "T001") -> Dict:
        """
        Lee el inventario directamente del archivo JSON del módulo de inventario
        
        Returns:
            Dict con estructura: {
                "impulsivo": {producto_key: {bultos: int, estado: str}},
                "granel": {producto_key: {bultos: int, estado: str, kgs: float}},
                "metadata": {tienda_id, fecha_sync, total_bultos}
            }
        """
        try:
            if not self.inventory_file.exists():
                return self._empty_inventory_response()
            
            with open(self.inventory_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Obtener inventario de la tienda específica
            inventario_tienda = data.get("inventario_por_tienda", {}).get(tienda_id, {})
            
            if not inventario_tienda:
                return self._empty_inventory_response()
            
            # Procesar inventario
            result = {
                "impulsivo": {},
                "granel": {},
                "metadata": {
                    "tienda_id": tienda_id,
                    "fecha_sync": datetime.now().isoformat(),
                    "total_bultos": 0,
                    "productos_con_stock": 0,
                    "productos_sin_stock": 0
                }
            }
            
            total_bultos = 0
            productos_con_stock = 0
            productos_sin_stock = 0
            
            # Procesar IMPULSIVOS
            impulsivos = inventario_tienda.get("Impulsivo", {})
            for producto, valores in impulsivos.items():
                if isinstance(valores, dict):
                    bultos = valores.get("bultos", 0)
                    unidad = valores.get("unidad", 0)
                    
                    # Buscar mapeo del producto
                    producto_key = self.product_mapping.get(producto)
                    if producto_key:
                        estado = self._calculate_stock_status(bultos, "Impulsivo")
                        result["impulsivo"][producto_key] = {
                            "bultos": bultos,
                            "unidad": unidad,
                            "estado": estado,
                            "producto_original": producto
                        }
                        
                        total_bultos += bultos
                        if bultos > 0:
                            productos_con_stock += 1
                        else:
                            productos_sin_stock += 1
            
            # Procesar GRANEL (Por Kilos)
            por_kilos = inventario_tienda.get("Por Kilos", {})
            for producto, valores in por_kilos.items():
                if isinstance(valores, dict):
                    cajas_cerradas = valores.get("cajas_cerradas", 0)
                    cajas_abiertas = valores.get("cajas_abiertas", 0)
                    kgs_cajas_abiertas = valores.get("kgs_cajas_abiertas", 0.0)
                    
                    # Total de bultos = cajas cerradas + cajas abiertas
                    bultos_totales = cajas_cerradas + cajas_abiertas
                    
                    # Buscar mapeo del producto
                    producto_key = self.product_mapping.get(producto)
                    if producto_key:
                        estado = self._calculate_stock_status(bultos_totales, "Por Kilos")
                        result["granel"][producto_key] = {
                            "bultos": bultos_totales,
                            "cajas_cerradas": cajas_cerradas,
                            "cajas_abiertas": cajas_abiertas,
                            "kgs_totales": (cajas_cerradas * 7.8) + kgs_cajas_abiertas,
                            "estado": estado,
                            "producto_original": producto
                        }
                        
                        total_bultos += bultos_totales
                        if bultos_totales > 0:
                            productos_con_stock += 1
                        else:
                            productos_sin_stock += 1
            
            # Procesar EXTRAS (opcional)
            extras = inventario_tienda.get("Extras", {})
            for producto, valores in extras.items():
                if isinstance(valores, dict):
                    bultos = valores.get("bultos", 0)
                    unidad = valores.get("unidad", 0)
                    
                    producto_key = self.product_mapping.get(producto)
                    if producto_key:
                        estado = self._calculate_stock_status(bultos, "Extras")
                        result["impulsivo"][producto_key] = {
                            "bultos": bultos,
                            "unidad": unidad,
                            "estado": estado,
                            "producto_original": producto
                        }
                        
                        total_bultos += bultos
                        if bultos > 0:
                            productos_con_stock += 1
                        else:
                            productos_sin_stock += 1
            
            # Actualizar metadata
            result["metadata"]["total_bultos"] = total_bultos
            result["metadata"]["productos_con_stock"] = productos_con_stock
            result["metadata"]["productos_sin_stock"] = productos_sin_stock
            result["metadata"]["total_productos"] = productos_con_stock + productos_sin_stock
            
            return result
            
        except Exception as e:
            st.error(f"Error leyendo inventario: {str(e)}")
            return self._empty_inventory_response()
    
    def _empty_inventory_response(self) -> Dict:
        """Retorna respuesta vacía cuando no hay inventario"""
        return {
            "impulsivo": {},
            "granel": {},
            "metadata": {
                "tienda_id": None,
                "fecha_sync": datetime.now().isoformat(),
                "total_bultos": 0,
                "productos_con_stock": 0,
                "productos_sin_stock": 0,
                "total_productos": 0
            }
        }
    
    def sync_to_cache(self, tienda_id: str = "T001") -> bool:
        """
        Sincroniza el inventario actual a un archivo cache para el módulo de sugerencias
        """
        try:
            inventory_data = self.read_inventory_from_file(tienda_id)
            
            # Asegurar que existe la carpeta data
            self.sugerencias_cache.parent.mkdir(parents=True, exist_ok=True)
            
            # Guardar en cache
            with open(self.sugerencias_cache, 'w', encoding='utf-8') as f:
                json.dump(inventory_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            st.error(f"Error sincronizando inventario: {str(e)}")
            return False
    
    def get_cached_inventory(self) -> Optional[Dict]:
        """Obtiene el inventario desde el cache"""
        try:
            if not self.sugerencias_cache.exists():
                return None
            
            with open(self.sugerencias_cache, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error leyendo cache: {str(e)}")
            return None
    
    def get_inventory_summary(self, tienda_id: str = "T001") -> Dict:
        """
        Obtiene un resumen ejecutivo del inventario
        """
        inventory = self.read_inventory_from_file(tienda_id)
        metadata = inventory["metadata"]
        
        # Clasificar por estado
        stock_ok = 0
        stock_bajo = 0
        sin_stock = 0
        
        for producto in list(inventory["impulsivo"].values()) + list(inventory["granel"].values()):
            if producto["estado"] == "STOCK OK":
                stock_ok += 1
            elif producto["estado"] == "STOCK BAJO":
                stock_bajo += 1
            elif producto["estado"] == "SIN STOCK":
                sin_stock += 1
        
        return {
            "tienda_id": metadata["tienda_id"],
            "total_bultos": metadata["total_bultos"],
            "total_productos": metadata["total_productos"],
            "stock_ok": stock_ok,
            "stock_bajo": stock_bajo,
            "sin_stock": sin_stock,
            "fecha_sync": metadata["fecha_sync"],
            "impulsivos_count": len(inventory["impulsivo"]),
            "granel_count": len(inventory["granel"])
        }
    
    def force_sync(self, tienda_id: str = "T001") -> Tuple[bool, str]:
        """
        Fuerza una sincronización inmediata del inventario
        
        Returns:
            (success: bool, message: str)
        """
        try:
            # Leer inventario actual
            inventory = self.read_inventory_from_file(tienda_id)
            
            if inventory["metadata"]["total_productos"] == 0:
                return False, "❌ No se encontró inventario para sincronizar"
            
            # Sincronizar a cache
            success = self.sync_to_cache(tienda_id)
            
            if success:
                summary = self.get_inventory_summary(tienda_id)
                message = f"""
                ✅ Sincronización exitosa!
                
                📊 Resumen:
                - Total productos: {summary['total_productos']}
                - Total bultos: {summary['total_bultos']}
                - Stock OK: {summary['stock_ok']}
                - Stock Bajo: {summary['stock_bajo']}
                - Sin Stock: {summary['sin_stock']}
                - Impulsivos: {summary['impulsivos_count']}
                - Granel: {summary['granel_count']}
                """
                return True, message
            else:
                return False, "❌ Error al guardar cache de sincronización"
                
        except Exception as e:
            return False, f"❌ Error en sincronización: {str(e)}"

# Instancia global del servicio
inventory_sync_service = InventorySyncService()
