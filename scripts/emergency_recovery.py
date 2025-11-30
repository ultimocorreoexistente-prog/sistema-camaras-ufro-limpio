#!/usr/bin/env python3
"""
SCRIPT DE RECUPERACIÓN DE EMERGENCIA
Este script se conecta directamente a PostgreSQL para desbloquear transacciones
y restaurar el funcionamiento del login.
"""

import psycopg2
import sys
from datetime import datetime

def emergency_rollback():
    """Conectar directamente a PostgreSQL y hacer rollback de emergencia"""
    
    # Configuración de conexión PostgreSQL (desde Railway)
    DATABASE_URL = "postgresql://postgres:WMQxvzTQsdkiAUOqfMgXmzgAHqxDkwRJ@postgres.railway.internal:5432/railway"
    
    try:
        print("🔧 INICIANDO RECUPERACIÓN DE EMERGENCIA")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Conectar directamente a PostgreSQL
        print("📡 Conectando a PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # 1. FORZAR rollback de cualquier transacción pendiente
        print("🔄 Ejecutando ROLLBACK de emergencia...")
        cursor.execute("ROLLBACK;")
        print("✅ ROLLBACK completado exitosamente")
        
        # 2. Verificar estado de la base de datos
        print("\n📊 VERIFICANDO ESTADO DE LA BASE DE DATOS:")
        
        # Verificar tablas existentes
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
        
        # 3. Verificar usuarios (para confirmar login)
        print(f"\n👤 VERIFICANDO TABLA USUARIOS:")
        cursor.execute("SELECT COUNT(*) FROM usuarios;")
        count_usuarios = cursor.fetchone()[0]
        print(f"  ✅ Total usuarios: {count_usuarios}")
        
        # 4. Verificar usuarios duplicados (tabla singular)
        cursor.execute("SELECT COUNT(*) FROM usuario;")
        try:
            count_usuario = cursor.fetchone()[0]
            print(f"  ⚠️ Usuarios duplicados (tabla singular): {count_usuario}")
            if count_usuario > 0:
                print("  🔧 ELIMINANDO TABLA USUARIO DUPLICADA...")
                cursor.execute("DROP TABLE usuario CASCADE;")
                print("  ✅ Tabla usuario duplicada eliminada")
        except psycopg2.errors.UndefinedTable:
            print("  ✅ No hay tabla usuario duplicada")
        
        # 5. Verificar otras tablas duplicadas conocidas
        tablas_problematicas = ['ubicacion', 'gabinete', 'switch', 'camara', 'ups', 'nvr']
        
        print(f"\n🔍 VERIFICANDO TABLAS DUPLICADAS:")
        for tabla in tablas_problematicas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla};")
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"  ⚠️ Tabla {tabla}: {count} registros")
                    print(f"  🔧 ELIMINANDO TABLA {tabla} DUPLICADA...")
                    cursor.execute(f"DROP TABLE {tabla} CASCADE;")
                    print(f"  ✅ Tabla {tabla} duplicada eliminada")
                else:
                    print(f"  ✅ Tabla {tabla}: no existe o está vacía")
            except psycopg2.errors.UndefinedTable:
                print(f"  ✅ Tabla {tabla}: no existe")
        
        # 6. Confirmar estado final
        print(f"\n📊 ESTADO FINAL DE LA BASE DE DATOS:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        tablas_finales = cursor.fetchall()
        print(f"📋 Tablas finales: {len(tablas_finales)}")
        
        for tabla in tablas_finales:
            print(f"  ✅ {tabla[0]}")
        
        # 7. Test final de conexión
        print(f"\n🧪 TEST DE CONEXIÓN:")
        cursor.execute("SELECT current_timestamp;")
        timestamp = cursor.fetchone()[0]
        print(f"  ✅ Conexión exitosa: {timestamp}")
        
        print("\n" + "=" * 60)
        print("🎉 RECUPERACIÓN DE EMERGENCIA COMPLETADA EXITOSAMENTE")
        print("🚀 El sistema de login debería funcionar normalmente ahora")
        print("=" * 60)
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN RECUPERACIÓN: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("SISTEMA DE RECUPERACIÓN DE EMERGENCIA - POSTGRESQL")
    print("=" * 60)
    
    success = emergency_rollback()
    
    if success:
        print("\n✅ PROCESO COMPLETADO - El sistema debería estar funcionando")
        sys.exit(0)
    else:
        print("\n❌ PROCESO FALLÓ - Revisar errores arriba")
        sys.exit(1)