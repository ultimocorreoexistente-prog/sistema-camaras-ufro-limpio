"""
Modelo de mantenimientos preventivos y correctivos.
Gestiona el ciclo de vida de mantenimientos para equipos del sistema.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from models.base import TimestampedModel
from models import db
import enum

# Enums de tipos de mantenimiento
class MaintenanceType(enum.Enum):
    """Tipos de mantenimiento."""
    PREVENTIVO = "preventivo"
    CORRECTIVO = "correctivo"
    PREDICTIVO = "predictivo"
    MEJORA = "mejora"


class MaintenanceStatus(enum.Enum):
    """Estados de mantenimiento."""
    PROGRAMADO = "programado"
    EN_PROGRESO = "en_progreso"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"
    RETRASADO = "retrasado"


class MaintenancePriority(enum.Enum):
    """Prioridades de mantenimiento."""
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"

class Mantenimiento(db.Model, TimestampedModel):
    """
    Modelo de mantenimientos.

    Attributes:
        codigo (str): Código único de mantenimiento
        titulo (str): Título descriptivo
        descripcion (str): Descripción detallada
        tipo (str): Tipo de mantenimiento
        equipo_tipo (str): Tipo de equipo al que se aplica
        equipo_id (int): ID del equipo
        fecha_programada (datetime): Fecha programada
        fecha_inicio (datetime): Fecha de inicio real
        fecha_fin (datetime): Fecha de finalización
        estado (str): Estado actual
        prioridad (str): Nivel de prioridad
        responsable (str): Persona responsable
        costo (float): Costo estimado/real
        observaciones (str): Notas adicionales
    """

    __tablename__ = 'mantenimientos'

    # Primary key
    id = Column(Integer, primary_key=True)
    
    # Campos básicos
    codigo = Column(String(50), unique=True, index=True, nullable=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=False)
    tipo = Column(Enum(MaintenanceType), default=MaintenanceType.PREVENTIVO, nullable=False)
    equipo_tipo = Column(String(50), nullable=True)
    equipo_id = Column(Integer, nullable=True)
    
    # Fechas
    fecha_programada = Column(DateTime, nullable=True)
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Estados y prioridades
    estado = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.PROGRAMADO, nullable=False)
    prioridad = Column(Enum(MaintenancePriority), default=MaintenancePriority.MEDIA)
    
    # Información de responsable
    responsable = Column(String(100), nullable=True)
    technician_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    supervisor_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    created_by = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    
    # Costos
    costo = Column(Float, default=0)
    maintenance_cost = Column(Float, default=0.0, nullable=False)
    parts_cost = Column(Float, default=0.0, nullable=False)
    labor_cost = Column(Float, default=0.0, nullable=False)
    external_cost = Column(Float, default=0.0, nullable=False)
    total_cost = Column(Float, default=0.0, nullable=False)
    
    # Tiempo y recurrencia
    downtime_minutes = Column(Integer, default=0, nullable=False)
    duration_estimated = Column(Integer, nullable=True)
    duration_actual = Column(Integer, nullable=True)
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_interval = Column(Integer, nullable=True)
    recurrence_pattern = Column(String(50), nullable=True)
    next_maintenance_date = Column(DateTime, nullable=True)
    
    # Notas y documentación
    observaciones = Column(Text, nullable=True)
    maintenance_notes = Column(Text, nullable=True)
    completion_notes = Column(Text, nullable=True)
    
    # Aprobaciones
    work_order_number = Column(String(50), nullable=True, unique=True)
    approval_required = Column(Boolean, default=False, nullable=False)
    approved_by = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    
    # Seguimiento
    follow_up_required = Column(Boolean, default=False, nullable=False)
    follow_up_date = Column(DateTime, nullable=True)
    customer_notification = Column(Boolean, default=False, nullable=False)
    emergency_contact = Column(String(100), nullable=True)
    
    # Control de calidad
    documentation_completed = Column(Boolean, default=False, nullable=False)
    quality_check_passed = Column(Boolean, default=False, nullable=False)
    warranty_impact = Column(Boolean, default=False, nullable=False)
    firmware_updated = Column(Boolean, default=False, nullable=False)
    configuration_backed_up = Column(Boolean, default=False, nullable=False)

    # Relaciones
    created_by_user = relationship("Usuario", foreign_keys=[created_by], back_populates="created_mantenimientos")
    technician = relationship("Usuario", foreign_keys=[technician_id])
    supervisor = relationship("Usuario", foreign_keys=[supervisor_id])
    approver = relationship("Usuario", foreign_keys=[approved_by])
    
    # Relaciones con equipos (compatibilidad)
    ubicacion = relationship("Ubicacion", back_populates="mantenimientos")
    camara = relationship("Camara", back_populates="mantenimientos")
    nvr = relationship("NVR", back_populates="mantenimientos")
    switch = relationship("Switch", back_populates="mantenimientos")
    ups = relationship("UPS", back_populates="mantenimientos")
    fuente_poder = relationship("FuentePoder", back_populates="mantenimientos")
    gabinete = relationship("Gabinete", back_populates="mantenimientos")
    falla = relationship("Falla", back_populates="mantenimientos")
    
    # Relaciones adicionales
    fallas = relationship("Falla", back_populates="mantenimiento")
    fotografias = relationship("Fotografia", back_populates="mantenimiento", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Mantenimiento(titulo='{self.titulo}', estado='{self.estado}', tipo='{self.tipo}')>"

    def duracion_estimada(self):
        """Calcula la duración estimada en horas."""
        if self.fecha_programada and self.fecha_fin:
            return (self.fecha_fin - self.fecha_programada).total_seconds() / 3600
        return 0

    def esta_atrasado(self):
        """Verifica si el mantenimiento está atrasado."""
        return self.estado != MaintenanceStatus.COMPLETADO and \
               self.fecha_programada and datetime.utcnow() > self.fecha_programada

    def porcentaje_completado(self):
        """Calcula el porcentaje de completado."""
        if self.estado == MaintenanceStatus.COMPLETADO:
            return 100
        elif self.estado == MaintenanceStatus.EN_PROGRESO:
            return 50
        else:
            return 0
    
    def calcular_costo_total(self):
        """Calcula el costo total sumando todas las partes."""
        return self.maintenance_cost + self.parts_cost + self.labor_cost + self.external_cost
    
    def marcar_completado(self):
        """Marca el mantenimiento como completado."""
        self.estado = MaintenanceStatus.COMPLETADO
        self.fecha_fin = datetime.utcnow()
        if self.fecha_inicio:
            self.duration_actual = int((self.fecha_fin - self.fecha_inicio).total_seconds() / 60)
