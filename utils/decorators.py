# utils/decorators.py
"""
Decoradores personalizados para el sistema
Contiene decoradores para autenticación, permisos, caching, manejo de errores, etc.
"""

import functools
import time
import logging
from functools import wraps
from typing import Callable, Any, Dict, Optional
from flask import request, session, jsonify, current_app
import json
import hashlib

def login_required(f: Callable) -> Callable:
    """
    Decorador para requerir autenticación en rutas
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'No autenticado', 'code': 'UNAUTHORIZED'}), 401
        return f(*args, **kwargs)
    return decorated_function

def require_permission(resource: str, action: str):
    """
    Decorador para requerir permisos específicos
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return jsonify({'error': 'No autenticado', 'code': 'UNAUTHORIZED'}), 401
            
            user = session['user']
            permissions = user.get('permissions', {})
            resource_perms = permissions.get(resource, {})
            
            if not resource_perms.get(action, False):
                return jsonify({
                    'error': 'Sin permisos suficientes', 
                    'code': 'FORBIDDEN',
                    'required': f'{resource}:{action}'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def cache_result(timeout: int = 300):
    """
    Decorador para cachear resultados de funciones
    """
    def decorator(f: Callable) -> Callable:
        cache = {}
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Crear clave de cache
            cache_key = hashlib.md5(
                f"{str(args)}{str(sorted(kwargs.items()))}".encode()
            ).hexdigest()
            
            # Verificar si existe en cache
            if cache_key in cache:
                cached_data, timestamp = cache[cache_key]
                if time.time() - timestamp < timeout:
                    return cached_data
            
            # Ejecutar función y cachear resultado
            result = f(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            
            return result
        
        decorated_function.cache = cache
        return decorated_function
    return decorator

def handle_exceptions(logger: logging.Logger = None, return_error: bool = True):
    """
    Decorador para manejo centralizado de excepciones
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                error_msg = f"Error en {f.__name__}: {str(e)}"
                
                if logger:
                    logger.error(error_msg, exc_info=True)
                else:
                    print(error_msg)
                
                if return_error:
                    return jsonify({
                        'error': 'Error interno del servidor',
                        'message': str(e),
                        'code': 'INTERNAL_ERROR'
                    }), 500
                else:
                    raise e
        
        return decorated_function
    return decorator

def rate_limit(max_calls: int = 100, window: int = 3600):
    """
    Decorador para limitar el número de llamadas a funciones
    """
    def decorator(f: Callable) -> Callable:
        call_times = {}
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user', {}).get('id', 'anonymous')
            current_time = time.time()
            
            # Limpiar llamadas antiguas
            call_times[user_id] = [
                t for t in call_times.get(user_id, [])
                if current_time - t < window
            ]
            
            # Verificar límite
            if len(call_times.get(user_id, [])) >= max_calls:
                return jsonify({
                    'error': 'Límite de llamadas excedido',
                    'code': 'RATE_LIMIT_EXCEEDED'
                }), 429
            
            # Registrar llamada
            if user_id not in call_times:
                call_times[user_id] = []
            call_times[user_id].append(current_time)
            
            return f(*args, **kwargs)
        
        decorated_function.call_times = call_times
        return decorated_function
    return decorator

def validate_json(required_fields: list = None, optional_fields: list = None):
    """
    Decorador para validar datos JSON
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'error': 'Content-Type debe ser application/json',
                    'code': 'INVALID_CONTENT_TYPE'
                }), 400
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'error': 'No se enviaron datos JSON',
                    'code': 'NO_DATA'
                }), 400
            
            # Validar campos requeridos
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'error': 'Campos requeridos faltantes',
                        'missing_fields': missing_fields,
                        'code': 'MISSING_FIELDS'
                    }), 400
            
            # Validar tipos de datos básicos
            validation_errors = []
            
            if required_fields:
                for field in required_fields:
                    if field in data:
                        if data[field] is None:
                            validation_errors.append(f'El campo {field} no puede ser nulo')
                        elif isinstance(data[field], str) and not data[field].strip():
                            validation_errors.append(f'El campo {field} no puede estar vacío')
            
            if validation_errors:
                return jsonify({
                    'error': 'Errores de validación',
                    'validation_errors': validation_errors,
                    'code': 'VALIDATION_ERROR'
                }), 400
            
            # Añadir datos validados al contexto
            kwargs['validated_data'] = data
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def audit_log(action: str, entity: str = None):
    """
    Decorador para registrar auditoría de acciones
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
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
                # Registrar auditoría
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
                
                # Aquí se guardaría en la base de datos de auditoría
                # audit_service.log_action(audit_data)
                
                current_app.logger.info(f"AUDIT: {json.dumps(audit_data, default=str)}")
        
        return decorated_function
    return decorator

def transaction(db_session):
    """
    Decorador para manejar transacciones de base de datos
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

def memoize(timeout: int = 300):
    """
    Decorador para memoización con timeout
    """
    def decorator(f: Callable) -> Callable:
        cache = {}
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Crear clave
            key = str(args) + str(sorted(kwargs.items()))
            cache_key = hashlib.md5(key.encode()).hexdigest()
            
            current_time = time.time()
            
            # Verificar cache
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if current_time - timestamp < timeout:
                    return result
            
            # Ejecutar y cachear
            result = f(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            
            return result
        
        decorated_function.cache = cache
        return decorated_function
    return decorator

def deprecated(reason: str = None):
    """
    Decorador para marcar funciones como deprecadas
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            import warnings
            warning_msg = f"La función {f.__name__} está deprecada"
            if reason:
                warning_msg += f". Razón: {reason}"
            
            warnings.warn(warning_msg, DeprecationWarning, stacklevel=2)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def profile(sort_by: str = 'cumulative'):
    """
    Decorador para perfilar funciones
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
                
                # Solo mostrar en desarrollo
                if current_app.config.get('DEBUG', False):
                    stats = pstats.Stats(pr)
                    stats.sort_stats(sort_by)
                    print(f"\n=== Profile for {f.__name__} ===")
                    stats.print_stats(10)
        
        return decorated_function
    return decorator