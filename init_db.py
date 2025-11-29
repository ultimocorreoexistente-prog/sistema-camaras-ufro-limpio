from app import app, db
from models import Usuario
import secrets

<<<<<<< HEAD
<<<<<<< HEAD
with app.app_context():
db.create_all()
print('Tablas creadas exitosamente')

if Usuario.query.count() == 0:
usuarios = [
Usuario(username='admin', rol='admin', nombre_completo='Administrador', activo=True),
Usuario(username='supervisor', rol='supervisor', nombre_completo='Supervisor', activo=True),
Usuario(username='tecnico1', rol='tecnico', nombre_completo='Técnico 1', activo=True),
Usuario(username='visualizador', rol='visualizador', nombre_completo='Visualizador', activo=True)
]

passwords = ['admin13', 'super13', 'tecnico13', 'viz13']

for user, password in zip(usuarios, passwords):
user.set_password(password)
db.session.add(user)

db.session.commit()
print('Usuarios creados exitosamente')
else:
print('Los usuarios ya existen')

print(f'\nTotal usuarios: {Usuario.query.count()}')
=======
=======
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
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
<<<<<<< HEAD
        print(f"📊 Total usuarios: {Usuario.query.count()}")
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
=======
        print(f"📊 Total usuarios: {Usuario.query.count()}")
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
