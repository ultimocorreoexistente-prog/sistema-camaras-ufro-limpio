#!/usr/bin/env python3
"""
Database Setup Script for UFRO Camera System - VERSIÓN CORREGIDA
Soluciona el problema de IndentationError
"""

import logging
import sys
import os
from sqlalchemy import create_engine, text, exc
from sqlalchemy.exc import ProgrammingError, OperationalError

# Configuración básica del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def create_database_engine():
    """Crea y retorna el motor de SQLAlchemy.
    
    INTENTO 1: Usar config.get_config() (versión limpia)
    INTENTO 2: Fallback directo a os.environ (versión robusta)
    """
    
    DB_URL = None
    
    # MÉTODO 1: Intentar usar get_config si está disponible (más limpio)
    try:
        from config import get_config
        app_config = get_config()
        DB_URL = app_config.SQLALCHEMY_DATABASE_URI
        logging.info("✅ DATABASE_URL obtenida desde get_config()")
    except ImportError:
        logging.info("⚠️ get_config() no disponible, usando fallback directo...")
    except Exception as e:
        logging.warning(f"⚠️ Error con get_config(): {e}, usando fallback directo...")
    
    # MÉTODO 2: Fallback directo a variables de entorno (más robusto)
    if not DB_URL:
        DB_URL = os.getenv('DATABASE_URL')
        if DB_URL:
            logging.info("✅ DATABASE_URL obtenida desde os.getenv()")
    
    if not DB_URL:
        logging.critical("❌ FALLO CRÍTICO: No se encontró DATABASE_URL en variables de entorno.")
        logging.critical("🔧 SOLUCIÓN: Configura DATABASE_URL en Railway o en variables de entorno.")
        sys.exit(1)
    
    # Asegurar formato correcto para SQLAlchemy
    if 'postgres://' in DB_URL:
        DB_URL = DB_URL.replace('postgres://', 'postgresql://', 1)
        logging.info("🔄 Convertido postgres:// a postgresql:// para SQLAlchemy")

    logging.info(f"✅ DATABASE_URL detectada: {DB_URL[:50]}...")
    return create_engine(DB_URL)

def run_migrations(engine):
    """Ejecuta migraciones de esquema usando ALTER TABLE IF NOT EXISTS
    Manejo profesional de excepciones y logging detallado
    """
    
    logging.info("⚙️ Iniciando migración de esquema para tablas...")
    
    migrations = [
        # Ubicaciones
        "ALTER TABLE ubicaciones ADD COLUMN IF NOT EXISTS latitud VARCHAR(255);",
        "ALTER TABLE ubicaciones ADD COLUMN IF NOT EXISTS longitud VARCHAR(255);",
        "ALTER TABLE ubicaciones ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
        
        # Usuarios
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
        
        # Cámaras
        "ALTER TABLE camaras ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
        "ALTER TABLE camaras ADD COLUMN IF NOT EXISTS estado VARCHAR(50) DEFAULT 'inactiva';",
        
        # Switches
        "ALTER TABLE switches ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
        
        # NVR/DVR
        "ALTER TABLE nvr_dvr ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
        
        # Gabinetes
        "ALTER TABLE gabinetes ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
        
        # UPS
        "ALTER TABLE ups ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
    ]

    with engine.connect() as connection:
        with connection.begin():
            for sql_command in migrations:
                # Extraer nombre de columna para logging informativo
                try:
                    column_part = sql_command.split('ADD COLUMN IF NOT EXISTS')[1].strip()
                    column_name = column_part.split(' ')[0]
                except IndexError:
                    column_name = "desconocida"
                
                try:
                    connection.execute(text(sql_command))
                    logging.info(f"✅ Migración exitosa: '{column_name}' añadido.")
                    
                except ProgrammingError as e:
                    # Errores de sintaxis SQL o estructura
                    if 'already exists' in str(e):
                        logging.warning(f"⚠️ Columna '{column_name}' ya existe. Continuando...")
                    else:
                        logging.error(f"❌ Error de programación SQL: {e}")
                        logging.error(f"🔍 Comando fallido: {sql_command}")
                        raise e
                        
                except OperationalError as e:
                    # Errores de conexión, permisos, etc.
                    logging.error(f"❌ Error operacional de BD: {e}")
                    logging.error(f"🔍 Comando fallido: {sql_command}")
                    raise e
                    
                except Exception as e:
                    # Captura cualquier otro error no esperado
                    logging.error(f"❌ Error inesperado: {e}")
                    logging.error(f"🔍 Comando fallido: {sql_command}")
                    raise e

def setup_db():
    """Función principal de setup de la base de datos."""
    
    try:
        logging.info("--- INICIO DEL PROCESO DE SETUP DE LA BASE DE DATOS ---")
        
        # Crear motor de BD
        engine = create_database_engine()
        logging.info("✅ Motor de base de datos creado exitosamente")
        
        # Ejecutar migraciones
        run_migrations(engine)
        logging.info("✅ Migraciones ejecutadas exitosamente")
        
        logging.info("🎉 --- SETUP DE LA BASE DE DATOS FINALIZADO EXITOSAMENTE ---")
        logging.info("🌟 El sistema está listo para funcionar en producción")
        
    except Exception as e:
        logging.critical(f"❌ FALLO CRÍTICO EN SETUP: {e}")
        logging.critical("🔧 Revisa que:")
        logging.critical("   1. DATABASE_URL esté correctamente configurada")
        logging.critical("   2. La base de datos PostgreSQL esté accesible")
        logging.critical("   3. Los permisos de conexión sean correctos")
        sys.exit(1)

if __name__ == '__main__':
    setup_db()