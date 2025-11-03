"""
Modelo base para equipos de red y hardware.

Proporciona funcionalidades comunes para todos los tipos de equipos.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db, EquipmentStatus, EquipmentType
import enum


class ConnectionType(enum.Enum):
    """Tipos de conexión de red."""
    ETHERNET = "ethernet"
    FIBRA_OPTICA = "fibra_optica"
    WIFI = "wifi"
    COAXIAL = "coaxial"
    INALAMBRICO = "inalambrico"


class NetworkConnection(BaseModel, db.Model):
    """
    Modelo de conexiones de red entre equipos.
    
    Attributes:
        source_equipment_id (int): ID del equipo origen
        source_equipment_type (str): Tipo del equipo origen
        target_equipment_id (int): ID del equipo destino
        target_equipment_type (str): Tipo del equipo destino
        connection_type (str): Tipo de conexión
        cable_type (str): Tipo de cable utilizado
        cable_length (float): Longitud del cable en metros
        port_source (str): Puerto de origen
        port_target (str): Puerto de destino
        is_active (bool): Si la conexión está activa
        vlan_id (int): ID de la VLAN
        bandwidth_limit (int): Límite de ancho de banda en Mbps
        latency_ms (float): Latencia en milisegundos
        packet_loss (float): Pérdida de paquetes en porcentaje
        notes (str): Notas adicionales
    """
    
    __tablename__ = 'network_connections'
    
    # Equipos conectados
    source_equipment_id = Column(Integer, nullable=False,
                                comment="ID del equipo origen de la conexión")
    source_equipment_type = Column(String(30), nullable=False,
                                  comment="Tipo del equipo origen")
    target_equipment_id = Column(Integer, nullable=False,
                                comment="ID del equipo destino de la conexión")
    target_equipment_type = Column(String(30), nullable=False,
                                  comment="Tipo del equipo destino")
    
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
    
    def get_source_equipment(self):
        """
        Obtiene el equipo origen según su tipo.
        
        Returns:
            Model: Equipo origen o None
        """
        from models import NVR, Switch, UPS, FuentePoder, Gabinete, Camara
        
        equipment_map = {
            'nvr': NVR,
            'switch': Switch,
            'ups': UPS,
            'fuente_poder': FuentePoder,
            'gabinete': Gabinete,
            'camara': Camara
        }
        
        equipment_class = equipment_map.get(self.source_equipment_type)
        if equipment_class:
            return equipment_class.query.get(self.source_equipment_id)
        return None
    
    def get_target_equipment(self):
        """
        Obtiene el equipo destino según su tipo.
        
        Returns:
            Model: Equipo destino o None
        """
        from models import NVR, Switch, UPS, FuentePoder, Gabinete, Camara
        
        equipment_map = {
            'nvr': NVR,
            'switch': Switch,
            'ups': UPS,
            'fuente_poder': FuentePoder,
            'gabinete': Gabinete,
            'camara': Camara
        }
        
        equipment_class = equipment_map.get(self.target_equipment_type)
        if equipment_class:
            return equipment_class.query.get(self.target_equipment_id)
        return None
    
    def test_connection(self):
        """
        Prueba la conexión y actualiza las métricas.
        
        Returns:
            dict: Resultados de la prueba
        """
        # Esta es una implementación simplificada
        # En producción se debería hacer ping o pruebas de conectividad reales
        import random
        
        # Simular métricas de red
        self.latency_ms = round(random.uniform(1.0, 50.0), 2)
        self.packet_loss = round(random.uniform(0.0, 5.0), 2)
        self.save()
        
        return {
            'status': 'success' if self.packet_loss < 1.0 else 'degraded',
            'latency_ms': self.latency_ms,
            'packet_loss': self.packet_loss
        }
    
    @classmethod
    def get_by_equipment(cls, equipment_id, equipment_type):
        """
        Obtiene todas las conexiones de un equipo.
        
        Args:
            equipment_id (int): ID del equipo
            equipment_type (str): Tipo del equipo
            
        Returns:
            list: Lista de conexiones del equipo
        """
        return cls.query.filter(
            db.or_(
                db.and_(cls.source_equipment_id == equipment_id, 
                       cls.source_equipment_type == equipment_type),
                db.and_(cls.target_equipment_id == equipment_id,
                       cls.target_equipment_type == equipment_type)
            ),
            cls.deleted == False
        ).all()
    
    @classmethod
    def get_active_connections(cls):
        """
        Obtiene todas las conexiones activas.
        
        Returns:
            list: Lista de conexiones activas
        """
        return cls.query.filter_by(is_active=True, deleted=False).all()


class EquipmentBase(BaseModel, db.Model):
    """
    Clase base abstracta para todos los equipos.
    Proporciona campos y métodos comunes.
    """
    
    __abstract__ = True
    
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
                       comment="Dirección IP del equipo")
    mac_address = Column(String(17), nullable=True, unique=True,
                        comment="Dirección MAC del equipo")
    hostname = Column(String(100), nullable=True,
                     comment="Nombre del host")
    
    # Ubicación y estado
    ubicacion_id = Column(Integer, ForeignKey('ubicaciones.id'), nullable=True,
                         comment="ID de la ubicación donde está instalado")
    status = Column(String(20), nullable=False, default=EquipmentStatus.ACTIVO,
                   comment="Estado actual del equipo")
    
    # Configuración
    firmware_version = Column(String(20), nullable=True,
                             comment="Versión del firmware")
    configuration_backup = Column(Text, nullable=True,
                                 comment="Respaldo de configuración en formato JSON")
    
    # Fechas importantes
    purchase_date = Column(DateTime, nullable=True,
                          comment="Fecha de compra")
    warranty_expiry = Column(DateTime, nullable=True,
                            comment="Fecha de vencimiento de garantía")
    installation_date = Column(DateTime, nullable=True,
                              comment="Fecha de instalación")
    
    # Especificaciones técnicas
    power_consumption = Column(Float, nullable=True,
                              comment="Consumo de energía en watts")
    operating_temperature = Column(String(50), nullable=True,
                                  comment="Temperatura de operación")
    dimensions = Column(String(50), nullable=True,
                       comment="Dimensiones del equipo")
    weight = Column(Float, nullable=True,
                   comment="Peso en kilogramos")
    
    # Monitoreo
    last_heartbeat = Column(DateTime, nullable=True,
                           comment="Último heartbeat del equipo")
    uptime_percentage = Column(Float, default=100.0, nullable=False,
                              comment="Porcentaje de tiempo de actividad")
    
    # Metadatos
    notes = Column(Text, nullable=True,
                  comment="Notas adicionales")
    
    # Relaciones
    ubicacion = relationship("Ubicacion", back_populates="equipos")
    created_by_user = None  # Se define en cada subclase
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}')>"
    
    def is_online(self):
        """
        Verifica si el equipo está en línea.
        
        Returns:
            bool: True si está en línea
        """
        if not self.last_heartbeat:
            return False
        
        # Considerar en línea si el último heartbeat fue hace menos de 5 minutos
        time_diff = datetime.utcnow() - self.last_heartbeat
        return time_diff.total_seconds() < 300  # 5 minutos
    
    def update_heartbeat(self):
        """
        Actualiza el timestamp del último heartbeat.
        """
        self.last_heartbeat = datetime.utcnow()
        self.save()
    
    def get_connection_string(self):
        """
        Obtiene la cadena de conexión completa.
        
        Returns:
            str: Cadena de conexión
        """
        if self.ip_address:
            return self.ip_address
        return self.hostname or "Sin conexión"
    
    def get_manufacturer_model(self):
        """
        Obtiene el fabricante y modelo en una cadena.
        
        Returns:
            str: Fabricante y modelo
        """
        if self.manufacturer and self.model:
            return f"{self.manufacturer} {self.model}"
        return self.model or self.manufacturer or "Sin especificar"
    
    def get_age_in_years(self):
        """
        Calcula la edad del equipo en años.
        
        Returns:
            float: Edad en años
        """
        if not self.installation_date:
            return None
        
        age = datetime.utcnow() - self.installation_date
        return round(age.days / 365.25, 2)
    
    def is_warranty_valid(self):
        """
        Verifica si la garantía aún es válida.
        
        Returns:
            bool: True si la garantía es válida
        """
        if not self.warranty_expiry:
            return None
        
        return datetime.utcnow() < self.warranty_expiry
    
    def days_until_warranty_expiry(self):
        """
        Calcula los días hasta el vencimiento de la garantía.
        
        Returns:
            int: Días restantes (negativo si ya venció)
        """
        if not self.warranty_expiry:
            return None
        
        remaining = self.warranty_expiry - datetime.utcnow()
        return remaining.days
    
    def get_connections(self):
        """
        Obtiene todas las conexiones de red de este equipo.
        
        Returns:
            list: Lista de conexiones
        """
        equipment_type = self.__class__.__name__.lower()
        return NetworkConnection.get_by_equipment(self.id, equipment_type)
    
    def add_connection(self, target_equipment, connection_type, **kwargs):
        """
        Agrega una conexión de red a este equipo.
        
        Args:
            target_equipment (EquipmentBase): Equipo destino
            connection_type (ConnectionType): Tipo de conexión
            **kwargs: Parámetros adicionales para la conexión
            
        Returns:
            NetworkConnection: Nueva conexión creada
        """
        connection = NetworkConnection(
            source_equipment_id=self.id,
            source_equipment_type=self.__class__.__name__.lower(),
            target_equipment_id=target_equipment.id,
            target_equipment_type=target_equipment.__class__.__name__.lower(),
            connection_type=connection_type,
            **kwargs
        )
        return connection.save()
    
    def get_failure_count(self):
        """
        Obtiene el número de fallas registradas para este equipo.
        
        Returns:
            int: Número de fallas
        """
        from models import Falla
        
        equipment_type = self.__class__.__name__.lower()
        return Falla.query.filter_by(
            equipment_id=self.id,
            equipment_type=equipment_type,
            deleted=False
        ).count()
    
    def get_maintenance_count(self):
        """
        Obtiene el número de mantenimientos realizados.
        
        Returns:
            int: Número de mantenimientos
        """
        from models import Mantenimiento
        
        equipment_type = self.__class__.__name__.lower()
        return Mantenimiento.query.filter_by(
            equipment_id=self.id,
            equipment_type=equipment_type,
            deleted=False
        ).count()
    
    @classmethod
    def get_by_location(cls, location_id):
        """
        Obtiene todos los equipos de una ubicación específica.
        
        Args:
            location_id (int): ID de la ubicación
            
        Returns:
            list: Lista de equipos en la ubicación
        """
        return cls.query.filter_by(ubicacion_id=location_id, deleted=False).all()
    
    @classmethod
    def get_active_equipment(cls):
        """
        Obtiene todos los equipos activos.
        
        Returns:
            list: Lista de equipos activos
        """
        return cls.query.filter_by(
            status=EquipmentStatus.ACTIVO,
            deleted=False
        ).all()
    
    @classmethod
    def get_offline_equipment(cls):
        """
        Obtiene todos los equipos fuera de línea.
        
        Returns:
            list: Lista de equipos fuera de línea
        """
        from datetime import timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        return cls.query.filter(
            (cls.last_heartbeat <= cutoff_time) | (cls.last_heartbeat.is_(None)),
            cls.status != EquipmentStatus.DADO_BAJA,
            cls.deleted == False
        ).all()


# Función helper para obtener el modelo según el tipo
def get_equipment_model(equipment_type):
    """
    Obtiene la clase del modelo según el tipo de equipo.
    
    Args:
        equipment_type (str): Tipo de equipo
        
    Returns:
        class: Clase del modelo o None
    """
    equipment_models = {
        'nvr': 'NVR',
        'dvr': 'NVR',  # DVR usa el mismo modelo que NVR
        'switch': 'Switch',
        'ups': 'UPS',
        'fuente_poder': 'FuentePoder',
        'gabinete': 'Gabinete',
        'camara': 'Camara'
    }
    
    # Esta función se puede implementar dinámicamente si es necesario
    return equipment_models.get(equipment_type)