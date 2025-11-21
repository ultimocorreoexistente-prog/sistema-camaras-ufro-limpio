# Usa Python 3.11 (compatible con tus modelos y Railway)
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (gcc para psycopg2-binary)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación principal
COPY app.py .
COPY migrate_data.py .
COPY Procfile .

# ✅ CORRECCIÓN CRÍTICA: copiar carpeta models/ (NO models.py)
COPY models ./models

# Crear directorios necesarios
RUN mkdir -p templates static uploads logs

# Copiar assets
COPY templates ./templates
COPY static ./static

# Configuración de entorno para producción
ENV PORT=8000
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Exponer puerto
EXPOSE 8000

# Comando de arranque (usando gunicorn desde Procfile o directo)
CMD ["gunicorn", "app:app", "--workers", "2", "--timeout", "30", "--bind", "0.0.0.0:8000"]