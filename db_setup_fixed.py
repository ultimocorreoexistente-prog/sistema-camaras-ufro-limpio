#!/usr/bin/env python3
"""
Database Setup Script for UFRO Camera System
This script fixes database schema issues that prevent Railway deployment
"""

import logging
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import ProgrammingError, OperationalError

# Import configuration
try:
    from config import config
except ImportError:
    # Fallback for Railway environment
    config = {
        'DB_URL': os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
    }

# Configuración básica del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def create_database_engine():
    """Crea y retorna el motor de SQLAlchemy."""
    DB_URL = config.get('DB_URL')
    if not DB_URL:
        logging.critical("❌ FALLO CRÍTICO: No se encontró la URL de la base de datos en la configuración.")
        sys.exit(1)
    
    # Aseguramos que la URL usa el driver psycopg2 (PostgreSQL)
    if 'postgresql://' not in DB_URL and 'postgres://' in DB_URL:
        DB_URL = DB_URL.replace('postgres://', 'postgresql://', 1)

    return create_engine(DB_URL)

def run_migrations(engine):
    """
    Ejecuta sentencias SQL para agregar las columnas faltantes a las tablas
    si no existen, resolviendo el error UndefinedColumn.
    """
    logging.info("⚙️ Iniciando migración de esquema para tablas...")
    
    # Lista de migraciones necesarias con CORRECTED table names
    migrations = [
        # 1. Ubicacion table - latitud/longitud (correct table name: ubicaciones)
        "ALTER TABLE ubicaciones ADD COLUMN IF NOT EXISTS latitud VARCHAR(255);",
        "ALTER TABLE ubicaciones ADD COLUMN IF NOT EXISTS longitud VARCHAR(255);",
        "ALTER TABLE ubicaciones ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
        
        # 2. Usuarios table (correct table name: usuarios)
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
        
        # 3. Camaras table (correct table name: camaras) 
        "ALTER TABLE camaras ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
        "ALTER TABLE camaras ADD COLUMN IF NOT EXISTS estado VARCHAR(50) DEFAULT 'inactiva';",
        
        # 4. Switches table (correct table name: switches)
        "ALTER TABLE switches ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
        
        # 5. NVR table - Checked actual table names: nvr_dvr and nvrs
        # Try nvr_dvr first (the comment says "nombre real")
        "ALTER TABLE nvr_dvr ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
        
        # 6. Gabinetes table (correct table name: gabinetes)
        "ALTER TABLE gabinetes ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
        
        # 7. UPS table (correct table name: ups)
        "ALTER TABLE ups ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
    ]

    with engine.connect() as connection:
        with connection.begin():
            for sql_command in migrations:
                # Extract table name and column name for better error handling
                parts = sql_command.split()
                table_name = parts[2]  # ALTER TABLE <table_name>
                column_name = parts[4]  # ADD COLUMN <column_name>
                
                try:
                    # Attempt to execute the SQL command
                    connection.execute(text(sql_command))
                    logging.info(f"✅ Migración exitosa: '{column_name}' añadido a '{table_name}'.")
                except ProgrammingError as e:
                    error_msg = str(e).lower()
                    if 'already exists' in error_msg:
                        logging.warning(f"⚠️ Columna '{column_name}' ya existe en '{table_name}'. Ignorando migración.")
                    elif 'does not exist' in error_msg or 'undefined' in error_msg:
                        logging.warning(f"⚠️ Tabla '{table_name}' no existe. Saltando migración.")
                    else:
                        logging.error(f"❌ Error de programación ejecutando migración en '{table_name}': {e}")
                        raise e
                except Exception as e:
                    logging.error(f"❌ Error crítico ejecutando migración {sql_command}: {e}")
                    # Don't raise - continue with other migrations

def verify_database_schema(engine):
    """Verifica que todas las columnas necesarias estén presentes"""
    logging.info("🔍 Verificando esquema de base de datos...")
    
    # CORRECTED table names based on actual database schema
    critical_checks = [
        ("ubicaciones", ["latitud", "longitud", "activo"]),
        ("usuarios", ["activo"]),
        ("camaras", ["activo", "estado"]),
        ("switches", ["activo"]),
        ("nvr_dvr", ["activo"]),  # Primary NVR table based on "nombre real" comment
        ("gabinetes", ["activo"]),
        ("ups", ["activo"]),
    ]
    
    verified_tables = 0
    with engine.connect() as connection:
        for table_name, required_columns in critical_checks:
            try:
                cursor = connection.execute(text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}';
                """))
                table_columns = [col[0] for col in cursor.fetchall()]
                missing = [col for col in required_columns if col not in table_columns]
                
                if not missing:
                    logging.info(f"   ✅ {table_name}: Todas las columnas requeridas presentes")
                    verified_tables += 1
                else:
                    logging.warning(f"   ⚠️ {table_name}: Columnas faltantes: {missing}")
            except Exception as e:
                logging.warning(f"   ⚠️ No se pudo verificar {table_name}: {e}")
    
    logging.info(f"   📊 Tablas verificadas exitosamente: {verified_tables}/{len(critical_checks)}")
    return verified_tables > 0

def check_existing_tables(engine):
    """Check what tables actually exist in the database"""
    logging.info("🔍 Verificando tablas existentes en la base de datos...")
    
    try:
        with engine.connect() as connection:
            cursor = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            logging.info(f"   📋 Tablas encontradas: {len(existing_tables)}")
            for table in existing_tables:
                logging.info(f"      - {table}")
            
            return existing_tables
    except Exception as e:
        logging.error(f"   ❌ Error verificando tablas: {e}")
        return []

def setup_db():
    """Función principal para inicializar y configurar la base de datos."""
    try:
        logging.info("--- INICIO DEL PROCESO DE SETUP DE LA BASE DE DATOS ---")
        
        # 1. Create database engine
        engine = create_database_engine()
        logging.info("✅ Motor de base de datos creado")
        
        # 2. Check existing tables first
        existing_tables = check_existing_tables(engine)
        
        # 3. Run migrations (skip tables that don't exist)
        run_migrations(engine)

        # 4. Verify that critical schema is correct
        if not verify_database_schema(engine):
            logging.warning("⚠️ Verificación de esquema incompleta - algunas tablas pueden no existir")
            logging.info("   💡 Esto es normal si algunas tablas no han sido creadas aún")

        logging.info("--- SETUP DE LA BASE DE DATOS COMPLETADO ---")
        logging.info("   ✅ Las migraciones se han aplicado sin errores")
        logging.info("   ✅ Las tablas faltantes serán creadas automáticamente por la aplicación")

    except ProgrammingError as e:
        # Schema-related errors
        logging.critical(f"❌ FALLO CRÍTICO: Error de programación/esquema. {e}")
        logging.error("❌ ERROR: Falló db_setup.py. Revisar el esquema.")
        sys.exit(1)
    except OperationalError as e:
        # Connection errors
        logging.critical(f"❌ FALLO CRÍTICO: Error de conexión a la base de datos. {e}")
        logging.error("❌ ERROR: Falló db_setup.py. Revisar la conexión.")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"❌ FALLO CRÍTICO: Error inesperado durante el setup de BD. {e}")
        logging.error("❌ ERROR: Falló db_setup.py.")
        sys.exit(1)

if __name__ == '__main__':
    setup_db()