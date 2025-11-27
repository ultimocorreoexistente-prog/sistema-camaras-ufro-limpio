"""
Modelo de switches de red.

Incluye gestión de switches, puertos, VLANs y configuraciones de red.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.base import db, EquipmentStatus, BaseModel, EquipmentBase
from models import db
import enum


class SwitchType(enum.Enum):
    """Tipos de switches."""
    ACCESS = "access"
    DISTRIBUTION = "distribution"
    CORE = "core"
    AGGREGATION = "aggregation"
    EDGE = "edge"


class PortType(enum.Enum):
    """Tipos de puertos."""
    ETHERNET = "ethernet"
    GIGABIT = "gigabit"
    TEN_GIGABIT = "ten_gigabit"
    FIBER = "fiber"
    SFP = "sfp"
    SFP_PLUS = "sfp_plus"
    COMBO = "combo"


class PortStatus(enum.Enum):
    """Estados de puertos."""
    UP = "up"
    DOWN = "down"
    DISABLED = "disabled"
    ERROR = "error"


class VLANType(enum.Enum):
    """Tipos de VLAN."""
    DEFAULT = "default"
    VOICE = "voice"
    GUEST = "guest"
    MANAGEMENT = "management"
    IOT = "iot"
    DATA = "data"


class Switch(EquipmentBase):
    """
    Modelo de switches de red.

    Attributes:
    switch_type (str): Tipo de switch
    total_ports (int): Número total de puertos
    poe_ports (int): Número de puertos PoE
    max_poe_power (int): Potencia máxima PoE en watts
    port_speed (str): Velocidad de puertos (ej: 1Gbps, 10Gbps)
    fiber_ports (int): Número de puertos de fibra
    stackable (bool): Si es apilable
    stacking_ports (int): Número de puertos de stacking
    management_protocols (str): Protocolos de gestión soportados (JSON)
    snmp_community (str): Comunidad SNMP
    vlan_support (bool): Soporte para VLANs
    qos_support (bool): Soporte para QoS
    poe_plus_support (bool): Soporte para PoE+
    managed (bool): Si es administrable
    layer_support (str): Capa OSI soportada (L, L3, L4)
    mac_address_table_size (int): Tamaño de tabla MAC
    forwarding_rate (int): Tasa de reenvío en Mpps
    switching_capacity (int): Capacidad de conmutación en Gbps
    redundancy_support (bool): Soporte para redundancia
    stack_id (int): ID del stack
    stack_master (bool): Si es el maestro del stack
    firmware_url (str): URL de firmware
    configuration_template (str): Plantilla de configuración
    backup_configuration (str): Respaldo de configuración
    monitoring_enabled (bool): Monitoreo habilitado
    alerting_enabled (bool): Alertas habilitadas
    auto_negotiation (bool): Negociación automática habilitada
    storm_control (bool): Control de tormentas habilitado
    spanning_tree_enabled (bool): Spanning Tree habilitado
    """

    __tablename__ = 'switches'

    # Configuración del switch
    switch_type = Column(Enum(SwitchType), nullable=True,
                         comment="Tipo de switch")
    total_ports = Column(Integer, nullable=False, default=0,
                         comment="Número total de puertos")
    poe_ports = Column(Integer, default=0, nullable=False,
                       comment="Número de puertos PoE")
    max_poe_power = Column(Integer, nullable=True,
                           comment="Potencia máxima PoE en watts")
    port_speed = Column(String(20), nullable=True,
                        comment="Velocidad de puertos (ej: 1Gbps)")

    # Puertos especializados
    fiber_ports = Column(Integer, default=0, nullable=False,
                         comment="Número de puertos de fibra")
    stackable = Column(Boolean, default=False, nullable=False,
                       comment="Si el switch es apilable")
    stacking_ports = Column(Integer, default=0, nullable=False,
                            comment="Número de puertos de stacking")

    # Configuración de gestión
    management_protocols = Column(Text, nullable=True,
                                  comment="Protocolos de gestión soportados (JSON)")
    snmp_community = Column(String(50), nullable=True,
                            comment="Comunidad SNMP")

    # Características avanzadas
    vlan_support = Column(Boolean, default=True, nullable=False,
                          comment="Soporte para VLANs")
    qos_support = Column(Boolean, default=True, nullable=False,
                         comment="Soporte para QoS")
    poe_plus_support = Column(Boolean, default=False, nullable=False,
                               comment="Soporte para PoE+")
    managed = Column(Boolean, default=True, nullable=False,
                     comment="Si el switch es administrable")
    layer_support = Column(String(10), nullable=True,
                           comment="Capa OSI soportada (L/L3/L4)")

    # Capacidades
    mac_address_table_size = Column(Integer, nullable=True,
                                    comment="Tamaño de tabla MAC")
    forwarding_rate = Column(Integer, nullable=True,
                             comment="Tasa de reenvío en Mpps")
    switching_capacity = Column(Integer, nullable=True,
                                comment="Capacidad de conmutación en Gbps")

    # Redundancia y stacking
    redundancy_support = Column(Boolean, default=False, nullable=False,
                                comment="Soporte para redundancia")
    stack_id = Column(Integer, nullable=True,
                      comment="ID del stack al que pertenece")
    stack_master = Column(Boolean, default=False, nullable=False,
                          comment="Si es el switch maestro del stack")

    # Configuración y firmware
    firmware_url = Column(String(500), nullable=True,
                          comment="URL de firmware")
    configuration_template = Column(Text, nullable=True,
                                    comment="Plantilla de configuración")
    backup_configuration = Column(Text, nullable=True,
                                  comment="Respaldo de configuración")

    # Monitoreo y seguridad
    monitoring_enabled = Column(Boolean, default=True, nullable=False,
                                comment="Monitoreo habilitado")
    alerting_enabled = Column(Boolean, default=True, nullable=False,
                              comment="Alertas habilitadas")
    auto_negotiation = Column(Boolean, default=True, nullable=False,
                              comment="Negociación automática habilitada")
    storm_control = Column(Boolean, default=False, nullable=False,
                           comment="Control de tormentas habilitado")
    spanning_tree_enabled = Column(Boolean, default=True, nullable=False,
                                   comment="Spanning Tree Protocol habilitado")

    # Relaciones
    ubicacion = relationship("Ubicacion", back_populates="switches")
    created_by_user = relationship("Usuario", back_populates="created_equipos")

    # Relaciones con otros modelos
    mantenimientos = relationship("Mantenimiento", back_populates="switch", cascade="all, delete-orphan")
    fotografias = relationship("Fotografia", back_populates="switch", cascade="all, delete-orphan")

    # Relaciones con puertos y VLANs
    puertos = relationship("SwitchPort", back_populates="switch", cascade="all, delete-orphan")
    vlans = relationship("SwitchVLAN", back_populates="switch", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Switch(name='{self.name}', type='{self.switch_type.value if self.switch_type else 'N/A'}', ports={self.total_ports})>"

    def get_available_ports(self):
        """
        Obtiene el número de puertos disponibles.

        Returns:
            int: Número de puertos disponibles
        """
        used_ports = len([p for p in self.puertos if not p.is_available()])
        return self.total_ports - used_ports

    def can_add_connection(self):
        """
        Verifica si se puede agregar otra conexión.

        Returns:
            bool: True si se puede agregar conexión
        """
        return self.get_available_ports() > 0

    def add_port(self, port_number, port_type=PortType.ETHERNET, **kwargs):
        """
        Agrega un puerto al switch.

        Args:
            port_number (int): Número del puerto
            port_type (PortType): Tipo de puerto
            **kwargs: Parámetros adicionales

        Returns:
            SwitchPort: Puerto creado
        """
        if not self.can_add_connection():
            return None

        port = SwitchPort(
            switch_id=self.id,
            port_number=port_number,
            port_type=port_type,
            **kwargs
        )
        db.session.add(port)
        db.session.commit()
        return port

    def get_port_utilization_percentage(self):
        """
        Calcula el porcentaje de utilización de puertos.

        Returns:
            float: Porcentaje de utilización (0-100)
        """
        if self.total_ports == 0:
            return 0

        used_ports = len([p for p in self.puertos if not p.is_available()])
        return round((used_ports / self.total_ports) * 100, 2)

    def get_poe_power_usage(self):
        """
        Obtiene el uso actual de potencia PoE.

        Returns:
            float: Potencia utilizada en watts
        """
        return sum([p.poe_power_consumption for p in self.puertos if p.poe_power_consumption])

    def get_poe_power_available(self):
        """
        Obtiene la potencia PoE disponible.

        Returns:
            float: Potencia disponible en watts
        """
        if not self.max_poe_power:
            return 0

        used_power = self.get_poe_power_usage()
        return self.max_poe_power - used_power

    def get_active_ports_count(self):
        """
        Obtiene el número de puertos activos.

        Returns:
            int: Número de puertos activos
        """
        return len([p for p in self.puertos if p.status == PortStatus.UP])

    def get_ports_summary(self):
        """
        Obtiene un resumen de los puertos del switch.

        Returns:
            dict: Resumen de puertos
        """
        total = len(self.puertos)
        active = 0
        down = 0
        disabled = 0
        error = 0

        for port in self.puertos:
            if port.status == PortStatus.UP:
                active += 1
            elif port.status == PortStatus.DOWN:
                down += 1
            elif port.status == PortStatus.DISABLED:
                disabled += 1
            elif port.status == PortStatus.ERROR:
                error += 1

        return {
            'total': total,
            'active': active,
            'down': down,
            'disabled': disabled,
            'error': error,
            'utilization_percentage': self.get_port_utilization_percentage()
        }

    def get_vlans_summary(self):
        """
        Obtiene un resumen de las VLANs configuradas.

        Returns:
            dict: Resumen de VLANs
        """
        total_vlans = len(self.vlans)
        native_vlans = len([v for v in self.vlans if v.is_native])
        tagged_vlans = len([v for v in self.vlans if v.is_tagged])

        return {
            'total': total_vlans,
            'native': native_vlans,
            'tagged': tagged_vlans
        }

    def get_network_topology_summary(self):
        """
        Obtiene un resumen de la topología de red del switch.

        Returns:
            dict: Resumen de topología
        """
        ports_summary = self.get_ports_summary()
        vlans_summary = self.get_vlans_summary()

        return {
            'switch_health_score': self.get_system_health_score(),
            'ports': ports_summary,
            'vlans': vlans_summary,
            'stacking': {
                'is_stackable': self.stackable,
                'stack_id': self.stack_id,
                'is_master': self.stack_master
            },
            'capabilities': {
                'vlan_support': self.vlan_support,
                'qos_support': self.qos_support,
                'poe_support': self.poe_ports > 0,
                'redundancy': self.redundancy_support,
                'layer_support': self.layer_support
            }
        }

    def get_system_health_score(self):
        """
        Calcula un puntaje de salud del sistema (0-100).

        Returns:
            int: Puntaje de salud del sistema
        """
        score = 100

        # Penalizar por puertos en error
        error_ports = len([p for p in self.puertos if p.status == PortStatus.ERROR])
        score -= (error_ports * 15)

        # Penalizar por puertos down
        down_ports = len([p for p in self.puertos if p.status == PortStatus.DOWN])
        score -= (down_ports * 5)

        # Penalizar por utilización alta de puertos
        port_utilization = self.get_port_utilization_percentage()
        if port_utilization > 90:
            score -= 20
        elif port_utilization > 80:
            score -= 10

        # Comparación corregida
        if hasattr(self, 'status') and self.status != EquipmentStatus.ACTIVO:
            score -= 10

        # Penalizar por falta de heartbeat reciente
        if hasattr(self, 'is_online') and not self.is_online():
            score -= 5

        return max(0, min(100, score))

    def configure_vlan(self, vlan_id, vlan_name, vlan_type=VLANType.DATA, **kwargs):
        """
        Configura una VLAN en el switch.

        Args:
            vlan_id (int): ID de la VLAN
            vlan_name (str): Nombre de la VLAN
            vlan_type (VLANType): Tipo de VLAN
            **kwargs: Parámetros adicionales

        Returns:
            SwitchVLAN: VLAN creada
        """
        vlan = SwitchVLAN(
            switch_id=self.id,
            vlan_id=vlan_id,
            vlan_name=vlan_name,
            vlan_type=vlan_type,
            **kwargs
        )
        db.session.add(vlan)
        db.session.commit()
        return vlan

    @classmethod
    def get_by_type(cls, switch_type):
        """
        Obtiene switches de un tipo específico.

        Args:
            switch_type (SwitchType): Tipo de switch

        Returns:
            list: Lista de switches del tipo especificado
        """
        return cls.query.filter_by(switch_type=switch_type, deleted=False).all()

    @classmethod
    def get_available_for_connections(cls):
        """
        Obtiene switches disponibles para nuevas conexiones.

        Returns:
            list: Lista de switches con puertos disponibles
        """
        switches = cls.query.filter_by(
            status=EquipmentStatus.ACTIVO,
            deleted=False
        ).all()

        available = []
        for switch in switches:
            if switch.can_add_connection():
                available.append(switch)

        return available

    @classmethod
    def get_stack_members(cls, stack_id):
        """
        Obtiene los miembros de un stack.

        Args:
            stack_id (int): ID del stack

        Returns:
            list: Lista de switches del stack
        """
        return cls.query.filter_by(stack_id=stack_id, deleted=False).all()

    @classmethod
    def get_stack_masters(cls):
        """
        Obtiene todos los switches maestros de stack.

        Returns:
            list: Lista de switches maestros
        """
        return cls.query.filter_by(stack_master=True, deleted=False).all()


class SwitchPort(BaseModel):
    """
    Modelo de puertos de switch.

    Attributes:
    switch_id (int): ID del switch
    port_number (int): Número de puerto
    port_type (str): Tipo de puerto
    status (str): Estado del puerto
    description (str): Descripción del puerto
    connected_equipment_id (int): ID del equipo conectado
    connected_equipment_type (str): Tipo del equipo conectado
    vlan_id (int): ID de la VLAN asignada
    speed (str): Velocidad del puerto
    duplex (str): Modo duplex (full/half/auto)
    poe_enabled (bool): PoE habilitado
    poe_power_consumption (float): Consumo de energía PoE
    error_count (int): Número de errores
    utilization_percentage (float): Porcentaje de utilización
    last_activity (datetime): Última actividad
    """

    __tablename__ = 'switch_ports'

    switch_id = Column(Integer, ForeignKey('switches.id'), nullable=False,
                       comment="ID del switch")
    port_number = Column(Integer, nullable=False,
                         comment="Número de puerto físico")
    port_type = Column(Enum(PortType), nullable=False,
                       comment="Tipo de puerto")
    status = Column(Enum(PortStatus), default=PortStatus.DOWN, nullable=False,
                    comment="Estado actual del puerto")

    # Configuración
    description = Column(String(100), nullable=True,
                         comment="Descripción del puerto")
    connected_equipment_id = Column(Integer, nullable=True,
                                    comment="ID del equipo conectado")
    connected_equipment_type = Column(String(30), nullable=True,
                                      comment="Tipo del equipo conectado")
    vlan_id = Column(Integer, nullable=True,
                     comment="ID de la VLAN asignada")

    # Configuración de velocidad
    speed = Column(String(20), nullable=True,
                   comment="Velocidad del puerto (ej: 1Gbps)")
    duplex = Column(String(10), nullable=True,
                    comment="Modo duplex (full/half/auto)")

    # PoE
    poe_enabled = Column(Boolean, default=False, nullable=False,
                         comment="Power over Ethernet habilitado")
    poe_power_consumption = Column(Float, default=0.0, nullable=False,
                                   comment="Consumo de energía PoE en watts")

    # Métricas
    error_count = Column(Integer, default=0, nullable=False,
                         comment="Número de errores en el puerto")
    utilization_percentage = Column(Float, default=0.0, nullable=False,
                                    comment="Porcentaje de utilización")
    last_activity = Column(DateTime, nullable=True,
                           comment="Fecha y hora de última actividad")

    # Relaciones
    switch = relationship("Switch", back_populates="puertos")

    def __repr__(self):
        return f"<SwitchPort(switch={self.switch_id}, port={self.port_number})>"

    def is_available(self):
        """
        Verifica si el puerto está disponible para conectar.

        Returns:
            bool: True si el puerto está disponible
        """
        return (self.status == PortStatus.DOWN and
                not self.connected_equipment_id and
                self.port_type in [PortType.ETHERNET, PortType.GIGABIT])

    def connect_equipment(self, equipment, equipment_type):
        """
        Conecta un equipo al puerto.

        Args:
            equipment: Equipo a conectar
            equipment_type (str): Tipo del equipo

        Returns:
            bool: True si se conectó exitosamente
        """
        if not self.is_available():
            return False

        self.connected_equipment_id = equipment.id
        self.connected_equipment_type = equipment_type
        self.status = PortStatus.UP
        self.last_activity = datetime.utcnow()
        db.session.commit()

        return True

    def disconnect_equipment(self):
        """
        Desconecta el equipo del puerto.

        Returns:
            bool: True si se desconectó exitosamente
        """
        self.connected_equipment_id = None
        self.connected_equipment_type = None
        self.status = PortStatus.DOWN
        self.last_activity = None
        db.session.commit()

        return True

    def get_connected_equipment(self):
        """
        Obtiene el equipo conectado al puerto.

        Returns:
            Model: Equipo conectado o None
        """
        if not self.connected_equipment_id:
            return None

        # Mapeo de tipos de equipos a modelos
        equipment_map = {
            'camara': 'Camara',
            'nvr': 'NVR',
            'switch': 'Switch',
            'ups': 'UPS',
            'fuente_poder': 'FuentePoder',
            'gabinete': 'Gabinete'
        }

        model_name = equipment_map.get(self.connected_equipment_type)
        if model_name and hasattr(globals(), model_name):
            return globals()[model_name].query.get(self.connected_equipment_id)

        return None

    def update_utilization(self, percentage):
        """
        Actualiza el porcentaje de utilización del puerto.

        Args:
            percentage (float): Nuevo porcentaje de utilización
        """
        self.utilization_percentage = max(0, min(100, percentage))
        self.last_activity = datetime.utcnow()
        db.session.commit()

    @classmethod
    def get_available_ports(cls, switch_id):
        """
        Obtiene los puertos disponibles de un switch.

        Args:
            switch_id (int): ID del switch

        Returns:
            list: Lista de puertos disponibles
        """
        return cls.query.filter_by(
            switch_id=switch_id,
            status=PortStatus.DOWN,
            connected_equipment_id=None,
            deleted=False
        ).all()

    @classmethod
    def get_connected_ports(cls, switch_id):
        """
        Obtiene los puertos conectados de un switch.

        Args:
            switch_id (int): ID del switch

        Returns:
            list: Lista de puertos conectados
        """
        return cls.query.filter(
            cls.switch_id == switch_id,
            cls.connected_equipment_id.is_not(None),
            cls.deleted == False
        ).all()


class SwitchVLAN(BaseModel):
    """
    Modelo de VLANs de switch.

    Attributes:
    switch_id (int): ID del switch
    vlan_id (int): ID de la VLAN
    vlan_name (str): Nombre de la VLAN
    vlan_type (str): Tipo de VLAN
    is_native (bool): Si es VLAN nativa
    is_tagged (bool): Si es VLAN tagged
    description (str): Descripción de la VLAN
    subnet (str): Subred asignada
    gateway (str): Gateway de la VLAN
    dhcp_enabled (bool): DHCP habilitado
    dhcp_range_start (str): Inicio del rango DHCP
    dhcp_range_end (str): Final del rango DHCP
    """

    __tablename__ = 'switch_vlans'

    switch_id = Column(Integer, ForeignKey('switches.id'), nullable=False,
                       comment="ID del switch")
    vlan_id = Column(Integer, nullable=False,
                     comment="ID numérico de la VLAN")
    vlan_name = Column(String(50), nullable=False,
                       comment="Nombre de la VLAN")
    vlan_type = Column(Enum(VLANType), nullable=True,
                       comment="Tipo de VLAN")

    # Configuración
    is_native = Column(Boolean, default=False, nullable=False,
                       comment="Si es la VLAN nativa")
    is_tagged = Column(Boolean, default=True, nullable=False,
                       comment="Si es VLAN tagged")
    description = Column(String(100), nullable=True,
                         comment="Descripción de la VLAN")

    # Configuración de red
    subnet = Column(String(18), nullable=True,
                    comment="Subred asignada (ej: 192.168.1.0/24)")
    gateway = Column(String(45), nullable=True,
                     comment="Gateway de la VLAN")

    # DHCP
    dhcp_enabled = Column(Boolean, default=False, nullable=False,
                          comment="DHCP habilitado para esta VLAN")
    dhcp_range_start = Column(String(45), nullable=True,
                              comment="Inicio del rango DHCP")
    dhcp_range_end = Column(String(45), nullable=True,
                            comment="Final del rango DHCP")

    # Relaciones
    switch = relationship("Switch", back_populates="vlans")

    def __repr__(self):
        return f"<SwitchVLAN(switch={self.switch_id}, vlan={self.vlan_id} - {self.vlan_name})>"

    @classmethod
    def get_by_switch(cls, switch_id):
        """
        Obtiene las VLANs de un switch.

        Args:
            switch_id (int): ID del switch

        Returns:
            list: Lista de VLANs del switch
        """
        return cls.query.filter_by(switch_id=switch_id, deleted=False).all()

    @classmethod
    def get_native_vlan(cls, switch_id):
        """
        Obtiene la VLAN nativa de un switch.

        Args:
            switch_id (int): ID del switch

        Returns:
            SwitchVLAN: VLAN nativa o None
        """
        return cls.query.filter_by(
            switch_id=switch_id,
            is_native=True,
            deleted=False
        ).first()
