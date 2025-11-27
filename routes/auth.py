#!/usr/bin/env python3
"""
Blueprint de Autenticación - Sistema Cámaras UFRO
================================================

Manejo completo de autenticación de usuarios con Flask-Login.
- Login/Logout
- Registro de usuarios
- Gestión de sesiones
- Validación de permisos

Autor: MiniMax Agent
Fecha: 2025-11-27
Versión: 3.0-hybrid
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
import logging
from datetime import datetime

# Configurar logging
logger = logging.getLogger(__name__)

# Crear blueprint
auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Ruta de login de usuarios
    GET: Mostrar formulario de login
    POST: Procesar autenticación
    """
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            # Validaciones básicas
            if not email or not password:
                flash('Por favor ingresa email y contraseña.', 'warning')
                return render_template('auth/login.html')
            
            # Buscar usuario en base de datos
            from models import Usuario
            user = Usuario.query.filter_by(email=email).first()
            
            # Verificar credenciales
            if user and check_password_hash(user.password_hash, password):
                if not user.activo:
                    flash('Tu cuenta está desactivada. Contacta al administrador.', 'danger')
                    return render_template('auth/login.html')
                
                # Login exitoso
                login_user(user, remember=True)
                logger.info(f"Login exitoso para usuario: {email}")
                
                # Redireccionar a la página que solicitó o al dashboard
                next_url = request.args.get('next')
                return redirect(next_url or url_for('dashboard_bp.index'))
            else:
                flash('Email o contraseña incorrectos.', 'danger')
                logger.warning(f"Intento de login fallido para: {email}")
                
        except Exception as e:
            logger.error(f"Error en login: {str(e)}")
            flash('Error interno. Intenta nuevamente.', 'danger')
    
    # Si ya está autenticado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_bp.index'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Logout de usuario
    """
    try:
        email = current_user.email
        logout_user()
        logger.info(f"Logout exitoso para usuario: {email}")
        flash('Sesión cerrada correctamente.', 'info')
    except Exception as e:
        logger.error(f"Error en logout: {str(e)}")
        flash('Error al cerrar sesión.', 'danger')
    
    return redirect(url_for('auth_bp.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registro de nuevos usuarios
    GET: Mostrar formulario de registro
    POST: Procesar registro
    """
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            nombre = request.form.get('nombre', '').strip()
            apellido = request.form.get('apellido', '').strip()
            
            # Validaciones
            if not all([email, password, confirm_password, nombre, apellido]):
                flash('Todos los campos son obligatorios.', 'warning')
                return render_template('auth/register.html')
            
            if password != confirm_password:
                flash('Las contraseñas no coinciden.', 'warning')
                return render_template('auth/register.html')
            
            if len(password) < 6:
                flash('La contraseña debe tener al menos 6 caracteres.', 'warning')
                return render_template('auth/register.html')
            
            # Verificar si el email ya existe
            from models import Usuario
            existing_user = Usuario.query.filter_by(email=email).first()
            if existing_user:
                flash('Este email ya está registrado.', 'warning')
                return render_template('auth/register.html')
            
            # Crear nuevo usuario
            new_user = Usuario(
                email=email,
                password_hash=generate_password_hash(password),
                nombre=nombre,
                apellido=apellido,
                activo=True
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            logger.info(f"Nuevo usuario registrado: {email}")
            flash('Cuenta creada exitosamente. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth_bp.login'))
            
        except IntegrityError:
            db.session.rollback()
            flash('Error: Este email ya está registrado.', 'danger')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error en registro: {str(e)}")
            flash('Error interno. Intenta nuevamente.', 'danger')
    
    return render_template('auth/register.html')

@auth_bp.route('/profile')
@login_required
def profile():
    """
    Perfil de usuario
    """
    try:
        return render_template('auth/profile.html', user=current_user)
    except Exception as e:
        logger.error(f"Error en perfil: {str(e)}")
        flash('Error cargando perfil.', 'danger')
        return redirect(url_for('dashboard_bp.index'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Cambio de contraseña
    """
    if request.method == 'POST':
        try:
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validaciones
            if not all([current_password, new_password, confirm_password]):
                flash('Todos los campos son obligatorios.', 'warning')
                return render_template('auth/change_password.html')
            
            # Verificar contraseña actual
            if not check_password_hash(current_user.password_hash, current_password):
                flash('Contraseña actual incorrecta.', 'danger')
                return render_template('auth/change_password.html')
            
            if new_password != confirm_password:
                flash('Las nuevas contraseñas no coinciden.', 'warning')
                return render_template('auth/change_password.html')
            
            if len(new_password) < 6:
                flash('La nueva contraseña debe tener al menos 6 caracteres.', 'warning')
                return render_template('auth/change_password.html')
            
            # Actualizar contraseña
            current_user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            
            logger.info(f"Contraseña actualizada para usuario: {current_user.email}")
            flash('Contraseña actualizada exitosamente.', 'success')
            return redirect(url_for('auth_bp.profile'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error cambiando contraseña: {str(e)}")
            flash('Error interno. Intenta nuevamente.', 'danger')
    
    return render_template('auth/change_password.html')

@auth_bp.route('/check-session')
@login_required
def check_session():
    """
    API endpoint para verificar estado de sesión
    """
    try:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'nombre': current_user.nombre,
                'apellido': current_user.apellido
            }
        })
    except Exception as e:
        logger.error(f"Error verificando sesión: {str(e)}")
        return jsonify({'authenticated': False, 'error': str(e)}), 500

@auth_bp.route('/unauthorized')
def unauthorized():
    """
    Página mostrada cuando usuario no autorizado intenta acceder
    """
    return render_template('auth/unauthorized.html')

# Importar db para evitar circular import
from models import db