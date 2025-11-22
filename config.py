import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'dev-salt-change-in-production'
    
    # ✅ Corregido: Railway usa DATABASE_URL directamente
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://postgres:password@localhost:5432/camaras_ufro'
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'max_overflow': 30
    }

    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV', 'production') != 'development'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_DURATION = timedelta(hours=24)

    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    TIMEZONE = os.environ.get('TIMEZONE', 'America/Santiago')


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])