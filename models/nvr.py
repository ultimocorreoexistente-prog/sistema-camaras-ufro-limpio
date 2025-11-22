"""
Modelo de NVR (Network Video Recorder) y DVR (Digital Video Recorder).

Incluye gestión de grabadores de video, canales y configuraciones.
"""

from datetime import datetime, timezone
import json
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from models.base import BaseModelMixin, BaseModel
from models.equipo import EquipmentBase, ConnectionType
from models import db, EquipmentStatus
import enum


class NVRSystemType(enum.Enum):
    """Tipos de sistema NVR/DVR."""
    NVR = "nvr"
    DVR = "dvr"
    HVR = "hvr"

class StorageType(enum.Enum):
    """Tipos de almacenamiento."""
    HDD = "hdd"
    SSD = "ssd"
    RAID = "raid"
    NAS = "nas"
    CLOUD = "cloud"

class RecordingQuality(enum.Enum):
    """Calidades de grabación."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


class NVR(EquipmentBase, db.Model):
    """
    Modelo de NVR/DVR para grabación de video. Hereda todos los campos
    comunes (name, ip_address, status, etc.) de EquipmentBase.
    """

    __tablename__ = 'nvrs'
    # id, created_at, updated_at, deleted, y campos técnicos heredados de EquipmentBase

    # Configuración del sistema
    system_type = Column(Enum(NVRSystemType), nullable=False, default=NVRSystemType.NVR.value,
                         comment="Tipo de sistema NVR/DVR")
    channels = Column(Integer, nullable=False, default=0,
                      comment="Número de canales actualmente configurados")
    max_channels = Column(Integer, nullable=False, default=0,
                          comment="Número máximo de canales soportados")

    # Almacenamiento
    storage_type = Column(Enum(StorageType), nullable=True,
                          comment="Tipo de almacenamiento")
    storage_capacity = Column(Integer, nullable=True,
                              comment="Capacidad total de almacenamiento en GB")
    storage_used = Column(Integer, default=0, nullable=False,
                          comment="Almacenamiento utilizado en GB")

    # Configuración de grabación
    recording_mode = Column(String(30), nullable=True,
                            comment="Modo de grabación (continuo, por evento, etc.)")
    default_recording_quality = Column(Enum(RecordingQuality), nullable=True,
                                        comment="Calidad por defecto de grabación")
    recording_schedule = Column(Text, nullable=True,
                                comment="Horario de grabación en formato JSON")
    motion_detection_enabled = Column(Boolean, default=True, nullable=False,
                                      comment="Detección de movimiento habilitada")

    # Entradas/Salidas
    alarm_inputs = Column(Integer, default=0, nullable=False,
                          comment="Número de entradas de alarma")
    alarm_outputs = Column(Integer, default=0, nullable=False,
                           comment="Número de salidas de alarma")

    # Conectividad
    poe_ports = Column(Integer, default=0, nullable=False,
                        comment="Número de puertos PoE")
    max_poe_power = Column(Integer, nullable=True,
                            comment="Potencia máxima PoE en watts")
    network_bandwidth = Column(Integer, nullable=True,
                                comment="Ancho de banda de red en Mbps")

    # Protocolos y compresión
    supported_protocols = Column(Text, nullable=True,
                                 comment="Protocolos soportados en formato JSON")
    video_compression = Column(String(20), nullable=True,
                               comment="Método de compresión de video")
    audio_channels = Column(Integer, default=0, nullable=False,
                            comment="Número de canales de audio")

    # Acceso remoto
    remote_access_enabled = Column(Boolean, default=True, nullable=False,
                                   comment="Acceso remoto habilitado")
    web_port = Column(Integer, nullable=True,
                      comment="Puerto web para acceso remoto")
    rtsp_port = Column(Integer, nullable=True,
                        comment="Puerto RTSP para streaming")
    onvif_enabled = Column(Boolean, default=False, nullable=False,
                            comment="Soporte ONVIF habilitado")

    # Respaldo y RAID
    backup_enabled = Column(Boolean, default=False, nullable=False,
                            comment="Respaldo automático habilitado")
    raid_configuration = Column(String(50), nullable=True,
                                comment="Configuración RAID")
    disk_health_status = Column(String(50), nullable=True,
                                comment="Estado de salud de discos")

    # Actualización y servicios
    firmware_url = Column(String(500), nullable=True,
                          comment="URL para actualización de firmware")
    backup_ftp_server = Column(String(100), nullable=True,
                               comment="Servidor FTP para respaldos")
    backup_schedule = Column(Text, nullable=True,
                             comment="Horario de respaldos en formato JSON")

    # Relaciones
    camaras = relationship("Camara", back_populates="nvr", cascade="all, delete-orphan")
    ubicacion = relationship("Ubicacion", back_populates="nvr_list") 

    # Relaciones con mantenimientos
    mantenimientos = relationship("Mantenimiento", back_populates="nvr", cascade="all, delete-orphan")
    fotografias = relationship("Fotografia", back_populates="nvr", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<NVR(name='{self.name}', type='{self.system_type.value}', channels={self.channels})>"

    def get_storage_usage_percentage(self):
        if not self.storage_capacity or self.storage_capacity == 0:
            return 0
        return round((self.storage_used / self.storage_capacity) * 100, 2)

    def get_available_channels(self):
        return self.max_channels - self.channels

    def can_add_camera(self):
        return self.channels < self.max_channels

    def add_camera(self, camara, session=None):
        """Agrega una cámara al NVR. Requiere pasar la sesión para el commit."""
        if not self.can_add_camera():
            return False
        
        session = session or db.session 

        # 1. Actualizar la cámara con el NVR
        camara.nvr_id = self.id
        session.add(camara)
        
        # 2. Actualizar la cuenta de canales (es más seguro contarlos al final, o simplemente incrementar)
        self.channels = len(self.camaras) + 1 
        session.commit()
        return True

    def remove_camera(self, camara, session=None):
        """Remueve una cámara del NVR. Requiere pasar la sesión para el commit."""
        session = session or db.session

        if camara.nvr_id != self.id:
            return False

        # 1. Actualizar la cámara
        camara.nvr_id = None
        session.add(camara)

        # 2. Actualizar el número de canales
        self.channels = max(0, len(self.camaras) - 1)
        session.commit()
        return True

    def get_cameras_connected(self):
        return self.camaras

    def get_cameras_status_summary(self):
        summary = {
            'total': len(self.camaras),
            'online': 0,
            'offline': 0,
            'maintenance': 0,
            'failing': 0
        }
        for camara in self.camaras:
            # Asume que Camara tiene status y el método is_online() de EquipmentBase
            if camara.status == EquipmentStatus.ACTIVO.value and camara.is_online():
                summary['online'] += 1
            elif camara.status == EquipmentStatus.MANTENIMIENTO.value:
                summary['maintenance'] += 1
            elif camara.status == EquipmentStatus.FALLA.value:
                summary['failing'] += 1
            else:
                summary['offline'] += 1
        return summary

    def get_system_health_score(self):
        score = 100
        storage_usage = self.get_storage_usage_percentage()
        if storage_usage > 90: score -= 30
        elif storage_usage > 80: score -= 15

        camera_summary = self.get_cameras_status_summary()
        if camera_summary['offline'] > 0:
            score -= (camera_summary['offline'] * 10)

        if hasattr(self, 'status') and self.status != EquipmentStatus.ACTIVO.value:
            score -= 10

        if hasattr(self, 'is_online') and not self.is_online():
            score -= 5

        return max(0, min(100, score))

    def get_recording_schedule_dict(self):
        if not self.recording_schedule:
            return None
        try:
            return json.loads(self.recording_schedule)
        except:
            return None

    def set_recording_schedule(self, schedule_dict, session=None):
        """Establece el horario de grabación. Requiere pasar la sesión para el commit."""
        session = session or db.session
        self.recording_schedule = json.dumps(schedule_dict)
        session.commit()

    def is_recording_schedule_active(self, now=None):
        if not now:
            now = datetime.now(timezone.utc)
        
        schedule = self.get_recording_schedule_dict()
        if not schedule:
            return True 
        
        # Lógica de horario simplificada
        return True

    @classmethod
    def get_available_for_cameras(cls, location_id=None):
        query = cls.query.filter(
            cls.channels < cls.max_channels,
            cls.status == EquipmentStatus.ACTIVO.value,
            cls.deleted == False
        )
        if location_id:
            query = query.filter(cls.ubicacion_id == location_id)
        return query.all()

    @classmethod
    def get_storage_usage_summary(cls):
        nvrs = cls.query.filter_by(deleted=False).all()
        summary = []
        for nvr in nvrs:
            usage_pct = nvr.get_storage_usage_percentage()
            summary.append({
                'id': nvr.id,
                'name': nvr.name,
                'capacity_gb': nvr.storage_capacity,
                'used_gb': nvr.storage_used,
                'usage_percentage': usage_pct,
                'status': nvr.status,
                'health_score': nvr.get_system_health_score()
            })
        return summary


class NVRCameraChannel(BaseModelMixin, db.Model):
    """
    Configuración de canales de cámaras en NVRs.
    """
    __tablename__ = 'nvr_camera_channels'
    # id, created_at, updated_at, deleted heredados de BaseModelMixin

    nvr_id = Column(Integer, ForeignKey('nvrs.id'), nullable=False,
                     comment="ID del NVR")
    camara_id = Column(Integer, ForeignKey('camaras.id'), nullable=False,
                       comment="ID de la cámara")
    channel_number = Column(Integer, nullable=False,
                            comment="Número de canal en el NVR")
    recording_enabled = Column(Boolean, default=True, nullable=False,
                               comment="Grabación habilitada para este canal")
    # ... otros campos ...
    
    # ✅ Constraint para asegurar la unicidad del canal por NVR
    __table_args__ = (
        UniqueConstraint('nvr_id', 'channel_number', name='_nvr_channel_uc'),
    )

    # Relaciones
    nvr = relationship("NVR")
    camara = relationship("Camara")

    def __repr__(self):
        return f"<NVRCameraChannel(nvr={self.nvr_id}, channel={self.channel_number}, camera={self.camara_id})>"

    @classmethod
    def get_available_channel_numbers(cls, nvr_id):
        nvr = NVR.query.get(nvr_id)
        if not nvr:
            return []

        existing_channels = cls.query.filter_by(nvr_id=nvr_id, deleted=False).all()
        used_numbers = {ch.channel_number for ch in existing_channels}

        available = []
        for i in range(1, nvr.max_channels + 1):
            if i not in used_numbers:
                available.append(i)

        return available