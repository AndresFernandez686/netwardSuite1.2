"""
Motor de sugerencias inteligente para heladerías Grido
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

from ..models.data_models import (
    Store, WeatherData, WeeklySuggestion, 
    ProductDemand, DailyAnalysis
)
from ..config.settings import (
    PRODUCT_SPECS, PARAGUAY_HOLIDAYS, 
    TEMP_FACTORS, STRATEGIES
)

logger = logging.getLogger(__name__)


class SuggestionEngine:
    """Motor principal para generar sugerencias inteligentes"""
    
    def __init__(self):
        self.product_specs = PRODUCT_SPECS
        self.holidays = PARAGUAY_HOLIDAYS
        self.temp_factors = TEMP_FACTORS
        self.strategies = STRATEGIES
    
    def generate_weekly_suggestion(
        self, 
        store: Store, 
        weather_data: List[WeatherData], 
        strategy: str = "balanceada",
        current_inventory: List[Dict] = None
    ) -> WeeklySuggestion:
        """
        Genera sugerencia semanal completa para una tienda
        
        Args:
            store: Información de la tienda
            weather_data: Datos del clima para la semana
            strategy: Estrategia de compra
            current_inventory: Inventario actual de la tienda (opcional)
            
        Returns:
            WeeklySuggestion con las recomendaciones
        """
        try:
            # Validar estrategia
            if strategy not in self.strategies:
                strategy = "balanceada"
            
            strategy_config = self.strategies[strategy]
            
            # Análisis diario
            daily_analysis = self._analyze_daily_factors(weather_data)
            
            # Calcular factor promedio de la semana
            avg_factor = sum(day.combined_factor for day in daily_analysis) / len(daily_analysis)
            
            # Procesar inventario actual si está disponible
            inventory_dict = {}
            low_stock_products = []
            out_of_stock_products = []
            stock_ok_products = []
            products_in_inventory = set()  # Productos que están en el inventario
            stock_status_info = {}  # {nombre_producto: {'bultos': int, 'estado': str}}
            total_bultos_actuales = 0  # NUEVO: Contador de bultos actuales
            
            if current_inventory:
                for item in current_inventory:
                    product_name = item.get('Producto', '')
                    bultos = item.get('Bultos', 0)
                    estado_stock = item.get('Estado Stock', '')
                    
                    # Sumar bultos actuales
                    total_bultos_actuales += bultos
                    
                    inventory_dict[product_name] = {
                        'bultos': bultos,
                        'estado': estado_stock
                    }
                    
                    # Agregar a lista de productos en inventario
                    products_in_inventory.add(product_name)
                    
                    # Guardar info de stock para todos los productos
                    stock_status_info[product_name] = {
                        'bultos': bultos,
                        'estado': estado_stock
                    }
                    
                    # Clasificar productos según su estado
                    if estado_stock == 'STOCK BAJO':
                        low_stock_products.append(product_name)
                    elif estado_stock == 'SIN STOCK' or bultos == 0:
                        out_of_stock_products.append(product_name)
                    elif estado_stock == 'STOCK OK':
                        stock_ok_products.append(product_name)
            
            # Obtener capacidad de almacenamiento
            storage_capacity_total = store.base_demand.get('storage_capacity_bultos', 50)
            
            # CALCULAR CAPACIDAD DISPONIBLE (lo que realmente cabe)
            storage_capacity_disponible = max(0, storage_capacity_total - total_bultos_actuales)
            
            # CALCULAR FACTOR CLIMÁTICO DE LA SEMANA
            # Para helados, usamos TEMPERATURA MÁXIMA (cuando hace más calor y más se vende)
            temps_max_semana = [day.temp_max for day in weather_data if hasattr(day, 'temp_max')]
            temp_promedio_semana = sum(temps_max_semana) / len(temps_max_semana) if temps_max_semana else 25.0
            
            logger.info(f"🌡️ Temperaturas MÁXIMAS de la semana ({len(temps_max_semana)} días): {[f'{t:.1f}°C' for t in temps_max_semana]}")
            logger.info(f"🌡️ Promedio de máximas semanal: {temp_promedio_semana:.1f}°C")
            
            # Determinar modificador climático basado en temperatura MÁXIMA promedio
            # Temperatura ALTA (>32°C) = +1 bulto por alta demanda
            # Temperatura BAJA (<22°C) = -1 bulto por baja demanda  
            # Temperatura NORMAL (22-32°C) = sin cambio
            if temp_promedio_semana > 32:
                climate_modifier = 1
                climate_description = f"🔥 CALOR ALTO (máx. promedio {temp_promedio_semana:.1f}°C en {len(temps_max_semana)} días): +1 bulto"
            elif temp_promedio_semana < 22:
                climate_modifier = -1
                climate_description = f"❄️ FRÍO (máx. promedio {temp_promedio_semana:.1f}°C en {len(temps_max_semana)} días): -1 bulto"
            else:
                climate_modifier = 0
                climate_description = f"🌤️ NORMAL (máx. promedio {temp_promedio_semana:.1f}°C en {len(temps_max_semana)} días): sin cambio"
            
            logger.info(f"📦 Capacidad total de almacenamiento: {storage_capacity_total} bultos")
            logger.info(f"📊 Bultos actuales en inventario: {total_bultos_actuales} bultos")
            logger.info(f"✅ Capacidad DISPONIBLE para nuevas compras: {storage_capacity_disponible} bultos")
            logger.info(f"{climate_description}")
            logger.info(f"Productos en inventario: {len(products_in_inventory)}")
            logger.info(f"STOCK BAJO: {len(low_stock_products)}, SIN STOCK: {len(out_of_stock_products)}, STOCK OK: {len(stock_ok_products)}")
            
            # PASO 1: Calcular sugerencias para TODOS los productos del inventario
            ideal_suggestions = []
            processed_products = set()  # Evitar duplicados
            
            # Si hay inventario cargado, procesar TODOS los productos del inventario
            if current_inventory and len(products_in_inventory) > 0:
                logger.info("Procesando TODOS los productos del inventario cargado")
                
                for inv_product_name in products_in_inventory:
                    # Obtener metadata del producto del inventario
                    inv_product_data = next((item for item in current_inventory if item.get('Producto') == inv_product_name), None)
                    tipo_esperado = inv_product_data.get('_tipo_producto', None) if inv_product_data else None
                    
                    # Buscar el product_id correspondiente en PRODUCT_SPECS
                    matched_product_id = None
                    matched_spec = None
                    best_match_score = 0
                    
                    for pid, spec in self.product_specs.items():
                        spec_name = spec.get('name', '')
                        inv_lower = inv_product_name.lower()
                        spec_lower = spec_name.lower()
                        
                        # FILTRAR POR TIPO: Si el inventario tiene tipo, verificar que coincida
                        if tipo_esperado:
                            producto_tipo = spec.get('tipo_producto', 'impulsivo')
                            if producto_tipo != tipo_esperado:
                                continue  # Saltar productos de otro tipo
                        
                        # Calcular score de coincidencia (más específico = mejor)
                        if spec_lower == inv_lower:
                            match_score = 100  # Coincidencia exacta
                        elif spec_lower in inv_lower:
                            match_score = len(spec_lower)  # Más largo = más específico
                        elif inv_lower in spec_lower:
                            match_score = len(inv_lower)
                        else:
                            continue
                        
                        # Quedarse con la mejor coincidencia
                        if match_score > best_match_score:
                            best_match_score = match_score
                            matched_product_id = pid
                            matched_spec = spec
                    
                    if not matched_product_id:
                        tipo_msg = f" (tipo: {tipo_esperado})" if tipo_esperado else ""
                        logger.warning(f"No se encontró producto en catálogo para: {inv_product_name}{tipo_msg}")
                        continue
                    
                    # Evitar duplicados
                    if matched_product_id in processed_products:
                        logger.info(f"Producto ya procesado, omitiendo duplicado: {inv_product_name}")
                        continue
                    
                    processed_products.add(matched_product_id)
                    logger.info(f"✓ Match: '{inv_product_name}' → {matched_product_id} ({matched_spec.get('tipo_producto', 'unknown')})")
                    
                    # Obtener base_demand o usar valor por defecto
                    base_demand = store.base_demand.get(matched_product_id, 10.0)  # Default: 10 unidades/semana
                    
                    suggestion = self._calculate_product_suggestion(
                        matched_product_id, 
                        base_demand, 
                        avg_factor, 
                        strategy_config
                    )
                    
                    # Calcular prioridad
                    priority_score = self._calculate_priority(matched_spec, base_demand, suggestion)
                    
                    ideal_suggestions.append({
                        'suggestion': suggestion,
                        'spec': matched_spec,
                        'priority': priority_score,
                        'inv_name': inv_product_name  # Guardar nombre del inventario
                    })
                    
            else:
                # Modo legacy: usar base_demand de la tienda
                logger.info("Modo legacy: usando base_demand de la tienda")
                for product_id, base_demand in store.base_demand.items():
                    if product_id == "storage_capacity_bultos":
                        continue
                    
                    if product_id in self.product_specs and base_demand > 0:
                        spec = self.product_specs[product_id]
                        
                        suggestion = self._calculate_product_suggestion(
                            product_id, 
                            base_demand, 
                            avg_factor, 
                            strategy_config
                        )
                        
                        priority_score = self._calculate_priority(spec, base_demand, suggestion)
                        
                        ideal_suggestions.append({
                            'suggestion': suggestion,
                            'spec': spec,
                            'priority': priority_score
                        })
            
            # PASO 2: Ordenar por prioridad (mayor a menor)
            ideal_suggestions.sort(key=lambda x: x['priority'], reverse=True)
            
            # PASO 3: Distribuir bultos respetando el límite
            product_suggestions = []
            total_bulks_allocated = 0
            total_investment = 0.0
            total_expected_revenue = 0.0
            
            # Reservar espacio para granel (siempre prioritario)
            granel_bulks = 0
            granel_suggestion = None
            for item in ideal_suggestions:
                if item['suggestion'].product_id == 'caja_granel':
                    granel_suggestion = item
                    # Calcular granel necesario para productos servidos
                    granel_bulks = min(item['suggestion'].suggested_bulks, int(storage_capacity_disponible * 0.4))  # Máximo 40% del espacio
                    total_bulks_allocated += granel_bulks
                    break
            
            # Distribuir resto de bultos
            remaining_capacity = storage_capacity_disponible - total_bulks_allocated
            
            for item in ideal_suggestions:
                product_id = item['suggestion'].product_id
                
                # Saltar granel (ya procesado)
                if product_id == 'caja_granel':
                    continue
                
                # Saltar productos servidos (no ocupan espacio adicional)
                if item['spec'].get('category') == 'served':
                    # Solo agregar a la lista, no consumen bultos
                    product_suggestions.append(item['suggestion'])
                    
                    # Revenue de productos servidos
                    if item['spec'].get('price_sale'):
                        product_revenue = item['suggestion'].suggested_quantity * item['spec']['price_sale']
                        total_expected_revenue += product_revenue
                    continue
                
                # Calcular cuántos bultos asignar a este producto
                ideal_bulks = item['suggestion'].suggested_bulks
                
                if total_bulks_allocated + ideal_bulks <= remaining_capacity + total_bulks_allocated:
                    # Cabe completo
                    allocated_bulks = ideal_bulks
                else:
                    # Asignar lo que queda (mínimo 1 si hay espacio)
                    allocated_bulks = max(0, remaining_capacity - (total_bulks_allocated - granel_bulks))
                    if allocated_bulks == 0:
                        continue  # No hay espacio
                
                # APLICAR BONUS SEGÚN ESTADO DE STOCK
                # Usar el nombre del inventario si está disponible, sino el nombre del spec
                inv_name_for_match = item.get('inv_name', item['spec'].get('name', ''))
                product_name = item['spec'].get('name', '')
                bonus_bulks = 0
                
                # Buscar el producto en el inventario por el nombre exacto del inventario
                stock_info = stock_status_info.get(inv_name_for_match)
                
                if not stock_info:
                    # Si no hay coincidencia exacta, buscar por similitud
                    for inv_name, info in stock_status_info.items():
                        inv_lower = inv_name.lower()
                        prod_lower = inv_name_for_match.lower()
                        
                        if inv_lower == prod_lower or inv_lower in prod_lower or prod_lower in inv_lower:
                            stock_info = info
                            logger.info(f"Coincidencia por similitud: '{inv_name}' <-> '{inv_name_for_match}'")
                            break
                
                if stock_info:
                    estado = stock_info['estado'].upper()
                    bultos_actual = stock_info['bultos']
                    
                    logger.info(f"Procesando: {inv_name_for_match} | Estado: {estado} | Bultos actuales: {bultos_actual}")
                    
                    if 'OK' in estado:
                        # STOCK OK: Sugerir SOLO si tiene 1-2 bultos (necesita reposición leve)
                        # 3+ bultos = stock suficiente, NO sugerir
                        if bultos_actual <= 2:
                            bonus_bulks = 1
                            logger.info(f"✓ STOCK OK ({bultos_actual} bultos actuales ≤ 2): +{bonus_bulks} bulto para mantener stock")
                        else:
                            # 3 o más bultos = stock suficiente, saltar
                            logger.info(f"⊗ STOCK OK ({bultos_actual} bultos actuales ≥ 3): STOCK SUFICIENTE, no se sugiere")
                            continue  # Saltar este producto completamente
                    elif 'BAJO' in estado:
                        # STOCK BAJO: +2 bultos (necesita reposición)
                        bonus_bulks = 2
                        logger.info(f"⚠ STOCK BAJO: +{bonus_bulks} bultos")
                    elif 'SIN' in estado or bultos_actual == 0:
                        # SIN STOCK: +2 a +3 bultos según clima
                        bonus_bulks = 3 if avg_factor > 1.5 else 2
                        logger.info(f"✗ SIN STOCK: +{bonus_bulks} bultos")
                    
                    # APLICAR MODIFICADOR CLIMÁTICO
                    # El clima modifica la cantidad final (+1 si calor, -1 si frío)
                    bulks_con_clima = bonus_bulks + climate_modifier
                    # Asegurar que nunca sea menor a 0
                    bulks_con_clima = max(0, bulks_con_clima)
                    
                    if climate_modifier != 0:
                        logger.info(f"🌡️ Factor climático: {bonus_bulks} → {bulks_con_clima} bultos ({'+' if climate_modifier > 0 else ''}{climate_modifier})")
                    
                    # IMPORTANTE: Cuando hay info de stock, USAR SOLO el bonus_bulks con clima
                    # Ignorar allocated_bulks (que viene de demanda base)
                    final_allocated_bulks = min(bulks_con_clima, storage_capacity_disponible - total_bulks_allocated)
                else:
                    logger.warning(f"Sin info de stock: {inv_name_for_match}")
                    # Sin info de stock, usar demanda base calculada con clima
                    bulks_con_clima = max(0, allocated_bulks + climate_modifier)
                    final_allocated_bulks = min(bulks_con_clima, storage_capacity_disponible - total_bulks_allocated)
                
                if final_allocated_bulks <= 0:
                    continue  # No hay espacio para este producto
                
                # Actualizar sugerencia con bultos ajustados
                adjusted_suggestion = ProductDemand(
                    product_id=item['suggestion'].product_id,
                    product_name=item['suggestion'].product_name,
                    base_daily_demand=item['suggestion'].base_daily_demand,
                    projected_weekly_demand=item['suggestion'].projected_weekly_demand,
                    suggested_quantity=final_allocated_bulks * item['suggestion'].bulk_size,
                    unit=item['suggestion'].unit,
                    bulk_size=item['suggestion'].bulk_size,
                    suggested_bulks=final_allocated_bulks,
                    confidence=item['suggestion'].confidence
                )
                
                product_suggestions.append(adjusted_suggestion)
                total_bulks_allocated += final_allocated_bulks  # Actualizar con bultos finales
                
                # Calcular costos e ingresos con bultos finales
                if item['spec'].get('price_cost_box'):
                    # Multiplicar por boxes_per_bulk para obtener el costo total
                    # Ejemplo: 4 bultos × 10 cajas × ₱64,000 = ₱2,560,000
                    boxes_per_bulk = item['spec'].get('boxes_per_bulk', 1)
                    product_cost = final_allocated_bulks * boxes_per_bulk * item['spec']['price_cost_box']
                    total_investment += product_cost
                
                if item['spec'].get('price_sale'):
                    product_revenue = adjusted_suggestion.suggested_quantity * item['spec']['price_sale']
                    total_expected_revenue += product_revenue
                elif item['spec'].get('price_sale_unit'):
                    product_revenue = adjusted_suggestion.suggested_quantity * item['spec']['price_sale_unit']
                    total_expected_revenue += product_revenue
            
            # Agregar granel al final
            if granel_suggestion:
                granel_adjusted = ProductDemand(
                    product_id='caja_granel',
                    product_name=granel_suggestion['suggestion'].product_name,
                    base_daily_demand=granel_suggestion['suggestion'].base_daily_demand,
                    projected_weekly_demand=granel_suggestion['suggestion'].projected_weekly_demand,
                    suggested_quantity=granel_bulks * granel_suggestion['suggestion'].bulk_size,
                    unit=granel_suggestion['suggestion'].unit,
                    bulk_size=granel_suggestion['suggestion'].bulk_size,
                    suggested_bulks=granel_bulks,
                    confidence=granel_suggestion['suggestion'].confidence
                )
                product_suggestions.insert(0, granel_adjusted)
                
                # Costo del granel
                granel_cost = granel_bulks * 150000  # ₱150.000 por caja
                total_investment += granel_cost
            
            logger.info(f"Bultos asignados: {total_bulks_allocated}/{storage_capacity_disponible} disponibles ({total_bultos_actuales + total_bulks_allocated}/{storage_capacity_total} totales)")
            logger.info(f"Inversión total: ₱{total_investment:,.0f}")
            
            # Calcular ROI esperado
            expected_roi = total_expected_revenue / total_investment if total_investment > 0 else 0
            
            # Generar explicación considerando el inventario
            explanation = self._generate_explanation(
                daily_analysis, 
                strategy, 
                avg_factor,
                low_stock_products,
                out_of_stock_products
            )
            
            # Crear sugerencia semanal
            suggestion = WeeklySuggestion(
                store_id=store.id or 1,
                week_start=weather_data[0].date if weather_data else datetime.now().strftime('%Y-%m-%d'),
                strategy=strategy,
                total_investment=total_investment,
                expected_revenue=total_expected_revenue,
                expected_roi=expected_roi,
                risk_level=self._assess_risk_level(expected_roi),
                product_suggestions=product_suggestions,
                daily_analysis=daily_analysis,
                explanation=explanation,
                capacidad_total=storage_capacity_total,
                capacidad_actual=total_bultos_actuales,
                capacidad_disponible=storage_capacity_disponible,
                temperatura_promedio_semana=temp_promedio_semana,
                factor_climatico=climate_modifier,
                descripcion_clima=climate_description
            )
            
            return suggestion
            
        except Exception as e:
            logger.error(f"Error generando sugerencia: {e}")
            raise
    
    def _analyze_daily_factors(self, weather_data: List[WeatherData]) -> List[DailyAnalysis]:
        """
        Analiza factores de demanda para cada día
        
        Args:
            weather_data: Datos del clima por día
            
        Returns:
            Lista de análisis diario
        """
        daily_analysis = []
        
        for weather in weather_data:
            # Factor de temperatura
            temp_factor = weather.get_temp_factor()
            
            # Factor de feriado
            is_holiday = weather.date in self.holidays
            holiday_factor = 1.5 if is_holiday else 1.0
            holiday_name = self.holidays.get(weather.date, "")
            
            # Factor de fin de semana
            date_obj = datetime.strptime(weather.date, '%Y-%m-%d')
            is_weekend = date_obj.weekday() >= 5  # Sábado o domingo
            weekend_factor = 1.3 if is_weekend else 1.0
            
            # Factor combinado
            combined_factor = temp_factor * holiday_factor * weekend_factor
            
            analysis = DailyAnalysis(
                date=weather.date,
                weather=weather,
                temp_factor=temp_factor,
                holiday_factor=holiday_factor,
                weekend_factor=weekend_factor,
                combined_factor=combined_factor,
                is_holiday=is_holiday,
                is_weekend=is_weekend,
                holiday_name=holiday_name
            )
            
            daily_analysis.append(analysis)
        
        return daily_analysis
    
    def _calculate_product_suggestion(
        self, 
        product_id: str, 
        base_demand: float, 
        demand_factor: float,
        strategy_config: Dict
    ) -> ProductDemand:
        """
        Calcula sugerencia para un producto específico
        
        Args:
            product_id: ID del producto
            base_demand: Demanda base diaria
            demand_factor: Factor de multiplicación de demanda
            strategy_config: Configuración de la estrategia
            
        Returns:
            ProductDemand con la sugerencia
        """
        spec = self.product_specs[product_id]
        
        # base_demand ya es la demanda SEMANAL (7 días)
        # Aplicar factor de clima/feriados/fin de semana
        weekly_projected = base_demand * demand_factor
        
        # Aplicar factor de estrategia
        strategy_multiplier = strategy_config['target_rotation']
        adjusted_demand = weekly_projected * strategy_multiplier
        
        # Calcular bultos y cantidades necesarias
        if spec.get('per_bulk') and spec.get('per_bulk') > 0:
            # Productos empaquetados con bultos definidos
            bulk_size = spec['per_bulk']
            # Redondear hacia arriba solo si es necesario
            suggested_bulks = max(1, round(adjusted_demand / bulk_size))
            suggested_quantity = suggested_bulks * bulk_size
        elif spec.get('category') == 'bulk':
            # Helado a granel (en kg)
            kg_per_bulk = spec.get('kg_per_bulk', 7.8)
            suggested_bulks = max(1, round(adjusted_demand / kg_per_bulk))
            suggested_quantity = suggested_bulks * kg_per_bulk
            bulk_size = kg_per_bulk
        elif spec.get('category') == 'served':
            # Productos servidos (cucuruchos, potes, batidos)
            # No necesitan bultos - se sirven del granel
            suggested_quantity = int(adjusted_demand)
            suggested_bulks = 0  # No requieren bultos adicionales
            bulk_size = 1  # Unidad individual
        else:
            # Fallback para otros productos
            suggested_quantity = int(adjusted_demand)
            suggested_bulks = max(1, round(adjusted_demand / 10))
            bulk_size = 10
        
        # Calcular confianza basada en múltiples factores
        confidence = 0.75  # Base
        
        # +10% si la demanda es alta y consistente
        if base_demand > 20:
            confidence += 0.10
        elif base_demand > 10:
            confidence += 0.05
        
        # +5% para productos con buena rotación
        if spec.get('category') in ['bulk', 'frozen']:
            confidence += 0.05
        
        # -5% si es producto servido (depende del granel)
        if spec.get('category') == 'served':
            confidence -= 0.05
        
        # Limitar entre 0.6 y 0.95
        confidence = max(0.6, min(0.95, confidence))
        
        return ProductDemand(
            product_id=product_id,
            product_name=spec['name'],
            base_daily_demand=base_demand,
            projected_weekly_demand=weekly_projected,
            suggested_quantity=suggested_quantity,
            unit=spec['unit'],
            bulk_size=bulk_size,
            suggested_bulks=suggested_bulks,
            confidence=confidence
        )
    
    def _calculate_priority(self, spec: Dict, base_demand: float, suggestion) -> float:
        """
        Calcula prioridad de un producto para distribución de espacio
        
        Factores:
        - Margen de ganancia (price_sale vs price_cost)
        - Rotación (demanda base)
        - Categoría (granel es prioritario)
        
        Args:
            spec: Especificación del producto
            base_demand: Demanda base diaria
            suggestion: Sugerencia calculada
            
        Returns:
            Score de prioridad (mayor = más prioritario)
        """
        priority = 0.0
        
        # Factor 1: Margen de ganancia (40% del peso)
        if spec.get('price_cost_box') and spec.get('price_cost_box') > 0:
            if spec.get('price_sale'):
                margin = (spec['price_sale'] - (spec['price_cost_box'] / spec.get('per_bulk', 1))) / spec['price_sale']
            elif spec.get('price_sale_unit'):
                margin = (spec['price_sale_unit'] - (spec['price_cost_box'] / spec.get('per_bulk', 1))) / spec['price_sale_unit']
            else:
                margin = 0.3  # Estimado
            priority += margin * 40
        
        # Factor 2: Rotación/Demanda (30% del peso)
        if base_demand > 0:
            # Normalizar demanda (productos con mayor demanda son más prioritarios)
            rotation_score = min(base_demand / 50, 1.0)  # Normalizar a máximo 50 unidades/día
            priority += rotation_score * 30
        
        # Factor 3: Categoría (30% del peso)
        category_weights = {
            'bulk': 30,      # Granel es crítico
            'frozen': 25,    # Productos congelados
            'served': 20,    # Productos servidos
            'packaged': 15   # Productos empaquetados
        }
        category = spec.get('category', 'packaged')
        priority += category_weights.get(category, 15)
        
        return priority
    
    def _assess_risk_level(self, roi: float) -> str:
        """
        Evalúa el nivel de riesgo basado en ROI
        
        Args:
            roi: Return on Investment proyectado
            
        Returns:
            Nivel de riesgo como string
        """
        if roi >= 1.2:
            return "ALTO"
        elif roi >= 1.0:
            return "MEDIO"
        else:
            return "BAJO"
    
    def _generate_explanation(
        self, 
        daily_analysis: List, 
        strategy: str, 
        avg_factor: float,
        low_stock_products: List[str] = None,
        out_of_stock_products: List[str] = None
    ) -> str:
        """
        Genera explicación detallada de la sugerencia
        
        Args:
            daily_analysis: Análisis diario de factores
            strategy: Estrategia seleccionada
            avg_factor: Factor promedio de demanda
            low_stock_products: Productos con stock bajo
            out_of_stock_products: Productos sin stock
            
        Returns:
            Explicación en formato texto
        """
        explanation_parts = []
        
        # Análisis de clima
        avg_temp = sum(day.temp_factor for day in daily_analysis) / len(daily_analysis) if daily_analysis else 1.0
        if avg_temp > 1.2:
            explanation_parts.append(" **Clima Favorable:** Temperaturas altas esperadas aumentan la demanda de helados significativamente.")
        elif avg_temp < 0.8:
            explanation_parts.append(" **Clima Frío:** Temperaturas bajas pueden reducir la demanda. Se recomienda estrategia conservadora.")
        else:
            explanation_parts.append(" **Clima Normal:** Temperaturas moderadas esperadas para la semana.")
        
        # Análisis de inventario
        if out_of_stock_products:
            explanation_parts.append(f"\n **PRIORIDAD ALTA - Sin Stock ({len(out_of_stock_products)} productos):**")
            explanation_parts.append("Estos productos necesitan reposición urgente:")
            for product in out_of_stock_products[:5]:  # Mostrar máximo 5
                explanation_parts.append(f"  • {product}")
            if len(out_of_stock_products) > 5:
                explanation_parts.append(f"  • ... y {len(out_of_stock_products) - 5} más")
        
        if low_stock_products:
            explanation_parts.append(f"\n **Stock Bajo ({len(low_stock_products)} productos):**")
            explanation_parts.append("Considera reponer pronto:")
            for product in low_stock_products[:5]:  # Mostrar máximo 5
                explanation_parts.append(f"  • {product}")
            if len(low_stock_products) > 5:
                explanation_parts.append(f"  • ... y {len(low_stock_products) - 5} más")
        
        # Estrategia
        strategy_info = {
            'conservadora': ' **Estrategia Conservadora:** Minimiza riesgos con inventario ajustado.',
            'balanceada': ' **Estrategia Balanceada:** Equilibrio entre ventas y rotación de stock.',
            'agresiva': ' **Estrategia Agresiva:** Maximiza oportunidades de venta con stock elevado.'
        }
        explanation_parts.append(f"\n{strategy_info.get(strategy, '')}")
        
        # Feriados y eventos
        holidays_found = [day for day in daily_analysis if day.is_holiday]
        if holidays_found:
            explanation_parts.append(f"\n **Eventos Especiales:** {len(holidays_found)} día(s) festivo(s) detectado(s) - aumento esperado en demanda.")
        
        # Fin de semana
        weekend_days = sum(1 for day in daily_analysis if day.is_weekend)
        if weekend_days > 0:
            explanation_parts.append(f"\n **Fin de Semana:** {weekend_days} día(s) de fin de semana - mayor afluencia esperada.")
        
        return "\n".join(explanation_parts)
    
    def get_strategy_explanation(self, strategy: str) -> str:
        """
        Obtiene explicación de una estrategia
        
        Args:
            strategy: Nombre de la estrategia
            
        Returns:
            Explicación de la estrategia
        """
        if strategy in self.strategies:
            config = self.strategies[strategy]
            return f"{config['name']}: {config['description']}"
        return "Estrategia no válida"


# Instancia global del motor
suggestion_engine = SuggestionEngine()