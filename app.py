# Deploy forzado 2025-11-14
"""
Sistema de Gestión de Cámaras UFRO - Aplicación Principal
Versión para Railway con PostgreSQL
467 cámaras + casos reales
"""

import os
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from datetime import datetime
import json

# Crear aplicación Flask
app = Flask(__name__)

# Configuración
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sistema-camaras-ufro-2024-secreto')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://localhost/camaras_ufro')

# Compatibilidad con Railway PostgreSQL
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 20,
    'pool_recycle': 300,
    'pool_pre_ping': True,
    'max_overflow': 30
}
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Inicializar extensiones
try:
    from models import db, Usuario, Camara, Falla, Mantenimiento, NVR, Switch, UPS, Gabinete, FuentePoder, Fotografia, Ubicacion
    db.init_app(app)
except ImportError as e:
    print(f"Error importing models: {e}")
    # Crear una instancia básica si los modelos no están disponibles
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app)

CORS(app)

# Configurar Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    try:
        if 'Usuario' in locals():
            return Usuario.query.get(int(user_id))
        return None
    except:
        return None


# ================================
# RUTAS BÁSICAS
# ================================

@app.route('/')
def index():
    """Página principal"""
    return jsonify({
        'status': 'ok',
        'message': 'Sistema de Gestión de Cámaras UFRO - Online',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta de login"""
    if request.method == 'POST':
        return jsonify({'message': 'Login endpoint - POST received'}), 200
    return jsonify({'message': 'Login endpoint - GET request'}), 200


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal"""
    return jsonify({'message': 'Dashboard endpoint'}), 200


# ================================
# ENDPOINTS DE DIAGNÓSTICO Y MANTENIMIENTO
# ================================

@app.route('/health')
def health_check():
    """Endpoint de health check para monitoreo"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'environment': os.environ.get('FLASK_ENV', 'production')
    })


@app.route('/status')
def system_status():
    """Endpoint de estado del sistema"""
    try:
        # Verificar base de datos
        db_status = 'ok'
        db_error = None
        try:
            if 'db' in locals():
                db.session.execute('SELECT 1')
            else:
                db_status = 'not_configured'
        except Exception as e:
            db_status = 'error'
            db_error = str(e)

        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'database': db_status,
            'database_error': db_error,
            'environment': os.environ.get('FLASK_ENV', 'production')
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


# ================================
# ERROR HANDLERS
# ================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ================================
# RUTAS DE CÁMARAS BÁSICAS
# ================================

@app.route('/camaras')
def listar_camaras():
    """Listar cámaras"""
    return jsonify({'message': 'Listar cámaras endpoint'}), 200


@app.route('/camaras/<int:camera_id>')
def detalle_camara(camera_id):
    """Detalle de una cámara"""
    return jsonify({'message': f'Detalle cámara {camera_id}'}), 200


# Rutas para fallas
@app.route('/fallas')
def listar_fallas():
    """Listar fallas"""
    return jsonify({'message': 'Listar fallas endpoint'}), 200


# Rutas para mantenimiento
@app.route('/mantenimiento')
def listar_mantenimiento():
    """Listar mantenimiento"""
    return jsonify({'message': 'Listar mantenimiento endpoint'}), 200


# ================================
# INICIALIZACIÓN
# ================================

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
