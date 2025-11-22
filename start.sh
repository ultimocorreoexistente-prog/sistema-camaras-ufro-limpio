#!/bin/bash
set -e  # Salir inmediatamente si un comando falla

echo "🔧 Iniciando sistema de cámaras UFRO..."
echo "   - Python: $(python --version)"
echo "   - Gunicorn: $(gunicorn --version 2>&1 | head -1)"

# 1. Verificar conexión a DB
echo "🔍 Paso 1/3: Verificando conexión a PostgreSQL..."
if python -c "from config import get_config; print('✅ Configuración cargada'); from models import db; print('✅ Modelo DB importado')" 2>&1; then
    echo "✅ Configuración y modelos cargados correctamente"
else
    echo "❌ ERROR: Falló la carga de configuración o modelos"
    exit 1
fi

# 2. Ejecutar migraciones (idempotente)
echo "🔄 Paso 2/3: Ejecutando migraciones idempotentes..."
if python migrate_data.py 2>&1; then
    echo "✅ Migraciones aplicadas correctamente"
else
    echo "❌ ERROR: Falló migrate_data.py"
    exit 1
fi

# 3. Arrancar Gunicorn
echo "🚀 Paso 3/3: Iniciando Gunicorn..."
exec gunicorn app:app \
    --workers 2 \
    --worker-class sync \
    --timeout 60 \
    --bind "0.0.0.0:${PORT:-8000}" \
    --log-level info \
    --access-logfile - \
    --error-logfile -