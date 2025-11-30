"""
Sistema Completo de Gestión de Cámaras UFRO
Flask Application with Blueprint Architecture
467 cámaras + casos reales
CORRECCIÓN: Conflictos de merge resueltos
"""

import os
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importaciones locales
from models import db, Usuario, Camara, Ubicacion, Equipo
from routes.inventario import inventario_bp
from routes.trazabilidad import trazabilidad_bp
from config import get_config
from routes.usuarios import usuarios_bp
from routes.dashboard import dashboard_bp
from routes.camaras import camaras_bp
from routes.fallas import fallas_bp
from routes.mantenimientos import mantenimientos_bp
from routes.fotografias import fotografias_bp
from routes.geolocalizacion import geolocalizacion_bp
from routes.topologia import topologia_bp
from routes.fuentes import fuentes_bp
from routes.gabinetes import gabinetes_bp
from routes.nvr import nvr_bp
from routes.switches import switches_bp
from routes.ups import ups_bp
from routes.api import api_bp

# Inicializar configuración
app_config = get_config()
app = Flask(__name__)

def configure_app(app):
    """Configurar la aplicación Flask"""
    # Configuración básica
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sistema-camaras-ufro-04-secreto')
    
    # Configuración de base de datos para Railway
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        # Fallback para desarrollo local
        database_url = 'sqlite:///sistema_camaras.db'
    
    # Compatibilidad con Railway PostgreSQL
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuración de engine para Railway
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'max_overflow': 20
    }
    
    # Configuración de uploads
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    
    # Configuración de login
    app.config['SESSION_COOKIE_SECURE'] = False  # True para HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['REMEMBER_COOKIE_DURATION'] = datetime.timedelta(hours=4)

# Configurar la aplicación
configure_app(app)

# Inicializar SQLAlchemy
db.init_app(app)

# Configurar Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Registrar blueprints
try:
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(camaras_bp, url_prefix='/camaras')
    app.register_blueprint(fallas_bp, url_prefix='/fallas')
    app.register_blueprint(mantenimientos_bp, url_prefix='/mantenimientos')
    app.register_blueprint(fotografias_bp, url_prefix='/fotografias')
    app.register_blueprint(geolocalizacion_bp, url_prefix='/geolocalizacion')
    app.register_blueprint(topologia_bp, url_prefix='/topologia')
    app.register_blueprint(fuentes_bp, url_prefix='/fuentes')
    app.register_blueprint(gabinetes_bp, url_prefix='/gabinetes')
    app.register_blueprint(nvr_bp, url_prefix='/nvr')
    app.register_blueprint(switches_bp, url_prefix='/switches')
    app.register_blueprint(ups_bp, url_prefix='/ups')
    app.register_blueprint(inventario_bp, url_prefix='/inventario')
    app.register_blueprint(trazabilidad_bp, url_prefix='/trazabilidad')
    app.register_blueprint(api_bp, url_prefix='/api')
    logger.info("✅ Todos los blueprints registrados exitosamente")
except Exception as e:
    logger.error(f"❌ Error registrando blueprints: {e}")

# Ruta principal
@app.route('/')
def index():
    """Página de inicio"""
    return render_template('index.html')

# Rutas de autenticación básicas
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta de login simple para desarrollo"""
    if request.method == 'POST':
        # Login simple para desarrollo
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Superadmin de desarrollo
        if email == 'admin@ufro.cl' and password == 'admin123':
            user = Usuario.query.filter_by(email=email).first()
            if not user:
                # Crear usuario si no existe
                user = Usuario(
                    email=email,
                    nombre='Administrador',
                    rol='ADMIN',
                    activo=True
                )
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                logger.info(f"✅ Usuario superadmin creado: {email}")
            
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))
        
        flash('Credenciales inválidas', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    return redirect(url_for('login'))

# Ruta de prueba de base de datos
@app.route('/test-db')
def test_database():
    """Probar conexión a base de datos"""
    try:
        # Test básico de conexión
        total_camaras = Camara.query.count()
        total_usuarios = Usuario.query.count()
        
        return jsonify({
            'status': 'success',
            'message': 'Base de datos funcionando',
            'stats': {
                'camaras': total_camaras,
                'usuarios': total_usuarios
            }
        })
    except Exception as e:
        logger.error(f"❌ Error de base de datos: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error de base de datos: {str(e)}'
        }), 500

# Manejo de errores
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, error_message='Página no encontrada'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error_code=500, error_message='Error interno del servidor'), 500

# Inicialización de la base de datos
def init_db():
    """Inicializar base de datos con datos de ejemplo"""
    try:
        with app.app_context():
            # Crear todas las tablas
            db.create_all()
            
            # Crear usuario superadmin si no existe
            admin_user = Usuario.query.filter_by(email='admin@ufro.cl').first()
            if not admin_user:
                admin_user = Usuario(
                    email='admin@ufro.cl',
                    nombre='Administrador UFRO',
                    rol='ADMIN',
                    activo=True
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                
                # Insertar datos de ejemplo
                ubicacion = Ubicacion(
                    nombre='Campus UFRO Temuco',
                    descripcion='Campus principal Universidad de La Frontera',
                    activo=True
                )
                db.session.add(ubicacion)
                
                # Cámara de ejemplo
                camara_ejemplo = Camara(
                    nombre='Cámara Entrance Principal',
                    ip='192.168.1.100',
                    ubicacion=ubicacion,
                    estado='operativa',
                    activo=True
                )
                db.session.add(camara_ejemplo)
                
                db.session.commit()
                logger.info("✅ Base de datos inicializada con datos de ejemplo")
            
    except Exception as e:
        logger.error(f"❌ Error inicializando base de datos: {e}")
        db.session.rollback()

# Script de inicialización para Railway
def setup_for_railway():
    """Configuración específica para Railway"""
    try:
        logger.info("🚀 Configurando para Railway...")
        
        # Crear carpetas necesarias
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Inicializar base de datos
        init_db()
        
        logger.info("✅ Configuración de Railway completada")
        
    except Exception as e:
        logger.error(f"❌ Error en configuración de Railway: {e}")

# Hook de inicialización para Railway
if __name__ == '__main__':
    setup_for_railway()
    
    # Configuración del puerto para Railway
    port = int(os.environ.get('PORT', 5000))
    
    # Iniciar aplicación
    logger.info(f"🚀 Iniciando Sistema de Cámaras UFRO en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
