import os
from dotenv import load_dotenv
load_dotenv()

class Config:
<<<<<<< HEAD
"""Configuración base para todos los entornos"""

# Configuración básica de Flask
SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

# Configuración de base de datos
# SQLite para desarrollo, PostgreSQL para producción
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///sistema_camaras.db')

# Compatibilidad con Railway PostgreSQL
if DATABASE_URL.startswith('postgres://'):
DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
'pool_size': 0,
'pool_recycle': 300,
'pool_pre_ping': True,
'max_overflow': 30
}

# Configuración de seguridad
SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'dev-salt-change-in-production'
REMEMBER_COOKIE_DURATION = timedelta(hours=4)

# Configuración de uploads
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
MAX_CONTENT_LENGTH = 16 * 104 * 104 # 16MB max file size
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'xls', 'doc', 'docx'}

# Configuración de sesiones
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Configuración de logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')

# Configuración de email (para notificaciones)
MAIL_SERVER = os.environ.get('MAIL_SERVER')
MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# Configuración de la aplicación
APP_NAME = "Sistema de Gestión de Cámaras UFRO"
APP_VERSION = "1.0.0"

# Configuración de Redis (para cache y sesiones)
REDIS_URL = os.environ.get('REDIS_URL')

# Configuración de celery (para tareas asíncronas)
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or REDIS_URL
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or REDIS_URL


class DevelopmentConfig(Config):
"""Configuración para desarrollo"""

DEBUG = True
TESTING = False

# Configuraciones específicas para desarrollo
SQLALCHEMY_ECHO = True # Log queries SQL en desarrollo

# Configuraciones de seguridad relajadas para desarrollo
SESSION_COOKIE_SECURE = False
PREFERRED_URL_SCHEME = 'http'

# Configuración de uploads en desarrollo
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'development')

# Configuración de logging más detallada
LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
"""Configuración para testing"""

DEBUG = False
TESTING = True

# Base de datos en memoria para testing
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Desactivar uploads en testing
UPLOAD_FOLDER = None
WTF_CSRF_ENABLED = False

# Configuraciones de testing
PRESERVE_CONTEXT_ON_EXCEPTION = False
LOG_LEVEL = 'DEBUG'


class StagingConfig(Config):
"""Configuración para staging"""

DEBUG = False
TESTING = False

# Configuraciones de seguridad para staging
SESSION_COOKIE_SECURE = True

# Configuración de logging
LOG_LEVEL = 'INFO'

# Configuración de uploads para staging
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'staging')


class ProductionConfig(Config):
"""Configuración para producción"""

DEBUG = False
TESTING = False

# Configuraciones de seguridad para producción
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'

# Configuración de logging para producción
LOG_LEVEL = 'WARNING'

# Configuración de uploads para producción
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/var/uploads/sistema_camaras')

# Configuración de performance
SQLALCHEMY_POOL_SIZE = 0
SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_POOL_TIMEOUT = 30

# Configuración de seguridad adicional
WTF_CSRF_TIME_LIMIT = 3600 # 1 hora

# Configuración de CORS
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')


# Diccionario de configuraciones
config = {
'development': DevelopmentConfig,
'testing': TestingConfig,
'staging': StagingConfig,
'production': ProductionConfig,
'default': DevelopmentConfig
}


def get_config():
"""
Obtener la configuración basada en la variable de entorno FLASK_ENV

Returns:
Config: Clase de configuración correspondiente
"""
env = os.environ.get('FLASK_ENV', 'development').lower()
return config.get(env, config['default'])


def init_app(app):
"""
Inicializar configuraciones específicas de la aplicación

Args:
app: Aplicación Flask
"""
# Asegurar que la carpeta de uploads existe
if hasattr(app.config, 'UPLOAD_FOLDER') and app.config['UPLOAD_FOLDER']:
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Asegurar que la carpeta de logs existe
log_file = app.config.get('LOG_FILE')
if log_file:
os.makedirs(os.path.dirname(log_file), exist_ok=True)

# Configurar logging
import logging
from logging.handlers import RotatingFileHandler

if not app.debug and not app.testing:
if not os.path.exists('logs'):
os.mkdir('logs')

file_handler = RotatingFileHandler(
log_file or 'logs/sistema_camaras.log',
maxBytes=1040000,
backupCount=10
)
file_handler.setFormatter(logging.Formatter(
'%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
app.logger.addHandler(file_handler)

app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
app.logger.info('Sistema de Gestión de Cámaras UFRO - Iniciando aplicación')


# Configuración específica para Railway/Heroku
def configure_for_platform():
"""
Configuraciones específicas para plataformas de deployment
"""
# Configuración automática para Railway
if os.environ.get('RAILWAY_ENVIRONMENT'):
os.environ.setdefault('FLASK_ENV', 'production')

# Configuración específica para Railway PostgreSQL
if not os.environ.get('DATABASE_URL'):
# Railway proporciona DATABASE_URL automáticamente
database_url = os.environ.get('DATABASE_URL')
if database_url:
os.environ['DATABASE_URL'] = database_url

# Configuración automática para Heroku
if os.environ.get('HEROKU'):
os.environ.setdefault('FLASK_ENV', 'production')

# Configuración específica para Heroku PostgreSQL
if not os.environ.get('DATABASE_URL'):
heroku_db = os.environ.get('HEROKU_POSTGRESQL_URL')
if heroku_db:
os.environ['DATABASE_URL'] = heroku_db


# Ejecutar configuración automática
configure_for_platform()
=======
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise RuntimeError("❌ DATABASE_URL es obligatoria en producción.")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ROLES = ["ADMIN", "TECNICO", "LECTURA"]
    PRIORIDADES = ["ALTA", "MEDIA", "BAJA"]
    ESTADOS_FALLA = ["PENDIENTE", "EN_PROGRESO", "CERRADA"]
    ESTADOS_EQUIPO = ["OPERATIVO", "FALLA_MENOR", "FUERA_DE_SERVICIO"]

class ProductionConfig(Config):
    DEBUG = False

def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    return ProductionConfig() if env == 'production' else Config()
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
