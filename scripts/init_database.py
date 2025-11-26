"""
Scripts de migración y utilidades para el Sistema de Cámaras UFRO.

Este directorio contiene scripts para:
- Migración de datos
- Inicialización de base de datos
- Scripts de mantenimiento
- Utilidades del sistema
"""

import os
import sys
from datetime import datetime

def init_database():
"""Script para inicializar la base de datos con datos por defecto."""
from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
try:
# Crear todas las tablas
db.create_all()
print(" Tablas creadas exitosamente")

# Crear usuario administrador por defecto
admin = User.query.filter_by(username='admin').first()
if not admin:
admin = User(
username='admin',
email='admin.sistema@ufrontera.cl',
full_name='Administrador del Sistema',
role='admin'
)
admin.set_password('admin13')
db.session.add(admin)
db.session.commit()
print(" Usuario administrador creado (admin/admin13)")

print(" Base de datos inicializada correctamente")

except Exception as e:
print(f" Error inicializando base de datos: {e}")
db.session.rollback()

def backup_database():
"""Script para crear backup de la base de datos."""
print(" Iniciando backup de base de datos...")

try:
from sqlalchemy import text
from app import app, db

with app.app_context():
# Obtener todos los registros de cada tabla
tables = ['usuarios', 'camaras', 'equipos', 'fotografias']
backup_data = {}

for table in tables:
try:
result = db.session.execute(text(f"SELECT * FROM {table}"))
backup_data[table] = result.fetchall()
print(f" Backup de tabla {table} completado")
except Exception as e:
print(f" Error respaldando {table}: {e}")

# Guardar backup
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file = f"backup_{timestamp}.json"

import json
with open(backup_file, 'w') as f:
json.dump(backup_data, f, default=str)

print(f" Backup guardado en {backup_file}")

except Exception as e:
print(f" Error creando backup: {e}")

if __name__ == '__main__':
import argparse

parser = argparse.ArgumentParser(description='Scripts de mantenimiento del sistema')
parser.add_argument('command', choices=['init-db', 'backup'], help='Comando a ejecutar')

args = parser.parse_args()

if args.command == 'init-db':
init_database()
elif args.command == 'backup':
backup_database()