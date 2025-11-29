"""
Modelo de fuentes de poder (Power Supplies).

Incluye gestión de fuentes de alimentación para equipos diversos.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.base import TimestampedModel
from models import db
from models.enums.equipment_status import EquipmentStatus
from models.equipo import EquipmentBase
import enum


class PowerSupplyType(enum.Enum):
    """Tipos de fuentes de poder."""
    AC_ADAPTER = "ac_adapter"
    DESKTOP_PSU = "desktop_psu"
    RACK_PSU = "rack_psu"
    REDUNDANT_PSU = "redundant_psu"
    INDUSTRIAL_PSU = "industrial_psu"
    CONVERTER = "converter"
    UNINTERRUPTIBLE = "uninterruptible"


class PSUFormFactor(enum.Enum):
    """Factores de forma de fuentes de poder."""
    ATX = "atx"
    SFX = "sfx"
    TFX = "tfx"
    EPS = "eps"
    FLEX_ATX = "flex_atx"
    PLUG = "plug"
    RACK_MOUNT = "rack_mount"


class PSUStatus(enum.Enum):
    """Estados de fuentes de poder."""
    NORMAL = "normal"
    WARNING = "warning"
    ERROR = "error"
    OFFLINE = "offline"


class FuentePoder(EquipmentBase, db.Model, TimestampedModel):
    """
    Modelo de fuentes de poder.

    Attributes:
    power_supply_type (str): Tipo de fuente de poder
    form_factor (str): Factor de forma
    max_output_watts (int): Potencia máxima de salida en watts
    max_output_voltage (float): Voltaje máximo de salida
    min_output_voltage (float): Voltaje mínimo de salida
    output_voltages (str): Voltajes de salida soportados (JSON)
    input_voltage_range (str): Rango de voltaje de entrada
    input_frequency_range (str): Rango de frecuencia de entrada
    efficiency_rating (str): Certificación de eficiencia (80 Plus)
    modular_cables (bool): Cables modulares
    cable_included (bool): Cables incluidos
    cable_length (float): Longitud de cables en metros
    power_connectors (str): Conectores de poder (JSON)
    fan_included (bool): Ventilador incluido
    fan_size (int): Tamaño del ventilador en mm
    fan_noise_db (float): Ruido del ventilador en dB
    protection_features (str): Características de protección (JSON)
    operating_temperature (str): Temperatura de operación
    storage_temperature (str): Temperatura de almacenamiento
    humidity_range (str): Rango de humedad
    dimensions (str): Dimensiones exactas
    weight_kg (float): Peso en kilogramos
    color (str): Color de la fuente
    mtbf_hours (int): Tiempo medio entre fallas en horas
    warranty_months (int): Garantía en meses
    manufacturer_url (str): URL del fabricante
    datasheet_url (str): URL de la hoja de datos
    certification (str): Certificaciones (CE, FCC, etc.)
    energy_star (bool): Certificación Energy Star
    rohs_compliant (bool): Cumplimiento RoHS
    model_version (str): Versión del modelo
    batch_number (str): Número de lote
    country_of_origin (str): País de origen
    installation_date (datetime): Fecha de instalación
    last_maintenance (datetime): Fecha del último mantenimiento
    next_maintenance (datetime): Fecha del próximo mantenimiento
    self_test_enabled (bool): Auto-prueba habilitada
    remote_monitoring (bool): Monitoreo remoto disponible
    current_output_watts (float): Salida actual en watts
    current_efficiency (float): Eficiencia actual
    temperature_celsius (float): Temperatura en °C
    fan_speed_rpm (int): Velocidad del ventilador en RPM
    psu_status (str): Estado actual de la fuente
    alert_threshold_voltage (float): Umbral de alerta de voltaje
    alert_threshold_temperature (float): Umbral de alerta de temperatura
    load_percentage (float): Porcentaje de carga
    """

    __tablename__ = 'fuente_poder'

    # Tipo y configuración
    power_supply_type = Column(Enum(PowerSupplyType), nullable=True,
                               comment="Tipo de fuente de poder")
    form_factor = Column(Enum(PSUFormFactor), nullable=True,
                         comment="Factor de forma de la fuente")

    # Especificaciones de potencia
    max_output_watts = Column(Integer, nullable=True,
                              comment="Potencia máxima de salida en watts")
    max_output_voltage = Column(Float, nullable=True,
                                comment="Voltaje máximo de salida")
    min_output_voltage = Column(Float, nullable=True,
                                comment="Voltaje mínimo de salida")
    output_voltages = Column(Text, nullable=True,
                             comment="Voltajes de salida soportados (JSON)")

    # Especificaciones de entrada
    input_voltage_range = Column(String(50), nullable=True,
                                 comment="Rango de voltaje de entrada")
    input_frequency_range = Column(String(50), nullable=True,
                                   comment="Rango de frecuencia de entrada")

    # Eficiencia y certificación
    efficiency_rating = Column(String(20), nullable=True,
                               comment="Certificación de eficiencia (80 Plus Bronze, Gold, etc.)")

    # Cables y conectores
    modular_cables = Column(Boolean, default=False, nullable=False,
                            comment="Si tiene cables modulares")
    cable_included = Column(Boolean, default=True, nullable=False,
                            comment="Si incluye cables")
    cable_length = Column(Float, nullable=True,
                          comment="Longitud de cables en metros")
    power_connectors = Column(Text, nullable=True,
                              comment="Conectores de poder soportados (JSON)")

    # Refrigeración
    fan_included = Column(Boolean, default=True, nullable=False,
                          comment="Si incluye ventilador")
    fan_size = Column(Integer, nullable=True,
                      comment="Tamaño del ventilador en mm")
    fan_noise_db = Column(Float, nullable=True,
                          comment="Ruido del ventilador en dB")

    # Características de protección
    protection_features = Column(Text, nullable=True,
                                 comment="Características de protección (JSON)")

    # Condiciones ambientales
    operating_temperature = Column(String(50), nullable=True,
                                   comment="Temperatura de operación")
    storage_temperature = Column(String(50), nullable=True,
                                 comment="Temperatura de almacenamiento")
    humidity_range = Column(String(50), nullable=True,
                            comment="Rango de humedad")

    # Dimensiones y peso
    dimensions = Column(String(50), nullable=True,
                        comment="Dimensiones exactas (L x A x H)")
    weight_kg = Column(Float, nullable=True,
                       comment="Peso en kilogramos")
    color = Column(String(50), nullable=True,
                   comment="Color de la fuente")

    # Confiabilidad
    mtbf_hours = Column(Integer, nullable=True,
                        comment="Tiempo medio entre fallas (MTBF) en horas")
    warranty_months = Column(Integer, nullable=True,
                             comment="Garantía en meses")

    # URLs y documentación
    manufacturer_url = Column(String(500), nullable=True,
                              comment="URL del fabricante")
    datasheet_url = Column(String(500), nullable=True,
                           comment="URL de la hoja de datos")

    # Certificaciones
    certification = Column(String(100), nullable=True,
                           comment="Certificaciones (CE, FCC, UL, etc.)")
    energy_star = Column(Boolean, default=False, nullable=False,
                         comment="Certificación Energy Star")
    rohs_compliant = Column(Boolean, default=False, nullable=False,
                            comment="Cumplimiento RoHS")

    # Identificación y tracking
    model_version = Column(String(20), nullable=True,
                           comment="Versión del modelo")
    batch_number = Column(String(50), nullable=True,
                          comment="Número de lote de producción")
    country_of_origin = Column(String(50), nullable=True,
                               comment="País de origen")

    # Fechas importantes
    installation_date = Column(DateTime, nullable=True,
                               comment="Fecha de instalación")
    last_maintenance = Column(DateTime, nullable=True,
                              comment="Fecha del último mantenimiento")
    next_maintenance = Column(DateTime, nullable=True,
                              comment="Fecha del próximo mantenimiento")

    # Características avanzadas
    self_test_enabled = Column(Boolean, default=False, nullable=False,
                               comment="Auto-prueba habilitada")
    remote_monitoring = Column(Boolean, default=False, nullable=False,
                               comment="Monitoreo remoto disponible")

    # Métricas actuales
    current_output_watts = Column(Float, default=0.0, nullable=False,
                                  comment="Salida actual en watts")
    current_efficiency = Column(Float, default=95.0, nullable=False,
                                comment="Eficiencia actual (%)")
    temperature_celsius = Column(Float, nullable=True,
                                 comment="Temperatura actual en °C")
    fan_speed_rpm = Column(Integer, nullable=True,
                           comment="Velocidad del ventilador en RPM")
    psu_status = Column(Enum(PSUStatus), default=PSUStatus.NORMAL, nullable=False,
                        comment="Estado actual de la fuente")

    # Umbrales de alerta
    alert_threshold_voltage = Column(Float, nullable=True,
                                     comment="Umbral de alerta de voltaje")
    alert_threshold_temperature = Column(Float, nullable=True,
                                         comment="Umbral de alerta de temperatura")

    # Métricas calculadas
    load_percentage = Column(Float, default=0.0, nullable=False,
                             comment="Porcentaje de carga actual")

    # Relaciones
    ubicacion = relationship("Ubicacion", back_populates="fuentes_poder")
    created_by_user = relationship("Usuario", back_populates="created_equipos")

    # Relaciones con otros modelos
    mantenimientos = relationship("Mantenimiento", back_populates="fuente_poder", cascade="all, delete-orphan")
    fotografias = relationship("Fotografia", back_populates="fuente_poder", cascade="all, delete-orphan")

    # Relaciones con equipos conectados
    connected_equipment = relationship("FuentePoderConnection", back_populates="fuente_poder", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FuentePoder(name='{self.name}', capacity='{self.max_output_watts}W', status='{self.psu_status.value}')>"

    def get_capacity_utilization(self):
        """
        Calcula la utilización de la capacidad.

        Returns:
        float: Porcentaje de utilización (0-100)
        """
        if not self.max_output_watts or self.max_output_watts == 0:
            return 0

        utilization = (self.current_output_watts / self.max_output_watts) * 100
        return min(100, max(0, utilization))

    def get_status_color(self):
        """
        Obtiene el color para el estado de la fuente.

        Returns:
        str: Código de color
        """
        colors = {
            PSUStatus.NORMAL: "#8a745",  # Verde
            PSUStatus.WARNING: "#ffc107",  # Amarillo
            PSUStatus.ERROR: "#dc3545",  # Rojo
            PSUStatus.OFFLINE: "#6c757d"  # Gris
        }
        return colors.get(self.psu_status, "#6c757d")

    def is_maintenance_due(self):
        """
        Verifica si el mantenimiento está vencido.

        Returns:
        bool: True si el mantenimiento está vencido
        """
        if not self.next_maintenance:
            return False

        return datetime.utcnow() >= self.next_maintenance

    def get_efficiency_estimate(self):
        """
        Estima la eficiencia basada en la carga actual.

        Returns:
        float: Eficiencia estimada en porcentaje
        """
        if not self.efficiency_rating or self.load_percentage == 0:
            return self.current_efficiency

        # Estimación simplificada de eficiencia basada en carga
        load = self.load_percentage

        if load < 0:
            return 75.0  # Baja eficiencia a cargas muy bajas
        elif load < 50:
            return 85.0
        elif load < 80:
            return self.current_efficiency or 90.0  # Eficiencia máxima
        else:
            return max(80.0, (self.current_efficiency or 90.0) - 5)  # Ligera reducción a máxima carga

    def add_connected_equipment(self, equipment, equipment_type, power_consumption):
        """
        Agrega un equipo conectado a la fuente.

        Args:
        equipment: Equipo conectado
        equipment_type (str): Tipo del equipo
        power_consumption (float): Consumo de poder

        Returns:
        FuentePoderConnection: Conexión creada
        """
        connection = FuentePoderConnection(
            fuente_poder_id=self.id,
            connected_equipment_id=equipment.id,
            connected_equipment_type=equipment_type,
            power_consumption=power_consumption
        )
        return connection.save()

    def get_total_power_consumption(self):
        """
        Obtiene el consumo total de los equipos conectados.

        Returns:
        float: Consumo total en watts
        """
        return sum([conn.power_consumption for conn in self.connected_equipment])

    def update_power_consumption(self):
        """
        Actualiza el consumo de potencia basado en los equipos conectados.
        """
        total_consumption = self.get_total_power_consumption()
        self.current_output_watts = total_consumption
        self.load_percentage = self.get_capacity_utilization()

        # Determinar estado basado en carga y temperatura
        if self.load_percentage > 90 or (self.temperature_celsius and self.temperature_celsius > 80):
            self.psu_status = PSUStatus.ERROR
        elif self.load_percentage > 75 or (self.temperature_celsius and self.temperature_celsius > 70):
            self.psu_status = PSUStatus.WARNING
        else:
            self.psu_status = PSUStatus.NORMAL

        self.save()

    def get_power_consumption_summary(self):
        """
        Obtiene un resumen del consumo de potencia.

        Returns:
        dict: Resumen de consumo
        """
        total_consumption = self.get_total_power_consumption()
        max_capacity = self.max_output_watts or 0
        utilization = self.get_capacity_utilization()

        return {
            'max_capacity_watts': max_capacity,
            'current_consumption_watts': self.current_output_watts,
            'total_connected_consumption_watts': total_consumption,
            'capacity_utilization_percentage': utilization,
            'available_capacity_watts': max_capacity - total_consumption,
            'efficiency_estimate': self.get_efficiency_estimate(),
            'status': self.psu_status.value
        }

    def get_thermal_info(self):
        """
        Obtiene información térmica de la fuente.

        Returns:
        dict: Información térmica
        """
        return {
            'current_temperature': self.temperature_celsius,
            'fan_speed_rpm': self.fan_speed_rpm,
            'has_fan': self.fan_included,
            'fan_size': self.fan_size,
            'noise_level_db': self.fan_noise_db,
            'operating_temperature_range': self.operating_temperature
        }

    def get_warranty_status(self):
        """
        Obtiene el estado de la garantía.

        Returns:
        dict: Estado de la garantía
        """
        if not self.warranty_months or not self.installation_date:
            return {'status': 'unknown', 'days_remaining': None}

        from datetime import timedelta

        warranty_end = self.installation_date + timedelta(days=self.warranty_months * 30)
        days_remaining = (warranty_end - datetime.utcnow()).days

        if days_remaining < 0:
            return {'status': 'expired', 'days_remaining': days_remaining}
        elif days_remaining < 30:
            return {'status': 'expiring', 'days_remaining': days_remaining}
        else:
            return {'status': 'valid', 'days_remaining': days_remaining}

    def perform_self_test(self):
        """
        Realiza una auto-prueba de la fuente.

        Returns:
        bool: True si la prueba fue exitosa
        """
        # Esta es una implementación simplificada
        # En producción se debería interactuar con la fuente real

        # Simular prueba exitosa
        self.self_test_enabled = True
        self.last_heartbeat = datetime.utcnow()

        # Actualizar temperatura y estado
        if self.temperature_celsius and self.temperature_celsius > 75:
            self.psu_status = PSUStatus.WARNING

        self.save()
        return True

    def get_system_health_score(self):
        """
        Calcula un puntaje de salud del sistema (0-100).

        Returns:
        int: Puntaje de salud del sistema
        """
        score = 100

        # Penalizar por estado crítico
        if self.psu_status == PSUStatus.ERROR:
            score -= 40
        elif self.psu_status == PSUStatus.WARNING:
            score -= 20
        elif self.psu_status == PSUStatus.OFFLINE:
            score -= 60

        # Penalizar por sobrecalentamiento
        if self.temperature_celsius and self.temperature_celsius > 80:
            score -= 30
        elif self.temperature_celsius and self.temperature_celsius > 70:
            score -= 15

        # Penalizar por sobrecarga
        if self.load_percentage > 95:
            score -= 30
        elif self.load_percentage > 85:
            score -= 15

        # Penalizar por mantenimiento vencido
        if self.is_maintenance_due():
            score -= 10

        # Penalizar por garantía vencida
        warranty_status = self.get_warranty_status()
        if warranty_status['status'] == 'expired':
            score -= 15

        return max(0, min(100, score))

    @classmethod
    def get_by_capacity_range(cls, min_watts, max_watts):
        """
        Obtiene fuentes por rango de capacidad.

        Args:
        min_watts (int): Potencia mínima
        max_watts (int): Potencia máxima

        Returns:
        list: Lista de fuentes que cumplen el criterio
        """
        return cls.query.filter(
            cls.max_output_watts >= min_watts,
            cls.max_output_watts <= max_watts,
            cls.deleted == False
        ).all()

    @classmethod
    def get_high_efficiency_psus(cls):
        """
        Obtiene fuentes con alta eficiencia (80 Plus Gold o superior).

        Returns:
        list: Lista de fuentes de alta eficiencia
        """
        efficient_ratings = ['80 Plus Gold', '80 Plus Platinum', '80 Plus Titanium']
        return cls.query.filter(
            cls.efficiency_rating.in_(efficient_ratings),
            cls.deleted == False
        ).all()

    @classmethod
    def get_critical_psus(cls):
        """
        Obtiene fuentes en estado crítico.

        Returns:
        list: Lista de fuentes críticas
        """
        return cls.query.filter(
            cls.psu_status.in_([PSUStatus.ERROR, PSUStatus.OFFLINE]),
            cls.deleted == False
        ).all()


class FuentePoderConnection(db.Model, TimestampedModel):
    """
    Modelo de equipos conectados a fuentes de poder.

    Attributes:
    fuente_poder_id (int): ID de la fuente de poder
    connected_equipment_id (int): ID del equipo conectado
    connected_equipment_type (str): Tipo del equipo conectado
    power_consumption (float): Consumo de poder en watts
    connection_type (str): Tipo de conexión
    priority_level (int): Nivel de prioridad (1=alta, 2=media, 3=baja)
    controlled_power (bool): Si tiene control de apagado
    startup_sequence (int): Secuencia de encendido
    shutdown_delay (int): Retraso de apagado en segundos
    is_critical (bool): Si es equipo crítico
    notes (str): Notas adicionales
    """

    __tablename__ = 'fuente_poder_connections'

    id = Column(Integer, primary_key=True)

    fuente_poder_id = Column(Integer, ForeignKey('fuente_poder.id'), nullable=False,
                             comment="ID de la fuente de poder")
    connected_equipment_id = Column(Integer, nullable=True,
                                     comment="ID del equipo conectado")
    connected_equipment_type = Column(String(30), nullable=True,
                                       comment="Tipo del equipo conectado")
    power_consumption = Column(Float, default=0.0, nullable=False,
                               comment="Consumo de poder en watts")

    # Configuración de control
    connection_type = Column(String(30), nullable=True,
                             comment="Tipo de conexión eléctrica")
    priority_level = Column(Integer, default=2, nullable=False,
                            comment="Nivel de prioridad (1=alta, 2=media, 3=baja)")
    controlled_power = Column(Boolean, default=False, nullable=False,
                              comment="Si tiene control de apagado/encendido")

    # Secuencias
    startup_sequence = Column(Integer, nullable=True,
                              comment="Secuencia de encendido")
    shutdown_delay = Column(Integer, default=0, nullable=False,
                            comment="Retraso de apagado en segundos")

    # Criticidad
    is_critical = Column(Boolean, default=False, nullable=False,
                         comment="Si es un equipo crítico")

    # Metadatos
    notes = Column(Text, nullable=True,
                   comment="Notas adicionales")

    # Relaciones
    fuente_poder = relationship("FuentePoder", back_populates="connected_equipment")

    def __repr__(self):
        return f"<FuentePoderConnection(fuente={self.fuente_poder_id}, equipment={self.connected_equipment_type}_{self.connected_equipment_id})>"

    @classmethod
    def get_by_fuente_poder(cls, fuente_poder_id):
        """
        Obtiene las conexiones de una fuente de poder.

        Args:
        fuente_poder_id (int): ID de la fuente de poder

        Returns:
        list: Lista de conexiones
        """
        return cls.query.filter_by(fuente_poder_id=fuente_poder_id, deleted=False).all()

    @classmethod
    def get_by_equipment(cls, equipment_id, equipment_type):
        """
        Obtiene las conexiones de un equipo específico.

        Args:
        equipment_id (int): ID del equipo
        equipment_type (str): Tipo del equipo

        Returns:
        list: Lista de conexiones del equipo
        """
        return cls.query.filter_by(
            connected_equipment_id=equipment_id,
            connected_equipment_type=equipment_type,
            deleted=False
        ).all()