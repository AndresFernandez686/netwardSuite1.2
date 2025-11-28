"""
Servicio para obtener datos meteorológicos
"""
import requests
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from ..models.data_models import WeatherData
from ..config.settings import OPENWEATHER_API_KEY, OPENWEATHER_BASE_URL, API_TIMEOUT

logger = logging.getLogger(__name__)


class WeatherService:
    """Servicio para obtener pronósticos meteorológicos"""
    
    def __init__(self, api_key: str = OPENWEATHER_API_KEY):
        self.api_key = api_key
        self.base_url = OPENWEATHER_BASE_URL
    
    def get_weekly_forecast(self, lat: float, lon: float) -> Optional[WeeklyForecast]:
        """
        Obtiene pronóstico de 7 días para las coordenadas especificadas
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            WeeklyForecast o None si hay error
        """
        try:
            # Llamada a OpenWeatherMap API
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'es'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Procesar datos de la API
            daily_weather = self._process_forecast_data(data)
            
            if not daily_weather:
                logger.error("No se pudieron procesar los datos meteorológicos")
                return None
            
            # Obtener información de ubicación
            city_name = data.get('city', {}).get('name', 'Ubicación desconocida')
            country = data.get('city', {}).get('country', '')
            location = f"{city_name}, {country}" if country else city_name
            
            week_start = datetime.now().strftime("%Y-%m-%d")
            
            return WeeklyForecast(
                daily_weather=daily_weather,
                week_start=week_start,
                location=location,
                source="OpenWeatherMap"
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la llamada a la API: {e}")
            return None
        except Exception as e:
            logger.error(f"Error procesando datos meteorológicos: {e}")
            return None
    
    def _process_forecast_data(self, api_data: dict) -> List[WeatherData]:
        """
        Procesa los datos de la API y los convierte en lista de WeatherData
        
        Args:
            api_data: Datos de respuesta de la API
            
        Returns:
            Lista de WeatherData para cada día
        """
        if 'list' not in api_data:
            logger.error("Formato de datos de API inválido")
            return []
        
        # Agrupar por día
        daily_data = {}
        
        for item in api_data['list']:
            try:
                # Obtener fecha
                timestamp = item['dt']
                date = datetime.fromtimestamp(timestamp).date()
                date_str = date.strftime("%Y-%m-%d")
                
                # Extraer datos meteorológicos
                temp = item['main']['temp']
                humidity = item['main']['humidity']
                description = item['weather'][0]['description']
                wind_speed = item.get('wind', {}).get('speed', 0)
                precipitation = item.get('rain', {}).get('3h', 0) + item.get('snow', {}).get('3h', 0)
                
                # Agrupar por día
                if date_str not in daily_data:
                    daily_data[date_str] = {
                        'temps': [],
                        'humidity': [],
                        'descriptions': [],
                        'wind_speeds': [],
                        'precipitations': []
                    }
                
                daily_data[date_str]['temps'].append(temp)
                daily_data[date_str]['humidity'].append(humidity)
                daily_data[date_str]['descriptions'].append(description)
                daily_data[date_str]['wind_speeds'].append(wind_speed)
                daily_data[date_str]['precipitations'].append(precipitation)
                
            except (KeyError, ValueError) as e:
                logger.warning(f"Error procesando item de pronóstico: {e}")
                continue
        
        # Convertir a WeatherData
        weather_list = []
        
        for date_str, data in daily_data.items():
            if not data['temps']:
                continue
                
            try:
                weather_data = WeatherData(
                    date=date_str,
                    temp_min=min(data['temps']),
                    temp_max=max(data['temps']),
                    temp_avg=sum(data['temps']) / len(data['temps']),
                    description=max(set(data['descriptions']), key=data['descriptions'].count),
                    humidity=sum(data['humidity']) / len(data['humidity']),
                    wind_speed=sum(data['wind_speeds']) / len(data['wind_speeds']),
                    precipitation=sum(data['precipitations'])
                )
                
                weather_list.append(weather_data)
                
            except Exception as e:
                logger.warning(f"Error creando WeatherData para {date_str}: {e}")
                continue
        
        # Ordenar por fecha y tomar solo 7 días
        weather_list.sort(key=lambda x: x.date)
        return weather_list[:7]
    
    def get_current_weather(self, lat: float, lon: float) -> Optional[WeatherData]:
        """
        Obtiene el clima actual para las coordenadas especificadas
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            WeatherData del clima actual o None si hay error
        """
        try:
            # API de clima actual
            current_url = "http://api.openweathermap.org/data/2.5/weather"
            
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'es'
            }
            
            response = requests.get(current_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return WeatherData(
                date=datetime.now().strftime("%Y-%m-%d"),
                temp_min=data['main']['temp_min'],
                temp_max=data['main']['temp_max'],
                temp_avg=data['main']['temp'],
                description=data['weather'][0]['description'],
                humidity=data['main']['humidity'],
                wind_speed=data.get('wind', {}).get('speed', 0),
                precipitation=data.get('rain', {}).get('1h', 0) + data.get('snow', {}).get('1h', 0)
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo clima actual: {e}")
            return None


# Instancia global del servicio
weather_service = WeatherService()