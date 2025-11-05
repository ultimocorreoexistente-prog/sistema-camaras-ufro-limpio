#!/usr/bin/env python3
"""
Creador automático de archivos necesarios para el sistema de cámaras UFRO
Este script genera todos los archivos necesarios en el directorio local
"""

import os
import sys
from datetime import datetime
import secrets

def crear_diagnostico_entorno():
    """Crea el archivo diagnostico_entorno.py"""
    contenido = '''#!/usr/bin/env python3
"""
Script de Diagnóstico del Entorno - Sistema de Cámaras UFRO
Verifica todas las variables de entorno y configuraciones necesarias
"""

import os
import sys
import platform
from datetime import datetime

def print_header():
    """Imprime el encabezado del diagnóstico"""
    print("=" * 70)
    print("🔍 DIAGNÓSTICO DEL ENTORNO - SISTEMA DE CÁMARAS UFRO")
    print("=" * 70)
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Sistema operativo: {platform.system()} {platform.release()}")
    print(f"Python version: {sys.version}")
    print(f"Directorio actual: {os.getcwd()}")
    print("=" * 70)

def print_section(title):
    """Imprime una sección del diagnóstico"""
    print(f"\\n📋 {title}")
    print("-" * 50)

def check_variable(name, required=True, description=""):
    """Verifica una variable de entorno específica"""
    value = os.getenv(name)
    if required:
        if value:
            status = "✅ OK"
            display_value = f"{value[:20]}{'...' if len(value) > 20 else ''}"
        else:
            status = "❌ FALTA"
            display_value = "No definida"
    else:
        status = "⚠️  OPCIONAL" if value else "ℹ️  No definida"
        display_value = value or "No definida"
    
    print(f"  {status} {name}")
    if description:
        print(f"      📝 {description}")
    return value is not None

def check_python_packages():
    """Verifica los paquetes de Python necesarios"""
    print_section("VERIFICACIÓN DE PAQUETES PYTHON")
    
    required_packages = [
        ('flask', 'Flask web framework'),
        ('gunicorn', 'WSGI server para producción'),
        ('psycopg2-binary', 'Driver PostgreSQL'),
        ('sqlalchemy', 'ORM para base de datos'),
        ('python-dotenv', 'Manejo de variables de entorno'),
    ]
    
    missing_packages = []
    
    for package, description in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package} - {description}")
        except ImportError:
            print(f"  ❌ {package} - {description}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\\n⚠️  Paquetes faltantes: {', '.join(missing_packages)}")
        print("💡 Instalar con: pip install " + " ".join(missing_packages))
    else:
        print("\\n✅ Todos los paquetes requeridos están instalados")

def check_environment_variables():
    """Verifica las variables de entorno"""
    print_section("VERIFICACIÓN DE VARIABLES DE ENTORNO")
    
    print("🔐 Variables de seguridad:")
    check_variable('SECRET_KEY', True, 'Clave secreta de la aplicación')
    check_variable('SECURITY_PASSWORD_SALT', True, 'Salt para encriptación')
    
    print("\\n🏷️  Variables de aplicación:")
    check_variable('APP_NAME', True, 'Nombre de la aplicación')
    check_variable('FLASK_ENV', True, 'Entorno de Flask')
    check_variable('DEBUG', False, 'Modo debug (opcional)')
    
    print("\\n🗄️  Variables de base de datos:")
    check_variable('DATABASE_URL', True, 'URL de la base de datos PostgreSQL')

def check_postgresql_connection():
    """Verifica la conexión a PostgreSQL"""
    print_section("VERIFICACIÓN DE CONEXIÓN A POSTGRESQL")
    
    try:
        import psycopg2
        import os
        from urllib.parse import urlparse
        
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("  ❌ DATABASE_URL no está definida")
            return False
            
        # Parsear la URL de la base de datos
        parsed = urlparse(database_url)
        
        try:
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port,
                database=parsed.path[1:],
                user=parsed.username,
                password=parsed.password
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            print(f"  ✅ Conexión exitosa")
            print(f"  📋 PostgreSQL: {version[0]}")
            
            conn.close()
            return True
            
        except psycopg2.Error as e:
            print(f"  ❌ Error de conexión: {e}")
            return False
            
    except ImportError:
        print("  ❌ psycopg2-binary no está instalado")
        return False

def generate_sample_env_file():
    """Genera un archivo .env de ejemplo"""
    print_section("GENERACIÓN DE ARCHIVO .env")
    
    secret_key = secrets.token_hex(32)
    security_salt = secrets.token_hex(16)
    
    env_content = f"""# Configuración Sistema Cámaras UFRO
# Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Variables de seguridad (OBLIGATORIAS)
SECRET_KEY={secret_key}
SECURITY_PASSWORD_SALT={security_salt}

# Variables de aplicación (OBLIGATORIAS)
APP_NAME=Sistema Cámaras UFRO
FLASK_ENV=production
DEBUG=false

# Variables de base de datos (Railway proporciona automáticamente)
# DATABASE_URL=postgresql://usuario:contraseña@host:puerto/database

# Variables adicionales (OPCIONALES)
LOG_LEVEL=INFO
PORT=5000
"""
    
    env_file_path = os.path.join(os.getcwd(), '.env')
    
    try:
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        print(f"  ✅ Archivo .env generado en: {env_file_path}")
        print("  ⚠️  IMPORTANTE: Este archivo contiene datos sensibles")
        print("  💡 El archivo ya incluye las variables SECRET_KEY y SECURITY_PASSWORD_SALT generadas")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error generando archivo .env: {e}")
        return False

def main():
    """Función principal del diagnóstico"""
    print_header()
    
    # Verificaciones principales
    check_python_packages()
    check_environment_variables()
    check_postgresql_connection()
    generate_sample_env_file()
    
    print("\\n" + "=" * 70)
    print("📊 RESUMEN DEL DIAGNÓSTICO COMPLETADO")
    print("=" * 70)
    print("✅ Revisa los resultados arriba para identificar cualquier problema")
    print("🔧 Si hay errores, resuélvelos antes de continuar con el despliegue")
    print("📖 Consulta la documentación para más detalles")

if __name__ == "__main__":
    main()
'''
    with open('diagnostico_entorno.py', 'w', encoding='utf-8') as f:
        f.write(contenido)
    print("✅ Creado: diagnostico_entorno.py")

def main():
    print("🚀 SISTEMA CÁMARAS UFRO - Creando archivos necesarios...")
    print()
    
    # Verificar directorio
    current_dir = os.getcwd()
    print(f"📁 Directorio actual: {current_dir}")
    
    # Crear archivos
    crear_diagnostico_entorno()
    
    print()
    print("📋 INSTRUCCIONES:")
    print("1. Ejecuta: python3 diagnostico_entorno.py")
    print("2. Revisa las advertencias y errores")
    print("3. Continúa con el siguiente paso")
    print()
    print("🔗 URLs importantes:")
    print("- GitHub: https://github.com/ultimocorreoexistente-prog/sistema-camaras-ufro-limpio")
    print("- Railway: https://sistema-camaras-ufro-limpio-production.up.railway.app")

if __name__ == "__main__":
    main()
