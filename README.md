# 🏢 BusinessSuite - Suite de Aplicaciones de Negocio

**Sistema Unificado de Gestión Empresarial** que combina múltiples módulos de negocio en una sola aplicación con autenticación por roles.

## 🚀 **Características Principales**

### 🔐 **Sistema de Autenticación por Roles**
- **👑 Administradores:** Acceso completo a todos los módulos
- **👨‍💼 Empleados:** Acceso restringido según permisos
- **🔒 Seguridad:** Autenticación robusta con permisos granulares

### 📦 **Módulo de Gestión de Inventario** 
*(Basado en Netward 1.8)*
- ✅ **Multi-tienda:** Gestión independiente por sucursal
- ✅ **Control de Stock:** Inventario en tiempo real
- ✅ **Sistema de Delivery:** Gestión de entregas y ventas
- ✅ **Mermas y Rupturas:** Control de pérdidas
- ✅ **Reportes Avanzados:** Métricas y análisis

### 💰 **Módulo de Cálculo de Nómina** 
*(Basado en Calculo 1.3 - Solo Administradores)*
- ✅ **Procesamiento Excel/PDF:** Soporte múltiples formatos
- ✅ **Cálculo Inteligente:** Horas normales y especiales
- ✅ **Gestión de Feriados:** Factor x2 configurable
- ✅ **Corrección Automática:** Detección de horarios incompletos
- ✅ **Reportes Detallados:** Exportación a Excel

## 🏗️ **Arquitectura del Sistema**

```
📁 BusinessSuite/
├── 📄 main.py                    # Aplicación principal
├── 📄 requirements.txt           # Dependencias
├── 📁 modules/                   # Módulos de negocio
│   ├── 📁 payroll/              # Cálculo de nómina (Solo Admin)
│   └── 📁 inventory/            # Gestión de inventario
├── 📁 shared/                   # Recursos compartidos
│   └── auth_unified.py          # Sistema de autenticación
└── 📁 data/                     # Datos por módulo
    ├── 📁 payroll/
    └── 📁 inventory/
```

## 🚀 **Instalación y Configuración**

### 1. **Clonar el Repositorio**
```bash
git clone <repository-url>
cd BusinessSuite
```

### 2. **Crear Entorno Virtual** (Recomendado)
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. **Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### 4. **Ejecutar la Aplicación**
```bash
streamlit run main.py
```

## 👥 **Usuarios de Prueba**

### 🔐 **Sistema Principal**
| Usuario     | Contraseña | Rol           | Permisos                    |
|-------------|------------|---------------|-----------------------------|
| `admin`     | `admin123` | Administrador | Inventario + Nómina         |
| `empleado1` | `emp123`   | Empleado      | Solo Inventario             |

### 📦 **Módulo de Inventario** (Login interno adicional)
| Usuario     | Rol           | Tienda        |
|-------------|---------------|---------------|
| `admin1`    | Administrador | Todas         |
| `empleado1` | Empleado      | Seminario     |
| `empleado2` | Empleado      | Mcal Lopez    |

## 🎯 **Funcionalidades por Rol**

### 👑 **Administradores**
- ✅ Acceso completo al **Dashboard Principal**
- ✅ **Módulo de Inventario:** Todas las funciones
- ✅ **Módulo de Nómina:** Cálculo de sueldos exclusivo
- ✅ **Gestión de Usuarios:** Configuración de permisos
- ✅ **Reportes Avanzados:** Métricas consolidadas

### 👨‍💼 **Empleados**
- ✅ Acceso al **Dashboard Principal**
- ✅ **Módulo de Inventario:** Gestión básica
- ❌ **Módulo de Nómina:** Restringido
- ✅ **Funciones Básicas:** Según permisos asignados

## 📊 **Módulos Detallados**

### 📦 **Gestión de Inventario**

#### **Para Empleados:**
- 📦 **Inventario:** Control de stock por categorías
- 🚚 **Delivery:** Gestión de entregas
- ⚠️ **Mermas:** Registro de pérdidas

#### **Para Administradores:**
- 📊 **Vista Multi-tienda:** Control consolidado
- 📈 **Reportes:** Análisis y métricas
- ⚙️ **Configuraciones:** Gestión de tiendas
- 📋 **Historial:** Auditoría completa

### 💰 **Cálculo de Nómina** (Solo Administradores)

#### **Funciones Principales:**
- 📊 **Procesamiento:** Excel y PDF múltiples
- ⏰ **Cálculo Automático:** Horas normales (100%) y especiales (130%)
- 🎯 **Feriados:** Factor x2 configurable por día
- 🔧 **Corrección Inteligente:** Detección de horarios incompletos
- 📋 **Reportes:** Exportación detallada a Excel

#### **Características Avanzadas:**
- ✅ **Detección Automática:** Registros sin entrada/salida
- ✅ **Corrección Guiada:** Interface para completar horarios
- ✅ **Validación Inteligente:** Detección de horarios ambiguos
- ✅ **Procesamiento Masivo:** Múltiples PDFs simultáneos

## 🔧 **Configuración Avanzada**

### **Personalización de Roles**
Edita `shared/auth_unified.py` para:
- Agregar nuevos usuarios
- Modificar permisos
- Configurar roles personalizados

### **Configuración de Módulos**
- **Inventario:** Configura tiendas en `data/inventory/inventario.json`
- **Nómina:** Ajusta valores por defecto en cada módulo

## 📈 **Roadmap Futuro**

### 🎯 **Próximas Funcionalidades**
- 📊 **Dashboard Ejecutivo:** Métricas consolidadas
- 🔔 **Sistema de Notificaciones:** Alertas en tiempo real
- 📱 **API REST:** Integración con otros sistemas
- 🌐 **Multi-idioma:** Soporte internacional
- 📊 **BI Avanzado:** Análisis predictivo
- 🔄 **Sincronización:** Respaldo automático

### 🏗️ **Módulos Futuros**
- 💳 **Facturación:** Sistema de facturación completo
- 👥 **RRHH:** Gestión de recursos humanos
- 📞 **CRM:** Gestión de clientes
- 🏦 **Contabilidad:** Sistema contable básico

## 🛠️ **Desarrollo y Contribución**

### **Estructura de Desarrollo**
```bash
# Cada módulo es independiente
modules/
├── payroll/          # Módulo de nómina
│   ├── main_payroll.py
│   └── ...
└── inventory/        # Módulo de inventario
    ├── main_inventory.py
    └── ...
```

### **Agregar Nuevos Módulos**
1. Crear carpeta en `modules/`
2. Implementar `main_<module>.py`
3. Agregar permisos en `auth_unified.py`
4. Actualizar navegación en `main.py`

## 📞 **Soporte y Contacto**

- **Desarrollado con:** GitHub Copilot & Claude
- **Framework:** Streamlit
- **Versión:** 1.0
- **Fecha:** Noviembre 2025

## 📄 **Licencia**

Este proyecto está desarrollado para uso interno empresarial. Todos los derechos reservados.

---


```bash
# Ejecutar BusinessSuite
streamlit run main.py
```

**¡Transforma tu gestión empresarial con BusinessSuite!** 🚀
