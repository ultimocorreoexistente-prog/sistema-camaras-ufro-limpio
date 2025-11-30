import os
import logging
from dotenv import load_dotenv

# Configurar logging para todo el módulo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno (si existe .env)
try:
    load_dotenv()
except Exception as e:
    logger.warning(f"No se pudo cargar .env: {e}")

class Config:
    """Clase base de configuración de Flask y SQLAlchemy."""
    
    # 🔑 Variables esenciales Railway
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # 🗄️ Base de datos PostgreSQL (Railway)
    # 1. Obtener la URL del entorno
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # ✅ Validación mejorada con fallback suave
    if not DATABASE_URL:
        env = os.environ.get('FLASK_ENV', 'development')
        if env == 'production':
            # ⚠️ Alerta en lugar de crash inmediato
            logger.critical("⚠️ ADVERTENCIA CRÍTICA: DATABASE_URL no encontrada en producción Railway")
            logger.critical("🔧 SOLUCIÓN: Configura DATABASE_URL en las variables de entorno de Railway")
            logger.critical("💡 Usando SQLite temporal como fallback (puede causar problemas)")
            
            # Fallback temporal (no ideal pero permite que la app funcione)
            DATABASE_URL = 'sqlite:///sistema_camaras_temp.db'
            logger.error("❌ CRÍTICO: Aplicación funcionando con SQLite en producción")
        else:
            # Fallback para desarrollo local
            DATABASE_URL = 'sqlite:///sistema_camaras_dev.db'
            logger.info("⚠️ Usando SQLite temporal para desarrollo local")
    
    # 2. Corregir el esquema de URL para SQLAlchemy
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        logger.info("🔄 URL convertida de postgres:// a postgresql:// para SQLAlchemy")
    
    # 🔧 Configuración SQLAlchemy (Usa la URL ya corregida)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 📋 Constantes del sistema
    ROLES = ["ADMIN", "TECNICO", "LECTURA"]
    PRIORIDADES = ["ALTA", "MEDIA", "BAJA"]
    ESTADOS_FALLA = ["PENDIENTE", "EN_PROGRESO", "CERRADA"]
    ESTADOS_EQUIPO = ["OPERATIVO", "FALLA_MENOR", "FUERA_DE_SERVICIO"]
    
    # 📁 Configuración de archivos
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 🔒 Configuración de seguridad mejorada
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # ✅ Validación de configuración al instanciar
    def __init__(self):
        super().__init__()
        self._validar_configuracion()
    
    def _validar_configuracion(self):
        """Valida la configuración al crear la instancia."""
        if not self.SECRET_KEY or self.SECRET_KEY == 'dev-key-change-in-production':
            logger.warning("⚠️ SECRET_KEY no configurada. Usando clave temporal.")
        
        if not self.DATABASE_URL:
            logger.error("❌ CRÍTICO: No hay URL de base de datos configurada")
        else:
            logger.info(f"✅ Base de datos configurada: {self.DATABASE_URL[:30]}...")

class ProductionConfig(Config):
    """🟢 Configuración específica para Railway"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    
    def __init__(self):
        super().__init__()
        logger.info("🚂 Configuración de producción Railway activada")

class DevelopmentConfig(Config):
    """🟡 Configuración para desarrollo local"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    
    def __init__(self):
        # Sobrescribir SQLALCHEMY_DATABASE_URI para desarrollo
        self.SQLALCHEMY_DATABASE_URI = 'sqlite:///sistema_camaras_dev.db'
        super().__init__()
        logger.info("🔧 Configuración de desarrollo local activada")

def get_config():
    """
    🎯 Retorna la instancia de configuración basada en la variable de entorno FLASK_ENV.
    Railway (FLASK_ENV='production') -> ProductionConfig
    Local (FLASK_ENV='development' o no definida) -> DevelopmentConfig
    """
    env = os.environ.get('FLASK_ENV', 'development')
    
    logger.info(f"🔍 Detectado entorno: {env}")
    
    if env == 'production':
        return ProductionConfig()
    else:
        return DevelopmentConfig()

def get_config_safe():
    """
    🔒 Versión segura de get_config() con manejo de errores
    Siempre retorna una configuración válida
    """
    try:
        config = get_config()
        if not config.DATABASE_URL:
            logger.error("❌ Configuración unsafe, usando fallback")
            return DevelopmentConfig()
        return config
    except Exception as e:
        logger.critical(f"❌ Error crítico en configuración: {e}")
        # Fallback de emergencia
        fallback_config = DevelopmentConfig()
        fallback_config.DATABASE_URL = 'sqlite:///emergency.db'
        return fallback_config

# 📝 Diccionario para compatibilidad con app.py (si usa la sintaxis de diccionario)
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}