from enum import Enum


class MantenimientoStatus(Enum):
    PROGRAMADO = 'programado'
    PENDIENTE = 'pendiente'
    ASIGNADO = 'asignado'
    EN_PROCESO = 'en_proceso'
    COMPLETADO = 'completado'
    CANCELADO = 'cancelado'
    REPROGRAMADO = 'reprogramado'