# models/mantenimiento.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db

# ✅ Enums locales (sin imports problemáticos)
class MaintenanceType:
    PREVENTIVO = "preventivo"
    CORRECTIVO = "correctivo"
    PREDICTIVO = "predictivo"
    URGENTE = "urgente"
    RUTINARIO = "rutinario"

class MaintenancePriority:
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"

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
    __tablename__ = 'mantenimientos'

    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    maintenance_type = Column(String(20), nullable=False)
    category = Column(String(20), nullable=False)
    priority = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="programado")

    equipment_id = Column(Integer, nullable=True)
    equipment_type = Column(String(30), nullable=True)

    # ✅ CORREGIDO: usar nombres reales de tablas
    camara_id = Column(Integer, ForeignKey('camaras.id'), nullable=True)
    nvr_id = Column(Integer, ForeignKey('nvr_dvr.id'), nullable=True)        # ✅ nvr_dvr.id
    switch_id = Column(Integer, ForeignKey('switches.id'), nullable=True)
    ups_id = Column(Integer, ForeignKey('ups.id'), nullable=True)
    fuente_poder_id = Column(Integer, ForeignKey('fuente_poder.id'), nullable=True)  # ✅ fuente_poder.id
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