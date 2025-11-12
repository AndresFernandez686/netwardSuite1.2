#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Configuración de Tiendas - Netw@rd 2.0
Gestión de múltiples ubicaciones con IDs únicos
"""

import json
import streamlit as st
from datetime import datetime
import os

class GestorTiendas:
    def __init__(self, archivo_inventario="inventario.json"):
        self.archivo_inventario = archivo_inventario
        self.config = self.cargar_configuracion()
        self.inicializar_tiendas_default()  # Inicializar tiendas automáticamente
    
    def cargar_configuracion(self):
        """Carga la configuración de tiendas desde el JSON"""
        try:
            with open(self.archivo_inventario, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("configuracion", {})
        except FileNotFoundError:
            return self.crear_configuracion_default()
        except Exception as e:
            st.error(f"Error cargando configuración: {str(e)}")
            return {}
    
    def crear_configuracion_default(self):
        """Crea configuración por defecto si no existe"""
        config_default = {
            "tiendas": {
                "T001": {
                    "id": "T001",
                    "nombre": "Seminario",
                    "direccion": "Dirección no especificada",
                    "activa": True,
                    "fecha_creacion": datetime.now().strftime("%Y-%m-%d")
                },
                "T002": {
                    "id": "T002",
                    "nombre": "Mcal Lopez",
                    "direccion": "Dirección no especificada",
                    "activa": True,
                    "fecha_creacion": datetime.now().strftime("%Y-%m-%d")
                }
            },
            "tienda_default": "T001",
            "version_esquema": "2.0"
        }
        return config_default
    
    def obtener_tiendas_activas(self):
        """Retorna lista de tiendas activas"""
        tiendas = self.config.get("tiendas", {})
        return {id: info for id, info in tiendas.items() if info.get("activa", True)}
    
    def obtener_tienda_default(self):
        """Retorna el ID de la tienda por defecto"""
        return self.config.get("tienda_default", "T001")
    
    def agregar_tienda(self, nombre, direccion=""):
        """Agrega una nueva tienda"""
        tiendas = self.config.get("tiendas", {})
        
        # Generar nuevo ID
        ids_existentes = [int(id[1:]) for id in tiendas.keys() if id.startswith("T")]
        nuevo_numero = max(ids_existentes) + 1 if ids_existentes else 1
        nuevo_id = f"T{nuevo_numero:03d}"
        
        # Crear nueva tienda
        nueva_tienda = {
            "id": nuevo_id,
            "nombre": nombre,
            "direccion": direccion,
            "activa": True,
            "fecha_creacion": datetime.now().strftime("%Y-%m-%d")
        }
        
        tiendas[nuevo_id] = nueva_tienda
        self.config["tiendas"] = tiendas
        
        # Crear estructura de inventario vacía para la nueva tienda
        self.crear_inventario_tienda(nuevo_id)
        
        return nuevo_id
    
    def crear_inventario_tienda(self, tienda_id):
        """Crea estructura de inventario vacía para una tienda"""
        try:
            with open(self.archivo_inventario, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "inventario_por_tienda" not in data:
                data["inventario_por_tienda"] = {}
            
            data["inventario_por_tienda"][tienda_id] = {
                "Impulsivo": {},
                "Por Kilos": {},
                "Extras": {}
            }
            
            # Actualizar configuración
            data["configuracion"] = self.config
            
            with open(self.archivo_inventario, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            st.error(f"Error creando inventario para tienda {tienda_id}: {str(e)}")
    
    def desactivar_tienda(self, tienda_id):
        """Desactiva una tienda (no la elimina)"""
        if tienda_id in self.config.get("tiendas", {}):
            self.config["tiendas"][tienda_id]["activa"] = False
            self.guardar_configuracion()
    
    def activar_tienda(self, tienda_id):
        """Activa una tienda"""
        if tienda_id in self.config.get("tiendas", {}):
            self.config["tiendas"][tienda_id]["activa"] = True
            self.guardar_configuracion()
    
    def establecer_tienda_default(self, tienda_id):
        """Establece una tienda como predeterminada"""
        if tienda_id in self.obtener_tiendas_activas():
            self.config["tienda_default"] = tienda_id
            self.guardar_configuracion()
    
    def guardar_configuracion(self):
        """Guarda la configuración en el archivo JSON"""
        try:
            with open(self.archivo_inventario, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data["configuracion"] = self.config
            
            with open(self.archivo_inventario, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            st.error(f"Error guardando configuración: {str(e)}")
    
    def obtener_info_tienda(self, tienda_id):
        """Obtiene información completa de una tienda"""
        return self.config.get("tiendas", {}).get(tienda_id, {})
    
    def inicializar_tiendas_default(self):
        """Inicializa las tiendas con nombres correctos si no existen"""
        tiendas = self.config.get("tiendas", {})
        
        # Actualizar T001 a "Seminario" si existe
        if "T001" in tiendas and tiendas["T001"].get("nombre") == "Tienda Principal":
            tiendas["T001"]["nombre"] = "Seminario"
            self.config["tiendas"] = tiendas
            self.guardar_configuracion()
        
        # Crear T002 "Mcal Lopez" si no existe
        if "T002" not in tiendas:
            tiendas["T002"] = {
                "id": "T002",
                "nombre": "Mcal Lopez",
                "direccion": "Dirección no especificada",
                "activa": True,
                "fecha_creacion": datetime.now().strftime("%Y-%m-%d")
            }
            self.config["tiendas"] = tiendas
            self.crear_inventario_tienda("T002")
            self.guardar_configuracion()

def mostrar_panel_configuracion_tiendas():
    """Interfaz para configurar tiendas"""
    st.header("🏪 Configuración de Tiendas")
    
    gestor = GestorTiendas()
    
    # Mostrar tiendas existentes
    st.subheader("Tiendas Registradas")
    
    tiendas = gestor.config.get("tiendas", {})
    tienda_default = gestor.obtener_tienda_default()
    
    if tiendas:
        for tienda_id, info in tiendas.items():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            
            with col1:
                status = "🟢" if info.get("activa", True) else "🔴"
                default_badge = " 🏆" if tienda_id == tienda_default else ""
                st.write(f"{status} **{info.get('nombre', 'Sin nombre')}**{default_badge}")
                st.caption(f"ID: {tienda_id} | {info.get('direccion', 'Sin dirección')}")
            
            with col2:
                st.caption(f"Creada: {info.get('fecha_creacion', 'N/A')}")
            
            with col3:
                if info.get("activa", True):
                    if st.button("Desactivar", key=f"deactivate_{tienda_id}"):
                        gestor.desactivar_tienda(tienda_id)
                        st.rerun()
                else:
                    if st.button("Activar", key=f"activate_{tienda_id}"):
                        gestor.activar_tienda(tienda_id)
                        st.rerun()
            
            with col4:
                if tienda_id != tienda_default and info.get("activa", True):
                    if st.button("Hacer Default", key=f"default_{tienda_id}"):
                        gestor.establecer_tienda_default(tienda_id)
                        st.rerun()
    
    st.divider()
    
    # Agregar nueva tienda
    st.subheader("➕ Agregar Nueva Tienda")
    
    with st.form("nueva_tienda"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_tienda = st.text_input("Nombre de la Tienda *", placeholder="Ej: Tienda Mall Plaza")
        
        with col2:
            direccion_tienda = st.text_input("Dirección", placeholder="Ej: Av. Principal 123")
        
        if st.form_submit_button("Crear Tienda"):
            if nombre_tienda.strip():
                nuevo_id = gestor.agregar_tienda(nombre_tienda.strip(), direccion_tienda.strip())
                st.success(f"✅ Tienda creada exitosamente con ID: {nuevo_id}")
                st.rerun()
            else:
                st.error("El nombre de la tienda es obligatorio")

def selector_tienda_empleado():
    """Selector de tienda para empleados"""
    gestor = GestorTiendas()
    tiendas_activas = gestor.obtener_tiendas_activas()
    tienda_default = gestor.obtener_tienda_default()
    
    if not tiendas_activas:
        st.error("No hay tiendas activas configuradas")
        return None
    
    # Crear opciones para el selectbox
    opciones_tiendas = {}
    for tienda_id, info in tiendas_activas.items():
        opciones_tiendas[f"{info['nombre']} ({tienda_id})"] = tienda_id
    
    # Determinar índice por defecto
    default_index = 0
    for idx, (label, tid) in enumerate(opciones_tiendas.items()):
        if tid == tienda_default:
            default_index = idx
            break
    
    # Mostrar selector
    tienda_seleccionada_label = st.selectbox(
        "Selecciona tu tienda:",
        options=list(opciones_tiendas.keys()),
        index=default_index,
        key="selector_tienda_empleado"
    )
    
    return opciones_tiendas[tienda_seleccionada_label]

def cargar_config_tiendas():
    """Función de conveniencia para cargar configuración de tiendas"""
    gestor = GestorTiendas()
    return gestor.config.get("tiendas", {})

def obtener_nombre_tienda(tienda_id):
    """Función de conveniencia para obtener el nombre de una tienda por ID"""
    gestor = GestorTiendas()
    tiendas = gestor.config.get("tiendas", {})
    return tiendas.get(tienda_id, {}).get("nombre", f"Tienda {tienda_id}")

if __name__ == "__main__":
    st.set_page_config(page_title="Netw@rd - Config Tiendas", layout="wide")
    mostrar_panel_configuracion_tiendas()