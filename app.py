import os
import logging
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importamos la función de configuración MEJORADA
from config import get_config

# ========================================
# 🔧 INICIALIZACIÓN DE EXTENSIONES
# ========================================

db = SQLAlchemy()
login_manager = LoginManager()

# ========================================
# 📊 DEFINICIÓN DE MODELOS SQLAlchemy
# ========================================

class Usuario(db.Model, UserMixin):
    """🎯 Modelo de usuario para autenticación y gestión."""
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    full_name = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(20), default='LECTURA')  # ADMIN, TECNICO, LECTURA
    password_hash = db.Column(db.String(256), nullable=False)
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """🔐 Genera el hash de la contraseña."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """✅ Verifica la contraseña contra el hash almacenado."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Usuario {self.username}>'

class Ubicacion(db.Model):
    """📍 Modelo para representar la ubicación física de los equipos."""
    __tablename__ = 'ubicaciones'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    latitud = db.Column(db.String(255))  # Columna añadida en db_setup.py
    longitud = db.Column(db.String(255))  # Columna añadida en db_setup.py
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔗 Relaciones uno a muchos con equipos
    camaras = db.relationship('Camara', backref='ubicacion_obj', lazy=True)
    switches = db.relationship('Switch', backref='ubicacion_obj', lazy=True)
    nvrs = db.relationship('NvrDvr', backref='ubicacion_obj', lazy=True)
    gabinetes = db.relationship('Gabinete', backref='ubicacion_obj', lazy=True)
    ups = db.relationship('Ups', backref='ubicacion_obj', lazy=True)

class Camara(db.Model):
    """📹 Modelo para representar una cámara de seguridad."""
    __tablename__ = 'camaras'
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.String(100), unique=True, nullable=False)
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    ip = db.Column(db.String(15), unique=True)
    estado = db.Column(db.String(50), default='inactiva')  # Columna añadida en db_setup.py
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Switch(db.Model):
    """🔌 Modelo para switches de red."""
    __tablename__ = 'switches'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(50))
    ip = db.Column(db.String(15), unique=True)
    puertos = db.Column(db.Integer, default=24)
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class NvrDvr(db.Model):
    """📺 Modelo para NVR/DVR."""
    __tablename__ = 'nvr_dvr'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), default='NVR')  # NVR o DVR
    modelo = db.Column(db.String(50))
    ip = db.Column(db.String(15), unique=True)
    canales = db.Column(db.Integer, default=16)
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Gabinete(db.Model):
    """🏠 Modelo para gabinetes de equipos."""
    __tablename__ = 'gabinetes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(50))
    tipo = db.Column(db.String(30), default='Pared')  # Pared, Piso, Rack
    capacidad_u = db.Column(db.Integer, default=12)  # Unidades de rack
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Ups(db.Model):
    """🔋 Modelo para sistemas UPS."""
    __tablename__ = 'ups'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(50))
    capacidad_va = db.Column(db.Integer)  # Voltamperes
    autonomia_minutos = db.Column(db.Integer)
    estado_bateria = db.Column(db.String(30), default='buena')  # buena, regular, mala
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ========================================
# 🔐 CONFIGURACIÓN FLASK-LOGIN
# ========================================

@login_manager.user_loader
def load_user(user_id):
    """🔍 Función requerida por Flask-Login para recargar al usuario."""
    try:
        return Usuario.query.get(int(user_id))
    except (ValueError, TypeError):
        return None

# ========================================
# 🏭 FACTORY DE APLICACIÓN FLASK
# ========================================

def create_app():
    """🏗️ Patrón de Fábrica de Aplicaciones para inicializar Flask."""
    
    app = Flask(__name__)
    
    try:
        # 1. 🎯 CARGAR CONFIGURACIÓN
        app_config = get_config()
        app.config.from_object(app_config)

        logger.info(f"🚀 App iniciada con SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI'][:30]}...")
        logger.info(f"🔑 SECRET_KEY configurada: {bool(app.config['SECRET_KEY'])}")
        
        # 2. 🔧 INICIALIZAR EXTENSIONES
        db.init_app(app)
        login_manager.init_app(app)
        
        # Configurar Flask-Login
        login_manager.login_view = 'login'
        login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."
        login_manager.login_message_category = "info"
        login_manager.session_protection = "strong"

        # 3. 📋 CREAR TABLAS SI NO EXISTEN
        with app.app_context():
            logger.info("🏗️ Verificando tablas de base de datos...")
            db.create_all()
            logger.info("✅ Tablas verificadas/creadas exitosamente")
            
            # Crear usuario admin si no existe
            try:
                if not Usuario.query.filter_by(username='admin').first():
                    admin = Usuario(
                        username='admin',
                        email='admin.sistema@ufrontera.cl',
                        full_name='Administrador Sistema UFRO',
                        role='ADMIN'
                    )
                    admin.set_password('admin123')
                    db.session.add(admin)
                    db.session.commit()
                    logger.info("🎉 Usuario admin creado: admin / admin123")
                else:
                    logger.info("ℹ️ Usuario admin ya existe")
            except Exception as e:
                logger.warning(f"⚠️ Error al verificar/crear usuario admin: {e}")

        # 4. 🛣️ DEFINIR RUTAS
        register_routes(app)
        
        # 5. 📝 MANEJADORES DE ERROR
        register_error_handlers(app)

        logger.info("🎉 Aplicación Flask inicializada correctamente")
        return app
        
    except Exception as e:
        logger.error(f"❌ Error crítico al inicializar aplicación: {e}")
        raise

def register_routes(app):
    """🛣️ Registrar todas las rutas de la aplicación."""
    
    @app.route('/')
    def index():
        """🏠 Ruta de inicio - Dashboard principal."""
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        # 📊 Obtener estadísticas del dashboard
        try:
            stats = {
                'total_camaras': Camara.query.count(),
                'camaras_activas': Camara.query.filter_by(activo=True).count(),
                'total_ubicaciones': Ubicacion.query.count(),
                'ubicaciones_activas': Ubicacion.query.filter_by(activo=True).count(),
                'total_switches': Switch.query.count(),
                'total_nvr_dvr': NvrDvr.query.count(),
                'total_gabinetes': Gabinete.query.count(),
                'total_ups': Ups.query.count(),
                'usuarios_activos': Usuario.query.filter_by(activo=True).count()
            }
            
            logger.debug(f"📊 Estadísticas obtenidas: {stats}")
            
        except Exception as e:
            logger.error(f"❌ Error al obtener estadísticas: {e}")
            flash("Error al cargar estadísticas del dashboard.", "warning")
            stats = {key: 0 for key in ['total_camaras', 'camaras_activas', 'total_ubicaciones', 'ubicaciones_activas', 'total_switches', 'total_nvr_dvr', 'total_gabinetes', 'total_ups', 'usuarios_activos']}

        return render_template('index.html', 
                                stats=stats,
                                user=current_user)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """🔑 Maneja el inicio de sesión."""
        if current_user.is_authenticated:
            logger.info(f"👤 Usuario {current_user.username} ya autenticado, redirigiendo a dashboard")
            return redirect(url_for('index'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not username or not password:
                flash('Por favor ingresa usuario y contraseña.', 'warning')
                return render_template('login.html', title='Iniciar Sesión')
            
            try:
                user = Usuario.query.filter_by(username=username).first()

                if user and user.check_password(password):
                    if not user.activo:
                        flash('Tu cuenta está desactivada. Contacta al administrador.', 'danger')
                        return render_template('login.html', title='Iniciar Sesión')
                    
                    login_user(user, remember=True)
                    logger.info(f"✅ Login exitoso para usuario: {user.username}")
                    
                    next_page = request.args.get('next')
                    flash(f'¡Bienvenido, {user.username}!', 'success')
                    return redirect(next_page or url_for('index'))
                else:
                    logger.warning(f"❌ Intento de login fallido para usuario: {username}")
                    flash('Credenciales inválidas. Por favor, verifica tu usuario y contraseña.', 'danger')
            
            except Exception as e:
                logger.error(f"❌ Error durante login: {e}")
                flash('Error interno del servidor. Intenta nuevamente.', 'danger')

        return render_template('login.html', title='Iniciar Sesión')

    @app.route('/logout')
    @login_required
    def logout():
        """🚪 Cierra la sesión del usuario."""
        username = current_user.username
        logout_user()
        logger.info(f"🚪 Logout exitoso para usuario: {username}")
        flash('Has cerrado sesión exitosamente.', 'info')
        return redirect(url_for('login'))

    @app.route('/test-db-connection')
    def test_db():
        """🧪 Ruta para probar la conexión a la base de datos."""
        try:
            # Prueba simple: contar registros
            stats = {
                'usuarios': Usuario.query.count(),
                'ubicaciones': Ubicacion.query.count(),
                'camaras': Camara.query.count(),
                'switches': Switch.query.count(),
                'nvr_dvr': NvrDvr.query.count(),
                'gabinetes': Gabinete.query.count(),
                'ups': Ups.query.count()
            }
            
            logger.info(f"🧪 Test DB exitoso: {stats}")
            return {
                'status': 'success',
                'message': 'Conexión a base de datos exitosa',
                'stats': stats
            }, 200
            
        except Exception as e:
            logger.error(f"❌ Fallo en test de conexión DB: {e}")
            return {
                'status': 'error',
                'message': f'Error de conexión: {str(e)}'
            }, 500

    @app.route('/health')
    def health():
        """❤️ Ruta de health check para Railway."""
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}

def register_error_handlers(app):
    """📝 Registrar manejadores de errores."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """🔍 Manejador para páginas no encontradas."""
        logger.warning(f"🔍 404 - Página no encontrada: {request.path}")
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """⚠️ Manejador para errores internos."""
        logger.error(f"💥 500 - Error interno: {error}")
        db.session.rollback()
        return render_template('500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        """🚫 Manejador para acceso denegado."""
        logger.warning(f"🚫 403 - Acceso denegado: {request.path}")
        return render_template('403.html'), 403

# ========================================
# 🚀 INSTANCIA PARA GUNICORN
# ========================================

# ✅ CORRECCIÓN CRÍTICA: Crear instancia de app para Gunicorn
# Esto es lo que Gunicorn necesita para ejecutar app:app
try:
    app = create_app()
    logger.info("✅ Instancia de app creada para Gunicorn")
except Exception as e:
    logger.error(f"❌ Error al crear instancia de app: {e}")
    # Crear app básica como fallback
    app = Flask(__name__)
    logger.warning("⚠️ Usando app básica como fallback")

# ========================================
# 🚀 PUNTO DE ENTRADA PRINCIPAL
# ========================================

if __name__ == '__main__':
    try:
        logger.info("🚀 Iniciando aplicación Sistema de Cámaras UFRO...")
        
        # Crear aplicación
        app = create_app()
        
        # Información de inicio
        port = int(os.getenv('PORT', 5000))
        logger.info(f"🌐 Servidor iniciando en puerto {port}")
        logger.info(f"🔗 URL: http://localhost:{port}")
        logger.info(f"🔑 Login inicial: admin / admin123")
        
        # Ejecutar en modo desarrollo o según configuración
        debug_mode = app.config.get('DEBUG', False)
        logger.info(f"🛠️ Modo debug: {debug_mode}")
        
        # Ejecutar aplicación
        app.run(
            host='0.0.0.0', 
            port=port, 
            debug=debug_mode,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("👋 Aplicación interrumpida por el usuario")
    except Exception as e:
        logger.error(f"💥 Error fatal al ejecutar aplicación: {e}")
        raise