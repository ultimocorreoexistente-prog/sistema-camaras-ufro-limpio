<<<<<<< HEAD
#/usr/bin/env python3
=======
#!/usr/bin/env python3
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
"""
Script de consolidación de tablas Railway - Versión Git Bash
Charles Jelvez - Sistema Cámaras UFRO

USO DESDE GIT BASH:
1. cd /ruta/a/tu/proyecto
<<<<<<< HEAD
. python scripts/consolidate_railway_db.py
=======
2. python scripts/consolidate_railway_db.py
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
"""

import os
import sys
from pathlib import Path

def check_database_connection():
<<<<<<< HEAD
"""Verificar conexión a la base de datos."""
try:
import psycopg
from urllib.parse import urlparse

# Obtener DATABASE_URL de variables de entorno
database_url = os.getenv('DATABASE_URL')
if not database_url:
print(" DATABASE_URL no encontrada")
print(" Configura tu .env o exporta la variable:")
print(" export DATABASE_URL=postgresql://usuario:password@host:puerto/database")
return None

print(f" DATABASE_URL encontrada: {database_url[:50]}...")
return database_url

except Exception as e:
print(f" Error configurando conexión: {e}")
return None

def execute_consolidation_sql(database_url):
"""Ejecutar consolidación usando psycopg directo."""
try:
import psycopg

# Conectar a la base de datos
conn = psycopg.connect(database_url)
cursor = conn.cursor()

print(" Conectado a la base de datos")

# Verificar estado inicial
print("\n Verificando estado inicial de tablas...")
tables_to_check = [
'fuente_poder', 'fuentes_poder',
'nvr', 'nvr_dvr',
'puerto_switch', 'puertos_switch'
]

for table in tables_to_check:
cursor.execute("SELECT COUNT(*) FROM %s" % table)
count = cursor.fetchone()[0]
status = "EXISTE" if count is not None else "NO EXISTE"
print(f" {table:<0}: {count} registros - {status}")

# Eliminar tablas duplicadas vacías
print("\n Eliminando tablas duplicadas vacías...")
cursor.execute("DROP TABLE IF EXISTS fuente_poder CASCADE")
cursor.execute("DROP TABLE IF EXISTS nvr CASCADE")
cursor.execute("DROP TABLE IF EXISTS puerto_switch CASCADE")
print(" Tablas duplicadas eliminadas")

# Crear/Verificar tablas consolidadas
print("\n Verificando/Creando tablas consolidadas...")

# Tabla fuentes_poder
cursor.execute("""
CREATE TABLE IF NOT EXISTS fuentes_poder (
id SERIAL PRIMARY KEY,
codigo VARCHAR(50) NOT NULL,
nombre VARCHAR(100),
marca VARCHAR(100),
modelo VARCHAR(100),
capacidad VARCHAR(50),
voltaje DECIMAL(5,),
amperaje DECIMAL(5,),
equipos_que_alimenta TEXT,
ubicacion_id INTEGER,
gabinete_id INTEGER,
estado VARCHAR(50),
activo BOOLEAN DEFAULT TRUE,
fecha_alta DATE,
fecha_baja DATE,
motivo_baja TEXT,
observaciones TEXT,
fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Tabla nvr_dvr
cursor.execute("""
CREATE TABLE IF NOT EXISTS nvr_dvr (
id SERIAL PRIMARY KEY,
codigo VARCHAR(50) NOT NULL,
nombre VARCHAR(100),
tipo VARCHAR(50),
marca VARCHAR(100),
modelo VARCHAR(100),
canales_totales INTEGER,
ip VARCHAR(50),
ubicacion_id INTEGER,
gabinete_id INTEGER,
estado VARCHAR(50),
activo BOOLEAN DEFAULT TRUE,
fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
fecha_alta DATE,
fecha_baja DATE,
motivo_baja TEXT,
observaciones TEXT,
latitud DECIMAL(9,6),
longitud DECIMAL(9,6)
)
""")

# Tabla puertos_switch
cursor.execute("""
CREATE TABLE IF NOT EXISTS puertos_switch (
id SERIAL PRIMARY KEY,
switch_id INTEGER NOT NULL,
numero_puerto INTEGER NOT NULL,
camara_id INTEGER,
id_dispositivo INTEGER,
dispositivo_conectado VARCHAR(100),
estado VARCHAR(50),
tipo_conexion VARCHAR(50),
nvr_id INTEGER,
nvr_asociado VARCHAR(100),
puerto_nvr VARCHAR(50),
observaciones TEXT,
fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
print(" Tablas consolidadas creadas/verificadas")

# Verificar resultado final
print("\n Verificación final:")
final_tables = ['fuentes_poder', 'nvr_dvr', 'puertos_switch']
for table in final_tables:
cursor.execute("SELECT COUNT(*) FROM %s" % table)
count = cursor.fetchone()[0]
print(f" {table:<0}: {count} registros")

print("\n CONSOLIDACIÓN COMPLETADA EXITOSAMENTE")
return True

except psycopg.Error as e:
print(f" Error PostgreSQL: {e}")
return False
except Exception as e:
print(f" Error general: {e}")
return False
finally:
try:
cursor.close()
conn.close()
print(" Conexión cerrada")
except:
pass

def main():
"""Función principal."""
print(" CONSOLIDACIÓN DE TABLAS RAILWAY")
print("=" * 50)

# Verificar conexión
database_url = check_database_connection()
if not database_url:
print("\n CONFIGURACIÓN NECESARIA:")
print("1. Ve a tu proyecto Railway")
print(". Copia la DATABASE_URL de tu PostgreSQL")
print("3. Configúrala en tu .env:")
print(" echo DATABASE_URL=postgresql://... >> .env")
return False

# Ejecutar consolidación
success = execute_consolidation_sql(database_url)

if success:
print("\n PRÓXIMOS PASOS:")
print(" 1. Confirma que tu aplicación funciona")
print(" . Verifica que las queries usan las tablas correctas")
print(" 3. Commit y push a GitHub para actualizar Railway")
else:
print("\n LA CONSOLIDACIÓN FALLÓ")
print(" Revisa los errores y vuelve a intentar")

return success

if __name__ == "__main__":
main()
=======
    """Verificar conexión a la base de datos."""
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Obtener DATABASE_URL de variables de entorno
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL no encontrada")
            print("💡 Configura tu .env o exporta la variable:")
            print("   export DATABASE_URL=postgresql://usuario:password@host:puerto/database")
            return None
        
        print(f"✅ DATABASE_URL encontrada: {database_url[:50]}...")
        return database_url
        
    except Exception as e:
        print(f"❌ Error configurando conexión: {e}")
        return None

def execute_consolidation_sql(database_url):
    """Ejecutar consolidación usando psycopg2 directo."""
    try:
        import psycopg2
        
        # Conectar a la base de datos
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🔌 Conectado a la base de datos")
        
        # Verificar estado inicial
        print("\n🔍 Verificando estado inicial de tablas...")
        tables_to_check = [
            'fuente_poder', 'fuentes_poder',
            'nvr', 'nvr_dvr', 
            'puerto_switch', 'puertos_switch'
        ]
        
        for table in tables_to_check:
            cursor.execute("SELECT COUNT(*) FROM %s" % table)
            count = cursor.fetchone()[0]
            status = "EXISTE" if count is not None else "NO EXISTE"
            print(f"   {table:<20}: {count} registros - {status}")
        
        # Eliminar tablas duplicadas vacías
        print("\n🗑️ Eliminando tablas duplicadas vacías...")
        cursor.execute("DROP TABLE IF EXISTS fuente_poder CASCADE")
        cursor.execute("DROP TABLE IF EXISTS nvr CASCADE") 
        cursor.execute("DROP TABLE IF EXISTS puerto_switch CASCADE")
        print("✅ Tablas duplicadas eliminadas")
        
        # Crear/Verificar tablas consolidadas
        print("\n🏗️ Verificando/Creando tablas consolidadas...")
        
        # Tabla fuentes_poder
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fuentes_poder (
                id SERIAL PRIMARY KEY,
                codigo VARCHAR(50) NOT NULL,
                nombre VARCHAR(100),
                marca VARCHAR(100),
                modelo VARCHAR(100),
                capacidad VARCHAR(50),
                voltaje DECIMAL(5,2),
                amperaje DECIMAL(5,2),
                equipos_que_alimenta TEXT,
                ubicacion_id INTEGER,
                gabinete_id INTEGER,
                estado VARCHAR(50),
                activo BOOLEAN DEFAULT TRUE,
                fecha_alta DATE,
                fecha_baja DATE,
                motivo_baja TEXT,
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla nvr_dvr
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nvr_dvr (
                id SERIAL PRIMARY KEY,
                codigo VARCHAR(50) NOT NULL,
                nombre VARCHAR(100),
                tipo VARCHAR(50),
                marca VARCHAR(100),
                modelo VARCHAR(100),
                canales_totales INTEGER,
                ip VARCHAR(50),
                ubicacion_id INTEGER,
                gabinete_id INTEGER,
                estado VARCHAR(50),
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_alta DATE,
                fecha_baja DATE,
                motivo_baja TEXT,
                observaciones TEXT,
                latitud DECIMAL(9,6),
                longitud DECIMAL(9,6)
            )
        """)
        
        # Tabla puertos_switch
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS puertos_switch (
                id SERIAL PRIMARY KEY,
                switch_id INTEGER NOT NULL,
                numero_puerto INTEGER NOT NULL,
                camara_id INTEGER,
                id_dispositivo INTEGER,
                dispositivo_conectado VARCHAR(100),
                estado VARCHAR(50),
                tipo_conexion VARCHAR(50),
                nvr_id INTEGER,
                nvr_asociado VARCHAR(100),
                puerto_nvr VARCHAR(50),
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ Tablas consolidadas creadas/verificadas")
        
        # Verificar resultado final
        print("\n🎯 Verificación final:")
        final_tables = ['fuentes_poder', 'nvr_dvr', 'puertos_switch']
        for table in final_tables:
            cursor.execute("SELECT COUNT(*) FROM %s" % table)
            count = cursor.fetchone()[0]
            print(f"   ✅ {table:<20}: {count} registros")
        
        print("\n🎉 CONSOLIDACIÓN COMPLETADA EXITOSAMENTE")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False
    finally:
        try:
            cursor.close()
            conn.close()
            print("🔒 Conexión cerrada")
        except:
            pass

def main():
    """Función principal."""
    print("🚀 CONSOLIDACIÓN DE TABLAS RAILWAY")
    print("=" * 50)
    
    # Verificar conexión
    database_url = check_database_connection()
    if not database_url:
        print("\n💡 CONFIGURACIÓN NECESARIA:")
        print("1. Ve a tu proyecto Railway")
        print("2. Copia la DATABASE_URL de tu PostgreSQL")
        print("3. Configúrala en tu .env:")
        print("   echo DATABASE_URL=postgresql://... >> .env")
        return False
    
    # Ejecutar consolidación
    success = execute_consolidation_sql(database_url)
    
    if success:
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Confirma que tu aplicación funciona")
        print("   2. Verifica que las queries usan las tablas correctas")
        print("   3. Commit y push a GitHub para actualizar Railway")
    else:
        print("\n❌ LA CONSOLIDACIÓN FALLÓ")
        print("   Revisa los errores y vuelve a intentar")
    
    return success

if __name__ == "__main__":
    main()
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
