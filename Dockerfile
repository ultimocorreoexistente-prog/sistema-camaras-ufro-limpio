FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copiar aplicación principal
COPY app.py .
COPY migrate_data.py .

# Copiar carpeta models/ completa (NO models.py)
COPY models ./models

# Crear directorios y copiar assets
RUN mkdir -p templates static uploads
COPY templates ./templates
COPY static ./static

ENV PORT=8000
ENV FLASK_ENV=production

EXPOSE 8000

CMD gunicorn app:app --workers 2 --timeout 30 --bind 0.0.0.0:$PORT