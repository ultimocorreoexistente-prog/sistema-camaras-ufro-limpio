#!/usr/bin/env python3
"""
health-check.py
Verifica la salud del sistema de cámaras UFRO antes de desplegar.
Ejecutar antes de `git push` para evitar errores en Railway.
"""
import os
import sys
import tempfile
import sqlite3
from pathlib import Path

print("🔍 Iniciando verificación de salud del sistema...\n")

# 1. Verificar carpeta 'instance'
print("1. Verificando carpeta 'instance'...")
instance_dir = Path("instance")
if not instance_dir.exists():
    print("   ❌ Carpeta 'instance' no existe.")
    sys.exit(1)
else:
    print(f"   ✅ Carpeta 'instance' existe: {instance_dir.resolve()}")

# 2. Verificar permisos de escritura en 'instance'
print("2. Verificando permisos de escritura en 'instance'...")
try:
    test_file = instance_dir / ".write_test"
    test_file.write_text("OK")
    test_file.unlink()
    print("   ✅ Permisos de escritura OK.")
except Exception as e:
    print(f"   ❌ Error de escritura en 'instance': {e}")
    sys.exit(1)

# 3. Probar conexión SQLite directamente
print("3. Probando conexión SQLite directa...")
db_path = instance_dir / "sistema_camaras.db"
try:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    conn.close()
    print(f"   ✅ SQLite OK: {db_path}")
except Exception as e:
    print(f"   ❌ Error SQLite: {e}")
    sys.exit(1)

# 4. Inicializar app y verificar SQLAlchemy
print("4. Inicializando Flask + SQLAlchemy...")
try:
    from app import app
    print("   ✅ App importada sin errores.")
except Exception as e:
    print(f"   ❌ Error al importar app.py: {e}")
    sys.exit(1)

# 5. Verificar modelos dentro del contexto
print("5. Verificando modelos y relaciones...")
try:
    with app.app_context():
        from models.usuario import Usuario
        from models.ubicacion import Ubicacion
        from models.camara import Camara
        from models.fotografia import Fotografia
        from models.falla import Falla
        from models import db

        # 5a. Crear tablas (si no existen)
        db.create_all()
        print("   ✅ Tablas creadas/verificadas.")

        # 5b. Probar relaciones jerárquicas
        # Ubicacion → children
        campus = Ubicacion(nombre="Campus A", tipo="campus", codigo="CA")
        edificio = Ubicacion(nombre="Edificio B", tipo="edificio", parent=campus)
        db.session.add_all([campus, edificio])
        db.session.flush()  # para obtener IDs

        assert campus.children == [edificio], "❌ Relación Ubicacion.children falló"
        assert edificio.parent == campus, "❌ Relación Ubicacion.parent falló"
        print("   ✅ Relación jerárquica Ubicacion OK.")

        # Fotografia → versions
        foto1 = Fotografia(filename="original.jpg", filepath="/tmp/original.jpg")
        foto2 = Fotografia(filename="recorte.jpg", filepath="/tmp/recorte.jpg", parent_photo=foto1)
        db.session.add_all([foto1, foto2])
        db.session.flush()

        assert foto1.versions == [foto2], "❌ Relación Fotografia.versions falló"
        assert foto2.parent_photo == foto1, "❌ Relación Fotografia.parent_photo falló"
        print("   ✅ Relación jerárquica Fotografia OK.")

        # Falla → related_fallas
        falla1 = Falla(descripcion="Cámara sin señal", severidad="alta", equipo_id=1, equipo_type="camara")
        falla2 = Falla(descripcion="Duplicado", severidad="baja", parent_falla=falla1, equipo_id=1, equipo_type="camara")
        db.session.add_all([falla1, falla2])
        db.session.flush()

        assert falla1.related_fallas == [falla2], "❌ Relación Falla.related_fallas falló"
        assert falla2.related_falla == falla1, "❌ Relación Falla.related_falla falló"
        print("   ✅ Relación jerárquica Falla OK.")

        # 5c. Probar FK explícitas (evitar NoForeignKeysError)
        from models.usuario_roles import UserRole
        superadmin = Usuario(
            username="test",
            email="test@ufrontera.cl",
            full_name="Test User",
            role=UserRole.SUPERADMIN
        )
        superadmin.set_password("test")
        db.session.add(superadmin)
        db.session.flush()

        camara_test = Camara(
            codigo="TEST-001",
            nombre="Cámara de Prueba",
            ubicacion=edificio,
            created_by_user=superadmin
        )
        db.session.add(camara_test)
        db.session.commit()

        assert camara_test.created_by_user == superadmin
        assert superadmin.created_camaras == [camara_test]
        print("   ✅ Relaciones FK explícitas (Usuario ↔ Camara) OK.")

        # 5d. Limpiar datos de prueba (sin borrar tablas)
        db.session.delete(camara_test)
        db.session.delete(falla2)
        db.session.delete(falla1)
        db.session.delete(foto2)
        db.session.delete(foto1)
        db.session.delete(edificio)
        db.session.delete(campus)
        db.session.delete(superadmin)
        db.session.commit()

        print("   ✅ Datos de prueba limpiados.")
except Exception as e:
    print(f"   ❌ Error en verificación de modelos: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 6. Verificar superadmin real
print("6. Verificando superadmin real...")
try:
    with app.app_context():
        from models.usuario import Usuario
        superadmin = Usuario.query.filter_by(email="charles.jelvez@ufrontera.cl").first()
        if superadmin:
            print(f"   ✅ Superadmin encontrado: {superadmin.email} (rol: {superadmin.role})")
        else:
            print("   ⚠️  Superadmin no encontrado (puede crearse con scripts/create_superadmin.py)")
except Exception as e:
    print(f"   ❌ Error al verificar superadmin: {e}")
    sys.exit(1)

print("\n✅ ¡TODAS LAS VERIFICACIONES PASARON!")
print("   Sistema listo para desarrollo local y despliegue en Railway.")