"""
Modelo de UPS (Uninterruptible Power Supply).

Incluye gestión de sistemas de alimentación ininterrumpida y monitoreo de baterías.
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.base import db, TimestampedModel
from models.equipo import EquipmentBase
from models.enums.equipment_status import EquipmentStatus
import enum


class UPSType(enum.Enum):
    """Tipos de UPS."""
    ONLINE = "online"
    LINE_INTERACTIVE = "line_interactive"
    OFFLINE = "offline"
    DOUBLE_CONVERSION = "double_conversion"
    FERRORESONANT = "ferroresonant"


class BatteryType(enum.Enum):
    """Tipos de baterías."""
    LEAD_ACID = "lead_acid"
    LITHIUM_ION = "lithium_ion"
    NICKEL_CADMIUM = "nickel_cadmium"
    VRLA = "vrla"
    AGM = "agm"
    GEL = "gel"


class LoadStatus(enum.Enum):
    """Estados de carga."""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


class UPS(EquipmentBase, db.Model, TimestampedModel):
    """
    Modelo de UPS (Uninterruptible Power Supply).

    Attributes:
    ups_type (str): Tipo de UPS
    capacity_va (int): Capacidad en Volt-Amperios
    capacity_watts (int): Capacidad en Watts
    input_voltage (float): Voltaje de entrada
    input_frequency (float): Frecuencia de entrada
    output_voltage (float): Voltaje de salida
    output_frequency (float): Frecuencia de salida
    battery_type (str): Tipo de batería
    battery_capacity (int): Capacidad de batería en Ah
    battery_count (int): Número de baterías
    battery_age_months (int): Edad de las baterías en meses
    runtime_minutes (int): Tiempo de autonomía en minutos
    load_percentage (float): Porcentaje de carga actual
    load_status (str): Estado de la carga
    battery_voltage (float): Voltaje de batería
    battery_current (float): Corriente de batería
    battery_temperature (float): Temperatura de batería
    battery_health_percentage (float): Salud de la batería (0-100)
    last_battery_test (datetime): Última prueba de batería
    next_battery_test (datetime): Próxima prueba de batería
    automatic_battery_test (bool): Pruebas automáticas habilitadas
    transfer_time_ms (int): Tiempo de transferencia en milisegundos
    input_connection_type (str): Tipo de conexión de entrada
    output_connection_type (str): Tipo de conexión de salida
    output_outlets (int): Número de salidas (tomacorrientes)
    managed_outlets (int): Número de salidas gestionables
    snmp_enabled (bool): SNMP habilitado
    snmp_community (str): Comunidad SNMP
    monitoring_port (int): Puerto de monitoreo
    remote_monitoring_enabled (bool): Monitoreo remoto habilitado
    shutdown_software_installed (bool): Software de apagado instalado
    maintenance_bypass (bool): Bypass de mantenimiento disponible
    external_battery_packs (int): Número de paquetes de baterías externas
    environmental_monitoring (bool): Monitoreo ambiental habilitado
    redundancy_configured (bool): Configuración de redundancia
    serial_communication (bool): Comunicación serie disponible
    relay_output (bool): Salida de relés disponible
    current_load_watts (float): Carga actual en Watts
    current_load_va (float): Carga actual en VA
    power_factor (float): Factor de potencia
    efficiency_percentage (float): Eficiencia del UPS
    heat_output_btu (float): Generación de calor en BTU/h
    cooling_fan_status (str): Estado del ventilador de refrigeración
    alarm_settings (str): Configuraciones de alarma en JSON
    """

    __tablename__ = 'ups'

    # Configuración del UPS
    ups_type = Column(Enum(UPSType), nullable=True,
                      comment="Tipo de UPS")
    capacity_va = Column(Integer, nullable=True,
                         comment="Capacidad en Volt-Amperios (VA)")
    capacity_watts = Column(Integer, nullable=True,
                            comment="Capacidad en Watts")

    # Especificaciones eléctricas de entrada
    input_voltage = Column(Float, nullable=True,
                           comment="Voltaje de entrada en volts")
    input_frequency = Column(Float, nullable=True,
                             comment="Frecuencia de entrada en Hz")

    # Especificaciones eléctricas de salida
    output_voltage = Column(Float, nullable=True,
                            comment="Voltaje de salida en volts")
    output_frequency = Column(Float, nullable=True,
                              comment="Frecuencia de salida en Hz")

    # Configuración de baterías
    battery_type = Column(Enum(BatteryType), nullable=True,
                          comment="Tipo de batería")
    battery_capacity = Column(Integer, nullable=True,
                              comment="Capacidad de batería en Ah")
    battery_count = Column(Integer, default=1, nullable=False,
                           comment="Número de baterías")
    battery_age_months = Column(Integer, nullable=True,
                                comment="Edad de las baterías en meses")
    runtime_minutes = Column(Integer, nullable=True,
                             comment="Tiempo de autonomía en minutos")

    # Estado actual
    load_percentage = Column(Float, default=0.0, nullable=False,
                             comment="Porcentaje de carga actual")
    load_status = Column(Enum(LoadStatus), default=LoadStatus.NORMAL, nullable=False,
                         comment="Estado de la carga")
    battery_voltage = Column(Float, nullable=True,
                             comment="Voltaje de batería en volts")
    battery_current = Column(Float, nullable=True,
                             comment="Corriente de batería en amperios")
    battery_temperature = Column(Float, nullable=True,
                                 comment="Temperatura de batería en °C")
    battery_health_percentage = Column(Float, default=100.0, nullable=False,
                                        comment="Salud de la batería (0-100%)")

    # Pruebas de batería
    last_battery_test = Column(DateTime, nullable=True,
                               comment="Fecha y hora de última prueba de batería")
    next_battery_test = Column(DateTime, nullable=True,
                               comment="Fecha y hora de próxima prueba de batería")
    automatic_battery_test = Column(Boolean, default=True, nullable=False,
                                    comment="Pruebas automáticas de batería habilitadas")

    # Tiempo de transferencia
    transfer_time_ms = Column(Integer, nullable=True,
                              comment="Tiempo de transferencia en milisegundos")

    # Conexiones
    input_connection_type = Column(String(30), nullable=True,
                                   comment="Tipo de conexión de entrada")
    output_connection_type = Column(String(30), nullable=True,
                                    comment="Tipo de conexión de salida")
    output_outlets = Column(Integer, default=0, nullable=False,
                            comment="Número de salidas (tomacorrientes)")
    managed_outlets = Column(Integer, default=0, nullable=False,
                             comment="Número de salidas gestionables")

    # Comunicación y monitoreo
    snmp_enabled = Column(Boolean, default=False, nullable=False,
                          comment="SNMP habilitado")
    snmp_community = Column(String(50), nullable=True,
                            comment="Comunidad SNMP")
    monitoring_port = Column(Integer, nullable=True,
                             comment="Puerto de monitoreo")
    remote_monitoring_enabled = Column(Boolean, default=False, nullable=False,
                                        comment="Monitoreo remoto habilitado")

    # Software y características avanzadas
    shutdown_software_installed = Column(Boolean, default=False, nullable=False,
                                         comment="Software de apagado instalado")
    maintenance_bypass = Column(Boolean, default=False, nullable=False,
                                comment="Bypass de mantenimiento disponible")
    external_battery_packs = Column(Integer, default=0, nullable=False,
                                    comment="Número de paquetes de baterías externas")
    environmental_monitoring = Column(Boolean, default=False, nullable=False,
                                      comment="Monitoreo ambiental habilitado")
    redundancy_configured = Column(Boolean, default=False, nullable=False,
                                   comment="Configuración de redundancia")
    serial_communication = Column(Boolean, default=False, nullable=False,
                                  comment="Comunicación serie disponible")
    relay_output = Column(Boolean, default=False, nullable=False,
                          comment="Salida de relés disponible")

    # Métricas actuales
    current_load_watts = Column(Float, default=0.0, nullable=False,
                                comment="Carga actual en Watts")
    current_load_va = Column(Float, default=0.0, nullable=False,
                             comment="Carga actual en VA")
    power_factor = Column(Float, default=1.0, nullable=False,
                          comment="Factor de potencia")
    efficiency_percentage = Column(Float, default=95.0, nullable=False,
                                   comment="Eficiencia del UPS (%)")
    heat_output_btu = Column(Float, nullable=True,
                             comment="Generación de calor en BTU/h")

    # Estado del sistema
    cooling_fan_status = Column(String(50), nullable=True,
                                comment="Estado del ventilador de refrigeración")

    # Configuración avanzada
    alarm_settings = Column(Text, nullable=True,
                            comment="Configuraciones de alarma en formato JSON")

    # Relaciones
    ubicacion = relationship("Ubicacion", back_populates="ups_devices")
    created_by_user = relationship("Usuario", back_populates="created_equipos")

    # Relaciones con otros modelos
    mantenimientos = relationship("Mantenimiento", back_populates="ups", cascade="all, delete-orphan")

    fotografias = relationship("Fotografia", back_populates="ups", cascade="all, delete-orphan")

    # Relaciones con cargas conectadas
    connected_loads = relationship("UPSConnectedLoad", back_populates="ups", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UPS(name='{self.name}', capacity='{self.capacity_va}VA', load='{self.load_percentage}%')>"

    def get_capacity_watts_estimated(self):
        """
        Estima la capacidad en watts basada en VA.

        Returns:
            int: Capacidad estimada en watts
        """
        if self.capacity_watts:
            return self.capacity_watts
        elif self.capacity_va:
            # Estimación típica: 0.9 * VA = watts
            return int(self.capacity_va * 0.9)
        return None

    def get_current_runtime_estimate(self):
        """
        Estima el tiempo de autonomía actual basado en la carga.

        Returns:
            int: Tiempo estimado en minutos
        """
        if not self.runtime_minutes or self.load_percentage == 0:
            return 0

        # La autonomía disminuye con la carga
        # A carga completa: 100% del tiempo estimado
        # A 50% de carga: aproximadamente 150% del tiempo estimado
        load_factor = 1 + (0.5 * (1 - self.load_percentage / 100))
        estimated_runtime = int(self.runtime_minutes * load_factor)

        return max(1, estimated_runtime)  # Mínimo 1 minuto

    def get_battery_status(self):
        """
        Obtiene el estado general de las baterías.

        Returns:
            str: Estado de la batería (excellent, good, warning, critical)
        """
        if self.battery_health_percentage >= 90:
            return "excellent"
        elif self.battery_health_percentage >= 75:
            return "good"
        elif self.battery_health_percentage >= 50:
            return "warning"
        else:
            return "critical"

    def get_load_status_color(self):
        """
        Obtiene el color para el estado de la carga.

        Returns:
            str: Código de color
        """
        colors = {
            LoadStatus.NORMAL: "#28a745",  # Verde
            LoadStatus.WARNING: "#ffc107",  # Amarillo
            LoadStatus.CRITICAL: "#dc3545"  # Rojo
        }
        return colors.get(self.load_status, "#6c757d")  # Gris por defecto

    def is_battery_test_due(self):
        """
        Verifica si es momento de hacer una prueba de batería.

        Returns:
            bool: True si la prueba está vencida
        """
        if not self.next_battery_test:
            return False

        return datetime.utcnow() >= self.next_battery_test

    def get_estimated_battery_replacement_date(self):
        """
        Estima la fecha de reemplazo de baterías.

        Returns:
            datetime: Fecha estimada de reemplazo o None
        """
        if not self.battery_age_months:
            return None

        # Reemplazo típico cada 3-5 años para baterías lead-acid
        if self.battery_type == BatteryType.LEAD_ACID:
            replacement_age = 48  # 4 años
        elif self.battery_type == BatteryType.LITHIUM_ION:
            replacement_age = 120  # 10 años
        else:
            replacement_age = 60  # 5 años por defecto

        if self.battery_age_months >= replacement_age:
            return datetime.utcnow()

        remaining_months = replacement_age - self.battery_age_months
        return datetime.utcnow() + timedelta(days=remaining_months * 30)

    def add_connected_load(self, equipment, equipment_type, watts_consumption):
        """
        Agrega una carga conectada al UPS.

        Args:
            equipment: Equipo conectado
            equipment_type (str): Tipo del equipo
            watts_consumption (float): Consumo en watts

        Returns:
            UPSConnectedLoad: Carga creada
        """
        load = UPSConnectedLoad(
            ups_id=self.id,
            connected_equipment_id=equipment.id,
            connected_equipment_type=equipment_type,
            watts_consumption=watts_consumption
        )
        db.session.add(load)
        db.session.commit()
        return load

    def get_total_connected_load(self):
        """
        Obtiene la carga total conectada.

        Returns:
            float: Carga total en watts
        """
        return sum([load.watts_consumption for load in self.connected_loads])

    def update_load_status(self):
        """
        Actualiza el estado de carga basado en el porcentaje.
        """
        if self.load_percentage < 70:
            self.load_status = LoadStatus.NORMAL
        elif self.load_percentage < 90:
            self.load_status = LoadStatus.WARNING
        else:
            self.load_status = LoadStatus.CRITICAL

        db.session.commit()

    def perform_battery_test(self):
        """
        Realiza una prueba de batería.

        Returns:
            bool: True si la prueba se inició exitosamente
        """
        self.last_battery_test = datetime.utcnow()

        # Programar próxima prueba (típicamente mensual)
        self.next_battery_test = self.last_battery_test + timedelta(days=30)

        db.session.commit()
        return True

    def get_system_health_score(self):
        """
        Calcula un puntaje de salud del sistema (0-100).

        Returns:
            int: Puntaje de salud del sistema
        """
        score = 100

        # Penalizar por batería en mal estado
        if self.battery_health_percentage < 50:
            score -= 40
        elif self.battery_health_percentage < 75:
            score -= 20

        # Penalizar por carga crítica
        if self.load_status == LoadStatus.CRITICAL:
            score -= 30
        elif self.load_status == LoadStatus.WARNING:
            score -= 15

        # Penalizar por batería vencida para prueba
        if self.is_battery_test_due():
            score -= 10

        # Penalizar por estado del equipo
        if hasattr(self, 'status') and self.status != EquipmentStatus.ACTIVO.value:
            score -= 10

        # Penalizar por falta de heartbeat reciente
        if hasattr(self, 'is_online') and not self.is_online():
            score -= 5

        return max(0, min(100, score))

    def get_power_estimate_summary(self):
        """
        Obtiene un resumen de estimaciones de potencia.

        Returns:
            dict: Resumen de potencia
        """
        capacity_watts = self.get_capacity_watts_estimated()
        total_load = self.get_total_connected_load()
        available_watts = capacity_watts - total_load if capacity_watts else 0

        return {
            'capacity_va': self.capacity_va,
            'capacity_watts': capacity_watts,
            'current_load_watts': self.current_load_watts,
            'connected_load_watts': total_load,
            'available_watts': available_watts,
            'load_percentage': self.load_percentage,
            'runtime_estimate_minutes': self.get_current_runtime_estimate(),
            'battery_health': self.battery_health_percentage
        }

    @classmethod
    def get_by_capacity_range(cls, min_va, max_va):
        """
        Obtiene UPSs por rango de capacidad.

        Args:
            min_va (int): Capacidad mínima en VA
            max_va (int): Capacidad máxima en VA

        Returns:
            list: Lista de UPSs que cumplen el criterio
        """
        return cls.query.filter(
            cls.capacity_va >= min_va,
            cls.capacity_va <= max_va,
            cls.deleted == False
        ).all()

    @classmethod
    def get_critical_batteries(cls):
        """
        Obtiene UPSs con baterías en estado crítico.

        Returns:
            list: Lista de UPSs con baterías críticas
        """
        return cls.query.filter(
            cls.battery_health_percentage < 50,
            cls.deleted == False
        ).all()

    @classmethod
    def get_high_load_ups(cls):
        """
        Obtiene UPSs con alta carga (>85%).

        Returns:
            list: Lista de UPSs con alta carga
        """
        return cls.query.filter(
            cls.load_percentage > 85,
            cls.deleted == False
        ).all()


class UPSConnectedLoad(db.Model, TimestampedModel):
    """
    Modelo de cargas conectadas a UPSs.

    Attributes:
    ups_id (int): ID del UPS
    connected_equipment_id (int): ID del equipo conectado
    connected_equipment_type (str): Tipo del equipo conectado
    watts_consumption (float): Consumo en watts
    priority_level (int): Nivel de prioridad (1=alta, 2=media, 3=baja)
    controlled_outlet (bool): Si está en una salida controlada
    shutdown_sequence (int): Secuencia de apagado
    startup_delay (int): Retraso de encendido en minutos
    notes (str): Notas adicionales
    """

    __tablename__ = 'ups_connected_loads'

    id = Column(Integer, primary_key=True)

    ups_id = Column(Integer, ForeignKey('ups.id'), nullable=False,
                    comment="ID del UPS")
    connected_equipment_id = Column(Integer, nullable=True,
                                    comment="ID del equipo conectado")
    connected_equipment_type = Column(String(30), nullable=True,
                                      comment="Tipo del equipo conectado")
    watts_consumption = Column(Float, default=0.0, nullable=False,
                               comment="Consumo en watts")

    # Configuración de gestión
    priority_level = Column(Integer, default=2, nullable=False,
                            comment="Nivel de prioridad (1=alta, 2=media, 3=baja)")
    controlled_outlet = Column(Boolean, default=False, nullable=False,
                               comment="Si está conectado a salida controlada")
    shutdown_sequence = Column(Integer, nullable=True,
                               comment="Secuencia de apagado")
    startup_delay = Column(Integer, default=0, nullable=False,
                           comment="Retraso de encendido en minutos")

    # Metadatos
    notes = Column(Text, nullable=True,
                    comment="Notas adicionales")

    # Relaciones
    ups = relationship("UPS", back_populates="connected_loads")

    def __repr__(self):
        return f"<UPSConnectedLoad(ups={self.ups_id}, equipment={self.connected_equipment_type}_{self.connected_equipment_id})>"

    @classmethod
    def get_by_ups(cls, ups_id):
        """
        Obtiene las cargas conectadas a un UPS.

        Args:
            ups_id (int): ID del UPS

        Returns:
            list: Lista de cargas conectadas
        """
        return cls.query.filter_by(ups_id=ups_id, deleted=False).all()

    @classmethod
    def get_by_equipment(cls, equipment_id, equipment_type):
        """
        Obtiene las cargas de un equipo específico.

        Args:
            equipment_id (int): ID del equipo
            equipment_type (str): Tipo del equipo

        Returns:
            list: Lista de cargas del equipo
        """
        return cls.query.filter_by(
            connected_equipment_id=equipment_id,
            connected_equipment_type=equipment_type,
            deleted=False
        ).all()
