"""
Motor de sugerencias inteligentes para heladerías Grido
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

from ..models.data_models import Store, WeeklySuggestion, ProductDemand, WeatherData, DailyAnalysis
from ..config.settings import (
    PRODUCT_SPECS, PARAGUAY_HOLIDAYS, TEMP_FACTORS, 
    WEEKDAY_FACTORS, PURCHASE_STRATEGIES, ICE_CREAM_FLAVORS
)

logger = logging.getLogger(__name__)


class SuggestionEngine:
    """Motor de sugerencias inteligentes basado en clima, demanda y estrategia"""
    
    def __init__(self):
        self.product_specs = PRODUCT_SPECS
        self.holidays = PARAGUAY_HOLIDAYS
        self.strategies = PURCHASE_STRATEGIES
    
    def generate_weekly_suggestion(
        self, 
        store: Store, 
        forecast: WeeklyForecast, 
        strategy: str = "balanceada"
    ) -> WeeklySuggestion:
        """
        Genera sugerencia semanal completa para una tienda
        
        Args:
            store: Tienda para la que generar sugerencias
            forecast: Pronóstico meteorológico semanal
            strategy: Estrategia de compra ("conservadora", "balanceada", "agresiva")
            
        Returns:
            WeeklySuggestion completa
        """
        logger.info(f"Generando sugerencia para tienda {store.name} con estrategia {strategy}")
        
        # Análisis de factores semanales
        weekly_analysis = self._analyze_weekly_factors(forecast)
        
        # Calcular demanda ajustada por tienda
        adjusted_demand = self._calculate_adjusted_demand(
            store.base_demand, 
            weekly_analysis, 
            strategy
        )
        
        # Generar sugerencias por producto
        products = self._generate_product_suggestions(adjusted_demand, strategy)
        
        # Calcular métricas financieras
        financial_metrics = self._calculate_financial_metrics(products)
        
        # Generar explicación
        explanation = self._generate_explanation(
            weekly_analysis, 
            strategy, 
            products, 
            financial_metrics
        )
        
        # Determinar nivel de riesgo
        risk_level = self._determine_risk_level(strategy, weekly_analysis, financial_metrics)
        
        return WeeklySuggestion(
            store_id=store.id,
            week_start=forecast.week_start,
            strategy=strategy,
            products=products,
            total_investment=financial_metrics['total_cost'],
            expected_revenue=financial_metrics['total_revenue'],
            roi_percentage=financial_metrics['roi_percentage'],
            risk_level=risk_level,
            explanation=explanation
        )
    
    def _analyze_weekly_factors(self, forecast: WeeklyForecast) -> Dict:
        """
        Analiza factores que afectan la demanda durante la semana
        
        Args:
            forecast: Pronóstico semanal
            
        Returns:
            Diccionario con análisis de factores
        """
        analysis = {
            'average_thermal_factor': forecast.get_average_thermal_factor(),
            'peak_days': forecast.get_peak_days_count(),
            'holiday_factor': 1.0,
            'weekend_factor': 1.0,
            'weather_risk': 'bajo',
            'demand_pattern': 'normal'
        }
        
        # Verificar feriados en la semana
        week_start = datetime.strptime(forecast.week_start, "%Y-%m-%d")
        for i in range(7):
            check_date = (week_start + timedelta(days=i)).strftime("%Y-%m-%d")
            if check_date in self.holidays:
                analysis['holiday_factor'] = 1.5
                logger.info(f"Feriado detectado: {self.holidays[check_date]} el {check_date}")
                break
        
        # Analizar patrón de demanda
        if analysis['average_thermal_factor'] > 2.0:
            analysis['demand_pattern'] = 'muy_alta'
            analysis['weather_risk'] = 'bajo'
        elif analysis['average_thermal_factor'] > 1.5:
            analysis['demand_pattern'] = 'alta'
            analysis['weather_risk'] = 'bajo'
        elif analysis['average_thermal_factor'] < 0.7:
            analysis['demand_pattern'] = 'baja'
            analysis['weather_risk'] = 'alto'
        
        # Factor de fin de semana (viernes-domingo tienen mayor demanda)
        if analysis['peak_days'] >= 2:
            analysis['weekend_factor'] = 1.3
        
        return analysis
    
    def _calculate_adjusted_demand(
        self, 
        base_demand: Dict[str, float], 
        weekly_analysis: Dict, 
        strategy: str
    ) -> Dict[str, float]:
        """
        Calcula la demanda ajustada basada en factores externos
        
        Args:
            base_demand: Demanda base de la tienda
            weekly_analysis: Análisis de factores semanales
            strategy: Estrategia de compra
            
        Returns:
            Demanda ajustada por producto
        """
        strategy_config = self.strategies[strategy]
        
        # Factor combinado
        combined_factor = (
            weekly_analysis['average_thermal_factor'] *
            weekly_analysis['holiday_factor'] *
            weekly_analysis['weekend_factor'] *
            strategy_config['demand_multiplier']
        )
        
        # Aplicar factor a cada producto
        adjusted_demand = {}
        for product, daily_demand in base_demand.items():
            # Demanda semanal base
            weekly_demand = daily_demand * 7
            
            # Aplicar factor combinado
            adjusted_weekly = weekly_demand * combined_factor
            
            # Aplicar buffer de seguridad
            safety_buffer = 1 + strategy_config['safety_buffer']
            adjusted_weekly *= safety_buffer
            
            adjusted_demand[product] = adjusted_weekly
        
        return adjusted_demand
    
    def _generate_product_suggestions(
        self, 
        adjusted_demand: Dict[str, float], 
        strategy: str
    ) -> List[ProductSuggestion]:
        """
        Genera sugerencias específicas por producto
        
        Args:
            adjusted_demand: Demanda ajustada por producto
            strategy: Estrategia de compra
            
        Returns:
            Lista de ProductSuggestion
        """
        products = []
        
        # Mapeo de demanda a productos específicos
        product_mapping = {
            'palitos_u_per_day': ('palitos', 'bulto'),
            'conos_u_per_day': ('conos', 'bulto'),
            'vasitos_u_per_day': ('vasitos', 'bulto'),
            'potes_kg_per_day': ('potes_1kg', 'bulto'),
            'helado_premium_kg_per_day': ('helado_premium', 'caja')
        }
        
        for demand_key, weekly_demand in adjusted_demand.items():
            if demand_key not in product_mapping:
                continue
            
            product_key, product_type = product_mapping[demand_key]
            
            if product_key not in self.product_specs:
                continue
            
            spec = self.product_specs[product_key]
            
            # Calcular cantidad necesaria
            if product_type == 'bulto':
                if 'units_per_package' in spec:
                    packages_needed = weekly_demand / spec['units_per_package']
                else:
                    packages_needed = weekly_demand / spec.get('kg_per_box', 1)
            else:  # caja
                packages_needed = weekly_demand / spec.get('kg_per_box', 7.8)
            
            # Redondear hacia arriba para tener stock suficiente
            packages_needed = max(1, round(packages_needed + 0.5))
            
            # Calcular métricas financieras
            cost_per_package = spec.get('cost_per_package', spec.get('cost_per_box', 0))
            estimated_cost = packages_needed * cost_per_package
            
            # Calcular ventas esperadas
            if product_type == 'bulto' and 'sale_price_per_unit' in spec:
                units_total = packages_needed * spec.get('units_per_package', 1)
                expected_sales = units_total * spec['sale_price_per_unit']
            else:  # por kg
                kg_total = packages_needed * spec.get('kg_per_box', 7.8)
                expected_sales = kg_total * spec.get('sale_price_per_kg', 15000)
            
            # Calcular ROI
            roi = ((expected_sales - estimated_cost) / estimated_cost * 100) if estimated_cost > 0 else 0
            
            # Generar reasoning
            reasoning = self._generate_product_reasoning(
                product_key, packages_needed, weekly_demand, strategy
            )
            
            # Determinar unidad de medida
            unit = "bultos" if product_type == 'bulto' else "cajas"
            
            products.append(ProductSuggestion(
                product_name=product_key.replace('_', ' ').title(),
                product_type=product_type,
                quantity=packages_needed,
                unit=unit,
                reasoning=reasoning,
                estimated_cost=estimated_cost,
                expected_sales=expected_sales,
                roi_percentage=roi
            ))
        
        # Agregar productos adicionales basados en estrategia
        if strategy == "agresiva":
            products.extend(self._suggest_premium_products(adjusted_demand))
        
        return products
    
    def _suggest_premium_products(self, adjusted_demand: Dict[str, float]) -> List[ProductSuggestion]:
        """
        Sugiere productos premium para estrategia agresiva
        
        Args:
            adjusted_demand: Demanda ajustada
            
        Returns:
            Lista de productos premium sugeridos
        """
        premium_products = []
        
        # Sugerir tortas si la demanda es alta
        base_demand = adjusted_demand.get('potes_kg_per_day', 0)
        if base_demand > 5:  # Alta demanda de helados
            spec = self.product_specs['tortas']
            
            # Sugerir 1-2 tortas por semana
            quantity = 1 if base_demand < 10 else 2
            cost = quantity * spec['cost_per_package']
            revenue = quantity * spec['units_per_package'] * spec['sale_price_per_unit']
            roi = ((revenue - cost) / cost * 100) if cost > 0 else 0
            
            premium_products.append(ProductSuggestion(
                product_name="Tortas Heladas",
                product_type="bulto",
                quantity=quantity,
                unit="bultos",
                reasoning=f"Producto premium recomendado para estrategia agresiva. Alta demanda detectada.",
                estimated_cost=cost,
                expected_sales=revenue,
                roi_percentage=roi
            ))
        
        return premium_products
    
    def _generate_product_reasoning(
        self, 
        product_key: str, 
        quantity: float, 
        weekly_demand: float, 
        strategy: str
    ) -> str:
        """
        Genera explicación del reasoning para un producto específico
        
        Args:
            product_key: Clave del producto
            quantity: Cantidad sugerida
            weekly_demand: Demanda semanal calculada
            strategy: Estrategia usada
            
        Returns:
            String con el reasoning
        """
        strategy_name = self.strategies[strategy]['name']
        
        if quantity == 1:
            return f"Demanda base estimada: {weekly_demand:.1f}/semana. Estrategia {strategy_name} sugiere 1 unidad para minimizar riesgo."
        elif quantity <= 3:
            return f"Demanda moderada estimada: {weekly_demand:.1f}/semana. {quantity} unidades para {strategy_name}."
        else:
            return f"Alta demanda estimada: {weekly_demand:.1f}/semana. {quantity} unidades para maximizar ventas ({strategy_name})."
    
    def _calculate_financial_metrics(self, products: List[ProductSuggestion]) -> Dict:
        """
        Calcula métricas financieras totales
        
        Args:
            products: Lista de productos sugeridos
            
        Returns:
            Diccionario con métricas financieras
        """
        total_cost = sum(p.estimated_cost for p in products)
        total_revenue = sum(p.expected_sales for p in products)
        
        roi_percentage = ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0
        profit = total_revenue - total_cost
        
        return {
            'total_cost': total_cost,
            'total_revenue': total_revenue,
            'roi_percentage': roi_percentage,
            'profit': profit,
            'product_count': len(products)
        }
    
    def _determine_risk_level(
        self, 
        strategy: str, 
        weekly_analysis: Dict, 
        financial_metrics: Dict
    ) -> str:
        """
        Determina el nivel de riesgo de la sugerencia
        
        Args:
            strategy: Estrategia usada
            weekly_analysis: Análisis semanal
            financial_metrics: Métricas financieras
            
        Returns:
            Nivel de riesgo ("bajo", "medio", "alto")
        """
        base_risk = self.strategies[strategy]['max_risk_percentage']
        
        # Ajustar riesgo por factores climáticos
        if weekly_analysis['weather_risk'] == 'alto':
            base_risk += 5
        
        if weekly_analysis['demand_pattern'] == 'muy_alta':
            base_risk -= 3  # Menor riesgo con alta demanda
        elif weekly_analysis['demand_pattern'] == 'baja':
            base_risk += 5  # Mayor riesgo con baja demanda
        
        # Clasificar riesgo
        if base_risk <= 7:
            return "bajo"
        elif base_risk <= 15:
            return "medio"
        else:
            return "alto"
    
    def _generate_explanation(
        self, 
        weekly_analysis: Dict, 
        strategy: str, 
        products: List[ProductSuggestion], 
        financial_metrics: Dict
    ) -> str:
        """
        Genera explicación detallada de la sugerencia
        
        Args:
            weekly_analysis: Análisis semanal
            strategy: Estrategia usada
            products: Productos sugeridos
            financial_metrics: Métricas financieras
            
        Returns:
            Explicación detallada
        """
        strategy_info = self.strategies[strategy]
        
        explanation_parts = [
            f" **Estrategia {strategy_info['name']}**: {strategy_info['description']}",
            f" **Factor térmico promedio**: {weekly_analysis['average_thermal_factor']:.1f}x",
            f" **Patrón de demanda**: {weekly_analysis['demand_pattern'].replace('_', ' ').title()}"
        ]
        
        # Información sobre feriados
        if weekly_analysis['holiday_factor'] > 1.0:
            explanation_parts.append(" **Feriado detectado**: Incremento de demanda esperado")
        
        # Días pico
        if weekly_analysis['peak_days'] > 0:
            explanation_parts.append(f" **Días de alta demanda**: {weekly_analysis['peak_days']} días")
        
        # Métricas financieras
        explanation_parts.extend([
            f" **Inversión total**: ₲{financial_metrics['total_cost']:,.0f}",
            f" **ROI esperado**: {financial_metrics['roi_percentage']:.1f}%",
            f" **Productos sugeridos**: {financial_metrics['product_count']}"
        ])
        
        # Recomendaciones adicionales
        if weekly_analysis['demand_pattern'] == 'muy_alta':
            explanation_parts.append(" **Recomendación**: Stock adicional de productos populares")
        elif weekly_analysis['demand_pattern'] == 'baja':
            explanation_parts.append(" **Precaución**: Clima frío detectado, evitar sobrestock")
        
        return "\n\n".join(explanation_parts)


# Instancia global del motor de sugerencias
suggestion_engine = SuggestionEngine()