# utils/constants.py
"""
Constantes del sistema
Contiene todas las constantes utilizadas en el sistema
"""

from enum import Enum

# Configuración general del sistema
class SystemConfig:
"""Constantes de configuración del sistema"""

SYSTEM_NAME = "Sistema de Cámaras UFRO"
SYSTEM_VERSION = "1.0.0"
SYSTEM_AUTHOR = "Universidad de La Frontera"
DEFAULT_TIMEZONE = "America/Santiago"
DEFAULT_LANGUAGE = "es"

# Límites del sistema
DEFAULT_PAGE_SIZE = 0
MAX_PAGE_SIZE = 100
DEFAULT_CACHE_TIMEOUT = 300 # 5 minutos

# Configuración de archivos
MAX_FILE_SIZE = 50 * 104 * 104 # 50MB
MAX_FILES_PER_REQUEST = 10

# Configuración de sesiones
SESSION_TIMEOUT = 1800 # 30 minutos
REMEMBER_ME_TIMEOUT = 30 * 4 * 3600 # 30 días

# Configuración de API
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"
RATE_LIMIT_PER_MINUTE = 60

# Estados del sistema
class StatusConstants:
"""Constantes de estados"""

# Estados de cámaras
CAMERA_OPERATIVE = "operativa"
CAMERA_OFFLINE = "offline"
CAMERA_MAINTENANCE = "mantenimiento"
CAMERA_ERROR = "error"

CAMERA_STATES = [
CAMERA_OPERATIVE,
CAMERA_OFFLINE,
CAMERA_MAINTENANCE,
CAMERA_ERROR
]

# Estados de switches
SWITCH_OPERATIVE = "operativo"
SWITCH_OFFLINE = "offline"
SWITCH_MAINTENANCE = "mantenimiento"

SWITCH_STATES = [
SWITCH_OPERATIVE,
SWITCH_OFFLINE,
SWITCH_MAINTENANCE
]

# Estados de fallas
FAILURE_OPEN = "abierta"
FAILURE_IN_PROGRESS = "en_progreso"
FAILURE_CLOSED = "cerrada"
FAILURE_CANCELLED = "cancelada"

FAILURE_STATES = [
FAILURE_OPEN,
FAILURE_IN_PROGRESS,
FAILURE_CLOSED,
FAILURE_CANCELLED
]

# Estados de mantenimientos
MAINTENANCE_SCHEDULED = "programado"
MAINTENANCE_IN_PROGRESS = "en_progreso"
MAINTENANCE_COMPLETED = "completado"
MAINTENANCE_CANCELLED = "cancelado"

MAINTENANCE_STATES = [
MAINTENANCE_SCHEDULED,
MAINTENANCE_IN_PROGRESS,
MAINTENANCE_COMPLETED,
MAINTENANCE_CANCELLED
]

# Estados de usuarios
USER_ACTIVE = True
USER_INACTIVE = False

# Tipos y categorías
class TypeConstants:
"""Constantes de tipos"""

# Tipos de cámaras
CAMERA_DOME = "domo"
CAMERA_BULLET = "bullet"
CAMERA_PTZ = "ptz"
CAMERA_FISHEYE = "fisheye"
CAMERA_THERMAL = "thermal"
CAMERA_MOTION = "motion"

CAMERA_TYPES = [
CAMERA_DOME,
CAMERA_BULLET,
CAMERA_PTZ,
CAMERA_FISHEYE,
CAMERA_THERMAL,
CAMERA_MOTION
]

# Tipos de fallas
FAILURE_HARDWARE = "hardware"
FAILURE_SOFTWARE = "software"
FAILURE_NETWORK = "red"
FAILURE_POWER = "alimentacion"
FAILURE_ENVIRONMENTAL = "ambiental"
FAILURE_OTHER = "otros"

FAILURE_TYPES = [
FAILURE_HARDWARE,
FAILURE_SOFTWARE,
FAILURE_NETWORK,
FAILURE_POWER,
FAILURE_ENVIRONMENTAL,
FAILURE_OTHER
]

# Severidades
SEVERITY_LOW = "baja"
SEVERITY_MEDIUM = "media"
SEVERITY_HIGH = "alta"
SEVERITY_CRITICAL = "critica"

SEVERITIES = [
SEVERITY_LOW,
SEVERITY_MEDIUM,
SEVERITY_HIGH,
SEVERITY_CRITICAL
]

# Tipos de mantenimiento
MAINTENANCE_PREVENTIVE = "preventivo"
MAINTENANCE_CORRECTIVE = "correctivo"
MAINTENANCE_PREDICTIVE = "predictivo"
MAINTENANCE_CALIBRATION = "calibracion"

MAINTENANCE_TYPES = [
MAINTENANCE_PREVENTIVE,
MAINTENANCE_CORRECTIVE,
MAINTENANCE_PREDICTIVE,
MAINTENANCE_CALIBRATION
]

# Roles de usuario
ROLE_ADMIN = "admin"
ROLE_TECHNICIAN = "tecnico"
ROLE_USER = "usuario"
ROLE_VIEWER = "visualizador"

USER_ROLES = [
ROLE_ADMIN,
ROLE_TECHNICIAN,
ROLE_USER,
ROLE_VIEWER
]

# Categorías de ubicaciones
LOCATION_BUILDING = "edificio"
LOCATION_OUTDOOR = "exterior"
LOCATION_PARKING = "estacionamiento"
LOCATION_COMMON = "areas_comunes"
LOCATION_RESTRICTED = "restringidas"

LOCATION_CATEGORIES = [
LOCATION_BUILDING,
LOCATION_OUTDOOR,
LOCATION_PARKING,
LOCATION_COMMON,
LOCATION_RESTRICTED
]

# Configuración de formatos
class FormatConstants:
"""Constantes de formatos"""

# Formatos de fecha
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"
DISPLAY_DATE_FORMAT = "%d/%m/%Y"
DISPLAY_DATETIME_FORMAT = "%d/%m/%Y %H:%M"
ISO_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

# Formatos de archivos
SUPPORTED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']
SUPPORTED_VIDEO_FORMATS = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv']
SUPPORTED_DOCUMENT_FORMATS = ['pdf', 'doc', 'docx', 'txt', 'csv', 'xlsx', 'xls']
SUPPORTED_EXPORT_FORMATS = ['xlsx', 'csv', 'pdf', 'json']

# Configuración de exportación
EXPORT_PAGE_SIZE = 1000
MAX_EXPORT_RECORDS = 10000

# Configuración de red
class NetworkConstants:
"""Constantes de red"""

# Puertos comunes
HTTP_PORT = 80
HTTPS_PORT = 443
FTP_PORT = 1
SSH_PORT =
TELNET_PORT = 3
SMTP_PORT = 5
DNS_PORT = 53
SNMP_PORT = 161

# Protocolos
PROTOCOL_HTTP = "http"
PROTOCOL_HTTPS = "https"
PROTOCOL_RTSP = "rtsp"
PROTOCOL_RTP = "rtp"
PROTOCOL_ONVIF = "onvif"

# Interfaces de red
INTERFACE_ETHERNET = "ethernet"
INTERFACE_WIFI = "wifi"
INTERFACE_FIBER = "fibra"
INTERFACE_WIRELESS = "inalambrico"

INTERFACE_TYPES = [
INTERFACE_ETHERNET,
INTERFACE_WIFI,
INTERFACE_FIBER,
INTERFACE_WIRELESS
]

# Configuración de notificaciones
class NotificationConstants:
"""Constantes de notificaciones"""

# Tipos de notificación
NOTIFICATION_INFO = "info"
NOTIFICATION_WARNING = "warning"
NOTIFICATION_ERROR = "error"
NOTIFICATION_SUCCESS = "success"
NOTIFICATION_FAILURE = "failure"
NOTIFICATION_MAINTENANCE = "maintenance"

NOTIFICATION_TYPES = [
NOTIFICATION_INFO,
NOTIFICATION_WARNING,
NOTIFICATION_ERROR,
NOTIFICATION_SUCCESS,
NOTIFICATION_FAILURE,
NOTIFICATION_MAINTENANCE
]

# Canales de notificación
CHANNEL_EMAIL = "email"
CHANNEL_SMS = "sms"
CHANNEL_SYSTEM = "sistema"
CHANNEL_PUSH = "push"

NOTIFICATION_CHANNELS = [
CHANNEL_EMAIL,
CHANNEL_SMS,
CHANNEL_SYSTEM,
CHANNEL_PUSH
]

# Prioridades
PRIORITY_LOW = "baja"
PRIORITY_NORMAL = "normal"
PRIORITY_HIGH = "alta"
PRIORITY_URGENT = "urgente"

NOTIFICATION_PRIORITIES = [
PRIORITY_LOW,
PRIORITY_NORMAL,
PRIORITY_HIGH,
PRIORITY_URGENT
]

# Configuración de reportes
class ReportConstants:
"""Constantes de reportes"""

# Tipos de reporte
REPORT_DASHBOARD = "dashboard"
REPORT_FAILURE_ANALYSIS = "analisis_fallas"
REPORT_MAINTENANCE = "mantenimiento"
REPORT_INVENTORY = "inventario"
REPORT_PERFORMANCE = "rendimiento"
REPORT_COMPLIANCE = "cumplimiento"

REPORT_TYPES = [
REPORT_DASHBOARD,
REPORT_FAILURE_ANALYSIS,
REPORT_MAINTENANCE,
REPORT_INVENTORY,
REPORT_PERFORMANCE,
REPORT_COMPLIANCE
]

# Períodos de reporte
PERIOD_DAILY = "diario"
PERIOD_WEEKLY = "semanal"
PERIOD_MONTHLY = "mensual"
PERIOD_QUARTERLY = "trimestral"
PERIOD_YEARLY = "anual"
PERIOD_CUSTOM = "personalizado"

REPORT_PERIODS = [
PERIOD_DAILY,
PERIOD_WEEKLY,
PERIOD_MONTHLY,
PERIOD_QUARTERLY,
PERIOD_YEARLY,
PERIOD_CUSTOM
]

# Configuración de logs
class LogConstants:
"""Constantes de logs"""

# Niveles de log
LEVEL_DEBUG = "DEBUG"
LEVEL_INFO = "INFO"
LEVEL_WARNING = "WARNING"
LEVEL_ERROR = "ERROR"
LEVEL_CRITICAL = "CRITICAL"

LOG_LEVELS = [
LEVEL_DEBUG,
LEVEL_INFO,
LEVEL_WARNING,
LEVEL_ERROR,
LEVEL_CRITICAL
]

# Categorías de log
CATEGORY_SYSTEM = "system"
CATEGORY_SECURITY = "security"
CATEGORY_PERFORMANCE = "performance"
CATEGORY_ERROR = "error"
CATEGORY_AUDIT = "audit"

LOG_CATEGORIES = [
CATEGORY_SYSTEM,
CATEGORY_SECURITY,
CATEGORY_PERFORMANCE,
CATEGORY_ERROR,
CATEGORY_AUDIT
]

# Mensajes del sistema
class MessageConstants:
"""Constantes de mensajes"""

# Mensajes de éxito
SUCCESS_SAVED = "Datos guardados exitosamente"
SUCCESS_UPDATED = "Datos actualizados exitosamente"
SUCCESS_DELETED = "Elemento eliminado exitosamente"
SUCCESS_PROCESSED = "Proceso completado exitosamente"

# Mensajes de error
ERROR_NOT_FOUND = "Elemento no encontrado"
ERROR_INVALID_DATA = "Datos inválidos"
ERROR_PERMISSION_DENIED = "Permisos insuficientes"
ERROR_DATABASE = "Error en la base de datos"
ERROR_NETWORK = "Error de conexión"
ERROR_FILE_UPLOAD = "Error al subir archivo"
ERROR_VALIDATION = "Error de validación"

# Mensajes de advertencia
WARNING_UNSAVED_CHANGES = "Hay cambios sin guardar"
WARNING_DATA_LOSS = "Esta acción eliminará datos permanentemente"
WARNING_DEPRECATED = "Esta funcionalidad está deprecada"

# Mensajes informativos
INFO_PROCESSING = "Procesando solicitud..."
INFO_LOADING = "Cargando datos..."
INFO_NO_DATA = "No hay datos disponibles"
INFO_REQUIRED_FIELD = "Este campo es requerido"

# Expresiones regulares
class RegexConstants:
"""Constantes de expresiones regulares"""

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{,}$'
IP_REGEX = r'^(\d{1,3}\.){3}\d{1,3}$'
MAC_REGEX = r'^([0-9A-Fa-f]{}[:-]){5}([0-9A-Fa-f]{})$'
PHONE_REGEX = r'^\+?[\d\s\-\(\)]{8,15}$'
UUID_REGEX = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{1}$'

# Patrones de nombres de archivo
FILENAME_REGEX = r'^[a-zA-Z0-9\.\-_ ]+$'

# Patrones de coordenadas
COORDINATE_REGEX = r'^[-+]?\d*\.?\d+$'

# Configuración de base de datos
class DatabaseConstants:
"""Constantes de base de datos"""

# Tipos de datos
TYPE_VARCHAR = "VARCHAR"
TYPE_TEXT = "TEXT"
TYPE_INTEGER = "INTEGER"
TYPE_BIGINT = "BIGINT"
TYPE_DECIMAL = "DECIMAL"
TYPE_BOOLEAN = "BOOLEAN"
TYPE_TIMESTAMP = "TIMESTAMP"
TYPE_DATE = "DATE"
TYPE_JSON = "JSON"
TYPE_UUID = "UUID"

# Configuración de paginación
PAGINATION_DEFAULT_SIZE = 0
PAGINATION_MAX_SIZE = 100
PAGINATION_MIN_SIZE = 5

# Configuración de índices
INDEX_NAME_PREFIX = "idx_"
UNIQUE_INDEX_PREFIX = "uk_"
FOREIGN_KEY_PREFIX = "fk_"

# Configuración de cache
class CacheConstants:
"""Constantes de cache"""

# Keys de cache
CACHE_USER_SESSION = "user_session"
CACHE_SYSTEM_CONFIG = "system_config"
CACHE_DASHBOARD_DATA = "dashboard_data"
CACHE_CAMERA_STATUS = "camera_status"
CACHE_TOPOLOGY = "topology"

# TTL por defecto (en segundos)
DEFAULT_TTL = 300 # 5 minutos
SHORT_TTL = 60 # 1 minuto
MEDIUM_TTL = 600 # 10 minutos
LONG_TTL = 3600 # 1 hora

# Configuración de limpieza
CLEANUP_INTERVAL = 3600 # 1 hora

# Configuración de monitoreo
class MonitoringConstants:
"""Constantes de monitoreo"""

# Umbrales
CPU_WARNING_THRESHOLD = 70
CPU_CRITICAL_THRESHOLD = 90

MEMORY_WARNING_THRESHOLD = 75
MEMORY_CRITICAL_THRESHOLD = 90

DISK_WARNING_THRESHOLD = 80
DISK_CRITICAL_THRESHOLD = 90

NETWORK_WARNING_THRESHOLD = 80
NETWORK_CRITICAL_THRESHOLD = 95

# Intervalos de monitoreo
MONITOR_INTERVAL = 60 # 1 minuto
HEALTH_CHECK_INTERVAL = 300 # 5 minutos

# Estados de salud
HEALTH_OK = "ok"
HEALTH_WARNING = "warning"
HEALTH_CRITICAL = "critical"
HEALTH_UNKNOWN = "unknown"

# Configuración de topología
class TopologyConstants:
"""Constantes de topología"""

# Tipos de dispositivos
DEVICE_NVR = "nvr"
DEVICE_SWITCH = "switch"
DEVICE_CAMERA = "camara"
DEVICE_SERVER = "servidor"
DEVICE_ROUTER = "router"
DEVICE_FIREWALL = "firewall"

DEVICE_TYPES = [
DEVICE_NVR,
DEVICE_SWITCH,
DEVICE_CAMERA,
DEVICE_SERVER,
DEVICE_ROUTER,
DEVICE_FIREWALL
]

# Relaciones
RELATION_CONNECTED = "conectado"
RELATION_MANAGES = "gestiona"
RELATION_MONITORS = "monitorea"
RELATION_CONTAINS = "contiene"

RELATION_TYPES = [
RELATION_CONNECTED,
RELATION_MANAGES,
RELATION_MONITORS,
RELATION_CONTAINS
]

# Rutas y endpoints
class RouteConstants:
"""Constantes de rutas"""

# Rutas principales
ROUTE_DASHBOARD = "/dashboard"
ROUTE_CAMERAS = "/camaras"
ROUTE_SWITCHES = "/switches"
ROUTE_FAILURES = "/fallas"
ROUTE_MAINTENANCE = "/mantenimiento"
ROUTE_REPORTS = "/reportes"
ROUTE_ADMIN = "/admin"

# APIs
API_CAMERAS = "/api/v1/camaras"
API_SWITCHES = "/api/v1/switches"
API_FAILURES = "/api/v1/fallas"
API_MAINTENANCE = "/api/v1/mantenimiento"
API_REPORTS = "/api/v1/reports"
API_NOTIFICATIONS = "/api/v1/notifications"

# Autenticación
ROUTE_LOGIN = "/login"
ROUTE_LOGOUT = "/logout"
ROUTE_REGISTER = "/register"
ROUTE_FORGOT_PASSWORD = "/forgot-password"

# Configuración de seguridad
class SecurityConstants:
"""Constantes de seguridad"""

# Algoritmos de hash
HASH_ALGORITHM = "sha56"
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_SPECIAL = True
PASSWORD_REQUIRE_NUMBER = True
PASSWORD_REQUIRE_UPPER = True
PASSWORD_REQUIRE_LOWER = True

# Configuración de sesión
SESSION_COOKIE_NAME = "ufro_session"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# CORS
CORS_ORIGINS = ["*"]
CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_HEADERS = ["Content-Type", "Authorization", "X-Requested-With"]

# Estados de sistema
class SystemStatus:
"""Constantes de estado del sistema"""

STATUS_ONLINE = "online"
STATUS_OFFLINE = "offline"
STATUS_MAINTENANCE = "maintenance"
STATUS_ERROR = "error"
STATUS_DEGRADED = "degradado"

SYSTEM_STATUSES = [
STATUS_ONLINE,
STATUS_OFFLINE,
STATUS_MAINTENANCE,
STATUS_ERROR,
STATUS_DEGRADED
]

# Exportar todas las constantes
__all__ = [
# Configuración
'SystemConfig',

# Estados
'StatusConstants',

# Tipos
'TypeConstants',

# Formatos
'FormatConstants',

# Red
'NetworkConstants',

# Notificaciones
'NotificationConstants',

# Reportes
'ReportConstants',

# Logs
'LogConstants',

# Mensajes
'MessageConstants',

# Expresiones regulares
'RegexConstants',

# Base de datos
'DatabaseConstants',

# Cache
'CacheConstants',

# Monitoreo
'MonitoringConstants',

# Topología
'TopologyConstants',

# Rutas
'RouteConstants',

# Seguridad
'SecurityConstants',

# Estado del sistema
'SystemStatus'
]