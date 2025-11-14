import os
import sys

# Añadir la carpeta raíz al PYTHONPATH (la que contiene app.py)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

print(f"🔍 Raíz del proyecto: {ROOT_DIR}")
print(f"📦 PYTHONPATH: {sys.path[0]}")

try:
    from app import app
    from models import db
    print("✅ app y db importados correctamente")
    
    # Probar modelos uno por uno
    try:
        from models.usuario import Usuario
        print("✅ Usuario cargado")
    except Exception as e:
        print(f"❌ Error en Usuario: {e}")
        import traceback; traceback.print_exc()
    
    try:
        from models.ubicacion import Ubicacion
        print("✅ Ubicacion cargada")
    except Exception as e:
        print(f"❌ Error en Ubicacion: {e}")
        import traceback; traceback.print_exc()
    
    try:
        from models.camara import Camara
        print("✅ Camara cargada")
    except Exception as e:
        print(f"❌ Error en Camara: {e}")
        import traceback; traceback.print_exc()
    
    try:
        from models.equipo import Switch, UPS, NVR, Gabinete, FuentePoder
        print("✅ Equipos cargados")
    except Exception as e:
        print(f"❌ Error en Equipos: {e}")
        import traceback; traceback.print_exc()
    
    try:
        from models.fotografia import Fotografia
        print("✅ Fotografia cargada")
    except Exception as e:
        print(f"❌ Error en Fotografia: {e}")
        import traceback; traceback.print_exc()
    
    print("🎉 Todos los modelos probados")

except Exception as e:
    print(f"❌ Error al importar app: {e}")
    import traceback; traceback.print_exc()