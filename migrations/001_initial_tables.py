"""
Migraciones de base de datos para el Sistema de Cámaras UFRO.
"""

# Migración inicial - Creación de tablas básicas
def create_initial_tables():
    """Crear las tablas iniciales del sistema."""
    migration_sql = """
    -- Tabla de usuarios
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(100) NOT NULL,
        role VARCHAR(20) DEFAULT 'visitante',
        is_active BOOLEAN DEFAULT TRUE,
        last_login TIMESTAMP,
        profile_image VARCHAR(255),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Tabla de cámaras
    CREATE TABLE IF NOT EXISTS camaras (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        ubicacion VARCHAR(200),
        ip_address VARCHAR(15),
        modelo VARCHAR(100),
        estado VARCHAR(20) DEFAULT 'offline',
        coordenadas VARCHAR(50),
        especificaciones TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Tabla de equipos
    CREATE TABLE IF NOT EXISTS equipos (
        id SERIAL PRIMARY KEY,
        tipo VARCHAR(50) NOT NULL,
        marca VARCHAR(100),
        modelo VARCHAR(100),
        numero_serie VARCHAR(100),
        ubicacion VARCHAR(200),
        estado VARCHAR(20) DEFAULT 'activo',
        especificaciones TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Tabla de fotografías
    CREATE TABLE IF NOT EXISTS fotografias (
        id SERIAL PRIMARY KEY,
        filename VARCHAR(255) NOT NULL,
        original_filename VARCHAR(255) NOT NULL,
        file_path VARCHAR(500) NOT NULL,
        file_size INTEGER,
        mime_type VARCHAR(100),
        categoria VARCHAR(50),
        descripcion TEXT,
        status VARCHAR(20) DEFAULT 'aprobado',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    return migration_sql

# Migración de índices
def create_indexes():
    """Crear índices para mejorar el rendimiento."""
    index_sql = """
    -- Índices para usuarios
    CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
    CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
    CREATE INDEX IF NOT EXISTS idx_usuarios_role ON usuarios(role);

    -- Índices para cámaras
    CREATE INDEX IF NOT EXISTS idx_camaras_estado ON camaras(estado);
    CREATE INDEX IF NOT EXISTS idx_camaras_ubicacion ON camaras(ubicacion);

    -- Índices para equipos
    CREATE INDEX IF NOT EXISTS idx_equipos_tipo ON equipos(tipo);
    CREATE INDEX IF NOT EXISTS idx_equipos_estado ON equipos(estado);

    -- Índices para fotografías
    CREATE INDEX IF NOT EXISTS idx_fotografias_categoria ON fotografias(categoria);
    CREATE INDEX IF NOT EXISTS idx_fotografias_status ON fotografias(status);
    """
    return index_sql

# Función para ejecutar migraciones
def run_migrations():
    """Ejecutar todas las migraciones."""
    print("🔄 Ejecutando migraciones...")
    
    try:
        from app import app, db
        from sqlalchemy import text
        
        with app.app_context():
            # Ejecutar creación de tablas
            db.session.execute(text(create_initial_tables()))
            print("✅ Tablas iniciales creadas")
            
            # Ejecutar creación de índices
            db.session.execute(text(create_indexes()))
            print("✅ Índices creados")
            
            db.session.commit()
            print("✅ Migraciones completadas exitosamente")
            
    except Exception as e:
        print(f"❌ Error ejecutando migraciones: {e}")
        db.session.rollback()

if __name__ == '__main__':
    run_migrations()