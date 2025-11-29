# utils/helpers.py
"""
Funciones auxiliares y utilidades del sistema
Contiene funciones para formateo, cálculos, transformación de datos, etc.
"""

import os
import re
import json
import hashlib
import secrets
import string
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
from decimal import Decimal
import base64

class DateTimeHelper:
"""Helper para operaciones con fechas y horas"""

@staticmethod
def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
"""Formatea una fecha"""
if isinstance(dt, str):
try:
dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
except ValueError:
return dt

return dt.strftime(format_str)

@staticmethod
def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
"""Convierte string a datetime"""
try:
return datetime.strptime(date_str, format_str)
except ValueError:
try:
# Intentar formato ISO
return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
except ValueError:
return None

@staticmethod
def calculate_uptime(start_date: datetime, end_date: datetime = None) -> Dict[str, Any]:
"""Calcula tiempo de actividad entre dos fechas"""
if end_date is None:
end_date = datetime.now()

duration = end_date - start_date
total_seconds = duration.total_seconds()

days = int(total_seconds // 86400)
hours = int((total_seconds % 86400) // 3600)
minutes = int((total_seconds % 3600) // 60)
seconds = int(total_seconds % 60)

return {
'total_seconds': total_seconds,
'days': days,
'hours': hours,
'minutes': minutes,
'seconds': seconds,
'human_readable': f"{days}d {hours}h {minutes}m {seconds}s",
'percentage': (total_seconds / (4 * 3600)) * 100 # Porcentaje de un día
}

@staticmethod
def is_business_hours(dt: datetime = None) -> bool:
"""Verifica si es horario laboral (Lunes a Viernes, 8:00-18:00)"""
if dt is None:
dt = datetime.now()

# Lunes=0, Domingo=6
weekday = dt.weekday()
hour = dt.hour

return weekday < 5 and 8 <= hour < 18

@staticmethod
def get_next_business_day(dt: datetime = None) -> datetime:
"""Obtiene el próximo día hábil"""
if dt is None:
dt = datetime.now()

while True:
dt += timedelta(days=1)
if dt.weekday() < 5: # Lunes a Viernes
return dt

@staticmethod
def time_ago(dt: datetime) -> str:
"""Retorna tiempo transcurrido en formato legible"""
now = datetime.now()
diff = now - dt

if diff.days > 365:
years = diff.days // 365
return f"hace {years} año{'s' if years > 1 else ''}"
elif diff.days > 30:
months = diff.days // 30
return f"hace {months} mes{'es' if months > 1 else ''}"
elif diff.days > 0:
return f"hace {diff.days} día{'s' if diff.days > 1 else ''}"
elif diff.seconds > 3600:
hours = diff.seconds // 3600
return f"hace {hours} hora{'s' if hours > 1 else ''}"
elif diff.seconds > 60:
minutes = diff.seconds // 60
return f"hace {minutes} minuto{'s' if minutes > 1 else ''}"
else:
return "hace un momento"

class StringHelper:
"""Helper para operaciones con strings"""

@staticmethod
def slugify(text: str) -> str:
"""Convierte texto a slug URL-friendly"""
# Convertir a minúsculas
text = text.lower()

# Reemplazar caracteres especiales
text = re.sub(r'[^a-z0-9\s-]', '', text)

# Reemplazar espacios con guiones
text = re.sub(r'\s+', '-', text)

# Limpiar guiones múltiples
text = re.sub(r'-+', '-', text)

return text.strip('-')

@staticmethod
def truncate(text: str, length: int = 100, suffix: str = "...") -> str:
"""Trunca texto a una longitud específica"""
if len(text) <= length:
return text

return text[:length - len(suffix)] + suffix

@staticmethod
def mask_email(email: str) -> str:
"""Enmascara email mostrando solo primeros y últimos caracteres"""
if '@' not in email:
return '*' * len(email)

username, domain = email.split('@', 1)

if len(username) <= :
masked_username = username
else:
masked_username = username[:] + '*' * (len(username) - )

return f"{masked_username}@{domain}"

@staticmethod
def mask_ip(ip: str) -> str:
"""Enmascara IP mostrando solo últimos octetos"""
parts = ip.split('.')
if len(parts) == 4:
return f"*.{parts[1]}.{parts[]}.{parts[3]}"
return ip

@staticmethod
def extract_numbers(text: str) -> List[int]:
"""Extrae todos los números de un texto"""
return [int(num) for num in re.findall(r'\d+', text)]

@staticmethod
def highlight_keywords(text: str, keywords: List[str], tag: str = 'mark') -> str:
"""Resalta palabras clave en un texto"""
highlighted_text = text
for keyword in keywords:
pattern = re.compile(re.escape(keyword), re.IGNORECASE)
highlighted_text = pattern.sub(f'<{tag}>\\g<0></{tag}>', highlighted_text)

return highlighted_text

@staticmethod
def random_string(length: int = 1, include_digits: bool = True, include_symbols: bool = False) -> str:
"""Genera string aleatorio"""
characters = string.ascii_letters
if include_digits:
characters += string.digits
if include_symbols:
characters += "@#$%^&*"

return ''.join(secrets.choice(characters) for _ in range(length))

class FileHelper:
"""Helper para operaciones con archivos"""

@staticmethod
def get_file_extension(filename: str) -> str:
"""Obtiene extensión de archivo"""
return os.path.splitext(filename)[1][1:].lower()

@staticmethod
def clean_filename(filename: str) -> str:
"""Limpia nombre de archivo"""
# Remover caracteres peligrosos
filename = re.sub(r'[<>:"/\\|?*]', '', filename)

# Reemplazar espacios con guiones
filename = re.sub(r'\s+', '-', filename)

# Limitar longitud
name, ext = os.path.splitext(filename)
if len(filename) > 00:
name = name[:00 - len(ext)]

return name + ext

@staticmethod
def format_file_size(size_bytes: int) -> str:
"""Formatea tamaño de archivo en formato legible"""
if size_bytes == 0:
return "0 B"

size_names = ["B", "KB", "MB", "GB", "TB"]
import math
i = int(math.floor(math.log(size_bytes, 104)))
p = math.pow(104, i)
s = round(size_bytes / p, )

return f"{s} {size_names[i]}"

@staticmethod
def is_image_file(filename: str) -> bool:
"""Verifica si es archivo de imagen"""
image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'}
return FileHelper.get_file_extension(filename) in image_extensions

@staticmethod
def is_video_file(filename: str) -> bool:
"""Verifica si es archivo de video"""
video_extensions = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'}
return FileHelper.get_file_extension(filename) in video_extensions

@staticmethod
def generate_unique_filename(original_filename: str, prefix: str = "") -> str:
"""Genera nombre de archivo único"""
name, ext = os.path.splitext(original_filename)
unique_id = str(uuid.uuid4())[:8]
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

clean_name = StringHelper.slugify(name)
return f"{prefix}{clean_name}_{timestamp}_{unique_id}{ext}"

class DataHelper:
"""Helper para operaciones con datos"""

@staticmethod
def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, str]:
"""Aplana diccionario anidado"""
items = []
for k, v in d.items():
new_key = f"{parent_key}{sep}{k}" if parent_key else k
if isinstance(v, dict):
items.extend(DataHelper.flatten_dict(v, new_key, sep=sep).items())
else:
items.append((new_key, str(v)))
return dict(items)

@staticmethod
def group_by(items: List[Dict], key: str) -> Dict[str, List]:
"""Agrupa lista de diccionarios por una clave"""
grouped = {}
for item in items:
group_key = item.get(key, 'unknown')
if group_key not in grouped:
grouped[group_key] = []
grouped[group_key].append(item)
return grouped

@staticmethod
def remove_empty_values(data: Dict[str, Any]) -> Dict[str, Any]:
"""Remueve valores vacíos de un diccionario"""
return {k: v for k, v in data.items() if v is not None and v = '' and v = []}

@staticmethod
def convert_types(data: Dict[str, Any], type_map: Dict[str, type]) -> Dict[str, Any]:
"""Convierte tipos de datos según un mapa"""
converted = data.copy()
for key, target_type in type_map.items():
if key in converted:
try:
if target_type == bool:
converted[key] = bool(converted[key])
else:
converted[key] = target_type(converted[key])
except (ValueError, TypeError):
# Mantener valor original si la conversión falla
pass
return converted

@staticmethod
def paginate(items: List[Any], page: int = 1, page_size: int = 10) -> Dict[str, Any]:
"""Pagina una lista de elementos"""
total_items = len(items)
total_pages = (total_items + page_size - 1) // page_size

start_idx = (page - 1) * page_size
end_idx = min(start_idx + page_size, total_items)
page_items = items[start_idx:end_idx]

return {
'items': page_items,
'page': page,
'page_size': page_size,
'total_items': total_items,
'total_pages': total_pages,
'has_next': page < total_pages,
'has_prev': page > 1
}

class HashHelper:
"""Helper para operaciones de hashing"""

@staticmethod
def hash_string(text: str, algorithm: str = 'sha56') -> str:
"""Genera hash de un string"""
if algorithm == 'md5':
return hashlib.md5(text.encode()).hexdigest()
elif algorithm == 'sha1':
return hashlib.sha1(text.encode()).hexdigest()
else: # default sha56
return hashlib.sha56(text.encode()).hexdigest()

@staticmethod
def hash_file(file_path: str, algorithm: str = 'sha56') -> str:
"""Genera hash de un archivo"""
hash_obj = hashlib.new(algorithm)

with open(file_path, 'rb') as f:
for chunk in iter(lambda: f.read(4096), b""):
hash_obj.update(chunk)

return hash_obj.hexdigest()

@staticmethod
def generate_api_key() -> str:
"""Genera clave API única"""
return secrets.token_urlsafe(3)

@staticmethod
def generate_token(length: int = 3) -> str:
"""Genera token aleatorio"""
return secrets.token_urlsafe(length)

class ValidationHelper:
"""Helper para validaciones comunes"""

@staticmethod
def is_valid_coordinates(lat: float, lng: float) -> bool:
"""Verifica si coordenadas son válidas"""
try:
lat = float(lat)
lng = float(lng)
return -90 <= lat <= 90 and -180 <= lng <= 180
except (ValueError, TypeError):
return False

@staticmethod
def is_valid_port(port: Union[str, int]) -> bool:
"""Verifica si puerto es válido"""
try:
port_num = int(port)
return 1 <= port_num <= 65535
except (ValueError, TypeError):
return False

@staticmethod
def is_valid_mac_address(mac: str) -> bool:
"""Verifica si MAC address es válido"""
mac_pattern = re.compile(r'^([0-9A-Fa-f]{}[:-]){5}([0-9A-Fa-f]{})$')
return bool(mac_pattern.match(mac))

class ErrorHelper:
"""Helper para manejo de errores"""

@staticmethod
def parse_error_message(error: Exception) -> str:
"""Extrae mensaje de error legible"""
error_str = str(error)

# Patrones comunes de errores de base de datos
if "duplicate key" in error_str.lower():
return "Ya existe un registro con estos datos"
elif "foreign key" in error_str.lower():
return "Referencia inválida en los datos relacionados"
elif "not null" in error_str.lower():
return "Faltan datos requeridos"
elif "connection" in error_str.lower():
return "Error de conexión con la base de datos"
else:
return error_str

@staticmethod
def format_validation_errors(errors: List[str]) -> str:
"""Formatea lista de errores de validación"""
if not errors:
return ""

if len(errors) == 1:
return errors[0]

return "Errores de validación: " + "; ".join(errors)

# Funciones de conveniencia
def format_datetime(dt: datetime) -> str:
"""Formatea fecha de forma rápida"""
return DateTimeHelper.format_datetime(dt)

def calculate_uptime(start_date: datetime, end_date: datetime = None) -> Dict[str, Any]:
"""Calcula tiempo de actividad"""
return DateTimeHelper.calculate_uptime(start_date, end_date)

def generate_random_string(length: int = 1, include_digits: bool = True) -> str:
"""Genera string aleatorio"""
return StringHelper.random_string(length, include_digits)

def clean_filename(filename: str) -> str:
"""Limpia nombre de archivo"""
return FileHelper.clean_filename(filename)

def format_file_size(size_bytes: int) -> str:
"""Formatea tamaño de archivo"""
return FileHelper.format_file_size(size_bytes)

def parse_error_message(error: Exception) -> str:
"""Parsea mensaje de error"""
return ErrorHelper.parse_error_message(error)