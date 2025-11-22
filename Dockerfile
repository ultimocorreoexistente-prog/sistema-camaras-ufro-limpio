FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación
COPY app.py .
COPY config.py .
COPY migrate_data.py .
COPY start.sh .
COPY models ./models
COPY templates ./templates
COPY static ./static

# Dar permisos y crear directorios
RUN chmod +x start.sh && \
    mkdir -p uploads logs

# Configuración
ENV FLASK_ENV=production \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# ✅ ENTRYPOINT robusto
ENTRYPOINT ["./start.sh"]