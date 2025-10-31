# Dockerfile Corregido para Sistema Cámaras UFRO
# Corrección: Copia archivos correctos y instala dependencias

FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ CORRECCIÓN CRÍTICA: Copiar archivos correctos de la aplicación
COPY app.py .
COPY models.py .
COPY migrate_data.py .

# ✅ Copiar templates y static files (si existen)
COPY templates ./templates 2>/dev/null || echo "Templates directory not found"
COPY static ./static 2>/dev/null || echo "Static directory not found"

# Variables de entorno
ENV PORT=8000
ENV FLASK_ENV=production

# Exponer puerto
EXPOSE 8000

# ✅ Comando correcto para producción con gunicorn
CMD ["gunicorn", "app:app", "--workers", "2", "--timeout", "30", "--bind", "0.0.0.0:8000"]