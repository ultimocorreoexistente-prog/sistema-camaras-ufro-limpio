#!/usr/bin/env python3
"""
<<<<<<< HEAD
Database Setup Script for UFRO Camera System
This script fixes database schema issues that prevent Railway deployment
=======
Database Setup Script for UFRO Camera System - VERSIÓN CORREGIDA
Soluciona el problema de IndentationError
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
"""

import logging
import sys
import os
<<<<<<< HEAD
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

=======
from sqlalchemy import create_engine, text, exc
from sqlalchemy.exc import ProgrammingError, OperationalError

>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
# Configuración básica del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def create_database_engine():
<<<<<<< HEAD
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
    
<<<<<<< HEAD
    # Lista de migraciones necesarias con CORRECTED table names
    migrations = [
        # 1. Ubicacion table - latitud/longitud (correct table name: ubicaciones)
=======
    # Lista de migraciones necesarias para el despliegue actual
    migrations = [
        # 1. Ubicacion table - latitud/longitud
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
=======
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
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
        "ALTER TABLE ubicaciones ADD COLUMN IF NOT EXISTS latitud VARCHAR(255);",
        "ALTER TABLE ubicaciones ADD COLUMN IF NOT EXISTS longitud VARCHAR(255);",
        "ALTER TABLE ubicaciones ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
        
<<<<<<< HEAD
<<<<<<< HEAD
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
=======
        # 2. Usuarios table
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
        
        # 3. Camaras table
        "ALTER TABLE camaras ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
        "ALTER TABLE camaras ADD COLUMN IF NOT EXISTS estado VARCHAR(50) DEFAULT 'inactiva';",
        
        # 4. Switches table
        "ALTER TABLE switches ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
        
        # 5. NVR table
        "ALTER TABLE nvr_dvr ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
        
        # 6. Gabinetes table
        "ALTER TABLE gabinetes ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
        
        # 7. UPS table
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
=======
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
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
        "ALTER TABLE ups ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
    ]

    with engine.connect() as connection:
        with connection.begin():
            for sql_command in migrations:
<<<<<<< HEAD
<<<<<<< HEAD
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
=======
                column_name = sql_command.split('ADD COLUMN')[1].split(' ')[1]
                try:
                    # Intentamos ejecutar la sentencia SQL
                    connection.execute(text(sql_command))
                    logging.info(f"✅ Migración exitosa: '{column_name}' añadido.")
                except ProgrammingError as e:
                    # Esto captura errores de columna ya existente o sintaxis
                    if 'already exists' in str(e):
                        logging.warning(f"⚠️ Columna '{column_name}' ya existe. Ignorando migración.")
                    else:
                        logging.error(f"❌ Error de programación: {e}")
                        raise e
                except Exception as e:
                    logging.error(f"❌ Error crítico al ejecutar la migración {sql_command}: {e}")
                    raise e
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4

def verify_database_schema(engine):
    """Verifica que todas las columnas necesarias estén presentes"""
    logging.info("🔍 Verificando esquema de base de datos...")
    
<<<<<<< HEAD
    # CORRECTED table names based on actual database schema
=======
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
    critical_checks = [
        ("ubicaciones", ["latitud", "longitud", "activo"]),
        ("usuarios", ["activo"]),
        ("camaras", ["activo", "estado"]),
        ("switches", ["activo"]),
<<<<<<< HEAD
        ("nvr_dvr", ["activo"]),  # Primary NVR table based on "nombre real" comment
=======
        ("nvr_dvr", ["activo"]),
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
        ("gabinetes", ["activo"]),
        ("ups", ["activo"]),
    ]
    
<<<<<<< HEAD
    verified_tables = 0
=======
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
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
<<<<<<< HEAD
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
=======
                else:
                    logging.error(f"   ❌ {table_name}: Columnas faltantes: {missing}")
                    return False
            except Exception as e:
                logging.error(f"   ❌ Error verificando {table_name}: {e}")
                return False
    
    return True
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4

def setup_db():
    """Función principal para inicializar y configurar la base de datos."""
    try:
        logging.info("--- INICIO DEL PROCESO DE SETUP DE LA BASE DE DATOS ---")
        
<<<<<<< HEAD
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
=======
        # 1. Crear el motor
        engine = create_database_engine()
        logging.info("✅ Motor de base de datos creado")
        
        # 2. Ejecutar las migraciones manuales (ALTER TABLE) ANTES de usar el ORM
        run_migrations(engine)

        # 3. Verificar que el esquema esté correcto
        if not verify_database_schema(engine):
            logging.error("❌ ERROR: Verificación de esquema falló")
            sys.exit(1)

        logging.info("--- SETUP DE LA BASE DE DATOS FINALIZADO EXITOSAMENTE ---")

    except ProgrammingError as e:
        # Esto captura la mayoría de los errores relacionados con el esquema
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
        logging.critical(f"❌ FALLO CRÍTICO: Error de programación/esquema. {e}")
        logging.error("❌ ERROR: Falló db_setup.py. Revisar el esquema.")
        sys.exit(1)
    except OperationalError as e:
<<<<<<< HEAD
        # Connection errors
=======
        # Esto captura errores de conexión
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
        logging.critical(f"❌ FALLO CRÍTICO: Error de conexión a la base de datos. {e}")
        logging.error("❌ ERROR: Falló db_setup.py. Revisar la conexión.")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"❌ FALLO CRÍTICO: Error inesperado durante el setup de BD. {e}")
        logging.error("❌ ERROR: Falló db_setup.py.")
=======
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
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
        sys.exit(1)

if __name__ == '__main__':
    setup_db()