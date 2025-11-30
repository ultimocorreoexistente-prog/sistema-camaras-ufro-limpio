<<<<<<< HEAD
"""
Sistema Completo de Gestión de Cámaras UFRO
Flask Application with Blueprint Architecture
467 cámaras + casos reales
"""

import os
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, current_app
=======
from flask import Flask, render_template, request, jsonify
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
<<<<<<< HEAD
import logging
=======
from models import db, Usuario, Camara, Ubicacion
from routes.inventario import inventario_bp
from routes.trazabilidad import trazabilidad_bp
from config import get_config
import os
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4

app_config = get_config()
app = Flask(__name__)
<<<<<<< HEAD

# Configuración de la aplicación
def configure_app(app):
    """Configurar la aplicación Flask"""
    # Configuración básica
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sistema-camaras-ufro-04-secreto')
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
    
    # Configuración de logging
    if not app.debug:
        app.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(handler)

# Configurar la aplicación
configure_app(app)

# Inicializar extensiones
try:
    from models import db
    db.init_app(app)
    
    # Importar todos los modelos para asegurar que estén registrados
    from models import (
        Usuario, Camara, Nvr, Switch, Ups, Fuente, Gabinete, 
        Falla, FallaComentario, BaseModel
    )
    
    print("✅ Models imported successfully")
    
except ImportError as e:
    print(f"❌ Error importing models: {e}")
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app)

# CORS configuration
CORS(app, 
     origins=["*"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"])
=======
app.config.from_object(app_config)
db.init_app(app)
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    try:
        from models import Usuario
        return Usuario.query.get(int(user_id))
    except Exception as e:
        app.logger.error(f"Error loading user {user_id}: {e}")
        return None

# Registrar blueprints
def register_blueprints(app):
    """Registrar todos los blueprints en la aplicación"""
    try:
        from routes import register_blueprints as register_bp
        register_bp(app)
        print("✅ Blueprints registered successfully")
    except Exception as e:
        print(f"❌ Error registering blueprints: {e}")
        raise

register_blueprints(app)

# Configurar contexto de la aplicación
@app.before_first_request
def initialize_database():
    """Inicializar base de datos al primer request"""
    try:
        with app.app_context():
            # Crear todas las tablas si no existen
            from models import db
            db.create_all()
            
            # Crear usuario administrador por defecto si no existe
            from models import Usuario
            admin_user = Usuario.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = Usuario(
                    username='admin',
                    email='admin@ufro.cl',
                    full_name='Administrador Sistema',
                    role='admin'
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Default admin user created (admin/admin123)")
                
    except Exception as e:
        app.logger.error(f"Database initialization error: {e}")

@app.route('/')
<<<<<<< HEAD
def index():
    """Página de inicio - redirige según autenticación"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.login'))

# Endpoints de API y diagnóstico
@app.route('/api/stats')
@login_required
def api_stats():
    """Endpoint de estadísticas para el dashboard"""
    try:
        from models import Camara, Falla, Ups, Switch, Nvr, Gabinete, Fuente
        
        # Estadísticas básicas
        stats = {
            'camaras_total': Camara.query.filter_by(activo=True).count(),
            'camaras_activas': Camara.query.filter_by(estado='activa', activo=True).count(),
            'fallas_abiertas': Falla.query.filter(Falla.estado.in_(['abierta', 'en_proceso']), Falla.activo==True).count(),
            'mantenimientos_pendientes': 0,  # Por implementar
            'gabinetes_total': Gabinete.query.filter_by(activo=True).count(),
            'ups_total': Ups.query.filter_by(activo=True).count(),
            'switches_total': Switch.query.filter_by(activo=True).count(),
            'nvr_total': Nvr.query.filter_by(activo=True).count(),
            'fuentes_total': Fuente.query.filter_by(activo=True).count(),
            'timestamp': datetime.utcnow().isoformat()
        }
        return jsonify(stats)
    except Exception as e:
        current_app.logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Endpoint de health check para monitoreo"""
    try:
        # Verificar conexión a base de datos
        with app.app_context():
            db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0.0',
            'environment': os.environ.get('FLASK_ENV', 'production')
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/api/status')
def system_status():
    """Endpoint de estado completo del sistema"""
    try:
        # Verificar base de datos
        db_status = 'ok'
        db_error = None
        try:
            with app.app_context():
                db.session.execute('SELECT 1')
        except Exception as e:
            db_status = 'error'
            db_error = str(e)

        # Contar registros por tabla
        with app.app_context():
            from models import Camara, Falla, Usuario
            stats = {
                'usuarios': Usuario.query.filter_by(activo=True).count(),
                'camaras': Camara.query.filter_by(activo=True).count(),
                'fallas': Falla.query.filter_by(activo=True).count()
            }

        return jsonify({
            'status': 'ok' if db_status == 'ok' else 'degraded',
            'timestamp': datetime.utcnow().isoformat(),
            'database': {
                'status': db_status,
                'error': db_error
            },
            'stats': stats,
            'environment': os.environ.get('FLASK_ENV', 'production')
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Manejo de errores HTTP
@app.errorhandler(404)
def not_found(error):
    """Manejo de errores 404"""
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Endpoint not found',
            'status': 404,
            'path': request.path
        }), 404
    
    try:
        return render_template('errors/404.html'), 404
    except:
        return jsonify({'error': 'Page not found', 'status': 404}), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores 500"""
    try:
        db.session.rollback()
    except:
        pass
    
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Internal server error',
            'status': 500,
            'message': 'An unexpected error occurred'
        }), 500
    
    try:
        return render_template('errors/500.html'), 500
    except:
        return jsonify({'error': 'Internal server error', 'status': 500}), 500
=======
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not email or not password:
            return render_template('login.html', error='Email y contraseña son requeridos')
        
        user = Usuario.query.filter_by(email=email).first()
        if user and user.activo and check_password_hash(user.password_hash, password):
            login_user(user)
            user.ultimo_acceso = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Credenciales inválidas')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'total_camaras': Camara.query.count(),
        'camaras_por_estado': db.session.query(Camara.estado, db.func.count()).group_by(Camara.estado).all(),
        'total_usuarios': Usuario.query.filter_by(activo=True).count(),
    }
    return render_template('dashboard.html', stats=stats, user=current_user)

@app.route('/camaras')
@login_required
def listar_camaras():
    camaras = Camara.query.all()
    return render_template('camaras.html', camaras=camaras, user=current_user)

# Blueprints
app.register_blueprint(inventario_bp, url_prefix='/api/inventario')
app.register_blueprint(trazabilidad_bp, url_prefix='/api/trazabilidad')
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4

@app.errorhandler(403)
def forbidden(error):
    """Manejo de errores 403"""
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Forbidden',
            'status': 403,
            'message': 'You do not have permission to access this resource'
        }), 403
    
    try:
        return render_template('errors/403.html'), 403
    except:
        return jsonify({'error': 'Forbidden', 'status': 403}), 403

# Manejo de errores de validación
@app.errorhandler(400)
def bad_request(error):
    """Manejo de errores 400"""
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Bad request',
            'status': 400,
            'message': 'The request could not be understood'
        }), 400
    return jsonify({'error': 'Bad request', 'status': 400}), 400

# Contexto de aplicación
@app.context_processor
def inject_user():
    """Inyectar usuario actual en todos los templates"""
    return dict(current_user=current_user)

# Hooks de aplicación
@app.before_request
def before_request():
    """Ejecutar antes de cada request"""
    # Log de requests en desarrollo
    if app.debug:
        print(f"{request.method} {request.path}")

@app.after_request
def after_request(response):
    """Ejecutar después de cada request"""
    # Headers de seguridad
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    if not app.debug:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response

# Ejecutar aplicación
if __name__ == '__main__':
<<<<<<< HEAD
    port = int(os.environ.get('PORT', 8000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🚀 Starting UFRO Camera Management System on port {port}")
    print(f"📊 Debug mode: {debug_mode}")
    print(f"🗄️ Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    try:
        with app.app_context():
            # Verificar conexión a base de datos
            db.session.execute('SELECT 1')
            print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=debug_mode,
        threaded=True
    )
=======
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
