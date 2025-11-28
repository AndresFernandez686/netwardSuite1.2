"""
Modelos de datos del sistema de sugerencias
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, date


@dataclass
class LocationInfo:
    """Información de ubicación"""
    lat: float
    lon: float
    city: str
    country: str
    timezone: str = ""
    accuracy: str = "unknown"  # ip, gps, manual, geocoding
    
    def __post_init__(self):
        """Validación después de inicialización"""
        if not (-90 <= self.lat <= 90):
            raise ValueError(f"Latitud inválida: {self.lat}")
        if not (-180 <= self.lon <= 180):
            raise ValueError(f"Longitud inválida: {self.lon}")


@dataclass
class WeatherData:
    """Datos del clima para un día específico"""
    date: str  # YYYY-MM-DD
    temp_min: float
    temp_max: float
    temp_avg: float
    humidity: int
    description: str
    icon: str = ""
    precipitation: float = 0.0
    wind_speed: float = 0.0
    
    def get_temp_factor(self) -> float:
        """Calcula el factor de demanda basado en temperatura"""
        if self.temp_max < 20:
            return 0.3
        elif self.temp_max < 25:
            return 1.0
        elif self.temp_max < 30:
            return 1.8
        else:
            return 2.5


@dataclass
class Store:
    """Información de una tienda"""
    id: Optional[int] = None
    name: str = ""
    location: Optional[LocationInfo] = None
    base_demand: Dict[str, float] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Inicialización después de crear el objeto"""
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class ProductDemand:
    """Demanda de un producto específico"""
    product_id: str
    product_name: str
    base_daily_demand: float
    projected_weekly_demand: float
    suggested_quantity: float
    unit: str  # "unidades" o "kg"
    bulk_size: int
    suggested_bulks: int
    confidence: float = 0.8
    
    def calculate_bulks_needed(self) -> int:
        """Calcula cuántos bultos se necesitan"""
        return max(1, int(self.projected_weekly_demand / self.bulk_size) + 1)


@dataclass 
class DailyAnalysis:
    """Análisis para un día específico"""
    date: str
    weather: WeatherData
    temp_factor: float
    holiday_factor: float
    weekend_factor: float
    combined_factor: float
    is_holiday: bool = False
    is_weekend: bool = False
    holiday_name: str = ""


@dataclass
class WeeklySuggestion:
    """Sugerencia semanal completa"""
    store_id: int
    week_start: str  # YYYY-MM-DD
    strategy: str
    total_investment: float
    expected_revenue: float
    expected_roi: float
    risk_level: str
    product_suggestions: List[ProductDemand] = field(default_factory=list)
    daily_analysis: List[DailyAnalysis] = field(default_factory=list)
    explanation: str = ""
    created_at: Optional[datetime] = None
    # Información de capacidad
    capacidad_total: int = 0
    capacidad_actual: int = 0
    capacidad_disponible: int = 0
    # Información climática
    temperatura_promedio_semana: float = 25.0
    factor_climatico: int = 0  # +1, 0, -1
    descripcion_clima: str = "NORMAL"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def total_bultos(self) -> int:
        """Calcula el total de bultos sugeridos"""
        return sum(p.suggested_bulks for p in self.product_suggestions)
    
    def get_total_bulks(self) -> int:
        """Calcula el total de bultos sugeridos (método legacy)"""
        return self.total_bultos
    
    def get_risk_assessment(self) -> str:
        """Evalúa el nivel de riesgo"""
        if self.expected_roi > 0.95:
            return "ALTO"
        elif self.expected_roi > 0.85:
            return "MEDIO"
        else:
            return "BAJO"


@dataclass
class APIResponse:
    """Respuesta genérica de API"""
    success: bool
    data: Any = None
    error: str = ""
    status_code: int = 200
    
    @classmethod
    def success_response(cls, data: Any = None):
        """Crea una respuesta exitosa"""
        return cls(success=True, data=data)
    
    @classmethod
    def error_response(cls, error: str, status_code: int = 400):
        """Crea una respuesta de error"""
        return cls(success=False, error=error, status_code=status_code)


@dataclass
class ValidationResult:
    """Resultado de validación"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, error: str):
        """Agrega un error"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Agrega una advertencia"""
        self.warnings.append(warning)