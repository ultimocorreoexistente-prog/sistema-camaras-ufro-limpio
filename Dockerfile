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

# Copiar aplicación principal
COPY app.py .
COPY Procfile .
COPY migrate_data.py .

# ✅ CORRECCIÓN CRÍTICA: copiar carpeta models/ completa (NO models.py)
COPY models ./models

# Crear y copiar assets
RUN mkdir -p templates static uploads logs
COPY templates ./templates
COPY static ./static

# Configuración de entorno para producción
ENV PORT=8000
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Exponer puerto
EXPOSE 8000

# ✅ Comando de arranque robusto (timeout aumentado para Railway)
CMD ["gunicorn", "app:app", "--workers", "2", "--timeout", "60", "--bind", "0.0.0.0:8000"]