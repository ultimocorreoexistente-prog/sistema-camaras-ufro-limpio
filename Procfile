# ================================
# PROCFILE - SISTEMA DE GESTIÓN DE CÁMARAS UFRO
# ================================

# Configuración principal para Railway/Heroku
web: gunicorn app:app --workers 1 --timeout 60 --bind 0.0.0.0:$PORT
