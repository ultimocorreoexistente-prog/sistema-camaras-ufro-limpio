#!/usr/bin/env python3
"""
Script de Diagnóstico para Railway
===================================

Verifica la configuración y dependencias del sistema.

Autor: MiniMax Agent
Fecha: 2025-11-30
"""

import sys
import os
import importlib.util

def check_python_version():
    """Verificar versión de Python."""
    print(f"🐍 Python Version: {sys.version}")
    print(f"   Version info: {sys.version_info}")
    return True

def check_module(module_name, import_path=None):
    """Verificar si un módulo está disponible."""
    if import_path is None:
        import_path = module_name
    
    try:
        module = __import__(import_path)
        version = getattr(module, '__version__', 'Unknown')
        print(f"✅ {module_name}: {version}")
        return True
    except ImportError as e:
        print(f"❌ {module_name}: NOT FOUND - {e}")
        return False

def check_dependencies():
    """Verificar todas las dependencias críticas."""
    print("\n📦 VERIFICACIÓN DE DEPENDENCIAS")
    print("=" * 50)
    
    dependencies = [
        ('Flask', 'flask'),
        ('Flask-Login', 'flask_login'),
        ('Flask-SQLAlchemy', 'flask_sqlalchemy'),
        ('Gunicorn', 'gunicorn'),
        ('Python-dotenv', 'dotenv'),
        ('SQLAlchemy', 'sqlalchemy'),
        ('Psycopg2', 'psycopg2'),
        ('Pandas', 'pandas'),
        ('Pillow', 'PIL'),
        ('Requests', 'requests'),
        ('BCrypt', 'bcrypt'),
    ]
    
    results = []
    for name, import_path in dependencies:
        result = check_module(name, import_path)
        results.append((name, result))
    
    return results

def check_environment():
    """Verificar variables de entorno."""
    print("\n🌍 VARIABLES DE ENTORNO")
    print("=" * 50)
    
    env_vars = [
        'PORT',
        'FLASK_ENV',
        'DATABASE_URL',
        'SECRET_KEY',
        'PYTHONPATH'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, 'NOT SET')
        if var == 'SECRET_KEY' and value != 'NOT SET':
            value = f"{value[:10]}...{value[-10:]}"  # Mask secret
        print(f"📋 {var}: {value}")

def check_files():
    """Verificar archivos críticos."""
    print("\n📁 ARCHIVOS CRÍTICOS")
    print("=" * 50)
    
    critical_files = [
        'app.py',
        'config.py',
        'requirements.txt',
        'Dockerfile',
        'Procfile',
        'models/__init__.py',
        'routes/__init__.py',
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NO EXISTE")

def test_config_import():
    """Probar importación de configuración."""
    print("\n⚙️ PRUEBA DE CONFIGURACIÓN")
    print("=" * 50)
    
    try:
        from config import get_config_safe
        config = get_config_safe()
        print(f"✅ Config importada exitosamente")
        print(f"   SECRET_KEY configurado: {'SÍ' if config.SECRET_KEY else 'NO'}")
        print(f"   DATABASE_URL: {config.SQLALCHEMY_DATABASE_URI[:30]}...")
        return True
    except Exception as e:
        print(f"❌ Error importando configuración: {e}")
        return False

def test_models_import():
    """Probar importación de modelos."""
    print("\n🗄️ PRUEBA DE MODELOS")
    print("=" * 50)
    
    try:
        from models import db, Usuario
        print(f"✅ Modelos importados exitosamente")
        print(f"   DB object: {type(db)}")
        print(f"   Usuario model: {type(Usuario)}")
        return True
    except Exception as e:
        print(f"❌ Error importando modelos: {e}")
        return False

def main():
    """Función principal de diagnóstico."""
    print("🔍 DIAGNÓSTICO SISTEMA CAMARAS UFRO - RAILWAY")
    print("=" * 60)
    
    check_python_version()
    
    results = check_dependencies()
    check_environment()
    check_files()
    
    config_ok = test_config_import()
    models_ok = test_models_import()
    
    print("\n📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    failed_deps = [name for name, success in results if not success]
    if failed_deps:
        print(f"❌ DEPENDENCIAS FALTANTES: {', '.join(failed_deps)}")
    else:
        print("✅ Todas las dependencias están disponibles")
    
    if not config_ok:
        print("❌ CONFIGURACIÓN: Error crítico")
    else:
        print("✅ CONFIGURACIÓN: OK")
    
    if not models_ok:
        print("❌ MODELOS: Error crítico")
    else:
        print("✅ MODELOS: OK")
    
    # Recomendaciones
    print("\n💡 RECOMENDACIONES")
    print("=" * 60)
    
    if failed_deps:
        print("1. Verificar requirements.txt")
        print("2. Reiniciar el deploy en Railway")
        print("3. Verificar que Railway use el Dockerfile")
    
    if not config_ok or not models_ok:
        print("4. Revisar import paths y dependencias")
        print("5. Verificar estructura de archivos")

if __name__ == '__main__':
    main()