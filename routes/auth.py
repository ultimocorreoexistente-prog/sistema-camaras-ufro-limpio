"""
Blueprint de Autenticación para Sistema de Cámaras UFRO
Maneja login, logout y autenticación con Flask-Login
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta de login con autenticación mejorada"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_bp.index'))
    
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            # Validación de entrada
            if not email or not password:
                logger.warning(f"Intento de login fallido - campos vacíos: {request.remote_addr}")
                return render_template('login.html', error='Email y contraseña son requeridos')
            
            # Importar usuario aquí para evitar dependencias circulares
            from models import Usuario
            from models import db
            
            # Búsqueda de usuario
            user = Usuario.query.filter(
                (Usuario.email == email) | (Usuario.username == email)
            ).first()
            
            # Verificación de credenciales
            if user and hasattr(user, 'activo') and user.activo and check_password_hash(user.password_hash, password):
                # Login exitoso
                login_user(user)
                user.ultimo_acceso = datetime.utcnow()
                user.ultima_ip = request.remote_addr
                if hasattr(user, 'intentos_login'):
                    user.intentos_login = 0
                db.session.commit()
                
                logger.info(f"✅ Login exitoso: {user.username} ({user.email})")
                
                # Redirección por rol
                next_url = request.args.get('next')
                return redirect(next_url or url_for('dashboard_bp.index'))
            
            # Login fallido
            if user and hasattr(user, 'intentos_login'):
                user.intentos_login += 1
                db.session.commit()
                logger.warning(f"❌ Login fallido para usuario: {user.username} - IP: {request.remote_addr}")
            
            return render_template('login.html', error='Credenciales inválidas')
            
        except Exception as e:
            logger.error(f"Error en login: {e}")
            return render_template('login.html', error='Error interno del servidor')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout seguro"""
    username = current_user.username
    logout_user()
    logger.info(f"✅ Logout exitoso: {username}")
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de nuevos usuarios (solo para desarrollo)"""
    # Solo en desarrollo - cerrar en producción
    if current_app.config.get('DEBUG', False):
        if request.method == 'POST':
            try:
                from models import Usuario, db
                data = request.form
                
                # Validar campos requeridos
                if not all([data.get('username'), data.get('email'), data.get('password')]):
                    return render_template('register.html', error='Todos los campos son requeridos')
                
                # Verificar que el usuario no exista
                if Usuario.query.filter(
                    (Usuario.email == data['email']) | (Usuario.username == data['username'])
                ).first():
                    return render_template('register.html', error='Usuario o email ya existe')
                
                # Crear nuevo usuario
                nuevo_usuario = Usuario(
                    username=data['username'],
                    email=data['email'],
                    password_hash=generate_password_hash(data['password']),
                    nombre=data.get('nombre', ''),
                    apellido=data.get('apellido', ''),
                    activo=True,
                    fecha_creacion=datetime.utcnow()
                )
                
                db.session.add(nuevo_usuario)
                db.session.commit()
                
                flash('Usuario creado exitosamente', 'success')
                return redirect(url_for('auth.login'))
                
            except Exception as e:
                logger.error(f"Error en registro: {e}")
                return render_template('register.html', error='Error al crear usuario')
        
        return render_template('register.html')
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Cambio de contraseña"""
    if request.method == 'POST':
        try:
            from models import Usuario, db
            
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            # Validar contraseñas
            if not current_password or not new_password:
                return render_template('change_password.html', error='Contraseñas requeridas')
            
            if new_password != confirm_password:
                return render_template('change_password.html', error='Las contraseñas no coinciden')
            
            if len(new_password) < 6:
                return render_template('change_password.html', error='La contraseña debe tener al menos 6 caracteres')
            
            # Verificar contraseña actual
            user = current_user
            if not check_password_hash(user.password_hash, current_password):
                return render_template('change_password.html', error='Contraseña actual incorrecta')
            
            # Actualizar contraseña
            user.password_hash = generate_password_hash(new_password)
            user.fecha_actualizacion = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"✅ Contraseña cambiada para usuario: {user.username}")
            flash('Contraseña cambiada exitosamente', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            logger.error(f"Error cambiando contraseña: {e}")
            return render_template('change_password.html', error='Error interno del servidor')
    
    return render_template('change_password.html')