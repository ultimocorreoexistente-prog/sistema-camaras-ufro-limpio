# app_min.py — versión mínima de prueba
import os
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'

<<<<<<< HEAD
<<<<<<< HEAD
# URI probada y correcta (usando tu output)
=======
# ✅ URI probada y correcta (usando tu output)
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
=======
# ✅ URI probada y correcta (usando tu output)
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
uri = "sqlite:///C:/Users/Usuario/sistema-camaras-ufro-limpio/instance/sistema_camaras.db"
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Test(db.Model):
<<<<<<< HEAD
<<<<<<< HEAD
id = db.Column(db.Integer, primary_key=True)

with app.app_context():
print(" Creando tablas...")
db.create_all()
print(" Tablas creadas.")
=======
=======
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
    id = db.Column(db.Integer, primary_key=True)

with app.app_context():
    print("🔧 Creando tablas...")
    db.create_all()
<<<<<<< HEAD
    print("✅ Tablas creadas.")
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
=======
    print("✅ Tablas creadas.")
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
