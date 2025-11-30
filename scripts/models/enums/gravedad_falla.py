"""
Enumeraciones para niveles de gravedad de fallas del sistema.
"""

class GravedadFalla:
    """Niveles de gravedad estándar para tipos de fallas."""

    CRITICA = "critica"
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"
    INFORMATIVA = "informativa"

    @classmethod
    def get_choices(cls):
        """Obtiene las opciones disponibles como lista de tuplas."""
        return [
            (cls.CRITICA, "Crítica"),
            (cls.ALTA, "Alta"),
            (cls.MEDIA, "Media"),
            (cls.BAJA, "Baja"),
            (cls.INFORMATIVA, "Informativa")
        ]

    @classmethod
    def get_values(cls):
        """Obtiene solo los valores disponibles."""
        return [
            cls.CRITICA, cls.ALTA, cls.MEDIA, cls.BAJA, cls.INFORMATIVA
        ]

    @classmethod
    def get_numeric_value(cls, gravedad):
        """
        Convierte gravedad textual a valor numérico para ordenamiento.

        Args:
            gravedad (str): Nivel de gravedad

        Returns:
            int: Valor numérico (mayor = más grave)
        """
        mapping = {
            cls.CRITICA: 5,
            cls.ALTA: 4,
            cls.MEDIA: 3,
            cls.BAJA: 2,
            cls.INFORMATIVA: 1
        }
        return mapping.get(gravedad, 3) # Default media

    @classmethod
    def get_priority_order(cls):
        """Obtiene la lista ordenada por prioridad (más grave primero)."""
        return [cls.CRITICA, cls.ALTA, cls.MEDIA, cls.BAJA, cls.INFORMATIVA]