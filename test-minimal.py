# test-minimal.py
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
with app.app_context():
    from models.usuario import Usuario
    print("✅ Usuario importado sin error")
    
    # Intentamos una query mínima
    count = Usuario.query.count()
    print(f"✅ Hay {count} usuarios en la base")
    
    print("🎉 ¡ÉXITO! El sistema está listo.")