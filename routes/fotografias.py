"""
Rutas CRUD para el manejo de NVRs
"""
from flask import request, jsonify
from sqlalchemy import or_, and_, desc, func
from datetime import datetime, timedelta
from .. import nvr_bp
from .auth import token_required
from models import Nvr, Falla, Camara, db
from utils.validators import validate_json, validate_required_fields
from utils.decorators import require_permission

@nvr_bp.route('', methods=['GET'])
@token_required
def get_nvrs(current_user):
    """
    Obtener lista de NVRs con filtros y paginación
    """
    try:
        # Validar paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

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
        query = Nvr.query.filter_by(activo=True)

        # Aplicar filtros
        if estado:
            query = query.filter(Nvr.estado == estado)
        if ubicacion:
            query = query.filter(Nvr.ubicacion.like(f'%{ubicacion}%'))
        if search:
            query = query.filter(
                or_(
                    Nvr.nombre.like(f'%{search}%'),
                    Nvr.descripcion.like(f'%{search}%'),
                    Nvr.ip_address.like(f'%{search}%')
                )
            )
        if marca:
            query = query.filter(Nvr.marca.like(f'%{marca}%'))
        if modelo:
            query = query.filter(Nvr.modelo.like(f'%{modelo}%'))

        # Ordenamiento
        orden_field = getattr(Nvr, orden, Nvr.nombre)
        if direccion == 'desc':
            query = query.order_by(orden_field.desc())
        else:
            query = query.order_by(orden_field.asc())

        # Paginación
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        nvrs = []
        for n in pagination.items:
            # Verificar si el NVR tiene fallas abiertas
            fallas_abiertas = Falla.query.filter(
                Falla.tipo == 'nvr',
                Falla.equipo_id == n.id,
                Falla.estado.in_(['abierta', 'en_proceso'])
            ).count()

            # Obtener cámaras conectadas al NVR
            camaras_conectadas = Camara.query.filter(
                Camara.nvr_id == n.id,
                Camara.activo == True
            ).count()

            nvrs.append({
                'id': n.id,
                'nombre': n.nombre,
                'descripcion': n.descripcion,
                'ip_address': n.ip_address,
                'puerto': n.puerto,
                'usuario': n.usuario,
                'password': '[ENCRYPTED]',  # No mostrar la contraseña real
                'marca': n.marca,
                'modelo': n.modelo,
                'numero_serie': n.numero_serie,
                'ubicacion': n.ubicacion,
                'estado': n.estado,
                'canales': n.canales,
                'capacidad_almacenamiento_gb': n.capacidad_almacenamiento_gb,
                'resolucion_maxima': n.resolucion_maxima,
                'fecha_instalacion': n.fecha_instalacion.isoformat() if n.fecha_instalacion else None,
                'fecha_ultimo_mantenimiento': n.fecha_ultimo_mantenimiento.isoformat() if n.fecha_ultimo_mantenimiento else None,
                'fallas_abiertas': fallas_abiertas,
                'camaras_conectadas': camaras_conectadas,
                'capacidad_usada_gb': getattr(n, 'capacidad_usada_gb', 0),
                'created_at': n.created_at.isoformat(),
                'updated_at': n.updated_at.isoformat() if n.updated_at else None
            })

        return jsonify({
            'nvrs': nvrs,
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
        return jsonify({'error': f'Error al obtener NVRs: {str(e)}'}), 500

@nvr_bp.route('/<int:nvr_id>', methods=['GET'])
@token_required
def get_nvr(current_user, nvr_id):
    """
    Obtener detalle de un NVR específico
    """
    try:
        nvr = Nvr.query.get_or_404(nvr_id)

        # Obtener fallas relacionadas
        fallas = Falla.query.filter(
            Falla.tipo == 'nvr',
            Falla.equipo_id == nvr_id
        ).order_by(Falla.fecha_creacion.desc()).limit(10).all()

        # Obtener cámaras conectadas al NVR
        camaras = Camara.query.filter_by(nvr_id=nvr_id, activo=True).all()

        fallas_info = [{
            'id': f.id,
            'titulo': f.titulo,
            'estado': f.estado,
            'prioridad': f.prioridad,
            'fecha_creacion': f.fecha_creacion.isoformat()
        } for f in fallas]

        camaras_info = [{
            'id': c.id,
            'nombre': c.nombre,
            'ip_address': c.ip_address,
            'ubicacion': c.ubicacion,
            'estado': c.estado
        } for c in camaras]

        return jsonify({
            'id': nvr.id,
            'nombre': nvr.nombre,
            'descripcion': nvr.descripcion,
            'ip_address': nvr.ip_address,
            'puerto': nvr.puerto,
            'usuario': nvr.usuario,
            'password': '[ENCRYPTED]',  # No mostrar contraseña real
            'marca': nvr.marca,
            'modelo': nvr.modelo,
            'numero_serie': nvr.numero_serie,
            'ubicacion': nvr.ubicacion,
            'estado': nvr.estado,
            'canales': nvr.canales,
            'capacidad_almacenamiento_gb': nvr.capacidad_almacenamiento_gb,
            'resolucion_maxima': nvr.resolucion_maxima,
            'fecha_instalacion': nvr.fecha_instalacion.isoformat() if nvr.fecha_instalacion else None,
            'fecha_ultimo_mantenimiento': nvr.fecha_ultimo_mantenimiento.isoformat() if nvr.fecha_ultimo_mantenimiento else None,
            'created_at': nvr.created_at.isoformat(),
            'updated_at': nvr.updated_at.isoformat() if nvr.updated_at else None,
            'fallas_recientes': fallas_info,
            'camaras_conectadas': camaras_info,
            'total_fallas': len(fallas_info),
            'fallas_abiertas': len([f for f in fallas if f.estado in ['abierta', 'en_proceso']]),
            'total_camaras': len(camaras_info)
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener NVR: {str(e)}'}), 500

@nvr_bp.route('', methods=['POST'])
@token_required
@require_permission('equipos_crear')
@validate_json
def create_nvr(current_user):
    """
    Crear un nuevo NVR
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

        # Verificar que no existe otro NVR con la misma IP
        ip_existe = Nvr.query.filter(
            Nvr.ip_address == data['ip_address'],
            Nvr.activo == True
        ).first()

        if ip_existe:
            return jsonify({'error': 'Ya existe un NVR con esa dirección IP'}), 400

        # Crear NVR
        nvr = Nvr(
            nombre=data['nombre'].strip(),
            descripcion=data.get('descripcion', '').strip(),
            ip_address=data['ip_address'],
            puerto=data.get('puerto', 8080),
            usuario=data.get('usuario', ''),
            password=data.get('password', ''),  # En producción, cifrar
            marca=data.get('marca', '').strip(),
            modelo=data.get('modelo', '').strip(),
            numero_serie=data.get('numero_serie', '').strip(),
            ubicacion=data.get('ubicacion', '').strip(),
            estado=data.get('estado', 'operativo'),
            canales=data.get('canales', 4),
            capacidad_almacenamiento_gb=data.get('capacidad_almacenamiento_gb', 1000),
            resolucion_maxima=data.get('resolucion_maxima', ''),
            fecha_instalacion=datetime.fromisoformat(data['fecha_instalacion']) if data.get('fecha_instalacion') else None,
            activo=True,
            created_at=datetime.utcnow()
        )

        db.session.add(nvr)
        db.session.commit()

        return jsonify({
            'message': 'NVR creado exitosamente',
            'nvr_id': nvr.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear NVR: {str(e)}'}), 500

@nvr_bp.route('/<int:nvr_id>', methods=['PUT'])
@token_required
@require_permission('equipos_editar')
@validate_json
def update_nvr(current_user, nvr_id):
    """
    Actualizar un NVR existente
    """
    try:
        nvr = Nvr.query.get_or_404(nvr_id)
        data = request.get_json()

        # Campos actualizables
        campos_actualizables = [
            'nombre', 'descripcion', 'ip_address', 'puerto', 'usuario', 'password',
            'marca', 'modelo', 'numero_serie', 'ubicacion', 'estado', 'canales',
            'capacidad_almacenamiento_gb', 'resolucion_maxima', 'fecha_instalacion'
        ]

        for campo in campos_actualizables:
            if campo in data and data[campo] is not None:
                if campo == 'nombre' and data[campo].strip():
                    nvr.nombre = data[campo].strip()
                elif campo == 'descripcion':
                    nvr.descripcion = data[campo].strip()
                elif campo == 'ip_address':
                    # Validar formato de IP
                    import ipaddress
                    try:
                        ipaddress.ip_address(data[campo])
                        # Verificar que no existe otro NVR con la misma IP
                        ip_existe = Nvr.query.filter(
                            Nvr.ip_address == data[campo],
                            Nvr.id != nvr_id,
                            Nvr.activo == True
                        ).first()
                        if ip_existe:
                            return jsonify({'error': 'Ya existe otro NVR con esa dirección IP'}), 400
                        nvr.ip_address = data[campo]
                    except ValueError:
                        return jsonify({'error': 'Dirección IP inválida'}), 400
                elif campo == 'puerto':
                    nvr.puerto = data[campo]
                elif campo == 'usuario':
                    nvr.usuario = data[campo].strip()
                elif campo == 'password':
                    nvr.password = data[campo]  # En producción, cifrar
                elif campo == 'marca':
                    nvr.marca = data[campo].strip()
                elif campo == 'modelo':
                    nvr.modelo = data[campo].strip()
                elif campo == 'numero_serie':
                    nvr.numero_serie = data[campo].strip()
                elif campo == 'ubicacion':
                    nvr.ubicacion = data[campo].strip()
                elif campo == 'estado':
                    estados_validos = ['operativo', 'mantenimiento', 'fuera_servicio', 'deshabilitado']
                    if data[campo] not in estados_validos:
                        return jsonify({'error': f'Estado debe ser uno de: {estados_validos}'}), 400
                    nvr.estado = data[campo]
                elif campo == 'canales':
                    nvr.canales = data[campo]
                elif campo == 'capacidad_almacenamiento_gb':
                    nvr.capacidad_almacenamiento_gb = data[campo]
                elif campo == 'resolucion_maxima':
                    nvr.resolucion_maxima = data[campo].strip()
                elif campo == 'fecha_instalacion':
                    nvr.fecha_instalacion = datetime.fromisoformat(data[campo]) if data[campo] else None

        nvr.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'NVR actualizado exitosamente'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar NVR: {str(e)}'}), 500

@nvr_bp.route('/<int:nvr_id>', methods=['DELETE'])
@token_required
@require_permission('equipos_eliminar')
def delete_nvr(current_user, nvr_id):
    """
    Eliminar un NVR (soft delete)
    """
    try:
        nvr = Nvr.query.get_or_404(nvr_id)

        # Verificar que no tiene fallas abiertas
        fallas_abiertas = Falla.query.filter(
            Falla.tipo == 'nvr',
            Falla.equipo_id == nvr_id,
            Falla.estado.in_(['abierta', 'en_proceso'])
        ).count()

        if fallas_abiertas > 0:
            return jsonify({'error': 'No se puede eliminar un NVR con fallas abiertas'}), 400

        # Verificar que no tiene cámaras conectadas
        camaras_conectadas = Camara.query.filter_by(nvr_id=nvr_id, activo=True).count()

        if camaras_conectadas > 0:
            return jsonify({'error': f'No se puede eliminar un NVR con {camaras_conectadas} cámaras conectadas'}), 400

        nvr.activo = False
        nvr.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'NVR eliminado exitosamente'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al eliminar NVR: {str(e)}'}), 500

@nvr_bp.route('/<int:nvr_id>/conectar-camara', methods=['POST'])
@token_required
@require_permission('equipos_editar')
@validate_json
def conectar_camara_nvr(current_user, nvr_id):
    """
    Conectar una cámara a un NVR
    """
    try:
        nvr = Nvr.query.get_or_404(nvr_id)
        data = request.get_json()

        if 'camara_id' not in data:
            return jsonify({'error': 'camara_id es requerido'}), 400

        # Verificar que la cámara existe
        camara = Camara.query.filter_by(id=data['camara_id'], activo=True).first()

        if not camara:
            return jsonify({'error': 'Cámara no encontrada'}), 404

        # Verificar que el NVR tiene canales disponibles
        camaras_conectadas = Camara.query.filter_by(nvr_id=nvr_id, activo=True).count()

        if camaras_conectadas >= nvr.canales:
            return jsonify({'error': 'NVR sin canales disponibles'}), 400

        # Conectar cámara al NVR
        camara.nvr_id = nvr_id
        camara.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Cámara conectada al NVR exitosamente',
            'nvr_id': nvr_id,
            'camara_id': camara.id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al conectar cámara: {str(e)}'}), 500

@nvr_bp.route('/<int:nvr_id>/desconectar-camara/<int:camara_id>', methods=['DELETE'])
@token_required
@require_permission('equipos_editar')
def desconectar_camara_nvr(current_user, nvr_id, camara_id):
    """
    Desconectar una cámara de un NVR
    """
    try:
        # Verificar que la cámara está conectada al NVR
        camara = Camara.query.filter_by(id=camara_id, nvr_id=nvr_id, activo=True).first()

        if not camara:
            return jsonify({'error': 'Cámara no encontrada o no está conectada a este NVR'}), 404

        # Desconectar cámara del NVR
        camara.nvr_id = None
        camara.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Cámara desconectada del NVR exitosamente'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al desconectar cámara: {str(e)}'}), 500

@nvr_bp.route('/<int:nvr_id>/test-conexion', methods=['POST'])
@token_required
def test_conexion_nvr(current_user, nvr_id):
    """
    Probar conexión con el NVR
    """
    try:
        nvr = Nvr.query.get_or_404(nvr_id)

        # Simular test de conexión (en producción sería una verificación real)
        resultado = {
            'nvr_id': nvr_id,
            'ip_address': nvr.ip_address,
            'puerto': nvr.puerto,
            'timestamp': datetime.utcnow().isoformat(),
            'resultado': 'exito',  # 'exito', 'error', 'timeout'
            'mensaje': 'Conexión exitosa',
            'tiempo_respuesta_ms': 45,  # Simulado
            'version_firmware': 'v.1.5',
            'espacio_libre_gb': 850,  # Simulado
            'canales_activos': 4
        }

        # En una implementación real, aquí se haría:
        # - Ping a la IP
        # - Verificar puerto específico
        # - Test de credenciales
        # - Obtener información del sistema

        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'error': f'Error al probar conexión: {str(e)}'
        }), 500

@nvr_bp.route('/<int:nvr_id>/mantenimiento', methods=['PUT'])
@token_required
@require_permission('equipos_editar')
def actualizar_mantenimiento_nvr(current_user, nvr_id):
    """
    Actualizar fecha de último mantenimiento
    """
    try:
        nvr = Nvr.query.get_or_404(nvr_id)

        nvr.fecha_ultimo_mantenimiento = datetime.utcnow()
        nvr.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Fecha de mantenimiento actualizada',
            'fecha_ultimo_mantenimiento': nvr.fecha_ultimo_mantenimiento.isoformat()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar mantenimiento: {str(e)}'}), 500

@nvr_bp.route('/estadisticas', methods=['GET'])
@token_required
def get_nvrs_estadisticas(current_user):
    """
    Obtener estadísticas de NVRs
    """
    try:
        # Total por estado
        por_estado = db.session.query(
            Nvr.estado,
            func.count(Nvr.id)
        ).filter_by(activo=True).group_by(Nvr.estado).all()

        # Total por marca
        por_marca = db.session.query(
            Nvr.marca,
            func.count(Nvr.id)
        ).filter(
            Nvr.activo == True,
            Nvr.marca != ''
        ).group_by(Nvr.marca).all()

        # Total por ubicación
        por_ubicacion = db.session.query(
            Nvr.ubicacion,
            func.count(Nvr.id)
        ).filter(
            Nvr.activo == True,
            Nvr.ubicacion != ''
        ).group_by(Nvr.ubicacion).all()

        # NVRs con fallas abiertas
        nvrs_con_fallas = db.session.query(
            Nvr.id,
            Nvr.nombre
        ).join(
            Falla, and_(
                Falla.tipo == 'nvr',
                Falla.equipo_id == Nvr.id,
                Falla.estado.in_(['abierta', 'en_proceso'])
            )
        ).filter(Nvr.activo == True).all()

        # NVRs que necesitan mantenimiento (más de 6 meses sin mantenimiento)
        fecha_limite = datetime.utcnow() - timedelta(days=180)
        nvrs_necesitan_mantenimiento = Nvr.query.filter(
            Nvr.activo == True,
            or_(
                Nvr.fecha_ultimo_mantenimiento < fecha_limite,
                Nvr.fecha_ultimo_mantenimiento.is_(None)
            )
        ).count()

        # Total de NVRs
        total_nvrs = Nvr.query.filter_by(activo=True).count()

        # Total de cámaras conectadas
        total_camaras_conectadas = db.session.query(func.count(Camara.id)).filter(
            Camara.activo == True,
            Camara.nvr_id.isnot(None)
        ).scalar()

        return jsonify({
            'total_nvrs': total_nvrs,
            'total_camaras_conectadas': total_camaras_conectadas,
            'por_estado': {estado: cantidad for estado, cantidad in por_estado},
            'por_marca': [{'marca': marca, 'cantidad': cantidad} for marca, cantidad in por_marca],
            'por_ubicacion': [{'ubicacion': ubicacion, 'cantidad': cantidad} for ubicacion, cantidad in por_ubicacion],
            'nvrs_con_fallas': len(nvrs_con_fallas),
            'nvrs_funcionando': total_nvrs - len(nvrs_con_fallas),
            'nvrs_necesitan_mantenimiento': nvrs_necesitan_mantenimiento,
            'porcentaje_funcionamiento': round(((total_nvrs - len(nvrs_con_fallas)) / total_nvrs * 100) if total_nvrs > 0 else 0, 1),
            'detalle_nvrs_con_fallas': [
                {'id': nvr_id, 'nombre': nombre} for nvr_id, nombre in nvrs_con_fallas
            ]
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500

@nvr_bp.route('/buscar-ip/<ip_address>', methods=['GET'])
@token_required
def buscar_nvr_por_ip(current_user, ip_address):
    """
    Buscar NVR por dirección IP
    """
    try:
        # Validar formato de IP
        import ipaddress
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            return jsonify({'error': 'Dirección IP inválida'}), 400

        nvr = Nvr.query.filter_by(
            ip_address=ip_address,
            activo=True
        ).first()

        if not nvr:
            return jsonify({'message': 'No se encontró NVR con esa IP'}), 404

        return jsonify({
            'id': nvr.id,
            'nombre': nvr.nombre,
            'ip_address': nvr.ip_address,
            'ubicacion': nvr.ubicacion,
            'estado': nvr.estado,
            'canales': nvr.canales,
            'fecha_instalacion': nvr.fecha_instalacion.isoformat() if nvr.fecha_instalacion else None
        })

    except Exception as e:
        return jsonify({'error': f'Error al buscar NVR: {str(e)}'}), 500