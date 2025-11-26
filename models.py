"""
Módulos de Modelos - Sistema de Cámaras UFRO
Consolida todos los modelos SQLAlchemy para imports simples
"""

# Importar base de datos
from models.base import db

# Importar todos los modelos
from models.usuario import Usuario
from models.camara import Camara
from models.ubicacion import Ubicacion
from models.nvr import NVR
from models.dvr import DVR
from models.switch import Switch
from models.ups import UPS
from models.gabinete import Gabinete
from models.fuente_poder import FuentePoder
from models.falla import Falla
from models.mantenimiento import Mantenimiento
from models.fotografia import Fotografia
from models.historial_estado_equipo import HistorialEstadoEquipo
from models.catalogo_tipo_falla import CatalogoTipoFalla
from models.equipo_tecnico import EquipoTecnico

# Importar enums
from models.enums.equipment_status import EquipmentStatus
from models.enums.estado_camara import EstadoCamara
from models.enums.mantenimiento_status import MantenimientoStatus
from models.enums.gravedad_falla import GravedadFalla
from models.enums.categoria_falla import CategoriaFalla

__all__ = [
    'db',
    'Usuario', 'Camara', 'Ubicacion', 'NVR', 'DVR', 'Switch', 'UPS',
    'Gabinete', 'FuentePoder', 'Falla', 'Mantenimiento', 'Fotografia',
    'HistorialEstadoEquipo', 'CatalogoTipoFalla', 'EquipoTecnico',
    'EquipmentStatus', 'EstadoCamara', 'MantenimientoStatus', 
    'GravedadFalla', 'CategoriaFalla'
]