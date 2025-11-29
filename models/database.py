"""
Archivo de configuración de base de datos.

Este archivo contiene la inicialización del objeto SQLAlchemy (db) para evitar
dependencias circulares entre los modelos.

Soluciona el problema de ImportError donde los modelos intentaban importar
desde models/__init__.py, creando un ciclo de dependencias.
"""

from flask_sqlalchemy import SQLAlchemy
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Inicializar SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """
    Inicializar la base de datos con una aplicación Flask.
    
    Args:
        app: Instancia de Flask
    """
    db.init_app(app)
    logger.info("✅ Base de datos inicializada con SQLAlchemy")
    
    # Importar todos los modelos para registrarlos con SQLAlchemy
    from . import init_models
    init_models()
    
    # Crear todas las tablas
    with app.app_context():
        try:
            logger.info("🏗️ Creando tablas de base de datos...")
            db.create_all()
            logger.info("✅ Tablas creadas exitosamente")
        except Exception as e:
            logger.error(f"❌ Error al crear tablas: {e}")
            raise