# models/__init__.py
from flask_sqlalchemy import SQLAlchemy

# Instancia única de db
db = SQLAlchemy()

# Importar modelos desde base.py (donde están definidos)
from .base import (
    Rol, Ubicacion, EventoCamara, Ticket, 
    TrazabilidadMantenimiento, Inventario
)

# Importar modelos desde archivos individuales
from .usuario import Usuario  # ✅ Clase de autenticación Flask-Login
from .camara import Camara
from .catalogo_tipo_falla import CatalogoTipoFalla
from .equipo_tecnico import EquipoTecnico
from .falla import Falla
from .falla_comentario import FallaComentario
from .fotografia import Fotografia
from .fuente import Fuente
from .fuente_poder import FuentePoder
from .gabinete import Gabinete
from .historial_estado_equipo import HistorialEstadoEquipo
from .mantenimiento import Mantenimiento
from .network_connections import NetworkConnection
from .nvr import NVR
from .puertos_switch import PuertoSwitch
from .switch import Switch
from .ups import UPS
from .usuario_logs import UsuarioLog

__all__ = [
    'db',
    'Usuario',  # ✅ Clase de autenticación Flask-Login
    'Rol', 'Ubicacion', 'EventoCamara', 'Ticket', 'TrazabilidadMantenimiento', 'Inventario',
    'Camara', 'CatalogoTipoFalla', 'EquipoTecnico', 'Falla', 'FallaComentario', 'Fotografia',
    'Fuente', 'FuentePoder', 'Gabinete', 'HistorialEstadoEquipo', 'Mantenimiento',
    'NetworkConnection', 'NVR', 'PuertoSwitch', 'Switch', 'UPS', 'UsuarioLog'
]