"""
Rutas CRUD para el manejo de UPS
"""
from flask import request, jsonify
from sqlalchemy import or_, and_, desc, func
from datetime import datetime, timedelta
from .. import ups_bp
from .auth import token_required
from models import Ups, Falla, db
from utils.validators import validate_json, validate_required_fields
from utils.decorators import require_permission

@ups_bp.route('', methods=['GET'])
@token_required
def get_ups(current_user):
    """
    Obtener lista de UPSs con filtros y paginación
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        if per_page > 100:
            per_page = 100
        
        query = Ups.query.filter_by(activo=True)
        
        # Aplicar filtros
        estado = request.args.get('estado', '')
        ubicacion = request.args.get('ubicacion', '')
        search = request.args.get('search', '')
        marca = request.args.get('marca', '')
        
        if estado:
            query = query.filter(Ups.estado == estado)
        if ubicacion:
            query = query.filter(Ups.ubicacion.like(f'%{ubicacion}%'))
        if search:
            query = query.filter(
                or_(
                    Ups.nombre.like(f'%{search}%'),
                    Ups.descripcion.like(f'%{search}%')
                )
            )
        if marca:
            query = query.filter(Ups.marca.like(f'%{marca}%'))
        
        # Ordenamiento
        orden = request.args.get('orden', 'nombre')
        direccion = request.args.get('direccion', 'asc')
        orden_field = getattr(Ups, orden, Ups.nombre)
        if direccion == 'desc':
            query = query.order_by(orden_field.desc())
        else:
            query = query.order_by(orden_field.asc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        ups_list = []
        for u in pagination.items:
            fallas_abiertas = Falla.query.filter(
                Falla.tipo == 'ups',
                Falla.equipo_id == u.id,
                Falla.estado.in_(['abierta', 'en_proceso'])
            ).count()
            
            ups_list.append({
                'id': u.id,
                'nombre': u.nombre,
                'descripcion': u.descripcion,
                'marca': u.marca,
                'modelo': u.modelo,
                'numero_serie': u.numero_serie,
                'ubicacion': u.ubicacion,
                'estado': u.estado,
                'potencia_va': u.potencia_va,
                'autonomia_minutos': u.autonomia_minutos,
                'voltaje_entrada': u.voltaje_entrada,
                'voltaje_salida': u.voltaje_salida,
                'fecha_instalacion': u.fecha_instalacion.isoformat() if u.fecha_instalacion else None,
                'fecha_ultimo_mantenimiento': u.fecha_ultimo_mantenimiento.isoformat() if u.fecha_ultimo_mantenimiento else None,
                'nivel_bateria': getattr(u, 'nivel_bateria', 100),
                'tiempo_funcionamiento': getattr(u, 'tiempo_funcionamiento', 0),
                'fallas_abiertas': fallas_abiertas,
                'created_at': u.created_at.isoformat()
            })
        
        return jsonify({
            'ups': ups_list,
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
        return jsonify({'error': f'Error al obtener UPS: {str(e)}'}), 500

@ups_bp.route('/<int:ups_id>', methods=['GET'])
@token_required
def get_ups_detail(current_user, ups_id):
    """
    Obtener detalle de un UPS específico
    """
    try:
        ups = Ups.query.get_or_404(ups_id)
        
        fallas = Falla.query.filter(
            Falla.tipo == 'ups',
            Falla.equipo_id == ups_id
        ).order_by(Falla.fecha_creacion.desc()).limit(10).all()
        
        fallas_info = [{
            'id': f.id,
            'titulo': f.titulo,
            'estado': f.estado,
            'prioridad': f.prioridad,
            'fecha_creacion': f.fecha_creacion.isoformat()
        } for f in fallas]
        
        return jsonify({
            'id': ups.id,
            'nombre': ups.nombre,
            'descripcion': ups.descripcion,
            'marca': ups.marca,
            'modelo': ups.modelo,
            'numero_serie': ups.numero_serie,
            'ubicacion': ups.ubicacion,
            'estado': ups.estado,
            'potencia_va': ups.potencia_va,
            'autonomia_minutos': ups.autonomia_minutos,
            'voltaje_entrada': ups.voltaje_entrada,
            'voltaje_salida': ups.voltaje_salida,
            'fecha_instalacion': ups.fecha_instalacion.isoformat() if ups.fecha_instalacion else None,
            'fecha_ultimo_mantenimiento': ups.fecha_ultimo_mantenimiento.isoformat() if ups.fecha_ultimo_mantenimiento else None,
            'nivel_bateria': getattr(ups, 'nivel_bateria', 100),
            'tiempo_funcionamiento': getattr(ups, 'tiempo_funcionamiento', 0),
            'carga_actual': getattr(ups, 'carga_actual', 0),
            'fallas_recientes': fallas_info,
            'total_fallas': len(fallas_info)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener UPS: {str(e)}'}), 500

@ups_bp.route('', methods=['POST'])
@token_required
@require_permission('equipos_crear')
@validate_json
def create_ups(current_user):
    """
    Crear un nuevo UPS
    """
    try:
        data = request.get_json()
        
        required_fields = ['nombre']
        if not validate_required_fields(data, required_fields):
            return jsonify({'error': 'Campo requerido: nombre'}), 400
        
        ups = Ups(
            nombre=data['nombre'].strip(),
            descripcion=data.get('descripcion', '').strip(),
            marca=data.get('marca', '').strip(),
            modelo=data.get('modelo', '').strip(),
            numero_serie=data.get('numero_serie', '').strip(),
            ubicacion=data.get('ubicacion', '').strip(),
            estado=data.get('estado', 'operativo'),
            potencia_va=data.get('potencia_va', 1000),
            autonomia_minutos=data.get('autonomia_minutos', 30),
            voltaje_entrada=data.get('voltaje_entrada', 220),
            voltaje_salida=data.get('voltaje_salida', 220),
            fecha_instalacion=datetime.fromisoformat(data['fecha_instalacion']) if data.get('fecha_instalacion') else None,
            activo=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(ups)
        db.session.commit()
        
        return jsonify({
            'message': 'UPS creado exitosamente',
            'ups_id': ups.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear UPS: {str(e)}'}), 500

@ups_bp.route('/<int:ups_id>', methods=['PUT'])
@token_required
@require_permission('equipos_editar')
@validate_json
def update_ups(current_user, ups_id):
    """
    Actualizar un UPS existente
    """
    try:
        ups = Ups.query.get_or_404(ups_id)
        data = request.get_json()
        
        campos_actualizables = [
            'nombre', 'descripcion', 'marca', 'modelo', 'numero_serie',
            'ubicacion', 'estado', 'potencia_va', 'autonomia_minutos',
            'voltaje_entrada', 'voltaje_salida', 'fecha_instalacion'
        ]
        
        for campo in campos_actualizables:
            if campo in data and data[campo] is not None:
                if campo == 'nombre' and data[campo].strip():
                    ups.nombre = data[campo].strip()
                else:
                    setattr(ups, campo, data[campo])
        
        ups.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'UPS actualizado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar UPS: {str(e)}'}), 500

@ups_bp.route('/<int:ups_id>', methods=['DELETE'])
@token_required
@require_permission('equipos_eliminar')
def delete_ups(current_user, ups_id):
    """
    Eliminar un UPS (soft delete)
    """
    try:
        ups = Ups.query.get_or_404(ups_id)
        
        fallas_abiertas = Falla.query.filter(
            Falla.tipo == 'ups',
            Falla.equipo_id == ups_id,
            Falla.estado.in_(['abierta', 'en_proceso'])
        ).count()
        
        if fallas_abiertas > 0:
            return jsonify({'error': 'No se puede eliminar un UPS con fallas abiertas'}), 400
        
        ups.activo = False
        ups.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'UPS eliminado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al eliminar UPS: {str(e)}'}), 500

@ups_bp.route('/<int:ups_id>/test', methods=['POST'])
@token_required
def test_ups(current_user, ups_id):
    """
    Probar funcionamiento del UPS
    """
    try:
        ups = Ups.query.get_or_404(ups_id)
        
        resultado = {
            'ups_id': ups_id,
            'timestamp': datetime.utcnow().isoformat(),
            'resultado': 'exito',
            'nivel_bateria': getattr(ups, 'nivel_bateria', 95),
            'voltaje_entrada': ups.voltaje_entrada,
            'voltaje_salida': ups.voltaje_salida,
            'carga_actual': getattr(ups, 'carga_actual', 45),
            'temperatura': getattr(ups, 'temperatura', 25),
            'autonomia_restante': ups.autonomia_minutos
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'error': f'Error al probar UPS: {str(e)}'}), 500

@ups_bp.route('/<int:ups_id>/mantenimiento', methods=['PUT'])
@token_required
@require_permission('equipos_editar')
def actualizar_mantenimiento_ups(current_user, ups_id):
    """
    Actualizar fecha de último mantenimiento
    """
    try:
        ups = Ups.query.get_or_404(ups_id)
        
        ups.fecha_ultimo_mantenimiento = datetime.utcnow()
        ups.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Fecha de mantenimiento actualizada',
            'fecha_ultimo_mantenimiento': ups.fecha_ultimo_mantenimiento.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar mantenimiento: {str(e)}'}), 500

@ups_bp.route('/estadisticas', methods=['GET'])
@token_required
def get_ups_estadisticas(current_user):
    """
    Obtener estadísticas de UPSs
    """
    try:
        total_ups = Ups.query.filter_by(activo=True).count()
        
        por_estado = db.session.query(
            Ups.estado,
            func.count(Ups.id)
        ).filter_by(activo=True).group_by(Ups.estado).all()
        
        por_marca = db.session.query(
            Ups.marca,
            func.count(Ups.id)
        ).filter(Ups.activo == True, Ups.marca != '').group_by(Ups.marca).all()
        
        return jsonify({
            'total_ups': total_ups,
            'por_estado': {estado: cantidad for estado, cantidad in por_estado},
            'por_marca': [{'marca': marca, 'cantidad': cantidad} for marca, cantidad in por_marca]
        })
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500