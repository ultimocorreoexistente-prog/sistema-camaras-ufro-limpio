"""
Modelo de fallas con historial y seguimiento.

Incluye gestión de fallas, seguimiento de estados y asignación de técnicos.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db, FallaStatus, EquipmentStatus
import enum


class FallaPriority(enum.Enum):
    """Niveles de prioridad de las fallas."""
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class FallaType(enum.Enum):
    """Tipos de fallas."""
    HARDWARE = "hardware"
    SOFTWARE = "software"
    CONECTIVIDAD = "conectividad"
    ALIMENTACION = "alimentacion"
    SISTEMA = "sistema"
    CONFIGURACION = "configuracion"


class Falla(BaseModel, db.Model):
    """
    Modelo de fallas del sistema.
    
    Attributes:
        title (str): Título descriptivo de la falla
        description (str): Descripción detallada
        falla_type (str): Tipo de falla
        priority (str): Prioridad de la falla
        status (str): Estado actual de la falla
        equipment_id (int): ID del equipo relacionado
        equipment_type (str): Tipo de equipo
        camara_id (int): ID de la cámara relacionada
        ubicacion_id (int): ID de la ubicación donde ocurrió
        assigned_to (int): ID del técnico asignado
        reported_by (int): ID de quien reportó
        assigned_date (datetime): Fecha de asignación
        start_date (datetime): Fecha de inicio de la falla
        resolution_date (datetime): Fecha de resolución
        estimated_resolution_time (int): Tiempo estimado de resolución en horas
        actual_resolution_time (int): Tiempo real de resolución en horas
        impact_assessment (str): Evaluación del impacto
        resolution_notes (str): Notas de resolución
        root_cause (str): Causa raíz de la falla
        prevention_measures (str): Medidas preventivas
        recurrence_risk (float): Riesgo de recurrencia (0-1)
        is_recurring (bool): Si es una falla recurrente
        related_falla_id (int): ID de falla relacionada
        external_ticket (str): Ticket externo del proveedor
        cost_impact (float): Impacto en costos
        downtime_hours (float): Horas de tiempo de inactividad
        affected_users (int): Número de usuarios afectados
        escalation_level (int): Nivel de escalamiento
        resolution_source (str): Fuente de la resolución
        verification_status (str): Estado de verificación
        client_notification (bool): Si se notificó al cliente
        contractor_involved (bool): Si se involucró un contratista
        notes (str): Notas adicionales
    """
    
    __tablename__ = 'fallas'
    
    # Información básica
    title = Column(String(200), nullable=False, index=True,
                  comment="Título descriptivo de la falla")
    description = Column(Text, nullable=False,
                        comment="Descripción detallada de la falla")
    falla_type = Column(Enum(FallaType), nullable=False,
                       comment="Tipo de falla")
    priority = Column(Enum(FallaPriority), nullable=False,
                     comment="Prioridad de la falla")
    status = Column(String(20), nullable=False, default=FallaStatus.ABIERTA,
                   comment="Estado actual de la falla")
    
    # Relaciones con otros modelos
    equipment_id = Column(Integer, nullable=True,
                         comment="ID del equipo donde ocurrió la falla")
    equipment_type = Column(String(30), nullable=True,
                           comment="Tipo de equipo (camara, nvr, switch, etc.)")
    camara_id = Column(Integer, ForeignKey('camaras.id'), nullable=True,
                      comment="ID de la cámara relacionada con la falla")
    ubicacion_id = Column(Integer, ForeignKey('ubicaciones.id'), nullable=True,
                         comment="ID de la ubicación donde ocurrió la falla")
    
    # Asignación y seguimiento
    assigned_to = Column(Integer, ForeignKey('usuarios.id'), nullable=True,
                        comment="ID del técnico asignado")
    reported_by = Column(Integer, ForeignKey('usuarios.id'), nullable=True,
                        comment="ID de quien reportó la falla")
    assigned_date = Column(DateTime, nullable=True,
                          comment="Fecha y hora de asignación")
    
    # Fechas de seguimiento
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False,
                       comment="Fecha y hora de inicio de la falla")
    resolution_date = Column(DateTime, nullable=True,
                            comment="Fecha y hora de resolución")
    
    # Tiempos estimados y reales
    estimated_resolution_time = Column(Integer, nullable=True,
                                      comment="Tiempo estimado de resolución en horas")
    actual_resolution_time = Column(Integer, nullable=True,
                                   comment="Tiempo real de resolución en horas")
    
    # Evaluación y resolución
    impact_assessment = Column(Text, nullable=True,
                              comment="Evaluación del impacto de la falla")
    resolution_notes = Column(Text, nullable=True,
                             comment="Notas de la solución aplicada")
    root_cause = Column(Text, nullable=True,
                       comment="Causa raíz de la falla")
    prevention_measures = Column(Text, nullable=True,
                                comment="Medidas preventivas recomendadas")
    
    # Análisis de recurrencia
    recurrence_risk = Column(Float, default=0.0, nullable=False,
                            comment="Riesgo de recurrencia (0.0 - 1.0)")
    is_recurring = Column(Boolean, default=False, nullable=False,
                         comment="Indica si es una falla recurrente")
    related_falla_id = Column(Integer, ForeignKey('fallas.id'), nullable=True,
                             comment="ID de falla relacionada")
    
    # Información externa
    external_ticket = Column(String(50), nullable=True,
                            comment="Número de ticket del proveedor externo")
    
    # Impacto y métricas
    cost_impact = Column(Float, default=0.0, nullable=False,
                        comment="Impacto económico de la falla")
    downtime_hours = Column(Float, default=0.0, nullable=False,
                           comment="Horas de tiempo de inactividad")
    affected_users = Column(Integer, default=0, nullable=False,
                           comment="Número de usuarios afectados")
    
    # Escalamiento y seguimiento
    escalation_level = Column(Integer, default=0, nullable=False,
                             comment="Nivel de escalamiento")
    resolution_source = Column(String(50), nullable=True,
                              comment="Fuente de la resolución")
    verification_status = Column(String(20), nullable=True,
                                comment="Estado de verificación de la solución")
    
    # Notificaciones
    client_notification = Column(Boolean, default=False, nullable=False,
                               comment="Si se notificó al cliente")
    contractor_involved = Column(Boolean, default=False, nullable=False,
                               comment="Si se involucró un contratista")
    
    # Metadatos
    notes = Column(Text, nullable=True,
                  comment="Notas adicionales")
    
    # Relaciones
    created_by_user = relationship("Usuario", foreign_keys=[created_by], back_populates="created_fallas")
    
    # Relaciones de asignación
    assigned_user = relationship("Usuario", foreign_keys=[assigned_to])
    reported_user = relationship("Usuario", foreign_keys=[reported_by])
    
    # Relaciones con otros modelos
    ubicacion = relationship("Ubicacion", back_populates="fallas")
    camara = relationship("Camara", back_populates="fallas")
    
    # Autorreferencia para fallas relacionadas
    related_falla = relationship("Falla", remote_side=[id], backref="related_fallas")
    
    # Relaciones con mantenimientos
    mantenimientos = relationship("Mantenimiento", back_populates="falla", cascade="all, delete-orphan")
    fotografias = relationship("Fotografia", back_populates="falla", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Falla(title='{self.title}', status='{self.status}')>"
    
    def get_duration_hours(self):
        """
        Calcula la duración de la falla en horas.
        
        Returns:
            float: Duración en horas
        """
        end_time = self.resolution_date or datetime.utcnow()
        duration = end_time - self.start_date
        return duration.total_seconds() / 3600
    
    def is_overdue(self):
        """
        Verifica si la falla está vencida según el tiempo estimado.
        
        Returns:
            bool: True si está vencida
        """
        if not self.estimated_resolution_time or self.status in [FallaStatus.RESUELTA, FallaStatus.CERRADA]:
            return False
        
        duration = self.get_duration_hours()
        return duration > self.estimated_resolution_time
    
    def get_age_in_hours(self):
        """
        Calcula la edad de la falla en horas.
        
        Returns:
            float: Edad en horas
        """
        duration = datetime.utcnow() - self.start_date
        return duration.total_seconds() / 3600
    
    def assign_to(self, user_id):
        """
        Asigna la falla a un técnico.
        
        Args:
            user_id (int): ID del técnico a asignar
        """
        self.assigned_to = user_id
        self.assigned_date = datetime.utcnow()
        
        if self.status == FallaStatus.ABIERTA:
            self.status = FallaStatus.EN_PROCESO
        
        self.save()
    
    def resolve(self, user_id, resolution_notes=None):
        """
        Marca la falla como resuelta.
        
        Args:
            user_id (int): ID del usuario que resuelve
            resolution_notes (str): Notas de resolución
        """
        self.status = FallaStatus.RESUELTA
        self.resolution_date = datetime.utcnow()
        self.actual_resolution_time = int(self.get_duration_hours())
        
        if resolution_notes:
            self.resolution_notes = resolution_notes
        
        self.save()
    
    def close(self, user_id):
        """
        Cierra la falla.
        
        Args:
            user_id (int): ID del usuario que cierra
        """
        self.status = FallaStatus.CERRADA
        self.save()
    
    def escalate(self, level=1):
        """
        Escalara la falla a un nivel superior.
        
        Args:
            level (int): Nivel de escalamiento
        """
        self.escalation_level += level
        self.save()
    
    def calculate_resolution_time_accuracy(self):
        """
        Calcula la precisión del tiempo estimado vs. real.
        
        Returns:
            float: Porcentaje de precisión (0-100)
        """
        if not self.estimated_resolution_time or not self.actual_resolution_time:
            return None
        
        difference = abs(self.estimated_resolution_time - self.actual_resolution_time)
        accuracy = max(0, 100 - (difference / self.estimated_resolution_time * 100))
        return round(accuracy, 2)
    
    def get_priority_color(self):
        """
        Obtiene el color para la prioridad.
        
        Returns:
            str: Código de color
        """
        colors = {
            FallaPriority.BAJA: "#28a745",     # Verde
            FallaPriority.MEDIA: "#ffc107",    # Amarillo
            FallaPriority.ALTA: "#fd7e14",     # Naranja
            FallaPriority.CRITICA: "#dc3545"   # Rojo
        }
        return colors.get(self.priority, "#6c757d")  # Gris por defecto
    
    @classmethod
    def get_active_fallas(cls):
        """
        Obtiene todas las fallas activas (abiertas o en proceso).
        
        Returns:
            list: Lista de fallas activas
        """
        return cls.query.filter(
            cls.status.in_([FallaStatus.ABIERTA, FallaStatus.EN_PROCESO]),
            cls.deleted == False
        ).all()
    
    @classmethod
    def get_overdue_fallas(cls):
        """
        Obtiene todas las fallas vencidas.
        
        Returns:
            list: Lista de fallas vencidas
        """
        from sqlalchemy import func
        
        # Esta consulta es simplificada, en producción se podría usar una subconsulta
        # para calcular la duración y compararla con el tiempo estimado
        fallas = cls.query.filter(
            cls.status.in_([FallaStatus.ABIERTA, FallaStatus.EN_PROCESO]),
            cls.estimated_resolution_time.isnot(None),
            cls.deleted == False
        ).all()
        
        overdue = []
        for falla in fallas:
            if falla.is_overdue():
                overdue.append(falla)
        
        return overdue
    
    @classmethod
    def get_by_equipment(cls, equipment_id, equipment_type):
        """
        Obtiene fallas de un equipo específico.
        
        Args:
            equipment_id (int): ID del equipo
            equipment_type (str): Tipo de equipo
            
        Returns:
            list: Lista de fallas del equipo
        """
        return cls.query.filter_by(
            equipment_id=equipment_id,
            equipment_type=equipment_type,
            deleted=False
        ).all()
    
    @classmethod
    def get_by_location(cls, location_id):
        """
        Obtiene fallas de una ubicación específica.
        
        Args:
            location_id (int): ID de la ubicación
            
        Returns:
            list: Lista de fallas en la ubicación
        """
        return cls.query.filter_by(ubicacion_id=location_id, deleted=False).all()
    
    @classmethod
    def get_by_technician(cls, technician_id):
        """
        Obtiene fallas asignadas a un técnico.
        
        Args:
            technician_id (int): ID del técnico
            
        Returns:
            list: Lista de fallas del técnico
        """
        return cls.query.filter_by(
            assigned_to=technician_id,
            deleted=False
        ).all()


class FallaHistorial(BaseModel, db.Model):
    """
    Historial de cambios en las fallas.
    
    Attributes:
        falla_id (int): ID de la falla
        action (str): Acción realizada
        old_status (str): Estado anterior
        new_status (str): Estado nuevo
        user_id (int): ID del usuario que realizó el cambio
        comments (str): Comentarios
        timestamp (datetime): Fecha y hora del cambio
    """
    
    __tablename__ = 'falla_historial'
    
    falla_id = Column(Integer, ForeignKey('fallas.id'), nullable=False,
                     comment="ID de la falla")
    action = Column(String(50), nullable=False,
                   comment="Acción realizada")
    old_status = Column(String(20), nullable=True,
                       comment="Estado anterior")
    new_status = Column(String(20), nullable=True,
                       comment="Estado nuevo")
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False,
                    comment="ID del usuario que realizó el cambio")
    comments = Column(Text, nullable=True,
                     comment="Comentarios adicionales")
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False,
                      comment="Fecha y hora del cambio")
    
    # Relaciones
    user = relationship("Usuario")
    falla = relationship("Falla")
    
    def __repr__(self):
        return f"<FallaHistorial(falla_id={self.falla_id}, action='{self.action}')>"