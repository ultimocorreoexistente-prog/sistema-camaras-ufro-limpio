# scripts/get_schema.py
import os
import sys
from pathlib import Path

# Añadir raíz del proyecto al PATH
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

# Detectar cómo se inicializa tu app
try:
    # Opción 1: app está en __init__.py como paquete
    from app import create_app, db
except (ImportError, AttributeError):
    try:
        # Opción 2: app es una variable en app.py
        from app import app as create_app_instance
        db = create_app_instance.extensions['sqlalchemy'].db
        def create_app():
            return create_app_instance
    except Exception:
        # Opción 3: app factory en otro lado (común en Flask)
        try:
            from main import app as create_app_instance  # o run.py, o __init__.py
            db = create_app_instance.extensions['sqlalchemy'].db
            def create_app():
                return create_app_instance
        except Exception as e3:
            print("❌ No se pudo encontrar la app ni db.")
            print("💡 Asegúrate de que:")
            print("   - Tienes una app Flask con SQLAlchemy")
            print("   - db está accesible como 'db' en algún módulo")
            sys.exit(1)

# Crear contexto
try:
    app = create_app()
    app.app_context().push()
except Exception as e:
    print(f"⚠️ Error al crear app: {e}")
    sys.exit(1)

# Definir tablas a inspeccionar
TABLES = [
    'fuente_poder', 'fuentes_poder',
    'nvr', 'nvr_dvr',
    'puerto_switch', 'puertos_switch'
]

print("🔍 Conectando a base de datos...")

# Usar db.engine directamente (más robusto que session)
from sqlalchemy import text

for tbl in TABLES:
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                  AND table_name = :tbl 
                ORDER BY ordinal_position
            """), {"tbl": tbl}).fetchall()
        
        if result:
            print(f"-- {tbl}")
            for col, typ in result:
                print(f"  {col} ({typ})")
        else:
            print(f"-- {tbl}: NO EXISTE")
    except Exception as e:
        print(f"-- {tbl}: ERROR → {e}")

print("\n✅ Listo.")