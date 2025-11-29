"""
WSGI Configuration for Gunicorn
Production WSGI server configuration
"""

import os
import multiprocessing
import signal
import sys

# Configuración base
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1

# Configuración de workers
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeouts
timeout = 10
keepalive = 5
graceful_timeout = 10

# Configuración de seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configuración específica para Railway
if os.environ.get('RAILWAY_ENVIRONMENT'):
    # Railway - Entorno de producción
    workers = 2
    worker_class = "sync"
    timeout = 60
    max_requests = 500
    bind = "0.0.0.0:8000"

elif os.environ.get('HEROKU'):
    # Heroku - Entorno de producción
    workers = 2
    worker_class = "sync"
    timeout = 30
    max_requests = 200

# Variables de entorno
raw_env = [
    'FLASK_ENV=production',
    'FLASK_DEBUG=False'
]

# Configuración de memoria
preload_app = True
daemon = False
pidfile = "/tmp/gunicorn.pid"

# Señales
def when_ready(server):
    server.log.info("🚀 Servidor Gunicorn iniciado para Sistema Cámaras UFRO")

def worker_int(worker):
    worker.log.info("🔄 Worker interrumpido, cerrando conexiones...")

def pre_fork(server, worker):
    server.log.info(f"📋 Worker {worker.pid} iniciado")

def post_fork(server, worker):
    worker.log.info(f"✅ Worker {worker.pid} listo para recibir conexiones")

def pre_exec(server):
    server.log.info("🔄 Reiniciando servidor...")

def worker_abort(worker):
    worker.log.warning("⚠️ Worker abortado por timeout")

# Hooks para logging
def on_starting(server):
    server.log.info("🎬 Iniciando servidor Gunicorn para Sistema Cámaras UFRO")

def on_reload(server):
    server.log.info("🔄 Recargando configuración del servidor...")

def on_exit(server):
    server.log.info("👋 Apagando servidor Gunicorn")