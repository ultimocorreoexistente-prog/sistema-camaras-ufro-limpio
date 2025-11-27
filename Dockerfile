# ==============================================
# DOCKERFILE HÍBRIDO PARA RAILWAY - SISTEMA CÁMARAS UFRO
# ✅ FUSIÓN OPTIMIZADA: start.sh robusto + directorios completos
# ==============================================

FROM python:3.11-slim
WORKDIR /app

# Instalar dependencias del sistema (incluye GCC para psycopg2-binary)
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos principales de la aplicación
COPY app.py .
COPY config.py .
COPY db_setup.py .
COPY start.sh .

# Copiar estructura completa de directorios
COPY models ./models
COPY routes ./routes
COPY templates ./templates
COPY static ./static
COPY services ./services
COPY utils ./utils

# Hacer ejecutable el script de inicio
RUN chmod +x start.sh && mkdir -p uploads logs instance

# Variables de entorno para Railway
ENV PORT=8000
ENV FLASK_ENV=production

# Exponer puerto
EXPOSE 8000

# Comando de inicio con script robusto (start.sh verifica config + BD antes de arrancar)
CMD ["./start.sh"]