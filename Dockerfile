# Usa Python 3.11 (compatible con tus modelos y Railway)
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (gcc para psycopg2-binary y bcrypt)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ COPIAR TODOS LOS ARCHIVOS NECESARIOS (corregido)
COPY app.py .
COPY config.py .          # ← crítico para "ModuleNotFoundError: config"
COPY Procfile .
COPY migrate_data.py .
COPY models ./models      # ← copia la carpeta completa (no models.py)
COPY templates ./templates
COPY static ./static

# Crear directorios necesarios
RUN mkdir -p uploads logs

# Configuración de entorno para producción
ENV PORT=8000
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Exponer puerto
EXPOSE 8000

# ✅ Comando de arranque robusto (usando Procfile implícito)
CMD ["gunicorn", "app:app", "--workers", "2", "--timeout", "60", "--bind", "0.0.0.0:8000"]