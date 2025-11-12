# Sistema de Gestión de Mermas y Rupturas
# Maneja el registro de productos averiados/dañados separadamente del inventario normal

import json
import os
from datetime import datetime, date
from typing import Dict, List, Any, Optional
import pandas as pd

# Archivo donde se almacenarán las mermas
MERMAS_FILE = "mermas_rupturas.json"

class MermasManager:
    """
    Gestiona el registro de mermas y rupturas de productos.
    Mantiene un registro separado del inventario normal.
    """
    
    def __init__(self):
        self.archivo_mermas = MERMAS_FILE
        self._asegurar_archivo_existe()
    
    def _asegurar_archivo_existe(self):
        """Crea el archivo de mermas si no existe"""
        if not os.path.exists(self.archivo_mermas):
            data_inicial = {
                "version": "1.0",
                "mermas_por_tienda": {},
                "ultima_actualizacion": datetime.now().isoformat(),
                "total_registros": 0
            }
            with open(self.archivo_mermas, 'w', encoding='utf-8') as f:
                json.dump(data_inicial, f, indent=2, ensure_ascii=False)
    
    def _cargar_datos(self) -> Dict[str, Any]:
        """Carga todos los datos de mermas desde el archivo"""
        try:
            with open(self.archivo_mermas, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Si hay error, recrear archivo
            self._asegurar_archivo_existe()
            with open(self.archivo_mermas, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def _guardar_datos(self, data: Dict[str, Any]) -> bool:
        """Guarda todos los datos de mermas en el archivo"""
        try:
            data["ultima_actualizacion"] = datetime.now().isoformat()
            with open(self.archivo_mermas, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando mermas: {e}")
            return False
    
    def registrar_merma(self, tienda_id: str, usuario: str, fecha: date, 
                       categoria: str, producto: str, cantidad: int, 
                       motivo: str = "Ruptura", observaciones: str = "") -> bool:
        """
        Registra una nueva merma/ruptura
        
        Args:
            tienda_id: ID de la tienda
            usuario: Usuario que registra la merma
            fecha: Fecha de la merma
            categoria: Categoría del producto (Impulsivo/Extras)
            producto: Nombre del producto
            cantidad: Cantidad perdida/averiada
            motivo: Motivo de la merma (Ruptura, Vencimiento, etc.)
            observaciones: Observaciones adicionales
            
        Returns:
            bool: True si se registró exitosamente
        """
        try:
            data = self._cargar_datos()
            fecha_str = fecha.strftime("%Y-%m-%d") if isinstance(fecha, date) else str(fecha)
            
            # Asegurar estructura de tienda
            if "mermas_por_tienda" not in data:
                data["mermas_por_tienda"] = {}
            
            if tienda_id not in data["mermas_por_tienda"]:
                data["mermas_por_tienda"][tienda_id] = []
            
            # Crear registro de merma
            registro_merma = {
                "id": len(data["mermas_por_tienda"][tienda_id]) + 1,
                "fecha": fecha_str,
                "hora": datetime.now().strftime("%H:%M:%S"),
                "tienda_id": tienda_id,
                "usuario": usuario,
                "categoria": categoria,
                "producto": producto,
                "cantidad": cantidad,
                "motivo": motivo,
                "observaciones": observaciones,
                "timestamp": datetime.now().isoformat()
            }
            
            # Agregar registro
            data["mermas_por_tienda"][tienda_id].append(registro_merma)
            data["total_registros"] = data.get("total_registros", 0) + 1
            
            return self._guardar_datos(data)
            
        except Exception as e:
            print(f"Error registrando merma: {e}")
            return False
    
    def obtener_mermas_tienda(self, tienda_id: str, fecha_inicio: Optional[date] = None, 
                             fecha_fin: Optional[date] = None) -> List[Dict]:
        """
        Obtiene todas las mermas de una tienda, opcionalmente filtradas por fecha
        
        Args:
            tienda_id: ID de la tienda
            fecha_inicio: Fecha de inicio del filtro (opcional)
            fecha_fin: Fecha de fin del filtro (opcional)
            
        Returns:
            List[Dict]: Lista de registros de mermas
        """
        try:
            data = self._cargar_datos()
            mermas_tienda = data.get("mermas_por_tienda", {}).get(tienda_id, [])
            
            # Filtrar por fechas si se especifica
            if fecha_inicio or fecha_fin:
                mermas_filtradas = []
                fecha_inicio_str = fecha_inicio.strftime("%Y-%m-%d") if fecha_inicio else "1900-01-01"
                fecha_fin_str = fecha_fin.strftime("%Y-%m-%d") if fecha_fin else "2100-12-31"
                
                for merma in mermas_tienda:
                    fecha_merma = merma.get("fecha", "")
                    if fecha_inicio_str <= fecha_merma <= fecha_fin_str:
                        mermas_filtradas.append(merma)
                
                return mermas_filtradas
            
            return mermas_tienda
            
        except Exception as e:
            print(f"Error obteniendo mermas de tienda: {e}")
            return []
    
    def obtener_todas_las_mermas(self, fecha_inicio: Optional[date] = None, 
                                fecha_fin: Optional[date] = None) -> List[Dict]:
        """
        Obtiene todas las mermas de todas las tiendas
        
        Args:
            fecha_inicio: Fecha de inicio del filtro (opcional)
            fecha_fin: Fecha de fin del filtro (opcional)
            
        Returns:
            List[Dict]: Lista de todos los registros de mermas
        """
        try:
            data = self._cargar_datos()
            todas_las_mermas = []
            
            for tienda_id, mermas in data.get("mermas_por_tienda", {}).items():
                todas_las_mermas.extend(mermas)
            
            # Filtrar por fechas si se especifica
            if fecha_inicio or fecha_fin:
                mermas_filtradas = []
                fecha_inicio_str = fecha_inicio.strftime("%Y-%m-%d") if fecha_inicio else "1900-01-01"
                fecha_fin_str = fecha_fin.strftime("%Y-%m-%d") if fecha_fin else "2100-12-31"
                
                for merma in todas_las_mermas:
                    fecha_merma = merma.get("fecha", "")
                    if fecha_inicio_str <= fecha_merma <= fecha_fin_str:
                        mermas_filtradas.append(merma)
                
                return mermas_filtradas
            
            return todas_las_mermas
            
        except Exception as e:
            print(f"Error obteniendo todas las mermas: {e}")
            return []
    
    def obtener_resumen_mermas(self, tienda_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene un resumen estadístico de las mermas
        
        Args:
            tienda_id: ID de tienda específica (opcional, si no se especifica es global)
            
        Returns:
            Dict con estadísticas de mermas
        """
        try:
            if tienda_id:
                mermas = self.obtener_mermas_tienda(tienda_id)
            else:
                mermas = self.obtener_todas_las_mermas()
            
            # Calcular estadísticas
            total_registros = len(mermas)
            total_cantidad = sum(m.get("cantidad", 0) for m in mermas)
            
            # Resumen por categoría
            por_categoria = {}
            for merma in mermas:
                categoria = merma.get("categoria", "Sin categoría")
                if categoria not in por_categoria:
                    por_categoria[categoria] = {"registros": 0, "cantidad": 0}
                por_categoria[categoria]["registros"] += 1
                por_categoria[categoria]["cantidad"] += merma.get("cantidad", 0)
            
            # Resumen por motivo
            por_motivo = {}
            for merma in mermas:
                motivo = merma.get("motivo", "Sin motivo")
                if motivo not in por_motivo:
                    por_motivo[motivo] = {"registros": 0, "cantidad": 0}
                por_motivo[motivo]["registros"] += 1
                por_motivo[motivo]["cantidad"] += merma.get("cantidad", 0)
            
            # Productos más afectados
            productos_afectados = {}
            for merma in mermas:
                producto = merma.get("producto", "Sin producto")
                if producto not in productos_afectados:
                    productos_afectados[producto] = 0
                productos_afectados[producto] += merma.get("cantidad", 0)
            
            # Ordenar productos por cantidad (top 10)
            top_productos = sorted(productos_afectados.items(), 
                                 key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "total_registros": total_registros,
                "total_cantidad": total_cantidad,
                "por_categoria": por_categoria,
                "por_motivo": por_motivo,
                "top_productos_afectados": top_productos
            }
            
        except Exception as e:
            print(f"Error obteniendo resumen de mermas: {e}")
            return {
                "total_registros": 0,
                "total_cantidad": 0,
                "por_categoria": {},
                "por_motivo": {},
                "top_productos_afectados": []
            }
    
    def exportar_a_excel(self, tienda_id: Optional[str] = None, 
                        fecha_inicio: Optional[date] = None,
                        fecha_fin: Optional[date] = None) -> bytes:
        """
        Exporta los datos de mermas a Excel
        
        Args:
            tienda_id: ID de tienda específica (opcional)
            fecha_inicio: Fecha de inicio del filtro (opcional)
            fecha_fin: Fecha de fin del filtro (opcional)
            
        Returns:
            bytes: Contenido del archivo Excel
        """
        try:
            # Obtener datos
            if tienda_id:
                mermas = self.obtener_mermas_tienda(tienda_id, fecha_inicio, fecha_fin)
            else:
                mermas = self.obtener_todas_las_mermas(fecha_inicio, fecha_fin)
            
            # Crear DataFrame
            if not mermas:
                # DataFrame vacío si no hay datos
                df = pd.DataFrame(columns=[
                    'ID', 'Fecha', 'Hora', 'Tienda', 'Usuario', 'Categoría', 
                    'Producto', 'Cantidad', 'Motivo', 'Observaciones'
                ])
            else:
                df = pd.DataFrame([
                    {
                        'ID': m.get('id', ''),
                        'Fecha': m.get('fecha', ''),
                        'Hora': m.get('hora', ''),
                        'Tienda': m.get('tienda_id', ''),
                        'Usuario': m.get('usuario', ''),
                        'Categoría': m.get('categoria', ''),
                        'Producto': m.get('producto', ''),
                        'Cantidad': m.get('cantidad', 0),
                        'Motivo': m.get('motivo', ''),
                        'Observaciones': m.get('observaciones', '')
                    }
                    for m in mermas
                ])
            
            # Crear Excel en memoria
            from io import BytesIO
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Hoja principal con datos
                df.to_excel(writer, sheet_name='Mermas y Rupturas', index=False)
                
                # Hoja de resumen si hay datos
                if not df.empty:
                    resumen = self.obtener_resumen_mermas(tienda_id)
                    
                    # Crear DataFrame de resumen
                    resumen_data = [
                        ['Total de registros', resumen['total_registros']],
                        ['Total cantidad afectada', resumen['total_cantidad']],
                        ['', ''],  # Línea vacía
                        ['RESUMEN POR CATEGORÍA', ''],
                    ]
                    
                    for categoria, datos in resumen['por_categoria'].items():
                        resumen_data.append([f"{categoria}", f"{datos['cantidad']} unidades ({datos['registros']} registros)"])
                    
                    resumen_data.append(['', ''])  # Línea vacía
                    resumen_data.append(['RESUMEN POR MOTIVO', ''])
                    
                    for motivo, datos in resumen['por_motivo'].items():
                        resumen_data.append([f"{motivo}", f"{datos['cantidad']} unidades ({datos['registros']} registros)"])
                    
                    resumen_df = pd.DataFrame(resumen_data, columns=['Concepto', 'Valor'])
                    resumen_df.to_excel(writer, sheet_name='Resumen', index=False)
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            print(f"Error exportando a Excel: {e}")
            # Retornar Excel vacío en caso de error
            from io import BytesIO
            output = BytesIO()
            df_vacio = pd.DataFrame(columns=['Error'])
            df_vacio.to_excel(output, index=False)
            output.seek(0)
            return output.getvalue()
    
    def eliminar_merma(self, tienda_id: str, merma_id: int) -> bool:
        """
        Elimina un registro de merma específico
        
        Args:
            tienda_id: ID de la tienda
            merma_id: ID del registro de merma
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            data = self._cargar_datos()
            
            if tienda_id in data.get("mermas_por_tienda", {}):
                mermas_tienda = data["mermas_por_tienda"][tienda_id]
                # Buscar y eliminar el registro
                for i, merma in enumerate(mermas_tienda):
                    if merma.get("id") == merma_id:
                        del mermas_tienda[i]
                        data["total_registros"] = data.get("total_registros", 1) - 1
                        return self._guardar_datos(data)
            
            return False
            
        except Exception as e:
            print(f"Error eliminando merma: {e}")
            return False

# Instancia global del gestor de mermas
mermas_manager = MermasManager()