#!/usr/bin/env python3
"""
Script de Test para Sistema Cámaras UFRO
Verifica que las correcciones funcionan correctamente
"""

import os
import sys

def test_imports():
    """Test de importaciones"""
    try:
        print("🔍 Probando importaciones...")
        
        # Test config
        from config import get_config
        config = get_config()
        print(f"✅ Configuración cargada: {config.__class__.__name__}")
        
        # Test Flask app
        from app import app
        print(f"✅ Aplicación Flask creada: {app.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        return False

def test_database():
    """Test de conexión a base de datos"""
    try:
        print("🔍 Probando conexión a base de datos...")
        
        from app import app, db
        from models import Usuario
        
        with app.app_context():
            # Test básico de conexión
            user_count = Usuario.query.count()
            print(f"✅ Conexión a BD exitosa. Usuarios: {user_count}")
            return True
            
    except Exception as e:
        print(f"❌ Error de conexión a BD: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando tests del Sistema Cámaras UFRO")
    print("=" * 50)
    
    success = True
    success &= test_imports()
    success &= test_database()
    
    print("=" * 50)
    if success:
        print("🎉 ¡Todos los tests pasaron! Sistema funcionando correctamente.")
        sys.exit(0)
    else:
        print("❌ Algunos tests fallaron. Revisar configuración.")
        sys.exit(1)
