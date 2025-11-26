#!/bin/bash
set -e
echo "🔧 Iniciando despliegue en Railway..."
if [ -z "$SECRET_KEY" ]; then
  echo "❌ ERROR: SECRET_KEY no definida"
  exit 1
fi
if [ -z "$DATABASE_URL" ]; then
  echo "❌ ERROR: DATABASE_URL no definida"
  exit 1
fi
echo "✅ Variables OK"
python -c "
from app import app
from models import db
with app.app_context():
    db.create_all()
    print('✅ Tablas creadas')
"
exec gunicorn app:app --workers 1 --timeout 60 --bind 0.0.0.0:$PORT