# Módulo de Sugerencias Inteligentes

Sistema de recomendación de compras basado en Inteligencia Artificial para Heladería Grido Paraguay, integrado en BusinessSuite.

## Características

- 🌤️ **Pronóstico del clima**: Análisis meteorológico para predecir demanda
- 📊 **Análisis de demanda**: Evaluación de patrones de consumo
- 🏪 **Gestión por tienda**: Sugerencias personalizadas por ubicación
- 📈 **Optimización de stock**: Recomendaciones basadas en datos históricos
- 📋 **Historial y analytics**: Seguimiento completo de sugerencias
- 📑 **Reportes detallados**: Información exportable en múltiples formatos

## Estructura del Módulo

```
sugerencias/
├── __init__.py
├── main_sugerencias.py         # Punto de entrada principal
├── config/                      # Configuraciones
│   ├── settings.py             # Configuración general
│   ├── productos_completos.py  # Catálogo de productos
│   └── bultos_config.py        # Configuración de bultos
├── core/                        # Lógica principal
│   └── suggestion_engine.py    # Motor de sugerencias
├── models/                      # Modelos de datos
│   └── data_models.py          # Definiciones de clases
├── services/                    # Servicios externos
│   ├── database_service.py     # Gestión de BD
│   ├── weather_service.py      # API del clima
│   └── location_service.py     # Servicios de ubicación
├── ui/                          # Interfaz de usuario
│   ├── pages.py                # Páginas de la app
│   └── components.py           # Componentes UI
└── data/                        # Datos y BD
    ├── stores.db               # Base de datos SQLite
    └── *.xlsx                  # Archivos de ejemplo
```

## Acceso

**Solo Administradores** - Este módulo está restringido para usuarios con rol de administrador en BusinessSuite.

## Uso

1. Inicia sesión como administrador en BusinessSuite
2. Desde el dashboard principal, selecciona "🤖 Sugerencias Inteligentes"
3. Configura tiendas y parámetros
4. Genera sugerencias automáticas
5. Revisa y exporta reportes

## Dependencias Adicionales

Este módulo requiere:
- requests
- beautifulsoup4
- python-dotenv
- geopy
- plotly

Todas las dependencias se instalan con el `requirements.txt` de BusinessSuite.

## API del Clima

Para funcionalidad completa, configura una API key de OpenWeather:
1. Obtén una clave en https://openweathermap.org/api
2. Crea un archivo `.env` en la raíz de BusinessSuite
3. Agrega: `OPENWEATHER_API_KEY=tu_clave_aqui`

## Integración

Este módulo está completamente integrado con BusinessSuite:
- Comparte el sistema de autenticación
- Usa la misma interfaz de navegación
- Mantiene consistencia visual con los otros módulos
- Gestiona datos de forma independiente

## Autor

Netward Suite - Sistema Integrado de Gestión Empresarial
