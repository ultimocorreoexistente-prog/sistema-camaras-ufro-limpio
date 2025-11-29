#!/usr/bin/env python3
"""
Sistema de Cámaras de Seguridad UFRO - Versión Corregida Railway
===============================================================

Punto de entrada principal optimizado para Railway.
- Configuración unificada
- Health check endpoint
- Logging simplificado
- Compatibilidad total Railway

Autor: MiniMax Agent
Fecha: 2025-11-30
Versión: 4.0-railway-fixed
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify, render_template, send_from_directory
from flask_login import LoginManager, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import func, desc
import sys
import traceback

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicialización de la aplicación Flask
app = Flask(__name__)

# Importar configuración de manera segura
try:
    from config import get_config_safe
    config = get_config_safe()
    app.config.update(
        SECRET_KEY=config.SECRET_KEY,
        SQLALCHEMY_DATABASE_URI=config.SQLALCHEMY_DATABASE_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=config.UPLOAD_FOLDER,
        MAX_CONTENT_LENGTH=config.MAX_CONTENT_LENGTH
    )
    logger.info("✅ Configuración cargada correctamente desde config.py")
except Exception as e:
    logger.error(f"❌ Error cargando configuración: {e}")
    # Fallback de emergencia
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'emergency-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///emergency.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    logger.warning("⚠️ Usando configuración de emergencia")

# Inicialización de extensiones
try:
    from models import db, Usuario
    db.init_app(app)
    logger.info("✅ Modelos importados correctamente")
except Exception as e:
    logger.error(f"❌ Error importando modelos: {e}")
    sys.exit(1)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    """Cargar usuario para Flask-Login."""
    try:
        return Usuario.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Error cargando usuario {user_id}: {e}")
        return None

# Registrar blueprints
try:
    from routes import (
        auth_bp, dashboard_bp, camaras_bp, fallas_bp, 
        usuarios_bp, mantenimientos_bp, nvr_bp, switches_bp,
        ups_bp, fuentes_bp, gabinetes_bp, fotografias_bp,
        topologia_bp, geolocalizacion_bp
    )
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(camaras_bp)
    app.register_blueprint(fallas_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(mantenimientos_bp)
    app.register_blueprint(nvr_bp)
    app.register_blueprint(switches_bp)
    app.register_blueprint(ups_bp)
    app.register_blueprint(fuentes_bp)
    app.register_blueprint(gabinetes_bp)
    app.register_blueprint(fotografias_bp)
    app.register_blueprint(topologia_bp)
    app.register_blueprint(geolocalizacion_bp)
    
    logger.info("✅ Blueprints registrados correctamente")
except Exception as e:
    logger.error(f"❌ Error registrando blueprints: {e}")

# Context processors
@app.context_processor
def inject_user():
    """Injectar usuario actual en todos los templates."""
    return dict(current_user=current_user)

@app.context_processor
def inject_constants():
    """Injectar constantes del sistema."""
    return dict(
        ROLES=["ADMIN", "TECNICO", "LECTURA"],
        PRIORIDADES=["ALTA", "MEDIA", "BAJA"],
        ESTADOS_FALLA=["PENDIENTE", "EN_PROGRESO", "CERRADA"],
        ESTADOS_EQUIPO=["OPERATIVO", "FALLA_MENOR", "FUERA_DE_SERVICIO"]
    )

# Routes principales
@app.route('/')
def index():
    """Página principal."""
    if current_user.is_authenticated:
        return render_template('dashboard.html')
    return render_template('login.html')

@app.route('/health')
def health_check():
    """Health check para Railway."""
    try:
        # Verificar base de datos
        db_status = "OK" if db else "ERROR"
        
        # Verificar configuraciones críticas
        secret_key_status = "OK" if app.config.get('SECRET_KEY') else "ERROR"
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '4.0-railway-fixed',
            'database': db_status,
            'secret_key': secret_key_status,
            'debug_mode': app.config.get('DEBUG', False)
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    """Servir archivos estáticos."""
    return send_from_directory('static', filename)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# CLI commands
@app.cli.command('init-db')
def init_db():
    """Inicializar base de datos."""
    try:
        db.create_all()
        logger.info("✅ Base de datos inicializada")
        from scripts.datos_iniciales import crear_usuario_admin
        crear_usuario_admin()
        logger.info("✅ Usuario admin creado")
    except Exception as e:
        logger.error(f"❌ Error inicializando BD: {e}")

@app.cli.command('create-admin')
def create_admin():
    """Crear usuario administrador."""
    try:
        from scripts.datos_iniciales import crear_usuario_admin
        crear_usuario_admin()
        logger.info("✅ Usuario admin creado")
    except Exception as e:
        logger.error(f"❌ Error creando admin: {e}")

# Main
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    logger.info(f"🚀 Iniciando servidor en puerto {port}")
    logger.info(f"🔧 Modo debug: {debug_mode}")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
