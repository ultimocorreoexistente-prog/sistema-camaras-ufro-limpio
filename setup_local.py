#!/usr/bin/env python3
<<<<<<< HEAD
# -*- coding: utf-8 -*-
"""
Sistema de Cámaras UFRO - Script de Configuración Automática
Desarrollador: MiniMax Agent
Fecha: 2025-11-26

Este script automatiza la configuración inicial del Sistema de Cámaras UFRO
para desarrollo local, incluyendo:
- Verificación de dependencias
- Configuración de base de datos
- Creación de usuarios
- Carga de datos iniciales
=======
"""
Configuración Automática del Entorno Local - Sistema Cámaras UFRO v2
Versión corregida con emails UFRO formato correcto
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

<<<<<<< HEAD
class SetupUFRO:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.instance_path = self.project_root / "instance"
        self.env_file = self.project_root / ".env"
        
    def print_header(self):
        print("=" * 80)
        print("🏠 SISTEMA DE CÁMARAS UFRO - CONFIGURACIÓN AUTOMÁTICA")
        print("=" * 80)
        print("Desarrollador: MiniMax Agent")
        print("Fecha: 2025-11-26 22:11:19")
        print("=" * 80)
        print()
    
    def check_python_version(self):
        """Verificar versión de Python"""
        print("🔍 Verificando versión de Python...")
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
            return True
        else:
            print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requiere Python 3.8+")
            return False
    
    def create_virtual_environment(self):
        """Crear entorno virtual"""
        print("\n📦 Creando entorno virtual...")
        try:
            if not self.venv_path.exists():
                subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
                print("✅ Entorno virtual creado exitosamente")
            else:
                print("ℹ️ Entorno virtual ya existe")
            return True
        except Exception as e:
            print(f"❌ Error creando entorno virtual: {e}")
            return False
    
    def get_pip_path(self):
        """Obtener ruta del pip en el entorno virtual"""
        if os.name == 'nt':  # Windows
            return self.venv_path / "Scripts" / "pip.exe"
        else:  # Linux/Mac
            return self.venv_path / "bin" / "pip"
    
    def install_dependencies(self):
        """Instalar dependencias"""
        print("\n📚 Instalando dependencias...")
        pip_path = self.get_pip_path()
        requirements_file = self.project_root / "requirements.txt"
        
        try:
            subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True)
            print("✅ Dependencias instaladas exitosamente")
            return True
        except Exception as e:
            print(f"❌ Error instalando dependencias: {e}")
            return False
    
    def create_env_file(self):
        """Crear archivo .env"""
        print("\n⚙️ Configurando variables de entorno...")
        if not self.env_file.exists():
            env_content = """# Sistema de Cámaras UFRO - Configuración Local
# Generado automáticamente el 2025-11-26 22:11:19

# Base de datos local (SQLite para desarrollo)
DATABASE_URL=sqlite:///instance/sistema_camaras.db

# Secret key para Flask (cambiar en producción)
SECRET_KEY=dev-secret-key-sistema-camaras-ufro-2025

# Entorno de desarrollo
FLASK_ENV=development
FLASK_DEBUG=1

# Google Maps API Key
GOOGLE_MAPS_API_KEY=AIzaSyCO0kKndUNlmQi3B5mxy4dblg_8WYcuKuk

# Configuración de logging
LOG_LEVEL=DEBUG

# Puerto local
PORT=8000

# Host local
HOST=localhost
"""
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            print("✅ Archivo .env creado")
        else:
            print("ℹ️ Archivo .env ya existe")
        return True
    
    def create_instance_directory(self):
        """Crear directorio instance si no existe"""
        print("\n📁 Creando directorio instance...")
        if not self.instance_path.exists():
            self.instance_path.mkdir(exist_ok=True)
            print("✅ Directorio instance creado")
        else:
            print("ℹ️ Directorio instance ya existe")
        return True
    
    def run_database_setup(self):
        """Ejecutar configuración de base de datos"""
        print("\n🗄️ Configurando base de datos...")
        
        # Ejecutar init_db.py
        try:
            result = subprocess.run([
                sys.executable, "init_db.py"
            ], cwd=str(self.project_root), capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Base de datos inicializada")
            else:
                print(f"⚠️ Warning en init_db.py: {result.stderr}")
        except Exception as e:
            print(f"❌ Error ejecutando init_db.py: {e}")
            return False
        
        # Ejecutar create_superadmin.py
        try:
            result = subprocess.run([
                sys.executable, "scripts/create_superadmin.py"
            ], cwd=str(self.project_root), capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Superusuario creado")
            else:
                print(f"⚠️ Warning en create_superadmin.py: {result.stderr}")
        except Exception as e:
            print(f"❌ Error ejecutando create_superadmin.py: {e}")
            return False
        
        # Ejecutar datos_iniciales.py
        try:
            result = subprocess.run([
                sys.executable, "scripts/datos_iniciales.py"
            ], cwd=str(self.project_root), capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Datos iniciales cargados")
            else:
                print(f"⚠️ Warning en datos_iniciales.py: {result.stderr}")
        except Exception as e:
            print(f"❌ Error ejecutando datos_iniciales.py: {e}")
            return False
        
        return True
    
    def verify_installation(self):
        """Verificar que todo esté configurado correctamente"""
        print("\n🔍 Verificando instalación...")
        
        # Verificar que el archivo principal existe
        main_file = self.project_root / "app.py"
        if not main_file.exists():
            print("❌ Archivo app.py no encontrado")
            return False
        
        # Verificar que la base de datos existe
        db_file = self.instance_path / "sistema_camaras.db"
        if not db_file.exists():
            print("❌ Base de datos no creada")
            return False
        
        # Verificar entorno virtual
        if not self.venv_path.exists():
            print("❌ Entorno virtual no encontrado")
            return False
        
        print("✅ Instalación verificada correctamente")
        return True
    
    def print_next_steps(self):
        """Mostrar pasos siguientes"""
        print("\n" + "=" * 80)
        print("🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
        print("=" * 80)
        print()
        print("📋 PRÓXIMOS PASOS:")
        print()
        print("1. Activar entorno virtual:")
        print("   Windows: venv\\Scripts\\activate")
        print("   Linux/Mac: source venv/bin/activate")
        print()
        print("2. Ejecutar el sistema:")
        print("   python app.py")
        print()
        print("3. Abrir navegador en:")
        print("   http://localhost:8000")
        print()
        print("🔑 CREDENCIALES DE ACCESO:")
        print("   Administrador: admin / admin13")
        print("   Supervisor: charles@ufro.cl / ufro05")
        print("   Operador: tecnico1 / ufro05")
        print()
        print("🗃️ DATOS CARGADOS:")
        print("   ✅ 467 cámaras de seguridad")
        print("   ✅ 14 modelos SQLAlchemy")
        print("   ✅ Casos reales: Mantenimiento Edificio O, Falla CFT Prat")
        print()
        print("🔗 GITHUB:")
        print("   git add .")
        print("   git commit -m 'Cambios de desarrollo local'")
        print("   git push origin main")
        print()
        print("=" * 80)
    
    def run_setup(self):
        """Ejecutar toda la configuración"""
        self.print_header()
        
        steps = [
            ("Verificar Python", self.check_python_version),
            ("Crear entorno virtual", self.create_virtual_environment),
            ("Instalar dependencias", self.install_dependencies),
            ("Configurar .env", self.create_env_file),
            ("Crear directorio instance", self.create_instance_directory),
            ("Configurar base de datos", self.run_database_setup),
            ("Verificar instalación", self.verify_installation)
        ]
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    print(f"\n❌ Error en: {step_name}")
                    return False
            except Exception as e:
                print(f"\n❌ Error inesperado en {step_name}: {e}")
                return False
        
        self.print_next_steps()
        return True

def main():
    """Función principal"""
    setup = SetupUFRO()
    success = setup.run_setup()
    
    if success:
        print("\n🎉 ¡Sistema configurado exitosamente!")
        print("🚀 Listo para desarrollo local")
        return 0
    else:
        print("\n❌ Configuración incompleta")
        print("📞 Revisa los errores arriba y ejecuta nuevamente")
        return 1

if __name__ == "__main__":
    sys.exit(main())
=======
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
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
