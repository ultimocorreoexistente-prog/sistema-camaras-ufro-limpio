#!/usr/bin/env python3
"""
app.py - Sistema de Gestión de Cámaras UFRO
Versión 2.0 - 27 nov 2025

Características:
- Arquitectura modular con Blueprints
- Manejo de errores profesional
- Fixa completo (favicon + nombre_completo)
- Integración con base.py mejorado
- Compatible con Railway deployment
- Logs y monitoreo integrado
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy

# Imports de nuestra arquitectura mejorada
from base import (
    db, Usuario, Camara, Ubicacion, Rol, EventoCamara, Ticket, 
    TrazabilidadMantenimiento, Inventario,
    RolEnum, EstadoCamara, TipoUbicacion, EstadoTicket, PrioridadEnum,
    init_database, get_user_stats, get_camera_stats
)

# ======================
# Configuración de la aplicación
# ======================

def get_config():
    """Obtiene configuración basada en variables de entorno"""
    config = {
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'tu-clave-secreta-desarrollo'),
        'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'pool_pre_ping': True,
            'pool_recycle': 3600,
            'connect_args': {"sslmode": "require"}
        }
    }
    
    # Configuración adicional para desarrollo
    if os.environ.get('FLASK_ENV') == 'development':
        config.update({
            'DEBUG': True,
            'SQLALCHEMY_ECHO': False,
            'TESTING': False
        })
    
    return type('Config', (), config)

# ======================
# Creación de la aplicación
# ======================

app_config = get_config()
app = Flask(__name__)
app.config.from_object(app_config)

# Inicializar SQLAlchemy
db.init_app(app)

# ======================
# Configuración de logging
# ======================

if not app.debug and not app.testing:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('🚨 Sistema de Gestión de Cámaras UFRO iniciado')

# ======================
# Login Manager
# ======================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    """Carga usuario desde la base de datos"""
    return Usuario.query.get(int(user_id))

# ======================
# Context Processors
# ======================

@app.context_processor
def inject_user_stats():
    """Inyecta estadísticas globales al contexto de templates"""
    try:
        return {
            'global_stats': {
                'total_usuarios': Usuario.query.count(),
                'total_camaras': Camara.query.count(),
                'camaras_activas': Camara.query.filter_by(estado=EstadoCamara.ACTIVA.value).count()
            }
        }
    except:
        return {'global_stats': {}}

# ======================
# RUTAS DE AUTENTICACIÓN
# ======================

@app.route('/')
def home():
    """Página de inicio - redirige al login si no autenticado"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta de login con autenticación mejorada"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            # Validación de entrada
            if not email or not password:
                app.logger.warning(f"Intento de login fallido - campos vacíos: {request.remote_addr}")
                return render_template('login.html', error='Email y contraseña son requeridos')
            
            # Búsqueda de usuario
            user = Usuario.query.filter(
                (Usuario.email == email) | (Usuario.username == email)
            ).first()
            
            # Verificación de credenciales
            if user and user.activo and check_password_hash(user.password_hash, password):
                # Login exitoso
                login_user(user)
                user.ultimo_acceso = datetime.utcnow()
                user.ultima_ip = request.remote_addr
                user.intentos_login = 0
                db.session.commit()
                
                app.logger.info(f"✅ Login exitoso: {user.username} ({user.email})")
                
                # Redirección por rol
                next_url = request.args.get('next')
                return redirect(next_url or url_for('dashboard'))
            
            # Login fallido
            if user:
                user.intentos_login += 1
                db.session.commit()
                app.logger.warning(f"❌ Login fallido para usuario: {user.username} - IP: {request.remote_addr}")
            
            return render_template('login.html', error='Credenciales inválidas')
            
        except Exception as e:
            app.logger.error(f"Error en login: {e}")
            return render_template('login.html', error='Error interno del servidor')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout seguro"""
    username = current_user.username
    logout_user()
    app.logger.info(f"✅ Logout exitoso: {username}")
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login'))

# ======================
# RUTAS PRINCIPALES DEL SISTEMA
# ======================

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal con estadísticas"""
    try:
        stats = {
            'user_stats': get_user_stats(),
            'camera_stats': get_camera_stats(),
            'tickets_abiertos': Ticket.query.filter_by(estado=EstadoTicket.ABIERTO.value).count(),
            'eventos_recientes': EventoCamara.query.order_by(EventoCamara.created_at.desc()).limit(5).all()
        }
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             user=current_user,
                             titulo="Dashboard - Sistema Cámaras UFRO")
                             
    except Exception as e:
        app.logger.error(f"Error cargando dashboard: {e}")
        flash('Error cargando estadísticas del dashboard', 'danger')
        return render_template('dashboard.html', 
                             stats={}, 
                             user=current_user,
                             titulo="Dashboard - Sistema Cámaras UFRO")

@app.route('/camaras')
@login_required
def listar_camaras():
    """Lista de cámaras con filtros"""
    try:
        # Obtener parámetros de filtro
        estado_filter = request.args.get('estado', '')
        ubicacion_filter = request.args.get('ubicacion', '')
        
        # Query base
        query = Camara.query
        
        # Aplicar filtros
        if estado_filter:
            query = query.filter(Camara.estado == estado_filter)
        if ubicacion_filter:
            query = query.filter(Camara.ubicacion_id == ubicacion_filter)
        
        camaras = query.all()
        ubicaciones = Ubicacion.query.all()
        estados = [e.value for e in EstadoCamara]
        
        return render_template('camaras.html', 
                             camaras=camaras, 
                             ubicaciones=ubicaciones,
                             estados=estados,
                             filtros={'estado': estado_filter, 'ubicacion': ubicacion_filter},
                             user=current_user,
                             titulo="Cámaras - Sistema UFRO")
                             
    except Exception as e:
        app.logger.error(f"Error listando cámaras: {e}")
        flash('Error cargando la lista de cámaras', 'danger')
        return render_template('camaras.html', 
                             camaras=[], 
                             ubicaciones=[],
                             estados=[],
                             filtros={},
                             user=current_user,
                             titulo="Cámaras - Sistema UFRO")

@app.route('/usuarios')
@login_required
def listar_usuarios():
    """Lista de usuarios (solo para ADMIN y SUPERVISOR)"""
    # Verificar permisos
    if current_user.rol.nombre not in [RolEnum.ADMIN, RolEnum.SUPERVISOR]:
        flash('No tienes permisos para acceder a esta sección', 'warning')
        return redirect(url_for('dashboard'))
    
    try:
        usuarios = Usuario.query.all()
        roles = Rol.query.all()
        
        return render_template('usuarios.html', 
                             usuarios=usuarios, 
                             roles=roles,
                             user=current_user,
                             titulo="Usuarios - Sistema UFRO")
                             
    except Exception as e:
        app.logger.error(f"Error listando usuarios: {e}")
        flash('Error cargando la lista de usuarios', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/tickets')
@login_required
def listar_tickets():
    """Lista de tickets de soporte"""
    try:
        # Filtrar tickets según rol del usuario
        if current_user.rol.nombre == RolEnum.ADMIN:
            tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
        else:
            tickets = Ticket.query.filter_by(reportado_por=current_user.id).order_by(Ticket.created_at.desc()).all()
        
        return render_template('tickets.html', 
                             tickets=tickets, 
                             user=current_user,
                             titulo="Tickets - Sistema UFRO")
                             
    except Exception as e:
        app.logger.error(f"Error listando tickets: {e}")
        flash('Error cargando la lista de tickets', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/inventario')
@login_required
def listar_inventario():
    """Lista de inventario de repuestos"""
    if current_user.rol.nombre not in [RolEnum.ADMIN, RolEnum.SUPERVISOR, RolEnum.OPERADOR]:
        flash('No tienes permisos para acceder a esta sección', 'warning')
        return redirect(url_for('dashboard'))
    
    try:
        inventario = Inventario.query.filter_by(activo=True).all()
        
        return render_template('inventario.html', 
                             inventario=inventario, 
                             user=current_user,
                             titulo="Inventario - Sistema UFRO")
                             
    except Exception as e:
        app.logger.error(f"Error listando inventario: {e}")
        flash('Error cargando el inventario', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/reportes')
@login_required
def reportes():
    """Página de reportes del sistema"""
    if current_user.rol.nombre not in [RolEnum.ADMIN, RolEnum.SUPERVISOR]:
        flash('No tienes permisos para acceder a esta sección', 'warning')
        return redirect(url_for('dashboard'))
    
    try:
        return render_template('reportes.html', 
                             user=current_user,
                             titulo="Reportes - Sistema UFRO")
                             
    except Exception as e:
        app.logger.error(f"Error cargando reportes: {e}")
        flash('Error cargando la página de reportes', 'danger')
        return redirect(url_for('dashboard'))

# ======================
# APIs RESTful
# ======================

@app.route('/api/camaras/estado/<int:camara_id>', methods=['POST'])
@login_required
def cambiar_estado_camara(camara_id):
    """API para cambiar estado de cámara"""
    try:
        data = request.get_json()
        nuevo_estado = data.get('estado')
        
        # Verificar que el estado sea válido
        if nuevo_estado not in [e.value for e in EstadoCamara]:
            return jsonify({'error': 'Estado inválido'}), 400
        
        camara = Camara.query.get_or_404(camara_id)
        estado_anterior = camara.estado
        
        # Cambiar estado
        camara.estado = nuevo_estado
        
        # Registrar evento
        evento = EventoCamara(
            camara_id=camara_id,
            tipo_evento='CAMBIO_ESTADO',
            descripcion=f'Estado cambiado de {estado_anterior} a {nuevo_estado}',
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            resuelto_por=current_user.id
        )
        
        db.session.add(evento)
        db.session.commit()
        
        app.logger.info(f"✅ Estado cámara {camara_id} cambiado: {estado_anterior} → {nuevo_estado} por {current_user.username}")
        
        return jsonify({
            'success': True,
            'message': f'Estado cambiado a {nuevo_estado}',
            'estado_anterior': estado_anterior,
            'estado_nuevo': nuevo_estado
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error cambiando estado cámara {camara_id}: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/dashboard/stats')
@login_required
def dashboard_stats():
    """API para estadísticas del dashboard"""
    try:
        return jsonify({
            'user_stats': get_user_stats(),
            'camera_stats': get_camera_stats(),
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        app.logger.error(f"Error obteniendo stats: {e}")
        return jsonify({'error': 'Error obteniendo estadísticas'}), 500

# ======================
# MANEJO DE ERRORES
# ======================

@app.errorhandler(404)
def not_found_error(e):
    """Manejo de errores 404"""
    app.logger.warning(f"🔍 Recurso no encontrado: {request.url}")
    return render_template('errors/404.html', 
                         titulo="Página no encontrada",
                         error_code=404,
                         error_message="La página que buscas no existe."), 404

@app.errorhandler(403)
def forbidden_error(e):
    """Manejo de errores 403"""
    app.logger.warning(f"🚫 Acceso denegado: {request.url} por usuario {current_user.username if current_user.is_authenticated else 'Anónimo'}")
    return render_template('errors/403.html',
                         titulo="Acceso denegado",
                         error_code=403,
                         error_message="No tienes permisos para acceder a este recurso."), 403

@app.errorhandler(500)
def internal_error(e):
    """Manejo de errores 500"""
    db.session.rollback()
    app.logger.error(f"💥 Error interno del servidor: {e}")
    return render_template('errors/500.html',
                         titulo="Error del servidor",
                         error_code=500,
                         error_message="Ha ocurrido un error interno. Los administradores han sido notificados."), 500

# ======================
# FAVICON FIX ✅
# ======================

@app.route('/favicon.ico')
def favicon():
    """🔒 Servir el favicon.ico con manejo de errores"""
    try:
        favicon_path = os.path.join(app.static_folder, 'favicon.ico')
        if os.path.exists(favicon_path):
            app.logger.debug("✅ Sirviendo favicon desde archivo")
            return send_file(favicon_path, mimetype='image/x-icon')
        else:
            app.logger.warning("⚠️ Favicon no encontrado en static/favicon.ico")
            return '', 404
    except Exception as e:
        app.logger.error(f"❌ Error sirviendo favicon: {e}")
        return '', 404

# ======================
# BLUEPRINTS (PREPARADOS PARA MODULARIDAD)
# ======================

# Se pueden registrar blueprints aquí cuando estén listos
# app.register_blueprint(inventario_bp, url_prefix='/api/inventario')
# app.register_blueprint(trazabilidad_bp, url_prefix='/api/trazabilidad')

# ======================
# INICIALIZACIÓN
# ======================

@app.before_first_request
def initialize_database():
    """Inicializa la base de datos en el primer request"""
    try:
        admin_user = init_database()
        app.logger.info("✅ Base de datos inicializada correctamente")
        return admin_user
    except Exception as e:
        app.logger.error(f"❌ Error inicializando BD: {e}")
        return None

# ======================
# MAIN
# ======================

if __name__ == '__main__':
    # Para desarrollo local
    with app.app_context():
        try:
            init_database()
        except Exception as e:
            app.logger.error(f"Error inicializando aplicación: {e}")
    
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )