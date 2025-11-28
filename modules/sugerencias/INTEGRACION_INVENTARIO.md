# 🔄 Integración Directa con Inventario - Sincronización en Tiempo Real

## 📋 Resumen de Cambios

Se ha implementado exitosamente la **sincronización directa** entre el módulo de **Inventario** y el módulo de **Sugerencias**, eliminando la necesidad de subir archivos Excel manualmente.

## ✨ Nuevas Características

### 🔌 Conexión Directa al Inventario

**Antes:**
- ❌ Subir archivos Excel manualmente
- ❌ Errores de formato
- ❌ Datos desactualizados
- ❌ Proceso manual repetitivo

**Ahora:**
- ✅ Conexión automática al módulo de inventario
- ✅ Datos en tiempo real
- ✅ Sin errores manuales
- ✅ Sincronización automática

### 🔄 Sincronización Automática

- **Scheduler inteligente**: Sincroniza cada 5 minutos (configurable: 1, 2, 5, 10, 15, 30, 60 min)
- **Sincronización manual**: Botón para forzar sync inmediata
- **Cache local**: Almacena snapshot para consultas rápidas
- **Background worker**: No interfiere con la UI

### 📊 Vista Previa en Tiempo Real

- **Dashboard de estado**: Métricas en vivo del inventario
- **Tablas interactivas**: Ver productos por categoría (Impulsivos/Granel)
- **Estados visuales**: Colores según stock (🟢 OK / 🟡 BAJO / 🔴 SIN)
- **Estadísticas**: Distribución completa del inventario

## 🏗️ Arquitectura

```
BusinessSuite/
├── modules/
│   ├── inventory/                          # Módulo fuente
│   │   └── data/
│   │       └── inventario.json            # ← Fuente de verdad
│   │
│   └── sugerencias/                        # Módulo consumidor
│       ├── services/
│       │   ├── inventory_sync_service.py  # 🆕 Servicio de sync
│       │   ├── inventory_scheduler.py     # 🆕 Scheduler automático
│       │   └── database_service.py        # ✏️ Métodos para snapshots
│       ├── ui/
│       │   ├── inventory_connection.py    # 🆕 UI de conexión
│       │   └── pages.py                   # ✏️ Selector de modo
│       └── data/
│           └── inventory_cache.json       # 🆕 Cache local
```

## 📁 Archivos Nuevos

### 1. `inventory_sync_service.py`

**Propósito**: Servicio principal de sincronización

**Funciones clave:**
```python
# Leer inventario directamente del archivo
read_inventory_from_file(tienda_id) -> Dict

# Sincronizar a cache local
sync_to_cache(tienda_id) -> bool

# Obtener resumen ejecutivo
get_inventory_summary(tienda_id) -> Dict

# Forzar sincronización manual
force_sync(tienda_id) -> Tuple[bool, str]
```

**Características:**
- ✅ Mapeo de 70+ productos
- ✅ Cálculo automático de estados
- ✅ Conversión impulsivos + granel
- ✅ Metadata detallada

### 2. `inventory_scheduler.py`

**Propósito**: Scheduler automático para sync periódica

**Clases:**
```python
InventorySyncScheduler:
    - start(tienda_id)          # Inicia sync automática
    - stop()                    # Detiene sync
    - get_status()              # Estado actual
    - set_interval(minutes)     # Cambia intervalo

InventorySyncUI:
    - render_status_widget()    # Widget de estado
    - render_controls()         # Controles de scheduler
```

**Características:**
- ✅ Thread daemon (no bloquea app)
- ✅ Intervalo configurable (1-60 min)
- ✅ Reintentos automáticos
- ✅ Estadísticas de sync

### 3. `inventory_connection.py`

**Propósito**: UI moderna para conexión directa

**Componentes:**
```python
InventoryConnectionUI:
    - render_connection_status()     # Estado de conexión
    - render_inventory_preview()     # Vista previa
    - render_sync_controls()         # Controles de sync
    - render_full_page()            # Página completa
```

**Características:**
- ✅ Métricas en tiempo real
- ✅ Tablas con colores por estado
- ✅ Tabs: Impulsivos / Granel / Stats
- ✅ Botones de acción

## 🔧 Actualizaciones

### `database_service.py`

**Nuevos métodos:**
```python
# Guardar snapshot del inventario
save_inventory_snapshot(store_id, inventory_data) -> int

# Obtener último snapshot
get_latest_inventory_snapshot(store_id) -> Dict
```

### `pages.py`

**Cambios:**
- ➕ Radio button para seleccionar modo:
  - 🔗 Conexión Directa (Recomendado)
  - 📤 Subir Excel (Manual)
- ➕ Lógica para ambos modos
- ➕ Conversión automática de formato

## 🎯 Mapeo de Productos

### Productos Mapeados

**Impulsivos (36):**
- Palitos (6): Frutilla, Limón, Naranja, Crema Americana, Crema Frutilla, Bombón
- Alfajores (4): Crocantino, Delicia, Casatta, Almendrado
- Bombones (4): Escocés, Suizo, Crocante, Vainilla Split
- Familiares (4): Familiar 1, 2, 3, 4
- Tortas (varios tamaños)

**Granel (36):**
- Cremas (18): Americana, Tramontana, Dulce de Leche, etc.
- Agua (18): Frutilla, Limón, Ananá, etc.

## 📊 Cálculo de Estados

```python
def _calculate_stock_status(bultos, categoria):
    if bultos == 0:
        return "SIN STOCK"  # 🔴
    
    if categoria == "Por Kilos":
        # Granel: más tolerante
        if bultos <= 3:
            return "STOCK BAJO"  # 🟡
        else:
            return "STOCK OK"  # 🟢
    else:
        # Impulsivo: más estricto
        if bultos <= 2:
            return "STOCK BAJO"  # 🟡
        else:
            return "STOCK OK"  # 🟢
```

## 🚀 Uso

### Modo Conexión Directa (Recomendado)

1. Abre el módulo de **Sugerencias**
2. Ve a **"📦 Paso 2: Carga tu Inventario Actual"**
3. Selecciona **"🔗 Conexión Directa al Inventario"**
4. El sistema se conecta automáticamente
5. (Opcional) Click **"🔄 Sincronizar Ahora"** para actualizar
6. (Opcional) Click **"👁️ Ver Detalles"** para vista previa
7. Continúa con el Paso 3 (generar sugerencia)

### Scheduler Automático

1. En la sección de **"Controles de Sincronización"**
2. Click **"▶️ Iniciar Auto-Sync"**
3. Selecciona intervalo (1-60 minutos)
4. El sistema sincroniza automáticamente en background
5. Monitorea el estado en tiempo real

### Modo Manual (Excel)

1. Selecciona **"📤 Subir Archivo Excel"**
2. Usa los tabs para subir archivos
3. Continúa con el proceso tradicional

## 🔍 Ejemplo de Sincronización

```
📊 Resumen de Sincronización:

Tienda: T001
Total productos: 42
Total bultos: 156

Distribución por Estado:
- 🟢 Stock OK: 25 (59.5%)
- 🟡 Stock Bajo: 12 (28.6%)
- 🔴 Sin Stock: 5 (11.9%)

Categorías:
- 🍦 Impulsivos: 28 productos
- ⚖️ Granel: 14 productos

Última sincronización: Hace 2m
Próxima sincronización: En 3m
```

## ⚡ Ventajas

### Para el Usuario

- ✅ **Sin errores**: No más problemas de formato Excel
- ✅ **Tiempo real**: Datos siempre actualizados
- ✅ **Automatización**: Se sincroniza solo
- ✅ **Transparencia**: Ves exactamente qué hay
- ✅ **Rapidez**: Un click en lugar de subir archivos

### Para el Sistema

- ✅ **Fuente única de verdad**: `inventario.json`
- ✅ **Consistencia**: Mismo dato en todos lados
- ✅ **Escalabilidad**: Fácil agregar más productos
- ✅ **Mantenibilidad**: Código centralizado
- ✅ **Trazabilidad**: Snapshots históricos

## 🐛 Solución de Problemas

### No se conecta al inventario

**Problema**: "No hay inventario disponible"

**Soluciones:**
1. Verifica que el módulo de Inventario tenga datos
2. Asegúrate de estar en la tienda correcta (T001, T002, etc.)
3. Recarga la página
4. Usa modo manual como alternativa

### Sincronización lenta

**Problema**: Tarda mucho en sincronizar

**Soluciones:**
1. Reduce el intervalo de sync (ej: 2 minutos en lugar de 5)
2. Usa sincronización manual bajo demanda
3. Verifica que el archivo `inventario.json` no sea muy grande

### Productos no aparecen

**Problema**: Algunos productos no se sincronizan

**Soluciones:**
1. Verifica el mapeo en `inventory_sync_service.py`
2. Asegúrate de que los nombres coincidan exactamente
3. Revisa que el producto esté en la tienda correcta
4. Agrega el producto al mapeo si es nuevo

## 📝 Configuración

### Agregar Nuevo Producto al Mapeo

En `inventory_sync_service.py`:

```python
self.product_mapping = {
    # ... productos existentes ...
    
    # Agregar nuevo producto
    "Nombre en Inventario": "nombre_en_sugerencias",
    
    # Ejemplo:
    "Palito Nuevo Sabor": "palito_nuevo_sabor",
}
```

### Cambiar Intervalo de Sync

En la UI:
1. Ve a **"Controles de Sincronización"**
2. Selecciona nuevo intervalo del dropdown
3. Click **"💾 Actualizar Intervalo"**

O en código (`inventory_scheduler.py`):

```python
scheduler = InventorySyncScheduler(
    sync_service=inventory_sync_service,
    interval_minutes=10  # ← Cambia aquí
)
```

## 🎉 Resultado Final

El módulo de **Sugerencias** ahora:

1. ✅ Se conecta directamente al **Inventario**
2. ✅ Sincroniza automáticamente cada X minutos
3. ✅ Muestra datos en tiempo real
4. ✅ Elimina errores manuales
5. ✅ Mantiene historial de snapshots
6. ✅ Ofrece vista previa interactiva
7. ✅ Permite sync manual bajo demanda
8. ✅ Funciona en background sin interrumpir

---

**Desarrollado con ❤️ para BusinessSuite - Netw@rd**
