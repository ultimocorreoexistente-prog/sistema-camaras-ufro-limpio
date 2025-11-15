"""
Rutas CRUD para el manejo de Switches
"""
from flask import request, jsonify
from sqlalchemy import or_, and_, desc, func
from datetime import datetime, timedelta
from .. import switches_bp
from .auth import token_required
from models import Switch, Falla, db
from utils.validators import validate_json, validate_required_fields
from utils.decorators import require_permission

@switches_bp.route('', methods=['GET'])
@token_required
def get_switches(current_user):
"""
Obtener lista de switches con filtros y paginación
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
tipo = request.args.get('tipo', '') # gestionable, no_gestionable
puertos = request.args.get('puertos', '') # rango de puertos
orden = request.args.get('orden', 'nombre')
direccion = request.args.get('direccion', 'asc')

# Query base
query = Switch.query.filter_by(activo=True)

# Aplicar filtros
if estado:
query = query.filter(Switch.estado == estado)
if ubicacion:
query = query.filter(Switch.ubicacion.like(f'%{ubicacion}%'))
if search:
query = query.filter(
or_(
Switch.nombre.like(f'%{search}%'),
Switch.descripcion.like(f'%{search}%'),
Switch.ip_address.like(f'%{search}%'),
Switch.mac_address.like(f'%{search}%')
)
)
if marca:
query = query.filter(Switch.marca.like(f'%{marca}%'))
if modelo:
query = query.filter(Switch.modelo.like(f'%{modelo}%'))
if tipo:
query = query.filter(Switch.tipo == tipo)
if puertos:
try:
min_puertos, max_puertos = map(int, puertos.split('-'))
query = query.filter(Switch.numero_puertos >= min_puertos, Switch.numero_puertos <= max_puertos)
except ValueError:
pass

# Ordenamiento
orden_field = getattr(Switch, orden, Switch.nombre)
if direccion == 'desc':
query = query.order_by(orden_field.desc())
else:
query = query.order_by(orden_field.asc())

# Paginación
pagination = query.paginate(
page=page, per_page=per_page, error_out=False
)

switches = []
for s in pagination.items:
# Verificar si el switch tiene fallas abiertas
fallas_abiertas = Falla.query.filter(
Falla.tipo == 'switch',
Falla.equipo_id == s.id,
Falla.estado.in_(['abierta', 'en_proceso'])
).count()

# Obtener puertos activos (simulado)
puertos_activos = getattr(s, 'puertos_activos', 0)

switches.append({
'id': s.id,
'nombre': s.nombre,
'descripcion': s.descripcion,
'ip_address': s.ip_address,
'puerto_admin': s.puerto_admin,
'usuario': s.usuario,
'password': '[ENCRYPTED]', # No mostrar la contraseña real
'marca': s.marca,
'modelo': s.modelo,
'numero_serie': s.numero_serie,
'mac_address': s.mac_address,
'ubicacion': s.ubicacion,
'estado': s.estado,
'tipo': s.tipo, # gestionable, no_gestionable
'numero_puertos': s.numero_puertos,
'puertos_activos': puertos_activos,
'velocidad_puertos': getattr(s, 'velocidad_puertos', '10/100/1000 Mbps'),
'poe_habilitado': getattr(s, 'poe_habilitado', False),
'vlans_configuradas': getattr(s, 'vlans_configuradas', 0),
'fecha_instalacion': s.fecha_instalacion.isoformat() if s.fecha_instalacion else None,
'fecha_ultimo_mantenimiento': s.fecha_ultimo_mantenimiento.isoformat() if s.fecha_ultimo_mantenimiento else None,
'fallas_abiertas': fallas_abiertas,
'porcentaje_utilizacion': round((puertos_activos / s.numero_puertos * 100) if s.numero_puertos > 0 else 0, 1),
'created_at': s.created_at.isoformat(),
'updated_at': s.updated_at.isoformat() if s.updated_at else None
})

return jsonify({
'switches': switches,
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
'tipo': tipo,
'puertos': puertos,
'orden': orden,
'direccion': direccion
}
})

except Exception as e:
return jsonify({'error': f'Error al obtener switches: {str(e)}'}), 500

@switches_bp.route('/<int:switch_id>', methods=['GET'])
@token_required
def get_switch(current_user, switch_id):
"""
Obtener detalle de un switch específico
"""
try:
switch = Switch.query.get_or_404(switch_id)

# Obtener fallas relacionadas
fallas = Falla.query.filter(
Falla.tipo == 'switch',
Falla.equipo_id == switch_id
).order_by(Falla.fecha_creacion.desc()).limit(10).all()

# Información de puertos (simulado para este ejemplo)
puertos_info = []
for i in range(1, min(switch.numero_puertos + 1, 5)): # Limitar a 4 puertos para visualización
puertos_info.append({
'numero': i,
'estado': 'activo' if i <= getattr(switch, 'puertos_activos', 0) else 'inactivo',
'velocidad': '1 Gbps',
'poe': getattr(switch, 'poe_habilitado', False) and i <= 4, # Primeros 4 puertos con POE
'vlan': 1,
'conectado_a': f'Dispositivo-{i}' if i <= getattr(switch, 'puertos_activos', 0) else None
})

fallas_info = [{
'id': f.id,
'titulo': f.titulo,
'estado': f.estado,
'prioridad': f.prioridad,
'fecha_creacion': f.fecha_creacion.isoformat()
} for f in fallas]

return jsonify({
'id': switch.id,
'nombre': switch.nombre,
'descripcion': switch.descripcion,
'ip_address': switch.ip_address,
'puerto_admin': switch.puerto_admin,
'usuario': switch.usuario,
'password': '[ENCRYPTED]', # No mostrar contraseña real
'marca': switch.marca,
'modelo': switch.modelo,
'numero_serie': switch.numero_serie,
'mac_address': switch.mac_address,
'ubicacion': switch.ubicacion,
'estado': switch.estado,
'tipo': switch.tipo,
'numero_puertos': switch.numero_puertos,
'puertos_activos': getattr(switch, 'puertos_activos', 0),
'velocidad_puertos': getattr(switch, 'velocidad_puertos', '10/100/1000 Mbps'),
'poe_habilitado': getattr(switch, 'poe_habilitado', False),
'vlans_configuradas': getattr(switch, 'vlans_configuradas', 0),
'fecha_instalacion': switch.fecha_instalacion.isoformat() if switch.fecha_instalacion else None,
'fecha_ultimo_mantenimiento': switch.fecha_ultimo_mantenimiento.isoformat() if switch.fecha_ultimo_mantenimiento else None,
'created_at': switch.created_at.isoformat(),
'updated_at': switch.updated_at.isoformat() if switch.updated_at else None,
'fallas_recientes': fallas_info,
'puertos_info': puertos_info,
'total_fallas': len(fallas_info),
'fallas_abiertas': len([f for f in fallas if f.estado in ['abierta', 'en_proceso']])
})

except Exception as e:
return jsonify({'error': f'Error al obtener switch: {str(e)}'}), 500

@switches_bp.route('', methods=['POST'])
@token_required
@require_permission('equipos_crear')
@validate_json
def create_switch(current_user):
"""
Crear un nuevo switch
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

# Validar formato de MAC (opcional)
if 'mac_address' in data and data['mac_address']:
import re
mac_pattern = re.compile(r'^([0-9A-Fa-f]{}[:-]){5}([0-9A-Fa-f]{})$')
if not mac_pattern.match(data['mac_address']):
return jsonify({'error': 'Formato de MAC inválido. Use XX:XX:XX:XX:XX:XX o XX-XX-XX-XX-XX-XX'}), 400

# Verificar que no existe otro switch con la misma IP
ip_existe = Switch.query.filter(
Switch.ip_address == data['ip_address'],
Switch.activo == True
).first()

if ip_existe:
return jsonify({'error': 'Ya existe un switch con esa dirección IP'}), 400

# Crear switch
switch = Switch(
nombre=data['nombre'].strip(),
descripcion=data.get('descripcion', '').strip(),
ip_address=data['ip_address'],
puerto_admin=data.get('puerto_admin', 80),
usuario=data.get('usuario', ''),
password=data.get('password', ''), # En producción, cifrar
marca=data.get('marca', '').strip(),
modelo=data.get('modelo', '').strip(),
numero_serie=data.get('numero_serie', '').strip(),
mac_address=data.get('mac_address', '').strip(),
ubicacion=data.get('ubicacion', '').strip(),
estado=data.get('estado', 'operativo'),
tipo=data.get('tipo', 'gestionable'), # gestionable, no_gestionable
numero_puertos=data.get('numero_puertos', 4),
fecha_instalacion=datetime.fromisoformat(data['fecha_instalacion']) if data.get('fecha_instalacion') else None,
activo=True,
created_at=datetime.utcnow()
)

# Campos adicionales
if 'puertos_activos' in data:
switch.puertos_activos = data['puertos_activos']
if 'velocidad_puertos' in data:
switch.velocidad_puertos = data['velocidad_puertos']
if 'poe_habilitado' in data:
switch.poe_habilitado = data['poe_habilitado']
if 'vlans_configuradas' in data:
switch.vlans_configuradas = data['vlans_configuradas']

db.session.add(switch)
db.session.commit()

return jsonify({
'message': 'Switch creado exitosamente',
'switch_id': switch.id
}), 01

except Exception as e:
db.session.rollback()
return jsonify({'error': f'Error al crear switch: {str(e)}'}), 500

@switches_bp.route('/<int:switch_id>', methods=['PUT'])
@token_required
@require_permission('equipos_editar')
@validate_json
def update_switch(current_user, switch_id):
"""
Actualizar un switch existente
"""
try:
switch = Switch.query.get_or_404(switch_id)
data = request.get_json()

# Campos actualizables
campos_actualizables = [
'nombre', 'descripcion', 'ip_address', 'puerto_admin', 'usuario', 'password',
'marca', 'modelo', 'numero_serie', 'mac_address', 'ubicacion', 'estado', 'tipo',
'numero_puertos', 'puertos_activos', 'velocidad_puertos', 'poe_habilitado',
'vlans_configuradas', 'fecha_instalacion'
]

for campo in campos_actualizables:
if campo in data and data[campo] is not None:
if campo == 'nombre' and data[campo].strip():
switch.nombre = data[campo].strip()
elif campo == 'descripcion':
switch.descripcion = data[campo].strip()
elif campo == 'ip_address':
# Validar formato de IP
import ipaddress
try:
ipaddress.ip_address(data[campo])
# Verificar que no existe otro switch con la misma IP
ip_existe = Switch.query.filter(
Switch.ip_address == data[campo],
Switch.id = switch_id,
Switch.activo == True
).first()
if ip_existe:
return jsonify({'error': 'Ya existe otro switch con esa dirección IP'}), 400
switch.ip_address = data[campo]
except ValueError:
return jsonify({'error': 'Dirección IP inválida'}), 400
elif campo == 'mac_address':
# Validar formato de MAC
import re
mac_pattern = re.compile(r'^([0-9A-Fa-f]{}[:-]){5}([0-9A-Fa-f]{})$')
if data[campo] and not mac_pattern.match(data[campo]):
return jsonify({'error': 'Formato de MAC inválido. Use XX:XX:XX:XX:XX:XX o XX-XX-XX-XX-XX-XX'}), 400
switch.mac_address = data[campo].strip()
elif campo == 'puerto_admin':
switch.puerto_admin = data[campo]
elif campo == 'usuario':
switch.usuario = data[campo].strip()
elif campo == 'password':
switch.password = data[campo] # En producción, cifrar
elif campo == 'marca':
switch.marca = data[campo].strip()
elif campo == 'modelo':
switch.modelo = data[campo].strip()
elif campo == 'numero_serie':
switch.numero_serie = data[campo].strip()
elif campo == 'ubicacion':
switch.ubicacion = data[campo].strip()
elif campo == 'estado':
estados_validos = ['operativo', 'mantenimiento', 'fuera_servicio', 'deshabilitado']
if data[campo] not in estados_validos:
return jsonify({'error': f'Estado debe ser uno de: {estados_validos}'}), 400
switch.estado = data[campo]
elif campo == 'tipo':
tipos_validos = ['gestionable', 'no_gestionable']
if data[campo] not in tipos_validos:
return jsonify({'error': f'Tipo debe ser uno de: {tipos_validos}'}), 400
switch.tipo = data[campo]
elif campo == 'numero_puertos':
switch.numero_puertos = data[campo]
elif campo == 'puertos_activos':
switch.puertos_activos = data[campo]
elif campo == 'velocidad_puertos':
switch.velocidad_puertos = data[campo].strip()
elif campo == 'poe_habilitado':
switch.poe_habilitado = data[campo]
elif campo == 'vlans_configuradas':
switch.vlans_configuradas = data[campo]
elif campo == 'fecha_instalacion':
switch.fecha_instalacion = datetime.fromisoformat(data[campo]) if data[campo] else None

switch.updated_at = datetime.utcnow()

db.session.commit()

return jsonify({
'message': 'Switch actualizado exitosamente'
})

except Exception as e:
db.session.rollback()
return jsonify({'error': f'Error al actualizar switch: {str(e)}'}), 500

@switches_bp.route('/<int:switch_id>', methods=['DELETE'])
@token_required
@require_permission('equipos_eliminar')
def delete_switch(current_user, switch_id):
"""
Eliminar un switch (soft delete)
"""
try:
switch = Switch.query.get_or_404(switch_id)

# Verificar que no tiene fallas abiertas
fallas_abiertas = Falla.query.filter(
Falla.tipo == 'switch',
Falla.equipo_id == switch_id,
Falla.estado.in_(['abierta', 'en_proceso'])
).count()

if fallas_abiertas > 0:
return jsonify({'error': 'No se puede eliminar un switch con fallas abiertas'}), 400

switch.activo = False
switch.updated_at = datetime.utcnow()

db.session.commit()

return jsonify({
'message': 'Switch eliminado exitosamente'
})

except Exception as e:
db.session.rollback()
return jsonify({'error': f'Error al eliminar switch: {str(e)}'}), 500

@switches_bp.route('/<int:switch_id>/test-conexion', methods=['POST'])
@token_required
def test_conexion_switch(current_user, switch_id):
"""
Probar conexión con el switch
"""
try:
switch = Switch.query.get_or_404(switch_id)

# Simular test de conexión (en producción sería una verificación real)
resultado = {
'switch_id': switch_id,
'ip_address': switch.ip_address,
'puerto_admin': switch.puerto_admin,
'timestamp': datetime.utcnow().isoformat(),
'resultado': 'exito', # 'exito', 'error', 'timeout'
'mensaje': 'Conexión exitosa',
'tiempo_respuesta_ms': 50, # Simulado
'version_firmware': 'v1.5.3',
'puertos_estado': [
{'puerto': i, 'estado': 'activo', 'velocidad': '1 Gbps'}
for i in range(1, min(getattr(switch, 'puertos_activos', 0) + 1, 5))
],
'utilizacion_cpu': 5,
'utilizacion_memoria': 45,
'temperatura': 35 # Celsius
}

# En una implementación real, aquí se haría:
# - Ping a la IP
# - SNMP query para obtener estadísticas
# - Verificar puertos individuales
# - Obtener información del sistema

return jsonify(resultado)

except Exception as e:
return jsonify({
'error': f'Error al probar conexión: {str(e)}'
}), 500

@switches_bp.route('/<int:switch_id>/actualizar-puertos', methods=['PUT'])
@token_required
@require_permission('equipos_editar')
@validate_json
def actualizar_puertos_switch(current_user, switch_id):
"""
Actualizar número de puertos activos
"""
try:
switch = Switch.query.get_or_404(switch_id)
data = request.get_json()

if 'puertos_activos' not in data:
return jsonify({'error': 'puertos_activos es requerido'}), 400

puertos_activos = data['puertos_activos']

if puertos_activos < 0 or puertos_activos > switch.numero_puertos:
return jsonify({
'error': f'puertos_activos debe estar entre 0 y {switch.numero_puertos}'
}), 400

switch.puertos_activos = puertos_activos
switch.updated_at = datetime.utcnow()

db.session.commit()

return jsonify({
'message': 'Puertos actualizados exitosamente',
'puertos_activos': switch.puertos_activos,
'porcentaje_utilizacion': round((switch.puertos_activos / switch.numero_puertos * 100) if switch.numero_puertos > 0 else 0, 1)
})

except Exception as e:
db.session.rollback()
return jsonify({'error': f'Error al actualizar puertos: {str(e)}'}), 500

@switches_bp.route('/<int:switch_id>/mantenimiento', methods=['PUT'])
@token_required
@require_permission('equipos_editar')
def actualizar_mantenimiento_switch(current_user, switch_id):
"""
Actualizar fecha de último mantenimiento
"""
try:
switch = Switch.query.get_or_404(switch_id)

switch.fecha_ultimo_mantenimiento = datetime.utcnow()
switch.updated_at = datetime.utcnow()

db.session.commit()

return jsonify({
'message': 'Fecha de mantenimiento actualizada',
'fecha_ultimo_mantenimiento': switch.fecha_ultimo_mantenimiento.isoformat()
})

except Exception as e:
db.session.rollback()
return jsonify({'error': f'Error al actualizar mantenimiento: {str(e)}'}), 500

@switches_bp.route('/estadisticas', methods=['GET'])
@token_required
def get_switches_estadisticas(current_user):
"""
Obtener estadísticas de switches
"""
try:
# Total por estado
por_estado = db.session.query(
Switch.estado,
func.count(Switch.id)
).filter_by(activo=True).group_by(Switch.estado).all()

# Total por tipo
por_tipo = db.session.query(
Switch.tipo,
func.count(Switch.id)
).filter_by(activo=True).group_by(Switch.tipo).all()

# Total por marca
por_marca = db.session.query(
Switch.marca,
func.count(Switch.id)
).filter(
Switch.activo == True,
Switch.marca = ''
).group_by(Switch.marca).all()

# Total por ubicación
por_ubicacion = db.session.query(
Switch.ubicacion,
func.count(Switch.id)
).filter(
Switch.activo == True,
Switch.ubicacion = ''
).group_by(Switch.ubicacion).all()

# Switches con fallas abiertas
switches_con_fallas = db.session.query(
Switch.id,
Switch.nombre
).join(
Falla, and_(
Falla.tipo == 'switch',
Falla.equipo_id == Switch.id,
Falla.estado.in_(['abierta', 'en_proceso'])
)
).filter(Switch.activo == True).all()

# Switches que necesitan mantenimiento (más de 6 meses sin mantenimiento)
fecha_limite = datetime.utcnow() - timedelta(days=180)
switches_necesitan_mantenimiento = Switch.query.filter(
Switch.activo == True,
or_(
Switch.fecha_ultimo_mantenimiento < fecha_limite,
Switch.fecha_ultimo_mantenimiento.is_(None)
)
).count()

# Total de switches
total_switches = Switch.query.filter_by(activo=True).count()

# Distribución por número de puertos
por_puertos = db.session.query(
Switch.numero_puertos,
func.count(Switch.id)
).filter_by(activo=True).group_by(Switch.numero_puertos).all()

# Total de puertos activos
total_puertos = db.session.query(func.sum(Switch.puertos_activos)).filter(
Switch.activo == True
).scalar() or 0

# Total de puertos disponibles
total_puertos_disponibles = db.session.query(func.sum(Switch.numero_puertos)).filter(
Switch.activo == True
).scalar() or 0

return jsonify({
'total_switches': total_switches,
'total_puertos_activos': total_puertos,
'total_puertos_disponibles': total_puertos_disponibles,
'porcentaje_utilizacion_puertos': round((total_puertos / total_puertos_disponibles * 100) if total_puertos_disponibles > 0 else 0, 1),
'por_estado': {estado: cantidad for estado, cantidad in por_estado},
'por_tipo': {tipo: cantidad for tipo, cantidad in por_tipo},
'por_marca': [{'marca': marca, 'cantidad': cantidad} for marca, cantidad in por_marca],
'por_ubicacion': [{'ubicacion': ubicacion, 'cantidad': cantidad} for ubicacion, cantidad in por_ubicacion],
'por_puertos': [{'puertos': puertos, 'cantidad': cantidad} for puertos, cantidad in por_puertos],
'switches_con_fallas': len(switches_con_fallas),
'switches_funcionando': total_switches - len(switches_con_fallas),
'switches_necesitan_mantenimiento': switches_necesitan_mantenimiento,
'porcentaje_funcionamiento': round(((total_switches - len(switches_con_fallas)) / total_switches * 100) if total_switches > 0 else 0, 1),
'detalle_switches_con_fallas': [
{'id': switch_id, 'nombre': nombre} for switch_id, nombre in switches_con_fallas
]
})

except Exception as e:
return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500

@switches_bp.route('/buscar-ip/<ip_address>', methods=['GET'])
@token_required
def buscar_switch_por_ip(current_user, ip_address):
"""
Buscar switch por dirección IP
"""
try:
# Validar formato de IP
import ipaddress
try:
ipaddress.ip_address(ip_address)
except ValueError:
return jsonify({'error': 'Dirección IP inválida'}), 400

switch = Switch.query.filter_by(
ip_address=ip_address,
activo=True
).first()

if not switch:
return jsonify({'message': 'No se encontró switch con esa IP'}), 404

return jsonify({
'id': switch.id,
'nombre': switch.nombre,
'ip_address': switch.ip_address,
'ubicacion': switch.ubicacion,
'estado': switch.estado,
'tipo': switch.tipo,
'numero_puertos': switch.numero_puertos,
'fecha_instalacion': switch.fecha_instalacion.isoformat() if switch.fecha_instalacion else None
})

except Exception as e:
return jsonify({'error': f'Error al buscar switch: {str(e)}'}), 500

@switches_bp.route('/buscar-mac/<mac_address>', methods=['GET'])
@token_required
def buscar_switch_por_mac(current_user, mac_address):
"""
Buscar switch por dirección MAC
"""
try:
# Normalizar formato de MAC
mac_normalizada = mac_address.replace('-', ':').upper()

switch = Switch.query.filter(
func.upper(Switch.mac_address) == mac_normalizada,
Switch.activo == True
).first()

if not switch:
return jsonify({'message': 'No se encontró switch con esa MAC'}), 404

return jsonify({
'id': switch.id,
'nombre': switch.nombre,
'mac_address': switch.mac_address,
'ip_address': switch.ip_address,
'ubicacion': switch.ubicacion,
'estado': switch.estado,
'tipo': switch.tipo,
'numero_serie': switch.numero_serie
})

except Exception as e:
return jsonify({'error': f'Error al buscar switch por MAC: {str(e)}'}), 500