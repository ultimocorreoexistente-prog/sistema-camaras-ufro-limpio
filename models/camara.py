"""
Modelo de cámaras de seguridad con coordenadas GPS.

Incluye gestión de cámaras, configuraciones, conexiones y estados.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db, CameraStatus, EquipmentType, EquipmentStatus
import enum


class CameraType(enum.Enum):
    """Tipos de cámaras de seguridad."""
    FIXA = "fija"
    PTZ = "ptz"  # Pan, Tilt, Zoom
    DOMO = "domo"
    BULLET = "bullet"
    FISH_EYE = "fish_eye"
    TERMICA = "termica"
    INFRARROJA = "infrarroja"


class ConnectionType(enum.Enum):
    """Tipos de conexión de cámaras."""
    ETHERNET = "ethernet"
    WIFI = "wifi"
    COAXIAL = "coaxial"
    FIBRA_OPTICA = "fibra_optica"
    INALAMBRICO = "inalambrico"


class Camara(BaseModel, db.Model):
    """
    Modelo de cámaras de seguridad.
    
    Attributes:
        name (str): Nombre identificador de la cámara
        model (str): Modelo de la cámara
        manufacturer (str): Fabricante
        camera_type (str): Tipo de cámara
        ip_address (str): Dirección IP de la cámara
        mac_address (str): Dirección MAC
        port (int): Puerto de conexión
        resolution (str): Resolución de video
        frame_rate (int): Frames por segundo
        codec (str): Codec de video
        connection_type (str): Tipo de conexión
        power_over_ethernet (bool): Soporta PoE
        nvr_id (int): ID del NVR/DVR al que está conectada
        ubicacion_id (int): ID de la ubicación donde está instalada
        status (str): Estado actual de la cámara
        is_recording (bool): Si está grabando actualmente
        last_heartbeat (datetime): Último latido de la cámara
        firmware_version (str): Versión del firmware
        stream_url (str): URL del stream de video
        image_url (str): URL de captura de imagen
        detection_area (str): Área de detección configurada
        motion_detection (bool): Tiene detección de movimiento
        night_vision (bool): Tiene visión nocturna
        infrared_leds (bool): Tiene LEDs infrarrojos
        pan_range (int): Rango de pan en grados
        tilt_range (int): Rango de tilt en grados
        zoom_capabilities (str): Capacidades de zoom
        weather_resistant (bool): Resistente a la intemperie
        operating_temperature (str): Temperatura de operación
        power_consumption (float): Consumo de energía en watts
        notes (str): Notas adicionales
    """
    
    __tablename__ = 'camaras'
    
    # Información básica
    name = Column(String(100), nullable=False, index=True,
                 comment="Nombre identificador de la cámara")
    model = Column(String(50), nullable=True,
                  comment="Modelo de la cámara")
    manufacturer = Column(String(50), nullable=True,
                         comment="Fabricante de la cámara")
    camera_type = Column(Enum(CameraType), nullable=False,
                        comment="Tipo de cámara")
    
    # Conexión de red
    ip_address = Column(String(45), nullable=True, index=True,
                       comment="Dirección IP de la cámara")
    mac_address = Column(String(17), nullable=True, unique=True,
                        comment="Dirección MAC de la cámara")
    port = Column(Integer, nullable=True,
                 comment="Puerto de conexión")
    connection_type = Column(Enum(ConnectionType), nullable=False,
                            comment="Tipo de conexión de red")
    power_over_ethernet = Column(Boolean, default=False, nullable=False,
                                comment="Soporta Power over Ethernet")
    
    # Configuración de video
    resolution = Column(String(20), nullable=True,
                       comment="Resolución de video (ej: 1920x1080)")
    frame_rate = Column(Integer, nullable=True,
                       comment="Frames por segundo")
    codec = Column(String(20), nullable=True,
                  comment="Codec de video (ej: H.264, H.265)")
    
    # Relaciones
    nvr_id = Column(Integer, ForeignKey('nvrs.id'), nullable=True,
                   comment="ID del NVR/DVR al que está conectada")
    ubicacion_id = Column(Integer, ForeignKey('ubicaciones.id'), nullable=True,
                         comment="ID de la ubicación donde está instalada")
    
    # Estado y monitoreo
    status = Column(String(20), nullable=False, default=CameraStatus.OFFLINE,
                   comment="Estado actual de la cámara")
    is_recording = Column(Boolean, default=False, nullable=False,
                         comment="Si está grabando actualmente")
    last_heartbeat = Column(DateTime, nullable=True,
                           comment="Último latido de la cámara (heartbeat)")
    firmware_version = Column(String(20), nullable=True,
                             comment="Versión del firmware")
    
    # URLs y streams
    stream_url = Column(String(500), nullable=True,
                       comment="URL del stream de video")
    image_url = Column(String(500), nullable=True,
                      comment="URL para capturar imágenes")
    
    # Configuraciones avanzadas
    detection_area = Column(Text, nullable=True,
                           comment="Área de detección configurada (coordenadas)")
    motion_detection = Column(Boolean, default=True, nullable=False,
                             comment="Tiene detección de movimiento habilitada")
    night_vision = Column(Boolean, default=False, nullable=False,
                         comment="Tiene capacidad de visión nocturna")
    infrared_leds = Column(Boolean, default=False, nullable=False,
                          comment="Tiene LEDs infrarrojos")
    
    # Capacidades PTZ (para cámaras PTZ)
    pan_range = Column(Integer, nullable=True,
                      comment="Rango de pan en grados")
    tilt_range = Column(Integer, nullable=True,
                       comment="Rango de tilt en grados")
    zoom_capabilities = Column(String(50), nullable=True,
                              comment="Capacidades de zoom")
    
    # Especificaciones físicas
    weather_resistant = Column(Boolean, default=False, nullable=False,
                              comment="Resistente a la intemperie")
    operating_temperature = Column(String(50), nullable=True,
                                  comment="Temperatura de operación")
    power_consumption = Column(Float, nullable=True,
                              comment="Consumo de energía en watts")
    
    # Metadatos
    notes = Column(Text, nullable=True,
                  comment="Notas adicionales")
    
    # Relaciones
    created_by_user = relationship("Usuario", back_populates="created_camaras")
    ubicacion = relationship("Ubicacion", back_populates="camaras")
    nvr = relationship("NVR", back_populates="camaras")
    
    # Relaciones con otros modelos
    fallas = relationship("Falla", back_populates="camara", cascade="all, delete-orphan")
    mantenimientos = relationship("Mantenimiento", back_populates="camara", cascade="all, delete-orphan")
    fotografias = relationship("Fotografia", back_populates="camara", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Camara(name='{self.name}', ip='{self.ip_address}')>"
    
    def is_online(self):
        """
        Verifica si la cámara está en línea.
        
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
        self.status = CameraStatus.ONLINE if self.status != CameraStatus.MANTENIMIENTO else self.status
        self.save()
    
    def get_connection_string(self):
        """
        Obtiene la cadena de conexión completa.
        
        Returns:
            str: Cadena de conexión
        """
        if self.ip_address and self.port:
            return f"{self.ip_address}:{self.port}"
        return self.ip_address
    
    def get_manufacturer_model(self):
        """
        Obtiene el fabricante y modelo en una cadena.
        
        Returns:
            str: Fabricante y modelo
        """
        if self.manufacturer and self.model:
            return f"{self.manufacturer} {self.model}"
        return self.model or self.manufacturer or "Sin especificar"
    
    def get_falla_count(self):
        """
        Obtiene el número de fallas registradas para esta cámara.
        
        Returns:
            int: Número de fallas
        """
        return len(self.fallas)
    
    def get_active_falla_count(self):
        """
        Obtiene el número de fallas activas para esta cámara.
        
        Returns:
            int: Número de fallas activas
        """
        from models import FallaStatus
        return len([f for f in self.fallas if f.status in [FallaStatus.ABIERTA, FallaStatus.EN_PROCESO]])
    
    def get_mantenimiento_count(self):
        """
        Obtiene el número de mantenimientos realizados.
        
        Returns:
            int: Número de mantenimientos
        """
        return len(self.mantenimientos)
    
    def get_last_mantenimiento(self):
        """
        Obtiene el último mantenimiento realizado.
        
        Returns:
            Mantenimiento: Último mantenimiento o None
        """
        if not self.mantenimientos:
            return None
        return max(self.mantenimientos, key=lambda m: m.start_date)
    
    @classmethod
    def get_by_location(cls, location_id):
        """
        Obtiene todas las cámaras de una ubicación específica.
        
        Args:
            location_id (int): ID de la ubicación
            
        Returns:
            list: Lista de cámaras en la ubicación
        """
        return cls.query.filter_by(ubicacion_id=location_id, deleted=False).all()
    
    @classmethod
    def get_by_nvr(cls, nvr_id):
        """
        Obtiene todas las cámaras conectadas a un NVR específico.
        
        Args:
            nvr_id (int): ID del NVR
            
        Returns:
            list: Lista de cámaras conectadas al NVR
        """
        return cls.query.filter_by(nvr_id=nvr_id, deleted=False).all()
    
    @classmethod
    def get_online_cameras(cls):
        """
        Obtiene todas las cámaras que están en línea.
        
        Returns:
            list: Lista de cámaras en línea
        """
        from datetime import timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        return cls.query.filter(
            cls.last_heartbeat > cutoff_time,
            cls.deleted == False
        ).all()
    
    @classmethod
    def get_offline_cameras(cls):
        """
        Obtiene todas las cámaras que están fuera de línea.
        
        Returns:
            list: Lista de cámaras fuera de línea
        """
        from datetime import timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        return cls.query.filter(
            (cls.last_heartbeat <= cutoff_time) | (cls.last_heartbeat.is_(None)),
            cls.deleted == False
        ).all()


class CamaraLog(BaseModel, db.Model):
    """
    Log de actividad y cambios en cámaras.
    
    Attributes:
        camara_id (int): ID de la cámara
        event_type (str): Tipo de evento
        old_status (str): Estado anterior
        new_status (str): Estado nuevo
        details (str): Detalles adicionales
        ip_address (str): Dirección IP del evento
    """
    
    __tablename__ = 'camara_logs'
    
    camara_id = Column(Integer, ForeignKey('camaras.id'), nullable=False,
                      comment="ID de la cámara")
    event_type = Column(String(50), nullable=False,
                       comment="Tipo de evento")
    old_status = Column(String(20), nullable=True,
                       comment="Estado anterior de la cámara")
    new_status = Column(String(20), nullable=True,
                       comment="Estado nuevo de la cámara")
    details = Column(Text, nullable=True,
                    comment="Detalles adicionales del evento")
    ip_address = Column(String(45), nullable=True,
                       comment="Dirección IP del evento")
    
    def __repr__(self):
        return f"<CamaraLog(camara_id={self.camara_id}, event='{self.event_type}')>"