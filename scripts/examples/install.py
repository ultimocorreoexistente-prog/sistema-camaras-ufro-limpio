<<<<<<< HEAD
#/usr/bin/env python3
=======
#!/usr/bin/env python3
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
"""
Script de instalación y migración de la base de datos.

Este script crea todas las tablas necesarias para el sistema de gestión
de infraestructura tecnológica.
"""

import os
import sys
from datetime import datetime

# Agregar el directorio actual al path para importaciones
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import init_db, db, create_all_tables, drop_all_tables

def create_app():
<<<<<<< HEAD
"""Crear aplicación Flask con configuración de base de datos."""
app = Flask(__name__)

# Configuración de base de datos
database_url = os.getenv('DATABASE_URL', 'sqlite:///infraestructura.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False # Cambiar a True para ver SQL

return app

def install_database():
"""Instalar e inicializar la base de datos."""
print(" INSTALACIÓN DE BASE DE DATOS - SISTEMA DE INFRAESTRUCTURA")
print("=" * 60)

app = create_app()

with app.app_context():
# Mostrar información de la base de datos
db_url = app.config['SQLALCHEMY_DATABASE_URI']
print(f" URL de Base de Datos: {db_url}")
print(f" Fecha de instalación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

try:
# Crear todas las tablas
print("\n Creando tablas...")
create_all_tables(db.engine)

# Verificar que las tablas se crearon
print("\n Verificando tablas creadas...")
tables = db.engine.table_names()
print(f" Tablas creadas: {len(tables)}")

# Mostrar lista de tablas
for table in sorted(tables):
print(f" - {table}")

# Mostrar información de la base de datos
print("\n Información de la instalación:")
print(f" - Total de tablas: {len(tables)}")
print(f" - Motor de BD: {db.engine.dialect.name}")

# Verificar algunos modelos específicos
print("\n Verificando modelos principales...")

# Verificar tabla de usuarios
if 'usuarios' in tables:
print(" Modelo Usuario - OK")
else:
print(" Modelo Usuario - FALTA")

# Verificar tabla de ubicaciones
if 'ubicaciones' in tables:
print(" Modelo Ubicación - OK")
else:
print(" Modelo Ubicación - FALTA")

# Verificar tabla de cámaras
if 'camaras' in tables:
print(" Modelo Cámara - OK")
else:
print(" Modelo Cámara - FALTA")

# Verificar tabla de NVRs
if 'nvrs' in tables:
print(" Modelo NVR - OK")
else:
print(" Modelo NVR - FALTA")

# Verificar tabla de switches
if 'switches' in tables:
print(" Modelo Switch - OK")
else:
print(" Modelo Switch - FALTA")

# Verificar tabla de UPS
if 'ups' in tables:
print(" Modelo UPS - OK")
else:
print(" Modelo UPS - FALTA")

# Verificar tabla de mantenimientos
if 'mantenimientos' in tables:
print(" Modelo Mantenimiento - OK")
else:
print(" Modelo Mantenimiento - FALTA")

# Verificar tabla de fotografías
if 'fotografias' in tables:
print(" Modelo Fotografía - OK")
else:
print(" Modelo Fotografía - FALTA")

print("\n INSTALACIÓN COMPLETADA EXITOSAMENTE")
print("\n Próximos pasos:")
print(" 1. Ejecutar script de datos iniciales (python datos_iniciales.py)")
print(" . Configurar usuario administrador inicial")
print(" 3. Configurar ubicaciones principales")
print(" 4. Importar inventario de equipos existente")

return True

except Exception as e:
print(f"\n ERROR durante la instalación:")
print(f" {str(e)}")
print("\n Posibles soluciones:")
print(" 1. Verificar que la base de datos sea accesible")
print(" . Verificar permisos de usuario")
print(" 3. Verificar que no haya conflictos de esquema")
return False

def reset_database():
"""Eliminar y recrear todas las tablas."""
print(" RESETEO DE BASE DE DATOS")
print("=" * 40)
print("ADVERTENCIA: Esta acción eliminará TODOS los datos existentes.")

respuesta = input("¿Estás seguro de que quieres continuar? (yes/no): ").lower().strip()

if respuesta = 'yes':
print(" Operación cancelada.")
return False

app = create_app()

with app.app_context():
try:
print(" Eliminando tablas existentes...")
drop_all_tables(db.engine)

print(" Creando tablas nuevas...")
create_all_tables(db.engine)

print(" Base de datos reseteada exitosamente.")
return True

except Exception as e:
print(f" Error durante el reseteo: {str(e)}")
return False

def check_database():
"""Verificar el estado de la base de datos."""
print(" VERIFICACIÓN DE BASE DE DATOS")
print("=" * 40)

app = create_app()

with app.app_context():
try:
# Verificar conexión
connection = db.engine.connect()
print(" Conexión a base de datos: OK")
connection.close()

# Obtener lista de tablas
tables = db.engine.table_names()
print(f" Tablas encontradas: {len(tables)}")

if tables:
print("\n Lista de tablas:")
for table in sorted(tables):
print(f" - {table}")
else:
print("\n No se encontraron tablas.")
print(" La base de datos está vacía.")
return False

return True

except Exception as e:
print(f" Error de conexión: {str(e)}")
return False

def show_schema_info():
"""Mostrar información del esquema de la base de datos."""
print(" INFORMACIÓN DEL ESQUEMA")
print("=" * 40)

app = create_app()

with app.app_context():
try:
tables = db.engine.table_names()

for table_name in sorted(tables):
print(f"\n Tabla: {table_name}")

# Obtener información de columnas
try:
result = db.engine.execute(f"PRAGMA table_info({table_name})")
columns = result.fetchall()

for column in columns:
col_name = column[1]
col_type = column[]
col_null = "NULL" if column[3] == 0 else "NOT NULL"
col_default = f"DEFAULT {column[4]}" if column[4] else ""

print(f" - {col_name} {col_type} {col_null} {col_default}")

except Exception as e:
print(f" (No se pudo obtener información de columnas: {str(e)})")

except Exception as e:
print(f" Error: {str(e)}")

def main():
"""Función principal del script."""
if len(sys.argv) > 1:
command = sys.argv[1].lower()

if command == "install":
install_database()
elif command == "reset":
reset_database()
elif command == "check":
check_database()
elif command == "schema":
show_schema_info()
elif command == "help":
print(" COMANDOS DISPONIBLES:")
print(" python install.py install - Instalar base de datos")
print(" python install.py reset - Resetear base de datos ( elimina datos)")
print(" python install.py check - Verificar estado de BD")
print(" python install.py schema - Mostrar esquema de BD")
print(" python install.py help - Mostrar esta ayuda")
else:
print(f" Comando desconocido: {command}")
print("Usa 'python install.py help' para ver comandos disponibles.")
else:
# Mostrar menú interactivo
print(" SISTEMA DE INSTALACIÓN DE BASE DE DATOS")
print("=" * 50)
print("Selecciona una opción:")
print("1. Instalar base de datos")
print(". Verificar estado de BD")
print("3. Mostrar esquema")
print("4. Resetear BD ( elimina datos)")
print("5. Salir")

try:
opcion = input("\nOpción (1-5): ").strip()

if opcion == "1":
install_database()
elif opcion == "":
check_database()
elif opcion == "3":
show_schema_info()
elif opcion == "4":
reset_database()
elif opcion == "5":
print(" ¡Hasta luego")
else:
print(" Opción inválida.")

except KeyboardInterrupt:
print("\n\n ¡Hasta luego")
except Exception as e:
print(f"\n Error: {str(e)}")

if __name__ == "__main__":
main()
=======
    """Crear aplicación Flask con configuración de base de datos."""
    app = Flask(__name__)
    
    # Configuración de base de datos
    database_url = os.getenv('DATABASE_URL', 'sqlite:///infraestructura.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False  # Cambiar a True para ver SQL
    
    return app

def install_database():
    """Instalar e inicializar la base de datos."""
    print("🔧 INSTALACIÓN DE BASE DE DATOS - SISTEMA DE INFRAESTRUCTURA")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        # Mostrar información de la base de datos
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"📍 URL de Base de Datos: {db_url}")
        print(f"🕒 Fecha de instalación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Crear todas las tablas
            print("\n📋 Creando tablas...")
            create_all_tables(db.engine)
            
            # Verificar que las tablas se crearon
            print("\n✅ Verificando tablas creadas...")
            tables = db.engine.table_names()
            print(f"   Tablas creadas: {len(tables)}")
            
            # Mostrar lista de tablas
            for table in sorted(tables):
                print(f"   - {table}")
            
            # Mostrar información de la base de datos
            print("\n📊 Información de la instalación:")
            print(f"   - Total de tablas: {len(tables)}")
            print(f"   - Motor de BD: {db.engine.dialect.name}")
            
            # Verificar algunos modelos específicos
            print("\n🔍 Verificando modelos principales...")
            
            # Verificar tabla de usuarios
            if 'usuarios' in tables:
                print("   ✅ Modelo Usuario - OK")
            else:
                print("   ❌ Modelo Usuario - FALTA")
            
            # Verificar tabla de ubicaciones
            if 'ubicaciones' in tables:
                print("   ✅ Modelo Ubicación - OK")
            else:
                print("   ❌ Modelo Ubicación - FALTA")
            
            # Verificar tabla de cámaras
            if 'camaras' in tables:
                print("   ✅ Modelo Cámara - OK")
            else:
                print("   ❌ Modelo Cámara - FALTA")
            
            # Verificar tabla de NVRs
            if 'nvrs' in tables:
                print("   ✅ Modelo NVR - OK")
            else:
                print("   ❌ Modelo NVR - FALTA")
            
            # Verificar tabla de switches
            if 'switches' in tables:
                print("   ✅ Modelo Switch - OK")
            else:
                print("   ❌ Modelo Switch - FALTA")
            
            # Verificar tabla de UPS
            if 'ups' in tables:
                print("   ✅ Modelo UPS - OK")
            else:
                print("   ❌ Modelo UPS - FALTA")
            
            # Verificar tabla de mantenimientos
            if 'mantenimientos' in tables:
                print("   ✅ Modelo Mantenimiento - OK")
            else:
                print("   ❌ Modelo Mantenimiento - FALTA")
            
            # Verificar tabla de fotografías
            if 'fotografias' in tables:
                print("   ✅ Modelo Fotografía - OK")
            else:
                print("   ❌ Modelo Fotografía - FALTA")
            
            print("\n🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE")
            print("\n📝 Próximos pasos:")
            print("   1. Ejecutar script de datos iniciales (python datos_iniciales.py)")
            print("   2. Configurar usuario administrador inicial")
            print("   3. Configurar ubicaciones principales")
            print("   4. Importar inventario de equipos existente")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR durante la instalación:")
            print(f"   {str(e)}")
            print("\n🔧 Posibles soluciones:")
            print("   1. Verificar que la base de datos sea accesible")
            print("   2. Verificar permisos de usuario")
            print("   3. Verificar que no haya conflictos de esquema")
            return False

def reset_database():
    """Eliminar y recrear todas las tablas."""
    print("⚠️  RESETEO DE BASE DE DATOS")
    print("=" * 40)
    print("ADVERTENCIA: Esta acción eliminará TODOS los datos existentes.")
    
    respuesta = input("¿Estás seguro de que quieres continuar? (yes/no): ").lower().strip()
    
    if respuesta != 'yes':
        print("❌ Operación cancelada.")
        return False
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🗑️  Eliminando tablas existentes...")
            drop_all_tables(db.engine)
            
            print("📋 Creando tablas nuevas...")
            create_all_tables(db.engine)
            
            print("✅ Base de datos reseteada exitosamente.")
            return True
            
        except Exception as e:
            print(f"❌ Error durante el reseteo: {str(e)}")
            return False

def check_database():
    """Verificar el estado de la base de datos."""
    print("🔍 VERIFICACIÓN DE BASE DE DATOS")
    print("=" * 40)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar conexión
            connection = db.engine.connect()
            print("✅ Conexión a base de datos: OK")
            connection.close()
            
            # Obtener lista de tablas
            tables = db.engine.table_names()
            print(f"📊 Tablas encontradas: {len(tables)}")
            
            if tables:
                print("\n📋 Lista de tablas:")
                for table in sorted(tables):
                    print(f"   - {table}")
            else:
                print("\n⚠️  No se encontraron tablas.")
                print("   La base de datos está vacía.")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error de conexión: {str(e)}")
            return False

def show_schema_info():
    """Mostrar información del esquema de la base de datos."""
    print("📋 INFORMACIÓN DEL ESQUEMA")
    print("=" * 40)
    
    app = create_app()
    
    with app.app_context():
        try:
            tables = db.engine.table_names()
            
            for table_name in sorted(tables):
                print(f"\n📊 Tabla: {table_name}")
                
                # Obtener información de columnas
                try:
                    result = db.engine.execute(f"PRAGMA table_info({table_name})")
                    columns = result.fetchall()
                    
                    for column in columns:
                        col_name = column[1]
                        col_type = column[2]
                        col_null = "NULL" if column[3] == 0 else "NOT NULL"
                        col_default = f"DEFAULT {column[4]}" if column[4] else ""
                        
                        print(f"   - {col_name} {col_type} {col_null} {col_default}")
                
                except Exception as e:
                    print(f"   (No se pudo obtener información de columnas: {str(e)})")
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def main():
    """Función principal del script."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "install":
            install_database()
        elif command == "reset":
            reset_database()
        elif command == "check":
            check_database()
        elif command == "schema":
            show_schema_info()
        elif command == "help":
            print("📚 COMANDOS DISPONIBLES:")
            print("   python install.py install    - Instalar base de datos")
            print("   python install.py reset      - Resetear base de datos (⚠️  elimina datos)")
            print("   python install.py check      - Verificar estado de BD")
            print("   python install.py schema     - Mostrar esquema de BD")
            print("   python install.py help       - Mostrar esta ayuda")
        else:
            print(f"❌ Comando desconocido: {command}")
            print("Usa 'python install.py help' para ver comandos disponibles.")
    else:
        # Mostrar menú interactivo
        print("🔧 SISTEMA DE INSTALACIÓN DE BASE DE DATOS")
        print("=" * 50)
        print("Selecciona una opción:")
        print("1. Instalar base de datos")
        print("2. Verificar estado de BD")
        print("3. Mostrar esquema")
        print("4. Resetear BD (⚠️  elimina datos)")
        print("5. Salir")
        
        try:
            opcion = input("\nOpción (1-5): ").strip()
            
            if opcion == "1":
                install_database()
            elif opcion == "2":
                check_database()
            elif opcion == "3":
                show_schema_info()
            elif opcion == "4":
                reset_database()
            elif opcion == "5":
                print("👋 ¡Hasta luego!")
            else:
                print("❌ Opción inválida.")
        
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
