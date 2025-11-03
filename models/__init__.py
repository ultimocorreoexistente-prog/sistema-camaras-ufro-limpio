"""
Paquete de modelos SQLAlchemy para el sistema de gestión de infraestructura tecnológica.

Este paquete contiene todos los modelos de datos para la gestión completa del sistema:
- Usuarios y autenticación
- Ubicaciones y geolocalización
- Cámaras y equipos de red
- Fallas y mantenimientos
- Fotografías y documentación

Uso:
    from models import db, Usuario, Camara, Falla, Mantenimiento
    
    # Crear una instancia de usuario
    usuario = Usuario(
        username="admin",
        email="admin@example.com",
        role="administrador"
    )
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean, String, Text, Float, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

# Inicializar SQLAlchemy
db = SQLAlchemy()

# Declarative base
Base = declarative_base()


def init_db(app):
    """
    Inicializar la base de datos con la aplicación Flask.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    db.init_app(app)
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()


def reset_db():
    """Reiniciar la base de datos (eliminar todas las tablas y recrearlas)."""
    db.drop_all()
    db.create_all()


def get_db_session():
    """Obtener una sesión de base de datos."""
    return db.session


# Configuración de tipos enum como clases
class UserRole:
    """Roles de usuario del sistema."""
    ADMINISTRADOR = "administrador"
    TECNICO = "tecnico"
    OPERADOR = "operador"
    VISUALIZADOR = "visualizador"


class EquipmentType:
    """Tipos de equipos de red."""
    NVR = "nvr"
    DVR = "dvr"
    SWITCH = "switch"
    UPS = "ups"
    FUENTE_PODER = "fuente_poder"
    GABINETE = "gabinete"
    CAMARA = "camara"


class EquipmentStatus:
    """Estados de los equipos."""
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    MANTENIMIENTO = "mantenimiento"
    FALLIDO = "fallido"
    DADO_BAJA = "dado_baja"


class CameraStatus:
    """Estados de las cámaras."""
    ONLINE = "online"
    OFFLINE = "offline"
    FALLANDO = "fallando"
    MANTENIMIENTO = "mantenimiento"
    FUERA_SERVICIO = "fuera_servicio"


class FallaStatus:
    """Estados de las fallas."""
    ABIERTA = "abierta"
    EN_PROCESO = "en_proceso"
    RESUELTA = "resuelta"
    CERRADA = "cerrada"


class MantenimientoStatus:
    """Estados de los mantenimientos."""
    PROGRAMADO = "programado"
    EN_PROCESO = "en_proceso"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"


class PhotoStatus:
    """Estados de las fotografías."""
    PROCESANDO = "procesando"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"


class PhotoType:
    """Tipos de fotografías."""
    FALLA = "falla"
    MANTENIMIENTO = "mantenimiento"
    INSTALACION = "instalacion"
    DOCUMENTACION = "documentacion"
    OTRO = "otro"


# Importar todos los modelos
from .usuario import Usuario, UsuarioLog, UsuarioRol
from .ubicacion import Ubicacion, UbicacionLog
from .camara import Camara, CamaraLog
from .falla import Falla, FallaHistorial
from .equipo import EquipmentBase, NetworkConnection, ConnectionType
from .nvr import NVR, NVRCameraChannel
from .switch import Switch, SwitchPort, SwitchVLAN
from .ups import UPS, UPSConnectedLoad
from .fuente_poder import FuentePoder, FuentePoderConnection
from .gabinete import Gabinete, GabineteEquipment
from .mantenimiento import Mantenimiento, MantenimientoHistorial
from .fotografia import Fotografia, FotografiaMetadata

# Lista de todos los modelos para facilitar el uso
__all__ = [
    # Base y utilidades
    "db",
    "Base",
    
    # Usuario
    "Usuario",
    "UsuarioLog", 
    "UsuarioRol",
    
    # Ubicación
    "Ubicacion",
    "UbicacionLog",
    
    # Cámara
    "Camara",
    "CamaraLog",
    
    # Falla
    "Falla",
    "FallaHistorial",
    
    # Equipo
    "EquipmentBase",
    "NetworkConnection",
    "ConnectionType",
    
    # NVR
    "NVR",
    "NVRCameraChannel",
    
    # Switch
    "Switch",
    "SwitchPort",
    "SwitchVLAN",
    
    # UPS
    "UPS",
    "UPSConnectedLoad",
    
    # Fuente de Poder
    "FuentePoder",
    "FuentePoderConnection",
    
    # Gabinete
    "Gabinete",
    "GabineteEquipment",
    
    # Mantenimiento
    "Mantenimiento",
    "MantenimientoHistorial",
    
    # Fotografía
    "Fotografia",
    "FotografiaMetadata",
]

# Función para crear todas las tablas
def create_all_tables(engine):
    """
    Crea todas las tablas en la base de datos.
    
    Args:
        engine: Motor de base de datos SQLAlchemy
    """
    Base.metadata.create_all(engine)


# Función para eliminar todas las tablas
def drop_all_tables(engine):
    """
    Elimina todas las tablas de la base de datos.
    
    Args:
        engine: Motor de base de datos SQLAlchemy
    """
    Base.metadata.drop_all(engine)