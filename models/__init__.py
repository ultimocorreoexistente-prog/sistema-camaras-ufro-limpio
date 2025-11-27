import os
import logging
from flask_sqlalchemy import SQLAlchemy

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from .base import (
    db, Usuario, Ubicacion, Camara, Switch, Nvr, Falla, Mantenimiento,
    Rol, Prioridad, EstadoFalla, EstadoEquipo,
    RolEnum, PrioridadEnum, EstadoFallaEnum, EstadoEquipoEnum,
    create_all_tables, seed_initial_data,
    FuentePoder, Gabinete, GabineteEquipment, NetworkConnection,
    EquipmentType, EquipmentStatus
)