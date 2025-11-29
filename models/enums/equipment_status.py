from enum import Enum

class EquipmentStatus(Enum):
    ACTIVO = 'activo'
    INACTIVO = 'inactivo'
    FALLANDO = 'fallando'
    MANTENIMIENTO = 'mantenimiento'
    DADO_BAJA = 'dado_baja'