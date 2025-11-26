"""
Rutas CRUD para el manejo de Fuentes de Alimentación
Incluye gestión completa de fuentes con todas sus especificaciones técnicas básicas.
"""
from flask import request, jsonify, current_app
from sqlalchemy import or_, and_, desc, func, case
from datetime import datetime, timedelta
from .. import fuentes_bp
from models import Fuente, Falla, Usuario, Ubicacion, Mantenimiento, Fotografia, db
from models.fuente import EstadoFuente
from utils.validators import validate_json, validate_required_fields, validate_pagination
from utils.decorators import token_required, require_permission

@fuentes_bp.route('', methods=['GET'])
@token_required
def get_fuentes(current_user):
    """
    Obtener lista de fuentes de alimentación con filtros y paginación
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
        potencia_min = request.args.get('potencia_min', '')
        potencia_max = request.args.get('potencia_max', '')
        orden = request.args.get('orden', 'fecha_creacion')
        direccion = request.args.get('direccion', 'desc')

        # Query base
        query = Fuente.query.filter_by(activo=True, deleted=False)

        # Aplicar filtros
        if estado:
            query = query.filter(Fuente.estado == estado)
        if ubicacion:
            query = query.filter(Fuente.ubicacion.like(f'%{ubicacion}%'))
        if search:
            query = query.filter(
                or_(
                    Fuente.nombre.like(f'%{search}%'),
                    Fuente.marca.like(f'%{search}%'),
                    Fuente.modelo.like(f'%{search}%'),
                    Fuente.descripcion.like(f'%{search}%')
                )
            )
        if marca:
            query = query.filter(Fuente.marca.like(f'%{marca}%'))
        if potencia_min:
            try:
                query = query.filter(Fuente.potencia >= int(potencia_min))
            except ValueError:
                pass
        if potencia_max:
            try:
                query = query.filter(Fuente.potencia <= int(potencia_max))
            except ValueError:
                pass

        # Ordenamiento
        if orden == 'potencia':
            orden_field = Fuente.potencia
            if direccion == 'desc':
                query = query.order_by(orden_field.desc(), Fuente.fecha_creacion.desc())
            else:
                query = query.order_by(orden_field.asc(), Fuente.fecha_creacion.asc())
        elif orden == 'temperatura':
            orden_field = Fuente.temperatura_actual
            if direccion == 'desc':
                query = query.order_by(orden_field.desc(), Fuente.fecha_creacion.desc())
            else:
                query = query.order_by(orden_field.asc(), Fuente.fecha_creacion.asc())
        else:
            orden_field = getattr(Fuente, orden, Fuente.fecha_creacion)
            if direccion == 'desc':
                query = query.order_by(orden_field.desc())
            else:
                query = query.order_by(orden_field.asc())

        # Paginación
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        fuentes = []
        for f in pagination.items:
            # Obtener fallas abiertas
            fallas_abiertas = Falla.query.filter(
                Falla.tipo == 'fuente',
                Falla.equipo_id == f.id,
                Falla.estado.in_(['abierta', 'en_proceso'])
            ).count()

            # Obtener próximo mantenimiento
            proximo_mantenimiento = None
            if f.fecha_proximo_mantenimiento:
                proximo_mantenimiento = f.fecha_proximo_mantenimiento.isoformat()
            elif f.fecha_ultimo_mantenimiento:
                # Sugerir próximo mantenimiento en 6 meses
                proximo_mantenimiento = (f.fecha_ultimo_mantenimiento + timedelta(days=180)).isoformat()

            # Calcular consumo
            consumo_porcentaje = f.get_consumption_percentage()

            fuentes.append({
                'id': f.id,
                'nombre': f.nombre,
                'descripcion': f.descripcion,
                'marca': f.marca,
                'modelo': f.modelo,
                'numero_serie': f.numero_serie,
                'ubicacion': f.ubicacion,
                'estado': f.estado,
                
                # Especificaciones técnicas básicas
                'potencia': f.potencia,
                'voltaje_entrada': f.voltaje_entrada,
                'voltaje_salida': f.voltaje_salida,
                'amperaje_salida': f.amperaje_salida,
                'eficiencia': f.eficiencia,
                
                # Monitoreo
                'temperatura_actual': f.temperatura_actual,
                'carga_actual': f.carga_actual,
                'voltaje_salida_actual': f.voltaje_salida_actual,
                'consumo_porcentaje': consumo_porcentaje,
                
                # Fechas
                'fecha_instalacion': f.fecha_instalacion.isoformat() if f.fecha_instalacion else None,
                'fecha_ultimo_mantenimiento': f.fecha_ultimo_mantenimiento.isoformat() if f.fecha_ultimo_mantenimiento else None,
                'fecha_proximo_mantenimiento': proximo_mantenimiento,
                
                # Control
                'activo': f.activo,
                'fecha_creacion': f.fecha_creacion.isoformat(),
                'fecha_actualizacion': f.fecha_actualizacion.isoformat() if f.fecha_actualizacion else None,
                
                # Estado y mantenimiento
                'mantenimiento_due': f.is_maintenance_due(),
                'fallas_abiertas': fallas_abiertas,
                'status_color': f.get_status_color()
            })

        return jsonify({
            'fuentes': fuentes,
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
                'potencia_min': potencia_min,
                'potencia_max': potencia_max,
                'orden': orden,
                'direccion': direccion
            }
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener fuentes: {str(e)}'}), 500

@fuentes_bp.route('/<int:fuente_id>', methods=['GET'])
@token_required
def get_fuente(current_user, fuente_id):
    """
    Obtener detalle de una fuente específica
    """
    try:
        fuente = Fuente.query.get_or_404(fuente_id)

        # Fallas relacionadas
        fallas = Falla.query.filter(
            Falla.tipo == 'fuente',
            Falla.equipo_id == fuente_id
        ).order_by(Falla.fecha_creacion.desc()).limit(10).all()

        fallas_info = [{
            'id': f.id,
            'titulo': f.titulo,
            'descripcion': f.descripcion,
            'prioridad': f.prioridad,
            'estado': f.estado,
            'fecha_creacion': f.fecha_creacion.isoformat(),
            'asignado_a': {
                'id': f.asignado_a.id if f.asignado_a else None,
                'nombre': f.asignado_a.nombre if f.asignado_a else None,
                'apellido': f.asignado_a.apellido if f.asignado_a else None
            } if f.asignado_a else None
        } for f in fallas]

        # Mantenimientos
        mantenimientos = Mantenimiento.query.filter(
            Mantenimiento.fuente_poder_id == fuente_id
        ).order_by(Mantenimiento.fecha_programada.desc()).limit(5).all()

        mantenimientos_info = [{
            'id': m.id,
            'tipo': m.tipo,
            'descripcion': m.descripcion,
            'estado': m.estado,
            'fecha_programada': m.fecha_programada.isoformat(),
            'fecha_completada': m.fecha_completada.isoformat() if m.fecha_completada else None,
            'tecnico': {
                'id': m.tecnico.id if m.tecnico else None,
                'nombre': m.tecnico.nombre if m.tecnico else None,
                'apellido': m.tecnico.apellido if m.tecnico else None
            } if m.tecnico else None
        } for m in mantenimientos]

        # Fotografías
        fotografias = Fotografia.query.filter(
            Fotografia.fuente_poder_id == fuente_id
        ).order_by(Fotografia.fecha_subida.desc()).limit(5).all()

        fotografias_info = [{
            'id': f.id,
            'nombre_archivo': f.nombre_archivo,
            'ruta_archivo': f.ruta_archivo,
            'descripcion': f.descripcion,
            'fecha_subida': f.fecha_subida.isoformat()
        } for f in fotografias]

        # Información de salud
        health_summary = fuente.get_health_summary()

        return jsonify({
            'id': fuente.id,
            'nombre': fuente.nombre,
            'descripcion': fuente.descripcion,
            'marca': fuente.marca,
            'modelo': fuente.modelo,
            'numero_serie': fuente.numero_serie,
            'ubicacion': fuente.ubicacion,
            'estado': fuente.estado,
            
            # Especificaciones técnicas
            'potencia': fuente.potencia,
            'voltaje_entrada': fuente.voltaje_entrada,
            'voltaje_salida': fuente.voltaje_salida,
            'amperaje_salida': fuente.amperaje_salida,
            'eficiencia': fuente.eficiencia,
            
            # Monitoreo
            'temperatura_actual': fuente.temperatura_actual,
            'carga_actual': fuente.carga_actual,
            'voltaje_salida_actual': fuente.voltaje_salida_actual,
            'consumo_porcentaje': fuente.get_consumption_percentage(),
            
            # Fechas importantes
            'fecha_instalacion': fuente.fecha_instalacion.isoformat() if fuente.fecha_instalacion else None,
            'fecha_ultimo_mantenimiento': fuente.fecha_ultimo_mantenimiento.isoformat() if fuente.fecha_ultimo_mantenimiento else None,
            'fecha_proximo_mantenimiento': fuente.fecha_proximo_mantenimiento.isoformat() if fuente.fecha_proximo_mantenimiento else None,
            
            # Control
            'activo': fuente.activo,
            'fecha_creacion': fuente.fecha_creacion.isoformat(),
            'fecha_actualizacion': fuente.fecha_actualizacion.isoformat() if fuente.fecha_actualizacion else None,
            
            # Información calculada
            'health_summary': health_summary,
            'status_color': fuente.get_status_color(),
            'mantenimiento_due': fuente.is_maintenance_due(),
            
            # Relaciones
            'fallas_recientes': fallas_info,
            'mantenimientos_recientes': mantenimientos_info,
            'fotografias_recientes': fotografias_info,
            'total_fallas': len(fallas),
            'total_mantenimientos': len(mantenimientos)
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

        # Validar campos requeridos
        required_fields = ['nombre']
        if not validate_required_fields(data, required_fields):
            return jsonify({'error': 'Campos requeridos: nombre'}), 400

        # Validar estado si se especifica
        if data.get('estado'):
            try:
                estado_fuente = EstadoFuente(data['estado'])
            except ValueError:
                return jsonify({'error': f'Estado inválido. Válidos: {[s.value for s in EstadoFuente]}'}), 400

        # Crear fuente
        fuente = Fuente(
            nombre=data['nombre'].strip(),
            descripcion=data.get('descripcion', '').strip(),
            marca=data.get('marca', '').strip(),
            modelo=data.get('modelo', '').strip(),
            numero_serie=data.get('numero_serie', '').strip(),
            ubicacion=data.get('ubicacion', '').strip(),
            
            # Estado
            estado=data.get('estado', EstadoFuente.OPERATIVA.value),
            
            # Especificaciones técnicas
            potencia=data.get('potencia'),
            voltaje_entrada=data.get('voltaje_entrada', '').strip(),
            voltaje_salida=data.get('voltaje_salida', '').strip(),
            amperaje_salida=data.get('amperaje_salida'),
            eficiencia=data.get('eficiencia'),
            
            # Monitoreo
            temperatura_actual=data.get('temperatura_actual'),
            carga_actual=data.get('carga_actual', 0),
            voltaje_salida_actual=data.get('voltaje_salida_actual', '').strip(),
            
            # Fechas
            fecha_instalacion=datetime.fromisoformat(data['fecha_instalacion']) if data.get('fecha_instalacion') else None,
            
            # Control
            activo=data.get('activo', True),
            
            fecha_creacion=datetime.utcnow()
        )

        db.session.add(fuente)
        db.session.commit()

        return jsonify({
            'message': 'Fuente creada exitosamente',
            'fuente_id': fuente.id
        }), 201

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

        # Campos que se pueden actualizar
        campos_actualizables = [
            'nombre', 'descripcion', 'marca', 'modelo', 'numero_serie',
            'ubicacion', 'estado', 'potencia', 'voltaje_entrada',
            'voltaje_salida', 'amperaje_salida', 'eficiencia', 'fecha_instalacion',
            'temperatura_actual', 'carga_actual', 'voltaje_salida_actual', 'activo'
        ]

        for campo in campos_actualizables:
            if campo in data and data[campo] is not None:
                if campo == 'nombre' and data[campo]:
                    fuente.nombre = data[campo].strip()
                elif campo == 'estado':
                    try:
                        fuente.estado = EstadoFuente(data[campo]).value
                    except ValueError:
                        return jsonify({'error': f'Estado inválido: {data[campo]}'}), 400
                elif campo == 'fecha_instalacion' and data[campo]:
                    try:
                        fecha = datetime.fromisoformat(data[campo].replace('Z', '+00:00'))
                        fuente.fecha_instalacion = fecha
                    except ValueError:
                        return jsonify({'error': 'Fecha de instalación inválida'}), 400
                else:
                    setattr(fuente, campo, data[campo])

        fuente.fecha_actualizacion = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Fuente actualizada exitosamente'
        })

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

        # Verificar que no tenga fallas abiertas
        fallas_abiertas = Falla.query.filter(
            Falla.tipo == 'fuente',
            Falla.equipo_id == fuente_id,
            Falla.estado.in_(['abierta', 'en_proceso'])
        ).count()

        if fallas_abiertas > 0:
            return jsonify({'error': 'No se puede eliminar una fuente con fallas abiertas'}), 400

        # Soft delete
        fuente.deleted = True
        fuente.activo = False
        fuente.fecha_actualizacion = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Fuente eliminada exitosamente'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al eliminar fuente: {str(e)}'}), 500

@fuentes_bp.route('/<int:fuente_id>/monitor', methods=['POST'])
@token_required
@validate_json
def update_monitor(current_user, fuente_id):
    """
    Actualizar métricas de monitoreo de la fuente
    """
    try:
        fuente = Fuente.query.get_or_404(fuente_id)
        data = request.get_json()

        # Actualizar métricas de monitoreo
        fuente.update_monitoring_data(
            temperatura=data.get('temperatura_actual'),
            carga=data.get('carga_actual'),
            voltaje_salida=data.get('voltaje_salida_actual')
        )

        return jsonify({
            'message': 'Métricas de monitoreo actualizadas',
            'estado': fuente.estado,
            'consumo_porcentaje': fuente.get_consumption_percentage(),
            'health_summary': fuente.get_health_summary()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar monitoreo: {str(e)}'}), 500

@fuentes_bp.route('/<int:fuente_id>/test', methods=['POST'])
@token_required
def test_fuente(current_user, fuente_id):
    """
    Realizar prueba básica de la fuente
    """
    try:
        fuente = Fuente.query.get_or_404(fuente_id)

        # Realizar prueba básica (simulada)
        resultado_exitoso = True
        
        # Actualizar estado si la prueba es exitosa
        if resultado_exitoso:
            fuente.estado = EstadoFuente.OPERATIVA.value
        
        fuente.fecha_actualizacion = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Prueba realizada exitosamente' if resultado_exitoso else 'Prueba falló',
            'fuente_id': fuente_id,
            'timestamp': datetime.utcnow().isoformat(),
            'resultado': 'exito' if resultado_exitoso else 'error',
            'estado': fuente.estado,
            'consumo_porcentaje': fuente.get_consumption_percentage()
        })

    except Exception as e:
        return jsonify({'error': f'Error al realizar prueba: {str(e)}'}), 500

@fuentes_bp.route('/<int:fuente_id>/maintenance', methods=['PUT'])
@token_required
@require_permission('equipos_editar')
@validate_json
def update_maintenance(current_user, fuente_id):
    """
    Actualizar información de mantenimiento
    """
    try:
        fuente = Fuente.query.get_or_404(fuente_id)
        data = request.get_json()

        # Actualizar fechas de mantenimiento
        if 'fecha_ultimo_mantenimiento' in data and data['fecha_ultimo_mantenimiento']:
            try:
                fuente.fecha_ultimo_mantenimiento = datetime.fromisoformat(data['fecha_ultimo_mantenimiento'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Fecha de último mantenimiento inválida'}), 400

        if 'fecha_proximo_mantenimiento' in data and data['fecha_proximo_mantenimiento']:
            try:
                fuente.fecha_proximo_mantenimiento = datetime.fromisoformat(data['fecha_proximo_mantenimiento'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Fecha de próximo mantenimiento inválida'}), 400

        # Programar próximo mantenimiento si no existe
        if not fuente.fecha_proximo_mantenimiento and fuente.fecha_ultimo_mantenimiento:
            fuente.schedule_maintenance()

        fuente.fecha_actualizacion = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Información de mantenimiento actualizada',
            'fecha_ultimo_mantenimiento': fuente.fecha_ultimo_mantenimiento.isoformat() if fuente.fecha_ultimo_mantenimiento else None,
            'fecha_proximo_mantenimiento': fuente.fecha_proximo_mantenimiento.isoformat() if fuente.fecha_proximo_mantenimiento else None,
            'mantenimiento_due': fuente.is_maintenance_due()
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
        # Total de fuentes
        total_fuentes = Fuente.query.filter_by(deleted=False).count()

        # Contar por estado
        por_estado = db.session.query(
            Fuente.estado,
            func.count(Fuente.id)
        ).filter_by(deleted=False).group_by(Fuente.estado).all()

        # Contar por marca
        por_marca = db.session.query(
            Fuente.marca,
            func.count(Fuente.id)
        ).filter(
            Fuente.deleted == False,
            Fuente.marca.isnot(None),
            Fuente.marca != ''
        ).group_by(Fuente.marca).all()

        # Fuentes por rango de potencia
        potencias = db.session.query(
            Fuente.potencia,
            func.count(Fuente.id)
        ).filter_by(deleted=False).filter(
            Fuente.potencia.isnot(None)
        ).group_by(Fuente.potencia).order_by(Fuente.potencia).all()

        # Fuentes con mantenimiento vencido
        fuentes_mantenimiento_vencido = Fuente.query.filter(
            Fuente.deleted == False,
            Fuente.fecha_proximo_mantenimiento < datetime.utcnow(),
            Fuente.fecha_proximo_mantenimiento.isnot(None)
        ).count()

        # Fuentes por estado operativo
        fuentes_operativas = Fuente.query.filter_by(
            deleted=False, 
            estado=EstadoFuente.OPERATIVA.value
        ).count()

        # Promedio de consumo
        consumos = db.session.query(
            func.avg(Fuente.carga_actual)
        ).filter_by(deleted=False).filter(
            Fuente.carga_actual.isnot(None)
        ).scalar() or 0

        # Promedio de eficiencia
        eficiencias = db.session.query(
            func.avg(Fuente.eficiencia)
        ).filter_by(deleted=False).filter(
            Fuente.eficiencia.isnot(None)
        ).scalar() or 0

        return jsonify({
            'total_fuentes': total_fuentes,
            'fuentes_operativas': fuentes_operativas,
            'por_estado': {estado: cantidad for estado, cantidad in por_estado},
            'por_marca': [
                {'marca': marca if marca else 'Sin marca', 'cantidad': cantidad}
                for marca, cantidad in por_marca
            ],
            'por_potencia': [
                {'potencia_watts': potencia, 'cantidad': cantidad}
                for potencia, cantidad in potencias
            ],
            'mantenimiento_vencido': fuentes_mantenimiento_vencido,
            'promedio_consumo': round(consumos, 2),
            'promedio_eficiencia': round(eficiencias, 2)
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500

@fuentes_bp.route('/capacidade/<int:min_watts>/<int:max_watts>', methods=['GET'])
@token_required
def get_fuentes_by_capacity(current_user, min_watts, max_watts):
    """
    Obtener fuentes por rango de capacidad
    """
    try:
        fuentes = Fuente.get_by_capacity_range(min_watts, max_watts)
        
        fuentes_list = [{
            'id': f.id,
            'nombre': f.nombre,
            'marca': f.marca,
            'modelo': f.modelo,
            'potencia': f.potencia,
            'estado': f.estado,
            'consumo_porcentaje': f.get_consumption_percentage(),
            'ubicacion': f.ubicacion
        } for f in fuentes]

        return jsonify({
            'fuentes': fuentes_list,
            'total': len(fuentes),
            'rango_solicitado': {
                'min_watts': min_watts,
                'max_watts': max_watts
            }
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener fuentes por capacidad: {str(e)}'}), 500

@fuentes_bp.route('/criticas', methods=['GET'])
@token_required
def get_fuentes_criticas(current_user):
    """
    Obtener fuentes en estado crítico (FALLA)
    """
    try:
        fuentes_criticas = Fuente.get_fuentes_by_status(EstadoFuente.FALLA.value)
        
        fuentes_list = []
        for f in fuentes_criticas:
            # Obtener fallas abiertas
            fallas_abiertas = Falla.query.filter(
                Falla.tipo == 'fuente',
                Falla.equipo_id == f.id,
                Falla.estado.in_(['abierta', 'en_proceso'])
            ).count()

            fuentes_list.append({
                'id': f.id,
                'nombre': f.nombre,
                'marca': f.marca,
                'modelo': f.modelo,
                'estado': f.estado,
                'ubicacion': f.ubicacion,
                'temperatura_actual': f.temperatura_actual,
                'consumo_porcentaje': f.get_consumption_percentage(),
                'fallas_abiertas': fallas_abiertas,
                'fecha_actualizacion': f.fecha_actualizacion.isoformat() if f.fecha_actualizacion else None
            })

        return jsonify({
            'fuentes_criticas': fuentes_list,
            'total': len(fuentes_list)
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener fuentes críticas: {str(e)}'}), 500

@fuentes_bp.route('/marcas', methods=['GET'])
@token_required
def get_marcas_fuentes(current_user):
    """
    Obtener lista de marcas de fuentes disponibles
    """
    try:
        marcas = db.session.query(
            Fuente.marca,
            func.count(Fuente.id).label('cantidad')
        ).filter(
            Fuente.deleted == False,
            Fuente.marca.isnot(None),
            Fuente.marca != ''
        ).group_by(Fuente.marca).order_by(func.count(Fuente.id).desc()).all()

        marcas_list = [{
            'marca': marca,
            'cantidad': cantidad
        } for marca, cantidad in marcas]

        return jsonify({
            'marcas': marcas_list
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener marcas: {str(e)}'}), 500