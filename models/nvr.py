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
<<<<<<< HEAD
"""Tipos de sistema NVR/DVR."""
NVR = "nvr"
DVR = "dvr"
HVR = "hvr" # Hybrid Video Recorder

=======
    """Tipos de sistema NVR/DVR."""
    NVR = "nvr"
    DVR = "dvr"
    HVR = "hvr"
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4

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


<<<<<<< HEAD
class NVR(EquipmentBase):
"""
Modelo de NVR/DVR para grabación de video.

Attributes:
system_type (str): Tipo de sistema (NVR/DVR/HVR)
channels (int): Número de canales de video
max_channels (int): Número máximo de canales soportados
storage_type (str): Tipo de almacenamiento
storage_capacity (int): Capacidad de almacenamiento en GB
storage_used (int): Almacenamiento utilizado en GB
recording_mode (str): Modo de grabación
default_recording_quality (str): Calidad por defecto
recording_schedule (str): Horario de grabación en JSON
motion_detection_enabled (bool): Detección de movimiento habilitada
alarm_inputs (int): Número de entradas de alarma
alarm_outputs (int): Número de salidas de alarma
poe_ports (int): Número de puertos PoE
max_poe_power (int): Potencia máxima PoE en watts
network_bandwidth (int): Ancho de banda de red en Mbps
supported_protocols (str): Protocolos soportados (JSON)
video_compression (str): Compresión de video
audio_channels (int): Número de canales de audio
remote_access_enabled (bool): Acceso remoto habilitado
web_port (int): Puerto web
rtsp_port (int): Puerto RTSP
onvif_enabled (bool): Soporte ONVIF habilitado
backup_enabled (bool): Respaldo automático habilitado
raid_configuration (str): Configuración RAID
disk_health_status (str): Estado de salud de discos
firmware_url (str): URL de actualización de firmware
backup_ftp_server (str): Servidor FTP para respaldos
backup_schedule (str): Horario de respaldos
"""

__tablename__ = 'nvrs'

# Configuración del sistema
system_type = Column(Enum(NVRSystemType), nullable=False, default=NVRSystemType.NVR,
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
video_compression = Column(String(0), nullable=True,
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
disk_health_status = Column(String(0), nullable=True,
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
ubicacion = relationship("Ubicacion", back_populates="nvr_dvrs")
created_by_user = relationship("Usuario", back_populates="created_equipos")

# Relaciones con mantenimientos
mantenimientos = relationship("Mantenimiento", back_populates="nvr", cascade="all, delete-orphan")
fotografias = relationship("Fotografia", back_populates="nvr", cascade="all, delete-orphan")

def __repr__(self):
return f"<NVR(name='{self.name}', type='{self.system_type.value}', channels={self.channels})>"

def get_storage_usage_percentage(self):
"""
Calcula el porcentaje de almacenamiento utilizado.

Returns:
float: Porcentaje de uso (0-100)
"""
if not self.storage_capacity or self.storage_capacity == 0:
return 0

return round((self.storage_used / self.storage_capacity) * 100, )

def get_available_channels(self):
"""
Obtiene el número de canales disponibles.

Returns:
int: Número de canales disponibles
"""
return self.max_channels - self.channels

def can_add_camera(self):
"""
Verifica si se puede agregar otra cámara.

Returns:
bool: True si se puede agregar cámara
"""
return self.channels < self.max_channels

def add_camera(self, camara):
"""
Agrega una cámara al NVR.

Args:
camara (Camara): Cámara a agregar

Returns:
bool: True si se agregó exitosamente
"""
if not self.can_add_camera():
return False

# Actualizar el número de canales
self.channels += 1
self.save()

# Actualizar la cámara con el NVR
camara.nvr_id = self.id
camara.save()

return True

def remove_camera(self, camara):
"""
Remueve una cámara del NVR.

Args:
camara (Camara): Cámara a remover

Returns:
bool: True si se removió exitosamente
"""
if camara.nvr_id = self.id:
return False

# Actualizar la cámara
camara.nvr_id = None
camara.save()

# Actualizar el número de canales
self.channels = max(0, self.channels - 1)
self.save()

return True

def get_cameras_connected(self):
"""
Obtiene todas las cámaras conectadas a este NVR.

Returns:
list: Lista de cámaras conectadas
"""
return self.camaras

def get_cameras_status_summary(self):
"""
Obtiene un resumen del estado de las cámaras conectadas.

Returns:
dict: Resumen de estados
"""
summary = {
'total': len(self.camaras),
'online': 0,
'offline': 0,
'maintenance': 0,
'failing': 0
}

for camara in self.camaras:
if camara.status == EquipmentStatus.ACTIVO and camara.is_online():
summary['online'] += 1
elif camara.status == EquipmentStatus.MANTENIMIENTO:
summary['maintenance'] += 1
elif camara.status == EquipmentStatus.FALLIDO:
summary['failing'] += 1
else:
summary['offline'] += 1

return summary

def get_total_recording_capacity_days(self):
"""
Calcula los días totales de grabación basado en la capacidad y configuración.

Returns:
int: Días estimados de grabación
"""
if not self.storage_capacity:
return None

# Esta es una estimación simplificada
# En producción se debería calcular basado en:
# - Resolución de cada cámara
# - Calidad de grabación
# - Número de cámaras
# - Horario de grabación

storage_gb = self.storage_capacity
cameras = len(self.camaras)

if cameras == 0:
return 0

# Estimación simplificada: 1GB por día por cámara en calidad media
estimated_days = storage_gb / cameras

return int(estimated_days)

def get_poe_power_usage(self):
"""
Obtiene el uso actual de potencia PoE.

Returns:
float: Potencia utilizada en watts
"""
if not self.poe_ports:
return 0

# Estimación simplificada del consumo por cámara PoE
cameras_poe = [c for c in self.camaras if c.power_over_ethernet]
estimated_power_per_camera = 15 # watts estimados por cámara PoE

return len(cameras_poe) * estimated_power_per_camera

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

def get_recording_schedule_dict(self):
"""
Obtiene el horario de grabación como diccionario.

Returns:
dict: Horario de grabación o None
"""
import json

if not self.recording_schedule:
return None

try:
return json.loads(self.recording_schedule)
except:
return None

def set_recording_schedule(self, schedule_dict):
"""
Establece el horario de grabación.

Args:
schedule_dict (dict): Horario de grabación
"""
import json

self.recording_schedule = json.dumps(schedule_dict)
self.save()

def is_recording_schedule_active(self, now=None):
"""
Verifica si el horario de grabación está activo para la hora actual.

Args:
now (datetime): Fecha y hora a verificar (por defecto: ahora)

Returns:
bool: True si el horario está activo
"""
if not now:
now = datetime.now()

schedule = self.get_recording_schedule_dict()
if not schedule:
return True # Si no hay horario específico, grabar siempre

# Esta es una implementación simplificada
# En producción se debería implementar lógica más compleja de horarios
return True

def get_system_health_score(self):
"""
Calcula un puntaje de salud del sistema (0-100).

Returns:
int: Puntaje de salud del sistema
"""
score = 100

# Penalizar por almacenamiento alto
storage_usage = self.get_storage_usage_percentage()
if storage_usage > 90:
score -= 30
elif storage_usage > 80:
score -= 15

# Penalizar por cámaras offline
camera_summary = self.get_cameras_status_summary()
if camera_summary['offline'] > 0:
score -= (camera_summary['offline'] * 10)

# Penalizar por estado del equipo
if self.status = EquipmentStatus.ACTIVO:
score -= 0

# Penalizar por falta de heartbeat reciente
if not self.is_online():
score -= 5

return max(0, min(100, score))

@classmethod
def get_by_channel_capacity(cls, min_channels):
"""
Obtiene NVRs con capacidad mínima de canales.

Args:
min_channels (int): Número mínimo de canales

Returns:
list: Lista de NVRs que cumplen el criterio
"""
return cls.query.filter(
cls.max_channels >= min_channels,
cls.deleted == False
).all()

@classmethod
def get_available_for_cameras(cls, location_id=None):
"""
Obtiene NVRs disponibles para conectar cámaras.

Args:
location_id (int): ID de ubicación opcional

Returns:
list: Lista de NVRs disponibles
"""
query = cls.query.filter(
cls.channels < cls.max_channels,
cls.status == EquipmentStatus.ACTIVO,
cls.deleted == False
)

if location_id:
query = query.filter(cls.ubicacion_id == location_id)

return query.all()

@classmethod
def get_storage_usage_summary(cls):
"""
Obtiene un resumen del uso de almacenamiento de todos los NVRs.

Returns:
list: Lista de diccionarios con resumen de uso
"""
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


class NVRCameraChannel(BaseModel, db.Model):
"""
Configuración de canales de cámaras en NVRs.

Attributes:
nvr_id (int): ID del NVR
camara_id (int): ID de la cámara
channel_number (int): Número de canal en el NVR
recording_enabled (bool): Grabación habilitada para este canal
motion_detection_enabled (bool): Detección de movimiento para este canal
recording_quality (str): Calidad de grabación específica para este canal
stream_type (str): Tipo de stream (principal/secundario)
"""

__tablename__ = 'nvr_camera_channels'

nvr_id = Column(Integer, ForeignKey('nvrs.id'), nullable=False,
comment="ID del NVR")
camara_id = Column(Integer, ForeignKey('camaras.id'), nullable=False,
comment="ID de la cámara")
channel_number = Column(Integer, nullable=False,
comment="Número de canal en el NVR")
recording_enabled = Column(Boolean, default=True, nullable=False,
comment="Grabación habilitada para este canal")
motion_detection_enabled = Column(Boolean, default=True, nullable=False,
comment="Detección de movimiento para este canal")
recording_quality = Column(Enum(RecordingQuality), nullable=True,
comment="Calidad de grabación específica")
stream_type = Column(String(0), default="main", nullable=False,
comment="Tipo de stream (main/sub)")

# Relaciones
nvr = relationship("NVR")
camara = relationship("Camara")

def __repr__(self):
return f"<NVRCameraChannel(nvr={self.nvr_id}, channel={self.channel_number})>"

@classmethod
def get_by_nvr(cls, nvr_id):
"""
Obtiene todos los canales de un NVR.

Args:
nvr_id (int): ID del NVR

Returns:
list: Lista de canales del NVR
"""
return cls.query.filter_by(nvr_id=nvr_id, deleted=False).all()

@classmethod
def get_by_camera(cls, camara_id):
"""
Obtiene todos los canales de una cámara.

Args:
camara_id (int): ID de la cámara

Returns:
list: Lista de canales de la cámara
"""
return cls.query.filter_by(camara_id=camara_id, deleted=False).all()

@classmethod
def get_available_channel_numbers(cls, nvr_id):
"""
Obtiene números de canal disponibles en un NVR.

Args:
nvr_id (int): ID del NVR

Returns:
list: Lista de números de canal disponibles
"""
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
=======
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
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
