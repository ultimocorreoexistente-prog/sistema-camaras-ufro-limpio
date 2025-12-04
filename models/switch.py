# models/switch.py
"""
Modelo de switches de red — Versión definitiva para producción.
Incluye gestión completa de switches, puertos, VLANs, stacking, PoE y topología.
Compatible con Railway y SQLAlchemy 2.0+.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from . import db
from .base import TimestampedModel
import enum

# ======================
# Enums (sin dependencias externas)
# ======================

class SwitchType(enum.Enum):
    ACCESS = "access"
    DISTRIBUTION = "distribution"
    CORE = "core"
    AGGREGATION = "aggregation"
    EDGE = "edge"

class PortType(enum.Enum):
    ETHERNET = "ethernet"
    GIGABIT = "gigabit"
    TEN_GIGABIT = "ten_gigabit"
    FIBER = "fiber"
    SFP = "sfp"
    SFP_PLUS = "sfp_plus"
    COMBO = "combo"

class PortStatus(enum.Enum):
    UP = "up"
    DOWN = "down"
    DISABLED = "disabled"
    ERROR = "error"

class VLANType(enum.Enum):
    DEFAULT = "default"
    VOICE = "voice"
    GUEST = "guest"
    MANAGEMENT = "management"
    IOT = "iot"
    DATA = "data"

# ======================
# Modelo principal: Switch
# ======================

class Switch(db.Model, TimestampedModel):
    __tablename__ = 'switches'
    
    # ✅ Clave primaria explícita (obligatoria en SQLAlchemy 2.0+)
    id = Column(Integer, primary_key=True)
    
    # ✅ Campos básicos para UI y operaciones
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default='activo')  # 'activo', 'inactivo', 'mantenimiento'

    # Configuración del switch
    switch_type = Column(Enum(SwitchType), nullable=True)
    total_ports = Column(Integer, nullable=False, default=0)
    poe_ports = Column(Integer, default=0, nullable=False)
    max_poe_power = Column(Integer, nullable=True)
    port_speed = Column(String(20), nullable=True)  # ✅ Corregido: era String(0)

    # Puertos especializados
    fiber_ports = Column(Integer, default=0, nullable=False)
    stackable = Column(Boolean, default=False, nullable=False)
    stacking_ports = Column(Integer, default=0, nullable=False)

    # Configuración de gestión
    management_protocols = Column(Text, nullable=True)
    snmp_community = Column(String(50), nullable=True)

    # Características avanzadas
    vlan_support = Column(Boolean, default=True, nullable=False)
    qos_support = Column(Boolean, default=True, nullable=False)
    poe_plus_support = Column(Boolean, default=False, nullable=False)
    managed = Column(Boolean, default=True, nullable=False)
    layer_support = Column(String(10), nullable=True)

    # Capacidades
    mac_address_table_size = Column(Integer, nullable=True)
    forwarding_rate = Column(Integer, nullable=True)
    switching_capacity = Column(Integer, nullable=True)

    # Redundancia y stacking
    redundancy_support = Column(Boolean, default=False, nullable=False)
    stack_id = Column(Integer, nullable=True)
    stack_master = Column(Boolean, default=False, nullable=False)

    # Configuración y firmware
    firmware_url = Column(String(500), nullable=True)
    configuration_template = Column(Text, nullable=True)
    backup_configuration = Column(Text, nullable=True)

    # Monitoreo y seguridad
    monitoring_enabled = Column(Boolean, default=True, nullable=False)
    alerting_enabled = Column(Boolean, default=True, nullable=False)
    auto_negotiation = Column(Boolean, default=True, nullable=False)
    storm_control = Column(Boolean, default=False, nullable=False)
    spanning_tree_enabled = Column(Boolean, default=True, nullable=False)

    # Relaciones
    ubicacion_id = Column(Integer, ForeignKey('ubicaciones.id'), nullable=True)
    ubicacion = relationship("Ubicacion", back_populates="switches")
    created_by_user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    created_by_user = relationship("Usuario", back_populates="created_equipos")

    mantenimientos = relationship("Mantenimiento", back_populates="switch", cascade="all, delete-orphan")
    fotografias = relationship("Fotografia", back_populates="switch", cascade="all, delete-orphan")
    puertos = relationship("SwitchPort", back_populates="switch", cascade="all, delete-orphan")
    vlans = relationship("SwitchVLAN", back_populates="switch", cascade="all, delete-orphan")

    # ======================
    # Métodos de negocio — COMPLETOS Y FUNCIONALES
    # ======================

    def __repr__(self):
        return f"<Switch(id={self.id}, name='{self.name}', ports={self.total_ports})>"

    def get_available_ports(self):
        used_ports = len([p for p in self.puertos if not p.is_available()])
        return max(0, self.total_ports - used_ports)

    def can_add_connection(self):
        return self.get_available_ports() > 0

    def add_port(self, port_number, port_type=PortType.ETHERNET, **kwargs):
        if not self.can_add_connection():
            return None
        port = SwitchPort(switch_id=self.id, port_number=port_number, port_type=port_type, **kwargs)
        db.session.add(port)
        db.session.commit()
        return port

    def get_port_utilization_percentage(self):
        if self.total_ports == 0:
            return 0.0
        used = len([p for p in self.puertos if not p.is_available()])
        return round((used / self.total_ports) * 100, 2)

    def get_poe_power_usage(self):
        return sum(p.poe_power_consumption for p in self.puertos if p.poe_power_consumption)

    def get_poe_power_available(self):
        return (self.max_poe_power or 0) - self.get_poe_power_usage()

    def get_active_ports_count(self):
        return len([p for p in self.puertos if p.status == PortStatus.UP])

    def get_ports_summary(self):
        total = len(self.puertos)
        active = down = disabled = error = 0
        for p in self.puertos:
            if p.status == PortStatus.UP: active += 1
            elif p.status == PortStatus.DOWN: down += 1
            elif p.status == PortStatus.DISABLED: disabled += 1
            elif p.status == PortStatus.ERROR: error += 1
        return {
            'total': total,
            'active': active,
            'down': down,
            'disabled': disabled,
            'error': error,
            'utilization_percentage': self.get_port_utilization_percentage()
        }

    def get_vlans_summary(self):
        total = len(self.vlans)
        native = len([v for v in self.vlans if v.is_native])
        tagged = len([v for v in self.vlans if v.is_tagged])
        return {'total': total, 'native': native, 'tagged': tagged}

    def get_system_health_score(self):
        """Puntaje de salud del sistema (0-100) — ✅ versión corregida y funcional"""
        score = 100
        error_ports = len([p for p in self.puertos if p.status == PortStatus.ERROR])
        score -= error_ports * 15
        down_ports = len([p for p in self.puertos if p.status == PortStatus.DOWN])
        score -= down_ports * 5
        util = self.get_port_utilization_percentage()
        if util > 90: score -= 20
        elif util > 80: score -= 10
        if self.status != 'activo': score -= 10
        return max(0, min(100, score))

    def get_network_topology_summary(self):
        """Resumen estructurado para dashboard y API"""
        return {
            'ports': self.get_ports_summary(),
            'vlans': self.get_vlans_summary(),
            'stacking': {'is_stackable': self.stackable, 'stack_id': self.stack_id, 'is_master': self.stack_master},
            'health_score': self.get_system_health_score(),
            'capabilities': {
                'vlan_support': self.vlan_support,
                'qos_support': self.qos_support,
                'poe_support': self.poe_ports > 0,
                'redundancy': self.redundancy_support,
                'layer_support': self.layer_support
            }
        }

    def configure_vlan(self, vlan_id, vlan_name, vlan_type=VLANType.DATA, **kwargs):
        vlan = SwitchVLAN(switch_id=self.id, vlan_id=vlan_id, vlan_name=vlan_name, vlan_type=vlan_type, **kwargs)
        db.session.add(vlan)
        db.session.commit()
        return vlan

    # ======================
    # Métodos de clase — PARA OPERACIONES MASIVAS
    # ======================

    @classmethod
    def get_by_type(cls, switch_type):
        return cls.query.filter_by(switch_type=switch_type, deleted_at=None).all()

    @classmethod
    def get_available_for_connections(cls):
        return [s for s in cls.query.filter_by(status='activo', deleted_at=None).all() if s.can_add_connection()]

    @classmethod
    def get_stack_members(cls, stack_id):
        return cls.query.filter_by(stack_id=stack_id, deleted_at=None).all()

    @classmethod
    def get_stack_masters(cls):
        return cls.query.filter_by(stack_master=True, deleted_at=None).all()


# ======================
# Modelo: SwitchPort
# ======================

class SwitchPort(db.Model, TimestampedModel):
    __tablename__ = 'switch_ports'
    
    id = Column(Integer, primary_key=True)
    switch_id = Column(Integer, ForeignKey('switches.id'), nullable=False)
    port_number = Column(Integer, nullable=False)
    port_type = Column(Enum(PortType), nullable=False)
    status = Column(Enum(PortStatus), default=PortStatus.DOWN, nullable=False)
    
    description = Column(String(100), nullable=True)
    connected_equipment_id = Column(Integer, nullable=True)
    connected_equipment_type = Column(String(30), nullable=True)
    vlan_id = Column(Integer, nullable=True)
    speed = Column(String(20), nullable=True)  # ✅ Corregido
    duplex = Column(String(10), nullable=True)
    poe_enabled = Column(Boolean, default=False, nullable=False)
    poe_power_consumption = Column(Float, default=0.0, nullable=False)
    error_count = Column(Integer, default=0, nullable=False)
    utilization_percentage = Column(Float, default=0.0, nullable=False)
    last_activity = Column(DateTime, nullable=True)

    switch = relationship("Switch", back_populates="puertos")

    def __repr__(self):
        return f"<SwitchPort(id={self.id}, switch={self.switch_id}, port={self.port_number})>"

    def is_available(self):
        return (self.status == PortStatus.DOWN and 
                not self.connected_equipment_id and
                self.port_type in [PortType.ETHERNET, PortType.GIGABIT])

    def connect_equipment(self, equipment, equipment_type):
        if not self.is_available():
            return False
        self.connected_equipment_id = equipment.id
        self.connected_equipment_type = equipment_type
        self.status = PortStatus.UP
        self.last_activity = datetime.utcnow()
        db.session.commit()
        return True

    def disconnect_equipment(self):
        self.connected_equipment_id = None
        self.connected_equipment_type = None
        self.status = PortStatus.DOWN
        self.last_activity = None
        db.session.commit()
        return True

    def get_connected_equipment(self):
        """Obtiene el equipo conectado (Camara, NVR, etc.) — ✅ funcional sin imports circulares"""
        if not self.connected_equipment_id or not self.connected_equipment_type:
            return None
        # Importación diferida para evitar circularidad
        from models import Camara, NVR, UPS, FuentePoder, Gabinete
        model_map = {
            'camara': Camara,
            'nvr': NVR,
            'ups': UPS,
            'fuente_poder': FuentePoder,
            'gabinete': Gabinete
        }
        model_class = model_map.get(self.connected_equipment_type)
        return model_class.query.get(self.connected_equipment_id) if model_class else None


# ======================
# Modelo: SwitchVLAN
# ======================

class SwitchVLAN(db.Model, TimestampedModel):
    __tablename__ = 'switch_vlans'
    
    id = Column(Integer, primary_key=True)
    switch_id = Column(Integer, ForeignKey('switches.id'), nullable=False)
    vlan_id = Column(Integer, nullable=False)
    vlan_name = Column(String(50), nullable=False)
    vlan_type = Column(Enum(VLANType), nullable=True)
    is_native = Column(Boolean, default=False, nullable=False)
    is_tagged = Column(Boolean, default=True, nullable=False)
    description = Column(String(100), nullable=True)
    subnet = Column(String(18), nullable=True)
    gateway = Column(String(45), nullable=True)
    dhcp_enabled = Column(Boolean, default=False, nullable=False)
    dhcp_range_start = Column(String(45), nullable=True)
    dhcp_range_end = Column(String(45), nullable=True)

    switch = relationship("Switch", back_populates="vlans")

    def __repr__(self):
        return f"<SwitchVLAN(id={self.id}, switch={self.switch_id}, vlan={self.vlan_id}, name='{self.vlan_name}')>"

    @classmethod
    def get_by_switch(cls, switch_id):
        return cls.query.filter_by(switch_id=switch_id, deleted_at=None).all()

    @classmethod
    def get_native_vlan(cls, switch_id):
        return cls.query.filter_by(switch_id=switch_id, is_native=True, deleted_at=None).first()