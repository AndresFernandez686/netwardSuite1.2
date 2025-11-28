"""
Catálogo completo de productos Grido con precios reales
Este archivo reemplazará PRODUCT_SPECS en settings.py
"""

# Mapeo de productos del Excel a IDs internos
PRODUCT_NAME_MAPPING = {
    # ===== IMPULSIVOS =====
    # Alfajores
    "Alfajor Almendrado": "alfajor_almendrado",
    "Alfajor Bombon Crocante": "bombon_crocante",
    "Alfajor Bombon Escoces": "bombon_escoces",
    "Alfajor Bombon Suizo": "bombon_suizo",
    "Alfajor Bombon Cookies and Crema": "bombon_cookies",
    "Alfajor Bombon Vainilla": "bombon_vainilla_split",
    "Alfajor Casatta": "alfajor_casatta",
    "Crocantino": "alfajor_crocantino",
    "Delicia": "alfajor_delicia",
    
    # Familiares - CADA UNO INDIVIDUAL
    "Familiar 1": "familiar_1",
    "Familiar 2": "familiar_2",
    "Familiar 3": "familiar_3",
    "Familiar 4": "familiar_4",
    
    # Palitos - CADA SABOR INDIVIDUAL
    "Palito Bombon": "palito_bombon",
    "Palito Bombon Caja x10": "palito_bombon",
    "Palito Crema Americana": "palito_crema_americana",
    "Palito Crema Americana Caja x10": "palito_crema_americana",
    "Palito Crema Frutilla": "palito_crema_frutilla",
    "Palito Crema Frutilla Caja x10": "palito_crema_frutilla",
    "Palito Frutal Frutilla": "palito_frutal_frutilla",
    "Palito Frutal Frutilla Caja x10": "palito_frutal_frutilla",
    "Palito Frutal Limon": "palito_frutal_limon",
    "Palito Frutal Limon Caja x10": "palito_frutal_limon",
    "Palito Frutal Naranja": "palito_frutal_naranja",
    
    # Tentaciones - CADA SABOR INDIVIDUAL
    "Tentacion Chocolate": "tentacion_chocolate",
    "Tentacion Chocolate con Almendra": "tentacion_chocolate_almendra",
    "Tentacion Cookies": "tentacion_cookies",
    "Tentacion Crema Americana": "tentacion_crema_americana",
    "Tentacion Dulce de Leche Granizado": "tentacion_dulce_granizado",
    "Tentacion Dulce de Leche": "tentacion_dulce_leche",
    "Tentacion Frutilla": "tentacion_frutilla",
    "Tentacion Granizado": "tentacion_granizado",
    "Tentacion Menta Granizada": "tentacion_menta",
    "Tentacion Mascarpone": "tentacion_mascarpone",
    "Tentacion Vainilla": "tentacion_vainilla",
    "Tentacion Limon": "tentacion_limon",
    "Tentacion Toddy": "tentacion_toddy",
    
    # Yogurt y sin azúcar
    "Yogurt Helado Frutilla sin Tacc": "yogurt_frutilla",
    "Yogurt Helado Mango Maracuya": "yogurt_mango",
    "Yogurt Helado Frutos del Bosque sin Tacc": "yogurt_frutos_bosque",
    "Helado sin Azucar Frutilla a la Crema": "sin_azucar_frutilla",
    "Helado sin Azucar Durazno a la Crema": "sin_azucar_durazno",
    "Helado sin Azucar chocolate sin Tacc": "sin_azucar_chocolate",
    
    # Tortas
    "Torta Grido Rellena": "torta_grido",
    "Torta Milka": "torta_milka",
    "Torta Helada Cookies Mousse": "torta_cookies",
    "Pizza": "pizza_helada",
    
    # ===== POR KILOS (GRANEL) =====
    "Vainilla": "granel_vainilla",
    "Chocolate": "granel_chocolate",
    "Fresa": "granel_fresa",
    "Anana a la crema": "granel_anana_crema",
    "Banana con Dulce de leche": "granel_banana_dulce",
    "Capuccino Granizado": "granel_capuccino",
    "Cereza": "granel_cereza",
    "Chocolate Blanco": "granel_chocolate_blanco",
    "Chocolate con Almendra": "granel_chocolate_almendra",
    "Chocolate Mani Crunch": "granel_chocolate_mani",
    "Chocolate Suizo": "granel_chocolate_suizo",
    "Crema Americana": "granel_crema_americana",
    "Crema Cookie": "granel_crema_cookie",
    "Crema Rusa": "granel_crema_rusa",
    "Dulce de Leche": "granel_dulce_leche",
    "Dulce de Leche con Brownie": "granel_dulce_brownie",
    "Dulce de Leche con Nuez": "granel_dulce_nuez",
    "Dulce de Leche Especial": "granel_dulce_especial",
    "Dulce de Leche Granizado": "granel_dulce_granizado",
    "Durazno a la Crema": "granel_durazno",
    "Flan": "granel_flan",
    "Frutos Rojos al Agua": "granel_frutos_rojos",
    "Granizado": "granel_granizado",
    "Kinotos al Whisky": "granel_kinotos",
    "Limon al Agua": "granel_limon",
    "Maracuya": "granel_maracuya",
    "Marroc Grido": "granel_marroc",
    "Mascarpone con Frutos del Bosque": "granel_mascarpone",
    "Menta Granizada": "granel_menta",
    "Naranja Helado al Agua": "granel_naranja",
    "Pistacho": "granel_pistacho",
    "Super Gridito": "granel_super_gridito",
    "Tiramisu": "granel_tiramisu",
    "Tramontana": "granel_tramontana",
    "Candy": "granel_candy"
}

PRODUCT_SPECS_COMPLETO = {
    # ========== HELADOS A GRANEL - Sabores a la Crema (₱120.000/caja de 7.8kg) ==========
    "granel_vainilla": {
        "name": "Vainilla",
        "display_name": "Vainilla (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_chocolate": {
        "name": "Chocolate",
        "display_name": "Chocolate (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_fresa": {
        "name": "Fresa",
        "display_name": "Fresa (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_anana_crema": {
        "name": "Anana a la crema",
        "display_name": "Anana a la crema (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_banana_dulce": {
        "name": "Banana con Dulce de leche",
        "display_name": "Banana con Dulce de leche (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_capuccino": {
        "name": "Capuccino Granizado",
        "display_name": "Capuccino Granizado (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_cereza": {
        "name": "Cereza",
        "display_name": "Cereza (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_chocolate_blanco": {
        "name": "Chocolate Blanco",
        "display_name": "Chocolate Blanco (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_chocolate_almendra": {
        "name": "Chocolate con Almendra",
        "display_name": "Chocolate con Almendra (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_chocolate_mani": {
        "name": "Chocolate Mani Crunch",
        "display_name": "Chocolate Mani Crunch (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_chocolate_suizo": {
        "name": "Chocolate Suizo",
        "display_name": "Chocolate Suizo (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_crema_americana": {
        "name": "Crema Americana",
        "display_name": "Crema Americana (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_crema_cookie": {
        "name": "Crema Cookie",
        "display_name": "Crema Cookie (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_crema_rusa": {
        "name": "Crema Rusa",
        "display_name": "Crema Rusa (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_dulce_leche": {
        "name": "Dulce de Leche",
        "display_name": "Dulce de Leche (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_dulce_brownie": {
        "name": "Dulce de Leche con Brownie",
        "display_name": "Dulce de Leche con Brownie (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_dulce_nuez": {
        "name": "Dulce de Leche con Nuez",
        "display_name": "Dulce de Leche con Nuez (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_dulce_especial": {
        "name": "Dulce de Leche Especial",
        "display_name": "Dulce de Leche Especial (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_dulce_granizado": {
        "name": "Dulce de Leche Granizado",
        "display_name": "Dulce de Leche Granizado (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_durazno": {
        "name": "Durazno a la Crema",
        "display_name": "Durazno a la Crema (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_flan": {
        "name": "Flan",
        "display_name": "Flan (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_granizado": {
        "name": "Granizado",
        "display_name": "Granizado (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_kinotos": {
        "name": "Kinotos al Whisky",
        "display_name": "Kinotos al Whisky (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_maracuya": {
        "name": "Maracuya",
        "display_name": "Maracuya (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_marroc": {
        "name": "Marroc Grido",
        "display_name": "Marroc Grido (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_mascarpone": {
        "name": "Mascarpone con Frutos del Bosque",
        "display_name": "Mascarpone con Frutos del Bosque (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_menta": {
        "name": "Menta Granizada",
        "display_name": "Menta Granizada (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_pistacho": {
        "name": "Pistacho",
        "display_name": "Pistacho (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_super_gridito": {
        "name": "Super Gridito",
        "display_name": "Super Gridito (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_tiramisu": {
        "name": "Tiramisu",
        "display_name": "Tiramisu (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_tramontana": {
        "name": "Tramontana",
        "display_name": "Tramontana (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    "granel_candy": {
        "name": "Candy",
        "display_name": "Candy (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 120000,
        "sabor_tipo": "crema"
    },
    
    # ========== HELADOS A GRANEL - Sabores al Agua (₱88.000/caja de 7.8kg) ==========
    "granel_frutos_rojos": {
        "name": "Frutos Rojos al Agua",
        "display_name": "Frutos Rojos al Agua (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 88000,
        "sabor_tipo": "agua"
    },
    "granel_limon": {
        "name": "Limon al Agua",
        "display_name": "Limon al Agua (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 88000,
        "sabor_tipo": "agua"
    },
    "granel_naranja": {
        "name": "Naranja Helado al Agua",
        "display_name": "Naranja Helado al Agua (Granel)",
        "unit": "kg",
        "kg_per_bulk": 7.8,
        "category": "bulk",
        "shelf_life_days": 180,
        "price_cost_box": 88000,
        "sabor_tipo": "agua"
    },
    
    # ========== CUCURUCHOS (Servidos del granel - sin costo adicional) ==========
    "cucurucho_simple": {
        "name": "Cucurucho 1 Sabor",
        "display_name": "Cucurucho 1 Sabor",
        "unit": "unidades",
        "per_bulk": 0,
        "category": "served",
        "shelf_life_days": 0,
        "price_sale": 6500,
        "portion_size_g": 80
    },
    "cucurucho_doble": {
        "name": "Cucurucho 2 Sabores",
        "display_name": "Cucurucho 2 Sabores",
        "unit": "unidades",
        "per_bulk": 0,
        "category": "served",
        "shelf_life_days": 0,
        "price_sale": 11000,
        "portion_size_g": 100
    },
    "cucurucho_triple": {
        "name": "Cucurucho 3 Sabores",
        "display_name": "Cucurucho 3 Sabores",
        "unit": "unidades",
        "per_bulk": 0,
        "category": "served",
        "shelf_life_days": 0,
        "price_sale": 14000,
        "portion_size_g": 120
    },
    "cucurucho_triple_bañado": {
        "name": "Cucurucho 3 Sabores Bañado",
        "display_name": "Cucurucho 3 Sabores Bañado",
        "unit": "unidades",
        "per_bulk": 0,
        "category": "served",
        "shelf_life_days": 0,
        "price_sale": 17500,
        "portion_size_g": 140
    },
    
    # ========== POTES (Servidos del granel - sin costo adicional) ==========
    "pote_cuarto": {
        "name": "Pote 1/4 KG",
        "display_name": "Pote 1/4 KG",
        "unit": "unidades",
        "per_bulk": 0,
        "category": "served",
        "shelf_life_days": 0,
        "price_sale": 17000,
        "portion_size_g": 250
    },
    "pote_medio": {
        "name": "Pote 1/2 KG",
        "display_name": "Pote 1/2 KG",
        "unit": "unidades",
        "per_bulk": 0,
        "category": "served",
        "shelf_life_days": 0,
        "price_sale": 30000,
        "portion_size_g": 500
    },
    "pote_kilo": {
        "name": "Pote 1 KG",
        "display_name": "Pote 1 KG",
        "unit": "unidades",
        "per_bulk": 0,
        "category": "served",
        "shelf_life_days": 0,
        "price_sale": 52000,
        "portion_size_g": 1000
    },
    
    # ========== BATIDOS (Servidos del granel - sin costo adicional) ==========
    "batido_capuccino": {
        "name": "Batido Capuccino",
        "display_name": "Batido Capuccino",
        "unit": "unidades",
        "per_bulk": 0,
        "category": "served",
        "shelf_life_days": 0,
        "price_sale": 16000,
        "portion_size_g": 200
    },
    "batido_grido": {
        "name": "Batido Grido",
        "display_name": "Batido Grido",
        "unit": "unidades",
        "per_bulk": 0,
        "category": "served",
        "shelf_life_days": 0,
        "price_sale": 14000,
        "portion_size_g": 200
    },
    
    # ========== PALITOS FRUTALES (Bulto = 10 cajas x 10 unidades = 100 und) ==========
    "palito_frutal_frutilla": {
        "name": "Palito Frutal Frutilla",
        "display_name": "Palito Frutal Frutilla",
        "unit": "unidades",
        "per_bulk": 100,  # 10 cajas x 10 und
        "boxes_per_bulk": 10,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 40000,
        "price_sale_unit": 3000
    },
    "palito_frutal_limon": {
        "name": "Palito Frutal Limon",
        "display_name": "Palito Frutal Limón",
        "unit": "unidades",
        "per_bulk": 100,
        "boxes_per_bulk": 10,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 40000,
        "price_sale_unit": 3000
    },
    "palito_frutal_naranja": {
        "name": "Palito Frutal Naranja",
        "display_name": "Palito Frutal Naranja",
        "unit": "unidades",
        "per_bulk": 100,
        "boxes_per_bulk": 10,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 40000,
        "price_sale_unit": 3000
    },
    "palito_frutal": {
        "name": "Palito Frutal",
        "display_name": "Palito Frutal (Genérico)",
        "unit": "unidades",
        "per_bulk": 100,
        "boxes_per_bulk": 10,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 40000,
        "price_sale_unit": 3000
    },
    
    # ========== PALITOS CREMOSOS (Bulto = 10 cajas x 10 unidades = 100 und) ==========
    "palito_crema_americana": {
        "name": "Palito Crema Americana",
        "display_name": "Palito Crema Americana",
        "unit": "unidades",
        "per_bulk": 100,
        "boxes_per_bulk": 10,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 50000,
        "price_sale_unit": 3500
    },
    "palito_crema_frutilla": {
        "name": "Palito Crema Frutilla",
        "display_name": "Palito Crema Frutilla",
        "unit": "unidades",
        "per_bulk": 100,
        "boxes_per_bulk": 10,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 50000,
        "price_sale_unit": 3500
    },
    "palito_cremoso": {
        "name": "Palito Cremoso",
        "display_name": "Palito Cremoso (Genérico)",
        "unit": "unidades",
        "per_bulk": 100,
        "boxes_per_bulk": 10,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 50000,
        "price_sale_unit": 3500
    },
    
    # ========== PALITO BOMBÓN ==========
    "palito_bombon": {
        "name": "Palito Bombon",
        "display_name": "Palito Bombón",
        "unit": "unidades",
        "per_bulk": 100,
        "boxes_per_bulk": 10,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 64000,
        "price_sale_unit": 4000
    },
    
    # ========== ALFAJORES (Bulto = 6 cajas x 6 unidades) ==========
    "alfajor_crocantino": {
        "name": "Crocantino",
        "display_name": "Alfajor Crocantino",
        "unit": "unidades",
        "per_bulk": 36,  # 6 cajas x 6 und
        "boxes_per_bulk": 6,
        "category": "frozen",
        "shelf_life_days": 90,
        "price_cost_box": 41000,
        "price_sale": 41000  # Precio por caja
    },
    "alfajor_delicia": {
        "name": "Delicia",
        "display_name": "Alfajor Delicia",
        "unit": "unidades",
        "per_bulk": 36,
        "boxes_per_bulk": 6,
        "category": "frozen",
        "shelf_life_days": 90,
        "price_cost_box": 41000,
        "price_sale": 41000
    },
    "alfajor_casatta": {
        "name": "Casatta",
        "display_name": "Alfajor Casatta",
        "unit": "unidades",
        "per_bulk": 36,
        "boxes_per_bulk": 6,
        "category": "frozen",
        "shelf_life_days": 90,
        "price_cost_box": 37000,
        "price_sale_unit": 5000
    },
    "alfajor_almendrado": {
        "name": "Almendrado",
        "display_name": "Alfajor Almendrado",
        "unit": "unidades",
        "per_bulk": 36,
        "boxes_per_bulk": 6,
        "category": "frozen",
        "shelf_life_days": 90,
        "price_cost_box": 37000,
        "price_sale_unit": 5000
    },
    
    # ========== BOMBONES (Bulto = 6 cajas x 8 unidades) ==========
    "bombon_escoces": {
        "name": "Bombón Escocés",
        "display_name": "Bombón Escocés",
        "unit": "unidades",
        "per_bulk": 48,  # 6 cajas x 8 und
        "boxes_per_bulk": 6,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 50000,
        "price_sale_unit": 6500
    },
    "bombon_suizo": {
        "name": "Bombón Suizo",
        "display_name": "Bombón Suizo",
        "unit": "unidades",
        "per_bulk": 48,
        "boxes_per_bulk": 6,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 48000,
        "price_sale_unit": 6500
    },
    "bombon_crocante": {
        "name": "Bombón Crocante",
        "display_name": "Bombón Crocante",
        "unit": "unidades",
        "per_bulk": 48,
        "boxes_per_bulk": 6,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 41000,
        "price_sale_unit": 5500
    },
    "bombon_vainilla_split": {
        "name": "Bombón Vainilla Split",
        "display_name": "Bombón Vainilla Split",
        "unit": "unidades",
        "per_bulk": 48,
        "boxes_per_bulk": 6,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 41000,
        "price_sale_unit": 5500
    },
    "bombon_cookies": {
        "name": "Bombón Cookies and Crema",
        "display_name": "Bombón Cookies and Crema",
        "unit": "unidades",
        "per_bulk": 48,
        "boxes_per_bulk": 6,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 41000,
        "price_sale_unit": 5500
    },
    
    # ========== TORTAS (Bulto = 8 tortas) ==========
    "torta": {
        "name": "Torta",
        "display_name": "Torta Helada (Grido/Milka/Cookies/Pizza)",
        "unit": "unidades",
        "per_bulk": 8,
        "boxes_per_bulk": 8,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 350000,
        "price_sale": 52000
    },
    
    # ========== TENTACIÓN (Bulto = 6 unidades) ==========
    "tentacion": {
        "name": "Tentación",
        "display_name": "Tentación (Todos los sabores)",
        "unit": "unidades",
        "per_bulk": 6,
        "boxes_per_bulk": 6,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 130000,
        "price_sale": 32000
    },
    
    # ========== FAMILIAR (Bulto = 6 unidades) - INDIVIDUALES ==========
    "familiar_1": {
        "name": "Familiar 1",
        "display_name": "Familiar 1",
        "unit": "unidades",
        "per_bulk": 6,
        "boxes_per_bulk": 6,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 250000,
        "price_sale": 62000
    },
    
    "familiar_2": {
        "name": "Familiar 2",
        "display_name": "Familiar 2",
        "unit": "unidades",
        "per_bulk": 6,
        "boxes_per_bulk": 6,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 250000,
        "price_sale": 62000
    },
    
    "familiar_3": {
        "name": "Familiar 3",
        "display_name": "Familiar 3",
        "unit": "unidades",
        "per_bulk": 6,
        "boxes_per_bulk": 6,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 250000,
        "price_sale": 62000
    },
    
    "familiar_4": {
        "name": "Familiar 4",
        "display_name": "Familiar 4",
        "unit": "unidades",
        "per_bulk": 6,
        "boxes_per_bulk": 6,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 250000,
        "price_sale": 62000
    },
    
    # ========== YOGURT HELADO Y SIN AZÚCAR (Bulto = 6 unidades estimado) ==========
    "helado_sin_azucar": {
        "name": "Helado Sin Azúcar / Yogurt Helado",
        "display_name": "Helado Sin Azúcar / Yogurt Helado",
        "unit": "unidades",
        "per_bulk": 6,
        "boxes_per_bulk": 6,
        "category": "frozen",
        "shelf_life_days": 120,
        "price_cost_box": 130000,  # Estimado similar a tentación
        "price_sale": 32000
    }
}


# ============================================================================
# FUNCIONES HELPER PARA CLASIFICACIÓN
# ============================================================================

def get_producto_tipo(product_id: str) -> str:
    """
    Determina si un producto es 'impulsivo' o 'granel'
    
    Args:
        product_id: ID del producto
        
    Returns:
        'impulsivo' o 'granel'
    """
    if product_id.startswith('granel_'):
        return 'granel'
    else:
        return 'impulsivo'


def filter_products_by_tipo(products_dict: dict, tipo: str) -> dict:
    """
    Filtra productos por tipo
    
    Args:
        products_dict: Diccionario de productos
        tipo: 'impulsivo' o 'granel'
        
    Returns:
        Diccionario filtrado
    """
    return {
        pid: spec for pid, spec in products_dict.items()
        if get_producto_tipo(pid) == tipo
    }


# Agregar tipo_producto a todos los productos
for product_id, spec in PRODUCT_SPECS_COMPLETO.items():
    spec['tipo_producto'] = get_producto_tipo(product_id)
