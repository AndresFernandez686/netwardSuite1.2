"""
UI modular para delivery de empleados.
Reemplaza la funcionalidad de ui_empleado.py relacionada con entregas.
"""
import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import date, datetime

from ...core.data_models import DeliveryRecord, Product
from ...data.persistence import DataPersistence
from ...data.history import HistoryManager
from ..components.widgets import (
    FilterPanel, MetricCards, StatusIndicators, 
    NotificationManager, ActionButtons, LoadingManager
)

class EmployeeDeliveryUI:
    """UI modular para delivery de empleados"""
    
    def __init__(self):
        self._persistence = DataPersistence()
        self._history = HistoryManager()
        
        # Inicializar en session_state si es necesario
        if "employee_delivery_ui" not in st.session_state:
            st.session_state.employee_delivery_ui = {
                "selected_products": [],
                "delivery_data": {}
            }
    
    def render(self, usuario: str):
        """Renderiza la interfaz de delivery para empleados"""
        st.header("🚚 Gestión de Entregas")
        
        # Cargar inventario para selección
        inventario = self._persistence.load_inventory()
        
        if not inventario:
            NotificationManager.error("No se pudo cargar el inventario")
            return
        
        # Pestañas principales
        tab1, tab2, tab3 = st.tabs([
            "📦 Nueva Entrega", 
            "📋 Entregas del Día", 
            "📊 Resumen"
        ])
        
        with tab1:
            self._render_new_delivery(usuario, inventario)
        
        with tab2:
            self._render_today_deliveries(usuario)
        
        with tab3:
            self._render_delivery_summary(usuario)
    
    def _render_new_delivery(self, usuario: str, inventario: Dict[str, Any]):
        """Renderiza formulario para nueva entrega"""
        st.subheader("📝 Registrar Nueva Entrega")
        
        # Información de la entrega
        col1, col2 = st.columns(2)
        
        with col1:
            cliente = st.text_input(
                "👤 Cliente",
                key="delivery_cliente",
                placeholder="Nombre del cliente"
            )
            
            direccion = st.text_area(
                "📍 Dirección",
                key="delivery_direccion",
                placeholder="Dirección de entrega"
            )
        
        with col2:
            telefono = st.text_input(
                "📞 Teléfono",
                key="delivery_telefono",
                placeholder="Número de contacto"
            )
            
            observaciones = st.text_area(
                "📝 Observaciones",
                key="delivery_observaciones",
                placeholder="Notas adicionales (opcional)"
            )
        
        # Selección de productos
        st.markdown("---")
        st.subheader("🛒 Productos a Entregar")
        
        # Crear lista de productos disponibles
        productos_disponibles = []
        for categoria, productos in inventario.items():
            for producto in productos.keys():
                productos_disponibles.append(f"{categoria}: {producto}")
        
        # Multiselect para productos
        productos_seleccionados = st.multiselect(
            "Seleccionar productos",
            productos_disponibles,
            key="delivery_productos_selected"
        )
        
        # Detalles de cada producto seleccionado
        productos_entrega = []
        if productos_seleccionados:
            st.markdown("**Cantidades por producto:**")
            
            for producto_completo in productos_seleccionados:
                categoria, producto = producto_completo.split(": ", 1)
                
                col1, col2, col3 = st.columns([3, 2, 2])
                
                with col1:
                    st.write(f"**{producto}** ({categoria})")
                
                with col2:
                    # Determinar tipo de input según categoría
                    if categoria == "Por Kilos":
                        cantidad = st.number_input(
                            f"Cantidad (kg)",
                            min_value=0.0,
                            step=0.1,
                            key=f"delivery_qty_{categoria}_{producto}",
                            format="%.1f"
                        )
                        unidad = "kg"
                    else:
                        cantidad = st.number_input(
                            f"Cantidad (unidades)",
                            min_value=0,
                            key=f"delivery_qty_{categoria}_{producto}"
                        )
                        unidad = "unidades"
                
                with col3:
                    precio_unitario = st.number_input(
                        f"Precio unitario ($)",
                        min_value=0.0,
                        step=0.01,
                        key=f"delivery_price_{categoria}_{producto}",
                        format="%.2f"
                    )
                
                if cantidad > 0:
                    productos_entrega.append({
                        "categoria": categoria,
                        "producto": producto,
                        "cantidad": cantidad,
                        "unidad": unidad,
                        "precio_unitario": precio_unitario,
                        "subtotal": cantidad * precio_unitario
                    })
        
        # Mostrar resumen si hay productos
        if productos_entrega:
            st.markdown("---")
            st.subheader("💰 Resumen del Pedido")
            
            total = 0
            for item in productos_entrega:
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(f"{item['producto']} ({item['categoria']})")
                
                with col2:
                    st.write(f"{item['cantidad']} {item['unidad']}")
                
                with col3:
                    st.write(f"${item['precio_unitario']:.2f}")
                
                with col4:
                    st.write(f"${item['subtotal']:.2f}")
                
                total += item['subtotal']
            
            st.markdown(f"**Total: ${total:.2f}**")
        
        # Botón para guardar entrega
        st.markdown("---")
        
        if st.button("💾 Registrar Entrega", type="primary"):
            if self._validate_delivery_form(cliente, direccion, productos_entrega):
                if self._save_delivery(usuario, cliente, direccion, telefono, 
                                     observaciones, productos_entrega):
                    NotificationManager.success("Entrega registrada exitosamente")
                    # Limpiar formulario
                    self._clear_delivery_form()
                    st.rerun()
                else:
                    NotificationManager.error("Error al registrar la entrega")
            else:
                NotificationManager.warning("Por favor complete todos los campos obligatorios")
    
    def _render_today_deliveries(self, usuario: str):
        """Renderiza entregas del día actual"""
        st.subheader("📅 Entregas de Hoy")
        
        # Cargar entregas del día
        deliveries = self._load_today_deliveries(usuario)
        
        if not deliveries:
            st.info("No hay entregas registradas hoy")
            return
        
        # Mostrar entregas
        for i, delivery in enumerate(deliveries):
            with st.expander(
                f"🚚 Entrega #{i+1} - {delivery['cliente']} (${delivery['total']:.2f})"
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Cliente:** {delivery['cliente']}")
                    st.write(f"**Dirección:** {delivery['direccion']}")
                    st.write(f"**Teléfono:** {delivery.get('telefono', 'N/A')}")
                
                with col2:
                    st.write(f"**Fecha:** {delivery['fecha']}")
                    st.write(f"**Hora:** {delivery['hora']}")
                    st.write(f"**Total:** ${delivery['total']:.2f}")
                
                if delivery.get('observaciones'):
                    st.write(f"**Observaciones:** {delivery['observaciones']}")
                
                # Productos
                st.markdown("**Productos:**")
                for producto in delivery['productos']:
                    st.write(
                        f"• {producto['producto']} ({producto['categoria']}): "
                        f"{producto['cantidad']} {producto['unidad']} - "
                        f"${producto['subtotal']:.2f}"
                    )
    
    def _render_delivery_summary(self, usuario: str):
        """Renderiza resumen de entregas"""
        st.subheader("📊 Resumen de Entregas")
        
        # Filtros de fecha
        start_date, end_date = FilterPanel.render_date_range("delivery_summary")
        
        # Cargar entregas del período
        deliveries = self._load_deliveries_period(usuario, start_date, end_date)
        
        if not deliveries:
            st.info(f"No hay entregas en el período seleccionado")
            return
        
        # Métricas generales
        total_entregas = len(deliveries)
        total_ventas = sum(d['total'] for d in deliveries)
        productos_vendidos = sum(len(d['productos']) for d in deliveries)
        
        MetricCards.render_user_metrics(
            total_entregas, 
            productos_vendidos,
            deliveries[-1]['fecha'] if deliveries else None
        )
        
        # Gráfico por día (si hay suficientes datos)
        if len(deliveries) > 1:
            self._render_delivery_chart(deliveries)
        
        # Lista detallada
        st.markdown("---")
        st.subheader("📋 Lista Detallada")
        
        for delivery in reversed(deliveries):  # Más recientes primero
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            with col1:
                st.write(f"**{delivery['cliente']}**")
            
            with col2:
                st.write(delivery['fecha'])
            
            with col3:
                st.write(f"{len(delivery['productos'])} items")
            
            with col4:
                st.write(f"${delivery['total']:.2f}")
    
    def _render_delivery_chart(self, deliveries: List[Dict[str, Any]]):
        """Renderiza gráfico de entregas por día"""
        try:
            import pandas as pd
            
            # Preparar datos
            df = pd.DataFrame(deliveries)
            df['fecha'] = pd.to_datetime(df['fecha'])
            
            # Agrupar por día
            daily_summary = df.groupby(df['fecha'].dt.date).agg({
                'total': 'sum',
                'cliente': 'count'
            }).rename(columns={'cliente': 'entregas'})
            
            # Mostrar gráfico
            st.line_chart(daily_summary)
            
        except ImportError:
            st.warning("Pandas no disponible para gráficos")
    
    def _validate_delivery_form(self, cliente: str, direccion: str, 
                               productos: List[Dict[str, Any]]) -> bool:
        """Valida formulario de entrega"""
        return bool(cliente and direccion and productos)
    
    def _save_delivery(self, usuario: str, cliente: str, direccion: str,
                      telefono: str, observaciones: str, 
                      productos: List[Dict[str, Any]]) -> bool:
        """Guarda entrega en historial"""
        try:
            # Crear registro de entrega
            delivery_record = DeliveryRecord(
                fecha=date.today(),
                hora=datetime.now().strftime("%H:%M:%S"),
                usuario=usuario,
                cliente=cliente,
                direccion=direccion,
                telefono=telefono,
                observaciones=observaciones,
                productos=productos,
                total=sum(p['subtotal'] for p in productos)
            )
            
            # Guardar en historial
            return self._history.add_delivery_record(delivery_record)
            
        except Exception as e:
            st.error(f"Error al guardar entrega: {str(e)}")
            return False
    
    def _clear_delivery_form(self):
        """Limpia formulario de entrega"""
        keys_to_clear = [
            "delivery_cliente", "delivery_direccion", "delivery_telefono",
            "delivery_observaciones", "delivery_productos_selected"
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    def _load_today_deliveries(self, usuario: str) -> List[Dict[str, Any]]:
        """Carga entregas del día actual"""
        return self._history.get_user_deliveries(usuario, date.today())
    
    def _load_deliveries_period(self, usuario: str, start_date: date, 
                               end_date: date) -> List[Dict[str, Any]]:
        """Carga entregas de un período específico"""
        return self._history.get_user_deliveries_period(usuario, start_date, end_date)