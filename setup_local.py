#!/usr/bin/env python3
"""
Configuración Automática del Entorno Local - Sistema Cámaras UFRO v2
Versión corregida con emails UFRO formato correcto
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def print_banner():
    """Mostrar banner de inicio"""
    print("=" * 60)
    print("🏢 SISTEMA DE GESTIÓN DE CÁMARAS UFRO v2")
    print("   Configuración Automática del Entorno Local")
    print("   Formato emails: usuario.apellido@ufrontera.cl")
    print("=" * 60)

def check_python_version():
    """Verificar versión de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def create_env_file():
    """Crear archivo .env para configuración local"""
    env_content = """# Configuración Sistema Cámaras UFRO - Entorno Local
SECRET_KEY=sistema-camaras-ufro-v2-local-secret-key-2025
DATABASE_URL=sqlite:///instance/sistema_camaras.db
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5000
GOOGLE_MAPS_API_KEY=AIzaSyCO0kKndUNlmQi3B5mxy4dblg_8WYcuKuk

# Usuarios por defecto (creados automáticamente)
# Admin: admin.sistema@ufrontera.cl / admin123
# Técnico: charles.jelvez@ufrontera.cl / ufro05  
# Operador: operador.principal@ufrontera.cl / operacion123
# Visualizador: visualizador.seguridad@ufrontera.cl / visual123
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✅ Archivo .env creado exitosamente")

def setup_virtual_environment():
    """Configurar entorno virtual de Python"""
    print("\n🔧 Configurando entorno virtual...")
    
    # Verificar si venv existe
    if not os.path.exists('venv'):
        print("   Creando entorno virtual...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("   ✅ Entorno virtual creado")
    else:
        print("   ✅ Entorno virtual ya existe")
    
    # Determinar rutas de pip y python según el sistema
    if os.name == 'nt':  # Windows
        pip_path = 'venv\\Scripts\\pip'
        python_path = 'venv\\Scripts\\python'
    else:  # Linux/Mac
        pip_path = 'venv/bin/pip'
        python_path = 'venv/bin/python'
    
    # Actualizar pip
    print("   Actualizando pip...")
    subprocess.run([python_path, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
    
    return pip_path, python_path

def install_dependencies(pip_path):
    """Instalar dependencias del proyecto"""
    print("\n📦 Instalando dependencias...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ Error: requirements.txt no encontrado")
        return False
    
    try:
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencias instaladas exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def create_instance_directory():
    """Crear directorio instance para SQLite"""
    instance_dir = Path('instance')
    instance_dir.mkdir(exist_ok=True)
    
    # Crear base de datos SQLite vacía
    db_path = instance_dir / 'sistema_camaras.db'
    if not db_path.exists():
        conn = sqlite3.connect(str(db_path))
        conn.close()
        print("✅ Base de datos SQLite creada en instance/")
    else:
        print("✅ Base de datos SQLite ya existe en instance/")

def verify_project_structure():
    """Verificar estructura del proyecto"""
    print("\n🔍 Verificando estructura del proyecto...")
    
    required_dirs = ['models', 'routes', 'templates', 'static', 'scripts', 'services', 'utils']
    required_files = ['app.py', 'config.py', 'models.py', 'requirements.txt']
    
    missing = []
    
    # Verificar directorios
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing.append(f"Directorio: {dir_name}")
    
    # Verificar archivos
    for file_name in required_files:
        if not os.path.exists(file_name):
            missing.append(f"Archivo: {file_name}")
    
    if missing:
        print("❌ Archivos/directorios faltantes:")
        for item in missing:
            print(f"   - {item}")
        return False
    else:
        print("✅ Estructura del proyecto correcta")
        return True

def test_imports():
    """Probar importaciones de los modelos"""
    print("\n🧪 Probando importaciones...")
    
    try:
        # Cambiar al directorio del script para las importaciones
        sys.path.insert(0, os.getcwd())
        
        from models import db, Usuario, Camara, Ubicacion
        print("✅ Modelos importados correctamente")
        
        # Probar configuración
        from config import get_config
        config = get_config()
        print(f"✅ Configuración cargada: {config}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        return False

def create_database():
    """Crear tablas de la base de datos"""
    print("\n🗄️  Creando tablas de base de datos...")
    
    try:
        sys.path.insert(0, os.getcwd())
        
        from app import app, init_database
        from models import db
        
        with app.app_context():
            init_database()
            print("✅ Base de datos inicializada correctamente")
            return True
            
    except Exception as e:
        print(f"❌ Error creando base de datos: {e}")
        return False

def verify_email_format():
    """Verificar que los usuarios tengan formato correcto"""
    print("\n📧 Verificando formato de emails...")
    
    try:
        from models import Usuario
        from app import app
        
        with app.app_context():
            # Verificar si hay usuarios con formato incorrecto
            usuarios_incorrectos = Usuario.query.filter(
                Usuario.email.like('%@ufro.cl%')
            ).all()
            
            if usuarios_incorrectos:
                print(f"⚠️  Encontrados {len(usuarios_incorrectos)} usuarios con formato @ufro.cl")
                print("   Estos deben ser actualizados manualmente a @ufrontera.cl")
                for usuario in usuarios_incorrectos:
                    print(f"   - {usuario.email}")
                return False
            else:
                print("✅ Todos los usuarios tienen formato correcto @ufrontera.cl")
                return True
                
    except Exception as e:
        print(f"❌ Error verificando emails: {e}")
        return False

def show_next_steps():
    """Mostrar pasos siguientes"""
    print("\n" + "=" * 60)
    print("🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
    print("=" * 60)
    
    print("\n📋 PASOS SIGUIENTES:")
    print("1. Activar entorno virtual:")
    if os.name == 'nt':  # Windows
        print("   source venv\\Scripts\\activate")
    else:  # Linux/Mac
        print("   source venv/bin/activate")
    
    print("\n2. Ejecutar aplicación:")
    print("   python app.py")
    
    print("\n3. Abrir en navegador:")
    print("   http://localhost:5000")
    
    print("\n4. Usuarios por defecto (formato correcto):")
    print("   📧 Admin: admin.sistema@ufrontera.cl / admin123")
    print("   📧 Técnico: charles.jelvez@ufrontera.cl / ufro05")
    print("   📧 Operador: operador.principal@ufrontera.cl / operacion123")
    print("   📧 Visualizador: visualizador.seguridad@ufrontera.cl / visual123")
    
    print("\n" + "=" * 60)

def main():
    """Función principal de configuración"""
    print_banner()
    
    # Verificar directorio
    if not os.path.exists('app.py'):
        print("❌ Error: Ejecute este script desde el directorio raíz del proyecto")
        print("   Asegúrese de estar en: sistema-camaras-ufro-limpio-v2/")
        return False
    
    success_steps = []
    
    # Paso 1: Verificar Python
    if check_python_version():
        success_steps.append("Python")
    
    # Paso 2: Crear .env
    create_env_file()
    success_steps.append(".env")
    
    # Paso 3: Configurar entorno virtual
    pip_path, python_path = setup_virtual_environment()
    success_steps.append("Entorno virtual")
    
    # Paso 4: Instalar dependencias
    if install_dependencies(pip_path):
        success_steps.append("Dependencias")
    
    # Paso 5: Crear directorio instance
    create_instance_directory()
    success_steps.append("Directorio instance")
    
    # Paso 6: Verificar estructura
    if verify_project_structure():
        success_steps.append("Estructura")
    
    # Paso 7: Probar importaciones
    if test_imports():
        success_steps.append("Importaciones")
    
    # Paso 8: Crear base de datos
    if create_database():
        success_steps.append("Base de datos")
    
    # Paso 9: Verificar formato de emails
    if verify_email_format():
        success_steps.append("Formato emails")
    
    # Mostrar resumen
    print(f"\n📊 RESUMEN: {len(success_steps)}/9 pasos completados")
    
    if len(success_steps) == 9:
        show_next_steps()
        return True
    else:
        print(f"\n⚠️  Pasos completados: {', '.join(success_steps)}")
        print("   Revise los errores anteriores y ejecute nuevamente")
        return False

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Configuración cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)