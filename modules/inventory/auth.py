# Lógica y datos de usuarios con asignación de tiendas - MODO BETA
import streamlit as st

# CONFIGURACIÓN BETA: Acepta cualquier contraseña
MODO_BETA = True

# Estructura: usuario -> {'rol': str, 'tienda': str}
usuarios = {
    'empleado1': {'rol': 'empleado', 'tienda': 'T001'},  # Seminario
    'empleado2': {'rol': 'empleado', 'tienda': 'T002'},  # Mcal Lopez
    'empleado3': {'rol': 'empleado', 'tienda': 'T001'},  # Seminario
    'admin1': {'rol': 'administrador', 'tienda': 'ALL'},  # Acceso a todas las tiendas
    'admin': {'rol': 'administrador', 'tienda': 'ALL'},   # Usuario admin adicional
    'empleado': {'rol': 'empleado', 'tienda': 'T001'},   # Usuario empleado genérico
}

def login(usuario, contrasena):
    """
    Función de login que acepta usuario y contraseña.
    En modo BETA, cualquier contraseña es válida.
    
    Returns:
        dict: {"exito": bool, "rol": str, "tienda": str, "mensaje": str}
    """
    if not usuario:
        return {
            "exito": False,
            "rol": None,
            "tienda": None,
            "mensaje": "Debe ingresar un usuario"
        }
    
    if not contrasena:
        return {
            "exito": False,
            "rol": None,
            "tienda": None,
            "mensaje": "Debe ingresar una contraseña"
        }
    
    # Verificar si el usuario existe
    if usuario in usuarios:
        user_info = usuarios[usuario]
        
        # En modo BETA, cualquier contraseña es válida
        if MODO_BETA:
            return {
                "exito": True,
                "rol": user_info['rol'],
                "tienda": user_info['tienda'],
                "mensaje": f"Login exitoso - MODO BETA (cualquier contraseña válida)"
            }
        else:
            # Aquí iría la verificación real de contraseña cuando no esté en beta
            # Por ahora, como estamos en beta, siempre es válida
            return {
                "exito": True,
                "rol": user_info['rol'],
                "tienda": user_info['tienda'],
                "mensaje": "Login exitoso"
            }
    else:
        return {
            "exito": False,
            "rol": None,
            "tienda": None,
            "mensaje": f"Usuario '{usuario}' no reconocido. Usuarios disponibles: {', '.join(usuarios.keys())}"
        }

def logout():
    """Función para cerrar sesión CON PRESERVACIÓN DEL CARRITO"""
    # Preservar carrito temporal antes de limpiar sesión
    try:
        # Importar el sistema de persistencia
        from carrito_persistencia import carrito_persistencia
        from datetime import date
        
        # Obtener datos de la sesión actual antes de limpiarla
        usuario_actual = st.session_state.get('usuario_actual')
        tienda_actual = st.session_state.get('tienda_actual')
        carrito_temporal = st.session_state.get('carrito_temporal', [])
        fecha_ultima_carga = st.session_state.get('fecha_ultima_carga')
        
        # Si hay carrito y datos de usuario/tienda, guardarlo
        if carrito_temporal and usuario_actual and tienda_actual:
            if fecha_ultima_carga:
                try:
                    fecha_carrito = date.fromisoformat(fecha_ultima_carga)
                except:
                    fecha_carrito = date.today()
            else:
                fecha_carrito = date.today()
            
            # Guardar carrito antes de logout
            if carrito_persistencia.guardar_carrito(usuario_actual, tienda_actual, fecha_carrito, carrito_temporal):
                st.success(f"💾 Carrito guardado automáticamente ({len(carrito_temporal)} productos)")
            else:
                st.warning("⚠️ No se pudo guardar el carrito automáticamente")
        
    except Exception as e:
        st.warning(f"⚠️ Error al guardar carrito en logout: {str(e)}")
    
    # Limpiar todas las variables de sesión relacionadas con autenticación
    keys_to_clear = [
        'usuario_autenticado',
        'rol_usuario', 
        'tienda_usuario',
        'usuario_actual',
        'rol_actual',
        'tienda_actual',
        'carrito_temporal',  # Limpiar carrito de memoria pero ya está guardado
        'esta_guardando',
        'fecha_ultima_carga',
        'carrito_cargado_desde_archivo'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            st.session_state[key] = None