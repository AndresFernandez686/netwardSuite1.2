"""
Paquete de servicios del sistema
"""
from .location_service import LocationService, location_service

try:
    from .weather_service import WeatherService, weather_service
    weather_available = True
except ImportError:
    weather_available = False

__all__ = [
    'LocationService',
    'location_service'
]

if weather_available:
    __all__.extend(['WeatherService', 'weather_service'])