"""
Enums para el modelo de cámaras de seguridad
Universidad de La Frontera (UFRO)

Enumeraciones para estados y configuraciones de cámaras IP
"""

from enum import Enum


class EstadoCamara(Enum):
    """Estados posibles para una cámara de seguridad"""

    ACTIVO = 'activo'
    INACTIVO = 'inactivo'
    FALLANDO = 'fallando'
    MANTENIMIENTO = 'mantenimiento'
    DADO_BAJA = 'dado_baja'
    CONECTANDO = 'conectando'
    SIN_CONEXION = 'sin_conexion'

    @classmethod
    def obtener_estados_activos(cls):
        """Obtiene los estados que indican actividad normal"""
        return [cls.ACTIVO, cls.CONECTANDO]

    @classmethod
    def obtener_estados_problema(cls):
        """Obtiene los estados que indican problemas"""
        return [cls.FALLANDO, cls.SIN_CONEXION]

    @classmethod
    def obtener_estados_inactivos(cls):
        """Obtiene los estados que indican inactividad"""
        return [cls.INACTIVO, cls.MANTENIMIENTO, cls.DADO_BAJA]

    def get_color_codigo(self):
        """Obtiene el código de color para representación visual"""
        colores = {
            self.ACTIVO: '#28a745', # Verde
            self.CONECTANDO: '#17a2b8', # Azul claro
            self.FALLANDO: '#dc3545', # Rojo
            self.SIN_CONEXION: '#fd7e14', # Naranja
            self.INACTIVO: '#6c757d', # Gris
            self.MANTENIMIENTO: '#ffc107', # Amarillo
            self.DADO_BAJA: '#6f42c1' # Morado
        }
        return colores.get(self, '#6c757d')

    def get_descripcion_larga(self):
        """Obtiene descripción detallada del estado"""
        descripciones = {
            self.ACTIVO: 'Cámara operativa y transmitiendo video normalmente',
            self.CONECTANDO: 'Cámara estableciendo conexión con el sistema',
            self.FALLANDO: 'Cámara con fallas técnicas o mal funcionamiento',
            self.SIN_CONEXION: 'Cámara sin conexión de red o no responde',
            self.INACTIVO: 'Cámara apagada o desactivada manualmente',
            self.MANTENIMIENTO: 'Cámara en mantenimiento preventivo o correctivo',
            self.DADO_BAJA: 'Cámara decommissioned o fuera de servicio permanente'
        }
        return descripciones.get(self, 'Estado no definido')


class ResolucionCamara(Enum):
    """Resoluciones de video soportadas por las cámaras"""

    VGA_640x480 = '640x480'
    HD_720p_1280x720 = '1280x720'
    FULL_HD_1080p_1920x1080 = '1920x1080'
    QHD_1440p_2560x1440 = '2560x1440'
UHD_4K_3840x2160 = '3840x2160'
UHD_8K_7680x4320 = '7680x4320'

    @classmethod
    def obtener_resoluciones_hd(cls):
        """Obtiene resoluciones HD y superiores"""
        return [cls.HD_720p_1280x720, cls.FULL_HD_1080p_1920x1080,
                cls.QHD_1440p_2560x1440, cls.UHD_4K_3840x2160, cls.UHD_8K_7680x4320]

    @classmethod
    def obtener_resoluciones_4k(cls):
        """Obtiene resoluciones 4K y superiores"""
        return [cls.UHD_4K_3840x2160, cls.UHD_8K_7680x4320]

    def get_megapixeles(self):
        """Obtiene la cantidad aproximada de megapíxeles"""
        megapixeles = {
            self.VGA_640x480: 0.3,
            self.HD_720p_1280x720: 0.9,
            self.FULL_HD_1080p_1920x1080: 2.1,
            self.QHD_1440p_2560x1440: 3.7,
            self.UHD_4K_3840x2160: 8.3,
            self.UHD_8K_7680x4320: 33.2
        }
        return megapixeles.get(self, 0)

def get_calidad_recomendada(self):
    """Obtiene la calidad recomendada basada en la resolución"""
    if self in [self.VGA_640x480, self.HD_720p_1280x720]:
        return 'Básica'
    elif self in [self.FULL_HD_1080p_1920x1080, self.QHD_1440p_2560x1440]:
        return 'Buena'
    else:
        return 'Excelente'


class ProtocoloConexion(Enum):
"""Protocolos de conexión para cámaras IP"""

HTTP = 'http'
HTTPS = 'https'
RTSP = 'rtsp'
ONVIF = 'onvif'

    @classmethod
    def obtener_protocolos_web(cls):
        """Obtiene protocolos web (HTTP/HTTPS)"""
        return [cls.HTTP, cls.HTTPS]

    @classmethod
    def obtener_protocolos_streaming(cls):
        """Obtiene protocolos de streaming de video"""
        return [cls.RTSP, cls.ONVIF]


class TipoVisionNocturna(Enum):
    """Tipos de visión nocturna disponibles"""

    INFRARROJA = 'infrarroja'
WDR = 'wdr'
STARLIGHT = 'starlight'
COLOR_VU = 'color_vu'
HIBRIDA = 'hibrida'

    def get_descripcion(self):
        """Obtiene descripción del tipo de visión nocturna"""
        descripciones = {
                    self.INFRARROJA: 'LEDs infrarrojos para visión nocturna en blanco y negro',
            self.WDR: 'Wide Dynamic Range para condiciones de alto contraste',
            self.STARLIGHT: 'Tecnología starlight para color en baja iluminación',
            self.COLOR_VU: 'Color Vision para mantener colores en oscuridad',
            self.HIBRIDA: 'Combinación de múltiples tecnologías'
        }
        return descripciones.get(self, 'Tipo no definido')