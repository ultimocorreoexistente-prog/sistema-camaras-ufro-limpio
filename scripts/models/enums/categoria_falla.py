"""
Enumeraciones para categorías de fallas del sistema.
"""

class CategoriaFalla:
    """Categorías estándar para tipos de fallas."""
    
    HARDWARE = "hardware"
    SOFTWARE = "software"
    CONECTIVIDAD = "conectividad"
    ALIMENTACION = "alimentacion"
    SISTEMA = "sistema"
    CONFIGURACION = "configuracion"
    MANTENIMIENTO = "mantenimiento"
    SEGURIDAD = "seguridad"
    RENDIMIENTO = "rendimiento"
    DISPONIBILIDAD = "disponibilidad"
    
    @classmethod
    def get_choices(cls):
        """Obtiene las opciones disponibles como lista de tuplas."""
        return [
            (cls.HARDWARE, "Hardware"),
            (cls.SOFTWARE, "Software"),
            (cls.CONECTIVIDAD, "Conectividad"),
            (cls.ALIMENTACION, "Alimentación"),
            (cls.SISTEMA, "Sistema"),
            (cls.CONFIGURACION, "Configuración"),
            (cls.MANTENIMIENTO, "Mantenimiento"),
            (cls.SEGURIDAD, "Seguridad"),
            (cls.RENDIMIENTO, "Rendimiento"),
            (cls.DISPONIBILIDAD, "Disponibilidad")
        ]
    
    @classmethod
    def get_values(cls):
        """Obtiene solo los valores disponibles."""
        return [
            cls.HARDWARE, cls.SOFTWARE, cls.CONECTIVIDAD, cls.ALIMENTACION,
            cls.SISTEMA, cls.CONFIGURACION, cls.MANTENIMIENTO, cls.SEGURIDAD,
            cls.RENDIMIENTO, cls.DISPONIBILIDAD
        ]