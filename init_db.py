from app import app, db
from models import Usuario
import secrets

def crear_superadmin_seguro():
    if Usuario.query.filter_by(email='Charles.Jelvez@ufrontera.cl').first():
        print("✅ Superadmin ya existe")
        return

    temp_pass = secrets.token_urlsafe(12)[:12]
    superadmin = Usuario(
        username='charles.jelvez',
        email='Charles.Jelvez@ufrontera.cl',
        nombre='Charles Jelvez',
        rol='superadmin',
        activo=True
    )
    superadmin.password_hash = secrets.token_urlsafe(20)  # placeholder
    from werkzeug.security import generate_password_hash
    superadmin.password_hash = generate_password_hash(temp_pass)
    db.session.add(superadmin)
    db.session.commit()
    
    print("✅ Superadmin creado")
    print(f"📧 Email: Charles.Jelvez@ufrontera.cl")
    print(f"🔑 Contraseña temporal: {temp_pass}")
    print("⚠️  Debe cambiarla al primer login.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Tablas creadas")
        crear_superadmin_seguro()
        print(f"📊 Total usuarios: {Usuario.query.count()}")