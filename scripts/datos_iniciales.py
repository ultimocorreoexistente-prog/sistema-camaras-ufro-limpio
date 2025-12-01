# scripts/datos_iniciales.py
from models import db, Usuario

def crear_usuario_admin():
    admin = Usuario.query.filter_by(email='admin@ufro.cl').first()
    if not admin:
        admin = Usuario(
            email='admin@ufro.cl',
            nombre='Administrador',
            apellido='Sistema',
            rol='ADMIN'
        )
        admin.set_password('Admin2025!')  # usa tu método seguro de hash
        db.session.add(admin)
        db.session.commit()
        print("✅ Usuario administrador creado.")
    else:
        print("ℹ️ Usuario administrador ya existe.")