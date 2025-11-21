"""
Paquete de modelos para el Sistema de Cámaras UFRO
Permite: from models import db, Gabinete, Switch, NVR, etc.
"""

# Instancia única compartida de SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Enums compartidos
import enum

class EquipmentStatus(enum.Enum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    MANTENIMIENTO = "mantenimiento"
    BAJA = "baja"
    FALLA = "falla"

class EquipmentType(enum.Enum):
    CAMARA = "camara"
    SWITCH = "switch"
    NVR = "nvr"
    UPS = "ups"
    GABINETE = "gabinete"
    FUENTE_PODER = "fuente_poder"
    MANTENIMIENTO = "mantenimiento"
    FALLA = "falla"

# Importar modelos (solo la arquitectura modular avanzada)
from .usuario import Usuario
from .ubicacion import Ubicacion
from .camara import Camara
from .gabinete import Cabinet as Gabinete, GabineteEquipment
from .switch import Switch
from .puertos_switch import PuertoSwitch
from .nvr import NVR
from .ups import UPS
from .fuente_poder import FuentePoder
from .falla import Falla
from .mantenimiento import Mantenimiento
from .fotografia import Fotografia

# Exportar para imports directos
__all__ = [
    'db',
    'EquipmentStatus',
    'EquipmentType',
    'Usuario',
    'Ubicacion',
    'Camara',
    'Gabinete',
    'GabineteEquipment',
    'Switch',
    'NVR',
    'UPS',
    'FuentePoder',
    'Falla',
    'Mantenimiento',
    'Fotografia'
]

# Funciones de inicialización
def init_models():
    return Usuario, Camara, Gabinete

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        if not Usuario.query.filter_by(email='Charles.Jelvez@ufrontera.cl').first():
            from werkzeug.security import generate_password_hash
            admin = Usuario(
                username='charles.jelvez',
                email='Charles.Jelvez@ufrontera.cl',
                nombre='Charles Jelvez',
                rol='superadmin',
                activo=True
            )
            admin.password_hash = generate_password_hash('Vivita0468')
            db.session.add(admin)
            db.session.commit()
            print("✅ Superadmin creado")