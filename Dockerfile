# ==============================================
# DOCKERFILE CORREGIDO PARA RAILWAY
# ✅ VERSIÓN SIMPLIFICADA Y FUNCIONAL
# ==============================================

FROM python:3.11-slim

# Configuración de trabajo
WORKDIR /app

# Instalar dependencias del sistema CRÍTICAS
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Actualizar pip y instalar wheel
RUN pip install --upgrade pip setuptools wheel

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias Python con versiones específicas
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Verificar instalaciones críticas
RUN python -c "import gunicorn; print(f'Gunicorn: {gunicorn.__version__}')" && \
    python -c "from dotenv import load_dotenv; print('python-dotenv: OK')"

# Copiar aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p uploads logs instance

# Configuración de entorno
ENV PORT=8000
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Exponer puerto
EXPOSE 8000

# Comando simple y directo
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT", "--workers", "2", "--timeout", "30"]
