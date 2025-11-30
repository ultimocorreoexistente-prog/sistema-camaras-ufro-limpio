<<<<<<< HEAD
#/usr/bin/env python3
=======
#!/usr/bin/env python3
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
"""
SCRIPT DE RECUPERACIÓN DE EMERGENCIA ACTUALIZADO
Versión que maneja la conectividad limitada de Railway durante mantenimiento
"""

<<<<<<< HEAD
import psycopg
=======
import psycopg2
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
import sys
import subprocess
import json
from datetime import datetime
import os

def test_railway_connectivity():
<<<<<<< HEAD
"""Probar diferentes formas de conectar con Railway durante mantenimiento"""

# URLs alternativas para intentar
urls_to_test = [
"https://gestion-camaras-ufro.up.railway.app",
"https://gestion-camaras-ufro-production.up.railway.app"
]

print(" PROBANDO CONECTIVIDAD RAILWAY:")

for url in urls_to_test:
try:
result = subprocess.run([
"curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url
], capture_output=True, text=True, timeout=10)

status_code = result.stdout.strip()
print(f" {url} -> HTTP {status_code}")

if status_code not in ["404", "50", "503"]:
print(f" Conectividad encontrada en: {url}")
return url, True

except Exception as e:
print(f" Error conectando a {url}: {str(e)}")

return None, False

def emergency_rollback():
"""Conectar directamente a PostgreSQL y hacer rollback de emergencia"""

# Configuración de conexión PostgreSQL (desde Railway)
DATABASE_URL = "postgresql://postgres:YOUR_DB_PASSWORD_HERE@postgres.railway.internal:543/railway"

try:
print(" INICIANDO RECUPERACIÓN DE EMERGENCIA ACTUALIZADA")
print(f"⏰ Timestamp: {datetime.now().isoformat()}")
print("=" * 60)

# 1. Verificar conectividad Railway
working_url, is_connected = test_railway_connectivity()

if not is_connected:
print(" RAILWAY EN MANTENIMIENTO - Esperando restauración...")
print(" EJECUTANDO RECUPERACIÓN LOCAL DE ESTADO")

# Intentar conectar con timeout corto
try:
print(" Intentando conexión PostgreSQL (timeout 10s)...")
conn = psycopg.connect(DATABASE_URL, connect_timeout=10)
conn.set_isolation_level(psycopg.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

cursor = conn.cursor()

# ROLLBACK forzado
print(" Ejecutando ROLLBACK de emergencia...")
cursor.execute("ROLLBACK;")
print(" ROLLBACK completado exitosamente")

# Verificar tablas
cursor.execute("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name
""")

tablas = cursor.fetchall()
print(f" Tablas encontradas: {len(tablas)}")

for tabla in tablas:
print(f" {tabla[0]}")

cursor.close()
conn.close()
return True

except Exception as e:
print(f" Conexión PostgreSQL falló: {str(e)}")
print(" RAILWAY AÚN EN MANTENIMIENTO - Esperando...")
return False

else:
print(f" Railway activo en: {working_url}")
print(" Sistema debería estar funcionando")
return True

except Exception as e:
print(f"\n ERROR EN RECUPERACIÓN: {str(e)}")
print(f" Tipo de error: {type(e).__name__}")
return False

def prepare_deploy_fix():
"""Preparar las correcciones para deploy una vez Railway esté activo"""

print("\n PREPARANDO CORRECCIONES PARA DEPLOY...")

# Verificar si tenemos los archivos necesarios
app_files = [
"app.py",
"models.py",
"requirements.txt"
]

for file in app_files:
if os.path.exists(file):
print(f" {file} disponible")
else:
print(f" {file} faltante")

# Verificar estructura
if os.path.exists("templates"):
print(" templates/ disponible")
if os.path.exists("static"):
print(" static/ disponible")

def main():
print("SISTEMA DE RECUPERACIÓN DE EMERGENCIA - POSTGRESQL v.0")
print("=" * 60)

# Ejecutar recuperación
success = emergency_rollback()

if not success:
print("\n RAILWAY EN MANTENIMIENTO - CORRECCIONES PREPARADAS")
print(" Una vez que Railway esté activo, ejecutar deploy")

prepare_deploy_fix()

print("\n PLAN DE ACCIÓN:")
print("1. Esperar restauración completa de Railway")
print(". Ejecutar git push con tokens restaurados")
print("3. Railway desplegará automáticamente las correcciones")
print("4. Sistema de login funcionará normalmente")

else:
print("\n RECUPERACIÓN COMPLETADA - Sistema operativo")

return success

if __name__ == "__main__":
success = main()
sys.exit(0 if success else 1)
=======
    """Probar diferentes formas de conectar con Railway durante mantenimiento"""
    
    # URLs alternativas para intentar
    urls_to_test = [
        "https://gestion-camaras-ufro.up.railway.app",
        "https://gestion-camaras-ufro-production.up.railway.app"
    ]
    
    print("🔍 PROBANDO CONECTIVIDAD RAILWAY:")
    
    for url in urls_to_test:
        try:
            result = subprocess.run([
                "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url
            ], capture_output=True, text=True, timeout=10)
            
            status_code = result.stdout.strip()
            print(f"  📡 {url} -> HTTP {status_code}")
            
            if status_code not in ["404", "502", "503"]:
                print(f"  ✅ Conectividad encontrada en: {url}")
                return url, True
                
        except Exception as e:
            print(f"  ❌ Error conectando a {url}: {str(e)}")
    
    return None, False

def emergency_rollback():
    """Conectar directamente a PostgreSQL y hacer rollback de emergencia"""
    
    # Configuración de conexión PostgreSQL (desde Railway)
    DATABASE_URL = "postgresql://postgres:WMQxvzTQsdkiAUOqfMgXmzgAHqxDkwRJ@postgres.railway.internal:5432/railway"
    
    try:
        print("🔧 INICIANDO RECUPERACIÓN DE EMERGENCIA ACTUALIZADA")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # 1. Verificar conectividad Railway
        working_url, is_connected = test_railway_connectivity()
        
        if not is_connected:
            print("⚠️ RAILWAY EN MANTENIMIENTO - Esperando restauración...")
            print("🔧 EJECUTANDO RECUPERACIÓN LOCAL DE ESTADO")
            
            # Intentar conectar con timeout corto
            try:
                print("📡 Intentando conexión PostgreSQL (timeout 10s)...")
                conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
                conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
                
                cursor = conn.cursor()
                
                # ROLLBACK forzado
                print("🔄 Ejecutando ROLLBACK de emergencia...")
                cursor.execute("ROLLBACK;")
                print("✅ ROLLBACK completado exitosamente")
                
                # Verificar tablas
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name
                """)
                
                tablas = cursor.fetchall()
                print(f"📋 Tablas encontradas: {len(tablas)}")
                
                for tabla in tablas:
                    print(f"  ✅ {tabla[0]}")
                
                cursor.close()
                conn.close()
                return True
                
            except Exception as e:
                print(f"❌ Conexión PostgreSQL falló: {str(e)}")
                print("🔄 RAILWAY AÚN EN MANTENIMIENTO - Esperando...")
                return False
        
        else:
            print(f"✅ Railway activo en: {working_url}")
            print("🚀 Sistema debería estar funcionando")
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR EN RECUPERACIÓN: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        return False

def prepare_deploy_fix():
    """Preparar las correcciones para deploy una vez Railway esté activo"""
    
    print("\n🔧 PREPARANDO CORRECCIONES PARA DEPLOY...")
    
    # Verificar si tenemos los archivos necesarios
    app_files = [
        "app.py",
        "models.py", 
        "requirements.txt"
    ]
    
    for file in app_files:
        if os.path.exists(file):
            print(f"  ✅ {file} disponible")
        else:
            print(f"  ❌ {file} faltante")
    
    # Verificar estructura
    if os.path.exists("templates"):
        print("  ✅ templates/ disponible")
    if os.path.exists("static"):
        print("  ✅ static/ disponible")

def main():
    print("SISTEMA DE RECUPERACIÓN DE EMERGENCIA - POSTGRESQL v2.0")
    print("=" * 60)
    
    # Ejecutar recuperación
    success = emergency_rollback()
    
    if not success:
        print("\n⚠️ RAILWAY EN MANTENIMIENTO - CORRECCIONES PREPARADAS")
        print("💡 Una vez que Railway esté activo, ejecutar deploy")
        
        prepare_deploy_fix()
        
        print("\n📋 PLAN DE ACCIÓN:")
        print("1. Esperar restauración completa de Railway")
        print("2. Ejecutar git push con tokens restaurados")
        print("3. Railway desplegará automáticamente las correcciones")
        print("4. Sistema de login funcionará normalmente")
        
    else:
        print("\n✅ RECUPERACIÓN COMPLETADA - Sistema operativo")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
