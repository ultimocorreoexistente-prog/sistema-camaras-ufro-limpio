"""
Modelo de fuentes de poder (Power Supplies).

Incluye gestión de fuentes de alimentación para equipos diversos.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models.equipo import EquipmentBase
from models import db, EquipmentStatus
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


class FuentePoder(EquipmentBase):
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

    # ✅ Corrección crítica: indentación y primary key
    id = Column(Integer, primary_key=True)

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
    efficiency_rating = Column(String(20), nullable=True,  # ✅ Corregido String(20) → String(20)
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
    color = Column(String(50), nullable=True,  # ✅ Corregido String(20) → String(50)
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
    model_version = Column(String(20), nullable=True,  # ✅ Corregido String(20) → String(20)
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
        """Calcula la utilización de la capacidad."""
        if not self.max_output_watts or self.max_output_watts == 0:
            return 0
        return min(100, max(0, (self.current_output_watts / self.max_output_watts) * 100))

    def get_system_health_score(self):
        """Calcula un puntaje de salud del sistema (0-100)."""
        score = 100

        if self.psu_status == PSUStatus.ERROR:
            score -= 40
        elif self.psu_status == PSUStatus.WARNING:
            score -= 20

        if self.temperature_celsius and self.temperature_celsius > 80:
            score -= 30
        elif self.temperature_celsius and self.temperature_celsius > 70:
            score -= 15

        if self.load_percentage > 95:
            score -= 30
        elif self.load_percentage > 85:
            score -= 15

        if self.is_maintenance_due():
            score -= 10

        # ✅ Corregido: comparación, no asignación
        if hasattr(self, 'status') and self.status != EquipmentStatus.ACTIVO.value:
            score -= 10

        return max(0, min(100, score))

    def is_maintenance_due(self):
        if not self.next_maintenance:
            return False
        return datetime.utcnow() >= self.next_maintenance

    def update_power_consumption(self):
        total_consumption = sum([conn.power_consumption for conn in self.connected_equipment])
        self.current_output_watts = total_consumption
        self.load_percentage = self.get_capacity_utilization()

        if self.load_percentage > 90 or (self.temperature_celsius and self.temperature_celsius > 80):
            self.psu_status = PSUStatus.ERROR
        elif self.load_percentage > 75 or (self.temperature_celsius and self.temperature_celsius > 70):
            self.psu_status = PSUStatus.WARNING
        else:
            self.psu_status = PSUStatus.NORMAL

        db.session.commit()

    def perform_self_test(self):
        self.self_test_enabled = True
        self.last_heartbeat = datetime.utcnow()
        db.session.commit()
        return True


class FuentePoderConnection(BaseModel, db.Model):
    """
    Modelo de equipos conectados a fuentes de poder.
    """

    __tablename__ = 'fuente_poder_connections'

    # ✅ Corrección crítica: indentación y primary key
    id = Column(Integer, primary_key=True)

    fuente_poder_id = Column(Integer, ForeignKey('fuentes_poder.id'), nullable=False,
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
    priority_level = Column(Integer, default=2, nullable=False,  # ✅ Corregido default=, → default=2
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