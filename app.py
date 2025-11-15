"""
Sistema Completo de Gestión de Cámaras UFRO
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

# Inicializar extensiones
try:
    from models import db, Usuario, Camara, Falla, Mantenimiento, NVR, Switch, UPS, Gabinete, FuentePoder, Fotografia, Ubicacion
    db.init_app(app)
except ImportError as e:
    print(f"Error importing models: {e}")
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app)

CORS(app)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    try:
        return Usuario.query.get(int(user_id))
    except:
        return None

# Rutas principales
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            user = Usuario.query.filter_by(username=username).first()
            
            if user and user.check_password(password) and user.activo:
                login_user(user)
                if hasattr(user, 'ultimo_acceso'):
                    user.ultimo_acceso = datetime.utcnow()
                    try:
                        db.session.commit()
                    except:
                        pass  # No hacer commit si falla, pero continuar con el login
                return redirect(url_for('dashboard'))
            
            flash('Usuario o contraseña incorrectos', 'error')
        except Exception as e:
            flash(f'Error en autenticación: {str(e)}', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Estadísticas
        total_camaras = Camara.query.filter_by(activo=True).count()
        camaras_activas = Camara.query.filter_by(estado='activa', activo=True).count()
        camaras_recientes = Camara.query.order_by(Camara.fecha_creacion.desc()).limit(5).all()

        fallas_abiertas = Falla.query.filter(Falla.estado.in_(['abierta', 'en_proceso'])).count()
        fallas_recientes = Falla.query.order_by(Falla.fecha_reporte.desc()).limit(5).all()

        mantenimientos_pendientes = Mantenimiento.query.filter_by(estado='programado').count()

        return render_template('dashboard.html',
                             total_camaras=total_camaras,
                             camaras_activas=camaras_activas,
                             fallas_abiertas=fallas_abiertas,
                             mantenimientos_pendientes=mantenimientos_pendientes,
                             camaras_recientes=camaras_recientes,
                             fallas_recientes=fallas_recientes)
    except Exception as e:
        flash(f'Error cargando dashboard: {str(e)}', 'error')
        return render_template('dashboard.html',
                             total_camaras=0,
                             camaras_activas=0,
                             fallas_abiertas=0,
                             mantenimientos_pendientes=0,
                             camaras_recientes=[],
                             fallas_recientes=[])

@app.route('/camaras')
@login_required
def camaras():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20

        camaras = Camara.query.filter_by(activo=True).order_by(Camara.nombre).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return render_template('camaras/list.html', camaras=camaras)
    except Exception as e:
        return f"Error en cámaras: {str(e)}"

@app.route('/fallas')
@login_required
def fallas():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20

        fallas = Falla.query.order_by(Falla.fecha_reporte.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return render_template('fallas/list.html', fallas=fallas)
    except Exception as e:
        return f"Error en fallas: {str(e)}"

@app.route('/mantenimientos')
@login_required
def mantenimientos():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20

        mantenimientos = Mantenimiento.query.order_by(Mantenimiento.fecha_programada.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return render_template('mantenimientos/list.html', mantenimientos=mantenimientos)
    except Exception as e:
        return f"Error en mantenimientos: {str(e)}"

@app.route('/equipos/gabinetes')
@login_required
def gabinetes():
    try:
        gabinetes = Gabinete.query.filter_by(activo=True).all()
        return render_template('gabinetes/list.html', gabinetes=gabinetes)
    except Exception as e:
        return f"Error en gabinetes: {str(e)}"

@app.route('/equipos/ups')
@login_required
def ups():
    try:
        ups_list = UPS.query.filter_by(activo=True).all()
        return render_template('ups/list.html', ups_list=ups_list)
    except Exception as e:
        return f"Error en UPS: {str(e)}"

@app.route('/equipos/switches')
@login_required
def switches():
    try:
        switches = Switch.query.filter_by(activo=True).all()
        return render_template('switches/list.html', switches=switches)
    except Exception as e:
        return f"Error en switches: {str(e)}"

@app.route('/equipos/nvr')
@login_required
def nvr():
    try:
        nvr_list = NVR.query.filter_by(activo=True).all()
        return render_template('nvr/list.html', nvr_list=nvr_list)
    except Exception as e:
        return f"Error en NVR: {str(e)}"

# API endpoints
@app.route('/api/stats')
@login_required
def api_stats():
    try:
        stats = {
            'camaras_total': Camara.query.count(),
            'camaras_activas': Camara.query.filter_by(estado='activa').count(),
            'fallas_abiertas': Falla.query.filter(Falla.estado.in_(['abierta', 'en_proceso'])).count(),
            'mantenimientos_pendientes': Mantenimiento.query.filter_by(estado='programado').count(),
            'gabinetes_total': Gabinete.query.count(),
            'ups_total': UPS.query.count(),
            'switches_total': Switch.query.count()
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoints de diagnóstico
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
        db_status = 'ok'
        db_error = None
        try:
            db.session.execute('SELECT 1')
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

# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    try:
        return render_template('errors/404.html'), 404
    except:
        return "Página no encontrada", 404

@app.errorhandler(500)
def internal_error(error):
    try:
        db.session.rollback()
        return render_template('errors/500.html'), 500
    except:
        return "Error interno del servidor", 500

# Inicialización
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)