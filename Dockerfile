FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY models.py .
COPY migrate_data.py .

# Crear directorios
RUN mkdir -p templates static

# Copiar archivos (sin condicionales)
COPY templates ./templates
COPY static ./static

ENV PORT=8000
ENV FLASK_ENV=production

EXPOSE 8000

CMD gunicorn app:app --workers 2 --timeout 30 --bind 0.0.0.0:$PORT