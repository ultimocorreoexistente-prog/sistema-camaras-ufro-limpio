# ================================
# PROCFILE - SISTEMA DE GESTIÓN DE CÁMARAS UFRO
# ================================

# Configuración principal para Railway/Heroku
web: gunicorn "app:app" --bind 0.0.0.0:$PORT --workers 4 --worker-class gevent --worker-connections 1000 --max-requests 1000 --max-requests-jitter 100 --timeout 120 --keepalive 2 --access-logfile - --error-logfile -

# Configuración alternativa para Heroku
# web: gunicorn "app:app" --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --keepalive 2

# Configuración para desarrollo local (solo para referencia)
# web: python app.py