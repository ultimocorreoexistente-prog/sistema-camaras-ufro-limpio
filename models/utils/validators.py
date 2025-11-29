# utils/validators.py
"""
Validadores de datos para el sistema
Contiene funciones para validar emails, IPs, datos de cámaras, usuarios, etc.
"""

import re
import ipaddress
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
import json

class ValidationError(Exception):
    """Excepción para errores de validación"""
    pass

class Validator:
    """Clase base para validadores"""
    
    @staticmethod
def is_required(value: Any) -> bool:
"""Verifica si un valor es requerido (no None, no vacío)"""
return value is not None and str(value).strip() = ''

@staticmethod
def is_in_range(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> bool:
"""Verifica si un valor está en un rango"""
try:
num_value = float(value)
return min_val <= num_value <= max_val
except (ValueError, TypeError):
return False

@staticmethod
def is_valid_length(value: str, min_length: int = 0, max_length: int = None) -> bool:
"""Verifica la longitud de una cadena"""
if not isinstance(value, str):
return False

length = len(value)
if length < min_length:
return False

if max_length is not None and length > max_length:
return False

return True

class EmailValidator(Validator):
"""Validador de direcciones de email"""

EMAIL_REGEX = re.compile(
r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{,}$'
)

@classmethod
def validate(cls, email: str) -> Tuple[bool, str]:
"""
Valida una dirección de email
Returns: (is_valid, error_message)
"""
if not cls.is_required(email):
return False, "Email es requerido"

if not cls.is_valid_length(email, 5, 55):
return False, "Email debe tener entre 5 y 55 caracteres"

if not cls.EMAIL_REGEX.match(email):
return False, "Formato de email inválido"

return True, ""

class IPAddressValidator(Validator):
"""Validador de direcciones IP"""

@classmethod
def validate(cls, ip_address: str) -> Tuple[bool, str]:
"""
Valida una dirección IP
Returns: (is_valid, error_message)
"""
if not cls.is_required(ip_address):
return False, "Dirección IP es requerida"

try:
ipaddress.ip_address(ip_address)
return True, ""
except ValueError:
return False, "Dirección IP inválida"

class MacAddressValidator(Validator):
"""Validador de direcciones MAC"""

MAC_REGEX = re.compile(
r'^([0-9A-Fa-f]{}[:-]){5}([0-9A-Fa-f]{})$'
)

@classmethod
def validate(cls, mac_address: str) -> Tuple[bool, str]:
"""
Valida una dirección MAC
Returns: (is_valid, error_message)
"""
if not cls.is_required(mac_address):
return False, "Dirección MAC es requerida"

if not cls.MAC_REGEX.match(mac_address):
return False, "Formato de dirección MAC inválido (AA:BB:CC:DD:EE:FF)"

return True, ""

class DateValidator(Validator):
"""Validador de fechas"""

@classmethod
def validate(cls, date_value: Union[str, datetime], date_format: str = "%Y-%m-%d") -> Tuple[bool, str]:
"""
Valida una fecha
Returns: (is_valid, error_message)
"""
if isinstance(date_value, datetime):
return True, ""

if not cls.is_required(date_value):
return False, "Fecha es requerida"

try:
datetime.strptime(date_value, date_format)
return True, ""
except ValueError:
return False, f"Formato de fecha inválido. Use {date_format}"

class CameraValidator(Validator):
"""Validador específico para datos de cámaras"""

VALID_TYPES = ['domo', 'bullet', 'ptz', 'fisheye', 'thermal']
VALID_STATES = ['operativa', 'offline', 'mantenimiento', 'error']

@classmethod
def validate_data(cls, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
"""
Valida datos de una cámara
Returns: (is_valid, error_messages)
"""
errors = []

# Validar nombre
if not cls.is_required(data.get('nombre')):
errors.append("Nombre de cámara es requerido")
elif not cls.is_valid_length(data.get('nombre', ''), 1, 100):
errors.append("Nombre debe tener entre 1 y 100 caracteres")

# Validar IP
if 'ip' in data:
is_valid, error = IPAddressValidator.validate(data['ip'])
if not is_valid:
errors.append(error)

# Validar tipo
if 'tipo' in data:
if data['tipo'] not in cls.VALID_TYPES:
errors.append(f"Tipo debe ser uno de: {', '.join(cls.VALID_TYPES)}")

# Validar estado
if 'estado' in data:
if data['estado'] not in cls.VALID_STATES:
errors.append(f"Estado debe ser uno de: {', '.join(cls.VALID_STATES)}")

# Validar puerto (si está presente)
if 'puerto' in data:
try:
port = int(data['puerto'])
if not cls.is_in_range(port, 1, 65535):
errors.append("Puerto debe estar entre 1 y 65535")
except (ValueError, TypeError):
errors.append("Puerto debe ser un número entero")

# Validar coordenadas (si están presentes)
if 'latitud' in data:
try:
lat = float(data['latitud'])
if not cls.is_in_range(lat, -90, 90):
errors.append("Latitud debe estar entre -90 y 90")
except (ValueError, TypeError):
errors.append("Latitud debe ser un número")

if 'longitud' in data:
try:
lng = float(data['longitud'])
if not cls.is_in_range(lng, -180, 180):
errors.append("Longitud debe estar entre -180 y 180")
except (ValueError, TypeError):
errors.append("Longitud debe ser un número")

# Validar fecha de instalación (si está presente)
if 'fecha_instalacion' in data:
is_valid, error = DateValidator.validate(data['fecha_instalacion'])
if not is_valid:
errors.append(error)

return len(errors) == 0, errors

class UserValidator(Validator):
"""Validador específico para datos de usuarios"""

VALID_ROLES = ['admin', 'tecnico', 'usuario']
VALID_STATES = [True, False]

@classmethod
def validate_data(cls, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
"""
Valida datos de un usuario
Returns: (is_valid, error_messages)
"""
errors = []

# Validar email
if 'email' in data:
is_valid, error = EmailValidator.validate(data['email'])
if not is_valid:
errors.append(error)

# Validar nombre
if 'nombre' in data:
if not cls.is_required(data['nombre']):
errors.append("Nombre es requerido")
elif not cls.is_valid_length(data['nombre'], 1, 50):
errors.append("Nombre debe tener entre 1 y 50 caracteres")

# Validar apellido
if 'apellido' in data:
if not cls.is_required(data['apellido']):
errors.append("Apellido es requerido")
elif not cls.is_valid_length(data['apellido'], 1, 50):
errors.append("Apellido debe tener entre 1 y 50 caracteres")

# Validar rol
if 'rol' in data:
if data['rol'] not in cls.VALID_ROLES:
errors.append(f"Rol debe ser uno de: {', '.join(cls.VALID_ROLES)}")

# Validar estado activo
if 'activo' in data:
if data['activo'] not in cls.VALID_STATES:
errors.append("Estado activo debe ser true o false")

return len(errors) == 0, errors

class FailureValidator(Validator):
"""Validador específico para datos de fallas"""

VALID_SEVERITIES = ['baja', 'media', 'alta', 'critica']
VALID_STATES = ['abierta', 'en_progreso', 'cerrada', 'cancelada']

@classmethod
def validate_data(cls, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
"""
Valida datos de una falla
Returns: (is_valid, error_messages)
"""
errors = []

# Validar título
if not cls.is_required(data.get('titulo')):
errors.append("Título de falla es requerido")
elif not cls.is_valid_length(data.get('titulo', ''), 5, 00):
errors.append("Título debe tener entre 5 y 00 caracteres")

# Validar descripción
if not cls.is_required(data.get('descripcion')):
errors.append("Descripción de falla es requerida")
elif not cls.is_valid_length(data.get('descripcion', ''), 10, 1000):
errors.append("Descripción debe tener entre 10 y 1000 caracteres")

# Validar severidad
if 'severidad' in data:
if data['severidad'] not in cls.VALID_SEVERITIES:
errors.append(f"Severidad debe ser una de: {', '.join(cls.VALID_SEVERITIES)}")

# Validar estado
if 'estado' in data:
if data['estado'] not in cls.VALID_STATES:
errors.append(f"Estado debe ser uno de: {', '.join(cls.VALID_STATES)}")

# Validar fechas
if 'fecha_reporte' in data:
is_valid, error = DateValidator.validate(data['fecha_reporte'])
if not is_valid:
errors.append(error)

if 'fecha_solucion' in data and data['fecha_solucion']:
is_valid, error = DateValidator.validate(data['fecha_solucion'])
if not is_valid:
errors.append(error)

# Validar que fecha_solucion sea posterior a fecha_reporte
if 'fecha_reporte' in data:
try:
reporte = datetime.strptime(data['fecha_reporte'], "%Y-%m-%d")
solucion = datetime.strptime(data['fecha_solucion'], "%Y-%m-%d")
if solucion <= reporte:
errors.append("Fecha de solución debe ser posterior a fecha de reporte")
except ValueError:
pass # Los errores de formato ya fueron validados

return len(errors) == 0, errors

class FileValidator(Validator):
"""Validador para archivos"""

VALID_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'}
VALID_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'csv', 'xlsx', 'xls'}

@classmethod
def validate_image_file(cls, filename: str, max_size: int = 10 * 104 * 104) -> Tuple[bool, str]:
"""
Valida un archivo de imagen
Returns: (is_valid, error_message)
"""
if not cls.is_required(filename):
return False, "Nombre de archivo es requerido"

# Verificar extensión
extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
if extension not in cls.VALID_IMAGE_EXTENSIONS:
return False, f"Extensión no válida. Permitidas: {', '.join(cls.VALID_IMAGE_EXTENSIONS)}"

return True, ""

@classmethod
def validate_document_file(cls, filename: str) -> Tuple[bool, str]:
"""
Valida un archivo de documento
Returns: (is_valid, error_message)
"""
if not cls.is_required(filename):
return False, "Nombre de archivo es requerido"

# Verificar extensión
extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
if extension not in cls.VALID_DOCUMENT_EXTENSIONS:
return False, f"Extensión no válida. Permitidas: {', '.join(cls.VALID_DOCUMENT_EXTENSIONS)}"

return True, ""

class JSONValidator(Validator):
"""Validador para datos JSON"""

@classmethod
def validate_json_data(cls, json_string: str) -> Tuple[bool, str, Dict]:
"""
Valida y parsea una cadena JSON
Returns: (is_valid, error_message, parsed_data)
"""
try:
data = json.loads(json_string)
return True, "", data
except json.JSONDecodeError as e:
return False, f"JSON inválido: {str(e)}", {}

# Funciones de utilidad para validación rápida
def validate_email(email: str) -> bool:
"""Valida una dirección de email de forma rápida"""
is_valid, _ = EmailValidator.validate(email)
return is_valid

def validate_ip_address(ip: str) -> bool:
"""Valida una dirección IP de forma rápida"""
is_valid, _ = IPAddressValidator.validate(ip)
return is_valid

def validate_camera_data(data: Dict[str, Any]) -> List[str]:
"""Valida datos de cámara y retorna lista de errores"""
is_valid, errors = CameraValidator.validate_data(data)
return errors

def validate_user_data(data: Dict[str, Any]) -> List[str]:
"""Valida datos de usuario y retorna lista de errores"""
is_valid, errors = UserValidator.validate_data(data)
return errors

def validate_failure_data(data: Dict[str, Any]) -> List[str]:
"""Valida datos de falla y retorna lista de errores"""
is_valid, errors = FailureValidator.validate_data(data)
return errors

# Flask-specific validation functions that return JSON responses
def validate_json(data) -> tuple[bool, dict]:
    """
    Validates if data is valid JSON or can be parsed as JSON.
    Returns: (is_valid, response_dict)
    If invalid, returns a JSON-ready error response.
    If valid, returns {'success': True}
    """
    try:
        if hasattr(data, 'get_json'):
            # Flask request object
            json_data = data.get_json()
            if json_data is None:
                return False, {
                    'success': False,
                    'error': 'Invalid JSON in request body',
                    'message': 'Unable to parse JSON data from request'
                }
            return True, {'success': True, 'data': json_data}
        elif isinstance(data, str):
            # JSON string
            parsed = json.loads(data)
            return True, {'success': True, 'data': parsed}
        elif isinstance(data, (dict, list)):
            # Already a dict or list
            return True, {'success': True, 'data': data}
        else:
            return False, {
                'success': False,
                'error': 'Invalid data type',
                'message': 'Data must be JSON serializable (dict, list, str, or Flask request)'
            }
    except (json.JSONDecodeError, TypeError) as e:
        return False, {
            'success': False,
            'error': 'JSON validation failed',
            'message': f'Unable to parse data as JSON: {str(e)}'
        }


def validate_required_fields(data: Union[Dict, Any], fields: List[str]) -> tuple[bool, dict]:
    """
    Validates that all required fields are present and not None/empty in the data.
    Returns: (is_valid, response_dict)
    If invalid, returns a JSON-ready error response with missing fields.
    If valid, returns {'success': True}
    
    Args:
        data: Dictionary-like object or Flask request
        fields: List of required field names
    """
    # Handle Flask request objects
    if hasattr(data, 'get_json'):
        json_data = data.get_json()
        if json_data is None:
            return False, {
                'success': False,
                'error': 'Invalid JSON',
                'message': 'Request contains no valid JSON data'
            }
        data = json_data
    
    # Ensure data is a dictionary
    if not isinstance(data, dict):
        return False, {
            'success': False,
            'error': 'Invalid data type',
            'message': 'Data must be a dictionary'
        }
    
    missing_fields = []
    empty_fields = []
    
    for field in fields:
        if field not in data:
            missing_fields.append(field)
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            empty_fields.append(field)
    
    if missing_fields or empty_fields:
        error_details = {}
        if missing_fields:
            error_details['missing_fields'] = missing_fields
        if empty_fields:
            error_details['empty_fields'] = empty_fields
            
        return False, {
            'success': False,
            'error': 'Missing required fields',
            'message': 'One or more required fields are missing or empty',
            'details': error_details
        }
    
    return True, {'success': True}


def validate_pagination(params: Union[Dict, Any]) -> tuple[bool, dict]:
    """
    Validates pagination parameters (page, per_page, limit, offset).
    Returns: (is_valid, response_dict)
    If invalid, returns a JSON-ready error response.
    If valid, returns {'success': True, 'validated_params': {...}}
    
    Args:
        params: Dictionary-like object or Flask request args
    """
    # Handle Flask request objects
    if hasattr(params, 'args'):
        # Flask request with query parameters
        params = dict(params.args)
    elif hasattr(params, 'get_json'):
        # Flask request with JSON body
        json_data = params.get_json()
        if json_data is None:
            return False, {
                'success': False,
                'error': 'Invalid JSON',
                'message': 'Request contains no valid JSON data'
            }
        params = json_data
    
    # Ensure params is a dictionary
    if not isinstance(params, dict):
        return False, {
            'success': False,
            'error': 'Invalid parameters type',
            'message': 'Parameters must be a dictionary'
        }
    
    validated_params = {}
    errors = []
    
    # Define pagination parameter constraints
    pagination_rules = {
        'page': {'min': 1, 'max': 10000, 'default': 1},
        'per_page': {'min': 1, 'max': 100, 'default': 20},
        'limit': {'min': 1, 'max': 1000, 'default': 50},
        'offset': {'min': 0, 'max': 1000000, 'default': 0}
    }
    
    # Validate pagination parameters
    for param, rules in pagination_rules.items():
        if param in params:
            try:
                value = int(params[param])
                
                if value < rules['min']:
                    errors.append(f"{param} must be at least {rules['min']}")
                elif value > rules['max']:
                    errors.append(f"{param} must not exceed {rules['max']}")
                else:
                    validated_params[param] = value
                    
            except (ValueError, TypeError):
                errors.append(f"{param} must be a valid integer")
        else:
            # Set default values for common parameters
            if param in ['page', 'per_page', 'limit']:
                validated_params[param] = rules['default']
    
    # Special validation: ensure either page+per_page or limit+offset is provided
    has_page_pagination = 'page' in validated_params or 'per_page' in validated_params
    has_offset_pagination = 'limit' in validated_params or 'offset' in validated_params
    
    if not has_page_pagination and not has_offset_pagination:
        # Provide defaults if neither set is present
        if 'page' not in validated_params and 'per_page' not in validated_params:
            validated_params['page'] = pagination_rules['page']['default']
            validated_params['per_page'] = pagination_rules['per_page']['default']
    
    # Validate search parameter if present
    if 'search' in params:
        search_value = str(params['search']).strip()
        if len(search_value) > 255:
            errors.append("search parameter must not exceed 255 characters")
        else:
            validated_params['search'] = search_value
    
    # Validate sort parameters if present
    if 'sort_by' in params:
        sort_value = str(params['sort_by']).strip()
        if len(sort_value) > 50:
            errors.append("sort_by parameter must not exceed 50 characters")
        else:
            validated_params['sort_by'] = sort_value
    
    if 'sort_order' in params:
        sort_order = str(params['sort_order']).lower().strip()
        if sort_order not in ['asc', 'desc', 'ascending', 'descending']:
            errors.append("sort_order must be 'asc', 'desc', 'ascending', or 'descending'")
        else:
            validated_params['sort_order'] = sort_order
    
    if errors:
        return False, {
            'success': False,
            'error': 'Invalid pagination parameters',
            'message': 'One or more pagination parameters are invalid',
            'details': {
                'errors': errors,
                'constraints': {
                    param: f"{rules['min']}-{rules['max']}" 
                    for param, rules in pagination_rules.items()
                }
            }
        }
    
    return True, {
        'success': True,
        'validated_params': validated_params
    }


# Convenience function for Flask route handlers
def validate_flask_request_json(request, required_fields: List[str] = None, 
                               pagination: bool = True) -> tuple[bool, dict]:
    """
    Comprehensive validation for Flask requests.
    Validates JSON data, required fields, and pagination parameters.
    
    Returns: (is_valid, response_dict)
    """
    # Validate JSON
    is_valid_json, json_response = validate_json(request)
    if not is_valid_json:
        return False, json_response
    
    data = json_response['data']
    
    # Validate required fields if specified
    if required_fields:
        is_valid_fields, fields_response = validate_required_fields(data, required_fields)
        if not is_valid_fields:
            return False, fields_response
    
    # Validate pagination if specified
    if pagination:
        # Check if request has query args (for GET requests) or use JSON body (for POST/PUT)
        params = request.args if hasattr(request, 'args') and request.args else data
        is_valid_pagination, pagination_response = validate_pagination(params)
        if not is_valid_pagination:
            return False, pagination_response
    
    return True, {
        'success': True,
        'data': data,
        'validated_params': pagination_response.get('validated_params', {}) if pagination else {}
    }