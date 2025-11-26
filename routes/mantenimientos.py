"""
Rutas CRUD para el manejo de Mantenimientos
"""
from flask import request, jsonify
from sqlalchemy import or_, and_, desc, func, case
from datetime import datetime, timedelta
from .. import mantenimientos_bp
from .auth import token_required
from models import Mantenimiento, Usuario, Camara, Nvr, Switch, Ups, Fuente, Gabinete, db
from utils.validators import validate_json, validate_required_fields, validate_pagination
from utils.decorators import require_permission

# Mapeo de tipos de equipo a modelos
EQUIPOS_MAP = {
    'camara': Camara,
    'nvr': Nvr,
    'switch': Switch,
    'ups': Ups,
    'fuente': Fuente,
    'gabinete': Gabinete
}

@mantenimientos_bp.route('', methods=['GET'])
@token_required
def get_mantenimientos(current_user):
    """
    Obtener lista de mantenimientos con filtros y paginación
    """
    try:
        # Validar paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 0, type=int)

        if per_page > 100:
            per_page = 100

        # Parámetros de filtro
        estado = request.args.get('estado', '')
        tipo = request.args.get('tipo', '')  # preventivo, correctivo, predictivo
        tipo_equipo = request.args.get('tipo_equipo', '')
        asignado_a = request.args.get('asignado_a', '')
        search = request.args.get('search', '')
        fecha_desde = request.args.get('fecha_desde', '')
        fecha_hasta = request.args.get('fecha_hasta', '')
        prioridad = request.args.get('prioridad', '')
        orden = request.args.get('orden', 'fecha_programada')
        direccion = request.args.get('direccion', 'asc')

        # Query base
        query = Mantenimiento.query.filter_by(activo=True)

        # Aplicar filtros
        if estado:
            query = query.filter(Mantenimiento.estado == estado)
        if tipo:
            query = query.filter(Mantenimiento.tipo == tipo)
        if tipo_equipo:
            query = query.filter(Mantenimiento.tipo_equipo == tipo_equipo)
        if asignado_a:
            query = query.filter(Mantenimiento.asignado_a_id == asignado_a)
        if search:
            query = query.filter(
                or_(
                    Mantenimiento.titulo.like(f'%{search}%'),
                    Mantenimiento.descripcion.like(f'%{search}%')
                )
            )
        if prioridad:
            query = query.filter(Mantenimiento.prioridad == prioridad)
        if fecha_desde:
            try:
                fecha_desde_dt = datetime.fromisoformat(fecha_desde.replace('Z', '+00:00'))
                query = query.filter(Mantenimiento.fecha_programada >= fecha_desde_dt)
            except ValueError:
                pass
        if fecha_hasta:
            try:
                fecha_hasta_dt = datetime.fromisoformat(fecha_hasta.replace('Z', '+00:00'))
                query = query.filter(Mantenimiento.fecha_programada <= fecha_hasta_dt)
            except ValueError:
                pass

        # Ordenamiento
        if orden == 'prioridad':
            # Prioridad: crítica > alta > media > baja
            orden_field = case(
                (Mantenimiento.prioridad == 'critica', 1),
                (Mantenimiento.prioridad == 'alta', 2),
                (Mantenimiento.prioridad == 'media', 3),
                (Mantenimiento.prioridad == 'baja', 4),
                else_=5
            )
            if direccion == 'desc':
                query = query.order_by(orden_field.desc(), Mantenimiento.fecha_programada.desc())
            else:
                query = query.order_by(orden_field.asc(), Mantenimiento.fecha_programada.asc())
        else:
            orden_field = getattr(Mantenimiento, orden, Mantenimiento.fecha_programada)
            if direccion == 'desc':
                query = query.order_by(orden_field.desc())
            else:
                query = query.order_by(orden_field.asc())

        # Paginación
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        mantenimientos = []
        for m in pagination.items:
            # Obtener información del equipo
            equipo_info = None
            if m.equipo_id and m.tipo_equipo in EQUIPOS_MAP:
                equipo = EQUIPOS_MAP[m.tipo_equipo].query.filter_by(id=m.equipo_id, activo=True).first()
                if equipo:
                    equipo_info = {
                        'id': equipo.id,
                        'nombre': equipo.nombre,
                        'ubicacion': getattr(equipo, 'ubicacion', ''),
                        'tipo': m.tipo_equipo
                    }

            mantenimientos.append({
                'id': m.id,
                'titulo': m.titulo,
                'descripcion': m.descripcion,
                'tipo': m.tipo,
                'tipo_equipo': m.tipo_equipo,
                'equipo_id': m.equipo_id,
                'equipo': equipo_info,
                'estado': m.estado,
                'prioridad': m.prioridad,
                'fecha_programada': m.fecha_programada.isoformat() if m.fecha_programada else None,
                'fecha_ejecucion': m.fecha_ejecucion.isoformat() if m.fecha_ejecucion else None,
                'tiempo_estimado_horas': m.tiempo_estimado_horas,
                'costo_estimado': m.costo_estimado,
                'costo_real': m.costo_real,
                'notas': m.notas,
                'asignado_a': {
                    'id': m.asignado_a.id if m.asignado_a else None,
                    'nombre': m.asignado_a.nombre if m.asignado_a else None,
                    'apellido': m.asignado_a.apellido if m.asignado_a else None
                } if m.asignado_a else None,
                'ejecutado_por': {
                    'id': m.ejecutado_por.id if m.ejecutado_por else None,
                    'nombre': m.ejecutado_por.nombre if m.ejecutado_por else None,
                    'apellido': m.ejecutado_por.apellido if m.ejecutado_por else None
                } if m.ejecutado_por else None,
                'created_at': m.created_at.isoformat(),
                'updated_at': m.updated_at.isoformat() if m.updated_at else None
            })

        return jsonify({
            'mantenimientos': mantenimientos,
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
                'tipo': tipo,
                'tipo_equipo': tipo_equipo,
                'asignado_a': asignado_a,
                'search': search,
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
                'prioridad': prioridad,
                'orden': orden,
                'direccion': direccion
            }
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener mantenimientos: {str(e)}'}), 500

@mantenimientos_bp.route('/<int:mantenimiento_id>', methods=['GET'])
@token_required
def get_mantenimiento(current_user, mantenimiento_id):
    """
    Obtener detalle de un mantenimiento específico
    """
    try:
        mantenimiento = Mantenimiento.query.get_or_404(mantenimiento_id)

        # Información del equipo
        equipo_info = None
        if mantenimiento.equipo_id and mantenimiento.tipo_equipo in EQUIPOS_MAP:
            equipo = EQUIPOS_MAP[mantenimiento.tipo_equipo].query.filter_by(id=mantenimiento.equipo_id, activo=True).first()
            if equipo:
                equipo_info = {
                    'id': equipo.id,
                    'nombre': equipo.nombre,
                    'ubicacion': getattr(equipo, 'ubicacion', ''),
                    'marca': getattr(equipo, 'marca', ''),
                    'modelo': getattr(equipo, 'modelo', ''),
                    'tipo': mantenimiento.tipo_equipo
                }

        return jsonify({
            'id': mantenimiento.id,
            'titulo': mantenimiento.titulo,
            'descripcion': mantenimiento.descripcion,
            'tipo': mantenimiento.tipo,
            'tipo_equipo': mantenimiento.tipo_equipo,
            'equipo_id': mantenimiento.equipo_id,
            'equipo': equipo_info,
            'estado': mantenimiento.estado,
            'prioridad': mantenimiento.prioridad,
            'fecha_programada': mantenimiento.fecha_programada.isoformat() if mantenimiento.fecha_programada else None,
            'fecha_ejecucion': mantenimiento.fecha_ejecucion.isoformat() if mantenimiento.fecha_ejecucion else None,
            'tiempo_estimado_horas': mantenimiento.tiempo_estimado_horas,
            'tiempo_real_horas': mantenimiento.tiempo_real_horas,
            'costo_estimado': mantenimiento.costo_estimado,
            'costo_real': mantenimiento.costo_real,
            'notas': mantenimiento.notas,
            'materiales_utilizados': getattr(mantenimiento, 'materiales_utilizados', []),
            'actividades_realizadas': getattr(mantenimiento, 'actividades_realizadas', []),
            'problemas_encontrados': getattr(mantenimiento, 'problemas_encontrados', []),
            'recomendaciones': getattr(mantenimiento, 'recomendaciones', ''),
            'asignado_a': {
                'id': mantenimiento.asignado_a.id if mantenimiento.asignado_a else None,
                'nombre': mantenimiento.asignado_a.nombre if mantenimiento.asignado_a else None,
                'apellido': mantenimiento.asignado_a.apellido if mantenimiento.asignado_a else None
            } if mantenimiento.asignado_a else None,
            'ejecutado_por': {
                'id': mantenimiento.ejecutado_por.id if mantenimiento.ejecutado_por else None,
                'nombre': mantenimiento.ejecutado_por.nombre if mantenimiento.ejecutado_por else None,
                'apellido': mantenimiento.ejecutado_por.apellido if mantenimiento.ejecutado_por else None
            } if mantenimiento.ejecutado_por else None,
            'created_at': mantenimiento.created_at.isoformat(),
            'updated_at': mantenimiento.updated_at.isoformat() if mantenimiento.updated_at else None
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener mantenimiento: {str(e)}'}), 500

@mantenimientos_bp.route('', methods=['POST'])
@token_required
@require_permission('mantenimientos_crear')
@validate_json
def create_mantenimiento(current_user):
    """
    Crear un nuevo mantenimiento
    """
    try:
        data = request.get_json()

        # Validar campos requeridos
        required_fields = ['titulo', 'tipo', 'tipo_equipo']
        if not validate_required_fields(data, required_fields):
            return jsonify({'error': 'Campos requeridos: titulo, tipo, tipo_equipo'}), 400

        # Validar tipos de mantenimiento
        tipos_validos = ['preventivo', 'correctivo', 'predictivo', 'urgente', 'rutinario']
        if data['tipo'] not in tipos_validos:
            return jsonify({'error': f'Tipo debe ser uno de: {tipos_validos}'}), 400

        # Validar tipo de equipo
        if data['tipo_equipo'] not in EQUIPOS_MAP:
            return jsonify({'error': f'Tipo de equipo inválido. Válidos: {list(EQUIPOS_MAP.keys())}'}), 400

        # Validar prioridad
        prioridades_validas = ['baja', 'media', 'alta', 'critica']
        prioridad = data.get('prioridad', 'media')
        if prioridad not in prioridades_validas:
            return jsonify({'error': f'Prioridad debe ser una de: {prioridades_validas}'}), 400

        # Validar que el equipo existe si se especifica
        equipo_id = data.get('equipo_id')
        if equipo_id:
            equipo = EQUIPOS_MAP[data['tipo_equipo']].query.filter_by(id=equipo_id, activo=True).first()
            if not equipo:
                return jsonify({'error': f'Equipo {data["tipo_equipo"]} no encontrado o inactivo'}), 400

        # Validar fechas
        fecha_programada = None
        if 'fecha_programada' in data and data['fecha_programada']:
            try:
                fecha_programada = datetime.fromisoformat(data['fecha_programada'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Formato de fecha_programada inválido'}), 400

        # Crear mantenimiento
        mantenimiento = Mantenimiento(
            titulo=data['titulo'].strip(),
            descripcion=data.get('descripcion', '').strip(),
            tipo=data['tipo'],
            tipo_equipo=data['tipo_equipo'],
            equipo_id=equipo_id,
            estado='pendiente',  # Estado inicial
            prioridad=prioridad,
            asignado_a_id=data.get('asignado_a_id'),
            fecha_programada=fecha_programada,
            created_at=datetime.utcnow()
        )

        # Campos adicionales opcionales
        if 'tiempo_estimado_horas' in data:
            mantenimiento.tiempo_estimado_horas = data['tiempo_estimado_horas']
        if 'costo_estimado' in data:
            mantenimiento.costo_estimado = data['costo_estimado']
        if 'notas' in data:
            mantenimiento.notas = data['notas']

        db.session.add(mantenimiento)
        db.session.commit()

        return jsonify({
            'message': 'Mantenimiento creado exitosamente',
            'mantenimiento_id': mantenimiento.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear mantenimiento: {str(e)}'}), 500

@mantenimientos_bp.route('/<int:mantenimiento_id>', methods=['PUT'])
@token_required
@require_permission('mantenimientos_editar')
@validate_json
def update_mantenimiento(current_user, mantenimiento_id):
    """
    Actualizar un mantenimiento existente
    """
    try:
        mantenimiento = Mantenimiento.query.get_or_404(mantenimiento_id)
        data = request.get_json()

        # Solo permitir actualizar mantenimientos no completados
        if mantenimiento.estado == 'completado':
            return jsonify({'error': 'No se puede modificar un mantenimiento completado'}), 400

        # Campos que se pueden actualizar
        campos_actualizables = [
            'titulo', 'descripcion', 'tipo', 'tipo_equipo', 'equipo_id', 'estado',
            'asignado_a_id', 'fecha_programada', 'prioridad', 'tiempo_estimado_horas',
            'costo_estimado', 'notas'
        ]

        for campo in campos_actualizables:
            if campo in data and data[campo] is not None:
                if campo == 'titulo' and data[campo].strip():
                    mantenimiento.titulo = data[campo].strip()
                elif campo == 'descripcion':
                    mantenimiento.descripcion = data[campo].strip()
                elif campo == 'tipo':
                    tipos_validos = ['preventivo', 'correctivo', 'predictivo', 'urgente', 'rutinario']
                    if data[campo] not in tipos_validos:
                        return jsonify({'error': f'Tipo debe ser uno de: {tipos_validos}'}), 400
                    mantenimiento.tipo = data[campo]
                elif campo == 'tipo_equipo':
                    if data[campo] not in EQUIPOS_MAP:
                        return jsonify({'error': f'Tipo de equipo inválido: {data[campo]}'}), 400
                    mantenimiento.tipo_equipo = data[campo]
                elif campo == 'equipo_id':
                    if data[campo]:
                        equipo = EQUIPOS_MAP[mantenimiento.tipo_equipo].query.filter_by(id=data[campo], activo=True).first()
                        if not equipo:
                            return jsonify({'error': 'Equipo no encontrado o inactivo'}), 400
                    mantenimiento.equipo_id = data[campo]
                elif campo == 'estado':
                    estados_validos = ['pendiente', 'en_proceso', 'completado', 'cancelado']
                    if data[campo] not in estados_validos:
                        return jsonify({'error': f'Estado debe ser uno de: {estados_validos}'}), 400
                    mantenimiento.estado = data[campo]
                elif campo == 'prioridad':
                    prioridades_validas = ['baja', 'media', 'alta', 'critica']
                    if data[campo] not in prioridades_validas:
                        return jsonify({'error': f'Prioridad debe ser una de: {prioridades_validas}'}), 400
                    mantenimiento.prioridad = data[campo]
                elif campo == 'fecha_programada':
                    if data[campo]:
                        try:
                            mantenimiento.fecha_programada = datetime.fromisoformat(data[campo].replace('Z', '+00:00'))
                        except ValueError:
                            return jsonify({'error': 'Formato de fecha_programada inválido'}), 400
                    else:
                        mantenimiento.fecha_programada = None
                elif campo == 'asignado_a_id':
                    if data[campo]:
                        usuario = Usuario.query.filter_by(id=data[campo], activo=True).first()
                        if not usuario:
                            return jsonify({'error': 'Usuario asignado no encontrado'}), 400
                    mantenimiento.asignado_a_id = data[campo]
                else:
                    setattr(mantenimiento, campo, data[campo])

        mantenimiento.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Mantenimiento actualizado exitosamente'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar mantenimiento: {str(e)}'}), 500

@mantenimientos_bp.route('/<int:mantenimiento_id>', methods=['DELETE'])
@token_required
@require_permission('mantenimientos_eliminar')
def delete_mantenimiento(current_user, mantenimiento_id):
    """
    Eliminar un mantenimiento (soft delete)
    """
    try:
        mantenimiento = Mantenimiento.query.get_or_404(mantenimiento_id)

        # Solo permitir eliminar mantenimientos pendientes o cancelados
        if mantenimiento.estado not in ['pendiente', 'cancelado']:
            return jsonify({'error': 'Solo se pueden eliminar mantenimientos pendientes o cancelados'}), 400

        mantenimiento.activo = False
        mantenimiento.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Mantenimiento eliminado exitosamente'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al eliminar mantenimiento: {str(e)}'}), 500

@mantenimientos_bp.route('/<int:mantenimiento_id>/completar', methods=['POST'])
@token_required
@require_permission('mantenimientos_editar')
@validate_json
def completar_mantenimiento(current_user, mantenimiento_id):
    """
    Completar un mantenimiento
    """
    try:
        mantenimiento = Mantenimiento.query.get_or_404(mantenimiento_id)
        data = request.get_json()

        if mantenimiento.estado == 'completado':
            return jsonify({'error': 'El mantenimiento ya está completado'}), 400

        # Actualizar campos de finalización
        mantenimiento.estado = 'completado'
        mantenimiento.fecha_ejecucion = datetime.utcnow()
        mantenimiento.ejecutado_por_id = current_user.id
        mantenimiento.updated_at = datetime.utcnow()

        # Campos opcionales de completación
        if 'tiempo_real_horas' in data:
            mantenimiento.tiempo_real_horas = data['tiempo_real_horas']
        if 'costo_real' in data:
            mantenimiento.costo_real = data['costo_real']
        if 'notas' in data:
            mantenimiento.notas = data['notas']
        if 'actividades_realizadas' in data:
            mantenimiento.actividades_realizadas = data['actividades_realizadas']
        if 'problemas_encontrados' in data:
            mantenimiento.problemas_encontrados = data['problemas_encontrados']
        if 'recomendaciones' in data:
            mantenimiento.recomendaciones = data['recomendaciones']
        if 'materiales_utilizados' in data:
            mantenimiento.materiales_utilizados = data['materiales_utilizados']

        # Actualizar fecha de último mantenimiento del equipo
        if mantenimiento.equipo_id and mantenimiento.tipo_equipo in EQUIPOS_MAP:
            equipo = EQUIPOS_MAP[mantenimiento.tipo_equipo].query.filter_by(id=mantenimiento.equipo_id).first()
            if equipo and hasattr(equipo, 'fecha_ultimo_mantenimiento'):
                equipo.fecha_ultimo_mantenimiento = datetime.utcnow()
                equipo.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Mantenimiento completado exitosamente',
            'fecha_ejecucion': mantenimiento.fecha_ejecucion.isoformat()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al completar mantenimiento: {str(e)}'}), 500

@mantenimientos_bp.route('/proximos', methods=['GET'])
@token_required
def get_mantenimientos_proximos(current_user):
    """
    Obtener mantenimientos próximos (próximos 30 días)
    """
    try:
        dias = request.args.get('dias', 30, type=int)
        fecha_limite = datetime.utcnow() + timedelta(days=dias)

        mantenimientos = Mantenimiento.query.filter(
            Mantenimiento.activo == True,
            Mantenimiento.estado.in_(['pendiente', 'en_proceso']),
            Mantenimiento.fecha_programada <= fecha_limite,
            Mantenimiento.fecha_programada >= datetime.utcnow()
        ).order_by(Mantenimiento.fecha_programada.asc()).all()

        resultados = []
        for m in mantenimientos:
            equipo_info = None
            if m.equipo_id and m.tipo_equipo in EQUIPOS_MAP:
                equipo = EQUIPOS_MAP[m.tipo_equipo].query.filter_by(id=m.equipo_id, activo=True).first()
                if equipo:
                    equipo_info = {
                        'id': equipo.id,
                        'nombre': equipo.nombre,
                        'ubicacion': getattr(equipo, 'ubicacion', ''),
                        'tipo': m.tipo_equipo
                    }

            dias_hasta_programada = (m.fecha_programada.date() - datetime.utcnow().date()).days

            resultados.append({
                'id': m.id,
                'titulo': m.titulo,
                'tipo': m.tipo,
                'tipo_equipo': m.tipo_equipo,
                'equipo': equipo_info,
                'estado': m.estado,
                'prioridad': m.prioridad,
                'fecha_programada': m.fecha_programada.isoformat(),
                'dias_hasta_programada': dias_hasta_programada,
                'asignado_a': {
                    'nombre': m.asignado_a.nombre if m.asignado_a else None,
                    'apellido': m.asignado_a.apellido if m.asignado_a else None
                } if m.asignado_a else None
            })

        return jsonify({
            'mantenimientos_proximos': resultados,
            'total': len(resultados)
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener mantenimientos próximos: {str(e)}'}), 500

@mantenimientos_bp.route('/calendario', methods=['GET'])
@token_required
def get_mantenimientos_calendario(current_user):
    """
    Obtener mantenimientos para vista de calendario
    """
    try:
        mes = request.args.get('mes', datetime.utcnow().month, type=int)
        año = request.args.get('año', datetime.utcnow().year, type=int)

        # Obtener primer y último día del mes
        primer_dia = datetime(año, mes, 1)
        if mes == 12:
            ultimo_dia = datetime(año + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo_dia = datetime(año, mes + 1, 1) - timedelta(days=1)

        mantenimientos = Mantenimiento.query.filter(
            Mantenimiento.activo == True,
            Mantenimiento.fecha_programada >= primer_dia,
            Mantenimiento.fecha_programada <= ultimo_dia,
            Mantenimiento.estado.in_(['pendiente', 'en_proceso'])
        ).order_by(Mantenimiento.fecha_programada.asc()).all()

        eventos = []
        for m in mantenimientos:
            equipo_nombre = ''
            if m.equipo_id and m.tipo_equipo in EQUIPOS_MAP:
                equipo = EQUIPOS_MAP[m.tipo_equipo].query.filter_by(id=m.equipo_id, activo=True).first()
                if equipo:
                    equipo_nombre = equipo.nombre

            eventos.append({
                'id': m.id,
                'titulo': m.titulo,
                'fecha': m.fecha_programada.strftime('%Y-%m-%d'),
                'hora': m.fecha_programada.strftime('%H:%M'),
                'tipo': m.tipo,
                'tipo_equipo': m.tipo_equipo,
                'equipo_nombre': equipo_nombre,
                'estado': m.estado,
                'prioridad': m.prioridad,
                'descripcion': m.descripcion[:100] + '...' if len(m.descripcion) > 100 else m.descripcion
            })

        return jsonify({
            'eventos': eventos,
            'mes': mes,
            'año': año,
            'total_eventos': len(eventos)
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener calendario: {str(e)}'}), 500

@mantenimientos_bp.route('/estadisticas', methods=['GET'])
@token_required
def get_mantenimientos_estadisticas(current_user):
    """
    Obtener estadísticas de mantenimientos
    """
    try:
        # Contar por estado
        por_estado = db.session.query(
            Mantenimiento.estado,
            func.count(Mantenimiento.id)
        ).filter(Mantenimiento.activo == True).group_by(Mantenimiento.estado).all()

        # Contar por tipo
        por_tipo = db.session.query(
            Mantenimiento.tipo,
            func.count(Mantenimiento.id)
        ).filter(Mantenimiento.activo == True).group_by(Mantenimiento.tipo).all()

        # Contar por tipo de equipo
        por_tipo_equipo = db.session.query(
            Mantenimiento.tipo_equipo,
            func.count(Mantenimiento.id)
        ).filter(Mantenimiento.activo == True).group_by(Mantenimiento.tipo_equipo).all()

        # Mantenimientos completados en los últimos 30 días
        fecha_limite = datetime.utcnow() - timedelta(days=30)
        completados_recientes = db.session.query(
            func.count(Mantenimiento.id)
        ).filter(
            Mantenimiento.activo == True,
            Mantenimiento.estado == 'completado',
            Mantenimiento.fecha_ejecucion >= fecha_limite
        ).scalar()

        # Mantenimientos próximos (próximos 7 días)
        fecha_proxima = datetime.utcnow() + timedelta(days=7)
        proximos = db.session.query(
            func.count(Mantenimiento.id)
        ).filter(
            Mantenimiento.activo == True,
            Mantenimiento.estado.in_(['pendiente', 'en_proceso']),
            Mantenimiento.fecha_programada <= fecha_proxima
        ).scalar()

        # Tiempo promedio de completación (últimos 30 días)
        mantenimientos_completados = db.session.query(
            Mantenimiento.tiempo_estimado_horas,
            Mantenimiento.tiempo_real_horas
        ).filter(
            Mantenimiento.activo == True,
            Mantenimiento.estado == 'completado',
            Mantenimiento.fecha_ejecucion >= fecha_limite,
            Mantenimiento.tiempo_real_horas.isnot(None)
        ).all()

        tiempo_promedio_real = None
        tiempo_promedio_estimado = None
        if mantenimientos_completados:
            tiempos_real = [m.tiempo_real_horas for m in mantenimientos_completados if m.tiempo_real_horas]
            tiempos_estimados = [m.tiempo_estimado_horas for m in mantenimientos_completados if m.tiempo_estimado_horas]

            if tiempos_real:
                tiempo_promedio_real = round(sum(tiempos_real) / len(tiempos_real), 2)
            if tiempos_estimados:
                tiempo_promedio_estimado = round(sum(tiempos_estimados) / len(tiempos_estimados), 2)

        return jsonify({
            'total_mantenimientos': sum(cantidad for _, cantidad in por_estado),
            'por_estado': {estado: cantidad for estado, cantidad in por_estado},
            'por_tipo': {tipo: cantidad for tipo, cantidad in por_tipo},
            'por_tipo_equipo': {tipo_equipo: cantidad for tipo_equipo, cantidad in por_tipo_equipo},
            'completados_ultimos_30_dias': completados_recientes,
            'proximos_7_dias': proximos,
            'tiempo_promedio_estimado_horas': tiempo_promedio_estimado,
            'tiempo_promedio_real_horas': tiempo_promedio_real,
            'cumplimiento_estimaciones': round((tiempo_promedio_estimado / tiempo_promedio_real * 100) if tiempo_promedio_real and tiempo_promedio_estimado else 0, 1)
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500
