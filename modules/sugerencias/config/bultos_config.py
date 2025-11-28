"""
Configuración de conversión de bultos a unidades
"""

# CONVERSIÓN DE BULTOS A UNIDADES
# Cada producto tiene una cantidad específica de unidades por bulto
# Formato: 'NOMBRE_PRODUCTO': unidades_por_bulto

BULTOS_CONVERSION = {
    # ALFAJORES
    'Alfajor Almendrado': 12,  # ¿Cuántos alfajores vienen en 1 bulto?
    'Alfajor Bombon Cookies and Crema': 12,
    'Alfajor Bombon Crocante': 12,
    'Alfajor Bombon Escoces': 12,
    'Alfajor Bombon Suizo': 12,
    'Alfajor Bombon Vainilla': 12,
    'Alfajor Casatta': 12,
    
    # BOCADITOS
    'Almendrado en Caja x 8': 8,
    'Bocaditos Frambuesa': 8,
    'Bocaditos Frutilla': 8,
    
    # BOMBONES EN CAJA
    'Bombon Crocante Caja x 8': 8,
    'Bombon Escoces en Caja x 8': 8,
    'Bombon Suizo en Caja x 8': 8,
    'Bombon cookies and cream caja x 8': 8,
    
    # PALITOS
    'Palito Bombon': 24,  # ¿Cuántos palitos vienen en 1 bulto?
    'Palito Bombon Caja x10': 10,
    'Palito Crema Americana': 24,
    'Palito Crema Americana Caja x10': 10,
    'Palito Crema Frutilla': 24,
    'Palito Crema Frutilla Caja x10': 10,
    'Palito Frutal Frutilla': 24,
    'Palito Frutal Frutilla Caja x10': 10,
    'Palito Frutal Limon': 24,
    'Palito Frutal Limon Caja x10': 10,
    'Palito Frutal Naranja': 24,
    'Palito Frutal Naranja Caja x10': 10,
    
    # TENTACIONES
    'Tentacion Chocolate': 6,  # ¿Cuántas tentaciones vienen en 1 bulto?
    'Tentacion Chocolate con Almendra': 6,
    'Tentacion Cookies': 6,
    'Tentacion Crema Americana': 6,
    'Tentacion Dulce de Leche': 6,
    'Tentacion Dulce de Leche Granizado': 6,
    'Tentacion Frutilla': 6,
    'Tentacion Granizado': 6,
    'Tentacion Limon': 6,
    'Tentacion Mascarpone': 6,
    'Tentacion Menta Granizada': 6,
    'Tentacion Toddy': 6,
    'Tentacion Vainilla': 6,
    
    # HELADOS SIN AZÚCAR
    'Helado sin Azucar Durazno a la Crema': 1,  # ¿kg por bulto?
    'Helado sin Azucar Frutilla a la Crema': 1,
    'Helado sin Azucar chocolate sin Tacc': 1,
    
    # TORTAS
    'Torta Grido Rellena': 1,  # 1 torta por bulto
    'Torta Milka': 1,
    
    # YOGURT HELADO
    'Yogurt Helado Frutilla sin Tacc': 1,  # ¿kg por bulto?
    'Yogurt Helado Frutos del Bosque sin Tacc': 1,
    'Yogurt Helado Mango Maracuya': 1,
    
    # OTROS
    'Crocantino': 12,
    'Delicia': 12,
    'Familiar 1': 1,
    'Familiar 2': 1,
    'Familiar 3': 1,
    'Familiar 4': 1,
    'Grido Toy': 12,
    'Pizza': 1,
}

def get_unidades_por_bulto(producto: str) -> int:
    """
    Obtiene la cantidad de unidades que vienen en un bulto
    
    Args:
        producto: Nombre del producto
        
    Returns:
        Cantidad de unidades por bulto (por defecto 1 si no está definido)
    """
    return BULTOS_CONVERSION.get(producto, 1)

def calcular_unidades_totales(producto: str, bultos: int) -> int:
    """
    Calcula el total de unidades basado en la cantidad de bultos
    
    Args:
        producto: Nombre del producto
        bultos: Cantidad de bultos
        
    Returns:
        Total de unidades
    """
    unidades_por_bulto = get_unidades_por_bulto(producto)
    return bultos * unidades_por_bulto
