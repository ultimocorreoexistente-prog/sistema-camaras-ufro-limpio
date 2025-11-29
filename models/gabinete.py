"""
Modelo de gabinetes (Network Racks/Cabinets).
Incluye gestión de gabinetes, equipos instalados y distribución física.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.base import TimestampedModel
from models import db
from models.equipo import EquipmentBase
from models.enums.equipment_status import EquipmentStatus
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


class Gabinete(db.Model, TimestampedModel):
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

    # Identificador
    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID único del gabinete")
    
    # Tipo y dimensiones físicas
    cabinet_type = Column(Enum(CabinetType), nullable=True, comment="Tipo de gabinete")
    material = Column(Enum(CabinetMaterial), nullable=True, comment="Material de construcción")
    depth_mm = Column(Integer, nullable=True, comment="Profundidad en milímetros")
    width_mm = Column(Integer, nullable=True, comment="Ancho en milímetros")
    height_mm = Column(Integer, nullable=True, comment="Alto en milímetros")

    # Capacidad de rack
    rack_units = Column(Integer, nullable=True, comment="Número total de unidades de rack (U)")
    usable_rack_units = Column(Integer, nullable=True, comment="Unidades de rack utilizables")
    max_weight_kg = Column(Float, nullable=True, comment="Peso máximo soportado en kg")

    # Ventilación y clima
    ventilation_type = Column(Enum(VentilationType), nullable=True, comment="Tipo de ventilación")
    cooling_fans = Column(Integer, default=0, nullable=False, comment="Número de ventiladores de refrigeración")
    airflow_cfm = Column(Integer, nullable=True, comment="Flujo de aire en CFM (pies cúbicos por minuto)")

    # Monitoreo ambiental
    temperature_monitoring = Column(Boolean, default=False, nullable=False, comment="Monitoreo de temperatura")
    humidity_monitoring = Column(Boolean, default=False, nullable=False, comment="Monitoreo de humedad")
    smoke_detection = Column(Boolean, default=False, nullable=False, comment="Detección de humo")

    # Seguridad
    security_lock = Column(Boolean, default=True, nullable=False, comment="Cerradura de seguridad")
    key_type = Column(String(30), nullable=True, comment="Tipo de llave")
    door_type = Column(String(30), nullable=True, comment="Tipo de puerta")
    lock_type = Column(String(30), nullable=True, comment="Tipo de cerradura")

    # Gestión de cables
    cable_management = Column(Boolean, default=False, nullable=False, comment="Gestión de cables disponible")
    cable_ring_capacity = Column(Integer, nullable=True, comment="Capacidad de anillos para cables")

    # PDUs y alimentación
    pdus_included = Column(Boolean, default=False, nullable=False, comment="PDUs (Power Distribution Units) incluidos")
    pdus_count = Column(Integer, default=0, nullable=False, comment="Número de PDUs incluidos")

    # Sistemas de protección
    grounding_available = Column(Boolean, default=False, nullable=False, comment="Sistema de puesta a tierra disponible")
    lightning_protection = Column(Boolean, default=False, nullable=False, comment="Protección contra rayos")
    fire_resistant = Column(Boolean, default=False, nullable=False, comment="Resistente al fuego")

    # Clasificación IP
    ip_rating = Column(String(10), nullable=True, comment="Rating de protección IP (ej: IP54)")

    # Características físicas avanzadas
    access_control = Column(Boolean, default=False, nullable=False, comment="Control de acceso disponible")
    door_opening_degrees = Column(Integer, nullable=True, comment="Grados de apertura de puerta")
    removable_side_panels = Column(Boolean, default=False, nullable=False, comment="Paneles laterales removibles")
    adjustable_feet = Column(Boolean, default=True, nullable=False, comment="Pies ajustables")
    casters_included = Column(Boolean, default=False, nullable=False, comment="Ruedas incluidas")
    leveling_feet = Column(Boolean, default=True, nullable=False, comment="Pies niveladores")

    # Montaje
    mounting_holes = Column(String(50), nullable=True, comment="Patrón de agujeros de montaje")

    # Acabado
    color = Column(String(30), nullable=True, comment="Color del gabinete")
    finish_type = Column(String(30), nullable=True, comment="Tipo de acabado")

    # Condiciones ambientales
    environmental_conditions = Column(String(100), nullable=True, comment="Condiciones ambientales soportadas")
    seismic_rating = Column(String(20), nullable=True, comment="Rating sísmico")

    # Certificaciones
    certifications = Column(Text, nullable=True, comment="Certificaciones en formato JSON")
    manufacturer_warranty = Column(String(50), nullable=True, comment="Garantía del fabricante")

    # Documentación
    installation_instructions = Column(Text, nullable=True, comment="Instrucciones de instalación")
    maintenance_schedule = Column(Text, nullable=True, comment="Programa de mantenimiento")

    # Ubicación y gestión
    inventory_location = Column(String(100), nullable=True, comment="Ubicación en inventario")
    physical_location_notes = Column(Text, nullable=True, comment="Notas sobre ubicación física")
    access_schedule = Column(Text, nullable=True, comment="Horario de acceso permitido")
    responsible_person = Column(Integer, ForeignKey('usuarios.id'), nullable=True, comment="ID del usuario responsable")

    # Inspecciones y mantenimiento
    last_inspection = Column(DateTime, nullable=True, comment="Fecha de última inspección")
    next_inspection = Column(DateTime, nullable=True, comment="Fecha de próxima inspección")
    cleaning_schedule = Column(Text, nullable=True, comment="Programa de limpieza")

    # Métricas actuales
    capacity_utilization = Column(Float, default=0.0, nullable=False, comment="Utilización de capacidad (%)")
    temperature_celsius = Column(Float, nullable=True, comment="Temperatura actual en °C")
    humidity_percentage = Column(Float, nullable=True, comment="Humedad actual (%)")

    # Estado actual
    door_status = Column(String(20), default="closed", nullable=False, comment="Estado de la puerta (open/closed)")
    alarm_status = Column(String(50), nullable=True, comment="Estado de alarmas")
    access_log_enabled = Column(Boolean, default=False, nullable=False, comment="Log de acceso habilitado")

    # Relaciones
    ubicacion = relationship("Ubicacion", back_populates="gabinetes")
    created_by_user = relationship("Usuario", back_populates="created_equipos")
    responsible = relationship("Usuario", foreign_keys=[responsible_person])

    # Relaciones con otros modelos
    mantenimientos = relationship("Mantenimiento", back_populates="gabinete", cascade="all, delete-orphan")
    fotografias = relationship("Fotografia", back_populates="gabinete", cascade="all, delete-orphan")

    # Relaciones con equipos instalados
    installed_equipment = relationship("GabineteEquipment", back_populates="gabinete", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Gabinete(id={self.id}, type='{self.cabinet_type.value if self.cabinet_type else 'N/A'}', units={self.rack_units}U)>"

    def get_available_units(self):
        """
        Obtiene las unidades de rack disponibles.

        Returns:
            int: Número de unidades disponibles
        """
        if not self.rack_units:
            return 0

        used_units = sum([eq.rack_units_used for eq in self.installed_equipment])
        available = self.usable_rack_units - used_units if self.usable_rack_units else self.rack_units - used_units
        return max(0, available)

    def can_install_equipment(self, required_units):
        """
        Verifica si se puede instalar equipo que requiera las unidades especificadas.

        Args:
            required_units (int): Unidades de rack requeridas

        Returns:
            bool: True si se puede instalar
        """
        return self.get_available_units() >= required_units

    def get_capacity_utilization_percentage(self):
        """
        Calcula el porcentaje de utilización de capacidad.

        Returns:
            float: Porcentaje de utilización
        """
        total_units = self.usable_rack_units or self.rack_units
        if not total_units or total_units == 0:
            return 0

        used_units = sum([eq.rack_units_used for eq in self.installed_equipment])
        return (used_units / total_units) * 100

    def get_equipment_summary(self):
        """
        Obtiene un resumen de los equipos instalados.

        Returns:
            dict: Resumen de equipos
        """
        total_equipment = len(self.installed_equipment)
        if total_equipment == 0:
            return {
                'total_equipment': 0,
                'equipment_types': {},
                'weight_kg': 0,
                'power_consumption_watts': 0
            }

        equipment_types = {}
        total_weight = 0
        total_power = 0

        for equipment in self.installed_equipment:
            eq_type = equipment.connected_equipment_type
            if eq_type not in equipment_types:
                equipment_types[eq_type] = 0
            equipment_types[eq_type] += 1

            # Estimar peso y consumo basado en el tipo
            if hasattr(equipment.equipment_object, 'weight'):
                total_weight += equipment.equipment_object.weight or 0
            if hasattr(equipment.equipment_object, 'power_consumption'):
                total_power += equipment.equipment_object.power_consumption or 0

        return {
            'total_equipment': total_equipment,
            'equipment_types': equipment_types,
            'weight_kg': total_weight,
            'power_consumption_watts': total_power
        }

    def get_environmental_status(self):
        """
        Obtiene el estado ambiental del gabinete.

        Returns:
            dict: Estado ambiental
        """
        return {
            'temperature_celsius': self.temperature_celsius,
            'humidity_percentage': self.humidity_percentage,
            'temperature_monitoring_enabled': self.temperature_monitoring,
            'humidity_monitoring_enabled': self.humidity_monitoring,
            'smoke_detection_enabled': self.smoke_detection,
            'cooling_fans_count': self.cooling_fans,
            'airflow_cfm': self.airflow_cfm
        }

    def get_security_status(self):
        """
        Obtiene el estado de seguridad del gabinete.

        Returns:
            dict: Estado de seguridad
        """
        return {
            'is_locked': self.security_lock,
            'door_status': self.door_status,
            'key_type': self.key_type,
            'access_control_enabled': self.access_control,
            'access_log_enabled': self.access_log_enabled
        }

    def is_inspection_due(self):
        """
        Verifica si la inspección está vencida.

        Returns:
            bool: True si la inspección está vencida
        """
        if not self.next_inspection:
            return False

        return datetime.utcnow() >= self.next_inspection

    def install_equipment(self, equipment_object, equipment_type, start_unit, rack_units_used, **kwargs):
        """
        Instala un equipo en el gabinete.

        Args:
            equipment_object: Objeto del equipo
            equipment_type (str): Tipo de equipo
            start_unit (int): Unidad de rack donde inicia la instalación
            rack_units_used (int): Unidades de rack que ocupa
            **kwargs: Parámetros adicionales

        Returns:
            GabineteEquipment: Instalación creada o None si no es posible
        """
        if not self.can_install_equipment(rack_units_used):
            return None

        # Verificar que no haya conflictos con otros equipos
        occupied_units = set()
        for installed in self.installed_equipment:
            for i in range(installed.start_unit, installed.start_unit + installed.rack_units_used):
                occupied_units.add(i)

        new_units = set(range(start_unit, start_unit + rack_units_used))
        if occupied_units.intersection(new_units):
            return None # Conflicto de espacio

        installation = GabineteEquipment(
            gabinete_id=self.id,
            connected_equipment_id=equipment_object.id,
            connected_equipment_type=equipment_type,
            start_unit=start_unit,
            rack_units_used=rack_units_used,
            **kwargs
        )
        return installation.save()

    def remove_equipment(self, equipment_object):
        """
        Remueve un equipo del gabinete.

        Args:
            equipment_object: Objeto del equipo a remover

        Returns:
            bool: True si se removió exitosamente
        """
        equipment_type = equipment_object.__class__.__name__.lower()

        installation = GabineteEquipment.query.filter_by(
            gabinete_id=self.id,
            connected_equipment_id=equipment_object.id,
            connected_equipment_type=equipment_type,
            deleted=False
        ).first()

        if installation:
            installation.delete()
            return True

        return False

    def get_temperature_alert_status(self):
        """
        Verifica el estado de alerta por temperatura.

        Returns:
            dict: Estado de alerta de temperatura
        """
        if not self.temperature_monitoring or not self.temperature_celsius:
            return {'status': 'no_monitoring', 'alert': False}

        # Umbrales típicos para equipos de red
        if self.temperature_celsius > 40:
            return {'status': 'critical', 'alert': True, 'message': 'Temperatura crítica'}
        elif self.temperature_celsius > 35:
            return {'status': 'warning', 'alert': True, 'message': 'Temperatura alta'}
        elif self.temperature_celsius > 30:
            return {'status': 'caution', 'alert': False, 'message': 'Temperatura elevada'}
        else:
            return {'status': 'normal', 'alert': False, 'message': 'Temperatura normal'}

    def get_humidity_alert_status(self):
        """
        Verifica el estado de alerta por humedad.

        Returns:
            dict: Estado de alerta de humedad
        """
        if not self.humidity_monitoring or not self.humidity_percentage:
            return {'status': 'no_monitoring', 'alert': False}

        # Umbrales típicos para equipos de red
        if self.humidity_percentage > 80:
            return {'status': 'critical', 'alert': True, 'message': 'Humedad crítica'}
        elif self.humidity_percentage > 70:
            return {'status': 'warning', 'alert': True, 'message': 'Humedad alta'}
        elif self.humidity_percentage > 60:
            return {'status': 'caution', 'alert': False, 'message': 'Humedad elevada'}
        elif self.humidity_percentage < 0:
            return {'status': 'warning', 'alert': True, 'message': 'Humedad muy baja'}
        elif self.humidity_percentage < 30:
            return {'status': 'caution', 'alert': False, 'message': 'Humedad baja'}
        else:
            return {'status': 'normal', 'alert': False, 'message': 'Humedad normal'}

    def update_capacity_utilization(self):
        """
        Actualiza el porcentaje de utilización de capacidad.
        """
        self.capacity_utilization = self.get_capacity_utilization_percentage()
        self.save()

    def get_system_health_score(self):
        """
        Calcula un puntaje de salud del sistema (0-100).

        Returns:
            int: Puntaje de salud del sistema
        """
        score = 100

        # Penalizar por alta utilización
        if self.capacity_utilization > 95:
            score -= 30
        elif self.capacity_utilization > 85:
            score -= 15

        # Penalizar por temperatura alta
        temp_status = self.get_temperature_alert_status()
        if temp_status.get('status') == 'critical':
            score -= 5
        elif temp_status.get('status') == 'warning':
            score -= 15

        # Penalizar por humedad inadecuada
        humidity_status = self.get_humidity_alert_status()
        if humidity_status.get('status') in ['critical', 'warning']:
            score -= 15

        # Penalizar por inspección vencida
        if self.is_inspection_due():
            score -= 10

        # Penalizar por estado del equipo
        if self.status != EquipmentStatus.ACTIVO:
            score -= 0

        # Penalizar por falta de heartbeat reciente
        if not self.is_online():
            score -= 15

        # Penalizar por puerta abierta
        if self.door_status == 'open':
            score -= 5

        return max(0, min(100, score))

    def get_maintenance_summary(self):
        """
        Obtiene un resumen de mantenimiento.

        Returns:
            dict: Resumen de mantenimiento
        """
        return {
            'last_inspection': self.last_inspection.isoformat() if self.last_inspection else None,
            'next_inspection': self.next_inspection.isoformat() if self.next_inspection else None,
            'inspection_due': self.is_inspection_due(),
            'maintenance_schedule': self.maintenance_schedule,
            'cleaning_schedule': self.cleaning_schedule,
            'responsible_person_id': self.responsible_person
        }

    @classmethod
    def get_by_capacity_requirement(cls, required_units):
        """
        Obtiene gabinetes con capacidad suficiente.

        Args:
            required_units (int): Unidades de rack requeridas

        Returns:
            list: Lista de gabinetes con capacidad suficiente
        """
        gabinetes = cls.query.filter_by(
            status=EquipmentStatus.ACTIVO,
            deleted=False
        ).all()

        available = []
        for gabinete in gabinetes:
            if gabinete.can_install_equipment(required_units):
                available.append(gabinete)

        return available

    @classmethod
    def get_by_type(cls, cabinet_type):
        """
        Obtiene gabinetes de un tipo específico.

        Args:
            cabinet_type (CabinetType): Tipo de gabinete

        Returns:
            list: Lista de gabinetes del tipo especificado
        """
        return cls.query.filter_by(cabinet_type=cabinet_type, deleted=False).all()

    @classmethod
    def get_environmental_monitoring_enabled(cls):
        """
        Obtiene gabinetes con monitoreo ambiental habilitado.

        Returns:
            list: Lista de gabinetes con monitoreo
        """
        return cls.query.filter(
            db.or_(
                cls.temperature_monitoring == True,
                cls.humidity_monitoring == True,
                cls.smoke_detection == True
            ),
            cls.deleted == False
        ).all()


class GabineteEquipment(db.Model, TimestampedModel):
    """
    Modelo de equipos instalados en gabinetes.

    Attributes:
        gabinete_id (int): ID del gabinete
        connected_equipment_id (int): ID del equipo instalado
        connected_equipment_type (str): Tipo del equipo instalado
        start_unit (int): Unidad de rack donde inicia la instalación
        rack_units_used (int): Unidades de rack que ocupa
        rack_position (int): Posición en el rack (1-4 típico)
        orientation (str): Orientación del equipo (front/back)
        cable_management_used (bool): Si usa gestión de cables
        weight_kg (float): Peso del equipo en kg
        power_consumption_watts (float): Consumo de potencia en watts
        ventilation_required (bool): Si requiere ventilación especial
        access_required (bool): Si requiere acceso frecuente
        priority_level (int): Nivel de prioridad (1=alta, 2=media, 3=baja)
        installation_date (datetime): Fecha de instalación
        installation_notes (str): Notas de instalación
        maintenance_access (bool): Si requiere acceso para mantenimiento
    """

    __tablename__ = 'gabinete_equipment'

    # Primary key
    id = Column(Integer, primary_key=True)

    gabinete_id = Column(Integer, ForeignKey('gabinetes.id'), nullable=False, comment="ID del gabinete")
    connected_equipment_id = Column(Integer, nullable=True, comment="ID del equipo instalado")
    connected_equipment_type = Column(String(30), nullable=True, comment="Tipo del equipo instalado")

    # Posición física
    start_unit = Column(Integer, nullable=False, comment="Unidad de rack donde inicia (1=bottom)")
    rack_units_used = Column(Integer, nullable=False, comment="Unidades de rack que ocupa")
    rack_position = Column(Integer, nullable=True, comment="Posición específica en el rack")
    orientation = Column(String(10), default="front", nullable=False, comment="Orientación del equipo (front/back)")

    # Características físicas
    cable_management_used = Column(Boolean, default=False, nullable=False, comment="Si usa gestión de cables del gabinete")
    weight_kg = Column(Float, nullable=True, comment="Peso del equipo en kg")
    power_consumption_watts = Column(Float, nullable=True, comment="Consumo de potencia en watts")

    # Requisitos especiales
    ventilation_required = Column(Boolean, default=False, nullable=False, comment="Si requiere ventilación especial")
    access_required = Column(Boolean, default=False, nullable=False, comment="Si requiere acceso frecuente")
    maintenance_access = Column(Boolean, default=True, nullable=False, comment="Si requiere acceso para mantenimiento")

    # Gestión
    priority_level = Column(Integer, default=2, nullable=False, comment="Nivel de prioridad (1=alta, 2=media, 3=baja)")

    # Fechas
    installation_date = Column(DateTime, default=datetime.utcnow, nullable=False, comment="Fecha de instalación")

    # Metadatos
    installation_notes = Column(Text, nullable=True, comment="Notas de la instalación")

    # Relaciones
    gabinete = relationship("Gabinete", back_populates="installed_equipment")

    def __repr__(self):
        return f"<GabineteEquipment(gabinete={self.gabinete_id}, equipment={self.connected_equipment_type}_{self.connected_equipment_id}, units={self.start_unit}-{self.start_unit + self.rack_units_used - 1})>"

    def get_end_unit(self):
        """
        Obtiene la unidad donde termina la instalación.

        Returns:
            int: Unidad final
        """
        return self.start_unit + self.rack_units_used - 1

    def overlaps_with(self, other_installation):
        """
        Verifica si se superpone con otra instalación.

        Args:
            other_installation: Otra instalación para comparar

        Returns:
            bool: True si se superpone
        """
        self_end = self.get_end_unit()
        other_end = other_installation.get_end_unit()

        return not (self_end < other_installation.start_unit or
                   other_end < self.start_unit)

    @classmethod
    def get_by_gabinete(cls, gabinete_id):
        """
        Obtiene los equipos instalados en un gabinete.

        Args:
            gabinete_id (int): ID del gabinete

        Returns:
            list: Lista de equipos instalados
        """
        return cls.query.filter_by(gabinete_id=gabinete_id, deleted=False).all()

    @classmethod
    def get_by_equipment(cls, equipment_id, equipment_type):
        """
        Obtiene la instalación de un equipo específico.

        Args:
            equipment_id (int): ID del equipo
            equipment_type (str): Tipo del equipo

        Returns:
            GabineteEquipment: Instalación del equipo o None
        """
        return cls.query.filter_by(
            connected_equipment_id=equipment_id,
            connected_equipment_type=equipment_type,
            deleted=False
        ).first()

    @classmethod
    def get_available_units(cls, gabinete_id):
        """
        Obtiene las unidades disponibles en un gabinete.

        Args:
            gabinete_id (int): ID del gabinete

        Returns:
            list: Lista de unidades disponibles
        """
        gabinete = Gabinete.query.get(gabinete_id)
        if not gabinete:
            return []

        installations = cls.query.filter_by(gabinete_id=gabinete_id, deleted=False).all()

        total_units = gabinete.usable_rack_units or gabinete.rack_units
        if not total_units:
            return []

        occupied_units = set()
        for installation in installations:
            for i in range(installation.start_unit, installation.get_end_unit() + 1):
                occupied_units.add(i)

        available = []
        for unit in range(1, total_units + 1):
            if unit not in occupied_units:
                available.append(unit)

        return available
