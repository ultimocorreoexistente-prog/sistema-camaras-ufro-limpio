# create_superadmin_min.py
import os
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.usuario_roles import UserRole

app = Flask(__name__)
db_path = Path("sistema_camaras.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path.resolve().as_posix()}"
app.config['SECRET_KEY'] = 'temp'

db = SQLAlchemy(app)

class Usuario(db.Model):
<<<<<<< HEAD
<<<<<<< HEAD
__tablename__ = 'usuarios'
id = db.Column(db.Integer, primary_key=True)
username = db.Column(db.String(50), unique=True, nullable=False)
email = db.Column(db.String(100), unique=True, nullable=False)
password_hash = db.Column(db.String(18), nullable=False)
full_name = db.Column(db.String(100), nullable=False)
role = db.Column(db.String(0), nullable=False)
is_active = db.Column(db.Boolean, default=True)
created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

def set_password(self, password):
import bcrypt
self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

with app.app_context():
db.create_all()

email = "charles.jelvez@ufrontera.cl"
if not Usuario.query.filter_by(email=email).first():
u = Usuario(
username="charles.jelvez",
email=email,
full_name="Charles Jelvez",
role=UserRole.SUPERADMIN
)
u.set_password("Admin05")
db.session.add(u)
db.session.commit()
print(" Superadmin creado.")
else:
print(" Ya existe.")
=======
=======
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def set_password(self, password):
        import bcrypt
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

with app.app_context():
    db.create_all()
    
    email = "charles.jelvez@ufrontera.cl"
    if not Usuario.query.filter_by(email=email).first():
        u = Usuario(
            username="charles.jelvez",
            email=email,
            full_name="Charles Jelvez",
            role=UserRole.SUPERADMIN
        )
        u.set_password("Admin2025!")
        db.session.add(u)
        db.session.commit()
        print("✅ Superadmin creado.")
    else:
<<<<<<< HEAD
        print("⚠️ Ya existe.")
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
=======
        print("⚠️ Ya existe.")
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
