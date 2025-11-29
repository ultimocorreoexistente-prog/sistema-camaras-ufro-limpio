# models/equipo.py
"""
Modelo base para equipos de red y hardware.
Proporciona funcionalidades comunes para todos los tipos de equipos.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, or_
from sqlalchemy.orm import relationship, declared_attr
from models.base import BaseModelMixin  # Correcto: Hereda metadatos base
from models import db, EquipmentStatus
import enum
import json

class ConnectionType(enum.Enum):
    """Tipos de conexión de red."""
    ETHERNET = "ethernet"
    FIBRA_OPTICA = "fibra_optica"
    WIFI = "wifi"
    COAXIAL = "coaxial"
    INALAMBRICO = "inalambrico"


class NetworkConnection(BaseModelMixin, db.Model):
    """
    Modelo de conexiones de red entre equipos. Utiliza polimorfismo implícito
    basado en tipo (source_equipment_type/target_equipment_type).
    """
    __tablename__ = 'network_connections'
    
    # id, created_at, updated_at, deleted heredados de BaseModelMixin

    # Equipos conectados
    source_equipment_id = Column(Integer, nullable=False,
                                 comment="ID del equipo origen de la conexión")
    source_equipment_type = Column(String(30), nullable=False,
                                  comment="Tipo del equipo origen (nvr, switch, camara, etc.)")
    target_equipment_id = Column(Integer, nullable=False,
                                 comment="ID del equipo destino de la conexión")
    target_equipment_type = Column(String(30), nullable=False,
                                  comment="Tipo del equipo destino (nvr, switch, camara, etc.)")

    # Detalles de la conexión
    connection_type = Column(Enum(ConnectionType), nullable=False,
                             comment="Tipo de conexión física")
    cable_type = Column(String(50), nullable=True,
                        comment="Tipo de cable utilizado (Cat6, fibra, etc.)")
    cable_length = Column(Float, nullable=True,
                          comment="Longitud del cable en metros")
    port_source = Column(String(20), nullable=True,
                         comment="Puerto o interfaz de origen")
    port_target = Column(String(20), nullable=True,
                         comment="Puerto o interfaz de destino")

    # Estado y configuración
    is_active = Column(Boolean, default=True, nullable=False,
                      comment="Si la conexión está activa")
    vlan_id = Column(Integer, nullable=True,
                    comment="ID de la VLAN asignada")

    # Métricas de rendimiento
    bandwidth_limit = Column(Integer, nullable=True,
                             comment="Límite de ancho de banda en Mbps")
    latency_ms = Column(Float, nullable=True,
                       comment="Latencia promedio en milisegundos")
    packet_loss = Column(Float, default=0.0, nullable=False,
                         comment="Pérdida de paquetes en porcentaje")

    # Metadatos
    notes = Column(Text, nullable=True,
                  comment="Notas adicionales")

    def __repr__(self):
        return f"<NetworkConnection(from_{self.source_equipment_type}_{self.source_equipment_id}_to_{self.target_equipment_type}_{self.target_equipment_id})>"

    def _get_equipment_class(self, type_name):
        """Helper para obtener la clase del modelo basado en el nombre del tipo."""
        # Se requiere importación local para evitar importaciones circulares
        from models import NVR, Switch, UPS, FuentePoder, Gabinete, Camara
        equipment_map = {
            'nvr': NVR,
            'switch': Switch,
            'ups': UPS,
            'fuente_poder': FuentePoder,
            'gabinete': Gabinete,
            'camara': Camara
        }
        return equipment_map.get(type_name)

    def get_source_equipment(self):
        """Obtiene el equipo origen según su tipo."""
        equipment_class = self._get_equipment_class(self.source_equipment_type)
        if equipment_class:
            return equipment_class.query.get(self.source_equipment_id)
        return None

    def get_target_equipment(self):
        """Obtiene el equipo destino según su tipo."""
        equipment_class = self._get_equipment_class(self.target_equipment_type)
        if equipment_class:
            return equipment_class.query.get(self.target_equipment_id)
        return None

    @classmethod
    def get_by_equipment(cls, equipment_id, equipment_type):
        """Obtiene todas las conexiones de un equipo (sea origen o destino)."""
        return cls.query.filter(
            cls.deleted == False,
            or_(
                # Es el origen Y coincide el tipo
                (cls.source_equipment_id == equipment_id) & (cls.source_equipment_type == equipment_type),
                # O es el destino Y coincide el tipo
                (cls.target_equipment_id == equipment_id) & (cls.target_equipment_type == equipment_type)
            )
        ).all()


class EquipmentBase(BaseModelMixin, db.Model):
    """
    Clase base abstracta para todos los equipos.
    Proporciona atributos comunes y funcionalidades de monitoreo.
    """
    __abstract__ = True

    # id, created_at, updated_at, deleted heredados de BaseModelMixin

    # Información básica
    name = Column(String(100), nullable=False, index=True,
                  comment="Nombre identificador del equipo")
    model = Column(String(50), nullable=True,
                   comment="Modelo del equipo")
    manufacturer = Column(String(50), nullable=True,
                          comment="Fabricante del equipo")
    serial_number = Column(String(100), nullable=True, unique=True,
                          comment="Número de serie del equipo")
    inventory_number = Column(String(50), nullable=True, unique=True,
                              comment="Número de inventario interno")

    # Identificación de red
    ip_address = Column(String(45), nullable=True, index=True,
                        comment="Dirección IP del equipo (IPv4 o IPv6)")
    mac_address = Column(String(17), nullable=True, unique=True,
                          comment="Dirección MAC del equipo (formato XX:XX:XX:XX:XX:XX)")
    hostname = Column(String(100), nullable=True,
                      comment="Nombre del host")

    # Ubicación y estado
    ubicacion_id = Column(Integer, ForeignKey('ubicaciones.id'), nullable=True,
                          comment="ID de la ubicación donde está instalado")
    # ✅ Corregido a .value, asegurando que se guarda el string/valor en la DB
    status = Column(Enum(EquipmentStatus), nullable=False, default=EquipmentStatus.ACTIVO.value,
                    comment="Estado actual del equipo")

    # Configuración
    firmware_version = Column(String(20), nullable=True,
                              comment="Versión del firmware")
    configuration_backup = Column(Text, nullable=True,
                                  comment="Respaldo de configuración en formato JSON")

    # Fechas importantes
    purchase_date = Column(DateTime(timezone=True), nullable=True, # ✅ Usar timezone=True
                           comment="Fecha de compra")
    warranty_expiry = Column(DateTime(timezone=True), nullable=True, # ✅ Usar timezone=True
                             comment="Fecha de vencimiento de garantía")
    installation_date = Column(DateTime(timezone=True), nullable=True, # ✅ Usar timezone=True
                               comment="Fecha de instalación")

    # Especificaciones técnicas
    power_consumption = Column(Float, nullable=True,
                              comment="Consumo de energía en watts")
    operating_temperature = Column(String(50), nullable=True,
                                  comment="Temperatura de operación (ej: 0°C a 40°C)")
    dimensions = Column(String(50), nullable=True,
                        comment="Dimensiones del equipo (ej: 44x440x280 mm)")
    weight = Column(Float, nullable=True,
                    comment="Peso en kilogramos")

    # Monitoreo
    last_heartbeat = Column(DateTime(timezone=True), nullable=True, # ✅ Usar timezone=True
                            comment="Último heartbeat del equipo")
    uptime_percentage = Column(Float, default=100.0, nullable=False,
                               comment="Porcentaje de tiempo de actividad")

    # Metadatos
    notes = Column(Text, nullable=True,
                  comment="Notas adicionales")

    # Relaciones
    @declared_attr
    def ubicacion(cls):
        # Asume que el modelo Ubicacion tiene un back_populates llamado 'equipos'
        return relationship("Ubicacion", back_populates="equipos")
    
    # Método para serializar la configuración de respaldo si existe
    def get_configuration_backup_dict(self):
        if not self.configuration_backup:
            return None
        try:
            return json.loads(self.configuration_backup)
        except json.JSONDecodeError:
            return {"error": "Configuración de respaldo no es JSON válido"}

    # Métodos de monitoreo
    def is_online(self):
        """Verifica si el equipo está online basado en el último heartbeat (dentro de 5 minutos)."""
        if not self.last_heartbeat:
            return False
        # Asume que last_heartbeat fue guardado con timezone=True
        time_diff = datetime.now(timezone.utc) - self.last_heartbeat
        return time_diff.total_seconds() < 300  # 5 minutos

    def update_heartbeat(self, session=None):
        """Actualiza el timestamp del último heartbeat."""
        session = session or db.session
        self.last_heartbeat = datetime.now(timezone.utc)
        session.add(self)
        session.commit()

    def get_age_in_years(self):
        """Calcula la edad del equipo en años."""
        if not self.installation_date:
            return None
        age = datetime.now(timezone.utc) - self.installation_date
        return round(age.days / 365.25, 2)


class Switch(EquipmentBase):
    """
    Modelo de switches de red.
    Hereda de EquipmentBase para funcionalidad común.
    """
    __tablename__ = 'switches'

    # Fotografías asociadas al switch
    fotografias = relationship("Fotografia", back_populates="switch")

    def __repr__(self):
        return f"<Switch(name='{self.name}')>"


class UPS(EquipmentBase):
    """
    Modelo de sistemas de alimentación ininterrumpida.
    Hereda de EquipmentBase para funcionalidad común.
    """
    __tablename__ = 'ups'

    # Fotografías asociadas al UPS
    fotografias = relationship("Fotografia", back_populates="ups")

    def __repr__(self):
        return f"<UPS(name='{self.name}')>"


class NVR(EquipmentBase):
    """
    Modelo de grabadores de video en red.
    Hereda de EquipmentBase para funcionalidad común.
    """
    __tablename__ = 'nvr_dvr' # nombre real

    # Relación con cámaras
    camaras = relationship("Camara", back_populates="nvr")
    
    # Fotografías asociadas al NVR
    fotografias = relationship("Fotografia", back_populates="nvr")

    def __repr__(self):
        return f"<NVR(name='{self.name}')>"


class Gabinete(EquipmentBase):
    """
    Modelo de gabinetes/racks para equipos.
    Hereda de EquipmentBase para funcionalidad común.
    """
    __tablename__ = 'gabinetes'

    # Fotografías asociadas al gabinete
    fotografias = relationship("Fotografia", back_populates="gabinete")

    def __repr__(self):
        return f"<Gabinete(name='{self.name}')>"


class FuentePoder(EquipmentBase):
    """
    Modelo de fuentes de alimentación.
    Hereda de EquipmentBase para funcionalidad común.
    """
    __tablename__ = 'fuente_poder' # singular, como en tu DB

    # Fotografías asociadas a la fuente de poder
    fotografias = relationship("Fotografia", back_populates="fuente_poder")

    def __repr__(self):
        return f"<FuentePoder(name='{self.name}')>"