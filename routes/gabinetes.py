"""
Rutas CRUD para el manejo de Gabinetes
"""
from flask import request, jsonify, current_app
from sqlalchemy import or_, and_, desc, func, case
from datetime import datetime, timedelta
from .. import gabinetes_bp
from models import Cabinet, Usuario, Ubicacion, db
from models.gabinete import CabinetType, CabinetMaterial, VentilationType
from utils.validators import validate_json, validate_required_fields, validate_pagination
from utils.decorators import token_required, require_permission

@gabinetes_bp.route('', methods=['GET'])
@token_required
def get_gabinetes(current_user):
    """
    Obtener lista de gabinetes con filtros y paginación
    """
    try:
        # Validar paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 0, type=int)

        if per_page > 100:
            per_page = 100

        # Parámetros de filtro
        cabinet_type = request.args.get('cabinet_type', '')
        material = request.args.get('material', '')
        status = request.args.get('status', '')
        ubicacion = request.args.get('ubicacion', '')
        search = request.args.get('search', '')
        fecha_desde = request.args.get('fecha_desde', '')
        fecha_hasta = request.args.get('fecha_hasta', '')
        orden = request.args.get('orden', 'fecha_creacion')
        direccion = request.args.get('direccion', 'desc')
        responsible_person = request.args.get('responsible_person', '')

        # Query base
        query = Cabinet.query

        # Aplicar filtros
        if cabinet_type:
            query = query.filter(Cabinet.cabinet_type == cabinet_type)
        if material:
            query = query.filter(Cabinet.material == material)
        if status:
            query = query.filter(Cabinet.status == status)
        if ubicacion:
            query = query.filter(Cabinet.ubicacion_id == ubicacion)
        if responsible_person:
            query = query.filter(Cabinet.responsible_person == responsible_person)
        if search:
            query = query.filter(
                or_(
                    Cabinet.name.like(f'%{search}%'),
                    Cabinet.description.like(f'%{search}%'),
                    Cabinet.inventory_location.like(f'%{search}%')
                )
            )
        if fecha_desde:
            try:
                fecha_desde_dt = datetime.fromisoformat(fecha_desde.replace('Z', '+00:00'))
                query = query.filter(Cabinet.fecha_creacion >= fecha_desde_dt)
            except ValueError:
                pass
        if fecha_hasta:
            try:
                fecha_hasta_dt = datetime.fromisoformat(fecha_hasta.replace('Z', '+00:00'))
                query = query.filter(Cabinet.fecha_creacion <= fecha_hasta_dt)
            except ValueError:
                pass

        # Ordenamiento
        orden_field = getattr(Cabinet, orden, Cabinet.fecha_creacion)
        if direccion == 'desc':
            query = query.order_by(orden_field.desc())
        else:
            query = query.order_by(orden_field.asc())

        # Paginación
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        gabinetes = []
        for g in pagination.items:
            gabinetes.append({
                'id': g.id,
                'name': g.name,
                'description': g.description,
                'cabinet_type': g.cabinet_type.value if g.cabinet_type else None,
                'material': g.material.value if g.material else None,
                'status': g.status.value if g.status else None,
                'ubicacion': {
                    'id': g.ubicacion.id if g.ubicacion else None,
                    'nombre': g.ubicacion.nombre if g.ubicacion else None,
                    'descripcion': g.ubicacion.descripcion if g.ubicacion else None
                } if g.ubicacion else None,
                'rack_units': g.rack_units,
                'usable_rack_units': g.usable_rack_units,
                'available_units': g.get_available_units(),
                'capacity_utilization': g.capacity_utilization,
                'max_weight_kg': g.max_weight_kg,
                'dimensions': {
                    'width_mm': g.width_mm,
                    'height_mm': g.height_mm,
                    'depth_mm': g.depth_mm
                },
                'ventilation': {
                    'type': g.ventilation_type.value if g.ventilation_type else None,
                    'cooling_fans': g.cooling_fans,
                    'airflow_cfm': g.airflow_cfm
                },
                'monitoring': {
                    'temperature_monitoring': g.temperature_monitoring,
                    'humidity_monitoring': g.humidity_monitoring,
                    'smoke_detection': g.smoke_detection,
                    'temperature_celsius': g.temperature_celsius,
                    'humidity_percentage': g.humidity_percentage
                },
                'security': {
                    'security_lock': g.security_lock,
                    'door_status': g.door_status,
                    'key_type': g.key_type,
                    'access_control': g.access_control
                },
                'equipment_summary': g.get_equipment_summary(),
                'environmental_status': g.get_environmental_status(),
                'security_status': g.get_security_status(),
                'system_health_score': g.get_system_health_score(),
                'inspection_due': g.is_inspection_due(),
                'responsible_person': {
                    'id': g.responsible_person if g.responsible_person else None,
                    'nombre': g.responsible.nombre if g.responsible else None,
                    'apellido': g.responsible.apellido if g.responsible else None
                } if g.responsible_person else None,
                'inventory_location': g.inventory_location,
                'physical_location_notes': g.physical_location_notes,
                'fecha_creacion': g.fecha_creacion.isoformat(),
                'fecha_actualizacion': g.fecha_actualizacion.isoformat() if g.fecha_actualizacion else None,
                'last_heartbeat': g.last_heartbeat.isoformat() if g.last_heartbeat else None
            })

        return jsonify({
            'gabinetes': gabinetes,
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters': {
                'cabinet_type': cabinet_type,
                'material': material,
                'status': status,
                'ubicacion': ubicacion,
                'search': search,
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
                'orden': orden,
                'direccion': direccion,
                'responsible_person': responsible_person
            }
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener gabinetes: {str(e)}'}), 500

@gabinetes_bp.route('/<int:gabinetes_id>', methods=['GET'])
@token_required
def get_gabinete(current_user, gabinetes_id):
    """
    Obtener detalle de un gabinete específico
    """
    try:
        gabinete = Cabinet.query.get_or_404(gabinetes_id)

        # Obtener equipos instalados
        installed_equipment = []
        for eq in gabinete.installed_equipment:
            installed_equipment.append({
                'id': eq.id,
                'equipment_type': eq.connected_equipment_type,
                'equipment_id': eq.connected_equipment_id,
                'start_unit': eq.start_unit,
                'end_unit': eq.get_end_unit(),
                'rack_units_used': eq.rack_units_used,
                'weight_kg': eq.weight_kg,
                'power_consumption_watts': eq.power_consumption_watts,
                'orientation': eq.orientation,
                'installation_date': eq.installation_date.isoformat() if eq.installation_date else None,
                'installation_notes': eq.installation_notes
            })

        return jsonify({
            'id': gabinete.id,
            'name': gabinete.name,
            'description': gabinete.description,
            'cabinet_type': gabinete.cabinet_type.value if gabinete.cabinet_type else None,
            'material': gabinete.material.value if gabinete.material else None,
            'status': gabinete.status.value if gabinete.status else None,
            'ubicacion': {
                'id': gabinete.ubicacion.id if gabinete.ubicacion else None,
                'nombre': gabinete.ubicacion.nombre if gabinete.ubicacion else None,
                'descripcion': gabinete.ubicacion.descripcion if gabinete.ubicacion else None,
                'edificio': gabinete.ubicacion.edificio if gabinete.ubicacion else None,
                'piso': gabinete.ubicacion.piso if gabinete.ubicacion else None,
                'area': gabinete.ubicacion.area if gabinete.ubicacion else None
            } if gabinete.ubicacion else None,
            
            # Dimensiones y capacidad
            'dimensions': {
                'width_mm': gabinete.width_mm,
                'height_mm': gabinete.height_mm,
                'depth_mm': gabinete.depth_mm,
                'rack_units': gabinete.rack_units,
                'usable_rack_units': gabinete.usable_rack_units,
                'max_weight_kg': gabinete.max_weight_kg,
                'available_units': gabinete.get_available_units()
            },
            
            # Ventilación y clima
            'ventilation': {
                'type': gabinete.ventilation_type.value if gabinete.ventilation_type else None,
                'cooling_fans': gabinete.cooling_fans,
                'airflow_cfm': gabinete.airflow_cfm
            },
            
            # Monitoreo ambiental
            'monitoring': {
                'temperature_monitoring': gabinete.temperature_monitoring,
                'humidity_monitoring': gabinete.humidity_monitoring,
                'smoke_detection': gabinete.smoke_detection,
                'temperature_celsius': gabinete.temperature_celsius,
                'humidity_percentage': gabinete.humidity_percentage,
                'temperature_alert': gabinete.get_temperature_alert_status(),
                'humidity_alert': gabinete.get_humidity_alert_status()
            },
            
            # Seguridad
            'security': {
                'security_lock': gabinete.security_lock,
                'door_status': gabinete.door_status,
                'door_opening_degrees': gabinete.door_opening_degrees,
                'key_type': gabinete.key_type,
                'door_type': gabinete.door_type,
                'lock_type': gabinete.lock_type,
                'access_control': gabinete.access_control,
                'access_log_enabled': gabinete.access_log_enabled
            },
            
            # Gestión de cables
            'cable_management': {
                'available': gabinete.cable_management,
                'ring_capacity': gabinete.cable_ring_capacity
            },
            
            # PDUs y alimentación
            'power': {
                'pdus_included': gabinete.pdus_included,
                'pdus_count': gabinete.pdus_count
            },
            
            # Sistemas de protección
            'protection': {
                'grounding_available': gabinete.grounding_available,
                'lightning_protection': gabinete.lightning_protection,
                'fire_resistant': gabinete.fire_resistant,
                'ip_rating': gabinete.ip_rating
            },
            
            # Características físicas
            'physical_features': {
                'removable_side_panels': gabinete.removable_side_panels,
                'adjustable_feet': gabinete.adjustable_feet,
                'casters_included': gabinete.casters_included,
                'leveling_feet': gabinete.leveling_feet,
                'mounting_holes': gabinete.mounting_holes
            },
            
            # Acabado
            'finish': {
                'color': gabinete.color,
                'finish_type': gabinete.finish_type
            },
            
            # Condiciones ambientales
            'environmental': {
                'conditions': gabinete.environmental_conditions,
                'seismic_rating': gabinete.seismic_rating
            },
            
            # Certificaciones
            'certifications': gabinete.certifications,
            
            # Documentación
            'documentation': {
                'manufacturer_warranty': gabinete.manufacturer_warranty,
                'installation_instructions': gabinete.installation_instructions,
                'maintenance_schedule': gabinete.maintenance_schedule
            },
            
            # Ubicación y gestión
            'location': {
                'inventory_location': gabinete.inventory_location,
                'physical_location_notes': gabinete.physical_location_notes,
                'access_schedule': gabinete.access_schedule
            },
            
            # Responsable y mantenimiento
            'responsible_person': {
                'id': gabinete.responsible_person if gabinete.responsible_person else None,
                'nombre': gabinete.responsible.nombre if gabinete.responsible else None,
                'apellido': gabinete.responsible.apellido if gabinete.responsible else None
            } if gabinete.responsible_person else None,
            
            # Inspecciones y mantenimiento
            'maintenance': {
                'last_inspection': gabinete.last_inspection.isoformat() if gabinete.last_inspection else None,
                'next_inspection': gabinete.next_inspection.isoformat() if gabinete.next_inspection else None,
                'inspection_due': gabinete.is_inspection_due(),
                'cleaning_schedule': gabinete.cleaning_schedule
            },
            
            # Métricas y estado
            'metrics': {
                'capacity_utilization': gabinete.capacity_utilization,
                'temperature_celsius': gabinete.temperature_celsius,
                'humidity_percentage': gabinete.humidity_percentage,
                'alarm_status': gabinete.alarm_status
            },
            
            # Resúmenes calculados
            'summaries': {
                'equipment': gabinete.get_equipment_summary(),
                'environmental': gabinete.get_environmental_status(),
                'security': gabinete.get_security_status(),
                'maintenance': gabinete.get_maintenance_summary()
            },
            
            'system_health_score': gabinete.get_system_health_score(),
            
            # Fechas
            'fecha_creacion': gabinete.fecha_creacion.isoformat(),
            'fecha_actualizacion': gabinete.fecha_actualizacion.isoformat() if gabinete.fecha_actualizacion else None,
            'last_heartbeat': gabinete.last_heartbeat.isoformat() if gabinete.last_heartbeat else None,
            
            # Equipos instalados
            'installed_equipment': installed_equipment
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener gabinete: {str(e)}'}), 500

@gabinetes_bp.route('', methods=['POST'])
@token_required
@require_permission('gabinetes_crear')
@validate_json
def create_gabinete(current_user):
    """
    Crear un nuevo gabinete
    """
    try:
        data = request.get_json()

        # Validar campos requeridos
        required_fields = ['name']
        if not validate_required_fields(data, required_fields):
            return jsonify({'error': 'Campos requeridos: name'}), 400

        # Validar tipos de gabinete
        if 'cabinet_type' in data and data['cabinet_type']:
            try:
                cabinet_type = CabinetType(data['cabinet_type'])
            except ValueError:
                valid_types = [t.value for t in CabinetType]
                return jsonify({'error': f'Tipo de gabinete inválido. Válidos: {valid_types}'}), 400
        else:
            cabinet_type = None

        # Validar material
        if 'material' in data and data['material']:
            try:
                material = CabinetMaterial(data['material'])
            except ValueError:
                valid_materials = [m.value for m in CabinetMaterial]
                return jsonify({'error': f'Material inválido. Válidos: {valid_materials}'}), 400
        else:
            material = None

        # Validar tipo de ventilación
        if 'ventilation_type' in data and data['ventilation_type']:
            try:
                ventilation_type = VentilationType(data['ventilation_type'])
            except ValueError:
                valid_ventilation = [v.value for v in VentilationType]
                return jsonify({'error': f'Tipo de ventilación inválido. Válidos: {valid_ventilation}'}), 400
        else:
            ventilation_type = None

        # Validar ubicación si se especifica
        ubicacion_id = data.get('ubicacion_id')
        if ubicacion_id:
            ubicacion = Ubicacion.query.filter_by(id=ubicacion_id, activo=True).first()
            if not ubicacion:
                return jsonify({'error': 'Ubicación no encontrada o inactiva'}), 400

        # Validar responsable si se especifica
        responsible_person = data.get('responsible_person')
        if responsible_person:
            usuario = Usuario.query.filter_by(id=responsible_person, activo=True).first()
            if not usuario:
                return jsonify({'error': 'Usuario responsable no encontrado'}), 400

        # Crear gabinete
        gabinete = Cabinet(
            name=data['name'].strip(),
            description=data.get('description', '').strip(),
            cabinet_type=cabinet_type,
            material=material,
            ubicacion_id=ubicacion_id,
            
            # Dimensiones
            depth_mm=data.get('depth_mm'),
            width_mm=data.get('width_mm'),
            height_mm=data.get('height_mm'),
            rack_units=data.get('rack_units'),
            usable_rack_units=data.get('usable_rack_units'),
            max_weight_kg=data.get('max_weight_kg'),
            
            # Ventilación
            ventilation_type=ventilation_type,
            cooling_fans=data.get('cooling_fans', 0),
            airflow_cfm=data.get('airflow_cfm'),
            
            # Monitoreo
            temperature_monitoring=data.get('temperature_monitoring', False),
            humidity_monitoring=data.get('humidity_monitoring', False),
            smoke_detection=data.get('smoke_detection', False),
            
            # Seguridad
            security_lock=data.get('security_lock', True),
            key_type=data.get('key_type'),
            door_type=data.get('door_type'),
            lock_type=data.get('lock_type'),
            
            # Gestión de cables
            cable_management=data.get('cable_management', False),
            cable_ring_capacity=data.get('cable_ring_capacity'),
            
            # PDUs
            pdus_included=data.get('pdus_included', False),
            pdus_count=data.get('pdus_count', 0),
            
            # Protección
            grounding_available=data.get('grounding_available', False),
            lightning_protection=data.get('lightning_protection', False),
            fire_resistant=data.get('fire_resistant', False),
            
            # Clasificación IP
            ip_rating=data.get('ip_rating'),
            
            # Características físicas
            access_control=data.get('access_control', False),
            door_opening_degrees=data.get('door_opening_degrees'),
            removable_side_panels=data.get('removable_side_panels', False),
            adjustable_feet=data.get('adjustable_feet', True),
            casters_included=data.get('casters_included', False),
            leveling_feet=data.get('leveling_feet', True),
            
            # Montaje
            mounting_holes=data.get('mounting_holes'),
            
            # Acabado
            color=data.get('color'),
            finish_type=data.get('finish_type'),
            
            # Ambiental
            environmental_conditions=data.get('environmental_conditions'),
            seismic_rating=data.get('seismic_rating'),
            
            # Certificaciones
            certifications=data.get('certifications'),
            manufacturer_warranty=data.get('manufacturer_warranty'),
            
            # Documentación
            installation_instructions=data.get('installation_instructions'),
            maintenance_schedule=data.get('maintenance_schedule'),
            
            # Ubicación
            inventory_location=data.get('inventory_location'),
            physical_location_notes=data.get('physical_location_notes'),
            access_schedule=data.get('access_schedule'),
            
            # Responsable
            responsible_person=responsible_person,
            
            # Inspecciones
            last_inspection=data.get('last_inspection'),
            next_inspection=data.get('next_inspection'),
            cleaning_schedule=data.get('cleaning_schedule'),
            
            # Métricas actuales
            capacity_utilization=data.get('capacity_utilization', 0.0),
            temperature_celsius=data.get('temperature_celsius'),
            humidity_percentage=data.get('humidity_percentage'),
            
            # Estado
            door_status=data.get('door_status', 'closed'),
            alarm_status=data.get('alarm_status'),
            access_log_enabled=data.get('access_log_enabled', False),
            
            fecha_creacion=datetime.utcnow()
        )

        db.session.add(gabinete)
        db.session.commit()

        return jsonify({
            'message': 'Gabinete creado exitosamente',
            'gabinete_id': gabinete.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear gabinete: {str(e)}'}), 500

@gabinetes_bp.route('/<int:gabinetes_id>', methods=['PUT'])
@token_required
@require_permission('gabinetes_editar')
@validate_json
def update_gabinete(current_user, gabinetes_id):
    """
    Actualizar un gabinete existente
    """
    try:
        gabinete = Cabinet.query.get_or_404(gabinetes_id)
        data = request.get_json()

        # Validar tipos de gabinete si se actualiza
        if 'cabinet_type' in data and data['cabinet_type']:
            try:
                cabinet_type = CabinetType(data['cabinet_type'])
                gabinete.cabinet_type = cabinet_type
            except ValueError:
                valid_types = [t.value for t in CabinetType]
                return jsonify({'error': f'Tipo de gabinete inválido. Válidos: {valid_types}'}), 400
        elif 'cabinet_type' in data and data['cabinet_type'] is None:
            gabinete.cabinet_type = None

        # Validar material si se actualiza
        if 'material' in data and data['material']:
            try:
                material = CabinetMaterial(data['material'])
                gabinete.material = material
            except ValueError:
                valid_materials = [m.value for m in CabinetMaterial]
                return jsonify({'error': f'Material inválido. Válidos: {valid_materials}'}), 400
        elif 'material' in data and data['material'] is None:
            gabinete.material = None

        # Validar tipo de ventilación si se actualiza
        if 'ventilation_type' in data and data['ventilation_type']:
            try:
                ventilation_type = VentilationType(data['ventilation_type'])
                gabinete.ventilation_type = ventilation_type
            except ValueError:
                valid_ventilation = [v.value for v in VentilationType]
                return jsonify({'error': f'Tipo de ventilación inválido. Válidos: {valid_ventilation}'}), 400
        elif 'ventilation_type' in data and data['ventilation_type'] is None:
            gabinete.ventilation_type = None

        # Validar ubicación si se actualiza
        if 'ubicacion_id' in data:
            ubicacion_id = data['ubicacion_id']
            if ubicacion_id:
                ubicacion = Ubicacion.query.filter_by(id=ubicacion_id, activo=True).first()
                if not ubicacion:
                    return jsonify({'error': 'Ubicación no encontrada o inactiva'}), 400
                gabinete.ubicacion_id = ubicacion_id
            else:
                gabinete.ubicacion_id = None

        # Validar responsable si se actualiza
        if 'responsible_person' in data:
            responsible_person = data['responsible_person']
            if responsible_person:
                usuario = Usuario.query.filter_by(id=responsible_person, activo=True).first()
                if not usuario:
                    return jsonify({'error': 'Usuario responsable no encontrado'}), 400
                gabinete.responsible_person = responsible_person
            else:
                gabinete.responsible_person = None

        # Actualizar campos básicos
        if 'name' in data and data['name']:
            gabinete.name = data['name'].strip()
        if 'description' in data:
            gabinete.description = data['description'].strip()

        # Actualizar dimensiones
        dimension_fields = ['depth_mm', 'width_mm', 'height_mm', 'rack_units', 'usable_rack_units', 'max_weight_kg']
        for field in dimension_fields:
            if field in data:
                setattr(gabinete, field, data[field])

        # Actualizar ventilación
        ventilation_fields = ['cooling_fans', 'airflow_cfm']
        for field in ventilation_fields:
            if field in data:
                setattr(gabinete, field, data[field])

        # Actualizar monitoreo
        monitoring_fields = ['temperature_monitoring', 'humidity_monitoring', 'smoke_detection']
        for field in monitoring_fields:
            if field in data:
                setattr(gabinete, field, data[field])

        # Actualizar métricas de monitoreo
        metric_fields = ['temperature_celsius', 'humidity_percentage']
        for field in metric_fields:
            if field in data:
                setattr(gabinete, field, data[field])

        # Actualizar seguridad
        security_fields = ['security_lock', 'key_type', 'door_type', 'lock_type', 'access_control', 'access_log_enabled', 'door_status']
        for field in security_fields:
            if field in data:
                setattr(gabinete, field, data[field])

        # Actualizar características físicas
        physical_fields = ['door_opening_degrees', 'removable_side_panels', 'adjustable_feet', 'casters_included', 'leveling_feet', 'mounting_holes']
        for field in physical_fields:
            if field in data:
                setattr(gabinete, field, data[field])

        # Actualizar acabado
        finish_fields = ['color', 'finish_type']
        for field in finish_fields:
            if field in data:
                setattr(gabinete, field, data[field])

        # Actualizar gestión de cables y protección
        cable_fields = ['cable_management', 'cable_ring_capacity', 'pdus_included', 'pdus_count', 'grounding_available', 'lightning_protection', 'fire_resistant']
        for field in cable_fields:
            if field in data:
                setattr(gabinete, field, data[field])

        # Actualizar clasificación y ambiental
        environmental_fields = ['ip_rating', 'environmental_conditions', 'seismic_rating', 'certifications', 'manufacturer_warranty']
        for field in environmental_fields:
            if field in data:
                setattr(gabinete, field, data[field])

        # Actualizar documentación
        doc_fields = ['installation_instructions', 'maintenance_schedule']
        for field in doc_fields:
            if field in data:
                setattr(gabinete, field, data[field])

        # Actualizar ubicación
        location_fields = ['inventory_location', 'physical_location_notes', 'access_schedule']
        for field in location_fields:
            if field in data:
                setattr(gabinete, field, data[field])

        # Actualizar mantenimiento
        maintenance_fields = ['last_inspection', 'next_inspection', 'cleaning_schedule', 'alarm_status']
        for field in maintenance_fields:
            if field in data:
                setattr(gabinete, field, data[field])

        # Actualizar utilización de capacidad si se proporciona
        if 'capacity_utilization' in data:
            gabinete.capacity_utilization = data['capacity_utilization']
        else:
            # Recalcular automáticamente
            gabinete.update_capacity_utilization()

        gabinete.fecha_actualizacion = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Gabinete actualizado exitosamente'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar gabinete: {str(e)}'}), 500

@gabinetes_bp.route('/<int:gabinetes_id>', methods=['DELETE'])
@token_required
@require_permission('gabinetes_eliminar')
def delete_gabinete(current_user, gabinetes_id):
    """
    Eliminar un gabinete (soft delete)
    """
    try:
        gabinete = Cabinet.query.get_or_404(gabinetes_id)

        # Verificar que no tenga equipos instalados activos
        active_equipment = [eq for eq in gabinete.installed_equipment if not eq.deleted]
        if active_equipment:
            return jsonify({'error': 'No se puede eliminar un gabinete con equipos instalados'}), 400

        gabinete.deleted = True
        gabinete.fecha_actualizacion = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Gabinete eliminado exitosamente'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al eliminar gabinete: {str(e)}'}), 500

@gabinetes_bp.route('/<int:gabinetes_id>/equipamiento', methods=['GET'])
@token_required
def get_gabinete_equipment(current_user, gabinetes_id):
    """
    Obtener equipos instalados en un gabinete específico
    """
    try:
        gabinete = Cabinet.query.get_or_404(gabinetes_id)

        equipment_list = []
        for eq in gabinete.installed_equipment:
            if not eq.deleted:
                equipment_list.append({
                    'id': eq.id,
                    'equipment_type': eq.connected_equipment_type,
                    'equipment_id': eq.connected_equipment_id,
                    'start_unit': eq.start_unit,
                    'end_unit': eq.get_end_unit(),
                    'rack_units_used': eq.rack_units_used,
                    'rack_position': eq.rack_position,
                    'orientation': eq.orientation,
                    'weight_kg': eq.weight_kg,
                    'power_consumption_watts': eq.power_consumption_watts,
                    'cable_management_used': eq.cable_management_used,
                    'ventilation_required': eq.ventilation_required,
                    'access_required': eq.access_required,
                    'maintenance_access': eq.maintenance_access,
                    'priority_level': eq.priority_level,
                    'installation_date': eq.installation_date.isoformat() if eq.installation_date else None,
                    'installation_notes': eq.installation_notes
                })

        return jsonify({
            'gabinete_id': gabinetes_id,
            'equipment': equipment_list,
            'equipment_count': len(equipment_list),
            'available_units': gabinete.get_available_units(),
            'capacity_utilization': gabinete.capacity_utilization,
            'equipment_summary': gabinete.get_equipment_summary()
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener equipamiento: {str(e)}'}), 500

@gabinetes_bp.route('/<int:gabinetes_id>/instalar-equipo', methods=['POST'])
@token_required
@require_permission('gabinetes_editar')
@validate_json
def install_equipment_in_gabinete(current_user, gabinetes_id):
    """
    Instalar un equipo en un gabinete
    """
    try:
        gabinete = Cabinet.query.get_or_404(gabinetes_id)
        data = request.get_json()

        # Validar campos requeridos
        required_fields = ['equipment_type', 'equipment_id', 'start_unit', 'rack_units_used']
        if not validate_required_fields(data, required_fields):
            return jsonify({'error': f'Campos requeridos: {", ".join(required_fields)}'}), 400

        # Buscar el equipo según su tipo
        equipment_models = {
            'camara': 'Camara',
            'nvr': 'Nvr',
            'switch': 'Switch',
            'ups': 'Ups',
            'fuente': 'Fuente'
        }

        if data['equipment_type'] not in equipment_models:
            return jsonify({'error': f'Tipo de equipo no válido. Válidos: {list(equipment_models.keys())}'}), 400

        # Obtener el modelo y buscar el equipo
        model_name = equipment_models[data['equipment_type']]
        model_class = globals()[model_name]
        equipment = model_class.query.filter_by(id=data['equipment_id'], deleted=False).first()

        if not equipment:
            return jsonify({'error': f'Equipo {data["equipment_type"]} no encontrado'}), 400

        # Verificar capacidad
        if not gabinete.can_install_equipment(data['rack_units_used']):
            return jsonify({'error': 'No hay suficiente capacidad en el gabinete'}), 400

        # Instalar el equipo
        from models.gabinete import GabineteEquipment
        installation = GabineteEquipment(
            gabinete_id=gabinetes_id,
            connected_equipment_id=data['equipment_id'],
            connected_equipment_type=data['equipment_type'],
            start_unit=data['start_unit'],
            rack_units_used=data['rack_units_used'],
            rack_position=data.get('rack_position'),
            orientation=data.get('orientation', 'front'),
            weight_kg=data.get('weight_kg'),
            power_consumption_watts=data.get('power_consumption_watts'),
            cable_management_used=data.get('cable_management_used', False),
            ventilation_required=data.get('ventilation_required', False),
            access_required=data.get('access_required', False),
            maintenance_access=data.get('maintenance_access', True),
            priority_level=data.get('priority_level', 2),
            installation_date=datetime.utcnow(),
            installation_notes=data.get('installation_notes', '')
        )

        db.session.add(installation)
        
        # Actualizar utilización de capacidad
        gabinete.update_capacity_utilization()
        
        db.session.commit()

        return jsonify({
            'message': 'Equipo instalado exitosamente',
            'installation_id': installation.id,
            'available_units': gabinete.get_available_units(),
            'capacity_utilization': gabinete.capacity_utilization
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al instalar equipo: {str(e)}'}), 500

@gabinetes_bp.route('/<int:gabinetes_id>/remover-equipo/<int:equipment_id>', methods=['DELETE'])
@token_required
@require_permission('gabinetes_editar')
def remove_equipment_from_gabinete(current_user, gabinetes_id, equipment_id):
    """
    Remover un equipo de un gabinete
    """
    try:
        gabinete = Cabinet.query.get_or_404(gabinetes_id)

        # Buscar la instalación
        from models.gabinete import GabineteEquipment
        installation = GabineteEquipment.query.filter_by(
            gabinete_id=gabinetes_id,
            id=equipment_id,
            deleted=False
        ).first()

        if not installation:
            return jsonify({'error': 'Instalación no encontrada'}), 404

        # Marcar como eliminada (soft delete)
        installation.deleted = True
        installation.fecha_actualizacion = datetime.utcnow()

        # Actualizar utilización de capacidad
        gabinete.update_capacity_utilization()

        db.session.commit()

        return jsonify({
            'message': 'Equipo removido exitosamente',
            'available_units': gabinete.get_available_units(),
            'capacity_utilization': gabinete.capacity_utilization
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al remover equipo: {str(e)}'}), 500

@gabinetes_bp.route('/estadisticas', methods=['GET'])
@token_required
def get_gabinetes_estadisticas(current_user):
    """
    Obtener estadísticas de gabinetes
    """
    try:
        # Contar por tipo
        por_tipo = db.session.query(
            Cabinet.cabinet_type,
            func.count(Cabinet.id)
        ).group_by(Cabinet.cabinet_type).all()

        # Contar por material
        por_material = db.session.query(
            Cabinet.material,
            func.count(Cabinet.id)
        ).group_by(Cabinet.material).all()

        # Contar por estado
        por_estado = db.session.query(
            Cabinet.status,
            func.count(Cabinet.id)
        ).group_by(Cabinet.status).all()

        # Utilización promedio de capacidad
        capacidad_promedio = db.session.query(
            func.avg(Cabinet.capacity_utilization)
        ).filter(Cabinet.deleted == False).scalar()

        # Gabinetes con monitoreo ambiental
        con_monitoreo = db.session.query(
            func.count(Cabinet.id)
        ).filter(
            db.or_(
                Cabinet.temperature_monitoring == True,
                Cabinet.humidity_monitoring == True,
                Cabinet.smoke_detection == True
            ),
            Cabinet.deleted == False
        ).scalar()

        # Inspecciones vencidas
        inspecciones_vencidas = 0
        for gabinete in Cabinet.query.filter_by(deleted=False).all():
            if gabinete.is_inspection_due():
                inspecciones_vencidas += 1

        # Distribución de equipos por gabinete
        equipos_por_gabinete = db.session.query(
            Cabinet.id,
            func.count(Cabinet.installed_equipment)
        ).outerjoin(
            Cabinet.installed_equipment
        ).filter(
            Cabinet.deleted == False,
            Cabinet.installed_equipment.has(deleted=False) if Cabinet.installed_equipment else True
        ).group_by(Cabinet.id).all()

        # Temperatura promedio (gabinetes con monitoreo)
        temperatura_promedio = db.session.query(
            func.avg(Cabinet.temperature_celsius)
        ).filter(
            Cabinet.temperature_monitoring == True,
            Cabinet.temperature_celsius.isnot(None),
            Cabinet.deleted == False
        ).scalar()

        # Humedad promedio (gabinetes con monitoreo)
        humedad_promedio = db.session.query(
            func.avg(Cabinet.humidity_percentage)
        ).filter(
            Cabinet.humidity_monitoring == True,
            Cabinet.humidity_percentage.isnot(None),
            Cabinet.deleted == False
        ).scalar()

        # Puntaje de salud promedio
        salud_promedio = 0
        total_gabinetes = Cabinet.query.filter_by(deleted=False).count()
        if total_gabinetes > 0:
            total_salud = sum([g.get_system_health_score() for g in Cabinet.query.filter_by(deleted=False).all()])
            salud_promedio = total_salud / total_gabinetes

        return jsonify({
            'por_tipo': {tipo.value if tipo else 'sin_tipo': cantidad for tipo, cantidad in por_tipo},
            'por_material': {material.value if material else 'sin_material': cantidad for material, cantidad in por_material},
            'por_estado': {estado.value if estado else 'sin_estado': cantidad for estado, cantidad in por_estado},
            'capacidad_promedio_utilizacion': round(capacidad_promedio, 2) if capacidad_promedio else 0,
            'gabinetes_con_monitoreo': con_monitoreo,
            'inspecciones_vencidas': inspecciones_vencidas,
            'equipos_por_gabinete_promedio': round(sum(cantidad for _, cantidad in equipos_por_gabinete) / len(equipos_por_gabinete), 2) if equipos_por_gabinete else 0,
            'temperatura_promedio': round(temperatura_promedio, 2) if temperatura_promedio else None,
            'humedad_promedio': round(humedad_promedio, 2) if humedad_promedio else None,
            'salud_promedio_sistema': round(salud_promedio, 2),
            'total_gabinetes': total_gabinetes,
            'total_equipos_instalados': sum(cantidad for _, cantidad in equipos_por_gabinete)
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500

@gabinetes_bp.route('/disponibles/<int:required_units>', methods=['GET'])
@token_required
def get_available_gabinetes(current_user, required_units):
    """
    Obtener gabinetes con capacidad disponible para instalación
    """
    try:
        # Obtener gabinetes con capacidad suficiente
        disponibles = Cabinet.get_by_capacity_requirement(required_units)

        gabinetes_disponibles = []
        for gabinete in disponibles:
            gabinetes_disponibles.append({
                'id': gabinete.id,
                'name': gabinete.name,
                'ubicacion': {
                    'id': gabinete.ubicacion.id if gabinete.ubicacion else None,
                    'nombre': gabinete.ubicacion.nombre if gabinete.ubicacion else None
                } if gabinete.ubicacion else None,
                'rack_units': gabinete.rack_units,
                'usable_rack_units': gabinete.usable_rack_units,
                'available_units': gabinete.get_available_units(),
                'max_weight_kg': gabinete.max_weight_kg,
                'capacity_utilization': gabinete.capacity_utilization,
                'system_health_score': gabinete.get_system_health_score()
            })

        return jsonify({
            'required_units': required_units,
            'available_gabinetes': gabinetes_disponibles,
            'total_available': len(gabinetes_disponibles)
        })

    except Exception as e:
        return jsonify({'error': f'Error al buscar gabinetes disponibles: {str(e)}'}), 500