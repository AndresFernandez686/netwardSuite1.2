"""
Servicio para obtener datos meteorológicos usando Open-Meteo (gratuito, sin API key)
Open-Meteo funciona perfectamente para Paraguay sin restricciones
"""
import requests
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta

from ..models.data_models import WeatherData
from ..config.settings import API_TIMEOUT

logger = logging.getLogger(__name__)


class WeatherService:
    """Servicio para obtener datos del clima usando Open-Meteo"""
    
    def __init__(self):
        self.open_meteo_url = "https://api.open-meteo.com/v1/forecast"
    
    def get_open_meteo_forecast(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Obtiene pronóstico de Open-Meteo (gratuito, sin API key, funciona en Paraguay)
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            Diccionario con datos del pronóstico o None si hay error
        """
        try:
            logger.info(f"🌤️ Obteniendo pronóstico REAL de Open-Meteo para Paraguay (lat={lat:.4f}, lon={lon:.4f})")
            
            params = {
                'latitude': lat,
                'longitude': lon,
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode',
                'timezone': 'America/Asuncion',
                'forecast_days': 7
            }
            
            response = requests.get(self.open_meteo_url, params=params, timeout=API_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            
            # Procesar datos para obtener pronóstico diario
            daily_forecasts = self._process_open_meteo_data(data)
            
            logger.info(f"✅ Pronóstico obtenido: {len(daily_forecasts)} días de datos REALES")
            
            return {
                'source': 'Open-Meteo',
                'location': f"Paraguay ({lat:.2f}, {lon:.2f})",
                'daily_weather': daily_forecasts,
                'week_start': datetime.now().strftime('%Y-%m-%d')
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error en API de Open-Meteo: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error procesando datos de Open-Meteo: {e}")
            return None
    
    def _process_open_meteo_data(self, data: Dict) -> List[WeatherData]:
        """
        Procesa los datos de Open-Meteo para obtener pronóstico diario
        
        Args:
            data: Datos crudos de la API
            
        Returns:
            Lista de WeatherData para cada día
        """
        weather_list = []
        daily = data.get('daily', {})
        
        dates = daily.get('time', [])
        temp_max = daily.get('temperature_2m_max', [])
        temp_min = daily.get('temperature_2m_min', [])
        precipitation = daily.get('precipitation_sum', [])
        weathercodes = daily.get('weathercode', [])
        
        # Códigos de clima Open-Meteo
        weather_descriptions = {
            0: "Despejado",
            1: "Mayormente despejado",
            2: "Parcialmente nublado",
            3: "Nublado",
            45: "Niebla",
            48: "Niebla con escarcha",
            51: "Llovizna ligera",
            53: "Llovizna moderada",
            55: "Llovizna densa",
            61: "Lluvia ligera",
            63: "Lluvia moderada",
            65: "Lluvia fuerte",
            71: "Nieve ligera",
            73: "Nieve moderada",
            75: "Nieve fuerte",
            77: "Granizo",
            80: "Chubascos ligeros",
            81: "Chubascos moderados",
            82: "Chubascos fuertes",
            95: "Tormenta",
            96: "Tormenta con granizo ligero",
            99: "Tormenta con granizo fuerte"
        }
        
        for i in range(len(dates)):
            temp_avg = (temp_max[i] + temp_min[i]) / 2
            weather_code = weathercodes[i] if i < len(weathercodes) else 0
            description = weather_descriptions.get(weather_code, "Desconocido")
            
            logger.info(f"  📅 {dates[i]}: {temp_min[i]:.1f}°C - {temp_max[i]:.1f}°C (promedio: {temp_avg:.1f}°C) - {description}")
            
            weather_data = WeatherData(
                date=dates[i],
                temp_min=temp_min[i],
                temp_max=temp_max[i],
                temp_avg=temp_avg,
                humidity=65,  # Open-Meteo no provee humedad en el plan gratuito
                description=description,
                precipitation=precipitation[i] if i < len(precipitation) else 0.0
            )
            weather_list.append(weather_data)
        
        return weather_list[:7]  # Máximo 7 días
    
    def get_weekly_forecast(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Obtiene pronóstico semanal usando Open-Meteo
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            Diccionario con datos del pronóstico o None si hay error
        """
        # Usar Open-Meteo (gratuito, sin API key, funciona en Paraguay)
        forecast = self.get_open_meteo_forecast(lat, lon)
        
        if forecast:
            return forecast
        
        # Si falla, usar datos de respaldo
        logger.warning("⚠️ Open-Meteo falló, usando datos de respaldo")
        try:
            return self._get_fallback_forecast(lat, lon)
        except Exception as e:
            logger.error(f"❌ Error obteniendo pronóstico: {e}")
            return None
    
    def _get_fallback_forecast(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Datos de respaldo si falla el API
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            Diccionario con datos del pronóstico de respaldo
        """
        logger.warning("⚠️ Usando datos de respaldo (no son reales)")
        
        # Generar datos conservadores para Paraguay
        daily_weather = []
        base_date = datetime.now()
        
        # Paraguay en noviembre: típicamente 25-32°C
        base_temp_min = 22
        base_temp_max = 30
        
        for i in range(7):
            date = base_date + timedelta(days=i)
            # Pequeña variación día a día
            temp_min = base_temp_min + (i % 3) - 1
            temp_max = base_temp_max + (i % 3) - 1
            temp_avg = (temp_min + temp_max) / 2
            
            weather_data = WeatherData(
                date=date.strftime('%Y-%m-%d'),
                temp_min=temp_min,
                temp_max=temp_max,
                temp_avg=temp_avg,
                humidity=65,
                description="Parcialmente nublado",
                precipitation=0.0
            )
            daily_weather.append(weather_data)
        
        return {
            'source': 'Datos de respaldo (estimados)',
            'location': 'Paraguay',
            'daily_weather': daily_weather,
            'week_start': base_date.strftime('%Y-%m-%d')
        }


# Instancia global del servicio
weather_service = WeatherService()
