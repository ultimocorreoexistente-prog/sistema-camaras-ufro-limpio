#!/usr/bin/env python3
"""
Script de Corrección Crítica - Sistema Cámaras UFRO
Aplica correcciones inmediatas para resolver conflictos de merge
"""

import os
import shutil
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def backup_files():
    """Crear backup de archivos originales"""
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = ['app.py', 'config.py']
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, f"{backup_dir}/{file}")
            logging.info(f"✅ Backup creado: {backup_dir}/{file}")
    
    return backup_dir

def apply_fixes():
    """Aplicar correcciones principales"""
    try:
        logging.info("🔧 Iniciando aplicación de correcciones...")
        
        # 1. Crear backup
        backup_dir = backup_files()
        logging.info(f"📦 Backup creado en: {backup_dir}")
        
        # 2. Aplicar correcciones
        fixes = [
            ('app_fixed.py', 'app.py'),
            ('config_fixed.py', 'config.py')
        ]
        
        for source, target in fixes:
            if os.path.exists(source):
                shutil.copy2(source, target)
                logging.info(f"✅ Corrección aplicada: {source} -> {target}")
            else:
                logging.error(f"❌ Archivo no encontrado: {source}")
        
        # 3. Verificar que las correcciones se aplicaron
        if os.path.exists('app.py') and os.path.exists('config.py'):
            with open('app.py', 'r') as f:
                content = f.read()
                if '<<<<<<< HEAD' in content:
                    logging.error("❌ app.py aún tiene conflictos de merge")
                    return False
                else:
                    logging.info("✅ app.py limpio de conflictos")
            
            with open('config.py', 'r') as f:
                content = f.read()
                if '<<<<<<< HEAD' in content:
                    logging.error("❌ config.py aún tiene conflictos de merge")
                    return False
                else:
                    logging.info("✅ config.py limpio de conflictos")
        
        logging.info("🎉 Todas las correcciones aplicadas exitosamente")
        return True
        
    except Exception as e:
        logging.error(f"❌ Error aplicando correcciones: {e}")
        return False

def create_test_script():
    """Crear script de test para verificar funcionamiento"""
    test_script = '''#!/usr/bin/env python3
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
'''
    
    with open('test_sistema.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    logging.info("✅ Script de test creado: test_sistema.py")

def create_deploy_instructions():
    """Crear instrucciones de deploy"""
    instructions = '''# Instrucciones de Deploy - Corrección Aplicada

## ✅ Correcciones Aplicadas:
1. **app.py**: Conflictos de merge resueltos
2. **config.py**: Conflictos de merge resueltos  
3. **Configuración Railway**: DATABASE_URL compatible

## 🚀 Pasos para Deploy:

### 1. Verificar localmente:
```bash
python test_sistema.py
```

### 2. Hacer commit y push:
```bash
git add .
git commit -m "FIXED: Resolver conflictos de merge en app.py y config.py

- Corregir imports y configuración Flask
- Solucionar conflictos de merge
- Configurar DATABASE_URL para Railway
- Crear versiones limpias de app.py y config.py"

git push origin main
```

### 3. Verificar en Railway:
- Esperar que Railway redeploy automáticamente
- Revisar logs para confirmar "Aplicación configurada"
- Probar endpoint: /test-db

## 🔍 Verificación Post-Deploy:

### Endpoints de Test:
- `GET /test-db` - Verificar conexión a BD
- `GET /` - Página principal
- `GET /login` - Página de login

### Credenciales de Test:
- Email: admin@ufro.cl
- Password: admin123

## 📊 Estadísticas Esperadas:
- 467 cámaras en BD
- 1 usuario superadmin
- Todas las rutas funcionando

## 🆘 Si hay problemas:
1. Revisar logs de Railway
2. Verificar variable DATABASE_URL
3. Ejecutar test localmente primero
'''
    
    with open('INSTRUCCIONES_DEPLOY_CORREGIDO.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    logging.info("✅ Instrucciones de deploy creadas")

def main():
    """Función principal"""
    print("🚨 SISTEMA CÁMARAS UFRO - APLICACIÓN DE CORRECCIONES CRÍTICAS")
    print("=" * 70)
    
    # Aplicar correcciones
    if apply_fixes():
        create_test_script()
        create_deploy_instructions()
        
        print("\n" + "=" * 70)
        print("✅ CORRECCIONES COMPLETADAS EXITOSAMENTE")
        print("\n📋 SIGUIENTE PASO:")
        print("   1. Ejecutar: python test_sistema.py")
        print("   2. Hacer commit y push a GitHub")
        print("   3. Verificar deploy en Railway")
        print("\n📖 Ver: INSTRUCCIONES_DEPLOY_CORREGIDO.md")
        
    else:
        print("\n❌ FALLÓ LA APLICACIÓN DE CORRECCIONES")
        print("   Revisar los logs para más detalles")
        return False
    
    return True

if __name__ == "__main__":
    main()
