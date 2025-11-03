"""
Modelo de mantenimientos preventivos y correctivos.

Incluye programación, seguimiento y documentación de mantenimientos.
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db, MantenimientoStatus
import enum


class MaintenanceType(enum.Enum):
    """Tipos de mantenimiento."""
    PREVENTIVO = "preventivo"
    CORRECTIVO = "correctivo"
    PREDICTIVO = "predictivo"
    URGENTE = "urgente"
    RUTINARIO = "rutinario"


class MaintenancePriority(enum.Enum):
    """Prioridades de mantenimiento."""
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class WorkOrderStatus(enum.Enum):
    """Estados de órdenes de trabajo."""
    PENDIENTE = "pendiente"
    ASIGNADO = "asignado"
    EN_PROCESO = "en_proceso"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"
    REPROGRAMADO = "reprogramado"


class MaintenanceCategory(enum.Enum):
    """Categorías de mantenimiento."""
    INSPECCION = "inspeccion"
    LIMPIEZA = "limpieza"
    CALIBRACION = "calibracion"
    ACTUALIZACION = "actualizacion"
    REPARACION = "reparacion"
    REEMPLAZO = "reemplazo"
    PRUEBAS = "pruebas"
    DOCUMENTACION = "documentacion"


class Mantenimiento(BaseModel, db.Model):
    """
    Modelo de mantenimientos para equipos e infraestructura.
    
    Attributes:
        title (str): Título del mantenimiento
        description (str): Descripción detallada
        maintenance_type (str): Tipo de mantenimiento
        category (str): Categoría del mantenimiento
        priority (str): Prioridad del mantenimiento
        status (str): Estado actual del mantenimiento
        equipment_id (int): ID del equipo a mantener
        equipment_type (str): Tipo de equipo
        camara_id (int): ID de la cámara relacionada
        nvr_id (int): ID del NVR relacionado
        switch_id (int): ID del switch relacionado
        ups_id (int): ID del UPS relacionado
        fuente_poder_id (int): ID de la fuente de poder relacionada
        gabinete_id (int): ID del gabinete relacionado
        ubicacion_id (int): ID de la ubicación donde se realiza
        falla_id (int): ID de la falla que origina el mantenimiento
        scheduled_start (datetime): Fecha programada de inicio
        scheduled_end (datetime): Fecha programada de fin
        actual_start (datetime): Fecha real de inicio
        actual_end (datetime): Fecha real de fin
        duration_estimated (int): Duración estimada en horas
        duration_actual (int): Duración real en horas
        technician_id (int): ID del técnico asignado
        supervisor_id (int): ID del supervisor
        required_skills (str): Habilidades requeridas (JSON)
        tools_required (str): Herramientas necesarias (JSON)
        spare_parts (str): Repuestos necesarios (JSON)
        safety_requirements (str): Requisitos de seguridad (JSON)
        work_instructions (str): Instrucciones de trabajo
        checklist_items (str): Ítems de verificación en JSON
        completion_criteria (str): Criterios de finalización
        maintenance_cost (float): Costo del mantenimiento
        parts_cost (float): Costo de repuestos
        labor_cost (float): Costo de mano de obra
        external_cost (float): Costo de servicios externos
        total_cost (float): Costo total
        downtime_minutes (int): Minutos de tiempo de inactividad
        recurrence_interval (int): Intervalo de recurrencia en días
        is_recurring (bool): Si es mantenimiento recurrente
        recurrence_pattern (str): Patrón de recurrencia
        next_maintenance_date (datetime): Fecha del próximo mantenimiento
        maintenance_window (str): Ventana de mantenimiento permitida
        customer_notification (bool): Si requiere notificación al cliente
        notification_sent (bool): Si ya se envió la notificación
        emergency_contact (str): Contacto de emergencia
        work_order_number (str): Número de orden de trabajo
        approval_required (bool): Si requiere aprobación
        approved_by (int): ID de quien aprueba
        approval_date (datetime): Fecha de aprobación
        follow_up_required (bool): Si requiere seguimiento
        follow_up_date (datetime): Fecha de seguimiento
        documentation_completed (bool): Si se completó la documentación
        quality_check_passed (bool): Si pasó el control de calidad
        warranty_impact (bool): Si afecta la garantía
        firmware_updated (bool): Si se actualizó firmware
        configuration_backed_up (bool): Si se respaldó configuración
        test_results (str): Resultados de pruebas en JSON
        issues_found (str): Problemas encontrados
        recommendations (str): Recomendaciones
        lessons_learned (str): Lecciones aprendidas
        maintenance_notes (str): Notas del mantenimiento
        completion_notes (str): Notas de finalización
    """
    
    __tablename__ = 'mantenimientos'
    
    # Información básica
    title = Column(String(200), nullable=False, index=True,
                  comment="Título descriptivo del mantenimiento")
    description = Column(Text, nullable=False,
                        comment="Descripción detallada del mantenimiento")
    maintenance_type = Column(Enum(MaintenanceType), nullable=False,
                             comment="Tipo de mantenimiento")
    category = Column(Enum(MaintenanceCategory), nullable=False,
                     comment="Categoría del mantenimiento")
    priority = Column(Enum(MaintenancePriority), nullable=False,
                     comment="Prioridad del mantenimiento")
    status = Column(String(20), nullable=False, default=MantenimientoStatus.PROGRAMADO,
                   comment="Estado actual del mantenimiento")
    
    # Relaciones con equipos
    equipment_id = Column(Integer, nullable=True,
                         comment="ID del equipo a mantener")
    equipment_type = Column(String(30), nullable=True,
                           comment="Tipo de equipo")
    camara_id = Column(Integer, ForeignKey('camaras.id'), nullable=True,
                      comment="ID de la cámara relacionada")
    nvr_id = Column(Integer, ForeignKey('nvrs.id'), nullable=True,
                   comment="ID del NVR relacionado")
    switch_id = Column(Integer, ForeignKey('switches.id'), nullable=True,
                      comment="ID del switch relacionado")
    ups_id = Column(Integer, ForeignKey('ups.id'), nullable=True,
                   comment="ID del UPS relacionado")
    fuente_poder_id = Column(Integer, ForeignKey('fuentes_poder.id'), nullable=True,
                            comment="ID de la fuente de poder relacionada")
    gabinete_id = Column(Integer, ForeignKey('gabinetes.id'), nullable=True,
                        comment="ID del gabinete relacionado")
    ubicacion_id = Column(Integer, ForeignKey('ubicaciones.id'), nullable=True,
                         comment="ID de la ubicación donde se realiza")
    falla_id = Column(Integer, ForeignKey('fallas.id'), nullable=True,
                     comment="ID de la falla que origina el mantenimiento")
    
    # Programación
    scheduled_start = Column(DateTime, nullable=True,
                            comment="Fecha y hora programada de inicio")
    scheduled_end = Column(DateTime, nullable=True,
                          comment="Fecha y hora programada de fin")
    actual_start = Column(DateTime, nullable=True,
                         comment="Fecha y hora real de inicio")
    actual_end = Column(DateTime, nullable=True,
                       comment="Fecha y hora real de fin")
    duration_estimated = Column(Integer, nullable=True,
                               comment="Duración estimada en horas")
    duration_actual = Column(Integer, nullable=True,
                            comment="Duración real en horas")
    
    # Asignación
    technician_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True,
                          comment="ID del técnico asignado")
    supervisor_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True,
                          comment="ID del supervisor")
    
    # Requisitos
    required_skills = Column(Text, nullable=True,
                            comment="Habilidades requeridas en formato JSON")
    tools_required = Column(Text, nullable=True,
                           comment="Herramientas necesarias en formato JSON")
    spare_parts = Column(Text, nullable=True,
                        comment="Repuestos necesarios en formato JSON")
    safety_requirements = Column(Text, nullable=True,
                                comment="Requisitos de seguridad en formato JSON")
    
    # Documentación
    work_instructions = Column(Text, nullable=True,
                              comment="Instrucciones detalladas de trabajo")
    checklist_items = Column(Text, nullable=True,
                            comment="Ítems de verificación en formato JSON")
    completion_criteria = Column(Text, nullable=True,
                                comment="Criterios de finalización")
    
    # Costos
    maintenance_cost = Column(Float, default=0.0, nullable=False,
                             comment="Costo del mantenimiento")
    parts_cost = Column(Float, default=0.0, nullable=False,
                       comment="Costo de repuestos")
    labor_cost = Column(Float, default=0.0, nullable=False,
                       comment="Costo de mano de obra")
    external_cost = Column(Float, default=0.0, nullable=False,
                          comment="Costo de servicios externos")
    total_cost = Column(Float, default=0.0, nullable=False,
                       comment="Costo total del mantenimiento")
    downtime_minutes = Column(Integer, default=0, nullable=False,
                             comment="Minutos de tiempo de inactividad")
    
    # Recurrencia
    recurrence_interval = Column(Integer, nullable=True,
                                comment="Intervalo de recurrencia en días")
    is_recurring = Column(Boolean, default=False, nullable=False,
                         comment="Si es mantenimiento recurrente")
    recurrence_pattern = Column(String(50), nullable=True,
                               comment="Patrón de recurrencia")
    next_maintenance_date = Column(DateTime, nullable=True,
                                  comment="Fecha del próximo mantenimiento")
    
    # Ventanas de tiempo
    maintenance_window = Column(String(100), nullable=True,
                               comment="Ventana de mantenimiento permitida")
    
    # Notificaciones
    customer_notification = Column(Boolean, default=False, nullable=False,
                                  comment="Si requiere notificación al cliente")
    notification_sent = Column(Boolean, default=False, nullable=False,
                              comment="Si ya se envió la notificación")
    emergency_contact = Column(String(100), nullable=True,
                              comment="Contacto de emergencia")
    
    # Órdenes de trabajo
    work_order_number = Column(String(50), nullable=True, unique=True,
                              comment="Número de orden de trabajo")
    approval_required = Column(Boolean, default=False, nullable=False,
                              comment="Si requiere aprobación antes de ejecutar")
    approved_by = Column(Integer, ForeignKey('usuarios.id'), nullable=True,
                        comment="ID de quien aprueba el mantenimiento")
    approval_date = Column(DateTime, nullable=True,
                          comment="Fecha de aprobación")
    
    # Seguimiento
    follow_up_required = Column(Boolean, default=False, nullable=False,
                               comment="Si requiere seguimiento posterior")
    follow_up_date = Column(DateTime, nullable=True,
                           comment="Fecha de seguimiento")
    
    # Documentación y calidad
    documentation_completed = Column(Boolean, default=False, nullable=False,
                                    comment="Si se completó la documentación")
    quality_check_passed = Column(Boolean, default=False, nullable=False,
                                 comment="Si pasó el control de calidad")
    warranty_impact = Column(Boolean, default=False, nullable=False,
                            comment="Si el mantenimiento afecta la garantía")
    firmware_updated = Column(Boolean, default=False, nullable=False,
                             comment="Si se actualizó el firmware")
    configuration_backed_up = Column(Boolean, default=False, nullable=False,
                                    comment="Si se respaldó la configuración")
    
    # Resultados
    test_results = Column(Text, nullable=True,
                         comment="Resultados de pruebas en formato JSON")
    issues_found = Column(Text, nullable=True,
                         comment="Problemas encontrados")
    recommendations = Column(Text, nullable=True,
                            comment="Recomendaciones")
    lessons_learned = Column(Text, nullable=True,
                            comment="Lecciones aprendidas")
    
    # Notas
    maintenance_notes = Column(Text, nullable=True,
                              comment="Notas durante el mantenimiento")
    completion_notes = Column(Text, nullable=True,
                             comment="Notas de finalización")
    
    # Relaciones
    created_by_user = relationship("Usuario", foreign_keys=[created_by], back_populates="created_mantenimientos")
    
    # Relaciones de asignación
    technician = relationship("Usuario", foreign_keys=[technician_id])
    supervisor = relationship("Usuario", foreign_keys=[supervisor_id])
    approver = relationship("Usuario", foreign_keys=[approved_by])
    
    # Relaciones con otros modelos
    ubicacion = relationship("Ubicacion", back_populates="mantenimientos")
    camara = relationship("Camara", back_populates="mantenimientos")
    nvr = relationship("NVR", back_populates="mantenimientos")
    switch = relationship("Switch", back_populates="mantenimientos")
    ups = relationship("UPS", back_populates="mantenimientos")
    fuente_poder = relationship("FuentePoder", back_populates="mantenimientos")
    gabinete = relationship("Gabinete", back_populates="mantenimientos")
    falla = relationship("Falla", back_populates="mantenimientos")
    
    # Relaciones con fotografías
    fotografias = relationship("Fotografia", back_populates="mantenimiento", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Mantenimiento(title='{self.title}', status='{self.status}', type='{self.maintenance_type.value}')>"
    
    def get_duration_hours(self):
        """
        Calcula la duración real del mantenimiento en horas.
        
        Returns:
            float: Duración en horas o None
        """
        if not self.actual_start or not self.actual_end:
            return None
        
        duration = self.actual_end - self.actual_start
        return duration.total_seconds() / 3600
    
    def is_overdue(self):
        """
        Verifica si el mantenimiento está vencido.
        
        Returns:
            bool: True si está vencido
        """
        if self.status in [MantenimientoStatus.COMPLETADO, MantenimientoStatus.CANCELADO]:
            return False
        
        if not self.scheduled_start:
            return False
        
        return datetime.utcnow() > self.scheduled_start
    
    def get_delay_hours(self):
        """
        Calcula el retraso en horas del mantenimiento.
        
        Returns:
            float: Retraso en horas (negativo si está adelantado)
        """
        if not self.scheduled_start or not self.actual_start:
            return None
        
        delay = self.actual_start - self.scheduled_start
        return delay.total_seconds() / 3600
    
    def assign_technician(self, technician_id):
        """
        Asigna un técnico al mantenimiento.
        
        Args:
            technician_id (int): ID del técnico
            
        Returns:
            bool: True si se asignó exitosamente
        """
        self.technician_id = technician_id
        if self.status == MantenimientoStatus.PROGRAMADO:
            self.status = MantenimientoStatus.EN_PROCESO
        self.save()
        return True
    
    def start_maintenance(self):
        """
        Inicia el mantenimiento.
        
        Returns:
            bool: True si se inició exitosamente
        """
        if not self.technician_id:
            return False
        
        self.actual_start = datetime.utcnow()
        self.status = MantenimientoStatus.EN_PROCESO
        self.save()
        return True
    
    def complete_maintenance(self, completion_notes=None):
        """
        Completa el mantenimiento.
        
        Args:
            completion_notes (str): Notas de finalización
            
        Returns:
            bool: True si se completó exitosamente
        """
        self.actual_end = datetime.utcnow()
        self.duration_actual = int(self.get_duration_hours()) if self.get_duration_hours() else None
        self.status = MantenimientoStatus.COMPLETADO
        self.documentation_completed = True
        self.quality_check_passed = True
        
        if completion_notes:
            self.completion_notes = completion_notes
        
        # Programar siguiente mantenimiento si es recurrente
        if self.is_recurring and self.recurrence_interval:
            self.next_maintenance_date = self.scheduled_start + timedelta(days=self.recurrence_interval)
        
        self.save()
        return True
    
    def cancel_maintenance(self, reason=None):
        """
        Cancela el mantenimiento.
        
        Args:
            reason (str): Razón de cancelación
            
        Returns:
            bool: True si se canceló exitosamente
        """
        self.status = MantenimientoStatus.CANCELADO
        if reason:
            self.completion_notes = f"Cancelado: {reason}"
        self.save()
        return True
    
    def reschedule_maintenance(self, new_scheduled_start, new_scheduled_end=None):
        """
        Reprograma el mantenimiento.
        
        Args:
            new_scheduled_start (datetime): Nueva fecha de inicio
            new_scheduled_end (datetime): Nueva fecha de fin
            
        Returns:
            bool: True si se reprogramó exitosamente
        """
        self.scheduled_start = new_scheduled_start
        if new_scheduled_end:
            self.scheduled_end = new_scheduled_end
        elif self.duration_estimated:
            self.scheduled_end = new_scheduled_start + timedelta(hours=self.duration_estimated)
        
        self.status = MantenimientoStatus.PROGRAMADO
        self.save()
        return True
    
    def get_total_cost(self):
        """
        Calcula el costo total del mantenimiento.
        
        Returns:
            float: Costo total
        """
        total = self.maintenance_cost + self.parts_cost + self.labor_cost + self.external_cost
        self.total_cost = total
        self.save()
        return total
    
    def get_work_order_summary(self):
        """
        Obtiene un resumen de la orden de trabajo.
        
        Returns:
            dict: Resumen de la orden de trabajo
        """
        return {
            'work_order_number': self.work_order_number,
            'status': self.status,
            'priority': self.priority,
            'scheduled_start': self.scheduled_start.isoformat() if self.scheduled_start else None,
            'actual_start': self.actual_start.isoformat() if self.actual_start else None,
            'duration_estimated_hours': self.duration_estimated,
            'duration_actual_hours': self.get_duration_hours(),
            'technician': self.technician.full_name if self.technician else None,
            'equipment_type': self.equipment_type,
            'equipment_id': self.equipment_id,
            'location': self.ubicacion.name if self.ubicacion else None,
            'total_cost': self.total_cost,
            'is_overdue': self.is_overdue()
        }
    
    def get_maintenance_effectiveness_score(self):
        """
        Calcula un puntaje de efectividad del mantenimiento.
        
        Returns:
            int: Puntaje de efectividad (0-100)
        """
        score = 100
        
        # Penalizar por retrasos
        delay_hours = self.get_delay_hours()
        if delay_hours:
            if delay_hours > 24:
                score -= 30
            elif delay_hours > 4:
                score -= 15
            elif delay_hours > 1:
                score -= 10
        
        # Penalizar si tomó más tiempo del estimado
        if self.duration_actual and self.duration_estimated:
            time_overrun = (self.duration_actual - self.duration_estimated) / self.duration_estimated
            if time_overrun > 0.5:
                score -= 25
            elif time_overrun > 0.2:
                score -= 15
        
        # Penalizar por documentación incompleta
        if not self.documentation_completed:
            score -= 20
        
        # Penalizar por no pasar control de calidad
        if not self.quality_check_passed:
            score -= 30
        
        # Penalizar por tiempo de inactividad excesivo
        if self.downtime_minutes > 120:  # 2 horas
            score -= 20
        elif self.downtime_minutes > 60:  # 1 hora
            score -= 10
        
        return max(0, min(100, score))
    
    def requires_approval(self):
        """
        Verifica si el mantenimiento requiere aprobación.
        
        Returns:
            bool: True si requiere aprobación
        """
        return (self.approval_required or 
                self.maintenance_type == MaintenanceType.CRITICO or
                self.maintenance_cost > 1000)  # Costo alto requiere aprobación
    
    def approve_maintenance(self, approver_id, approval_notes=None):
        """
        Aprueba el mantenimiento.
        
        Args:
            approver_id (int): ID de quien aprueba
            approval_notes (str): Notas de aprobación
            
        Returns:
            bool: True si se aprobó exitosamente
        """
        self.approved_by = approver_id
        self.approval_date = datetime.utcnow()
        if approval_notes:
            self.maintenance_notes = f"Aprobado: {approval_notes}"
        self.save()
        return True
    
    def get_safety_compliance_score(self):
        """
        Calcula el cumplimiento de seguridad.
        
        Returns:
            int: Puntaje de seguridad (0-100)
        """
        score = 100
        
        # Verificar requisitos de seguridad
        if not self.safety_requirements:
            score -= 30
        else:
            # Verificar que se documentaron los requisitos
            # Esta es una implementación simplificada
            pass
        
        # Verificar herramientas requeridas
        if not self.tools_required:
            score -= 20
        
        # Verificar habilidades requeridas del técnico
        if self.technician and self.required_skills:
            # Verificar que el técnico tiene las habilidades
            # Implementación simplificada
            pass
        
        return max(0, min(100, score))
    
    @classmethod
    def get_scheduled_maintenances(cls, start_date, end_date):
        """
        Obtiene mantenimientos programados en un período.
        
        Args:
            start_date (datetime): Fecha de inicio
            end_date (datetime): Fecha de fin
            
        Returns:
            list: Lista de mantenimientos programados
        """
        return cls.query.filter(
            cls.scheduled_start >= start_date,
            cls.scheduled_start <= end_date,
            cls.status != MantenimientoStatus.CANCELADO,
            cls.deleted == False
        ).all()
    
    @classmethod
    def get_overdue_maintenances(cls):
        """
        Obtiene mantenimientos vencidos.
        
        Returns:
            list: Lista de mantenimientos vencidos
        """
        now = datetime.utcnow()
        return cls.query.filter(
            cls.scheduled_start < now,
            cls.status.in_([MantenimientoStatus.PROGRAMADO, MantenimientoStatus.EN_PROCESO]),
            cls.deleted == False
        ).all()
    
    @classmethod
    def get_by_equipment(cls, equipment_id, equipment_type):
        """
        Obtiene mantenimientos de un equipo específico.
        
        Args:
            equipment_id (int): ID del equipo
            equipment_type (str): Tipo del equipo
            
        Returns:
            list: Lista de mantenimientos del equipo
        """
        return cls.query.filter_by(
            equipment_id=equipment_id,
            equipment_type=equipment_type,
            deleted=False
        ).all()
    
    @classmethod
    def get_by_technician(cls, technician_id):
        """
        Obtiene mantenimientos asignados a un técnico.
        
        Args:
            technician_id (int): ID del técnico
            
        Returns:
            list: Lista de mantenimientos del técnico
        """
        return cls.query.filter_by(
            technician_id=technician_id,
            deleted=False
        ).all()
    
    @classmethod
    def get_recurring_maintenances(cls):
        """
        Obtiene todos los mantenimientos recurrentes.
        
        Returns:
            list: Lista de mantenimientos recurrentes
        """
        return cls.query.filter_by(
            is_recurring=True,
            deleted=False
        ).all()


class MantenimientoHistorial(BaseModel, db.Model):
    """
    Historial de cambios en mantenimientos.
    
    Attributes:
        mantenimiento_id (int): ID del mantenimiento
        action (str): Acción realizada
        old_status (str): Estado anterior
        new_status (str): Estado nuevo
        user_id (int): ID del usuario que realizó el cambio
        comments (str): Comentarios
        timestamp (datetime): Fecha y hora del cambio
        details (str): Detalles adicionales
    """
    
    __tablename__ = 'mantenimiento_historial'
    
    mantenimiento_id = Column(Integer, ForeignKey('mantenimientos.id'), nullable=False,
                             comment="ID del mantenimiento")
    action = Column(String(50), nullable=False,
                   comment="Acción realizada")
    old_status = Column(String(20), nullable=True,
                       comment="Estado anterior")
    new_status = Column(String(20), nullable=True,
                       comment="Estado nuevo")
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False,
                    comment="ID del usuario que realizó el cambio")
    comments = Column(Text, nullable=True,
                     comment="Comentarios del cambio")
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False,
                      comment="Fecha y hora del cambio")
    details = Column(Text, nullable=True,
                    comment="Detalles adicionales del cambio")
    
    # Relaciones
    user = relationship("Usuario")
    mantenimiento = relationship("Mantenimiento")
    
    def __repr__(self):
        return f"<MantenimientoHistorial(mantenimiento={self.mantenimiento_id}, action='{self.action}')>"