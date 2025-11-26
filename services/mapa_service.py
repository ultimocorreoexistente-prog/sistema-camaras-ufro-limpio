# services/mapa_service.py
"""
Servicio de mapas y geolocalización
Integración con Google Maps API para manejo de ubicaciones
"""

import requests
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import os

class MapaService:
"""Servicio para manejo de mapas y geolocalización"""

def __init__(self, api_key: str = None, db_session=None):
self.api_key = api_key or os.environ.get('GOOGLE_MAPS_API_KEY')
self.base_url = "https://maps.googleapis.com/maps/api"
self.db = db_session

# Centro de la UFRO (ejemplo - ajustar según ubicación real)
self.ufro_center = {
'lat': -38.9531,
'lng': -7.3338
}
self.ufro_bounds = {
'north': -38.9450,
'south': -38.9600,
'east': -7.350,
'west': -7.3400
}

def geocode_address(self, address: str) -> Dict[str, Any]:
"""
Convierte una dirección a coordenadas
"""
if not self.api_key:
return {
'success': False,
'error': 'API Key de Google Maps no configurada'
}

try:
url = f"{self.base_url}/geocode/json"
params = {
'address': address,
'key': self.api_key
}

response = requests.get(url, params=params)
data = response.json()

if data['status'] == 'OK' and data['results']:
result = data['results'][0]
location = result['geometry']['location']

return {
'success': True,
'latitude': location['lat'],
'longitude': location['lng'],
'formatted_address': result['formatted_address'],
'place_id': result['place_id'],
'types': result['types'],
'address_components': result['address_components']
}
else:
return {
'success': False,
'error': data.get('error_message', 'No se pudo geocodificar la dirección')
}

except Exception as e:
return {
'success': False,
'error': f'Error en geocodificación: {str(e)}'
}

def reverse_geocode(self, lat: float, lng: float) -> Dict[str, Any]:
"""
Convierte coordenadas a dirección
"""
if not self.api_key:
return {
'success': False,
'error': 'API Key de Google Maps no configurada'
}

try:
url = f"{self.base_url}/geocode/json"
params = {
'latlng': f"{lat},{lng}",
'key': self.api_key
}

response = requests.get(url, params=params)
data = response.json()

if data['status'] == 'OK' and data['results']:
result = data['results'][0]

return {
'success': True,
'formatted_address': result['formatted_address'],
'place_id': result['place_id'],
'types': result['types'],
'address_components': result['address_components']
}
else:
return {
'success': False,
'error': data.get('error_message', 'No se pudo obtener dirección')
}

except Exception as e:
return {
'success': False,
'error': f'Error en geocodificación inversa: {str(e)}'
}

def calculate_distance(self, origin: Tuple[float, float], destination: Tuple[float, float]) -> Dict[str, Any]:
"""
Calcula distancia entre dos puntos
"""
if not self.api_key:
return {
'success': False,
'error': 'API Key de Google Maps no configurada'
}

try:
url = f"{self.base_url}/distancematrix/json"
params = {
'origins': f"{origin[0]},{origin[1]}",
'destinations': f"{destination[0]},{destination[1]}",
'units': 'metric',
'key': self.api_key
}

response = requests.get(url, params=params)
data = response.json()

if data['status'] == 'OK' and data['rows']:
element = data['rows'][0]['elements'][0]

if element['status'] == 'OK':
return {
'success': True,
'distance': element['distance']['text'],
'duration': element['duration']['text'],
'distance_meters': element['distance']['value'],
'duration_seconds': element['duration']['value']
}
else:
return {
'success': False,
'error': f'No se pudo calcular distancia: {element["status"]}'
}
else:
return {
'success': False,
'error': 'Error en Distance Matrix API'
}

except Exception as e:
return {
'success': False,
'error': f'Error calculando distancia: {str(e)}'
}

def is_within_campus(self, lat: float, lng: float) -> bool:
"""
Verifica si una ubicación está dentro del campus UFRO
"""
bounds = self.ufro_bounds
return (bounds['south'] <= lat <= bounds['north'] and
bounds['west'] <= lng <= bounds['east'])

def get_nearby_places(self, lat: float, lng: float, radius: int = 1000,
place_type: str = None) -> List[Dict[str, Any]]:
"""
Busca lugares cercanos a una ubicación
"""
if not self.api_key:
return []

try:
url = f"{self.base_url}/place/nearbysearch/json"
params = {
'location': f"{lat},{lng}",
'radius': radius,
'key': self.api_key
}

if place_type:
params['type'] = place_type

response = requests.get(url, params=params)
data = response.json()

if data['status'] == 'OK':
return [{
'place_id': place['place_id'],
'name': place['name'],
'latitude': place['geometry']['location']['lat'],
'longitude': place['geometry']['location']['lng'],
'rating': place.get('rating'),
'types': place['types'],
'vicinity': place.get('vicinity', '')
} for place in data['results']]

return []

except Exception as e:
print(f"Error buscando lugares cercanos: {e}")
return []

def generate_static_map_url(self, center: Tuple[float, float], zoom: int = 15,
size: str = "600x400", markers: List[Dict] = None) -> str:
"""
Genera URL para mapa estático de Google
"""
if not self.api_key:
return ""

base_url = f"{self.base_url}/staticmap"
params = {
'center': f"{center[0]},{center[1]}",
'zoom': zoom,
'size': size,
'key': self.api_key
}

# Agregar marcadores
if markers:
marker_parts = []
for marker in markers:
lat = marker.get('lat')
lng = marker.get('lng')
color = marker.get('color', 'red')
label = marker.get('label', '')

if lat and lng:
marker_str = f"color:{color}"
if label:
marker_str += f"|label:{label}"
marker_str += f"|{lat},{lng}"
marker_parts.append(marker_str)

if marker_parts:
params['markers'] = marker_parts

# Construir URL
query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
return f"{base_url}?{query_string}"

def save_location(self, nombre: str, lat: float, lng: float,
description: str = None, tipo: str = 'general') -> int:
"""
Guarda una ubicación en la base de datos
"""
try:
# Verificar si ya existe
existing = self.db.execute(
"SELECT id FROM ubicaciones WHERE nombre = %s", (nombre,)
).fetchone()

if existing:
# Actualizar
self.db.execute(
"UPDATE ubicaciones SET lat = %s, lng = %s, description = %s, "
"tipo = %s, updated_at = %s WHERE id = %s",
(lat, lng, description, tipo, datetime.now(), existing.id)
)
self.db.commit()
return existing.id
else:
# Crear nueva
result = self.db.execute(
"INSERT INTO ubicaciones (nombre, lat, lng, description, tipo, created_at) "
"VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
(nombre, lat, lng, description, tipo, datetime.now())
)
self.db.commit()
return result.fetchone()[0]

except Exception as e:
print(f"Error guardando ubicación: {e}")
self.db.rollback()
return 0

def get_locations(self, tipo: str = None) -> List[Dict[str, Any]]:
"""
Obtiene ubicaciones guardadas
"""
try:
query = "SELECT * FROM ubicaciones"
params = []

if tipo:
query += " WHERE tipo = %s"
params.append(tipo)

query += " ORDER BY nombre"

results = self.db.execute(query, params).fetchall()

return [{
'id': row.id,
'nombre': row.nombre,
'lat': row.lat,
'lng': row.lng,
'description': row.description,
'tipo': row.tipo,
'created_at': row.created_at,
'updated_at': row.updated_at
} for row in results]

except Exception as e:
print(f"Error obteniendo ubicaciones: {e}")
return []

def get_cameras_map_data(self) -> List[Dict[str, Any]]:
"""
Obtiene datos de cámaras para mostrar en mapa
"""
try:
results = self.db.execute(
"""
SELECT c.id, c.nombre, c.ip, c.latitud, c.longitud,
c.estado, c.fecha_instalacion,
l.nombre as ubicacion
FROM camaras c
LEFT JOIN ubicaciones l ON c.ubicacion_id = l.id
WHERE c.latitud IS NOT NULL AND c.longitud IS NOT NULL
ORDER BY c.nombre
"""
).fetchall()

return [{
'id': row.id,
'nombre': row.nombre,
'ip': row.ip,
'latitude': row.latitud,
'longitude': row.longitud,
'estado': row.estado,
'ubicacion': row.ubicacion,
'fecha_instalacion': row.fecha_instalacion,
'marker_color': 'green' if row.estado == 'operativa' else 'red'
} for row in results]

except Exception as e:
print(f"Error obteniendo datos de cámaras: {e}")
return []

def calculate_route(self, origin: Tuple[float, float],
destination: Tuple[float, float]) -> Dict[str, Any]:
"""
Calcula ruta entre dos puntos
"""
if not self.api_key:
return {
'success': False,
'error': 'API Key de Google Maps no configurada'
}

try:
url = f"{self.base_url}/directions/json"
params = {
'origin': f"{origin[0]},{origin[1]}",
'destination': f"{destination[0]},{destination[1]}",
'mode': 'driving',
'key': self.api_key
}

response = requests.get(url, params=params)
data = response.json()

if data['status'] == 'OK' and data['routes']:
route = data['routes'][0]
leg = route['legs'][0]

return {
'success': True,
'distance': leg['distance']['text'],
'duration': leg['duration']['text'],
'polyline': route['overview_polyline']['points'],
'steps': len(leg['steps'])
}
else:
return {
'success': False,
'error': 'No se pudo calcular ruta'
}

except Exception as e:
return {
'success': False,
'error': f'Error calculando ruta: {str(e)}'
}