"""
Servicio para detección y manejo de ubicaciones
"""
import os
import logging
from typing import Optional, List, Dict

# Importar requests de manera segura
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print(" Warning: requests no está disponible")

from ..models.data_models import LocationInfo
from ..config.settings import IPAPI_URL, API_TIMEOUT, OPENWEATHER_API_KEY

# URLs para geocoding
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
GOOGLE_PLACES_FIND_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"

# Google API Key desde configuración
GOOGLE_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY', 'demo')

logger = logging.getLogger(__name__)


class LocationService:
    """Servicio para detectar y manejar ubicaciones"""
    
    def __init__(self):
        self.ip_api_url = IPAPI_URL
        self.nominatim_url = NOMINATIM_URL
    
    def detect_location_by_ip(self) -> Optional[LocationInfo]:
        """
        Detecta la ubicación del usuario usando su IP
        
        Returns:
            LocationInfo o None si hay error
        """
        if not REQUESTS_AVAILABLE:
            logger.error("requests no está disponible")
            return self._get_default_location()
            
        try:
            # Llamada a IP-API para obtener ubicación por IP
            response = requests.get(self.ip_api_url, timeout=API_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'fail':
                logger.error(f"Error en IP-API: {data.get('message', 'Error desconocido')}")
                return None
            
            return LocationInfo(
                lat=float(data.get('lat', 0)),
                lon=float(data.get('lon', 0)),
                city=data.get('city', ''),
                country=data.get('country', ''),
                timezone=data.get('timezone', ''),
                accuracy="ip"
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la llamada a IP-API: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Error procesando datos de ubicación: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado detectando ubicación: {e}")
            return self._get_default_location()
    
    def get_location_info(self, lat: float, lon: float) -> Optional[LocationInfo]:
        """
        Obtiene información de ubicación para coordenadas específicas
        usando reverse geocoding
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            LocationInfo o None si hay error
        """
        try:
            # Usar OpenWeatherMap para reverse geocoding
            url = "http://api.openweathermap.org/geo/1.0/reverse"
            params = {
                'lat': lat,
                'lon': lon,
                'limit': 1,
                'appid': OPENWEATHER_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    location = data[0]
                    return LocationInfo(
                        lat=lat,
                        lon=lon,
                        city=location.get('name', ''),
                        country=location.get('country', ''),
                        timezone="",
                        accuracy="geocoding"
                    )
            
            # Fallback: crear LocationInfo con coordenadas solamente
            return LocationInfo(
                lat=lat,
                lon=lon,
                city="Ubicación personalizada",
                country="",
                timezone="",
                accuracy="manual"
            )
            
        except Exception as e:
            logger.warning(f"Error en reverse geocoding: {e}")
            # Fallback: crear LocationInfo básica
            return LocationInfo(
                lat=lat,
                lon=lon,
                city="Ubicación personalizada",
                country="",
                timezone="",
                accuracy="manual"
            )
    
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """
        Valida que las coordenadas estén en rangos válidos
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            True si las coordenadas son válidas
        """
        return -90 <= lat <= 90 and -180 <= lon <= 180
    
    def is_in_paraguay(self, lat: float, lon: float) -> bool:
        """
        Verifica si las coordenadas están dentro de Paraguay
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            True si está en Paraguay
        """
        # Límites aproximados de Paraguay
        paraguay_bounds = {
            'north': -19.3,
            'south': -27.6,
            'east': -54.3,
            'west': -62.6
        }
        
        return (paraguay_bounds['south'] <= lat <= paraguay_bounds['north'] and
                paraguay_bounds['west'] <= lon <= paraguay_bounds['east'])
    
    def get_nearest_major_city(self, lat: float, lon: float) -> str:
        """
        Obtiene la ciudad principal más cercana en Paraguay
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            Nombre de la ciudad más cercana
        """
        major_cities = {
            'Asunción': (-25.2637, -57.5759),
            'Ciudad del Este': (-25.5163, -54.6116),
            'San Lorenzo': (-25.3389, -57.5072),
            'Luque': (-25.2667, -57.4833),
            'Capiatá': (-25.3575, -57.4456),
            'Lambaré': (-25.3425, -57.6094),
            'Fernando de la Mora': (-25.3194, -57.5431),
            'Limpio': (-25.1658, -57.4703),
            'Ñemby': (-25.3892, -57.5369),
            'Encarnación': (-27.3306, -55.8683)
        }
        
        min_distance = float('inf')
        nearest_city = 'Asunción'  # Default
        
        for city, (city_lat, city_lon) in major_cities.items():
            # Cálculo simple de distancia
            distance = ((lat - city_lat) ** 2 + (lon - city_lon) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                nearest_city = city
        
        return nearest_city
    
    def _get_default_location(self) -> LocationInfo:
        """
        Retorna la ubicación por defecto (Asunción, Paraguay)
        
        Returns:
            LocationInfo con datos de Asunción
        """
        return LocationInfo(
            lat=-25.2637,
            lon=-57.5759,
            city="Asunción",
            country="Paraguay",
            timezone="America/Asuncion",
            accuracy="default"
        )
    
    def get_location_info_safe(self, lat: float, lon: float) -> LocationInfo:
        """
        Versión segura de get_location_info que siempre retorna algo
        
        Args:
            lat: Latitud
            lon: Longitud
            
        Returns:
            LocationInfo (nunca None)
        """
        result = self.get_location_info(lat, lon)
        if result is None:
            return LocationInfo(
                lat=lat,
                lon=lon,
                city="Ubicación personalizada",
                country="",
                timezone="",
                accuracy="manual"
            )
        return result
    
    def search_store_by_name(self, store_name: str, country: str = "Paraguay") -> List[Dict]:
        """
        Busca tiendas por nombre usando OpenStreetMap Nominatim
        
        Args:
            store_name: Nombre de la tienda (ej: "Grido Asunción Centro")
            country: País donde buscar (default: Paraguay)
        
        Returns:
            Lista de ubicaciones encontradas
        """
        if not REQUESTS_AVAILABLE:
            logger.error("requests no está disponible para búsqueda")
            return []
        
        try:
            # Preparar la consulta de búsqueda
            query = f"{store_name}, {country}"
            params = {
                'q': query,
                'format': 'json',
                'limit': 10,
                'countrycodes': 'py' if country.lower() == 'paraguay' else None,
                'addressdetails': 1,
                'extratags': 1
            }
            
            # Headers para ser un buen ciudadano de la API
            headers = {
                'User-Agent': 'Grido-Sugerencias-App/1.0 (sugerencias@grido.py)'
            }
            
            logger.info(f"Buscando tienda: {query}")
            response = requests.get(
                self.nominatim_url, 
                params=params, 
                headers=headers,
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            for item in data:
                result = {
                    'name': item.get('display_name', ''),
                    'lat': float(item.get('lat', 0)),
                    'lon': float(item.get('lon', 0)),
                    'address': item.get('display_name', ''),
                    'city': item.get('address', {}).get('city') or item.get('address', {}).get('town', ''),
                    'country': item.get('address', {}).get('country', ''),
                    'type': item.get('type', ''),
                    'importance': float(item.get('importance', 0)),
                    'confidence': self._calculate_name_confidence(store_name, item.get('display_name', ''))
                }
                results.append(result)
            
            # Ordenar por relevancia (confianza + importancia)
            results.sort(key=lambda x: (x['confidence'], x['importance']), reverse=True)
            
            logger.info(f"Encontradas {len(results)} ubicaciones para '{store_name}'")
            return results
            
        except requests.RequestException as e:
            logger.error(f"Error en búsqueda de tienda: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado en búsqueda: {e}")
            return []
    
    def search_address(self, address: str) -> List[Dict]:
        """
        Busca una dirección específica
        
        Args:
            address: Dirección a buscar (ej: "Av. España 1234, Asunción")
        
        Returns:
            Lista de ubicaciones encontradas
        """
        if not REQUESTS_AVAILABLE:
            logger.error("requests no está disponible para búsqueda")
            return []
        
        try:
            params = {
                'q': address,
                'format': 'json',
                'limit': 5,
                'countrycodes': 'py',
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'Grido-Sugerencias-App/1.0 (sugerencias@grido.py)'
            }
            
            logger.info(f"Buscando dirección: {address}")
            response = requests.get(
                self.nominatim_url, 
                params=params, 
                headers=headers,
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            for item in data:
                result = {
                    'address': item.get('display_name', ''),
                    'lat': float(item.get('lat', 0)),
                    'lon': float(item.get('lon', 0)),
                    'city': item.get('address', {}).get('city') or item.get('address', {}).get('town', ''),
                    'country': item.get('address', {}).get('country', ''),
                    'type': item.get('type', ''),
                    'importance': float(item.get('importance', 0))
                }
                results.append(result)
            
            # Ordenar por importancia
            results.sort(key=lambda x: x['importance'], reverse=True)
            
            logger.info(f"Encontradas {len(results)} direcciones para '{address}'")
            return results
            
        except requests.RequestException as e:
            logger.error(f"Error en búsqueda de dirección: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado en búsqueda de dirección: {e}")
            return []
    
    def _calculate_name_confidence(self, search_name: str, found_name: str) -> float:
        """
        Calcula la confianza de coincidencia entre nombres
        
        Args:
            search_name: Nombre buscado
            found_name: Nombre encontrado
        
        Returns:
            Puntuación de confianza (0.0 - 1.0)
        """
        search_lower = search_name.lower()
        found_lower = found_name.lower()
        
        # Coincidencia exacta
        if search_lower == found_lower:
            return 1.0
        
        # Contiene el nombre buscado
        if search_lower in found_lower:
            return 0.8
        
        # Palabras clave coinciden
        search_words = set(search_lower.split())
        found_words = set(found_lower.split())
        common_words = search_words.intersection(found_words)
        
        if len(search_words) > 0:
            return len(common_words) / len(search_words) * 0.6
        
        return 0.0
    
    def _fuzzy_match_score(self, text1: str, text2: str) -> float:
        """
        Calcula un puntaje de similitud entre dos textos usando Levenshtein distance
        
        Args:
            text1: Primer texto
            text2: Segundo texto
        
        Returns:
            Puntaje de similitud (0.0 - 1.0)
        """
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        if text1 == text2:
            return 1.0
        
        # Calcular distancia de Levenshtein simple
        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        max_len = max(len(text1), len(text2))
        if max_len == 0:
            return 1.0
        
        distance = levenshtein_distance(text1, text2)
        similarity = 1 - (distance / max_len)
        return max(0.0, similarity)
    
    def _normalize_search_term(self, term: str) -> str:
        """
        Normaliza términos de búsqueda removiendo acentos y caracteres especiales
        
        Args:
            term: Término a normalizar
        
        Returns:
            Término normalizado
        """
        # Diccionario de reemplazos para caracteres con acentos
        replacements = {
            'á': 'a', 'à': 'a', 'ä': 'a', 'â': 'a',
            'é': 'e', 'è': 'e', 'ë': 'e', 'ê': 'e',
            'í': 'i', 'ì': 'i', 'ï': 'i', 'î': 'i',
            'ó': 'o', 'ò': 'o', 'ö': 'o', 'ô': 'o',
            'ú': 'u', 'ù': 'u', 'ü': 'u', 'û': 'u',
            'ñ': 'n', 'ç': 'c'
        }
        
        normalized = term.lower()
        for accented, normal in replacements.items():
            normalized = normalized.replace(accented, normal)
        
        return normalized
    
    def _get_store_synonyms(self) -> Dict[str, List[str]]:
        """
        Retorna un diccionario de sinónimos para búsquedas de tiendas
        
        Returns:
            Diccionario con términos y sus sinónimos
        """
        return {
            'centro': ['downtown', 'city center', 'casco historico', 'microcentro'],
            'shopping': ['mall', 'centro comercial', 'galeria'],
            'aeropuerto': ['airport', 'silvio pettirossi'],
            'terminal': ['terminal de omnibus', 'estacion de buses'],
            'hospital': ['clinica', 'sanatorio'],
            'universidad': ['uni', 'facultad', 'campus'],
            'estadio': ['cancha', 'campo de futbol'],
            'mercado': ['market', 'feria', 'abasto'],
            'plaza': ['square', 'parque', 'plazoleta'],
            'avenida': ['av', 'avenue', 'avda'],
            'calle': ['c/', 'street', 'st'],
            'barrio': ['b°', 'neighborhood', 'zona'],
            'asuncion': ['asunción', 'asu', 'capital'],
            'cde': ['ciudad del este', 'cde'],
            'encarnacion': ['encarnación', 'enc']
        }
    
    def _expand_search_terms(self, search_term: str) -> List[str]:
        """
        Expande términos de búsqueda con sinónimos
        
        Args:
            search_term: Término original
        
        Returns:
            Lista de términos expandidos
        """
        synonyms = self._get_store_synonyms()
        terms = [search_term.lower()]
        normalized = self._normalize_search_term(search_term)
        
        if normalized != search_term.lower():
            terms.append(normalized)
        
        # Agregar sinónimos
        words = search_term.lower().split()
        for word in words:
            if word in synonyms:
                for synonym in synonyms[word]:
                    # Reemplazar la palabra original con el sinónimo
                    new_term = search_term.lower().replace(word, synonym)
                    if new_term not in terms:
                        terms.append(new_term)
        
        return terms


    def search_local_stores(self, search_term: str, max_results: int = 10) -> List[Dict]:
        """
        Búsqueda inteligente en la base de datos local de tiendas Grido
        
        Args:
            search_term: Término de búsqueda
            max_results: Número máximo de resultados
        
        Returns:
            Lista de tiendas encontradas con puntajes de relevancia
        """
        try:
            # Importar la función de búsqueda desde settings
            from ..config.settings import search_grido_stores, GRIDO_STORES_DATABASE
            
            if not GRIDO_STORES_DATABASE:
                logger.warning("Base de datos de tiendas Grido vacía")
                return []
            
            # Expandir términos de búsqueda con sinónimos
            expanded_terms = self._expand_search_terms(search_term)
            all_results = []
            
            for term in expanded_terms:
                # Búsqueda básica usando la función existente
                basic_results = search_grido_stores(term)
                
                # Agregar resultados básicos con puntaje alto
                for basic_result in basic_results:
                    basic_result['score'] = 0.9  # Puntaje alto para coincidencias exactas
                    basic_result['match_type'] = 'exact'
                    basic_result['search_term'] = term
                    basic_result['id'] = f"{basic_result.get('city', '')}_{basic_result.get('name', '')}"
                    
                    # Evitar duplicados
                    store_id = basic_result.get('id', '')
                    if not any(r.get('id') == store_id for r in all_results):
                        all_results.append(basic_result)
                
                # Búsqueda avanzada con fuzzy matching
                for city, stores_list in GRIDO_STORES_DATABASE.items():
                    for store_data in stores_list:
                        store_name = store_data.get('name', '')
                        store_address = store_data.get('address', '')
                        store_city = city.replace('_', ' ').title()
                        
                        # Calcular puntajes de similitud
                        name_score = self._fuzzy_match_score(term, store_name)
                        address_score = self._fuzzy_match_score(term, store_address) * 0.7
                        city_score = self._fuzzy_match_score(term, store_city) * 0.8
                        
                        # Puntaje combinado
                        combined_score = max(name_score, address_score, city_score)
                        
                        # Solo incluir si el puntaje es significativo
                        if combined_score > 0.3:
                            store_id = f"{city}_{store_name}"
                            result = {
                                'id': store_id,
                                'name': store_name,
                                'address': store_address,
                                'city': store_city,
                                'lat': store_data.get('lat', 0),
                                'lon': store_data.get('lon', 0),
                                'phone': store_data.get('phone', ''),
                                'score': combined_score,
                                'match_type': 'fuzzy',
                                'search_term': term
                            }
                            
                            # Evitar duplicados
                            if not any(r.get('id') == store_id for r in all_results):
                                all_results.append(result)
            
            # Ordenar por puntaje y limitar resultados
            all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            final_results = all_results[:max_results]
            
            logger.info(f"Búsqueda local encontró {len(final_results)} tiendas para '{search_term}'")
            return final_results
            
        except ImportError as e:
            logger.error(f"Error importando datos de tiendas: {e}")
            return []
        except Exception as e:
            logger.error(f"Error en búsqueda local: {e}")
            return []
    
    def search_by_geographic_context(self, search_term: str) -> List[Dict]:
        """
        Búsqueda inteligente usando contexto geográfico.
        Ej: "Grido Seminario" busca franquicias cerca de calles/barrios "Seminario"
        
        Args:
            search_term: Término que puede incluir referencias geográficas
        
        Returns:
            Lista de tiendas ordenadas por relevancia geográfica
        """
        try:
            from ..config.settings import GRIDO_STORES_DATABASE
            
            if not GRIDO_STORES_DATABASE:
                return []
            
            # Extraer posibles referencias geográficas del término de búsqueda
            geographic_terms = self._extract_geographic_terms(search_term)
            results = []
            exact_matches = []  # Para almacenar coincidencias exactas
            
            logger.info(f"Términos geográficos extraídos: {geographic_terms}")
            
            # Si no hay términos geográficos, usar el término completo
            if not geographic_terms:
                geographic_terms = [search_term.lower().replace('grido', '').strip()]
            
            # Para cada tienda, calcular relevancia geográfica
            for city, stores_list in GRIDO_STORES_DATABASE.items():
                for store_data in stores_list:
                    store_name = store_data.get('name', '')
                    store_address = store_data.get('address', '')
                    store_city = city.replace('_', ' ').title()
                    
                    # Combinar información para búsqueda
                    full_text = f"{store_name} {store_address} {store_city}".lower()
                    location_text = f"{store_address} {store_city}".lower()
                    name_words = set(store_name.lower().split())
                    address_words = set(store_address.lower().split())
                    
                    # Calcular puntaje de relevancia geográfica
                    geo_score = 0.0
                    matched_terms = []
                    has_exact_match = False
                    
                    for geo_term in geographic_terms:
                        geo_term_lower = geo_term.lower().strip()
                        
                        if not geo_term_lower or len(geo_term_lower) < 2:
                            continue
                        
                        # PRIORIDAD 1: Coincidencia exacta en nombre de tienda
                        if geo_term_lower in name_words or geo_term_lower in store_name.lower():
                            geo_score += 15.0
                            matched_terms.append(f"nombre:{geo_term}")
                            has_exact_match = True
                        
                        # PRIORIDAD 2: Coincidencia exacta en palabras de dirección
                        elif geo_term_lower in address_words:
                            geo_score += 10.0
                            matched_terms.append(f"dirección:{geo_term}")
                            has_exact_match = True
                        
                        # PRIORIDAD 3: Substring en dirección completa
                        elif geo_term_lower in location_text:
                            geo_score += 7.0
                            matched_terms.append(geo_term)
                            has_exact_match = True
                        
                        # PRIORIDAD 4: Substring en texto completo
                        elif geo_term_lower in full_text:
                            geo_score += 5.0
                            matched_terms.append(geo_term)
                        
                        # PRIORIDAD 5: Fuzzy match flexible
                        elif self._fuzzy_match_score(geo_term, store_name.lower()) > 0.6:
                            fuzzy_score = self._fuzzy_match_score(geo_term, store_name.lower())
                            geo_score += fuzzy_score * 4.0
                            matched_terms.append(f"{geo_term}~nombre")
                        
                        elif self._fuzzy_match_score(geo_term, store_address.lower()) > 0.6:
                            fuzzy_score = self._fuzzy_match_score(geo_term, store_address.lower())
                            geo_score += fuzzy_score * 3.0
                            matched_terms.append(f"{geo_term}~dirección")
                    
                    # Solo incluir si hay alguna coincidencia geográfica
                    if geo_score > 0:
                        store_id = f"{city}_{store_name}"
                        result = {
                            'id': store_id,
                            'name': store_name,
                            'address': store_address,
                            'city': store_city,
                            'lat': store_data.get('lat', 0),
                            'lon': store_data.get('lon', 0),
                            'phone': store_data.get('phone', ''),
                            'score': geo_score,
                            'match_type': 'geographic',
                            'matched_terms': matched_terms,
                            'search_term': search_term,
                            'source': 'local_geographic',
                            'exact_match': has_exact_match
                        }
                        
                        # Separar coincidencias exactas
                        if has_exact_match:
                            exact_matches.append(result)
                        else:
                            results.append(result)
            
            # Si hay coincidencias exactas, retornar SOLO esas
            if exact_matches:
                exact_matches.sort(key=lambda x: x['score'], reverse=True)
                logger.info(f"Búsqueda geográfica encontró {len(exact_matches)} coincidencias EXACTAS para '{search_term}'")
                return exact_matches[:3]  # Máximo 3 resultados exactos
            
            # Si no hay exactas, ordenar por puntaje y filtrar por umbral mínimo
            results.sort(key=lambda x: x['score'], reverse=True)
            
            # Filtrar solo resultados con score >= 2.0 (eliminar matches muy débiles)
            filtered_results = [r for r in results if r.get('score', 0) >= 2.0]
            
            logger.info(f"Búsqueda geográfica encontró {len(filtered_results)} coincidencias relevantes para '{search_term}'")
            return filtered_results[:8]  # Máximo 8 resultados relevantes
            
        except Exception as e:
            logger.error(f"Error en búsqueda geográfica: {e}")
            return []
    
    def _extract_geographic_terms(self, search_term: str) -> List[str]:
        """
        Extrae posibles términos geográficos del texto de búsqueda
        
        Args:
            search_term: Término de búsqueda original
        
        Returns:
            Lista de términos que podrían ser referencias geográficas
        """
        # Remover "Grido" y términos comunes para quedarse con la referencia geográfica
        common_prefixes = ['grido', 'helado', 'heladeria', 'tienda', 'sucursal', 'local']
        
        # Normalizar y dividir en palabras
        normalized = self._normalize_search_term(search_term.lower())
        words = normalized.split()
        
        # Filtrar palabras comunes
        geographic_terms = []
        for word in words:
            if word not in common_prefixes and len(word) > 2:
                geographic_terms.append(word)
        
        # Si no quedan términos, usar el término original sin "grido"
        if not geographic_terms:
            clean_term = search_term.lower()
            for prefix in common_prefixes:
                clean_term = clean_term.replace(prefix, '').strip()
            if clean_term:
                geographic_terms = [clean_term]
        
        return geographic_terms
    
    def search_grido_with_context(self, search_term: str) -> List[Dict]:
        """
        Búsqueda especializada para franquicias Grido usando contexto geográfico.
        Esta es la función principal que deberías usar para buscar Grido.
        
        Args:
            search_term: Término de búsqueda (ej: "Grido Seminario", "Grido Villa Morra")
        
        Returns:
            Lista de franquicias Grido ordenadas por relevancia
        """
        all_results = []
        
        # 1. Búsqueda geográfica (más precisa para Grido)
        geo_results = self.search_by_geographic_context(search_term)
        
        # Si hay resultados con coincidencia exacta, retornar SOLO esos
        exact_geo_results = [r for r in geo_results if r.get('exact_match', False)]
        if exact_geo_results:
            logger.info(f"Retornando {len(exact_geo_results)} coincidencias exactas")
            return exact_geo_results  # No buscar más si hay exactas
        
        all_results.extend(geo_results)
        
        # 2. Solo si no hay buenos resultados geográficos, buscar local tradicional
        if len(all_results) < 2:
            local_results = self.search_local_stores(search_term, max_results=5)
            
            # Agregar resultados locales que no estén ya incluidos
            existing_ids = {r.get('id') for r in all_results}
            for result in local_results:
                if result.get('id') not in existing_ids and result.get('score', 0) > 0.6:
                    result['source'] = 'local_traditional'
                    all_results.append(result)
        
        # 3. Si aún hay muy pocos resultados, usar Google Maps (prioritario) o OpenStreetMap
        if len(all_results) < 2:
            logger.info("Complementando con búsqueda online...")
            
            # Primero intentar Google Maps (más preciso)
            if GOOGLE_API_KEY and GOOGLE_API_KEY != 'demo':
                logger.info("Usando Google Maps API...")
                google_results = self.search_grido_google_maps(search_term)
                
                for google_result in google_results[:3]:
                    google_result['source'] = 'google_maps'
                    
                    # Evitar duplicados por proximidad
                    is_duplicate = False
                    for existing in all_results:
                        existing_lat = existing.get('lat', 0)
                        existing_lon = existing.get('lon', 0)
                        google_lat = google_result.get('lat', 0)
                        google_lon = google_result.get('lon', 0)
                        
                        distance = ((existing_lat - google_lat) ** 2 + (existing_lon - google_lon) ** 2) ** 0.5
                        if distance < 0.001:  # ~100m
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        all_results.append(google_result)
            
            # Respaldo con OpenStreetMap si Google Maps no está disponible o no encontró suficientes
            if len(all_results) < 3:
                logger.info("Complementando con OpenStreetMap...")
                geo_terms = self._extract_geographic_terms(search_term)
                
                for geo_term in geo_terms:
                    online_query = f"Grido Helado {geo_term} Paraguay"
                    online_results = self.search_store_by_name(online_query)
                    
                    for online_result in online_results[:3]:
                        online_result['source'] = 'openstreetmap'
                        online_result['geographic_term'] = geo_term
                        online_result['score'] = online_result.get('confidence', 0.7)
                        
                        # Evitar duplicados por proximidad
                        is_duplicate = False
                        for existing in all_results:
                            existing_lat = existing.get('lat', 0)
                            existing_lon = existing.get('lon', 0)
                            online_lat = online_result.get('lat', 0)
                            online_lon = online_result.get('lon', 0)
                            
                            distance = ((existing_lat - online_lat) ** 2 + (existing_lon - online_lon) ** 2) ** 0.5
                            if distance < 0.001:  # ~100m
                                is_duplicate = True
                                break
                        
                        if not is_duplicate:
                            all_results.append(online_result)
        
        # Ordenar por puntaje y agregar información adicional
        all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Agregar información de distancia si hay suficientes resultados
        for i, result in enumerate(all_results):
            result['rank'] = i + 1
            result['search_strategy'] = f"{result.get('source', 'unknown')} (score: {result.get('score', 0):.2f})"
        
        # Limitar resultados según calidad
        high_quality = [r for r in all_results if r.get('score', 0) >= 5.0]
        medium_quality = [r for r in all_results if 2.0 <= r.get('score', 0) < 5.0]
        
        if high_quality:
            # Si hay resultados de alta calidad, mostrar hasta 5
            final_results = high_quality[:5]
        elif medium_quality:
            # Si hay resultados de calidad media, mostrar hasta 8
            final_results = medium_quality[:8]
        else:
            # Mostrar todos los resultados disponibles (máximo 10)
            final_results = all_results[:10]
        
        logger.info(f"Búsqueda Grido con contexto: {len(final_results)} resultados para '{search_term}'")
        return final_results
    
    def search_google_maps(self, search_term: str) -> List[Dict]:
        """
        Búsqueda usando Google Maps Places API
        
        Args:
            search_term: Término de búsqueda (ej: "Grido Seminario Paraguay")
        
        Returns:
            Lista de lugares encontrados usando Google Maps
        """
        if not REQUESTS_AVAILABLE:
            logger.error("requests no está disponible para búsqueda Google Maps")
            return []
            
        if not GOOGLE_API_KEY or GOOGLE_API_KEY == 'demo':
            logger.warning("Google Maps API Key no configurada")
            return []
        
        try:
            # Preparar consulta para Google Places Text Search
            query = f"Grido Helado {search_term} Paraguay"
            params = {
                'query': query,
                'key': GOOGLE_API_KEY,
                'region': 'py',  # Paraguay
                'type': 'food',  # Tipo de establecimiento
                'language': 'es'  # Idioma español
            }
            
            logger.info(f"Buscando en Google Maps: {query}")
            response = requests.get(
                GOOGLE_PLACES_URL,
                params=params,
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK':
                logger.warning(f"Google Maps API error: {data.get('status')} - {data.get('error_message', '')}")
                return []
            
            results = []
            for place in data.get('results', []):
                # Extraer información del lugar
                geometry = place.get('geometry', {})
                location = geometry.get('location', {})
                
                result = {
                    'name': place.get('name', ''),
                    'address': place.get('formatted_address', ''),
                    'lat': location.get('lat', 0),
                    'lon': location.get('lng', 0),
                    'rating': place.get('rating', 0),
                    'user_ratings_total': place.get('user_ratings_total', 0),
                    'place_id': place.get('place_id', ''),
                    'types': place.get('types', []),
                    'price_level': place.get('price_level'),
                    'opening_hours': place.get('opening_hours', {}),
                    'photos': place.get('photos', []),
                    'source': 'google_maps',
                    'confidence': 0.95,  # Google Maps tiene alta confianza
                    'score': 0.95
                }
                
                # Calcular relevancia basada en rating y coincidencia de nombre
                name_match = self._calculate_name_confidence(search_term, place.get('name', ''))
                rating_score = (place.get('rating', 0) / 5.0) * 0.3  # Rating como factor
                result['score'] = max(0.7, name_match + rating_score)
                
                results.append(result)
            
            # Ordenar por relevancia
            results.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"Google Maps encontró {len(results)} lugares para '{search_term}'")
            return results[:10]  # Limitar a 10 resultados
            
        except requests.RequestException as e:
            logger.error(f"Error en Google Maps API: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado en Google Maps: {e}")
            return []
    
    def search_grido_google_maps(self, search_term: str) -> List[Dict]:
        """
        Búsqueda especializada de Grido usando Google Maps con términos geográficos
        
        Args:
            search_term: Término con referencia geográfica (ej: "Grido Seminario")
        
        Returns:
            Lista de franquicias Grido encontradas en Google Maps
        """
        # Extraer términos geográficos
        geo_terms = self._extract_geographic_terms(search_term)
        all_results = []
        
        # Buscar con cada término geográfico
        for geo_term in geo_terms:
            google_results = self.search_google_maps(geo_term)
            
            for result in google_results:
                result['geographic_term'] = geo_term
                result['search_strategy'] = f"Google Maps ({geo_term})"
                
                # Evitar duplicados usando place_id
                place_id = result.get('place_id', '')
                if not any(r.get('place_id') == place_id for r in all_results):
                    all_results.append(result)
        
        # Si no hay términos geográficos específicos, buscar directamente
        if not geo_terms or not all_results:
            direct_results = self.search_google_maps(search_term)
            for result in direct_results:
                result['search_strategy'] = "Google Maps (directo)"
                place_id = result.get('place_id', '')
                if not any(r.get('place_id') == place_id for r in all_results):
                    all_results.append(result)
        
        # Ordenar por relevancia
        all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        logger.info(f"Google Maps Grido búsqueda: {len(all_results)} resultados para '{search_term}'")
        return all_results[:8]
    
    def search_combined(self, search_term: str, use_online: bool = True) -> List[Dict]:
        """
        Búsqueda combinada: local + online (si está habilitado)
        
        Args:
            search_term: Término de búsqueda
            use_online: Si usar búsqueda online como respaldo
        
        Returns:
            Lista combinada de resultados
        """
        results = []
        
        # Primero búsqueda local (más rápida y precisa para Grido)
        local_results = self.search_local_stores(search_term)
        
        # Marcar resultados locales
        for result in local_results:
            result['source'] = 'local'
            results.append(result)
        
        # Si no hay suficientes resultados locales, usar búsqueda online
        if len(local_results) < 3 and use_online:
            logger.info("Complementando con búsqueda online...")
            online_results = self.search_store_by_name(search_term)
            
            # Agregar resultados online que no dupliquen los locales
            for online_result in online_results[:5]:  # Limitar resultados online
                online_result['source'] = 'online'
                online_result['score'] = online_result.get('confidence', 0.5)
                
                # Verificar que no sea duplicado (comparar coordenadas)
                is_duplicate = False
                for local_result in local_results:
                    local_lat = local_result.get('lat', 0)
                    local_lon = local_result.get('lon', 0)
                    online_lat = online_result.get('lat', 0)
                    online_lon = online_result.get('lon', 0)
                    
                    # Si están muy cerca (menos de 100m), es probablemente el mismo lugar
                    distance = ((local_lat - online_lat) ** 2 + (local_lon - online_lon) ** 2) ** 0.5
                    if distance < 0.001:  # Aproximadamente 100m
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    results.append(online_result)
        
        # Ordenar por puntaje final
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        logger.info(f"Búsqueda combinada: {len(local_results)} locales + {len(results) - len(local_results)} online")
        return results[:10]  # Limitar a 10 resultados totales


# Instancia global del servicio
location_service = LocationService()