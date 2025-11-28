"""
Scheduler Automático para Sincronización de Inventario
Ejecuta sincronización periódica en background
"""
import threading
import time
from datetime import datetime, timedelta
from typing import Optional
import streamlit as st

class InventorySyncScheduler:
    """
    Scheduler que ejecuta sincronización automática del inventario
    en intervalos configurables
    """
    
    def __init__(self, sync_service, interval_minutes: int = 5):
        """
        Args:
            sync_service: Instancia de InventorySyncService
            interval_minutes: Intervalo de sincronización en minutos (default: 5)
        """
        self.sync_service = sync_service
        self.interval_minutes = interval_minutes
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.last_sync: Optional[datetime] = None
        self.next_sync: Optional[datetime] = None
        self.sync_count = 0
        self.error_count = 0
        self.last_error: Optional[str] = None
    
    def _sync_worker(self, tienda_id: str):
        """Worker que ejecuta la sincronización en background"""
        while self.is_running:
            try:
                # Ejecutar sincronización
                success, message = self.sync_service.force_sync(tienda_id)
                
                if success:
                    self.last_sync = datetime.now()
                    self.sync_count += 1
                    self.last_error = None
                else:
                    self.error_count += 1
                    self.last_error = message
                
                # Calcular próxima sincronización
                self.next_sync = datetime.now() + timedelta(minutes=self.interval_minutes)
                
                # Esperar el intervalo
                time.sleep(self.interval_minutes * 60)
                
            except Exception as e:
                self.error_count += 1
                self.last_error = str(e)
                # En caso de error, esperar antes de reintentar
                time.sleep(30)  # 30 segundos
    
    def start(self, tienda_id: str = "T001"):
        """Inicia el scheduler de sincronización"""
        if self.is_running:
            return False, "⚠️ El scheduler ya está en ejecución"
        
        try:
            self.is_running = True
            self.thread = threading.Thread(
                target=self._sync_worker,
                args=(tienda_id,),
                daemon=True  # Thread daemon para que se cierre con la app
            )
            self.thread.start()
            self.next_sync = datetime.now() + timedelta(minutes=self.interval_minutes)
            
            return True, f"✅ Scheduler iniciado (sincronización cada {self.interval_minutes} min)"
        except Exception as e:
            self.is_running = False
            return False, f"❌ Error iniciando scheduler: {str(e)}"
    
    def stop(self):
        """Detiene el scheduler"""
        if not self.is_running:
            return False, "⚠️ El scheduler no está en ejecución"
        
        self.is_running = False
        if self.thread:
            # Esperar a que termine el thread (máximo 5 segundos)
            self.thread.join(timeout=5)
        
        return True, "✅ Scheduler detenido"
    
    def get_status(self) -> dict:
        """Obtiene el estado actual del scheduler"""
        return {
            "is_running": self.is_running,
            "interval_minutes": self.interval_minutes,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "next_sync": self.next_sync.isoformat() if self.next_sync else None,
            "sync_count": self.sync_count,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "time_to_next_sync": self._time_to_next_sync()
        }
    
    def _time_to_next_sync(self) -> Optional[str]:
        """Calcula tiempo restante hasta la próxima sincronización"""
        if not self.next_sync or not self.is_running:
            return None
        
        delta = self.next_sync - datetime.now()
        if delta.total_seconds() < 0:
            return "Sincronizando ahora..."
        
        minutes = int(delta.total_seconds() / 60)
        seconds = int(delta.total_seconds() % 60)
        
        return f"{minutes}m {seconds}s"
    
    def set_interval(self, minutes: int):
        """Cambia el intervalo de sincronización (requiere reinicio)"""
        was_running = self.is_running
        tienda_id = None
        
        if was_running:
            # Guardar tienda actual antes de detener
            # (en una implementación real, guardarías esto en session_state)
            self.stop()
        
        self.interval_minutes = minutes
        
        if was_running and tienda_id:
            self.start(tienda_id)
        
        return True, f"✅ Intervalo actualizado a {minutes} minutos"


class InventorySyncUI:
    """Componente UI para control del scheduler"""
    
    def __init__(self, scheduler: InventorySyncScheduler):
        self.scheduler = scheduler
    
    def render_status_widget(self):
        """Renderiza widget de estado del scheduler"""
        status = self.scheduler.get_status()
        
        st.markdown("### 🔄 Sincronización Automática")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if status["is_running"]:
                st.success("🟢 Activo")
            else:
                st.error("🔴 Inactivo")
        
        with col2:
            st.metric(
                "Intervalo",
                f"{status['interval_minutes']} min"
            )
        
        with col3:
            if status["time_to_next_sync"]:
                st.metric(
                    "Próxima Sync",
                    status["time_to_next_sync"]
                )
            else:
                st.metric("Próxima Sync", "N/A")
        
        # Estadísticas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("✅ Sincronizaciones", status["sync_count"])
        
        with col2:
            st.metric("❌ Errores", status["error_count"])
        
        with col3:
            if status["last_sync"]:
                last_sync_dt = datetime.fromisoformat(status["last_sync"])
                ago = datetime.now() - last_sync_dt
                minutes_ago = int(ago.total_seconds() / 60)
                st.metric("Última Sync", f"Hace {minutes_ago}m")
            else:
                st.metric("Última Sync", "Nunca")
        
        # Mostrar errores si existen
        if status["last_error"]:
            st.error(f"**Último error:** {status['last_error']}")
    
    def render_controls(self, tienda_id: str = "T001"):
        """Renderiza controles de inicio/parada"""
        status = self.scheduler.get_status()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if not status["is_running"]:
                if st.button("▶️ Iniciar Auto-Sync", use_container_width=True):
                    success, message = self.scheduler.start(tienda_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                if st.button("⏹️ Detener Auto-Sync", use_container_width=True):
                    success, message = self.scheduler.stop()
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        
        with col2:
            # Selector de intervalo
            new_interval = st.selectbox(
                "Intervalo de sincronización",
                options=[1, 2, 5, 10, 15, 30, 60],
                index=2,  # Default 5 minutos
                format_func=lambda x: f"{x} minuto{'s' if x > 1 else ''}",
                key="sync_interval_selector"
            )
            
            if new_interval != status["interval_minutes"]:
                if st.button("💾 Actualizar Intervalo", use_container_width=True):
                    success, message = self.scheduler.set_interval(new_interval)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        
        with col3:
            st.info("""
            **Auto-Sync:**
            Mantiene el inventario
            sincronizado en tiempo real
            """)
