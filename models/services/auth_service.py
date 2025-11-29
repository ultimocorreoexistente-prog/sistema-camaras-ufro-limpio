# services/auth_service.py
"""
Servicio de autenticación y autorización
Maneja login, logout, permisos y roles de usuario
"""

import hashlib
from flask import session, current_app
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any
import secrets

class AuthService:
    """Servicio para manejar autenticación y autorización"""
    
    def __init__(self, db_session=None):
        self.db = db_session
        self.session_timeout = 1800 # 30 minutos

def hash_password(self, password: str) -> str:
    """
    Hashea una contraseña usando SHA-256 con salt
    """
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(self, password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash
    """
    try:
        salt, password_hash = hashed_password.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except ValueError:
        return False

def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Autentica un usuario por email y contraseña
    """
    try:
        user = self.db.execute(
            "SELECT * FROM usuarios WHERE email = %s AND activo = true",
            (email,)
        ).fetchone()

        if user and self.verify_password(password, user.password_hash):
            # Actualizar último acceso
            self.db.execute(
                "UPDATE usuarios SET ultimo_acceso = %s WHERE id = %s",
                (datetime.now(), user.id)
            )
            self.db.commit()

            return {
                'id': user.id,
                'email': user.email,
                'nombre': user.nombre,
                'apellido': user.apellido,
                'rol': user.rol,
                'permissions': self.get_user_permissions(user.rol)
            }
        return None

    except Exception as e:
        current_app.logger.error(f"Error en autenticación: {e}")
        return None

def get_user_permissions(self, rol: str) -> Dict[str, bool]:
    """
    Retorna los permisos basados en el rol del usuario
    """
    permissions = {
        'admin': {
            'usuarios': {'read': True, 'write': True, 'delete': True},
            'camaras': {'read': True, 'write': True, 'delete': True},
            'fails': {'read': True, 'write': True, 'delete': True},
            'mantenimientos': {'read': True, 'write': True, 'delete': True},
            'reportes': {'read': True, 'write': True},
            'sistema': {'read': True, 'write': True}
        },
        'tecnico': {
            'usuarios': {'read': True},
            'camaras': {'read': True, 'write': True},
            'fails': {'read': True, 'write': True},
            'mantenimientos': {'read': True, 'write': True},
            'reportes': {'read': True, 'write': True},
            'sistema': {'read': True}
        },
        'usuario': {
            'usuarios': {'read': True},
            'camaras': {'read': True},
            'fails': {'read': True},
            'mantenimientos': {'read': True},
            'reportes': {'read': True},
            'sistema': {'read': False}
        }
    }

    return permissions.get(rol, permissions['usuario'])

def has_permission(self, user: Dict[str, Any], resource: str, action: str) -> bool:
    """
    Verifica si un usuario tiene permiso para una acción específica
    """
    permissions = user.get('permissions', {})
    resource_perms = permissions.get(resource, {})
    return resource_perms.get(action, False)

def create_session(self, user_id: int) -> str:
    """
    Crea una sesión para el usuario
    """
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(seconds=self.session_timeout)

    # Guardar en base de datos de sesiones
    self.db.execute(
        "INSERT INTO user_sessions (session_id, user_id, expires_at) VALUES (%s, %s, %s)",
        (session_id, user_id, expires_at)
    )
    self.db.commit()

    return session_id

def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
    """
    Valida una sesión y retorna información del usuario
    """
    try:
        session_data = self.db.execute(
            "SELECT s.*, u.* FROM user_sessions s "
            "JOIN usuarios u ON s.user_id = u.id "
            "WHERE s.session_id = %s AND s.expires_at > %s AND u.activo = true",
            (session_id, datetime.now())
        ).fetchone()

        if session_data:
            return {
                'id': session_data.user_id,
                'email': session_data.email,
                'nombre': session_data.nombre,
                'apellido': session_data.apellido,
                'rol': session_data.rol
            }
        return None

    except Exception as e:
        current_app.logger.error(f"Error validando sesión: {e}")
        return None

def logout(self, session_id: str) -> bool:
    """
    Cierra una sesión específica
    """
    try:
        self.db.execute("DELETE FROM user_sessions WHERE session_id = %s", (session_id,))
        self.db.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Error cerrando sesión: {e}")
        return False

def cleanup_expired_sessions(self) -> int:
    """
    Limpia sesiones expiradas
    """
    try:
        result = self.db.execute(
            "DELETE FROM user_sessions WHERE expires_at <= %s",
            (datetime.now(),)
        )
        self.db.commit()
        return result.rowcount
    except Exception as e:
        current_app.logger.error(f"Error limpiando sesiones: {e}")
        return 0

# Decorador para proteger rutas
def login_required(f):
    """
    Decorador para requerir autenticación en rutas
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return {'error': 'No autenticado'}, 401
        return f(*args, **kwargs)
    return decorated_function

def require_permission(resource: str, action: str):
    """
    Decorador para requerir permisos específicos
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return {'error': 'No autenticado'}, 401

            auth_service = AuthService()
            if not auth_service.has_permission(session['user'], resource, action):
                return {'error': 'Sin permisos suficientes'}, 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator