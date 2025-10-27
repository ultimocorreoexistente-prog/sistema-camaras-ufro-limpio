#!/usr/bin/env python3
"""
Script de migración de nomenclatura: usuario → usuarios
Fecha: 2025-10-27 09:52:20
Descripción: Migra la base de datos para unificar nomenclatura de tablas

USO:
1. Ejecutar: python migrate_nomenclature.py
2. O vía endpoint HTTP: POST /admin/migrate-nomenclature

SEGURIDAD:
- Solo ejecutar cuando no haya usuarios activos en el sistema
- Hacer backup de la BD antes de ejecutar
- Verificar que todas las foreign keys están correctamente actualizadas
"""

import os
import sys
from sqlalchemy import text
from models import db, Usuario

def migrate_usuario_to_usuarios():
    """
    Migra la tabla usuario a usuarios de manera segura
    """
    try:
        print("🔄 Iniciando migración usuario → usuarios...")
        
        # Verificar conexión
        with db.engine.connect() as conn:
            # Verificar que la tabla 'usuario' existe
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'usuario'
                )
            """))
            usuario_exists = result.scalar()
            
            if not usuario_exists:
                print("❌ ERROR: La tabla 'usuario' no existe")
                return False
            
            # Verificar que no hay conflictos con 'usuarios'
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'usuarios'
                )
            """))
            usuarios_exists = result.scalar()
            
            if usuarios_exists:
                print("⚠️ ADVERTENCIA: La tabla 'usuarios' ya existe")
                print("Abortando migración para evitar pérdida de datos")
                return False
            
            print("✅ Verificaciones previas completadas")
            
            # Ejecutar migración en transacción
            with conn.begin():
                # Renombrar tabla
                conn.execute(text("ALTER TABLE usuario RENAME TO usuarios"))
                print("✅ Tabla renombrada: usuario → usuarios")
                
                # Actualizar foreign keys constraints
                print("🔄 Actualizando foreign keys...")
                
                # Buscar y actualizar constraints
                constraints_query = text("""
                    SELECT conname, relname, a.attname 
                    FROM pg_constraint c
                    JOIN pg_class t ON t.oid = c.conrelid  
                    JOIN pg_attribute a ON a.attrelid = t.oid 
                    WHERE c.contype = 'f' 
                    AND pg_get_constraintdef(c.oid) LIKE '%usuario.id%'
                """)
                
                constraints = conn.execute(constraints_query).fetchall()
                
                for conname, table_name, column_name in constraints:
                    try:
                        # Eliminar constraint antiguo
                        conn.execute(text(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {conname}"))
                        
                        # Crear nuevo constraint
                        new_name = conname.replace('usuario', 'usuarios')
                        conn.execute(text(f"""
                            ALTER TABLE {table_name} 
                            ADD CONSTRAINT {new_name} 
                            FOREIGN KEY ({column_name}) REFERENCES usuarios(id)
                        """))
                        
                        print(f"✅ Constraint actualizado: {conname} → {new_name}")
                        
                    except Exception as e:
                        print(f"⚠️ Error con constraint {conname}: {e}")
                        # Continuar con otros constraints
                
                # Verificar integridad
                result = conn.execute(text("SELECT COUNT(*) FROM usuarios"))
                user_count = result.scalar()
                print(f"✅ Migración exitosa: {user_count} usuarios preservados")
            
            return True
            
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

def verify_migration():
    """
    Verifica que la migración fue exitosa
    """
    try:
        with db.engine.connect() as conn:
            # Verificar que usuarios existe y usuario no
            usuario_check = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'usuario')")).scalar()
            usuarios_check = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'usuarios')")).scalar()
            
            print(f"Tabla 'usuario' existe: {usuario_check}")
            print(f"Tabla 'usuarios' existe: {usuarios_check}")
            
            if not usuario_check and usuarios_check:
                print("✅ Verificación exitosa: migración completada correctamente")
                return True
            else:
                print("❌ Verificación falló: la migración no se completó correctamente")
                return False
                
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

if __name__ == "__main__":
    print("🚨 MIGRACIÓN DE NOMENCLATURA USUARIO → USUARIOS")
    print("=" * 50)
    print("⚠️ IMPORTANTE: Asegúrate de que:")
    print("   - El sistema esté inactivo")
    print("   - Hayas hecho backup de la BD")
    print("   - No hay conexiones activas a la BD")
    print()
    
    confirm = input("¿Continuar con la migración? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y', 'sí', 's']:
        success = migrate_usuario_to_usuarios()
        
        if success:
            print("\n🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("\n📋 PRÓXIMOS PASOS:")
            print("1. Actualizar models.py: __tablename__ = 'usuarios'")
            print("2. Actualizar ForeignKey('usuarios.id') en models.py")
            print("3. Reiniciar la aplicación")
            print("4. Verificar funcionalidades")
            
            verify = input("\n¿Verificar migración? (yes/no): ").strip().lower()
            if verify in ['yes', 'y', 'sí', 's']:
                verify_migration()
                
        else:
            print("\n❌ MIGRACIÓN FALLÓ")
            sys.exit(1)
    else:
        print("Migración cancelada por el usuario")
        sys.exit(0)