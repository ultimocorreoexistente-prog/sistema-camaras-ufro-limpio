<<<<<<< HEAD
# models/mantenimiento.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db
=======
"""
Modelo de mantenimientos preventivos y correctivos.
Gestiona el ciclo de vida de mantenimientos para equipos del sistema.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db
import enum
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4

# Enums locales (sin imports problemáticos)
class MaintenanceType:
PREVENTIVO = "preventivo"
CORRECTIVO = "correctivo"
PREDICTIVO = "predictivo"
URGENTE = "urgente"
RUTINARIO = "rutinario"

<<<<<<< HEAD
class MaintenancePriority:
BAJA = "baja"
MEDIA = "media"
ALTA = "alta"
CRITICA = "critica"
=======
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
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4

class MaintenanceCategory:
INSPECCION = "inspeccion"
LIMPIEZA = "limpieza"
CALIBRACION = "calibracion"
ACTUALIZACION = "actualizacion"
REPARACION = "reparacion"
REEMPLAZO = "reemplazo"
PRUEBAS = "pruebas"
DOCUMENTACION = "documentacion"

class Mantenimiento(BaseModel, db.Model):
<<<<<<< HEAD
__tablename__ = 'mantenimientos'

title = Column(String(00), nullable=False, index=True)
description = Column(Text, nullable=False)
maintenance_type = Column(String(0), nullable=False)
category = Column(String(0), nullable=False)
priority = Column(String(0), nullable=False)
status = Column(String(0), nullable=False, default="programado")

equipment_id = Column(Integer, nullable=True)
equipment_type = Column(String(30), nullable=True)

# CORREGIDO: usar nombres reales de tablas
camara_id = Column(Integer, ForeignKey('camaras.id'), nullable=True)
nvr_id = Column(Integer, ForeignKey('nvr_dvr.id'), nullable=True) # nvr_dvr.id
switch_id = Column(Integer, ForeignKey('switches.id'), nullable=True)
ups_id = Column(Integer, ForeignKey('ups.id'), nullable=True)
fuente_poder_id = Column(Integer, ForeignKey('fuente_poder.id'), nullable=True) # fuente_poder.id
gabinete_id = Column(Integer, ForeignKey('gabinetes.id'), nullable=True)
ubicacion_id = Column(Integer, ForeignKey('ubicaciones.id'), nullable=True)
falla_id = Column(Integer, ForeignKey('fallas.id'), nullable=True)

scheduled_start = Column(DateTime, nullable=True)
scheduled_end = Column(DateTime, nullable=True)
actual_start = Column(DateTime, nullable=True)
actual_end = Column(DateTime, nullable=True)
duration_estimated = Column(Integer, nullable=True)
duration_actual = Column(Integer, nullable=True)

technician_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
supervisor_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
created_by = Column(Integer, ForeignKey('usuarios.id'), nullable=True)

maintenance_cost = Column(Float, default=0.0, nullable=False)
parts_cost = Column(Float, default=0.0, nullable=False)
labor_cost = Column(Float, default=0.0, nullable=False)
external_cost = Column(Float, default=0.0, nullable=False)
total_cost = Column(Float, default=0.0, nullable=False)
downtime_minutes = Column(Integer, default=0, nullable=False)

is_recurring = Column(Boolean, default=False, nullable=False)
recurrence_interval = Column(Integer, nullable=True)
recurrence_pattern = Column(String(50), nullable=True)
next_maintenance_date = Column(DateTime, nullable=True)

customer_notification = Column(Boolean, default=False, nullable=False)
emergency_contact = Column(String(100), nullable=True)

work_order_number = Column(String(50), nullable=True, unique=True)
approval_required = Column(Boolean, default=False, nullable=False)
approved_by = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
approval_date = Column(DateTime, nullable=True)

follow_up_required = Column(Boolean, default=False, nullable=False)
follow_up_date = Column(DateTime, nullable=True)

documentation_completed = Column(Boolean, default=False, nullable=False)
quality_check_passed = Column(Boolean, default=False, nullable=False)
warranty_impact = Column(Boolean, default=False, nullable=False)
firmware_updated = Column(Boolean, default=False, nullable=False)
configuration_backed_up = Column(Boolean, default=False, nullable=False)

maintenance_notes = Column(Text, nullable=True)
completion_notes = Column(Text, nullable=True)

created_by_user = relationship("Usuario", foreign_keys=[created_by], back_populates="created_mantenimientos")
technician = relationship("Usuario", foreign_keys=[technician_id])
supervisor = relationship("Usuario", foreign_keys=[supervisor_id])
approver = relationship("Usuario", foreign_keys=[approved_by])

ubicacion = relationship("Ubicacion", back_populates="mantenimientos")
camara = relationship("Camara", back_populates="mantenimientos")
nvr = relationship("NVR", back_populates="mantenimientos")
switch = relationship("Switch", back_populates="mantenimientos")
ups = relationship("UPS", back_populates="mantenimientos")
fuente_poder = relationship("FuentePoder", back_populates="mantenimientos")
gabinete = relationship("Gabinete", back_populates="mantenimientos")
falla = relationship("Falla", back_populates="mantenimientos")

fotografias = relationship("Fotografia", back_populates="mantenimiento", cascade="all, delete-orphan")

def __repr__(self):
return f"<Mantenimiento(title='{self.title}', status='{self.status}', type='{self.maintenance_type}')>"
=======
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

    # ✅ Corrección crítica: primary key obligatoria
    id = Column(Integer, primary_key=True)

    codigo = Column(String(50), unique=True, index=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    tipo = Column(Enum(MaintenanceType), default=MaintenanceType.PREVENTIVO)
    equipo_tipo = Column(String(50))
    equipo_id = Column(Integer)
    fecha_programada = Column(DateTime)
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    estado = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.PROGRAMADO)
    prioridad = Column(String(20), default='media')
    responsable = Column(String(100))
    costo = Column(Float, default=0)
    observaciones = Column(Text)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    fallas = relationship("Falla", back_populates="mantenimiento")
    fotografias = relationship("Fotografia", lazy="dynamic")

    def __repr__(self):
        return f"<Mantenimiento(title='{self.titulo}', status='{self.estado}', type='{self.tipo}')>"

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
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
