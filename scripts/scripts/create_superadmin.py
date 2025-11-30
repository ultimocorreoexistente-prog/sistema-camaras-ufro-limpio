import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db
from models.usuario import Usuario
from models.usuario_roles import UserRole

def create_superadmin():
<<<<<<< HEAD
email = "charles.jelvez@ufrontera.cl"
username = "charles.jelvez"
password = "Admin05"
full_name = "Charles Jelvez"

existing = Usuario.query.filter_by(email=email).first()
if existing:
print(f"ADVERTENCIA: Ya existe: {email}")
return

user = Usuario(
username=username,
email=email,
full_name=full_name,
role=UserRole.SUPERADMIN,
is_active=True
)
user.set_password(password)
db.session.add(user)
db.session.commit()
print(f"Superadmin creado: {email}")

if __name__ == "__main__":
with app.app_context():
create_superadmin()
=======
    email = "charles.jelvez@ufrontera.cl"
    username = "charles.jelvez"
    password = "Admin2025!"
    full_name = "Charles Jelvez"

    existing = Usuario.query.filter_by(email=email).first()
    if existing:
        print(f"ADVERTENCIA: Ya existe: {email}")
        return

    user = Usuario(
        username=username,
        email=email,
        full_name=full_name,
        role=UserRole.SUPERADMIN,
        is_active=True
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f"Superadmin creado: {email}")

if __name__ == "__main__":
    with app.app_context():
        create_superadmin()
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
