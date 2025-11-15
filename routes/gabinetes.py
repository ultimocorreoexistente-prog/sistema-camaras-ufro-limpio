"""
Rutas CRUD para el manejo de Gabinetes
"""
from flask import request, jsonify
from sqlalchemy import or_, and_, desc, func
from datetime import datetime, timedelta
from .. import gabinetes_bp
from .auth import token_required
from models import Gabinete, Falla, db
from utils.validators import validate_json, validate_required_fields
from utils.decorators import require_permission

@gabinetes_bp.route('', methods=['GET'])
@token_required
def get_gabinetes(current_user):
"""
Obtener lista de gabinetes con filtros y paginación
"""
try:
page = request.args.get('page', 1, type=int)
per_page = request.args.get('per_page', 0, type=int)

if per_page > 100:
per_page = 100

query = Gabinete.query.filter_by(activo=True)

# Aplicar filtros
estado = request.args.get('estado', '')
ubicacion = request.args.get('ubicacion', '')
search = request.args.get('search', '')
tipo = request.args.get('tipo', '') # rack, pared, suelo
altura = request.args.get('altura', '') # en U

if estado:
query = query.filter(Gabinete.estado == estado)
if ubicacion:
query = query.filter(Gabinete.ubicacion.like(f'%{ubicacion}%'))
if search:
query = query.filter(
or_(
Gabinete.nombre.like(f'%{search}%'),
Gabinete.descripcion.like(f'%{search}%')
)
)
if tipo:
query = query.filter(Gabinete.tipo == tipo)
if altura:
try:
altura_u = int(altura)
query = query.filter(Gabinete.altura_u >= altura_u)
except ValueError:
pass

# Ordenamiento
orden = request.args.get('orden', 'nombre')
direccion = request.args.get('direccion', 'asc')
orden_field = getattr(Gabinete, orden, Gabinete.nombre)
if direccion == 'desc':
query = query.order_by(orden_field.desc())
else:
query = query.order_by(orden_field.asc())

pagination = query.paginate(page=page, per_page=per_page, error_out=False)

gabinetes_list = []
for g in pagination.items:
fallas_abiertas = Falla.query.filter(
Falla.tipo == 'gabinete',
Falla.equipo_id == g.id,
Falla.estado.in_(['abierta', 'en_proceso'])
).count()

gabinetes_list.append({
'id': g.id,
'nombre': g.nombre,
'descripcion': g.descripcion,
'tipo': g.tipo,
'ubicacion': g.ubicacion,
'estado': g.estado,
'altura_u': g.altura_u,
'anchura_mm': g.anchura_mm,
'profundidad_mm': g.profundidad_mm,
'capacidad_kg': g.capacidad_kg,
'puertas': g.puertas,
'ventilacion': g.ventilacion,
'fecha_instalacion': g.fecha_instalacion.isoformat() if g.fecha_instalacion else None,
'fecha_ultimo_mantenimiento': g.fecha_ultimo_mantenimiento.isoformat() if g.fecha_ultimo_mantenimiento else None,
'temperatura_actual': getattr(g, 'temperatura_actual', ),
'humedad_actual': getattr(g, 'humedad_actual', 45),
'espacios_ocupados': getattr(g, 'espacios_ocupados', 0),
'fallas_abiertas': fallas_abiertas,
'porcentaje_ocupacion': round((getattr(g, 'espacios_ocupados', 0) / g.altura_u * 100) if g.altura_u > 0 else 0, 1),
'created_at': g.created_at.isoformat()
})

return jsonify({
'gabinetes': gabinetes_list,
'pagination': {
'page': pagination.page,
'pages': pagination.pages,
'per_page': pagination.per_page,
'total': pagination.total,
'has_next': pagination.has_next,
'has_prev': pagination.has_prev
}
})

except Exception as e:
return jsonify({'error': f'Error al obtener gabinetes: {str(e)}'}), 500

@gabinetes_bp.route('/<int:gabinete_id>', methods=['GET'])
@token_required
def get_gabinete_detail(current_user, gabinete_id):
"""
Obtener detalle de un gabinete específico
"""
try:
gabinete = Gabinete.query.get_or_404(gabinete_id)

fallas = Falla.query.filter(
Falla.tipo == 'gabinete',
Falla.equipo_id == gabinete_id
).order_by(Falla.fecha_creacion.desc()).limit(10).all()

fallas_info = [{
'id': f.id,
'titulo': f.titulo,
'estado': f.estado,
'prioridad': f.prioridad,
'fecha_creacion': f.fecha_creacion.isoformat()
} for f in fallas]

return jsonify({
'id': gabinete.id,
'nombre': gabinete.nombre,
'descripcion': gabinete.descripcion,
'tipo': gabinete.tipo,
'ubicacion': gabinete.ubicacion,
'estado': gabinete.estado,
'altura_u': gabinete.altura_u,
'anchura_mm': gabinete.anchura_mm,
'profundidad_mm': gabinete.profundidad_mm,
'capacidad_kg': gabinete.capacidad_kg,
'puertas': gabinete.puertas,
'ventilacion': gabinete.ventilacion,
'fecha_instalacion': gabinete.fecha_instalacion.isoformat() if gabinete.fecha_instalacion else None,
'fecha_ultimo_mantenimiento': gabinete.fecha_ultimo_mantenimiento.isoformat() if gabinete.fecha_ultimo_mantenimiento else None,
'temperatura_actual': getattr(gabinete, 'temperatura_actual', ),
'humedad_actual': getattr(gabinete, 'humedad_actual', 45),
'espacios_ocupados': getattr(gabinete, 'espacios_ocupados', 0),
'equipos_instalados': getattr(gabinete, 'equipos_instalados', []),
'fallas_recientes': fallas_info,
'total_fallas': len(fallas_info)
})

except Exception as e:
return jsonify({'error': f'Error al obtener gabinete: {str(e)}'}), 500

@gabinetes_bp.route('', methods=['POST'])
@token_required
@require_permission('equipos_crear')
@validate_json
def create_gabinete(current_user):
"""
Crear un nuevo gabinete
"""
try:
data = request.get_json()

required_fields = ['nombre']
if not validate_required_fields(data, required_fields):
return jsonify({'error': 'Campo requerido: nombre'}), 400

gabinete = Gabinete(
nombre=data['nombre'].strip(),
descripcion=data.get('descripcion', '').strip(),
tipo=data.get('tipo', 'rack'), # rack, pared, suelo
ubicacion=data.get('ubicacion', '').strip(),
estado=data.get('estado', 'disponible'),
altura_u=data.get('altura_u', 4),
anchura_mm=data.get('anchura_mm', 600),
profundidad_mm=data.get('profundidad_mm', 800),
capacidad_kg=data.get('capacidad_kg', 1000),
puertas=data.get('puertas', ),
ventilacion=data.get('ventilacion', True),
fecha_instalacion=datetime.fromisoformat(data['fecha_instalacion']) if data.get('fecha_instalacion') else None,
activo=True,
created_at=datetime.utcnow()
)

db.session.add(gabinete)
db.session.commit()

return jsonify({
'message': 'Gabinete creado exitosamente',
'gabinete_id': gabinete.id
}), 01

except Exception as e:
db.session.rollback()
return jsonify({'error': f'Error al crear gabinete: {str(e)}'}), 500

@gabinetes_bp.route('/<int:gabinete_id>', methods=['PUT'])
@token_required
@require_permission('equipos_editar')
@validate_json
def update_gabinete(current_user, gabinete_id):
"""
Actualizar un gabinete existente
"""
try:
gabinete = Gabinete.query.get_or_404(gabinete_id)
data = request.get_json()

campos_actualizables = [
'nombre', 'descripcion', 'tipo', 'ubicacion', 'estado',
'altura_u', 'anchura_mm', 'profundidad_mm', 'capacidad_kg',
'puertas', 'ventilacion', 'fecha_instalacion'
]

for campo in campos_actualizables:
if campo in data and data[campo] is not None:
if campo == 'nombre' and data[campo].strip():
gabinete.nombre = data[campo].strip()
else:
setattr(gabinete, campo, data[campo])

gabinete.updated_at = datetime.utcnow()
db.session.commit()

return jsonify({'message': 'Gabinete actualizado exitosamente'})

except Exception as e:
db.session.rollback()
return jsonify({'error': f'Error al actualizar gabinete: {str(e)}'}), 500

@gabinetes_bp.route('/<int:gabinete_id>', methods=['DELETE'])
@token_required
@require_permission('equipos_eliminar')
def delete_gabinete(current_user, gabinete_id):
"""
Eliminar un gabinete (soft delete)
"""
try:
gabinete = Gabinete.query.get_or_404(gabinete_id)

fallas_abiertas = Falla.query.filter(
Falla.tipo == 'gabinete',
Falla.equipo_id == gabinete_id,
Falla.estado.in_(['abierta', 'en_proceso'])
).count()

if fallas_abiertas > 0:
return jsonify({'error': 'No se puede eliminar un gabinete con fallas abiertas'}), 400

gabinete.activo = False
gabinete.updated_at = datetime.utcnow()
db.session.commit()

return jsonify({'message': 'Gabinete eliminado exitosamente'})

except Exception as e:
db.session.rollback()
return jsonify({'error': f'Error al eliminar gabinete: {str(e)}'}), 500

@gabinetes_bp.route('/<int:gabinete_id>/actualizar-ocupacion', methods=['PUT'])
@token_required
@require_permission('equipos_editar')
@validate_json
def actualizar_ocupacion_gabinete(current_user, gabinete_id):
"""
Actualizar espacios ocupados en el gabinete
"""
try:
gabinete = Gabinete.query.get_or_404(gabinete_id)
data = request.get_json()

if 'espacios_ocupados' not in data:
return jsonify({'error': 'espacios_ocupados es requerido'}), 400

espacios_ocupados = data['espacios_ocupados']

if espacios_ocupados < 0 or espacios_ocupados > gabinete.altura_u:
return jsonify({
'error': f'espacios_ocupados debe estar entre 0 y {gabinete.altura_u}'
}), 400

gabinete.espacios_ocupados = espacios_ocupados
gabinete.updated_at = datetime.utcnow()

db.session.commit()

return jsonify({
'message': 'Ocupación actualizada exitosamente',
'espacios_ocupados': gabinete.espacios_ocupados,
'porcentaje_ocupacion': round((gabinete.espacios_ocupados / gabinete.altura_u * 100), 1)
})

except Exception as e:
db.session.rollback()
return jsonify({'error': f'Error al actualizar ocupación: {str(e)}'}), 500

@gabinetes_bp.route('/<int:gabinete_id>/condiciones', methods=['GET'])
@token_required
def get_condiciones_gabinete(current_user, gabinete_id):
"""
Obtener condiciones ambientales del gabinete
"""
try:
gabinete = Gabinete.query.get_or_404(gabinete_id)

# En una implementación real, estos datos vendrían de sensores
condiciones = {
'gabinete_id': gabinete_id,
'timestamp': datetime.utcnow().isoformat(),
'temperatura': getattr(gabinete, 'temperatura_actual', ),
'humedad': getattr(gabinete, 'humedad_actual', 45),
'ventilacion_activa': gabinete.ventilacion,
'estado_puertas': 'cerradas', # Simulado
'alertas': []
}

# Generar alertas según condiciones
if condiciones['temperatura'] > 30:
condiciones['alertas'].append('Temperatura alta')
if condiciones['humedad'] > 70:
condiciones['alertas'].append('Humedad alta')

return jsonify(condiciones)

except Exception as e:
return jsonify({'error': f'Error al obtener condiciones: {str(e)}'}), 500

@gabinetes_bp.route('/<int:gabinete_id>/mantenimiento', methods=['PUT'])
@token_required
@require_permission('equipos_editar')
def actualizar_mantenimiento_gabinete(current_user, gabinete_id):
"""
Actualizar fecha de último mantenimiento
"""
try:
gabinete = Gabinete.query.get_or_404(gabinete_id)

gabinete.fecha_ultimo_mantenimiento = datetime.utcnow()
gabinete.updated_at = datetime.utcnow()

db.session.commit()

return jsonify({
'message': 'Fecha de mantenimiento actualizada',
'fecha_ultimo_mantenimiento': gabinete.fecha_ultimo_mantenimiento.isoformat()
})

except Exception as e:
db.session.rollback()
return jsonify({'error': f'Error al actualizar mantenimiento: {str(e)}'}), 500

@gabinetes_bp.route('/estadisticas', methods=['GET'])
@token_required
def get_gabinetes_estadisticas(current_user):
"""
Obtener estadísticas de gabinetes
"""
try:
total_gabinetes = Gabinete.query.filter_by(activo=True).count()

por_estado = db.session.query(
Gabinete.estado,
func.count(Gabinete.id)
).filter_by(activo=True).group_by(Gabinete.estado).all()

por_tipo = db.session.query(
Gabinete.tipo,
func.count(Gabinete.id)
).filter_by(activo=True).group_by(Gabinete.tipo).all()

por_ubicacion = db.session.query(
Gabinete.ubicacion,
func.count(Gabinete.id)
).filter(Gabinete.activo == True, Gabinete.ubicacion = '').group_by(Gabinete.ubicacion).all()

# Cálculos de ocupación promedio
total_u_disponibles = db.session.query(func.sum(Gabinete.altura_u)).filter(
Gabinete.activo == True
).scalar() or 0

total_u_ocupadas = db.session.query(func.sum(Gabinete.espacios_ocupados)).filter(
Gabinete.activo == True,
Gabinete.espacios_ocupados.isnot(None)
).scalar() or 0

porcentaje_ocupacion_promedio = round((total_u_ocupadas / total_u_disponibles * 100) if total_u_disponibles > 0 else 0, 1)

return jsonify({
'total_gabinetes': total_gabinetes,
'total_u_disponibles': total_u_disponibles,
'total_u_ocupadas': total_u_ocupadas,
'porcentaje_ocupacion_promedio': porcentaje_ocupacion_promedio,
'por_estado': {estado: cantidad for estado, cantidad in por_estado},
'por_tipo': {tipo: cantidad for tipo, cantidad in por_tipo},
'por_ubicacion': [{'ubicacion': ubicacion, 'cantidad': cantidad} for ubicacion, cantidad in por_ubicacion]
})

except Exception as e:
return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500

@gabinetes_bp.route('/buscar-disponibles', methods=['GET'])
@token_required
def buscar_gabinetes_disponibles(current_user):
"""
Buscar gabinetes disponibles para instalar equipos
"""
try:
altura_minima = request.args.get('altura_minima', 1, type=int)
tipo = request.args.get('tipo', '')

query = Gabinete.query.filter(
Gabinete.activo == True,
Gabinete.estado == 'disponible',
Gabinete.altura_u >= altura_minima
)

if tipo:
query = query.filter(Gabinete.tipo == tipo)

gabinetes = query.order_by(Gabinete.altura_u.asc()).all()

resultados = []
for g in gabinetes:
espacios_libres = g.altura_u - getattr(g, 'espacios_ocupados', 0)
if espacios_libres >= altura_minima:
resultados.append({
'id': g.id,
'nombre': g.nombre,
'ubicacion': g.ubicacion,
'tipo': g.tipo,
'altura_u': g.altura_u,
'espacios_libres': espacios_libres,
'porcentaje_ocupacion': round((getattr(g, 'espacios_ocupados', 0) / g.altura_u * 100), 1)
})

return jsonify({
'gabinetes_disponibles': resultados,
'total': len(resultados)
})

except Exception as e:
return jsonify({'error': f'Error al buscar gabinetes disponibles: {str(e)}'}), 500