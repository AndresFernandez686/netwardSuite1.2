"""
Sistema de Autenticación Unificado para BusinessSuite
Maneja roles de usuario: Admin y Empleado
"""
import streamlit as st
import json
import os
import hashlib
from datetime import datetime

class AuthSystem:
    def __init__(self):
        self.users_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')
        self.ensure_users_file()
    
    def ensure_users_file(self):
        """Asegura que el archivo de usuarios existe con datos por defecto"""
        if not os.path.exists(self.users_file):
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
            default_users = {
                "users": {
                    "admin": {
                        "password": self.hash_password("admin123"),
                        "role": "admin",
                        "name": "Administrador",
                        "created_at": datetime.now().isoformat(),
                        "permissions": ["inventory", "payroll", "reports", "user_management"]
                    },
                    "empleado1": {
                        "password": self.hash_password("emp123"),
                        "role": "employee", 
                        "name": "Empleado 1",
                        "created_at": datetime.now().isoformat(),
                        "permissions": ["inventory"]
                    }
                }
            }
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(default_users, f, indent=2, ensure_ascii=False)
    
    def hash_password(self, password):
        """Hashea la contraseña para almacenamiento seguro"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_users(self):
        """Carga los usuarios del archivo JSON"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.ensure_users_file()
            return self.load_users()
    
    def save_users(self, users_data):
        """Guarda los usuarios en el archivo JSON"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
    
    def authenticate(self, username, password):
        """Autentica un usuario"""
        users_data = self.load_users()
        users = users_data.get('users', {})
        
        if username in users:
            user = users[username]
            if user['password'] == self.hash_password(password):
                return {
                    'username': username,
                    'role': user['role'],
                    'name': user['name'],
                    'permissions': user['permissions']
                }
        return None
    
    def is_admin(self, user_info):
        """Verifica si el usuario es administrador"""
        return user_info and user_info.get('role') == 'admin'
    
    def has_permission(self, user_info, permission):
        """Verifica si el usuario tiene un permiso específico"""
        if not user_info:
            return False
        permissions = user_info.get('permissions', [])
        return permission in permissions
    
    def login_form(self):
        """Muestra el formulario de login"""
        st.markdown("""
        <div style="max-width: 400px; margin: 0 auto; padding: 2rem; border-radius: 10px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    box-shadow: 0 8px 32px 0 rgba(0,0,0,0.2);">
            <h2 style="color: white; text-align: center; margin-bottom: 2rem;">
                🏢 BusinessSuite Login
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                with st.form("login_form"):
                    st.markdown("### 🔐 Iniciar Sesión")
                    
                    username = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario")
                    password = st.text_input("🔒 Contraseña", type="password", placeholder="Ingresa tu contraseña")
                    
                    login_button = st.form_submit_button("🚀 Iniciar Sesión", use_container_width=True)
                    
                    if login_button:
                        if username and password:
                            user_info = self.authenticate(username, password)
                            if user_info:
                                st.session_state.user_info = user_info
                                st.session_state.logged_in = True
                                
                                # Para empleados, ir directamente al inventario
                                if user_info['role'] == 'employee':
                                    st.session_state.current_module = 'inventory'
                                    st.success(f"¡Bienvenido {user_info['name']}! Accediendo al sistema...")
                                else:
                                    st.success(f"¡Bienvenido {user_info['name']}!")
                                
                                st.rerun()
                            else:
                                st.error("❌ Usuario o contraseña incorrectos")
                        else:
                            st.warning("⚠️ Por favor, completa todos los campos")
                
                # Información de usuarios demo
                st.info("**👥 Usuarios Demo:**\n\n"
                       "**Administrador:**\n"
                       "- Usuario: `admin`\n"
                       "- Contraseña: `admin123`\n\n"
                       "**Empleado:**\n"
                       "- Usuario: `empleado1`\n"
                       "- Contraseña: `emp123`")
    
    def logout(self):
        """Cierra la sesión del usuario"""
        for key in ['user_info', 'logged_in']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    def show_user_info(self):
        """Muestra información del usuario logueado en la sidebar"""
        if 'user_info' in st.session_state:
            user = st.session_state.user_info
            
            st.sidebar.markdown("---")
            if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
                self.logout()
    
    def require_permission(self, permission, message="No tienes permisos para acceder a esta función"):
        """Decorator/función para requerir permisos específicos"""
        if not self.is_logged_in():
            return False
        
        user_info = st.session_state.get('user_info')
        if not self.has_permission(user_info, permission):
            st.error(f"🔒 {message}")
            st.info("Contacta al administrador si necesitas acceso a esta función.")
            return False
        
        return True
    
    def is_logged_in(self):
        """Verifica si hay un usuario logueado"""
        return st.session_state.get('logged_in', False) and 'user_info' in st.session_state

# Instancia global del sistema de autenticación
auth_system = AuthSystem()