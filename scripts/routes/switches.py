"""
Rutas CRUD para el manejo de Switches de red
"""
from flask import request, jsonify
from sqlalchemy import or_, and_, desc, func, case
from datetime import datetime, timedelta
from .. import switches_bp
from models import Switch, Falla, Ubicacion, Usuario, db
from utils.validators import validate_json, validate_required_fields, validate_pagination
from utils.decorators import token_required, require_permission
import ipaddress
import re


@switches_bp.route('', methods=['GET'])
@token_required
def get_switches(current_user):
    """
    Obtener lista de switches con filtros y paginación
    """
    try:
        # Validar paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        if per_page > 100:
            per_page = 100

        # Parámetros de filtro
        estado = request.args.get('estado', '')
        ubicacion_id = request.args.get('ubicacion_id', '', type=int)
        search = request.args.get('search', '')
        marca = request.args.get('marca', '')
        modelo = request.args.get('modelo', '')
        switch_type = request.args.get('switch_type', '')
        total_ports_min = request.args.get('total_ports_min', '', type=int)
        total_ports_max = request.args.get('total_ports_max', '', type=int)
        managed = request.args.get('managed', '')
        vlan_support = request.args.get('vlan_support', '')
        poe_support = request.args.get('poe_support', '')
        orden = request.args.get('orden', 'nombre')
        direccion = request.args.get('direccion', 'asc')

        # Query base
        query = Switch.query.filter_by(deleted=False)

        # Aplicar filtros
        if estado:
            query = query.filter(Switch.status == estado)
        if ubicacion_id:
            query = query.filter(Switch.ubicacion_id == ubicacion_id)
        if search:
            query = query.filter(
                or_(
                    Switch.nombre.like(f'%{search}%'),
                    Switch.descripcion.like(f'%{search}%'),
                    Switch.ip_address.like(f'%{search}%'),
                    Switch.mac_address.like(f'%{search}%'),
                    Switch.serial_number.like(f'%{search}%')
                )
            )
        if marca:
            query = query.filter(Switch.marca.like(f'%{marca}%'))
        if modelo:
            query = query.filter(Switch.modelo.like(f'%{modelo}%'))
        if switch_type:
            from models.switch import SwitchType
            query = query.filter(Switch.switch_type == SwitchType(switch_type))
        if total_ports_min:
            query = query.filter(Switch.total_ports >= total_ports_min)
        if total_ports_max:
            query = query.filter(Switch.total_ports <= total_ports_max)
        if managed:
            query = query.filter(Switch.managed == (managed.lower() == 'true'))
        if vlan_support:
            query = query.filter(Switch.vlan_support == (vlan_support.lower() == 'true'))
        if poe_support:
            query = query.filter(Switch.poe_ports > 0)

        # Ordenamiento
        if orden == 'port_utilization':
            # Ordenar por utilización de puertos
            orden_field = case(
                (Switch.total_ports > 0, 
                 (func.coalesce(func.sum(SwitchPort.utilization_percentage), 0) / Switch.total_ports) * 100),
                else_=0
            )
        else:
            orden_field = getattr(Switch, orden, Switch.nombre)

        if direccion == 'desc':
            query = query.order_by(desc(orden_field))
        else:
            query = query.order_by(orden_field.asc())

        # Paginación
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        switches = []
        for switch in pagination.items:
            # Obtener estadísticas del switch
            ports_summary = switch.get_ports_summary() if hasattr(switch, 'get_ports_summary') else {}
            vlans_summary = switch.get_vlans_summary() if hasattr(switch, 'get_vlans_summary') else {}
            
            # Verificar si el switch tiene fallas abiertas
            fallas_abiertas = Falla.query.filter(
                Falla.tipo == 'switch',
                Falla.equipo_id == switch.id,
                Falla.estado.in_(['abierta', 'en_proceso']),
                Falla.activo == True
            ).count()

            # Información de ubicación
            ubicacion_info = None
            if switch.ubicacion:
                ubicacion_info = {
                    'id': switch.ubicacion.id,
                    'nombre': switch.ubicacion.nombre,
                    'descripcion': switch.ubicacion.descripcion
                }

            switches.append({
                'id': switch.id,
                'nombre': switch.nombre,
                'descripcion': switch.descripcion,
                'ip_address': switch.ip_address,
                'mac_address': switch.mac_address,
                'serial_number': switch.serial_number,
                'marca': switch.marca,
                'modelo': switch.modelo,
                'ubicacion': ubicacion_info,
                'status': switch.status.value if switch.status else None,
                'switch_type': switch.switch_type.value if switch.switch_type else None,
                'total_ports': switch.total_ports,
                'poe_ports': switch.poe_ports,
                'max_poe_power': switch.max_poe_power,
                'port_speed': switch.port_speed,
                'fiber_ports': switch.fiber_ports,
                'stackable': switch.stackable,
                'managed': switch.managed,
                'vlan_support': switch.vlan_support,
                'qos_support': switch.qos_support,
                'poe_plus_support': switch.poe_plus_support,
                'layer_support': switch.layer_support,
                'forwarding_rate': switch.forwarding_rate,
                'switching_capacity': switch.switching_capacity,
                'redundancy_support': switch.redundancy_support,
                'stack_id': switch.stack_id,
                'stack_master': switch.stack_master,
                'monitoring_enabled': switch.monitoring_enabled,
                'alerting_enabled': switch.alerting_enabled,
                'auto_negotiation': switch.auto_negotiation,
                'storm_control': switch.storm_control,
                'spanning_tree_enabled': switch.spanning_tree_enabled,
                'installation_date': switch.installation_date.isoformat() if switch.installation_date else None,
                'last_maintenance': switch.last_maintenance.isoformat() if switch.last_maintenance else None,
                'firmware_version': switch.firmware_version,
                'health_score': switch.get_system_health_score() if hasattr(switch, 'get_system_health_score') else 100,
                'ports_summary': ports_summary,
                'vlans_summary': vlans_summary,
                'fallas_abiertas': fallas_abiertas,
                'puertos_activos': ports_summary.get('active', 0),
                'porcentaje_utilizacion': ports_summary.get('utilization_percentage', 0),
                'created_at': switch.created_at.isoformat(),
                'updated_at': switch.updated_at.isoformat() if switch.updated_at else None
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
                'ubicacion_id': ubicacion_id,
                'search': search,
                'marca': marca,
                'modelo': modelo,
                'switch_type': switch_type,
                'total_ports_min': total_ports_min,
                'total_ports_max': total_ports_max,
                'managed': managed,
                'vlan_support': vlan_support,
                'poe_support': poe_support,
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

        # Verificar que no esté eliminado
        if switch.deleted:
            return jsonify({'error': 'Switch no encontrado'}), 404

        # Obtener información de ubicación
        ubicacion_info = None
        if switch.ubicacion:
            ubicacion_info = {
                'id': switch.ubicacion.id,
                'nombre': switch.ubicacion.nombre,
                'descripcion': switch.ubicacion.descripcion,
                'direccion': getattr(switch.ubicacion, 'direccion', ''),
                'coordenadas': {
                    'lat': getattr(switch.ubicacion, 'latitud', None),
                    'lng': getattr(switch.ubicacion, 'longitud', None)
                } if hasattr(switch.ubicacion, 'latitud') and hasattr(switch.ubicacion, 'longitud') else None
            }

        # Obtener fallas relacionadas
        fallas = Falla.query.filter(
            Falla.tipo == 'switch',
            Falla.equipo_id == switch_id,
            Falla.activo == True
        ).order_by(Falla.fecha_creacion.desc()).limit(10).all()

        # Información detallada de puertos
        puertos_info = []
        if hasattr(switch, 'puertos') and switch.puertos:
            for puerto in switch.puertos:
                conectado_a = None
                if puerto.connected_equipment_id:
                    conectado_a = {
                        'id': puerto.connected_equipment_id,
                        'tipo': puerto.connected_equipment_type,
                        'nombre': f'Equipo {puerto.connected_equipment_type} #{puerto.connected_equipment_id}'
                    }

                puertos_info.append({
                    'id': puerto.id,
                    'numero': puerto.port_number,
                    'tipo': puerto.port_type.value if puerto.port_type else None,
                    'status': puerto.status.value if puerto.status else None,
                    'descripcion': puerto.description,
                    'velocidad': puerto.speed,
                    'duplex': puerto.duplex,
                    'poe_habilitado': puerto.poe_enabled,
                    'consumo_poe': puerto.poe_power_consumption,
                    'porcentaje_utilizacion': puerto.utilization_percentage,
                    'errores': puerto.error_count,
                    'ultima_actividad': puerto.last_activity.isoformat() if puerto.last_activity else None,
                    'conectado_a': conectado_a
                })

        # Información de VLANs
        vlans_info = []
        if hasattr(switch, 'vlans') and switch.vlans:
            for vlan in switch.vlans:
                vlans_info.append({
                    'id': vlan.id,
                    'vlan_id': vlan.vlan_id,
                    'nombre': vlan.vlan_name,
                    'tipo': vlan.vlan_type.value if vlan.vlan_type else None,
                    'es_nativa': vlan.is_native,
                    'es_tagged': vlan.is_tagged,
                    'descripcion': vlan.description,
                    'subred': vlan.subnet,
                    'gateway': vlan.gateway,
                    'dhcp_habilitado': vlan.dhcp_enabled,
                    'rango_dhcp': {
                        'inicio': vlan.dhcp_range_start,
                        'fin': vlan.dhcp_range_end
                    } if vlan.dhcp_range_start and vlan.dhcp_range_end else None
                })

        # Información del creador
        creado_por = None
        if switch.created_by_user:
            creado_por = {
                'id': switch.created_by_user.id,
                'nombre': switch.created_by_user.nombre,
                'apellido': switch.created_by_user.apellido,
                'email': switch.created_by_user.email
            }

        # Estadísticas y métricas
        ports_summary = switch.get_ports_summary() if hasattr(switch, 'get_ports_summary') else {}
        vlans_summary = switch.get_vlans_summary() if hasattr(switch, 'get_vlans_summary') else {}
        topology_summary = switch.get_network_topology_summary() if hasattr(switch, 'get_network_topology_summary') else {}

        # Información de fallas
        fallas_info = [{
            'id': f.id,
            'titulo': f.titulo,
            'descripcion': f.descripcion,
            'estado': f.estado,
            'prioridad': f.prioridad,
            'fecha_creacion': f.fecha_creacion.isoformat(),
            'fecha_actualizacion': f.fecha_actualizacion.isoformat() if f.fecha_actualizacion else None
        } for f in fallas]

        return jsonify({
            'id': switch.id,
            'nombre': switch.nombre,
            'descripcion': switch.descripcion,
            'ip_address': switch.ip_address,
            'mac_address': switch.mac_address,
            'serial_number': switch.serial_number,
            'marca': switch.marca,
            'modelo': switch.modelo,
            'ubicacion': ubicacion_info,
            'status': switch.status.value if switch.status else None,
            'switch_type': switch.switch_type.value if switch.switch_type else None,
            
            # Configuración de puertos
            'total_ports': switch.total_ports,
            'poe_ports': switch.poe_ports,
            'max_poe_power': switch.max_poe_power,
            'port_speed': switch.port_speed,
            'fiber_ports': switch.fiber_ports,
            'stackable': switch.stackable,
            'stacking_ports': switch.stacking_ports,
            
            # Configuración de gestión
            'management_protocols': switch.management_protocols,
            'snmp_community': switch.snmp_community,
            
            # Características avanzadas
            'managed': switch.managed,
            'vlan_support': switch.vlan_support,
            'qos_support': switch.qos_support,
            'poe_plus_support': switch.poe_plus_support,
            'layer_support': switch.layer_support,
            
            # Capacidades
            'mac_address_table_size': switch.mac_address_table_size,
            'forwarding_rate': switch.forwarding_rate,
            'switching_capacity': switch.switching_capacity,
            
            # Redundancia y stacking
            'redundancy_support': switch.redundancy_support,
            'stack_id': switch.stack_id,
            'stack_master': switch.stack_master,
            
            # Configuración y firmware
            'firmware_version': switch.firmware_version,
            'firmware_url': switch.firmware_url,
            'configuration_template': switch.configuration_template,
            'backup_configuration': switch.backup_configuration,
            
            # Monitoreo y seguridad
            'monitoring_enabled': switch.monitoring_enabled,
            'alerting_enabled': switch.alerting_enabled,
            'auto_negotiation': switch.auto_negotiation,
            'storm_control': switch.storm_control,
            'spanning_tree_enabled': switch.spanning_tree_enabled,
            
            # Fechas
            'installation_date': switch.installation_date.isoformat() if switch.installation_date else None,
            'last_maintenance': switch.last_maintenance.isoformat() if switch.last_maintenance else None,
            'created_at': switch.created_at.isoformat(),
            'updated_at': switch.updated_at.isoformat() if switch.updated_at else None,
            
            # Metadatos
            'creado_por': creado_por,
            
            # Información relacionada
            'puertos': puertos_info,
            'vlans': vlans_info,
            'fallas_recientes': fallas_info,
            'estadisticas': {
                'ports_summary': ports_summary,
                'vlans_summary': vlans_summary,
                'topology_summary': topology_summary,
                'health_score': switch.get_system_health_score() if hasattr(switch, 'get_system_health_score') else 100,
                'poe_power_usage': switch.get_poe_power_usage() if hasattr(switch, 'get_poe_power_usage') else 0,
                'poe_power_available': switch.get_poe_power_available() if hasattr(switch, 'get_poe_power_available') else 0
            },
            'resumen': {
                'total_fallas': len(fallas_info),
                'fallas_abiertas': len([f for f in fallas if f.estado in ['abierta', 'en_proceso']]),
                'puertos_activos': ports_summary.get('active', 0),
                'puertos_disponibles': ports_summary.get('total', 0) - ports_summary.get('active', 0),
                'porcentaje_utilizacion': ports_summary.get('utilization_percentage', 0),
                'vlans_configuradas': len(vlans_info)
            }
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
        required_fields = ['nombre', 'ip_address', 'total_ports']
        if not validate_required_fields(data, required_fields):
            return jsonify({'error': 'Campos requeridos: nombre, ip_address, total_ports'}), 400

        # Validar formato de IP
        try:
            ipaddress.ip_address(data['ip_address'])
        except ValueError:
            return jsonify({'error': 'Dirección IP inválida'}), 400

        # Validar formato de MAC si se proporciona
        if 'mac_address' in data and data['mac_address']:
            mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
            if not mac_pattern.match(data['mac_address']):
                return jsonify({'error': 'Formato de MAC inválido. Use XX:XX:XX:XX:XX:XX o XX-XX-XX-XX-XX-XX'}), 400

        # Verificar que no existe otro switch con la misma IP
        ip_existe = Switch.query.filter(
            Switch.ip_address == data['ip_address'],
            Switch.deleted == False
        ).first()

        if ip_existe:
            return jsonify({'error': 'Ya existe un switch con esa dirección IP'}), 400

        # Validar tipo de switch si se proporciona
        switch_type = None
        if 'switch_type' in data and data['switch_type']:
            from models.switch import SwitchType
            try:
                switch_type = SwitchType(data['switch_type'])
            except ValueError:
                return jsonify({'error': 'Tipo de switch inválido'}), 400

        # Validar que la ubicación existe si se proporciona
        ubicacion_id = None
        if 'ubicacion_id' in data and data['ubicacion_id']:
            ubicacion = Ubicacion.query.filter_by(id=data['ubicacion_id'], deleted=False).first()
            if not ubicacion:
                return jsonify({'error': 'Ubicación no encontrada'}), 400
            ubicacion_id = data['ubicacion_id']

        # Crear switch
        switch = Switch(
            nombre=data['nombre'].strip(),
            descripcion=data.get('descripcion', '').strip(),
            ip_address=data['ip_address'],
            mac_address=data.get('mac_address', '').strip(),
            serial_number=data.get('serial_number', '').strip(),
            marca=data.get('marca', '').strip(),
            modelo=data.get('modelo', '').strip(),
            ubicacion_id=ubicacion_id,
            status=data.get('status', 'activo'),
            switch_type=switch_type,
            total_ports=data['total_ports'],
            poe_ports=data.get('poe_ports', 0),
            max_poe_power=data.get('max_poe_power'),
            port_speed=data.get('port_speed'),
            fiber_ports=data.get('fiber_ports', 0),
            stackable=data.get('stackable', False),
            stacking_ports=data.get('stacking_ports', 0),
            management_protocols=data.get('management_protocols'),
            snmp_community=data.get('snmp_community'),
            vlan_support=data.get('vlan_support', True),
            qos_support=data.get('qos_support', True),
            poe_plus_support=data.get('poe_plus_support', False),
            managed=data.get('managed', True),
            layer_support=data.get('layer_support'),
            mac_address_table_size=data.get('mac_address_table_size'),
            forwarding_rate=data.get('forwarding_rate'),
            switching_capacity=data.get('switching_capacity'),
            redundancy_support=data.get('redundancy_support', False),
            stack_id=data.get('stack_id'),
            stack_master=data.get('stack_master', False),
            firmware_version=data.get('firmware_version'),
            firmware_url=data.get('firmware_url'),
            configuration_template=data.get('configuration_template'),
            backup_configuration=data.get('backup_configuration'),
            monitoring_enabled=data.get('monitoring_enabled', True),
            alerting_enabled=data.get('alerting_enabled', True),
            auto_negotiation=data.get('auto_negotiation', True),
            storm_control=data.get('storm_control', False),
            spanning_tree_enabled=data.get('spanning_tree_enabled', True),
            installation_date=datetime.fromisoformat(data['installation_date']) if data.get('installation_date') else None,
            created_by_id=current_user.id,
            deleted=False,
            created_at=datetime.utcnow()
        )

        db.session.add(switch)
        db.session.commit()

        return jsonify({
            'message': 'Switch creado exitosamente',
            'switch_id': switch.id
        }), 201

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

        # Verificar que no esté eliminado
        if switch.deleted:
            return jsonify({'error': 'Switch no encontrado'}), 404

        data = request.get_json()

        # Campos actualizables
        campos_actualizables = [
            'nombre', 'descripcion', 'ip_address', 'mac_address', 'serial_number',
            'marca', 'modelo', 'ubicacion_id', 'status', 'switch_type',
            'total_ports', 'poe_ports', 'max_poe_power', 'port_speed', 'fiber_ports',
            'stackable', 'stacking_ports', 'management_protocols', 'snmp_community',
            'vlan_support', 'qos_support', 'poe_plus_support', 'managed', 'layer_support',
            'mac_address_table_size', 'forwarding_rate', 'switching_capacity',
            'redundancy_support', 'stack_id', 'stack_master', 'firmware_version',
            'firmware_url', 'configuration_template', 'backup_configuration',
            'monitoring_enabled', 'alerting_enabled', 'auto_negotiation',
            'storm_control', 'spanning_tree_enabled', 'installation_date'
        ]

        for campo in campos_actualizables:
            if campo in data and data[campo] is not None:
                if campo == 'nombre' and data[campo].strip():
                    switch.nombre = data[campo].strip()
                elif campo == 'descripcion':
                    switch.descripcion = data[campo].strip()
                elif campo == 'ip_address':
                    # Validar formato de IP
                    try:
                        ipaddress.ip_address(data[campo])
                        # Verificar que no existe otro switch con la misma IP
                        ip_existe = Switch.query.filter(
                            Switch.ip_address == data[campo],
                            Switch.id != switch_id,
                            Switch.deleted == False
                        ).first()
                        if ip_existe:
                            return jsonify({'error': 'Ya existe otro switch con esa dirección IP'}), 400
                        switch.ip_address = data[campo]
                    except ValueError:
                        return jsonify({'error': 'Dirección IP inválida'}), 400
                elif campo == 'mac_address':
                    # Validar formato de MAC
                    if data[campo]:
                        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
                        if not mac_pattern.match(data[campo]):
                            return jsonify({'error': 'Formato de MAC inválido. Use XX:XX:XX:XX:XX:XX o XX-XX-XX-XX-XX-XX'}), 400
                    switch.mac_address = data[campo].strip() if data[campo] else ''
                elif campo == 'serial_number':
                    switch.serial_number = data[campo].strip() if data[campo] else ''
                elif campo == 'marca':
                    switch.marca = data[campo].strip() if data[campo] else ''
                elif campo == 'modelo':
                    switch.modelo = data[campo].strip() if data[campo] else ''
                elif campo == 'ubicacion_id':
                    if data[campo]:
                        # Verificar que la ubicación existe
                        ubicacion = Ubicacion.query.filter_by(id=data[campo], deleted=False).first()
                        if not ubicacion:
                            return jsonify({'error': 'Ubicación no encontrada'}), 400
                        switch.ubicacion_id = data[campo]
                    else:
                        switch.ubicacion_id = None
                elif campo == 'status':
                    from models.enums.equipment_status import EquipmentStatus
                    try:
                        switch.status = EquipmentStatus(data[campo])
                    except ValueError:
                        return jsonify({'error': 'Estado de equipo inválido'}), 400
                elif campo == 'switch_type':
                    if data[campo]:
                        from models.switch import SwitchType
                        try:
                            switch.switch_type = SwitchType(data[campo])
                        except ValueError:
                            return jsonify({'error': 'Tipo de switch inválido'}), 400
                    else:
                        switch.switch_type = None
                elif campo in ['total_ports', 'poe_ports', 'fiber_ports', 'stacking_ports']:
                    if data[campo] < 0:
                        return jsonify({'error': f'{campo} debe ser un número positivo'}), 400
                    setattr(switch, campo, data[campo])
                elif campo == 'max_poe_power':
                    if data[campo] is not None and data[campo] < 0:
                        return jsonify({'error': 'max_poe_power debe ser un número positivo'}), 400
                    switch.max_poe_power = data[campo]
                elif campo in ['vlan_support', 'qos_support', 'poe_plus_support', 'managed', 
                              'stackable', 'stack_master', 'redundancy_support', 'monitoring_enabled',
                              'alerting_enabled', 'auto_negotiation', 'storm_control', 'spanning_tree_enabled']:
                    setattr(switch, campo, data[campo])
                elif campo in ['management_protocols', 'snmp_community', 'port_speed', 'layer_support',
                              'firmware_version', 'firmware_url', 'configuration_template', 'backup_configuration']:
                    setattr(switch, campo, data[campo].strip() if data[campo] else None)
                elif campo in ['mac_address_table_size', 'forwarding_rate', 'switching_capacity']:
                    if data[campo] is not None and data[campo] < 0:
                        return jsonify({'error': f'{campo} debe ser un número positivo'}), 400
                    setattr(switch, campo, data[campo])
                elif campo == 'stack_id':
                    switch.stack_id = data[campo] if data[campo] else None
                elif campo == 'installation_date':
                    switch.installation_date = datetime.fromisoformat(data[campo]) if data[campo] else None

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

        # Verificar que no esté eliminado
        if switch.deleted:
            return jsonify({'error': 'Switch no encontrado'}), 404

        # Verificar que no tiene fallas abiertas
        fallas_abiertas = Falla.query.filter(
            Falla.tipo == 'switch',
            Falla.equipo_id == switch_id,
            Falla.estado.in_(['abierta', 'en_proceso']),
            Falla.activo == True
        ).count()

        if fallas_abiertas > 0:
            return jsonify({'error': 'No se puede eliminar un switch con fallas abiertas'}), 400

        # Soft delete
        switch.deleted = True
        switch.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Switch eliminado exitosamente'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al eliminar switch: {str(e)}'}), 500


@switches_bp.route('/<int:switch_id>/puertos', methods=['PUT'])
@token_required
@require_permission('equipos_editar')
@validate_json
def actualizar_puertos_switch(current_user, switch_id):
    """
    Actualizar estado de puertos del switch
    """
    try:
        switch = Switch.query.get_or_404(switch_id)

        # Verificar que no esté eliminado
        if switch.deleted:
            return jsonify({'error': 'Switch no encontrado'}), 404

        data = request.get_json()

        if 'puertos' not in data or not isinstance(data['puertos'], list):
            return jsonify({'error': 'Lista de puertos requerida'}), 400

        puertos_actualizados = 0
        for puerto_data in data['puertos']:
            puerto_id = puerto_data.get('id')
            if not puerto_id:
                continue

            # Buscar el puerto
            puerto = None
            if hasattr(switch, 'puertos') and switch.puertos:
                puerto = next((p for p in switch.puertos if p.id == puerto_id), None)

            if not puerto:
                return jsonify({'error': f'Puerto {puerto_id} no encontrado'}), 400

            # Actualizar campos del puerto
            if 'status' in puerto_data:
                from models.switch import PortStatus
                try:
                    puerto.status = PortStatus(puerto_data['status'])
                except ValueError:
                    return jsonify({'error': f'Estado de puerto inválido: {puerto_data["status"]}'}), 400

            if 'description' in puerto_data:
                puerto.description = puerto_data['description']

            if 'speed' in puerto_data:
                puerto.speed = puerto_data['speed']

            if 'duplex' in puerto_data:
                puerto.duplex = puerto_data['duplex']

            if 'poe_enabled' in puerto_data:
                puerto.poe_enabled = puerto_data['poe_enabled']

            if 'poe_power_consumption' in puerto_data:
                puerto.poe_power_consumption = puerto_data['poe_power_consumption']

            puerto.updated_at = datetime.utcnow()
            puertos_actualizados += 1

        db.session.commit()

        return jsonify({
            'message': f'{puertos_actualizados} puertos actualizados exitosamente',
            'puertos_actualizados': puertos_actualizados,
            'resumen': switch.get_ports_summary() if hasattr(switch, 'get_ports_summary') else {}
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar puertos: {str(e)}'}), 500


@switches_bp.route('/<int:switch_id>/vlans', methods=['POST'])
@token_required
@require_permission('equipos_editar')
@validate_json
def crear_vlan_switch(current_user, switch_id):
    """
    Crear una nueva VLAN para el switch
    """
    try:
        switch = Switch.query.get_or_404(switch_id)

        # Verificar que no esté eliminado
        if switch.deleted:
            return jsonify({'error': 'Switch no encontrado'}), 404

        data = request.get_json()

        # Validar campos requeridos
        required_fields = ['vlan_id', 'vlan_name']
        if not validate_required_fields(data, required_fields):
            return jsonify({'error': 'Campos requeridos: vlan_id, vlan_name'}), 400

        # Validar que la VLAN no existe ya
        vlan_existe = None
        if hasattr(switch, 'vlans') and switch.vlans:
            vlan_existe = next((v for v in switch.vlans if v.vlan_id == data['vlan_id']), None)

        if vlan_existe:
            return jsonify({'error': 'Ya existe una VLAN con ese ID'}), 400

        # Validar tipo de VLAN si se proporciona
        vlan_type = None
        if 'vlan_type' in data and data['vlan_type']:
            from models.switch import VLANType
            try:
                vlan_type = VLANType(data['vlan_type'])
            except ValueError:
                return jsonify({'error': 'Tipo de VLAN inválido'}), 400

        # Crear VLAN
        from models.switch import SwitchVLAN
        vlan = SwitchVLAN(
            switch_id=switch_id,
            vlan_id=data['vlan_id'],
            vlan_name=data['vlan_name'],
            vlan_type=vlan_type,
            is_native=data.get('is_native', False),
            is_tagged=data.get('is_tagged', True),
            description=data.get('description', ''),
            subnet=data.get('subnet'),
            gateway=data.get('gateway'),
            dhcp_enabled=data.get('dhcp_enabled', False),
            dhcp_range_start=data.get('dhcp_range_start'),
            dhcp_range_end=data.get('dhcp_range_end'),
            deleted=False,
            created_at=datetime.utcnow()
        )

        db.session.add(vlan)
        db.session.commit()

        return jsonify({
            'message': 'VLAN creada exitosamente',
            'vlan_id': vlan.id,
            'vlan_data': {
                'id': vlan.id,
                'vlan_id': vlan.vlan_id,
                'nombre': vlan.vlan_name,
                'tipo': vlan.vlan_type.value if vlan.vlan_type else None
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear VLAN: {str(e)}'}), 500


@switches_bp.route('/<int:switch_id>/mantenimiento', methods=['PUT'])
@token_required
@require_permission('equipos_editar')
def actualizar_mantenimiento_switch(current_user, switch_id):
    """
    Actualizar fecha de último mantenimiento
    """
    try:
        switch = Switch.query.get_or_404(switch_id)

        # Verificar que no esté eliminado
        if switch.deleted:
            return jsonify({'error': 'Switch no encontrado'}), 404

        switch.last_maintenance = datetime.utcnow()
        switch.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Fecha de mantenimiento actualizada',
            'last_maintenance': switch.last_maintenance.isoformat()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar mantenimiento: {str(e)}'}), 500


@switches_bp.route('/estadisticas', methods=['GET'])
@token_required
def get_switches_estadisticas(current_user):
    """
    Obtener estadísticas generales de switches
    """
    try:
        # Total por estado
        por_estado = db.session.query(
            Switch.status,
            func.count(Switch.id)
        ).filter_by(deleted=False).group_by(Switch.status).all()

        # Total por tipo
        por_tipo = db.session.query(
            Switch.switch_type,
            func.count(Switch.id)
        ).filter_by(deleted=False).group_by(Switch.switch_type).all()

        # Total por marca
        por_marca = db.session.query(
            Switch.marca,
            func.count(Switch.id)
        ).filter(
            Switch.deleted == False,
            Switch.marca.isnot(None),
            Switch.marca != ''
        ).group_by(Switch.marca).all()

        # Total por ubicación
        por_ubicacion = db.session.query(
            Ubicacion.nombre,
            func.count(Switch.id)
        ).join(
            Switch, Switch.ubicacion_id == Ubicacion.id
        ).filter(
            Switch.deleted == False,
            Ubicacion.deleted == False
        ).group_by(Ubicacion.id, Ubicacion.nombre).all()

        # Switches con fallas abiertas
        switches_con_fallas = db.session.query(
            Switch.id,
            Switch.nombre
        ).join(
            Falla, and_(
                Falla.tipo == 'switch',
                Falla.equipo_id == Switch.id,
                Falla.estado.in_(['abierta', 'en_proceso']),
                Falla.activo == True
            )
        ).filter(Switch.deleted == False).distinct().all()

        # Switches que necesitan mantenimiento (más de 6 meses sin mantenimiento)
        fecha_limite = datetime.utcnow() - timedelta(days=180)
        switches_necesitan_mantenimiento = Switch.query.filter(
            Switch.deleted == False,
            or_(
                Switch.last_maintenance < fecha_limite,
                Switch.last_maintenance.is_(None)
            )
        ).count()

        # Total de switches
        total_switches = Switch.query.filter_by(deleted=False).count()

        # Distribución por número de puertos
        por_puertos = db.session.query(
            Switch.total_ports,
            func.count(Switch.id)
        ).filter_by(deleted=False).group_by(Switch.total_ports).all()

        # Estadísticas de puertos
        total_puertos = db.session.query(func.sum(Switch.total_ports)).filter(
            Switch.deleted == False
        ).scalar() or 0

        total_poe_ports = db.session.query(func.sum(Switch.poe_ports)).filter(
            Switch.deleted == False
        ).scalar() or 0

        # Switches gestionables vs no gestionables
        gestionables = Switch.query.filter_by(deleted=False, managed=True).count()
        no_gestionables = Switch.query.filter_by(deleted=False, managed=False).count()

        # Switches con soporte VLAN
        con_vlan = Switch.query.filter_by(deleted=False, vlan_support=True).count()

        return jsonify({
            'total_switches': total_switches,
            'total_puertos': total_puertos,
            'total_poe_ports': total_poe_ports,
            'por_estado': {str(estado.value): cantidad for estado, cantidad in por_estado} if por_estado else {},
            'por_tipo': {str(tipo.value) if tipo else 'None': cantidad for tipo, cantidad in por_tipo} if por_tipo else {},
            'por_marca': [{'marca': marca, 'cantidad': cantidad} for marca, cantidad in por_marca] if por_marca else [],
            'por_ubicacion': [{'ubicacion': ubicacion, 'cantidad': cantidad} for ubicacion, cantidad in por_ubicacion] if por_ubicacion else [],
            'por_puertos': [{'puertos': puertos, 'cantidad': cantidad} for puertos, cantidad in por_puertos] if por_puertos else [],
            'switches_con_fallas': len(switches_con_fallas),
            'switches_funcionando': total_switches - len(switches_con_fallas),
            'switches_necesitan_mantenimiento': switches_necesitan_mantenimiento,
            'switches_gestionables': gestionables,
            'switches_no_gestionables': no_gestionables,
            'switches_con_vlan': con_vlan,
            'porcentaje_funcionamiento': round(((total_switches - len(switches_con_fallas)) / total_switches * 100) if total_switches > 0 else 0, 1),
            'detalle_switches_con_fallas': [
                {'id': switch_id, 'nombre': nombre} for switch_id, nombre in switches_con_fallas
            ] if switches_con_fallas else []
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
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            return jsonify({'error': 'Dirección IP inválida'}), 400

        switch = Switch.query.filter_by(
            ip_address=ip_address,
            deleted=False
        ).first()

        if not switch:
            return jsonify({'message': 'No se encontró switch con esa IP'}), 404

        # Información de ubicación
        ubicacion_info = None
        if switch.ubicacion:
            ubicacion_info = {
                'id': switch.ubicacion.id,
                'nombre': switch.ubicacion.nombre
            }

        return jsonify({
            'id': switch.id,
            'nombre': switch.nombre,
            'ip_address': switch.ip_address,
            'ubicacion': ubicacion_info,
            'status': switch.status.value if switch.status else None,
            'switch_type': switch.switch_type.value if switch.switch_type else None,
            'total_ports': switch.total_ports,
            'managed': switch.managed,
            'installation_date': switch.installation_date.isoformat() if switch.installation_date else None
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
            Switch.deleted == False
        ).first()

        if not switch:
            return jsonify({'message': 'No se encontró switch con esa MAC'}), 404

        # Información de ubicación
        ubicacion_info = None
        if switch.ubicacion:
            ubicacion_info = {
                'id': switch.ubicacion.id,
                'nombre': switch.ubicacion.nombre
            }

        return jsonify({
            'id': switch.id,
            'nombre': switch.nombre,
            'mac_address': switch.mac_address,
            'ip_address': switch.ip_address,
            'ubicacion': ubicacion_info,
            'status': switch.status.value if switch.status else None,
            'switch_type': switch.switch_type.value if switch.switch_type else None,
            'serial_number': switch.serial_number,
            'marca': switch.marca,
            'modelo': switch.modelo
        })

    except Exception as e:
        return jsonify({'error': f'Error al buscar switch por MAC: {str(e)}'}), 500