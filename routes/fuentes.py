"""
Rutas CRUD para el manejo de Fuentes de Alimentación
"""
from flask import request, jsonify
from sqlalchemy import or_, and_, desc, func
from datetime import datetime, timedelta
from .. import fuentes_bp
from .auth import token_required
from models import Fuente, Falla, db
from utils.validators import validate_json, validate_required_fields
from utils.decorators import require_permission

@fuentes_bp.route('', methods=['GET'])
@token_required
def get_fuentes(current_user):
"""
Obtener lista de fuentes de alimentación con filtros y paginación
"""
try:
page = request.args.get('page', 1, type=int)
per_page = request.args.get('per_page', 0, type=int)

if per_page > 100:
per_page = 100

query = Fuente.query.filter_by(activo=True)

# Aplicar filtros
estado = request.args.get('estado', '')
ubicacion = request.args.get('ubicacion', '')
search = request.args.get('search', '')
marca = request.args.get('marca', '')
potencia = request.args.get('potencia', '') # rango de potencia

if estado:
query = query.filter(Fuente.estado == estado)
if ubicacion:
query = query.filter(Fuente.ubicacion.like(f'%{ubicacion}%'))
if search:
query = query.filter(
or_(
Fuente.nombre.like(f'%{search}%'),
Fuente.descripcion.like(f'%{search}%')
)
)
if marca:
query = query.filter(Fuente.marca.like(f'%{marca}%'))
if potencia:
try:
min_potencia, max_potencia = map(int, potencia.split('-'))
query = query.filter(Fuente.potencia_watts >= min_potencia, Fuente.potencia_watts <= max_potencia)
except ValueError:
pass

# Ordenamiento
orden = request.args.get('orden', 'nombre')
direccion = request.args.get('direccion', 'asc')
orden_field = getattr(Fuente, orden, Fuente.nombre)
if direccion == 'desc':
query = query.order_by(orden_field.desc())
else:
query = query.order_by(orden_field.asc())

pagination = query.paginate(page=page, per_page=per_page, error_out=False)

fuentes_list = []
for f in pagination.items:
fallas_abiertas = Falla.query.filter(
Falla.tipo == 'fuente',
Falla.equipo_id == f.id,
Falla.estado.in_(['abierta', 'en_proceso'])
).count()

fuentes_list.append({
'id': f.id,
'nombre': f.nombre,
'descripcion': f.descripcion,
'marca': f.marca,
'modelo': f.modelo,
'numero_serie': f.numero_serie,
'ubicacion': f.ubicacion,
'estado': f.estado,
'potencia_watts': f.potencia_watts,
'voltaje_entrada': f.voltaje_entrada,
'voltaje_salida': f.voltaje_salida,
'amperaje_salida': f.amperaje_salida,
'eficiencia': f.eficiencia,
'fecha_instalacion': f.fecha_instalacion.isoformat() if f.fecha_instalacion else None,
'fecha_ultimo_mantenimiento': f.fecha_ultimo_mantenimiento.isoformat() if f.fecha_ultimo_mantenimiento else None,
'temperatura_actual': getattr(f, 'temperatura_actual', 5),
'fallas_abiertas': fallas_abiertas,
'created_at': f.created_at.isoformat()
})

return jsonify({
'fuentes': fuentes_list,
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
return jsonify({'error': f'Error al obtener fuentes: {str(e)}'}), 500

@fuentes_bp.route('/<int:fuente_id>', methods=['GET'])
@token_required
def get_fuente_detail(current_user, fuente_id):
"""
Obtener detalle de una fuente específica
"""
try:
fuente = Fuente.query.get_or_404(fuente_id)

fallas = Falla.query.filter(
Falla.tipo == 'fuente',
Falla.equipo_id == fuente_id
).order_by(Falla.fecha_creacion.desc()).limit(10).all()

fallas_info = [{
'id': f.id,
'titulo': f.titulo,
'estado': f.estado,
'prioridad': f.prioridad,
'fecha_creacion': f.fecha_creacion.isoformat()
} for f in fallas]

return jsonify({
'id': fuente.id,
'nombre': fuente.nombre,
'descripcion': fuente.descripcion,
'marca': fuente.marca,
'modelo': fuente.modelo,
'numero_serie': fuente.numero_serie,
'ubicacion': fuente.ubicacion,
'estado': fuente.estado,
'potencia_watts': fuente.potencia_watts,
'voltaje_entrada': fuente.voltaje_entrada,
'voltaje_salida': fuente.voltaje_salida,
'amperaje_salida': fuente.amperaje_salida,
'eficiencia': fuente.eficiencia,
'fecha_instalacion': fuente.fecha_instalacion.isoformat() if fuente.fecha_instalacion else None,
'fecha_ultimo_mantenimiento': fuente.fecha_ultimo_mantenimiento.isoformat() if fuente.fecha_ultimo_mantenimiento else None,
'temperatura_actual': getattr(fuente, 'temperatura_actual', 5),
'carga_actual': getattr(fuente, 'carga_actual', 0),
'voltaje_salida_actual': getattr(fuente, 'voltaje_salida_actual', fuente.voltaje_salida),
'fallas_recientes': fallas_info,
'total_fallas': len(fallas_info)
})

except Exception as e:
return jsonify({'error': f'Error al obtener fuente: {str(e)}'}), 500

@fuentes_bp.route('', methods=['POST'])
@token_required
@require_permission('equipos_crear')
@validate_json
def create_fuente(current_user):
"""
Crear una nueva fuente de alimentación
"""
try:
data = request.get_json()

required_fields = ['nombre']
if not validate_required_fields(data, required_fields):
return jsonify({'error': 'Campo requerido: nombre'}), 400

fuente = Fuente(
nombre=data['nombre'].strip(),
descripcion=data.get('descripcion', '').strip(),
marca=data.get('marca', '').strip(),
modelo=data.get('modelo', '').strip(),
numero_serie=data.get('numero_serie', '').strip(),
ubicacion=data.get('ubicacion', '').strip(),
estado=data.get('estado', 'operativa'),
potencia_watts=data.get('potencia_watts', 500),
voltaje_entrada=data.get('voltaje_entrada', 0),
voltaje_salida=data.get('voltaje_salida', 1),
amperaje_salida=data.get('amperaje_salida', 10),
eficiencia=data.get('eficiencia', 85),
fecha_instalacion=datetime.fromisoformat(data['fecha_instalacion']) if data.get('fecha_instalacion') else None,
activo=True,
created_at=datetime.utcnow()
)

db.session.add(fuente)
db.session.commit()

return jsonify({
'message': 'Fuente creada exitosamente',
'fuente_id': fuente.id
}), 01

except Exception as e:
db.session.rollback()
return jsonify({'error': f'Error al crear fuente: {str(e)}'}), 500

@fuentes_bp.route('/<int:fuente_id>', methods=['PUT'])
@token_required
@require_permission('equipos_editar')
@validate_json
def update_fuente(current_user, fuente_id):
"""
Actualizar una fuente existente
"""
try:
fuente = Fuente.query.get_or_404(fuente_id)
data = request.get_json()

campos_actualizables = [
'nombre', 'descripcion', 'marca', 'modelo', 'numero_serie',
'ubicacion', 'estado', 'potencia_watts', 'voltaje_entrada',
'voltaje_salida', 'amperaje_salida', 'eficiencia', 'fecha_instalacion'
]

for campo in campos_actualizables:
if campo in data and data[campo] is not None:
if campo == 'nombre' and data[campo].strip():
fuente.nombre = data[campo].strip()
else:
setattr(fuente, campo, data[campo])

fuente.updated_at = datetime.utcnow()
db.session.commit()

return jsonify({'message': 'Fuente actualizada exitosamente'})

except Exception as e:
db.session.rollback()
return jsonify({'error': f'Error al actualizar fuente: {str(e)}'}), 500

@fuentes_bp.route('/<int:fuente_id>', methods=['DELETE'])
@token_required
@require_permission('equipos_eliminar')
def delete_fuente(current_user, fuente_id):
"""
Eliminar una fuente (soft delete)
"""
try:
fuente = Fuente.query.get_or_404(fuente_id)

fallas_abiertas = Falla.query.filter(
Falla.tipo == 'fuente',
Falla.equipo_id == fuente_id,
Falla.estado.in_(['abierta', 'en_proceso'])
).count()

if fallas_abiertas > 0:
return jsonify({'error': 'No se puede eliminar una fuente con fallas abiertas'}), 400

fuente.activo = False
fuente.updated_at = datetime.utcnow()
db.session.commit()

return jsonify({'message': 'Fuente eliminada exitosamente'})

except Exception as e:
db.session.rollback()
return jsonify({'error': f'Error al eliminar fuente: {str(e)}'}), 500

@fuentes_bp.route('/<int:fuente_id>/test', methods=['POST'])
@token_required
def test_fuente(current_user, fuente_id):
"""
Probar funcionamiento de la fuente
"""
try:
fuente = Fuente.query.get_or_404(fuente_id)

resultado = {
'fuente_id': fuente_id,
'timestamp': datetime.utcnow().isoformat(),
'resultado': 'exito',
'voltaje_entrada': fuente.voltaje_entrada,
'voltaje_salida': getattr(fuente, 'voltaje_salida_actual', fuente.voltaje_salida),
'amperaje_salida': fuente.amperaje_salida,
'temperatura': getattr(fuente, 'temperatura_actual', 30),
'eficiencia_actual': fuente.eficiencia,
'estado': fuente.estado
}

return jsonify(resultado)

except Exception as e:
return jsonify({'error': f'Error al probar fuente: {str(e)}'}), 500

@fuentes_bp.route('/<int:fuente_id>/mantenimiento', methods=['PUT'])
@token_required
@require_permission('equipos_editar')
def actualizar_mantenimiento_fuente(current_user, fuente_id):
"""
Actualizar fecha de último mantenimiento
"""
try:
fuente = Fuente.query.get_or_404(fuente_id)

fuente.fecha_ultimo_mantenimiento = datetime.utcnow()
fuente.updated_at = datetime.utcnow()

db.session.commit()

return jsonify({
'message': 'Fecha de mantenimiento actualizada',
'fecha_ultimo_mantenimiento': fuente.fecha_ultimo_mantenimiento.isoformat()
})

except Exception as e:
db.session.rollback()
return jsonify({'error': f'Error al actualizar mantenimiento: {str(e)}'}), 500

@fuentes_bp.route('/estadisticas', methods=['GET'])
@token_required
def get_fuentes_estadisticas(current_user):
"""
Obtener estadísticas de fuentes
"""
try:
total_fuentes = Fuente.query.filter_by(activo=True).count()

por_estado = db.session.query(
Fuente.estado,
func.count(Fuente.id)
).filter_by(activo=True).group_by(Fuente.estado).all()

por_marca = db.session.query(
Fuente.marca,
func.count(Fuente.id)
).filter(Fuente.activo == True, Fuente.marca = '').group_by(Fuente.marca).all()

por_potencia = db.session.query(
Fuente.potencia_watts,
func.count(Fuente.id)
).filter_by(activo=True).group_by(Fuente.potencia_watts).all()

return jsonify({
'total_fuentes': total_fuentes,
'por_estado': {estado: cantidad for estado, cantidad in por_estado},
'por_marca': [{'marca': marca, 'cantidad': cantidad} for marca, cantidad in por_marca],
'por_potencia': [{'potencia': potencia, 'cantidad': cantidad} for potencia, cantidad in por_potencia]
})

except Exception as e:
return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500