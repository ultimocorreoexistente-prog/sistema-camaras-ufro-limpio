"""
Modelo de gabinetes (Network Racks/Cabinets).
Incluye gestión de gabinetes, equipos instalados y distribución física.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models.equipo import EquipmentBase
from models import db, EquipmentStatus
import enum


class CabinetType(enum.Enum):
    """Tipos de gabinetes."""
    WALL_MOUNT = "wall_mount"
    FLOOR_STANDING = "floor_standing"
    RACK = "rack"
    OUTDOOR = "outdoor"
    SERVER = "server"
    PATCH = "patch"


class CabinetMaterial(enum.Enum):
    """Materiales de construcción."""
    STEEL = "steel"
    ALUMINUM = "aluminum"
    PLASTIC = "plastic"
    GLASS = "glass"
    WOOD = "wood"


class VentilationType(enum.Enum):
    """Tipos de ventilación."""
    PASSIVE = "passive"
    ACTIVE = "active"
    FORCED = "forced"
    CONDITIONED = "conditioned"


class Gabinete(EquipmentBase):  # ✅ Renombrado de Cabinet → Gabinete (consistencia en español)
    """
    Modelo de gabinetes y racks de red.
    Attributes:
    cabinet_type (str): Tipo de gabinete
    material (str): Material de construcción
    depth_mm (int): Profundidad en milímetros
    width_mm (int): Ancho en milímetros
    height_mm (int): Alto en milímetros
    rack_units (int): Número de unidades de rack (U)
    usable_rack_units (int): Unidades de rack utilizables
    max_weight_kg (float): Peso máximo soportado en kg
    ventilation_type (str): Tipo de ventilación
    cooling_fans (int): Número de ventiladores de refrigeración
    airflow_cfm (int): Flujo de aire en CFM
    temperature_monitoring (bool): Monitoreo de temperatura
    humidity_monitoring (bool): Monitoreo de humedad
    smoke_detection (bool): Detección de humo
    security_lock (bool): Cerradura de seguridad
    key_type (str): Tipo de llave
    door_type (str): Tipo de puerta
    cable_management (bool): Gestión de cables disponible
    cable_ring_capacity (int): Capacidad de anillos para cables
    pdus_included (bool): PDUs incluidos
    pdus_count (int): Número de PDUs incluidos
    grounding_available (bool): Sistema de puesta a tierra disponible
    lightning_protection (bool): Protección contra rayos
    fire_resistant (bool): Resistente al fuego
    ip_rating (str): Rating de protección IP
    lock_type (str): Tipo de cerradura
    access_control (bool): Control de acceso
    door_opening_degrees (int): Grados de apertura de puerta
    removable_side_panels (bool): Paneles laterales removibles
    adjustable_feet (bool): Pies ajustables
    casters_included (bool): Ruedas incluidas
    leveling_feet (bool): Pies niveladores
    mounting_holes (str): Patrón de agujeros de montaje
    color (str): Color del gabinete
    finish_type (str): Tipo de acabado
    environmental_conditions (str): Condiciones ambientales soportadas
    seismic_rating (str): Rating sísmico
    certifications (str): Certificaciones (JSON)
    manufacturer_warranty (str): Garantía del fabricante
    installation_instructions (str): Instrucciones de instalación
    maintenance_schedule (str): Programa de mantenimiento
    inventory_location (str): Ubicación en inventario
    physical_location_notes (str): Notas sobre ubicación física
    access_schedule (str): Horario de acceso permitido
    responsible_person (int): ID del responsable
    last_inspection (datetime): Fecha de última inspección
    next_inspection (datetime): Fecha de próxima inspección
    cleaning_schedule (str): Programa de limpieza
    capacity_utilization (float): Utilización de capacidad
    temperature_celsius (float): Temperatura actual
    humidity_percentage (float): Humedad actual
    door_status (str): Estado de la puerta (abierta/cerrada)
    alarm_status (str): Estado de alarmas
    access_log_enabled (bool): Log de acceso habilitado
    """

    __tablename__ = 'gabinetes'

    # ✅ Corrección crítica: primary key
    id = Column(Integer, primary_key=True)

    # Tipo y dimensiones físicas
    cabinet_type = Column(Enum(CabinetType), nullable=True,
                          comment="Tipo de gabinete")
    material = Column(Enum(CabinetMaterial), nullable=True,
                      comment="Material de construcción")

    # Dimensiones
    depth_mm = Column(Integer, nullable=True,
                      comment="Profundidad en milímetros")
    width_mm = Column(Integer, nullable=True,
                      comment="Ancho en milímetros")
    height_mm = Column(Integer, nullable=True,
                       comment="Alto en milímetros")

    # Capacidad de rack
    rack_units = Column(Integer, nullable=True,
                        comment="Número total de unidades de rack (U)")
    usable_rack_units = Column(Integer, nullable=True,
                               comment="Unidades de rack utilizables")
    max_weight_kg = Column(Float, nullable=True,
                           comment="Peso máximo soportado en kg")

    # Ventilación y clima
    ventilation_type = Column(Enum(VentilationType), nullable=True,
                              comment="Tipo de ventilación")
    cooling_fans = Column(Integer, default=0, nullable=False,
                          comment="Número de ventiladores de refrigeración")
    airflow_cfm = Column(Integer, nullable=True,
                         comment="Flujo de aire en CFM (pies cúbicos por minuto)")

    # Monitoreo ambiental
    temperature_monitoring = Column(Boolean, default=False, nullable=False,
                                    comment="Monitoreo de temperatura")
    humidity_monitoring = Column(Boolean, default=False, nullable=False,
                                 comment="Monitoreo de humedad")
    smoke_detection = Column(Boolean, default=False, nullable=False,
                             comment="Detección de humo")

    # Seguridad
    security_lock = Column(Boolean, default=True, nullable=False,
                           comment="Cerradura de seguridad")
    key_type = Column(String(30), nullable=True,
                      comment="Tipo de llave")
    door_type = Column(String(30), nullable=True,
                       comment="Tipo de puerta")
    lock_type = Column(String(30), nullable=True,
                       comment="Tipo de cerradura")

    # Gestión de cables
    cable_management = Column(Boolean, default=False, nullable=False,
                              comment="Gestión de cables disponible")
    cable_ring_capacity = Column(Integer, nullable=True,
                                 comment="Capacidad de anillos para cables")

    # PDUs y alimentación
    pdus_included = Column(Boolean, default=False, nullable=False,
                           comment="PDUs (Power Distribution Units) incluidos")
    pdus_count = Column(Integer, default=0, nullable=False,
                        comment="Número de PDUs incluidos")

    # Sistemas de protección
    grounding_available = Column(Boolean, default=False, nullable=False,
                                 comment="Sistema de puesta a tierra disponible")
    lightning_protection = Column(Boolean, default=False, nullable=False,
                                  comment="Protección contra rayos")
    fire_resistant = Column(Boolean, default=False, nullable=False,
                            comment="Resistente al fuego")

    # Clasificación IP
    ip_rating = Column(String(10), nullable=True,
                       comment="Rating de protección IP (ej: IP54)")

    # Características físicas avanzadas
    access_control = Column(Boolean, default=False, nullable=False,
                            comment="Control de acceso disponible")
    door_opening_degrees = Column(Integer, nullable=True,
                                  comment="Grados de apertura de puerta")
    removable_side_panels = Column(Boolean, default=False, nullable=False,
                                   comment="Paneles laterales removibles")
    adjustable_feet = Column(Boolean, default=True, nullable=False,
                             comment="Pies ajustables")
    casters_included = Column(Boolean, default=False, nullable=False,
                              comment="Ruedas incluidas")
    leveling_feet = Column(Boolean, default=True, nullable=False,
                           comment="Pies niveladores")

    # Montaje
    mounting_holes = Column(String(50), nullable=True,
                            comment="Patrón de agujeros de montaje")

    # Acabado
    color = Column(String(30), nullable=True,
                   comment="Color del gabinete")
    finish_type = Column(String(30), nullable=True,
                         comment="Tipo de acabado")

    # Condiciones ambientales
    environmental_conditions = Column(String(100), nullable=True,
                                      comment="Condiciones ambientales soportadas")
    seismic_rating = Column(String(20), nullable=True,  # ✅ Corregido String(0) → String(20)
                            comment="Rating sísmico")

    # Certificaciones
    certifications = Column(Text, nullable=True,
                            comment="Certificaciones en formato JSON")
    manufacturer_warranty = Column(String(50), nullable=True,
                                   comment="Garantía del fabricante")

    # Documentación
    installation_instructions = Column(Text, nullable=True,
                                       comment="Instrucciones de instalación")
    maintenance_schedule = Column(Text, nullable=True,
                                  comment="Programa de mantenimiento")

    # Ubicación y gestión
    inventory_location = Column(String(100), nullable=True,
                                comment="Ubicación en inventario")
    physical_location_notes = Column(Text, nullable=True,
                                     comment="Notas sobre ubicación física")
    access_schedule = Column(Text, nullable=True,
                             comment="Horario de acceso permitido")
    responsible_person = Column(Integer, ForeignKey('usuarios.id'), nullable=True,
                                comment="ID del usuario responsable")

    # Inspecciones y mantenimiento
    last_inspection = Column(DateTime, nullable=True,
                             comment="Fecha de última inspección")
    next_inspection = Column(DateTime, nullable=True,
                             comment="Fecha de próxima inspección")
    cleaning_schedule = Column(Text, nullable=True,
                               comment="Programa de limpieza")

    # Métricas actuales
    capacity_utilization = Column(Float, default=0.0, nullable=False,
                                  comment="Utilización de capacidad (%)")
    temperature_celsius = Column(Float, nullable=True,
                                 comment="Temperatura actual en °C")
    humidity_percentage = Column(Float, nullable=True,
                                 comment="Humedad actual (%)")

    # Estado actual
    door_status = Column(String(20), default="closed", nullable=False,  # ✅ String(0) → String(20)
                         comment="Estado de la puerta (open/closed)")
    alarm_status = Column(String(50), nullable=True,  # ✅ String(0) → String(50)
                          comment="Estado de alarmas")
    access_log_enabled = Column(Boolean, default=False, nullable=False,
                                comment="Log de acceso habilitado")

    # Relaciones
    ubicacion = relationship("Ubicacion", back_populates="gabinetes")
    created_by_user = relationship("Usuario", back_populates="created_equipos")
    responsible = relationship("Usuario", foreign_keys=[responsible_person])

    # Relaciones con otros modelos
    mantenimientos = relationship("Mantenimiento", back_populates="gabinete", cascade="all, delete-orphan")
    fotografias = relationship("Fotografia", back_populates="gabinete", cascade="all, delete-orphan")
    installed_equipment = relationship("GabineteEquipment", back_populates="gabinete", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Gabinete(name='{self.name}', type='{self.cabinet_type.value if self.cabinet_type else 'N/A'}', units={self.rack_units}U)>"

    def get_available_units(self):
        if not self.rack_units:
            return 0
        used_units = sum([eq.rack_units_used for eq in self.installed_equipment])
        available = self.usable_rack_units - used_units if self.usable_rack_units else self.rack_units - used_units
        return max(0, available)

    def can_install_equipment(self, required_units):
        return self.get_available_units() >= required_units

    def get_capacity_utilization_percentage(self):
        total_units = self.usable_rack_units or self.rack_units
        if not total_units or total_units == 0:
            return 0
        used_units = sum([eq.rack_units_used for eq in self.installed_equipment])
        return (used_units / total_units) * 100

    def get_system_health_score(self):
        score = 100
        if self.capacity_utilization > 95:
            score -= 30
        elif self.capacity_utilization > 85:
            score -= 15
        if hasattr(self, 'status') and self.status != EquipmentStatus.ACTIVO.value:  # ✅ Corregido =
            score -= 10
        return max(0, min(100, score))

    @classmethod
    def get_by_capacity_requirement(cls, required_units):
        gabinetes = cls.query.filter_by(status=EquipmentStatus.ACTIVO.value, deleted=False).all()
        available = []
        for gabinete in gabinetes:
            if gabinete.can_install_equipment(required_units):
                available.append(gabinete)
        return available


class GabineteEquipment(BaseModel, db.Model):
    __tablename__ = 'gabinete_equipment'
    id = Column(Integer, primary_key=True)  # ✅ Primary key añadida

    gabinete_id = Column(Integer, ForeignKey('gabinetes.id'), nullable=False)
    connected_equipment_id = Column(Integer, nullable=True)
    connected_equipment_type = Column(String(30), nullable=True)
    start_unit = Column(Integer, nullable=False)
    rack_units_used = Column(Integer, nullable=False)
    orientation = Column(String(10), default="front", nullable=False)  # ✅ String(0) → String(10)
    priority_level = Column(Integer, default=2, nullable=False)  # ✅ default=, → default=2

    installation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    installation_notes = Column(Text, nullable=True)
    gabinete = relationship("Gabinete", back_populates="installed_equipment")

    def __repr__(self):
        return f"<GabineteEquipment(gabinete={self.gabinete_id}, equipment={self.connected_equipment_type}_{self.connected_equipment_id})>"