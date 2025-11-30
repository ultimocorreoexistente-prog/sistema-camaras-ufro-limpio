# test-minimal.py
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
with app.app_context():
<<<<<<< HEAD
<<<<<<< HEAD
from models.usuario import Usuario
print(" Usuario importado sin error")

# Intentamos una query mínima
count = Usuario.query.count()
print(f" Hay {count} usuarios en la base")

print(" ¡ÉXITO El sistema está listo.")
=======
=======
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
    from models.usuario import Usuario
    print("✅ Usuario importado sin error")
    
    # Intentamos una query mínima
    count = Usuario.query.count()
    print(f"✅ Hay {count} usuarios en la base")
    
<<<<<<< HEAD
    print("🎉 ¡ÉXITO! El sistema está listo.")
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
=======
    print("🎉 ¡ÉXITO! El sistema está listo.")
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
