# app_min.py — versión mínima de prueba
import os
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'

# ✅ URI probada y correcta (usando tu output)
uri = "sqlite:///C:/Users/Usuario/sistema-camaras-ufro-limpio/instance/sistema_camaras.db"
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)

with app.app_context():
    print("🔧 Creando tablas...")
    db.create_all()
    print("✅ Tablas creadas.")