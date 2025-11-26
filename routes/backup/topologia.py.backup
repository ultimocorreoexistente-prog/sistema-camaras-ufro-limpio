# -*- coding: utf-8 -*-
"""
Módulo de Rutas para Topología de Red
=====================================

Este módulo contiene todas las rutas relacionadas con la visualización
y gestión de la topología de infraestructura de red.

Características principales:
- Diagramas Mermaid dinámicos
- Filtros por ubicación y tipo de equipo
- Visualización jerárquica de la red
- API endpoints para datos en tiempo real

Autor: Sistema de Gestión de Cámaras UFRO
Fecha: 05-11-04
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from sqlalchemy import or_, func, text
from datetime import datetime
import json
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Crear blueprint para topología
topologia_bp = Blueprint('topologia', __name__, url_prefix='/topologia')

# ========== DECORADOR DE CONTROL DE ROLES PARA TOPOLOGÍA ==========
def role_required(*roles):
    """
    Decorador para controlar acceso por roles en topología.
    Roles disponibles: SUPERADMIN, ADMIN, SUPERVISOR, TECNICO, VISUALIZADOR
    """
def decorator(f):
    @wraps(f)
        def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Necesitas iniciar sesión', 'warning')
            return redirect(url_for('login'))

        user_role = current_user.rol.upper()
        allowed_roles = [role.upper() for role in roles]

        # SUPERADMIN siempre tiene acceso completo
        if user_role == 'SUPERADMIN' or user_role in allowed_roles:
            return f(*args, **kwargs)

        flash('No tienes permisos para acceder a esta sección', 'danger')
        return redirect(url_for('dashboard'))
    return decorated_function

        # ========== RUTA PRINCIPAL DE TOPOLOGÍA ==========
        @topologia_bp.route('/', methods=['GET'])
        @login_required
        @role_required('SUPERADMIN', 'ADMIN', 'SUPERVISOR', 'VISUALIZADOR')
@role_required('SUPERADMIN', 'ADMIN', 'SUPERVISOR', 'VISUALIZADOR')
def index():
    """
    Ruta principal de topología de red.
    Muestra vista completa con filtros y diagramas Mermaid dinámicos.
    """
    try:
        # Importar modelos dinámicamente para evitar errores
        from models import (
        db, Ubicacion, Camara, Switch, Puerto_Switch,
        UPS, NVR_DVR, Fuente_Poder, Gabinete
        )

        # Obtener parámetros de filtrado
        campus_filtro = request.args.get('campus', '')
        edificio_filtro = request.args.get('edificio', '')
        tipo_equipo_filtro = request.args.get('tipo_equipo', '')
        estado_filtro = request.args.get('estado', '')

        # Construir query base con filtros
        query_ubicaciones = Ubicacion.query

        if campus_filtro:
        query_ubicaciones = query_ubicaciones.filter(Ubicacion.campus == campus_filtro)

        if edificio_filtro:
        query_ubicaciones = query_ubicaciones.filter(Ubicacion.edificio == edificio_filtro)

        ubicaciones = query_ubicaciones.all()

        # Obtener listas para filtros
        campus_list = [u.campus for u in Ubicacion.query.group_by(Ubicacion.campus).all()]
        edificios_list = [u.edificio for u in Ubicacion.query.group_by(Ubicacion.edificio).all()]
        tipos_equipo = ['Camara', 'Switch', 'NVR_DVR', 'UPS', 'Fuente_Poder']
        estados_equipo = ['Activo', 'Inactivo', 'Mantenimiento', 'Falla']

        # Generar datos de topología con filtros aplicados
        topology_data = generar_topologia_dinamica(
        ubicaciones,
        campus_filtro,
        tipo_equipo_filtro,
        estado_filtro
        )

        # Generar diagrama Mermaid
        mermaid_diagram = generar_diagrama_mermaid(topology_data)

        return render_template('topologia_red.html',
        topology_data=json.dumps(topology_data),
        mermaid_diagram=mermaid_diagram,
        campus_list=campus_list,
        edificios_list=edificios_list,
        tipos_equipo=tipos_equipo,
        estados_equipo=estados_equipo,
        filtros_activos={
        'campus': campus_filtro,
        'edificio': edificio_filtro,
        'tipo_equipo': tipo_equipo_filtro,
        'estado': estado_filtro
        })

    except Exception as e:
        logger.error(f"Error cargando topología: {str(e)}")
    flash(f'Error cargando topología: {str(e)}', 'danger')
    return redirect(url_for('dashboard'))

    # ========== TOPOLOGÍA POR CAMPUS ==========
@topologia_bp.route('/campus/<campus>', methods=['GET'])
@login_required
@role_required('SUPERADMIN', 'ADMIN', 'SUPERVISOR', 'VISUALIZADOR')
def topologia_por_campus(campus):
    """
    Vista de topología filtrada por campus específico.
    """
    try:
        # Filtrar ubicaciones por campus
        ubicaciones = Ubicacion.query.filter_by(campus=campus).all()

        if not ubicaciones:
        flash(f'No se encontraron ubicaciones en el campus: {campus}', 'warning')
        return redirect(url_for('topologia.index'))

        # Generar topología para el campus
        topology_data = generar_topologia_dinamica(ubicaciones, campus_filtro=campus)
        mermaid_diagram = generar_diagrama_mermaid(topology_data)

        # Obtener estadísticas del campus
        stats_campus = obtener_estadisticas_campus(ubicaciones)

        return render_template('topologia_campus.html',
        campus=campus,
        topology_data=json.dumps(topology_data),
        mermaid_diagram=mermaid_diagram,
        estadisticas=stats_campus)

    except Exception as e:
        logger.error(f"Error cargando topología del campus {campus}: {str(e)}")
    flash(f'Error cargando topología del campus: {str(e)}', 'danger')
    return redirect(urlify('topologia.index'))

    # ========== TOPOLOGÍA POR TIPO DE EQUIPO ==========
@topologia_bp.route('/equipo/<tipo_equipo>', methods=['GET'])
@login_required
@role_required('SUPERADMIN', 'ADMIN', 'SUPERVISOR', 'VISUALIZADOR')
def topologia_por_equipo(tipo_equipo):
    """
    Vista de topología filtrada por tipo de equipo específico.
    """
    try:
        tipos_validos = ['camara', 'switch', 'nvr_dvr', 'ups', 'fuente_poder', 'gabinete']

        if tipo_equipo.lower() not in tipos_validos:
        flash(f'Tipo de equipo no válido: {tipo_equipo}', 'warning')
        return redirect(url_for('topologia.index'))

        # Obtener ubicaciones con equipos del tipo especificado
        ubicaciones = obtener_ubicaciones_por_tipo_equipo(tipo_equipo.lower())

        topology_data = generar_topologia_dinamica(
        ubicaciones,
        tipo_equipo_filtro=tipo_equipo.lower()
        )
        mermaid_diagram = generar_diagrama_mermaid(topology_data)

        return render_template('topologia_equipo.html',
        tipo_equipo=tipo_equipo,
        topology_data=json.dumps(topology_data),
        mermaid_diagram=mermaid_diagram)

    except Exception as e:
        logger.error(f"Error cargando topología de {tipo_equipo}: {str(e)}")
    flash(f'Error cargando topología de equipo: {str(e)}', 'danger')
    return redirect(url_for('topologia.index'))

    # ========== API ENDPOINTS ==========

@topologia_bp.route('/api/datos', methods=['GET'])
@login_required
@role_required('SUPERADMIN', 'ADMIN', 'SUPERVISOR', 'VISUALIZADOR')
def api_datos_topologia():
    """
    API endpoint para obtener datos de topología en formato JSON.
    """
    try:
        # Parámetros de filtrado
        campus = request.args.get('campus', '')
        tipo_equipo = request.args.get('tipo_equipo', '')
        estado = request.args.get('estado', '')

        # Construir query
        query_ubicaciones = Ubicacion.query

        if campus:
        query_ubicaciones = query_ubicaciones.filter(Ubicacion.campus == campus)

        ubicaciones = query_ubicaciones.all()

        # Generar datos
        topology_data = generar_topologia_dinamica(
        ubicaciones,
        campus_filtro=campus,
        tipo_equipo_filtro=tipo_equipo,
        estado_filtro=estado
        )

        return jsonify({
        'success': True,
        'data': topology_data,
        'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error en API de topología: {str(e)}")
    return jsonify({
    'success': False,
    'error': str(e),
    'timestamp': datetime.now().isoformat()
    }), 500

@topologia_bp.route('/api/mermaid', methods=['GET'])
@login_required
@role_required('SUPERADMIN', 'ADMIN', 'SUPERVISOR', 'VISUALIZADOR')
def api_diagrama_mermaid():
    """
    API endpoint para generar diagramas Mermaid dinámicos.
    """
    try:
        # Parámetros
        campus = request.args.get('campus', '')
        tipo_equipo = request.args.get('tipo_equipo', '')
        vista = request.args.get('vista', 'completa') # completa, resumida, detalles

        # Obtener datos
        query_ubicaciones = Ubicacion.query
        if campus:
        query_ubicaciones = query_ubicaciones.filter(Ubicacion.campus == campus)

        ubicaciones = query_ubicaciones.all()

        # Generar topología y diagrama
        topology_data = generar_topologia_dinamica(
        ubicaciones,
        campus_filtro=campus,
        tipo_equipo_filtro=tipo_equipo
        )

        mermaid_diagram = generar_diagrama_mermaid(topology_data, vista=vista)

        return jsonify({
        'success': True,
        'mermaid': mermaid_diagram,
        'metadata': {
        'total_nodos': len(topology_data['nodes']),
        'total_conexiones': len(topology_data['edges']),
        'filtros_aplicados': {
        'campus': campus,
        'tipo_equipo': tipo_equipo,
        'vista': vista
        }
        },
        'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error generando diagrama Mermaid: {str(e)}")
    return jsonify({
    'success': False,
    'error': str(e)
    }), 500

@topologia_bp.route('/api/estadisticas', methods=['GET'])
@login_required
@role_required('SUPERADMIN', 'ADMIN', 'SUPERVISOR', 'VISUALIZADOR')
def api_estadisticas_topologia():
    """
    API endpoint para obtener estadísticas de la topología.
    """
    try:
        from models import Camara, Switch, NVR_DVR, UPS, Gabinete, Fuente_Poder

        # Estadísticas generales
        stats = {
        'equipos': {
        'camaras': {
        'total': Camara.query.count(),
        'activas': Camara.query.filter_by(estado='Activo').count(),
        'inactivas': Camara.query.filter_by(estado='Inactivo').count(),
        'mantenimiento': Camara.query.filter_by(estado='Mantenimiento').count()
        },
        'switches': {
        'total': Switch.query.count(),
        'activos': Switch.query.filter_by(estado='Activo').count(),
        'puertos_totales': Switch.query.with_entities(func.sum(Switch.puertos_totales)).scalar() or 0,
        'puertos_usados': Switch.query.with_entities(func.sum(Switch.puertos_usados)).scalar() or 0
        },
        'nvr_dvr': {
        'total': NVR_DVR.query.count(),
        'activos': NVR_DVR.query.filter_by(estado='Activo').count(),
        'canales_totales': NVR_DVR.query.with_entities(func.sum(NVR_DVR.canales_totales)).scalar() or 0,
        'canales_usados': NVR_DVR.query.with_entities(func.sum(NVR_DVR.canales_usados)).scalar() or 0
        },
        'ups': {
        'total': UPS.query.count(),
        'activos': UPS.query.filter_by(estado='Activo').count()
        },
        'gabinetes': {
        'total': Gabinete.query.count(),
        'con_equipos': len([g for g in Gabinete.query.all() if g.switches])
        }
        },
        'ubicaciones': {
        'total_campus': len([u.campus for u in Ubicacion.query.group_by(Ubicacion.campus).all()]),
        'total_edificios': len([u.edificio for u in Ubicacion.query.group_by(Ubicacion.edificio).all()]),
        'total_ubicaciones': Ubicacion.query.count()
        }
        }

        # Estadísticas por campus
        stats['por_campus'] = obtener_estadisticas_por_campus()

        return jsonify({
        'success': True,
        'estadisticas': stats,
        'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
    return jsonify({
    'success': False,
    'error': str(e)
    }), 500

    # ========== FUNCIONES AUXILIARES ==========

def generar_topologia_dinamica(ubicaciones, campus_filtro='', tipo_equipo_filtro='', estado_filtro=''):
    """
    Genera estructura de datos de topología dinámica basada en filtros.

    Args:
    ubicaciones: Lista de ubicaciones a procesar
    campus_filtro: Filtro por campus
    tipo_equipo_filtro: Filtro por tipo de equipo
    estado_filtro: Filtro por estado

    Returns:
    dict: Estructura con nodos y conexiones de la topología
    """
    try:
        from models import (
        Camara, Switch, Puerto_Switch, NVR_DVR,
        UPS, Fuente_Poder, Gabinete
        )

        topology_data = {
        'nodes': [],
        'edges': []
        }

        node_id = 1

        for ubicacion in ubicaciones:
        # Agregar nodo de ubicación
        ubicacion_node = {
        'id': f'ubicacion_{ubicacion.id}',
        'label': f'{ubicacion.campus}\\n{ubicacion.edificio}',
        'type': 'ubicacion',
        'campus': ubicacion.campus,
        'edificio': ubicacion.edificio,
        'piso': ubicacion.piso or 'N/A',
        'x': ubicacion.latitud,
        'y': ubicacion.longitud
        }
        topology_data['nodes'].append(ubicacion_node)

        # Procesar cámaras
        if not tipo_equipo_filtro or tipo_equipo_filtro == 'camara':
        camaras = Camara.query.filter_by(ubicacion_id=ubicacion.id)
        if estado_filtro:
        camaras = camaras.filter_by(estado=estado_filtro)

        for camara in camaras.all():
        camara_node = {
        'id': f'camara_{camara.id}',
        'label': f'{camara.codigo}\\n{camara.nombre or ""}',
        'type': 'camara',
        'ip': camara.ip or 'N/A',
        'estado': camara.estado,
        'ubicacion_id': ubicacion.id
        }
        topology_data['nodes'].append(camara_node)

        # Conexión: Cámara → Ubicación
        topology_data['edges'].append({
        'from': f'camara_{camara.id}',
        'to': f'ubicacion_{ubicacion.id}',
        'label': 'Instalada en'
        })

        # Procesar switches
        if not tipo_equipo_filtro or tipo_equipo_filtro == 'switch':
        switches = Switch.query.join(Gabinete).filter(Gabinete.ubicacion_id == ubicacion.id)

        for switch in switches.all():
        switch_node = {
        'id': f'switch_{switch.id}',
        'label': f'{switch.codigo}\\n{switch.modelo or ""}',
        'type': 'switch',
        'ip': switch.ip or 'N/A',
        'puertos': f'{switch.puertos_usados}/{switch.puertos_totales}',
        'estado': switch.estado
        }
        topology_data['nodes'].append(switch_node)

        # Conexión: Switch → Ubicación
        topology_data['edges'].append({
        'from': f'switch_{switch.id}',
        'to': f'ubicacion_{ubicacion.id}',
        'label': 'Instalado en'
        })

        # Agregar puertos como nodos intermedios
        for puerto in switch.puertos:
        puerto_node = {
        'id': f'puerto_{puerto.id}',
        'label': f'P{puerto.numero_puerto}',
        'type': 'puerto',
        'estado': puerto.estado
        }
        topology_data['nodes'].append(puerto_node)

        topology_data['edges'].append({
        'from': f'puerto_{puerto.id}',
        'to': f'switch_{switch.id}',
        'label': ''
        })

        # Procesar NVR/DVR
        if not tipo_equipo_filtro or tipo_equipo_filtro == 'nvr_dvr':
        nvr_dvrs = NVR_DVR.query.filter_by(ubicacion_id=ubicacion.id)
        if estado_filtro:
        nvr_dvrs = nvr_dvrs.filter_by(estado=estado_filtro)

        for nvr in nvr_dvrs.all():
        nvr_node = {
        'id': f'nvr_{nvr.id}',
        'label': f'{nvr.codigo}\\n{nvr.tipo}',
        'type': 'nvr',
        'ip': nvr.ip or 'N/A',
        'canales': f'{nvr.canales_usados}/{nvr.canales_totales}',
        'estado': nvr.estado
        }
        topology_data['nodes'].append(nvr_node)

        topology_data['edges'].append({
        'from': f'nvr_{nvr.id}',
        'to': f'ubicacion_{ubicacion.id}',
        'label': 'Ubicado en'
        })

        # Procesar UPS
        if not tipo_equipo_filtro or tipo_equipo_filtro == 'ups':
        ups_list = UPS.query.filter_by(ubicacion_id=ubicacion.id)
        if estado_filtro:
        ups_list = ups_list.filter_by(estado=estado_filtro)

        for ups in ups_list.all():
        ups_node = {
        'id': f'ups_{ups.id}',
        'label': f'{ups.codigo}\\n{ups.marca or ""}',
        'type': 'ups',
        'capacidad': f'{ups.capacidad_watts}W' if ups.capacidad_watts else 'N/A',
        'estado': ups.estado
        }
        topology_data['nodes'].append(ups_node)

        topology_data['edges'].append({
        'from': f'ups_{ups.id}',
        'to': f'ubicacion_{ubicacion.id}',
        'label': 'Instalado en'
        })

        return topology_data

    except Exception as e:
        logger.error(f"Error generando topología dinámica: {str(e)}")
    return {'nodes': [], 'edges': []}

def generar_diagrama_mermaid(topology_data, vista='completa'):
    """
    Genera un diagrama Mermaid a partir de los datos de topología.

    Args:
    topology_data: Datos de la topología
    vista: Tipo de vista ('completa', 'resumida', 'detalles')

    Returns:
    str: Código Mermaid para el diagrama
    """
    try:
        mermaid_code = ["graph TD"]

        # Colores por tipo de nodo
        colores = {
        'ubicacion': 'fill:#e1f5fe,stroke:#077bd,stroke-width:3px',
        'camara': 'fill:#e8f5e8,stroke:#e7d3,stroke-width:px',
        'switch': 'fill:#fff3e0,stroke:#f57c00,stroke-width:px',
        'nvr': 'fill:#f3e5f5,stroke:#7b1fa,stroke-width:px',
        'ups': 'fill:#fce4ec,stroke:#c185b,stroke-width:px',
        'puerto': 'fill:#f1f8e9,stroke:#558bf,stroke-width:1px'
        }

        if vista == 'resumida':
        # Vista resumida: solo ubicaciones y tipos de equipos
        for node in topology_data['nodes']:
        if node['type'] == 'ubicacion':
        style = colores['ubicacion']
        mermaid_code.append(f" {node['id']}[\"{node['label']}\"]:::ubicacion")
    elif node['type'] in ['camara', 'switch', 'nvr', 'ups']:
        style = colores[node['type']]
    # Agrupar por tipo para vista resumida
    tipo_count = sum(1 for n in topology_data['nodes']
    if n['type'] == node['type'] and
    n.get('ubicacion_id') == node.get('ubicacion_id'))
    label = f"{node['type'].upper()}\\n({tipo_count} equipos)"
    mermaid_code.append(f" {node['id']}[\"{label}\"]:::{node['type']}")

    else: # vista completa
        # Vista completa: todos los nodos
    for node in topology_data['nodes']:
    style = colores.get(node['type'], 'fill:#f5f5f5,stroke:#444,stroke-width:1px')
    mermaid_code.append(f" {node['id']}[\"{node['label']}\"]:::{node['type']}")

    # Aplicar estilos
    for tipo, color in colores.items():
    mermaid_code.append(f" classDef {tipo} {color}")

    # Agregar conexiones
    for edge in topology_data['edges']:
        if edge['label']:
        mermaid_code.append(f" {edge['from']} -->|{edge['label']}| {edge['to']}")
    else:
        mermaid_code.append(f" {edge['from']} --> {edge['to']}")

    return '\\n'.join(mermaid_code)

    except Exception as e:
        logger.error(f"Error generando diagrama Mermaid: {str(e)}")
    return "graph TD\\n A[Error generando diagrama]"

def obtener_ubicaciones_por_tipo_equipo(tipo_equipo):
    """
    Obtiene ubicaciones que contienen equipos del tipo especificado.
    """
    try:
        from models import Camara, Switch, NVR_DVR, UPS, Gabinete

        ubicaciones_ids = set()

        if tipo_equipo == 'camara':
        ubicaciones_ids.update([camara.ubicacion_id for camara in Camara.query.all()])
    elif tipo_equipo == 'switch':
        ubicaciones_ids.update([switch.gabinete.ubicacion_id for switch in Switch.query.join(Gabinete).all()])
    elif tipo_equipo == 'nvr_dvr':
        ubicaciones_ids.update([nvr.ubicacion_id for nvr in NVR_DVR.query.all()])
    elif tipo_equipo == 'ups':
        ubicaciones_ids.update([ups.ubicacion_id for ups in UPS.query.all()])

    return Ubicacion.query.filter(Ubicacion.id.in_(ubicaciones_ids)).all()

    except Exception as e:
        logger.error(f"Error obteniendo ubicaciones por tipo: {str(e)}")
    return []

def obtener_estadisticas_campus(ubicaciones):
    """
    Obtiene estadísticas detalladas para un campus específico.
    """
    try:
        from models import Camara, Switch, NVR_DVR, UPS

        stats = {
        'total_ubicaciones': len(ubicaciones),
        'total_camaras': 0,
        'total_switches': 0,
        'total_nvr': 0,
        'total_ups': 0,
        'equipos_activos': 0,
        'equipos_inactivos': 0
        }

        ubicaciones_ids = [u.id for u in ubicaciones]

        # Contar cámaras
        camaras = Camara.query.filter(Camara.ubicacion_id.in_(ubicaciones_ids)).all()
        stats['total_camaras'] = len(camaras)
        stats['equipos_activos'] += len([c for c in camaras if c.estado == 'Activo'])
        stats['equipos_inactivos'] += len([c for c in camaras if c.estado = 'Activo'])

        # Contar switches
        from models import Gabinete
        gabinetes_campus = Gabinete.query.filter(Gabinete.ubicacion_id.in_(ubicaciones_ids)).all()
        gabinetes_ids = [g.id for g in gabinetes_campus]
        switches = Switch.query.filter(Switch.gabinete_id.in_(gabinetes_ids)).all()
        stats['total_switches'] = len(switches)
        stats['equipos_activos'] += len([s for s in switches if s.estado == 'Activo'])
        stats['equipos_inactivos'] += len([s for s in switches if s.estado = 'Activo'])

        # Contar NVR/DVR
        nvrs = NVR_DVR.query.filter(NVR_DVR.ubicacion_id.in_(ubicaciones_ids)).all()
        stats['total_nvr'] = len(nvrs)
        stats['equipos_activos'] += len([n for n in nvrs if n.estado == 'Activo'])
        stats['equipos_inactivos'] += len([n for n in nvrs if n.estado = 'Activo'])

        # Contar UPS
        ups_list = UPS.query.filter(UPS.ubicacion_id.in_(ubicaciones_ids)).all()
        stats['total_ups'] = len(ups_list)
        stats['equipos_activos'] += len([u for u in ups_list if u.estado == 'Activo'])
        stats['equipos_inactivos'] += len([u for u in ups_list if u.estado = 'Activo'])

        return stats

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas del campus: {str(e)}")
    return {}

def obtener_estadisticas_por_campus():
    """
    Obtiene estadísticas detalladas para todos los campus.
    """
    try:
        from models import Camara, Switch, NVR_DVR, UPS, Gabinete

        campus_stats = []

        # Obtener todos los campus únicos
        campus_list = [u.campus for u in Ubicacion.query.group_by(Ubicacion.campus).all()]

        for campus in campus_list:
        ubicaciones = Ubicacion.query.filter_by(campus=campus).all()
        ubicaciones_ids = [u.id for u in ubicaciones]

        # Contar equipos por campus
        camaras = Camara.query.filter(Camara.ubicacion_id.in_(ubicaciones_ids)).all()
        switches = Switch.query.join(Gabinete).filter(
        Gabinete.ubicacion_id.in_(ubicaciones_ids)
        ).all()
        nvrs = NVR_DVR.query.filter(NVR_DVR.ubicacion_id.in_(ubicaciones_ids)).all()
        ups_list = UPS.query.filter(UPS.ubicacion_id.in_(ubicaciones_ids)).all()

        campus_data = {
        'campus': campus,
        'ubicaciones': len(ubicaciones),
        'camaras': len(camaras),
        'camaras_activas': len([c for c in camaras if c.estado == 'Activo']),
        'switches': len(switches),
        'switches_activos': len([s for s in switches if s.estado == 'Activo']),
        'nvr_dvr': len(nvrs),
        'nvr_activos': len([n for n in nvrs if n.estado == 'Activo']),
        'ups': len(ups_list),
        'ups_activos': len([u for u in ups_list if u.estado == 'Activo'])
        }

        campus_stats.append(campus_data)

        return campus_stats

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas por campus: {str(e)}")
    return []

    # ========== EXPORTAR BLUEPRINT ==========
def init_topologia_routes(app):
    """
    Función para registrar el blueprint en la aplicación Flask.
    """
    app.register_blueprint(topologia_bp)
    logger.info("Rutas de topología registradas exitosamente")