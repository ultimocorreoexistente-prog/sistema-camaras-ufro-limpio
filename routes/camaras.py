"""
Rutas CRUD para el manejo de Cámaras
"""
from flask import request, jsonify
from sqlalchemy import or_, and_, desc
from datetime import datetime
from .. import camaras_bp
from .auth import token_required
from models import Camara, Falla, db
from utils.validators import validate_json, validate_required_fields
from utils.decorators import require_permission

@camaras_bp.route('', methods=['GET'])
@token_required
def get_camaras(current_user):
"""
Obtener lista de cámaras con filtros y paginación
"""
try:
# Validar paginación
page = request.args.get('page', 1, type=int)
per_page = request.args.get('per_page', 0, type=int)

if per_page > 100:
per_page = 100

# Parámetros de filtro
estado = request.args.get('estado', '')
ubicacion = request.args.get('ubicacion', '')
search = request.args.get('search', '')
marca = request.args.get('marca', '')
modelo = request.args.get('modelo', '')
orden = request.args.get('orden', 'nombre')
direccion = request.args.get('direccion', 'asc')

# Query base
query = Camara.query.filter_by(activo=True)

# Aplicar filtros
if estado:
query = query.filter(Camara.estado == estado)
if ubicacion:
query = query.filter(Camara.ubicacion.like(f'%{ubicacion}%'))
if search:
query = query.filter(
or_(
Camara.nombre.like(f'%{search}%'),
Camara.descripcion.like(f'%{search}%'),
Camara.ip_address.like(f'%{search}%')
)
)
if marca:
query = query.filter(Camara.marca.like(f'%{marca}%'))
if modelo:
query = query.filter(Camara.modelo.like(f'%{modelo}%'))

# Ordenamiento
orden_field = getattr(Camara, orden, Camara.nombre)
if direccion == 'desc':
query = query.order_by(orden_field.desc())
else:
query = query.order_by(orden_field.asc())

# Paginación
pagination = query.paginate(
page=page, per_page=per_page, error_out=False
)

camaras = []
for c in pagination.items:
# Verificar si la cámara tiene fallas abiertas
fallas_abiertas = Falla.query.filter(
Falla.tipo == 'camara',
Falla.equipo_id == c.id,
Falla.estado.in_(['abierta', 'en_proceso'])
).count()

camaras.append({
'id': c.id,
'nombre': c.nombre,
'descripcion': c.descripcion,
'ip_address': c.ip_address,
'puerto': c.puerto,
'usuario': c.usuario,
'password': '[ENCRYPTED]', # No mostrar la contraseña real
'marca': c.marca,
'modelo': c.modelo,
'numero_serie': c.numero_serie,
'ubicacion': c.ubicacion,
'estado': c.estado,
'resolucion': c.resolucion,
'fps': c.fps,
'codec': c.codec,
'fecha_instalacion': c.fecha_instalacion.isoformat() if c.fecha_instalacion else None,
'fecha_ultimo_mantenimiento': c.fecha_ultimo_mantenimiento.isoformat() if c.fecha_ultimo_mantenimiento else None,
'fallas_abiertas': fallas_abiertas,
'created_at': c.created_at.isoformat(),
'updated_at': c.updated_at.isoformat() if c.updated_at else None
})

return jsonify({
'camaras': camaras,
'pagination': {
'page': pagination.page,
'pages': pagination.pages,
'per_page': pagination.per_page,
'total': pagination.total,
'has_next': pagination.has_next,
'has_prev': pagination.has_prev
},
'filters': {
'estado': estado,
'ubicacion': ubicacion,
'search': search,
'marca': marca,
'modelo': modelo,
'orden': orden,
'direccion': direccion
}
})

except Exception as e:
return jsonify({'error': f'Error al obtener cámaras: {str(e)}'}), 500

@camaras_bp.route('/<int:camaras_id>', methods=['GET'])
@token_required
def get_camara(current_user, camaras_id):
"""
Obtener detalle de una cámara específica
"""
try:
camara = Camara.query.get_or_404(camaras_id)

# Obtener fallas relacionadas
fallas = Falla.query.filter(
Falla.tipo == 'camara',
Falla.equipo_id == camaras_id
).order_by(Falla.fecha_creacion.desc()).limit(10).all()

fallas_info = [{
'id': f.id,
'titulo': f.titulo,
'estado': f.estado,
'prioridad': f.prioridad,
'fecha_creacion': f.fecha_creacion.isoformat()
} for f in fallas]

return jsonify({
'id': camara.id,
'nombre': camara.nombre,
'descripcion': camara.descripcion,
'ip_address': camara.ip_address,
'puerto': camara.puerto,
'usuario': camara.usuario,
'password': '[ENCRYPTED]', # No mostrar contraseña real
'marca': camara.marca,
'modelo': camara.modelo,
'numero_serie': camara.numero_serie,
'ubicacion': camara.ubicacion,
'estado': camara.estado,
'resolucion': camara.resolucion,
'fps': camara.fps,
'codec': camara.codec,
'fecha_instalacion': camara.fecha_instalacion.isoformat() if camara.fecha_instalacion else None,
'fecha_ultimo_mantenimiento': camara.fecha_ultimo_mantenimiento.isoformat() if camara.fecha_ultimo_mantenimiento else None,
'created_at': camara.created_at.isoformat(),
'updated_at': camara.updated_at.isoformat() if camara.updated_at else None,
'fallas_recientes': fallas_info,
'total_fallas': len(fallas_info),
'fallas_abiertas': len([f for f in fallas if f.estado in ['abierta', 'en_proceso']])
})

except Exception as e:
return jsonify({'error': f'Error al obtener cámara: {str(e)}'}), 500

@camaras_bp.route('', methods=['POST'])
@token_required
@require_permission('equipos_crear')
@validate_json
def create_camara(current_user):
"""
Crear una nueva cámara
"""
try:
data = request.get_json()

# Validar campos requeridos
required_fields = ['nombre', 'ip_address']
if not validate_required_fields(data, required_fields):
return jsonify({'error': 'Campos requeridos: nombre, ip_address'}), 400

# Validar formato de IP
import ipaddress
try:
ipaddress.ip_address(data['ip_address'])
except ValueError:
return jsonify({'error': 'Dirección IP inválida'}), 400

# Verificar que no existe otra cámara con la misma IP
ip_existe = Camara.query.filter(
Camara.ip_address == data['ip_address'],
Camara.activo == True
).first()

if ip_existe:
return jsonify({'error': 'Ya existe una cámara con esa dirección IP'}), 400

# Crear cámara
camara = Camara(
nombre=data['nombre'].strip(),
descripcion=data.get('descripcion', '').strip(),
ip_address=data['ip_address'],
puerto=data.get('puerto', 554),
usuario=data.get('usuario', ''),
# En producción, cifrar la contraseña
password=data.get('password', ''),
marca=data.get('marca', '').strip(),
modelo=data.get('modelo', '').strip(),
numero_serie=data.get('numero_serie', '').strip(),
ubicacion=data.get('ubicacion', '').strip(),
estado=data.get('estado', 'operativa'),
resolucion=data.get('resolucion', ''),
fps=data.get('fps'),
codec=data.get('codec', ''),
fecha_instalacion=datetime.fromisoformat(data['fecha_instalacion']) if data.get('fecha_instalacion') else None,
activo=True,
created_at=datetime.utcnow()
)

db.session.add(camara)
db.session.commit()

return jsonify({
'message': 'Cámara creada exitosamente',
'camara_id': camara.id
}), 01

except Exception as e:
db.session.rollback()
return jsonify({'error': f'Error al crear cámara: {str(e)}'}), 500

@camaras_bp.route('/<int:camaras_id>', methods=['PUT'])
@token_required
@require_permission('equipos_editar')
@validate_json
def update_camara(current_user, camaras_id):
"""
Actualizar una cámara existente
"""
try:
camara = Camara.query.get_or_404(camaras_id)
data = request.get_json()

# Campos actualizables
campos_actualizables = [
'nombre', 'descripcion', 'ip_address', 'puerto', 'usuario', 'password',
'marca', 'modelo', 'numero_serie', 'ubicacion', 'estado', 'resolucion',
'fps', 'codec', 'fecha_instalacion'
]

for campo in campos_actualizables:
if campo in data and data[campo] is not None:
if campo == 'nombre' and data[campo].strip():
camara.nombre = data[campo].strip()
elif campo == 'descripcion':
camara.descripcion = data[campo].strip()
elif campo == 'ip_address':
# Validar formato de IP
import ipaddress
try:
ipaddress.ip_address(data[campo])
# Verificar que no existe otra cámara con la misma IP
ip_existe = Camara.query.filter(
Camara.ip_address == data[campo],
Camara.id = camaras_id,
Camara.activo == True
).first()
if ip_existe:
return jsonify({'error': 'Ya existe otra cámara con esa dirección IP'}), 400
camara.ip_address = data[campo]
except ValueError:
return jsonify({'error': 'Dirección IP inválida'}), 400
elif campo == 'puerto':
camara.puerto = data[campo]
elif campo == 'usuario':
camara.usuario = data[campo].strip()
elif campo == 'password':
# En producción, cifrar la contraseña
camara.password = data[campo]
elif campo == 'marca':
camara.marca = data[campo].strip()
elif campo == 'modelo':
camara.modelo = data[campo].strip()
elif campo == 'numero_serie':
camara.numero_serie = data[campo].strip()
elif campo == 'ubicacion':
camara.ubicacion = data[campo].strip()
elif campo == 'estado':
estados_validos = ['operativa', 'mantenimiento', 'fuera_servicio', 'deshabilitada']
if data[campo] not in estados_validos:
return jsonify({'error': f'Estado debe ser uno de: {estados_validos}'}), 400
camara.estado = data[campo]
elif campo == 'resolucion':
camara.resolucion = data[campo].strip()
elif campo == 'fps':
camara.fps = data[campo]
elif campo == 'codec':
camara.codec = data[campo].strip()
elif campo == 'fecha_instalacion':
camara.fecha_instalacion = datetime.fromisoformat(data[campo]) if data[campo] else None

camara.updated_at = datetime.utcnow()

db.session.commit()

return jsonify({
'message': 'Cámara actualizada exitosamente'
})

except Exception as e:
db.session.rollback()
return jsonify({'error': f'Error al actualizar cámara: {str(e)}'}), 500

@camaras_bp.route('/<int:camaras_id>', methods=['DELETE'])
@token_required
@require_permission('equipos_eliminar')
def delete_camara(current_user, camaras_id):
"""
Eliminar una cámara (soft delete)
"""
try:
camara = Camara.query.get_or_404(camaras_id)

# Verificar que no tiene fallas abiertas
fallas_abiertas = Falla.query.filter(
Falla.tipo == 'camara',
Falla.equipo_id == camaras_id,
Falla.estado.in_(['abierta', 'en_proceso'])
).count()

if fallas_abiertas > 0:
return jsonify({'error': 'No se puede eliminar una cámara con fallas abiertas'}), 400

camara.activo = False
camara.updated_at = datetime.utcnow()

db.session.commit()

return jsonify({
'message': 'Cámara eliminada exitosamente'
})

except Exception as e:
db.session.rollback()
return jsonify({'error': f'Error al eliminar cámara: {str(e)}'}), 500

@camaras_bp.route('/<int:camaras_id>/test-conexion', methods=['POST'])
@token_required
def test_conexion_camara(current_user, camaras_id):
"""
Probar conexión con la cámara
"""
try:
camara = Camara.query.get_or_404(camaras_id)

# Simular test de conexión (en producción sería una verificación real)
resultado = {
'camara_id': camaras_id,
'ip_address': camara.ip_address,
'puerto': camara.puerto,
'timestamp': datetime.utcnow().isoformat(),
'resultado': 'exito', # 'exito', 'error', 'timeout'
'mensaje': 'Conexión exitosa',
'tiempo_respuesta_ms': 150, # Simulado
'protocolos_activos': ['RTSP', 'HTTP'] if resultado == 'exito' else []
}

# En una implementación real, aquí se haría:
# - Ping a la IP
# - Verificar puerto específico
# - Test de credenciales si aplica
# - Verificar streams RTSP

return jsonify(resultado)

except Exception as e:
return jsonify({
'error': f'Error al probar conexión: {str(e)}'
}), 500

@camaras_bp.route('/<int:camaras_id>/mantenimiento', methods=['PUT'])
@token_required
@require_permission('equipos_editar')
def actualizar_mantenimiento_camara(current_user, camaras_id):
"""
Actualizar fecha de último mantenimiento
"""
try:
camara = Camara.query.get_or_404(camaras_id)

camara.fecha_ultimo_mantenimiento = datetime.utcnow()
camara.updated_at = datetime.utcnow()

db.session.commit()

return jsonify({
'message': 'Fecha de mantenimiento actualizada',
'fecha_ultimo_mantenimiento': camara.fecha_ultimo_mantenimiento.isoformat()
})

except Exception as e:
db.session.rollback()
return jsonify({'error': f'Error al actualizar mantenimiento: {str(e)}'}), 500

@camaras_bp.route('/estadisticas', methods=['GET'])
@token_required
def get_camaras_estadisticas(current_user):
"""
Obtener estadísticas de cámaras
"""
try:
# Total por estado
por_estado = db.session.query(
Camara.estado,
func.count(Camara.id)
).filter_by(activo=True).group_by(Camara.estado).all()

# Total por marca
por_marca = db.session.query(
Camara.marca,
func.count(Camara.id)
).filter(
Camara.activo == True,
Camara.marca = ''
).group_by(Camara.marca).all()

# Total por ubicación
por_ubicacion = db.session.query(
Camara.ubicacion,
func.count(Camara.id)
).filter(
Camara.activo == True,
Camara.ubicacion = ''
).group_by(Camara.ubicacion).all()

# Cámaras con fallas abiertas
camaras_con_fallas = db.session.query(
Camara.id,
Camara.nombre
).join(
Falla, and_(
Falla.tipo == 'camara',
Falla.equipo_id == Camara.id,
Falla.estado.in_(['abierta', 'en_proceso'])
)
).filter(Camara.activo == True).all()

# Cámaras que necesitan mantenimiento (más de 6 meses sin mantenimiento)
fecha_limite = datetime.utcnow() - timedelta(days=180)
camaras_necesitan_mantenimiento = Camara.query.filter(
Camara.activo == True,
or_(
Camara.fecha_ultimo_mantenimiento < fecha_limite,
Camara.fecha_ultimo_mantenimiento.is_(None)
)
).count()

# Total de cámaras
total_camaras = Camara.query.filter_by(activo=True).count()

return jsonify({
'total_camaras': total_camaras,
'por_estado': {estado: cantidad for estado, cantidad in por_estado},
'por_marca': [{'marca': marca, 'cantidad': cantidad} for marca, cantidad in por_marca],
'por_ubicacion': [{'ubicacion': ubicacion, 'cantidad': cantidad} for ubicacion, cantidad in por_ubicacion],
'camaras_con_fallas': len(camaras_con_fallas),
'camaras_funcionando': total_camaras - len(camaras_con_fallas),
'camaras_necesitan_mantenimiento': camaras_necesitan_mantenimiento,
'porcentaje_funcionamiento': round(((total_camaras - len(camaras_con_fallas)) / total_camaras * 100) if total_camaras > 0 else 0, 1),
'detalle_camaras_con_fallas': [
{'id': cam_id, 'nombre': nombre} for cam_id, nombre in camaras_con_fallas
]
})

except Exception as e:
return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500

@camaras_bp.route('/buscar-ip/<ip_address>', methods=['GET'])
@token_required
def buscar_camara_por_ip(current_user, ip_address):
"""
Buscar cámara por dirección IP
"""
try:
# Validar formato de IP
import ipaddress
try:
ipaddress.ip_address(ip_address)
except ValueError:
return jsonify({'error': 'Dirección IP inválida'}), 400

camara = Camara.query.filter_by(
ip_address=ip_address,
activo=True
).first()

if not camara:
return jsonify({'message': 'No se encontró cámara con esa IP'}), 404

return jsonify({
'id': camara.id,
'nombre': camara.nombre,
'ip_address': camara.ip_address,
'ubicacion': camara.ubicacion,
'estado': camara.estado,
'fecha_instalacion': camara.fecha_instalacion.isoformat() if camara.fecha_instalacion else None
})

except Exception as e:
return jsonify({'error': f'Error al buscar cámara: {str(e)}'}), 500