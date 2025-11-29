#!/usr/bin/env python3
"""
Sistema de Cámaras de Seguridad UFRO - Versión 3 Híbrida
========================================================

Punto de entrada principal que combina funcionalidades avanzadas con compatibilidad Railway.
- Flask-Login para autenticación completa
- Blueprints modulares
- Health check endpoint
- Context processors globales
- Logging avanzado

Autor: MiniMax Agent
Fecha: 2025-11-27
Versión: 3.0-hybrid
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify, render_template, send_from_directory, request
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

# Configuración de la aplicación
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost/camaras_ufro')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialización de extensiones
from models import db, Usuario

# Inicializar SQLAlchemy
db.init_app(app)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth_bp.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    """Cargar usuario por ID para Flask-Login"""
    try:
        return Usuario.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Error cargando usuario {user_id}: {str(e)}")
        return None

# Registrar blueprints con manejo seguro de errores
def register_blueprints():
    """Registrar todos los blueprints de la aplicación"""
    blueprints = [
        ('auth', 'routes.auth', 'auth_bp'),
        ('dashboard', 'routes.dashboard', 'dashboard_bp'),
        ('api', 'routes.api', 'api_bp'),
        ('camaras', 'routes.camaras', 'camaras_bp'),
        ('fallas', 'routes.fallas', 'fallas_bp'),
        ('usuarios', 'routes.usuarios', 'usuarios_bp'),
        ('nvr', 'routes.nvr', 'nvr_bp'),
        ('switches', 'routes.switches', 'switches_bp'),
        ('fuentes', 'routes.fuentes', 'fuentes_bp'),
        ('ups', 'routes.ups', 'ups_bp'),
        ('gabinetes', 'routes.gabinetes', 'gabinetes_bp'),
        ('fotografias', 'routes.fotografias', 'fotografias_bp'),
        ('topologia', 'routes.topologia', 'topologia_bp'),
        ('trazabilidad', 'routes.trazabilidad', 'trazabilidad_bp'),
        ('inventario', 'routes.inventario', 'inventario_bp'),
        ('geolocalizacion', 'routes.geolocalizacion', 'geolocalizacion_bp'),
        ('mantenimientos', 'routes.mantenimientos', 'mantenimientos_bp')
    ]
    
    for name, module_name, blueprint_name in blueprints:
        try:
            module = __import__(module_name, fromlist=[blueprint_name])
            blueprint = getattr(module, blueprint_name)
            app.register_blueprint(blueprint)
            logger.info(f"✅ Blueprint {name} registrado exitosamente")
        except ImportError as e:
            logger.warning(f"⚠️  No se pudo cargar blueprint {name}: {str(e)}")
        except AttributeError as e:
            logger.warning(f"⚠️  Blueprint {blueprint_name} no encontrado en {module_name}: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Error registrando blueprint {name}: {str(e)}")

# Context processors globales
@app.context_processor
def inject_user_and_stats():
    """Inyectar usuario actual y estadísticas en todos los templates"""
    try:
        from models import Camara, Falla, Usuario, Mantenimiento
        
        stats = {
            'total_camaras': Camara.query.count(),
            'fallas_abiertas': Falla.query.filter_by(estado='abierta').count(),
            'usuarios_activos': Usuario.query.filter_by(activo=True).count(),
            'mantenimientos_pendientes': Mantenimiento.query.filter_by(
                estado='pendiente'
            ).count()
        }
        
        return {
            'current_user': current_user,
            'now': datetime.now(),
            'stats': stats
        }
    except Exception as e:
        logger.error(f"Error en context processor: {str(e)}")
        return {
            'current_user': current_user,
            'now': datetime.now(),
            'stats': {}
        }

# Rutas especiales
@app.route('/health')
def health_check():
    """Health check endpoint para Railway y monitoreo"""
    try:
        # Verificar conexión a base de datos
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'version': '3.0-hybrid',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected'
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'version': '3.0-hybrid',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

@app.route('/favicon.ico')
def favicon():
    """Servir favicon para evitar errores 404"""
    return send_from_directory(os.path.join(app.root_path, 'static'),
                              'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
@login_required
def index():
    """Página principal - redirigir al dashboard"""
    from flask import redirect, url_for
    return redirect(url_for('dashboard_bp.index'))

# Manejo de errores
@app.errorhandler(404)
def not_found_error(error):
    """Manejar errores 404"""
    logger.warning(f"404 Error: {request.url}")
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejar errores 500"""
    logger.error(f"500 Error: {str(error)}")
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Decorators personalizados
def admin_required(f):
    """Decorator para rutas que requieren permisos de administrador"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        if not current_user.is_admin():
            logger.warning(f"Usuario {current_user.email} intentó acceder a ruta admin sin permisos")
            from flask import flash, redirect, url_for
            flash('No tienes permisos para acceder a esta página.', 'danger')
            return redirect(url_for('dashboard_bp.index'))
        return f(*args, **kwargs)
    return decorated_function

# Función de inicialización
def init_app():
    """Inicializar la aplicación y crear tablas"""
    with app.app_context():
        try:
            # Crear todas las tablas
            db.create_all()
            logger.info("✅ Base de datos inicializada correctamente")
            
            # Seed data si es necesario
            from models import seed_initial_data
            seed_initial_data()
            logger.info("✅ Datos iniciales insertados")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando aplicación: {str(e)}")
            traceback.print_exc()
            raise

# Función principal
if __name__ == '__main__':
    # Configuración para Railway
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Iniciando Sistema Cámaras UFRO v3.0-hybrid en puerto {port}")
    logger.info(f"🔧 Debug mode: {debug_mode}")
    
    # Registrar blueprints
    register_blueprints()
    
    # Inicializar aplicación
    init_app()
    
    # Ejecutar servidor
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )