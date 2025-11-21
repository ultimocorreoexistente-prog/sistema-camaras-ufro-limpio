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


class Mantenimiento(BaseModel, db.Model):
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