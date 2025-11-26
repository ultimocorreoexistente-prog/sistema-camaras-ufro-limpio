# services/foto_service.py
"""
Servicio para manejo de fotografías y archivos
Procesa, guarda, valida y administra archivos de imágenes
"""

import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from PIL import Image
import hashlib
from werkzeug.utils import secure_filename

class FotoService:
"""Servicio para manejar fotografías y archivos"""

def __init__(self, upload_folder: str = 'uploads', db_session=None):
self.upload_folder = upload_folder
self.db = db_session
self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
self.max_file_size = 10 * 104 * 104 # 10MB
self.thumbnail_size = (300, 300)

def validate_file(self, file) -> Dict[str, Any]:
"""
Valida un archivo subido
"""
result = {'valid': True, 'error': None}

# Verificar extensión
if '.' not in file.filename:
result.update({'valid': False, 'error': 'Archivo sin extensión'})
return result

extension = file.filename.rsplit('.', 1)[1].lower()
if extension not in self.allowed_extensions:
result.update({
'valid': False,
'error': f'Extensión no permitida. Permitidas: {", ".join(self.allowed_extensions)}'
})
return result

# Verificar tamaño
file.seek(0, os.SEEK_END)
file_size = file.tell()
file.seek(0)

if file_size > self.max_file_size:
result.update({
'valid': False,
'error': f'Archivo demasiado grande. Máximo: {self.max_file_size // (104*104)}MB'
})
return result

return result

def save_file(self, file, categoria: str = 'general', metadata: Dict = None) -> Dict[str, Any]:
"""
Guarda un archivo y retorna información del mismo
"""
# Validar archivo
validation = self.validate_file(file)
if not validation['valid']:
return validation

try:
# Generar nombre único
original_filename = secure_filename(file.filename)
file_extension = original_filename.rsplit('.', 1)[1].lower()
unique_filename = f"{uuid.uuid4().hex}.{file_extension}"

# Crear directorios si no existen
categoria_folder = os.path.join(self.upload_folder, categoria)
os.makedirs(categoria_folder, exist_ok=True)

# Guardar archivo original
file_path = os.path.join(categoria_folder, unique_filename)
file.save(file_path)

# Generar metadatos
file_hash = self._calculate_file_hash(file_path)
file_info = self._get_image_info(file_path)

# Crear thumbnail
thumbnail_path = self._create_thumbnail(file_path)

# Guardar información en base de datos
foto_id = self._save_foto_metadata(
filename=unique_filename,
original_filename=original_filename,
file_path=file_path,
thumbnail_path=thumbnail_path,
categoria=categoria,
file_size=os.path.getsize(file_path),
file_hash=file_hash,
mime_type=file_info['mime_type'],
dimensions=file_info['dimensions'],
metadata=metadata or {}
)

return {
'success': True,
'foto_id': foto_id,
'filename': unique_filename,
'original_filename': original_filename,
'file_path': file_path,
'thumbnail_path': thumbnail_path,
'file_size': file_info['size'],
'dimensions': file_info['dimensions'],
'mime_type': file_info['mime_type'],
'hash': file_hash,
'categoria': categoria
}

except Exception as e:
return {
'valid': False,
'error': f'Error guardando archivo: {str(e)}'
}

def _calculate_file_hash(self, file_path: str) -> str:
"""
Calcula el hash MD5 de un archivo
"""
hash_md5 = hashlib.md5()
with open(file_path, "rb") as f:
for chunk in iter(lambda: f.read(4096), b""):
hash_md5.update(chunk)
return hash_md5.hexdigest()

def _get_image_info(self, file_path: str) -> Dict[str, Any]:
"""
Obtiene información de una imagen
"""
try:
with Image.open(file_path) as img:
return {
'size': os.path.getsize(file_path),
'dimensions': img.size,
'mode': img.mode,
'format': img.format,
'mime_type': f"image/{img.format.lower() if img.format else 'jpeg'}"
}
except Exception as e:
return {
'size': os.path.getsize(file_path),
'dimensions': (0, 0),
'mode': 'Unknown',
'format': 'Unknown',
'mime_type': 'application/octet-stream'
}

def _create_thumbnail(self, file_path: str) -> Optional[str]:
"""
Crea un thumbnail de la imagen
"""
try:
thumbnail_dir = os.path.join(os.path.dirname(file_path), 'thumbnails')
os.makedirs(thumbnail_dir, exist_ok=True)

original_filename = os.path.basename(file_path)
name, ext = os.path.splitext(original_filename)
thumbnail_filename = f"{name}_thumb{ext}"
thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)

with Image.open(file_path) as img:
img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
img.save(thumbnail_path, optimize=True, quality=85)

return thumbnail_path

except Exception as e:
print(f"Error creando thumbnail: {e}")
return None

def _save_foto_metadata(self, **kwargs) -> int:
"""
Guarda metadatos de la foto en la base de datos
"""
try:
query = """
INSERT INTO fotografias (
filename, original_filename, file_path, thumbnail_path,
categoria, file_size, file_hash, mime_type,
width, height, metadata, created_at
) VALUES (%(filename)s, %(original_filename)s, %(file_path)s,
%(thumbnail_path)s, %(categoria)s, %(file_size)s,
%(file_hash)s, %(mime_type)s, %(width)s, %(height)s,
%(metadata)s, %(created_at)s)
RETURNING id
"""

data = {
'filename': kwargs['filename'],
'original_filename': kwargs['original_filename'],
'file_path': kwargs['file_path'],
'thumbnail_path': kwargs['thumbnail_path'],
'categoria': kwargs['categoria'],
'file_size': kwargs['file_size'],
'file_hash': kwargs['file_hash'],
'mime_type': kwargs['mime_type'],
'width': kwargs['dimensions'][0],
'height': kwargs['dimensions'][1],
'metadata': kwargs.get('metadata', {}),
'created_at': datetime.now()
}

result = self.db.execute(query, data)
self.db.commit()
return result.fetchone()[0]

except Exception as e:
self.db.rollback()
raise Exception(f"Error guardando metadatos: {e}")

def get_foto(self, foto_id: int) -> Optional[Dict[str, Any]]:
"""
Obtiene información de una foto por ID
"""
try:
result = self.db.execute(
"SELECT * FROM fotografias WHERE id = %s", (foto_id,)
).fetchone()

if result:
return {
'id': result.id,
'filename': result.filename,
'original_filename': result.original_filename,
'file_path': result.file_path,
'thumbnail_path': result.thumbnail_path,
'categoria': result.categoria,
'file_size': result.file_size,
'file_hash': result.file_hash,
'mime_type': result.mime_type,
'width': result.width,
'height': result.height,
'metadata': result.metadata,
'created_at': result.created_at
}
return None

except Exception as e:
print(f"Error obteniendo foto: {e}")
return None

def list_fotos(self, categoria: str = None, limit: int = 50) -> List[Dict[str, Any]]:
"""
Lista fotografías con filtros opcionales
"""
try:
query = "SELECT * FROM fotografias"
params = []

if categoria:
query += " WHERE categoria = %s"
params.append(categoria)

query += " ORDER BY created_at DESC LIMIT %s"
params.append(limit)

results = self.db.execute(query, params).fetchall()

return [{
'id': row.id,
'filename': row.filename,
'original_filename': row.original_filename,
'categoria': row.categoria,
'file_size': row.file_size,
'width': row.width,
'height': row.height,
'created_at': row.created_at
} for row in results]

except Exception as e:
print(f"Error listando fotos: {e}")
return []

def delete_foto(self, foto_id: int) -> bool:
"""
Elimina una foto y sus archivos asociados
"""
try:
foto = self.get_foto(foto_id)
if not foto:
return False

# Eliminar archivos del sistema
files_to_delete = [
foto['file_path'],
foto['thumbnail_path']
]

for file_path in files_to_delete:
if file_path and os.path.exists(file_path):
os.remove(file_path)

# Eliminar de base de datos
self.db.execute("DELETE FROM fotografias WHERE id = %s", (foto_id,))
self.db.commit()

return True

except Exception as e:
print(f"Error eliminando foto: {e}")
self.db.rollback()
return False

def search_fotos(self, query: str, categoria: str = None) -> List[Dict[str, Any]]:
"""
Busca fotos por texto en metadatos o nombre
"""
try:
sql_query = """
SELECT * FROM fotografias
WHERE (original_filename ILIKE %s OR metadata::text ILIKE %s)
"""
params = [f"%{query}%", f"%{query}%"]

if categoria:
sql_query += " AND categoria = %s"
params.append(categoria)

sql_query += " ORDER BY created_at DESC"

results = self.db.execute(sql_query, params).fetchall()

return [{
'id': row.id,
'filename': row.filename,
'original_filename': row.original_filename,
'categoria': row.categoria,
'created_at': row.created_at
} for row in results]

except Exception as e:
print(f"Error buscando fotos: {e}")
return []