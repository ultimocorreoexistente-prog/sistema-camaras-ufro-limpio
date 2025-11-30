# utils/decorators.py
"""
Decorators utility module for authentication and authorization
Contains JWT-based authentication and role-based access control decorators
"""

from functools import wraps
from flask import request, jsonify, current_app
import jwt
from datetime import datetime, timedelta
from typing import Callable, Any, Dict, Optional


def token_required(f: Callable) -> Callable:
    """
    Decorator for JWT token authentication
    Requires valid Bearer token in Authorization header
    Passes current_user as first parameter to decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer TOKEN
            except IndexError:
                return jsonify({'error': 'Token inválido'}), 401

        if not token:
            return jsonify({'error': 'Token requerido'}), 401

        try:
            # Decode JWT token
            data = jwt.decode(
                token, 
                current_app.config['SECRET_KEY'], 
                algorithms=['HS256']
            )
            
            # Get current user from database
            from models import Usuario
            current_user = Usuario.query.filter_by(
                id=data['user_id'], 
                activo=True
            ).first()

            if not current_user:
                return jsonify({'error': 'Usuario no encontrado o inactivo'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        except Exception as e:
            return jsonify({'error': f'Error de autenticación: {str(e)}'}), 401

        # Pass current_user as first argument
        return f(current_user, *args, **kwargs)

    return decorated


def require_permission(permission: str):
    """
    Decorator for role-based access control
    Checks if current_user has specific permission
    Must be used after @token_required decorator
    
    Args:
        permission: Permission name to check (e.g., 'fallas_crear', 'usuarios_editar')
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            # Check if user has permission
            if not current_user.tiene_permiso(permission):
                return jsonify({
                    'error': 'Permisos insuficientes',
                    'required_permission': permission
                }), 403
            
            return f(current_user, *args, **kwargs)
        
        return decorated_function
    return decorator


def require_role(role_name: str):
    """
    Decorator for role-based access control
    Checks if current_user has specific role
    Must be used after @token_required decorator
    
    Args:
        role_name: Role name to check (e.g., 'admin', 'tecnico', 'supervisor')
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            # Check if user has role
            if not current_user.rol or current_user.rol.nombre != role_name:
                return jsonify({
                    'error': 'Rol insuficiente',
                    'required_role': role_name,
                    'user_role': current_user.rol.nombre if current_user.rol else None
                }), 403
            
            return f(current_user, *args, **kwargs)
        
        return decorated_function
    return decorator


def require_any_permission(permissions: list):
    """
    Decorator for role-based access control
    Checks if current_user has ANY of the specified permissions
    Must be used after @token_required decorator
    
    Args:
        permissions: List of permission names to check (user needs at least one)
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            # Check if user has any of the permissions
            has_permission = any(
                current_user.tiene_permiso(perm) 
                for perm in permissions
            )
            
            if not has_permission:
                return jsonify({
                    'error': 'Permisos insuficientes',
                    'required_permissions': permissions
                }), 403
            
            return f(current_user, *args, **kwargs)
        
        return decorated_function
    return decorator


def require_all_permissions(permissions: list):
    """
    Decorator for role-based access control
    Checks if current_user has ALL of the specified permissions
    Must be used after @token_required decorator
    
    Args:
        permissions: List of permission names to check (user needs all)
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            # Check if user has all the permissions
            has_all_permissions = all(
                current_user.tiene_permiso(perm) 
                for perm in permissions
            )
            
            if not has_all_permissions:
                return jsonify({
                    'error': 'Permisos insuficientes',
                    'required_permissions': permissions
                }), 403
            
            return f(current_user, *args, **kwargs)
        
        return decorated_function
    return decorator


def owner_or_permission(resource_id_param: str = 'id', permission: str = None):
    """
    Decorator that allows access if:
    1. User is the owner of the resource, OR
    2. User has the specified permission
    
    Must be used after @token_required decorator
    
    Args:
        resource_id_param: Name of the parameter containing the resource ID
        permission: Permission name to check if not owner
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            # Get resource ID from kwargs
            resource_id = kwargs.get(resource_id_param)
            
            if not resource_id:
                return jsonify({'error': 'ID de recurso no encontrado'}), 400
            
            # Check if user is owner or has permission
            is_owner = hasattr(current_user, 'id') and str(current_user.id) == str(resource_id)
            
            if is_owner:
                return f(current_user, *args, **kwargs)
            
            if permission and not current_user.tiene_permiso(permission):
                return jsonify({
                    'error': 'Permisos insuficientes',
                    'required_permission': permission
                }), 403
            
            return f(current_user, *args, **kwargs)
        
        return decorated_function
    return decorator


# Legacy decorators for backward compatibility
def cache_result(timeout: int = 300):
    """
    Decorator for caching function results
    """
    def decorator(f: Callable) -> Callable:
        cache = {}

        @wraps(f)
        def decorated_function(*args, **kwargs):
            import hashlib
            import time
            
            # Create cache key
            cache_key = hashlib.md5(
                f"{str(args)}{str(sorted(kwargs.items()))}".encode()
            ).hexdigest()

            # Check if exists in cache
            if cache_key in cache:
                cached_data, timestamp = cache[cache_key]
                if time.time() - timestamp < timeout:
                    return cached_data

            # Execute function and cache result
            result = f(*args, **kwargs)
            cache[cache_key] = (result, time.time())

            return result

        decorated_function.cache = cache
        return decorated_function
    return decorator


def handle_exceptions(logger=None, return_error: bool = True):
    """
    Decorator for centralized exception handling
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                import logging
                error_msg = f"Error en {f.__name__}: {str(e)}"

                if logger:
                    logger.error(error_msg, exc_info=True)
                else:
                    logging.error(error_msg, exc_info=True)

                if return_error:
                    return jsonify({
                        'error': 'Error interno del servidor',
                        'message': str(e)
                    }), 500
                else:
                    raise e

        return decorated_function
    return decorator


def rate_limit(max_calls: int = 100, window: int = 3600):
    """
    Decorator for limiting function calls
    """
    def decorator(f: Callable) -> Callable:
        import time
        call_times = {}

        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import session
            
            user_id = session.get('user', {}).get('id', 'anonymous')
            current_time = time.time()

            # Clean old calls
            call_times[user_id] = [
                t for t in call_times.get(user_id, [])
                if current_time - t < window
            ]

            # Check limit
            if len(call_times.get(user_id, [])) >= max_calls:
                return jsonify({
                    'error': 'Límite de llamadas excedido',
                    'retry_after': window
                }), 429

            # Register call
            if user_id not in call_times:
                call_times[user_id] = []
            call_times[user_id].append(current_time)

            return f(*args, **kwargs)

        decorated_function.call_times = call_times
        return decorated_function
    return decorator


def transaction(db_session):
    """
    Decorator for database transaction management
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                db_session.commit()
                return result
            except Exception as e:
                db_session.rollback()
                current_app.logger.error(f"Transaction rolled back for {f.__name__}: {e}")
                raise e

        return decorated_function
    return decorator


def audit_log(action: str, entity: str = None):
    """
    Decorator for logging audit trails
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            import time
            import json
            from flask import session
            
            start_time = time.time()
            result = None
            error = None

            try:
                result = f(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                raise e
            finally:
                # Log audit information
                execution_time = time.time() - start_time

                audit_data = {
                    'action': action,
                    'entity': entity or f.__name__,
                    'user_id': session.get('user', {}).get('id'),
                    'user_email': session.get('user', {}).get('email'),
                    'execution_time': execution_time,
                    'success': error is None,
                    'error': error,
                    'timestamp': time.time(),
                    'request_data': {
                        'method': request.method,
                        'url': request.url,
                        'args': dict(request.args),
                        'form': dict(request.form) if request.form else None
                    }
                }

                current_app.logger.info(f"AUDIT: {json.dumps(audit_data, default=str)}")

        return decorated_function
    return decorator


def deprecated(reason: str = None):
    """
    Decorator for marking functions as deprecated
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            import warnings
            import traceback
            
            warning_msg = f"La función {f.__name__} está deprecada"
            if reason:
                warning_msg += f". Razón: {reason}"

            warnings.warn(warning_msg, DeprecationWarning, stacklevel=2)
            traceback.print_stack(limit=3)

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def profile(sort_by: str = 'cumulative'):
    """
    Decorator for function profiling
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            import cProfile
            import pstats

            pr = cProfile.Profile()
            pr.enable()

            try:
                result = f(*args, **kwargs)
                return result
            finally:
                pr.disable()

                # Only show in development
                if current_app.config.get('DEBUG', False):
                    stats = pstats.Stats(pr)
                    stats.sort_stats(sort_by)
                    print(f"\n=== Profile for {f.__name__} ===")
                    stats.print_stats(10)

        return decorated_function
    return decorator
