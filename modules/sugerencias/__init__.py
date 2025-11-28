"""
Módulo de Sugerencias Inteligentes
Sistema de recomendación de compras basado en IA para Heladería Grido Paraguay
"""

__version__ = "1.0.0"
__author__ = "Netward Suite"

# Importaciones principales del módulo
try:
    from .main_sugerencias import init_app, main
    __all__ = ['init_app', 'main']
except ImportError:
    __all__ = []