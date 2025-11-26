"""
Rutas CRUD para el manejo de UPS (Uninterruptible Power Supply)
"""
from flask import request, jsonify
from sqlalchemy import or_, and_, desc, func
from datetime import datetime, timedelta
from .. import ups_bp
from models import Ups, Falla, db, Usuario
from utils.validators import validate_json, validate_required_fields, validate_pagination
from utils.decorators import token_required, require_permission

@ups_bp.route('', methods=['GET'])
@token_required
def get_ups(current_user):
    """
    Obtener lista de UPSs con filtros y paginación
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
        tipo_ups = request.args.get('tipo_ups', '')
        tipo_bateria = request.args.get('tipo_bateria', '')
        capacidad_min = request.args.get('capacidad_min', '')
        capacidad_max = request.args.get('capacidad_max', '')
        estado_carga = request.args.get('estado_carga', '')
        fecha_desde = request.args.get('fecha_desde', '')
        fecha_hasta = request.args.get('fecha_hasta', '')
        orden = request.args.get('orden', 'nombre')
        direccion = request.args.get('direccion', 'asc')

        # Query base
        query = Ups.query.filter_by(deleted=False)

        # Aplicar filtros
        if estado:
            query = query.filter(Ups.status == estado)
        if ubicacion:
            query = query.filter(Ups.ubicacion.like(f'%{ubicacion}%'))
        if search:
            query = query.filter(
                or_(
                    Ups.name.like(f'%{search}%'),
                    Ups.description.like(f'%{search}%'),
                    Ups.marca.like(f'%{search}%'),
                    Ups.modelo.like(f'%{search}%')
                )
            )
        if marca:
            query = query.filter(Ups.marca.like(f'%{marca}%'))
        if tipo_ups:
            query = query.filter(Ups.ups_type == tipo_ups)
        if tipo_bateria:
            query = query.filter(Ups.battery_type == tipo_bateria)
        if capacidad_min:
            try:
                query = query.filter(Ups.capacity_va >= int(capacidad_min))
            except ValueError:
                pass
        if capacidad_max:
            try:
                query = query.filter(Ups.capacity_va <= int(capacidad_max))
            except ValueError:
                pass
        if estado_carga:
            query = query.filter(Ups.load_status == estado_carga)
        if fecha_desde:
            try:
                fecha_desde_dt = datetime.fromisoformat(fecha_desde.replace('Z', '+00:00'))
                query = query.filter(Ups.created_at >= fecha_desde_dt)
            except ValueError:
                pass
        if fecha_hasta:
            try:
                fecha_hasta_dt = datetime.fromisoformat(fecha_hasta.replace('Z', '+00:00'))
                query = query.filter(Ups.created_at <= fecha_hasta_dt)
            except ValueError:
                pass

        # Ordenamiento
        orden_field = getattr(Ups, orden, Ups.name)
        if direccion == 'desc':
            query = query.order_by(orden_field.desc())
        else:
            query = query.order_by(orden_field.asc())

        # Paginación
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        ups_list = []
        for ups in pagination.items:
            # Obtener fallas abiertas asociadas
            fallas_abiertas = Falla.query.filter(
                Falla.tipo == 'ups',
                Falla.equipo_id == ups.id,
                Falla.estado.in_(['abierta', 'en_proceso'])
            ).count()

            ups_list.append({
                'id': ups.id,
                'nombre': ups.name,
                'descripcion': ups.description,
                'marca': ups.marca,
                'modelo': ups.modelo,
                'numero_serie': ups.serial_number,
                'ubicacion': ups.ubicacion,
                'estado': ups.status,
                'capacidad_va': ups.capacity_va,
                'capacidad_watts': ups.capacity_watts,
                'autonomia_minutos': ups.runtime_minutes,
                'tipo_ups': ups.ups_type.value if ups.ups_type else None,
                'tipo_bateria': ups.battery_type.value if ups.battery_type else None,
                'voltaje_entrada': ups.input_voltage,
                'voltaje_salida': ups.output_voltage,
                'frecuencia_entrada': ups.input_frequency,
                'frecuencia_salida': ups.output_frequency,
                'capacidad_bateria_ah': ups.battery_capacity,
                'numero_baterias': ups.battery_count,
                'edad_bateria_meses': ups.battery_age_months,
                'porcentaje_carga': ups.load_percentage,
                'estado_carga': ups.load_status.value if ups.load_status else None,
                'voltaje_bateria': ups.battery_voltage,
                'corriente_bateria': ups.battery_current,
                'temperatura_bateria': ups.battery_temperature,
                'salud_bateria_porcentaje': ups.battery_health_percentage,
                'fecha_instalacion': ups.fecha_instalacion.isoformat() if ups.fecha_instalacion else None,
                'fecha_ultimo_mantenimiento': ups.fecha_ultimo_mantenimiento.isoformat() if ups.fecha_ultimo_mantenimiento else None,
                'fecha_ultima_prueba': ups.last_battery_test.isoformat() if ups.last_battery_test else None,
                'fecha_proxima_prueba': ups.next_battery_test.isoformat() if ups.next_battery_test else None,
                'pruebas_automaticas': ups.automatic_battery_test,
                'snmp_habilitado': ups.snmp_enabled,
                'monitoreo_remoto': ups.remote_monitoring_enabled,
                'numero_salidas': ups.output_outlets,
                'salidas_gestionables': ups.managed_outlets,
                'carga_actual_watts': ups.current_load_watts,
                'carga_actual_va': ups.current_load_va,
                'factor_potencia': ups.power_factor,
                'eficiencia_porcentaje': ups.efficiency_percentage,
                'bypass_mantenimiento': ups.maintenance_bypass,
                'paquetes_bateria_externa': ups.external_battery_packs,
                'monitoreo_ambiental': ups.environmental_monitoring,
                'redundancia_configurada': ups.redundancy_configured,
                'software_apagado': ups.shutdown_software_installed,
                'tiempo_funcionamiento': ups.get_current_runtime_estimate(),
                'salud_bateria': ups.get_battery_status(),
                'salud_sistema': ups.get_system_health_score(),
                'fallas_abiertas': fallas_abiertas,
                'created_at': ups.created_at.isoformat(),
                'updated_at': ups.updated_at.isoformat() if ups.updated_at else None
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
            },
            'filters': {
                'estado': estado,
                'ubicacion': ubicacion,
                'search': search,
                'marca': marca,
                'tipo_ups': tipo_ups,
                'tipo_bateria': tipo_bateria,
                'capacidad_min': capacidad_min,
                'capacidad_max': capacidad_max,
                'estado_carga': estado_carga,
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
                'orden': orden,
                'direccion': direccion
            }
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener UPSs: {str(e)}'}), 500

@ups_bp.route('/<int:ups_id>', methods=['GET'])
@token_required
def get_ups_detail(current_user, ups_id):
    """
    Obtener detalle de un UPS específico
    """
    try:
        ups = Ups.query.get_or_404(ups_id)

        # Obtener fallas asociadas
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

        # Obtener cargas conectadas
        cargas_conectadas = []
        for carga in ups.connected_loads:
            cargas_conectadas.append({
                'id': carga.id,
                'equipo_id': carga.connected_equipment_id,
                'tipo_equipo': carga.connected_equipment_type,
                'consumo_watts': carga.watts_consumption,
                'prioridad': carga.priority_level,
                'salida_controlada': carga.controlled_outlet,
                'secuencia_apagado': carga.shutdown_sequence,
                'retardo_encendido': carga.startup_delay,
                'notas': carga.notes
            })

        # Resumen de potencia
        resumen_potencia = ups.get_power_estimate_summary()

        return jsonify({
            'id': ups.id,
            'nombre': ups.name,
            'descripcion': ups.description,
            'marca': ups.marca,
            'modelo': ups.modelo,
            'numero_serie': ups.serial_number,
            'ubicacion': ups.ubicacion,
            'estado': ups.status,
            
            # Configuración del UPS
            'tipo_ups': ups.ups_type.value if ups.ups_type else None,
            'capacidad_va': ups.capacity_va,
            'capacidad_watts': ups.capacity_watts,
            
            # Especificaciones eléctricas
            'voltaje_entrada': ups.input_voltage,
            'frecuencia_entrada': ups.input_frequency,
            'voltaje_salida': ups.output_voltage,
            'frecuencia_salida': ups.output_frequency,
            
            # Configuración de baterías
            'tipo_bateria': ups.battery_type.value if ups.battery_type else None,
            'capacidad_bateria_ah': ups.battery_capacity,
            'numero_baterias': ups.battery_count,
            'edad_bateria_meses': ups.battery_age_months,
            'autonomia_minutos': ups.runtime_minutes,
            
            # Estado actual
            'porcentaje_carga': ups.load_percentage,
            'estado_carga': ups.load_status.value if ups.load_status else None,
            'voltaje_bateria': ups.battery_voltage,
            'corriente_bateria': ups.battery_current,
            'temperatura_bateria': ups.battery_temperature,
            'salud_bateria_porcentaje': ups.battery_health_percentage,
            'salud_bateria': ups.get_battery_status(),
            
            # Pruebas de batería
            'fecha_ultima_prueba': ups.last_battery_test.isoformat() if ups.last_battery_test else None,
            'fecha_proxima_prueba': ups.next_battery_test.isoformat() if ups.next_battery_test else None,
            'pruebas_automaticas': ups.automatic_battery_test,
            'prueba_vencida': ups.is_battery_test_due(),
            
            # Conexiones
            'tipo_conexion_entrada': ups.input_connection_type,
            'tipo_conexion_salida': ups.output_connection_type,
            'numero_salidas': ups.output_outlets,
            'salidas_gestionables': ups.managed_outlets,
            
            # Comunicación y monitoreo
            'snmp_habilitado': ups.snmp_enabled,
            'comunidad_snmp': ups.snmp_community,
            'puerto_monitoreo': ups.monitoring_port,
            'monitoreo_remoto': ups.remote_monitoring_enabled,
            'comunicacion_serie': ups.serial_communication,
            'salida_reles': ups.relay_output,
            
            # Características avanzadas
            'software_apagado': ups.shutdown_software_installed,
            'bypass_mantenimiento': ups.maintenance_bypass,
            'paquetes_bateria_externa': ups.external_battery_packs,
            'monitoreo_ambiental': ups.environmental_monitoring,
            'redundancia_configurada': ups.redundancy_configured,
            
            # Métricas actuales
            'carga_actual_watts': ups.current_load_watts,
            'carga_actual_va': ups.current_load_va,
            'factor_potencia': ups.power_factor,
            'eficiencia_porcentaje': ups.efficiency_percentage,
            'generacion_calor_btu': ups.heat_output_btu,
            'estado_ventilador': ups.cooling_fan_status,
            
            # Fechas importantes
            'fecha_instalacion': ups.fecha_instalacion.isoformat() if ups.fecha_instalacion else None,
            'fecha_ultimo_mantenimiento': ups.fecha_ultimo_mantenimiento.isoformat() if ups.fecha_ultimo_mantenimiento else None,
            
            # Estimaciones y estado
            'tiempo_funcionamiento_estimado': ups.get_current_runtime_estimate(),
            'salud_sistema': ups.get_system_health_score(),
            'fecha_estimada_reemplazo_bateria': ups.get_estimated_battery_replacement_date().isoformat() if ups.get_estimated_battery_replacement_date() else None,
            
            # Datos relacionados
            'fallas_recientes': fallas_info,
            'cargas_conectadas': cargas_conectadas,
            'resumen_potencia': resumen_potencia,
            'total_fallas': len(fallas_info),
            'total_cargas_conectadas': len(cargas_conectadas),
            
            # Metadatos
            'created_at': ups.created_at.isoformat(),
            'updated_at': ups.updated_at.isoformat() if ups.updated_at else None
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

        # Validar campos requeridos
        required_fields = ['nombre']
        if not validate_required_fields(data, required_fields):
            return jsonify({'error': 'Campo requerido: nombre'}), 400

        # Validar tipos de UPS si se especifica
        if 'tipo_ups' in data:
            tipos_validos = ['online', 'line_interactive', 'offline', 'double_conversion', 'ferroresonant']
            if data['tipo_ups'] not in tipos_validos:
                return jsonify({'error': f'Tipo de UPS debe ser uno de: {tipos_validos}'}), 400

        # Validar tipos de batería si se especifica
        if 'tipo_bateria' in data:
            tipos_bateria_validos = ['lead_acid', 'lithium_ion', 'nickel_cadmium', 'vrla', 'agm', 'gel']
            if data['tipo_bateria'] not in tipos_bateria_validos:
                return jsonify({'error': f'Tipo de batería debe ser uno de: {tipos_bateria_validos}'}), 400

        # Crear UPS
        from models.enums.equipment_status import EquipmentStatus
        
        ups = Ups(
            name=data['nombre'].strip(),
            description=data.get('descripcion', '').strip(),
            marca=data.get('marca', '').strip(),
            modelo=data.get('modelo', '').strip(),
            serial_number=data.get('numero_serie', '').strip(),
            ubicacion=data.get('ubicacion', '').strip(),
            status=data.get('estado', 'activo'),
            
            # Configuración del UPS
            ups_type=data.get('tipo_ups'),
            capacity_va=data.get('capacidad_va'),
            capacity_watts=data.get('capacidad_watts'),
            
            # Especificaciones eléctricas
            input_voltage=data.get('voltaje_entrada'),
            input_frequency=data.get('frecuencia_entrada'),
            output_voltage=data.get('voltaje_salida'),
            output_frequency=data.get('frecuencia_salida'),
            
            # Configuración de baterías
            battery_type=data.get('tipo_bateria'),
            battery_capacity=data.get('capacidad_bateria_ah'),
            battery_count=data.get('numero_baterias', 1),
            battery_age_months=data.get('edad_bateria_meses'),
            runtime_minutes=data.get('autonomia_minutos'),
            
            # Estado inicial
            load_percentage=data.get('porcentaje_carga', 0.0),
            battery_voltage=data.get('voltaje_bateria'),
            battery_current=data.get('corriente_bateria'),
            battery_temperature=data.get('temperatura_bateria'),
            battery_health_percentage=data.get('salud_bateria_porcentaje', 100.0),
            
            # Configuración de pruebas
            automatic_battery_test=data.get('pruebas_automaticas', True),
            
            # Conexiones
            input_connection_type=data.get('tipo_conexion_entrada'),
            output_connection_type=data.get('tipo_conexion_salida'),
            output_outlets=data.get('numero_salidas', 0),
            managed_outlets=data.get('salidas_gestionables', 0),
            
            # Comunicación y monitoreo
            snmp_enabled=data.get('snmp_habilitado', False),
            snmp_community=data.get('comunidad_snmp'),
            monitoring_port=data.get('puerto_monitoreo'),
            remote_monitoring_enabled=data.get('monitoreo_remoto', False),
            
            # Características avanzadas
            shutdown_software_installed=data.get('software_apagado', False),
            maintenance_bypass=data.get('bypass_mantenimiento', False),
            external_battery_packs=data.get('paquetes_bateria_externa', 0),
            environmental_monitoring=data.get('monitoreo_ambiental', False),
            redundancy_configured=data.get('redundancia_configurada', False),
            serial_communication=data.get('comunicacion_serie', False),
            relay_output=data.get('salida_reles', False),
            
            # Métricas actuales
            current_load_watts=data.get('carga_actual_watts', 0.0),
            current_load_va=data.get('carga_actual_va', 0.0),
            power_factor=data.get('factor_potencia', 1.0),
            efficiency_percentage=data.get('eficiencia_porcentaje', 95.0),
            heat_output_btu=data.get('generacion_calor_btu'),
            
            # Fechas
            fecha_instalacion=datetime.fromisoformat(data['fecha_instalacion']) if data.get('fecha_instalacion') else None,
            
            # Configuración avanzada
            alarm_settings=data.get('configuracion_alarma'),
            
            # Relaciones
            ubicacion_id=data.get('ubicacion_id'),
            created_by_user_id=current_user.id,
            
            # Estado base
            activo=True,
            deleted=False
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

        # Campos que se pueden actualizar
        campos_actualizables = [
            'nombre', 'descripcion', 'marca', 'modelo', 'numero_serie', 'ubicacion', 'estado',
            'tipo_ups', 'capacidad_va', 'capacidad_watts', 'voltaje_entrada', 'voltaje_salida',
            'frecuencia_entrada', 'frecuencia_salida', 'tipo_bateria', 'capacidad_bateria_ah',
            'numero_baterias', 'edad_bateria_meses', 'autonomia_minutos', 'porcentaje_carga',
            'voltaje_bateria', 'corriente_bateria', 'temperatura_bateria', 'salud_bateria_porcentaje',
            'fecha_instalacion', 'tipo_conexion_entrada', 'tipo_conexion_salida', 'numero_salidas',
            'salidas_gestionables', 'snmp_habilitado', 'comunidad_snmp', 'puerto_monitoreo',
            'monitoreo_remoto', 'software_apagado', 'bypass_mantenimiento', 'paquetes_bateria_externa',
            'monitoreo_ambiental', 'redundancia_configurada', 'comunicacion_serie', 'salida_reles',
            'carga_actual_watts', 'carga_actual_va', 'factor_potencia', 'eficiencia_porcentaje',
            'generacion_calor_btu', 'configuracion_alarma'
        ]

        for campo in campos_actualizables:
            if campo in data and data[campo] is not None:
                if campo == 'nombre' and data[campo].strip():
                    ups.name = data[campo].strip()
                elif campo == 'descripcion' and isinstance(data[campo], str):
                    ups.description = data[campo].strip()
                elif campo == 'marca' and isinstance(data[campo], str):
                    ups.marca = data[campo].strip()
                elif campo == 'modelo' and isinstance(data[campo], str):
                    ups.modelo = data[campo].strip()
                elif campo == 'numero_serie' and isinstance(data[campo], str):
                    ups.serial_number = data[campo].strip()
                elif campo == 'ubicacion' and isinstance(data[campo], str):
                    ups.ubicacion = data[campo].strip()
                elif campo == 'fecha_instalacion' and data[campo]:
                    try:
                        ups.fecha_instalacion = datetime.fromisoformat(data[campo])
                    except ValueError:
                        pass
                else:
                    setattr(ups, campo, data[campo])

        # Actualizar estado de carga basado en porcentaje
        if 'porcentaje_carga' in data:
            ups.update_load_status()

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

        # Verificar que no tenga fallas abiertas
        fallas_abiertas = Falla.query.filter(
            Falla.tipo == 'ups',
            Falla.equipo_id == ups_id,
            Falla.estado.in_(['abierta', 'en_proceso'])
        ).count()

        if fallas_abiertas > 0:
            return jsonify({'error': 'No se puede eliminar un UPS con fallas abiertas'}), 400

        # Soft delete
        ups.deleted = True
        ups.activo = False
        ups.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({'message': 'UPS eliminado exitosamente'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al eliminar UPS: {str(e)}'}), 500

@ups_bp.route('/<int:ups_id>/test-bateria', methods=['POST'])
@token_required
def test_bateria_ups(current_user, ups_id):
    """
    Realizar prueba de batería del UPS
    """
    try:
        ups = Ups.query.get_or_404(ups_id)

        # Realizar prueba de batería
        resultado = ups.perform_battery_test()
        
        if resultado:
            return jsonify({
                'message': 'Prueba de batería iniciada exitosamente',
                'fecha_ultima_prueba': ups.last_battery_test.isoformat(),
                'fecha_proxima_prueba': ups.next_battery_test.isoformat()
            })
        else:
            return jsonify({'error': 'No se pudo iniciar la prueba de batería'}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al realizar prueba de batería: {str(e)}'}), 500

@ups_bp.route('/<int:ups_id>/cargar-conectada', methods=['POST'])
@token_required
@validate_json
@require_permission('equipos_editar')
def agregar_carga_conectada(current_user, ups_id):
    """
    Agregar una carga conectada al UPS
    """
    try:
        ups = Ups.query.get_or_404(ups_id)
        data = request.get_json()

        # Validar campos requeridos
        required_fields = ['equipment_id', 'tipo_equipo', 'consumo_watts']
        if not validate_required_fields(data, required_fields):
            return jsonify({'error': 'Campos requeridos: equipment_id, tipo_equipo, consumo_watts'}), 400

        # Crear carga conectada
        from models.ups import UPSConnectedLoad
        carga = UPSConnectedLoad(
            ups_id=ups_id,
            connected_equipment_id=data['equipment_id'],
            connected_equipment_type=data['tipo_equipo'],
            watts_consumption=data['consumo_watts'],
            priority_level=data.get('prioridad', 2),
            controlled_outlet=data.get('salida_controlada', False),
            shutdown_sequence=data.get('secuencia_apagado'),
            startup_delay=data.get('retardo_encendido', 0),
            notes=data.get('notas', '')
        )

        db.session.add(carga)
        db.session.commit()

        return jsonify({
            'message': 'Carga conectada agregada exitosamente',
            'carga_id': carga.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al agregar carga conectada: {str(e)}'}), 500

@ups_bp.route('/criticos', methods=['GET'])
@token_required
def get_ups_criticos(current_user):
    """
    Obtener UPSs en estado crítico (baterías con problemas o alta carga)
    """
    try:
        # UPSs con baterías críticas
        ups_baterias_criticas = Ups.get_critical_batteries()
        
        # UPSs con alta carga
        ups_alta_carga = Ups.get_high_load_ups()
        
        # Combinar y eliminar duplicados
        ups_criticos_ids = set()
        ups_criticos = []
        
        for ups in ups_baterias_criticas + ups_alta_carga:
            if ups.id not in ups_criticos_ids:
                ups_criticos_ids.add(ups.id)
                
                razon = []
                if ups.battery_health_percentage < 50:
                    razon.append('Batería crítica')
                if ups.load_percentage > 85:
                    razon.append('Alta carga')
                if ups.is_battery_test_due():
                    razon.append('Prueba de batería vencida')
                
                ups_criticos.append({
                    'id': ups.id,
                    'nombre': ups.name,
                    'ubicacion': ups.ubicacion,
                    'salud_bateria': ups.battery_health_percentage,
                    'porcentaje_carga': ups.load_percentage,
                    'razon': ', '.join(razon),
                    'salud_sistema': ups.get_system_health_score()
                })

        return jsonify({
            'ups_criticos': ups_criticos,
            'total': len(ups_criticos)
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener UPSs críticos: {str(e)}'}), 500

@ups_bp.route('/estadisticas', methods=['GET'])
@token_required
def get_ups_estadisticas(current_user):
    """
    Obtener estadísticas de UPSs
    """
    try:
        # Total de UPSs activos
        total_ups = Ups.query.filter_by(deleted=False).count()

        # Por estado
        por_estado = db.session.query(
            Ups.status,
            func.count(Ups.id)
        ).filter_by(deleted=False).group_by(Ups.status).all()

        # Por tipo de UPS
        por_tipo = db.session.query(
            Ups.ups_type,
            func.count(Ups.id)
        ).filter(Ups.deleted == False, Ups.ups_type.isnot(None)).group_by(Ups.ups_type).all()

        # Por tipo de batería
        por_bateria = db.session.query(
            Ups.battery_type,
            func.count(Ups.id)
        ).filter(Ups.deleted == False, Ups.battery_type.isnot(None)).group_by(Ups.battery_type).all()

        # Por marca
        por_marca = db.session.query(
            Ups.marca,
            func.count(Ups.id)
        ).filter(Ups.deleted == False, Ups.marca != '').group_by(Ups.marca).all()

        # Rangos de capacidad
        rangos_capacidad = {
            'baja (0-1000VA)': Ups.query.filter(Ups.deleted == False, Ups.capacity_va <= 1000).count(),
            'media (1001-3000VA)': Ups.query.filter(Ups.deleted == False, Ups.capacity_va > 1000, Ups.capacity_va <= 3000).count(),
            'alta (3001-10000VA)': Ups.query.filter(Ups.deleted == False, Ups.capacity_va > 3000, Ups.capacity_va <= 10000).count(),
            'muy_alta (>10000VA)': Ups.query.filter(Ups.deleted == False, Ups.capacity_va > 10000).count()
        }

        # Estado de salud de baterías
        bateria_excelente = Ups.query.filter(Ups.deleted == False, Ups.battery_health_percentage >= 90).count()
        bateria_buena = Ups.query.filter(Ups.deleted == False, Ups.battery_health_percentage >= 75, Ups.battery_health_percentage < 90).count()
        bateria_advertencia = Ups.query.filter(Ups.deleted == False, Ups.battery_health_percentage >= 50, Ups.battery_health_percentage < 75).count()
        bateria_critica = Ups.query.filter(Ups.deleted == False, Ups.battery_health_percentage < 50).count()

        return jsonify({
            'total_ups': total_ups,
            'por_estado': {estado: cantidad for estado, cantidad in por_estado},
            'por_tipo': [{'tipo': tipo.value if tipo else 'No especificado', 'cantidad': cantidad} for tipo, cantidad in por_tipo],
            'por_bateria': [{'tipo': tipo.value if tipo else 'No especificado', 'cantidad': cantidad} for tipo, cantidad in por_bateria],
            'por_marca': [{'marca': marca, 'cantidad': cantidad} for marca, cantidad in por_marca],
            'rangos_capacidad': rangos_capacidad,
            'estado_baterias': {
                'excelente': bateria_excelente,
                'buena': bateria_buena,
                'advertencia': bateria_advertencia,
                'critica': bateria_critica
            }
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500