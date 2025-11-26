# test_models.py
from app import app
with app.app_context():
    print("📥 Probando importación de modelos uno por uno...")
    
    try:
        from models.base import BaseModel
        print("✅ BaseModel")
    except Exception as e:
        print(f"❌ BaseModel: {e}")
        raise

    try:
        from models.usuario_roles import UserRole
        print("✅ UserRole")
    except Exception as e:
        print(f"❌ UserRole: {e}")
        raise

    try:
        from models.usuario import Usuario
        print("✅ Usuario")
    except Exception as e:
        print(f"❌ Usuario: {e}")
        import traceback
        traceback.print_exc()
        raise

    try:
        from models.ubicacion import Ubicacion
        print("✅ Ubicacion")
    except Exception as e:
        print(f"❌ Ubicacion: {e}")
        raise

    try:
        from models.camara import Camara
        print("✅ Camara")
    except Exception as e:
        print(f"❌ Camara: {e}")
        raise