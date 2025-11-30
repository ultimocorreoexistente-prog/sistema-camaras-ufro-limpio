"""
Rutas CRUD para el manejo de Cámaras
"""
from flask import request, jsonify
from sqlalchemy import or_, and_, desc, func
from datetime import datetime, timedelta
from .. import camaras_bp
from models import Camara, Falla, Usuario, db
from utils.validators import validate_json, validate_required_fields, validate_pagination
from utils.decorators import token_required, require_permission

@api_bp.route('', methods=['GET'])
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
        tipo_camara = request.args.get('tipo_camara', '')
        marca = request.args.get('marca', '')
        modelo = request.args.get('modelo', '')
        search = request.args.get('search', '')
        fecha_desde = request.args.get('fecha_desde', '')
        fecha_hasta = request.args.get('fecha_hasta', '')
        orden = request.args.get('orden', 'nombre')
        direccion = request.args.get('direccion', 'asc')

        # Query base - solo cámaras activas
        query = Camara.query.filter(Camara.activo == True)

        # Aplicar filtros
        if estado:
            query = query.filter(Camara.estado == estado)
        if tipo_camara:
            query = query.filter(Camara.tipo_camara == tipo_camara)
        if marca:
            query = query.filter(Camara.marca.like(f'%{marca}%'))
        if modelo:
            query = query.filter(Camara.modelo.like(f'%{modelo}%'))
        if search:
            query = query.filter(
                or_(
                    Camara.nombre.like(f'%{search}%'),
                    Camara.codigo.like(f'%{search}%'),
                    Camara.ubicacion.like(f'%{search}%'),
                    Camara.ip_address.like(f'%{search}%'),
                    Camara.observaciones.like(f'%{search}%')
                )
            )
        if fecha_desde:
            try:
                fecha_desde_dt = datetime.fromisoformat(fecha_desde.replace('Z', '+00:00'))
                query = query.filter(Camara.fecha_instalacion >= fecha_desde_dt)
            except ValueError:
                pass
        if fecha_hasta:
            try:
                fecha_hasta_dt = datetime.fromisoformat(fecha_hasta.replace('Z', '+00:00'))
                query = query.filter(Camara.fecha_instalacion <= fecha_hasta_dt)
            except ValueError:
                pass

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
                Falla.estado.in_(['abierta', 'en_proceso']),
                Falla.activo == True
            ).count()

            camaras.append({
                'id': c.id,
                'codigo': c.codigo,
                'nombre': c.nombre,
                'modelo': c.modelo,
                'marca': c.marca,
                'tipo_camara': c.tipo_camara,
                'estado': c.estado,
                'ip_address': c.ip_address,
                'mac_address': c.mac_address,
                'ubicacion': getattr(c, 'ubicacion', ''),
                'fecha_instalacion': c.fecha_instalacion.isoformat() if c.fecha_instalacion else None,
                'observaciones': c.observaciones,
                'fallas_abiertas': fallas_abiertas,
                'fecha_creacion': c.fecha_creacion.isoformat(),
                'fecha_actualizacion': c.fecha_actualizacion.isoformat() if c.fecha_actualizacion else None
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
                'tipo_camara': tipo_camara,
                'marca': marca,
                'modelo': modelo,
                'search': search,
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
                'orden': orden,
                'direccion': direccion
            }
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener cámaras: {str(e)}'}), 500

@api_bp.route('/<int:camaras_id>', methods=['GET'])
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
            Falla.equipo_id == camaras_id,
            Falla.activo == True
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
            'codigo': camara.codigo,
            'nombre': camara.nombre,
            'modelo': camara.modelo,
            'marca': camara.marca,
            'tipo_camara': camara.tipo_camara,
            'estado': camara.estado,
            'ip_address': camara.ip_address,
            'mac_address': camara.mac_address,
            'ubicacion': getattr(camara, 'ubicacion', ''),
            'fecha_instalacion': camara.fecha_instalacion.isoformat() if camara.fecha_instalacion else None,
            'observaciones': camara.observaciones,
            'fecha_creacion': camara.fecha_creacion.isoformat(),
            'fecha_actualizacion': camara.fecha_actualizacion.isoformat() if camara.fecha_actualizacion else None,
            'fallas_recientes': fallas_info,
            'total_fallas': len(fallas_info),
            'fallas_abiertas': len([f for f in fallas if f.estado in ['abierta', 'en_proceso']])
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener cámara: {str(e)}'}), 500

@api_bp.route('', methods=['POST'])
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
        required_fields = ['codigo', 'nombre', 'tipo_camara']
        if not validate_required_fields(data, required_fields):
            return jsonify({'error': 'Campos requeridos: codigo, nombre, tipo_camara'}), 400

        # Validar tipo de cámara
        tipos_validos = ['IP', 'Analogica', 'HDCVI', 'AHD']
        if data['tipo_camara'] not in tipos_validos:
            return jsonify({'error': f'Tipo de cámara debe ser uno de: {tipos_validos}'}), 400

        # Validar formato de IP si se proporciona
        if data.get('ip_address'):
            import ipaddress
            try:
                ipaddress.ip_address(data['ip_address'])
            except ValueError:
                return jsonify({'error': 'Dirección IP inválida'}), 400

        # Verificar que no existe otra cámara con el mismo código
        codigo_existe = Camara.query.filter(
            Camara.codigo == data['codigo'],
            Camara.activo == True
        ).first()

        if codigo_existe:
            return jsonify({'error': 'Ya existe una cámara con ese código'}), 400

        # Verificar que no existe otra cámara con la misma IP
        if data.get('ip_address'):
            ip_existe = Camara.query.filter(
                Camara.ip_address == data['ip_address'],
                Camara.activo == True
            ).first()

            if ip_existe:
                return jsonify({'error': 'Ya existe una cámara con esa dirección IP'}), 400

        # Crear cámara
        camara = Camara(
            codigo=data['codigo'].strip(),
            nombre=data['nombre'].strip(),
            modelo=data.get('modelo', '').strip(),
            marca=data.get('marca', '').strip(),
            tipo_camara=data['tipo_camara'],
            estado=data.get('estado', 'activo'),
            ip_address=data.get('ip_address'),
            mac_address=data.get('mac_address'),
            fecha_instalacion=datetime.fromisoformat(data['fecha_instalacion']) if data.get('fecha_instalacion') else datetime.utcnow(),
            observaciones=data.get('observaciones', '').strip(),
            activo=True,
            fecha_creacion=datetime.utcnow()
        )

        db.session.add(camara)
        db.session.commit()

        return jsonify({
            'message': 'Cámara creada exitosamente',
            'camara_id': camara.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear cámara: {str(e)}'}), 500

@api_bp.route('/<int:camaras_id>', methods=['PUT'])
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

        # Validar tipo de cámara si se proporciona
        if 'tipo_camara' in data:
            tipos_validos = ['IP', 'Analogica', 'HDCVI', 'AHD']
            if data['tipo_camara'] not in tipos_validos:
                return jsonify({'error': f'Tipo de cámara debe ser uno de: {tipos_validos}'}), 400

        # Validar formato de IP si se proporciona
        if 'ip_address' in data and data['ip_address']:
            import ipaddress
            try:
                ipaddress.ip_address(data['ip_address'])
            except ValueError:
                return jsonify({'error': 'Dirección IP inválida'}), 400

        # Campos actualizables
        campos_actualizables = [
            'codigo', 'nombre', 'modelo', 'marca', 'tipo_camara', 'estado',
            'ip_address', 'mac_address', 'ubicacion', 'fecha_instalacion', 'observaciones'
        ]

        for campo in campos_actualizables:
            if campo in data and data[campo] is not None:
                if campo == 'codigo' and data[campo].strip():
                    # Verificar que no existe otra cámara con el mismo código
                    codigo_existe = Camara.query.filter(
                        Camara.codigo == data[campo],
                        Camara.id != camaras_id,
                        Camara.activo == True
                    ).first()

                    if codigo_existe:
                        return jsonify({'error': 'Ya existe otra cámara con ese código'}), 400

                    camara.codigo = data[campo].strip()
                elif campo == 'nombre' and data[campo].strip():
                    camara.nombre = data[campo].strip()
                elif campo == 'modelo':
                    camara.modelo = data[campo].strip()
                elif campo == 'marca':
                    camara.marca = data[campo].strip()
                elif campo == 'tipo_camara':
                    camara.tipo_camara = data[campo]
                elif campo == 'estado':
                    estados_validos = ['activo', 'inactivo', 'mantenimiento', 'fuera_servicio']
                    if data[campo] not in estados_validos:
                        return jsonify({'error': f'Estado debe ser uno de: {estados_validos}'}), 400
                    camara.estado = data[campo]
                elif campo == 'ip_address':
                    # Verificar que no existe otra cámara con la misma IP
                    ip_existe = Camara.query.filter(
                        Camara.ip_address == data[campo],
                        Camara.id != camaras_id,
                        Camara.activo == True
                    ).first()

                    if ip_existe:
                        return jsonify({'error': 'Ya existe otra cámara con esa dirección IP'}), 400

                    camara.ip_address = data[campo]
                elif campo == 'mac_address':
                    camara.mac_address = data[campo]
                elif campo == 'ubicacion':
                    camara.ubicacion = data[campo].strip()
                elif campo == 'fecha_instalacion':
                    if data[campo]:
                        camara.fecha_instalacion = datetime.fromisoformat(data[campo])
                    else:
                        camara.fecha_instalacion = None
                elif campo == 'observaciones':
                    camara.observaciones = data[campo].strip()

        camara.fecha_actualizacion = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Cámara actualizada exitosamente'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar cámara: {str(e)}'}), 500

@api_bp.route('/<int:camaras_id>', methods=['DELETE'])
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
            Falla.estado.in_(['abierta', 'en_proceso']),
            Falla.activo == True
        ).count()

        if fallas_abiertas > 0:
            return jsonify({'error': 'No se puede eliminar una cámara con fallas abiertas'}), 400

        # Soft delete
        camara.activo = False
        camara.fecha_actualizacion = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Cámara eliminada exitosamente'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al eliminar cámara: {str(e)}'}), 500

@api_bp.route('/<int:camaras_id>/cambiar-estado', methods=['POST'])
@token_required
@require_permission('equipos_editar')
@validate_json
def cambiar_estado_camara(current_user, camaras_id):
    """
    Cambiar el estado de una cámara
    """
    try:
        camara = Camara.query.get_or_404(camaras_id)
        data = request.get_json()

        # Validar nuevo estado
        estados_validos = ['activo', 'inactivo', 'mantenimiento', 'fuera_servicio']
        if 'estado' not in data or data['estado'] not in estados_validos:
            return jsonify({'error': f'Estado debe ser uno de: {estados_validos}'}), 400

        estado_anterior = camara.estado
        camara.estado = data['estado']
        camara.fecha_actualizacion = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Estado de cámara actualizado exitosamente',
            'nuevo_estado': camara.estado,
            'estado_anterior': estado_anterior
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al cambiar estado: {str(e)}'}), 500

@api_bp.route('/buscar-ip/<ip_address>', methods=['GET'])
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
            'codigo': camara.codigo,
            'nombre': camara.nombre,
            'ip_address': camara.ip_address,
            'estado': camara.estado,
            'ubicacion': getattr(camara, 'ubicacion', ''),
            'fecha_instalacion': camara.fecha_instalacion.isoformat() if camara.fecha_instalacion else None
        })

    except Exception as e:
        return jsonify({'error': f'Error al buscar cámara: {str(e)}'}), 500

@api_bp.route('/estadisticas', methods=['GET'])
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
        ).filter(Camara.activo == True).group_by(Camara.estado).all()

        # Total por tipo
        por_tipo = db.session.query(
            Camara.tipo_camara,
            func.count(Camara.id)
        ).filter(Camara.activo == True).group_by(Camara.tipo_camara).all()

        # Total por marca
        por_marca = db.session.query(
            Camara.marca,
            func.count(Camara.id)
        ).filter(
            Camara.activo == True,
            Camara.marca.isnot(None),
            Camara.marca != ''
        ).group_by(Camara.marca).all()

        # Cámaras con fallas abiertas
        camaras_con_fallas = db.session.query(
            Camara.id,
            Camara.nombre
        ).join(
            Falla, and_(
                Falla.tipo == 'camara',
                Falla.equipo_id == Camara.id,
                Falla.estado.in_(['abierta', 'en_proceso']),
                Falla.activo == True
            )
        ).filter(Camara.activo == True).all()

        # Total de cámaras
        total_camaras = Camara.query.filter_by(activo=True).count()

        return jsonify({
            'total_camaras': total_camaras,
            'por_estado': {estado: cantidad for estado, cantidad in por_estado},
            'por_tipo': {tipo: cantidad for tipo, cantidad in por_tipo},
            'por_marca': {marca: cantidad for marca, cantidad in por_marca},
            'camaras_con_fallas': len(camaras_con_fallas),
            'camaras_funcionando': total_camaras - len(camaras_con_fallas),
            'porcentaje_funcionamiento': round(((total_camaras - len(camaras_con_fallas)) / total_camaras * 100) if total_camaras > 0 else 0, 1),
            'detalle_camaras_con_fallas': [
                {'id': cam_id, 'nombre': nombre} for cam_id, nombre in camaras_con_fallas
            ]
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500