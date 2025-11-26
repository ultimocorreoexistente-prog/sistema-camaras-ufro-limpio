#!/bin/bash
set -e

echo "🔧 Iniciando sistema de cámaras UFRO..."
echo "   - Python: $(python --version)"
echo "   - Gunicorn: $(gunicorn --version 2>&1 | head -1)"

# 1. Verificar conexión
echo "🔍 Paso 1/3: Verificando conexión a PostgreSQL..."
if python -c "from config import get_config; print('✅ Configuración cargada'); from models import db; print('✅ DB importada')" 2>&1; then
    echo "✅ Configuración y modelos cargados"
else
    echo "❌ ERROR: Falló carga de configuración"
    exit 1
fi

# 2. Setup de BD
echo "🔄 Paso 2/3: Ejecutando setup de BD..."
if python db_setup.py 2>&1; then
    echo "✅ Setup de BD aplicado"
else
    echo "❌ ERROR: Falló db_setup.py"
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