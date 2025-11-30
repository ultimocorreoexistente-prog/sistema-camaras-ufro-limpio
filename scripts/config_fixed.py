"""
Configuración para Sistema de Cámaras UFRO
CORRECCIÓN: Conflictos de merge resueltos
"""

import os
from datetime import timedelta

class Config:
    """Configuración base para todos los entornos"""
    
    # Configuración básica de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sistema-camaras-ufro-04-secreto'
    
    # Configuración de base de datos
    # Railway proporciona DATABASE_URL automáticamente
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        # Fallback para desarrollo local
        DATABASE_URL = 'sqlite:///sistema_camaras.db'
    
    # Compatibilidad con Railway PostgreSQL
    if 'postgres://' in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de engine para Railway
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'max_overflow': 20
    }
    
    # Configuración de seguridad
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'sistema-camaras-ufro-salt'
    REMEMBER_COOKIE_DURATION = timedelta(hours=4)
    
    # Configuración de uploads
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'xls', 'doc', 'docx'}
    
    # Configuración de sesiones
    SESSION_COOKIE_SECURE = False  # True en producción con HTTPS
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
    
    # Configuración de Redis (opcional)
    REDIS_URL = os.environ.get('REDIS_URL')
    
    # Configuraciones específicas del negocio
    ROLES = ["ADMIN", "TECNICO", "LECTURA"]
    PRIORIDADES = ["ALTA", "MEDIA", "BAJA"]
    ESTADOS_FALLA = ["PENDIENTE", "EN_PROGRESO", "CERRADA"]
    ESTADOS_EQUIPO = ["OPERATIVO", "FALLA_MENOR", "FUERA_DE_SERVICIO"]
    ESTADOS_CAMARA = ["operativa", "inactiva", "mantenimiento", "fuera_de_servicio"]


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    
    DEBUG = True
    TESTING = False
    
    # Configuraciones específicas para desarrollo
    SQLALCHEMY_ECHO = True  # Log queries SQL en desarrollo
    
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
    """Configuración para producción (Railway)"""
    
    DEBUG = False
    TESTING = False
    
    # Verificar que DATABASE_URL existe en producción
    if not DATABASE_URL:
        raise RuntimeError("❌ DATABASE_URL es obligatoria en producción")
    
    # Configuraciones de seguridad para producción
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Configuración de logging para producción
    LOG_LEVEL = 'WARNING'
    
    # Configuración de uploads para producción
    UPLOAD_FOLDER = '/var/uploads/sistema_camaras'
    
    # Configuración de performance
    SQLALCHEMY_POOL_SIZE = 15
    SQLALCHEMY_POOL_RECYCLE = 3600
    SQLALCHEMY_POOL_TIMEOUT = 30
    
    # Configuración de seguridad adicional
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hora
    
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
        file_handler.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
        app.logger.addHandler(file_handler)
    
    app.logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
    app.logger.info('Sistema de Gestión de Cámaras UFRO - Aplicación configurada')


# Configuración automática para Railway
def configure_for_railway():
    """Configuraciones específicas para Railway"""
    
    # Configuración automática para Railway
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        os.environ.setdefault('FLASK_ENV', 'production')
        
        # Railway proporciona DATABASE_URL automáticamente
        # Si no está configurada, intentar obtenerla de variables específicas
        if not os.environ.get('DATABASE_URL'):
            railway_db_url = os.environ.get('DATABASE_URL')
            if railway_db_url:
                os.environ['DATABASE_URL'] = railway_db_url

# Ejecutar configuración automática
configure_for_railway()
