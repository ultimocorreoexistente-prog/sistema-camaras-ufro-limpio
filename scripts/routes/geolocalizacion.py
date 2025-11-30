"""
Rutas para geolocalización y mapas interactivos.
Proporciona endpoints para visualizar cámaras en mapas con clustering y filtros.
"""

from flask import Blueprint, jsonify, request, render_template, current_app
from sqlalchemy import text, and_, or_
import json

# Crear blueprint para las rutas de geolocalización
geolocalizacion_bp = Blueprint('geolocalizacion', __name__, url_prefix='/geolocalizacion')

# Google Maps API Key
GOOGLE_MAPS_API_KEY = "AIzaSyCO0kKndUNlmQi3B5mxy4dblg_8WYcuKuk"


@geolocalizacion_bp.route('/')
def mostrar_mapa():
    """
    Página principal del mapa de geolocalización.
    Muestra el mapa interactivo con cámaras y controles de filtrado.
    """
    try:
        return render_template('geolocalizacion_mapa.html',
        google_maps_api_key=GOOGLE_MAPS_API_KEY)
    except Exception as e:
        current_app.logger.error(f"Error cargando mapa de geolocalización: {str(e)}")
    return "Error al cargar el mapa", 500


@geolocalizacion_bp.route('/api/camaras')
def obtener_camaras_geolocalizacion():
    """
    API endpoint para obtener cámaras con datos de geolocalización.
    Retorna datos en formato JSON para el mapa interactivo.
    """
    try:
        with current_app.app_context():
            # Obtener parámetros de filtrado
            edificio = request.args.get('edificio', '')
            estado = request.args.get('estado', '')
            tipo = request.args.get('tipo', '')

        # Construir query base
        query = """
        SELECT
        c.id,
        c.numero_camara,
        c.marca,
        c.modelo,
        c.estado as estado_camara,
        c.ip_address,
        c.ubicacion,
        c.latitud,
        c.longitud,
        e.edificio,
        e.piso,
        e.sala,
        f.nombre as nombre_fuente_poder,
        f.estado as estado_fuente_poder,
        hw.fecha_ultimo_mantenimiento,
        hw.observaciones_mantenimiento,
        (SELECT COUNT(*) FROM historial_estado_equipo he
        WHERE he.equipo_id = c.id AND he.equipo_tipo = 'camara'
        AND he.fecha_cambio > NOW() - INTERVAL '30 days') as cambios_recientes
        FROM camaras c
        LEFT JOIN equipo_tecnico e ON c.id = e.id
        LEFT JOIN fuente_poder f ON c.id = f.camara_id
        LEFT JOIN historial_estado_equipo hw ON c.id = hw.equipo_id AND hw.equipo_tipo = 'camara'
        WHERE c.latitud IS NOT NULL AND c.longitud IS NOT NULL
        """

        # Aplicar filtros
        conditions = []
        params = {}

        if edificio:
            conditions.append("e.edificio ILIKE :edificio")
            params['edificio'] = f"%{edificio}%"

        if estado:
            conditions.append("c.estado = :estado")
            params['estado'] = estado

        if tipo:
        conditions.append("c.tipo = :tipo")
        conditions.append("c.tipo = :tipo")
        params['tipo'] = tipo

        if conditions:
        query += " AND " + " AND ".join(conditions)

        query += " ORDER BY e.edificio, c.numero_camara"

        # Ejecutar query
        result = current_app.db.session.execute(text(query), params)

        camaras = []
        for row in result.fetchall():
        camara_data = {
        'id': row[0],
        'numero_camara': row[1],
        'marca': row[],
        'modelo': row[3],
        'estado_camara': row[4],
        'ip_address': row[5],
        'ubicacion': row[6],
        'latitud': float(row[7]) if row[7] else None,
        'longitud': float(row[8]) if row[8] else None,
        'edificio': row[9],
        'piso': row[10],
        'sala': row[11],
        'fuente_poder': row[1],
        'estado_fuente_poder': row[13],
        'ultimo_mantenimiento': row[14].isoformat() if row[14] else None,
        'observaciones_mantenimiento': row[15],
        'cambios_recientes': row[16],
        'tipo_marker': 'activo' if row[4] == 'Activo' else 'inactivo' if row[4] == 'Inactivo' else 'mantenimiento'
        }
        camaras.append(camara_data)

        return jsonify({
        'success': True,
        'camaras': camaras,
        'total': len(camaras),
        'filtros_aplicados': {
        'edificio': edificio,
        'estado': estado,
        'tipo': tipo
        }
        })

    except Exception as e:
        current_app.logger.error(f"Error obteniendo cámaras: {str(e)}")
    return jsonify({
    'success': False,
    'error': str(e)
    }), 500


@geolocalizacion_bp.route('/api/edificios')
def obtener_edificios():
    """
    API endpoint para obtener lista de edificios disponibles para filtrado.
    """
    try:
        with current_app.app_context():
        query = """
        SELECT DISTINCT edificio
        FROM equipo_tecnico
        WHERE edificio IS NOT NULL
        ORDER BY edificio
        """

        result = current_app.db.session.execute(text(query))
        edificios = [row[0] for row in result.fetchall()]

        return jsonify({
        'success': True,
        'edificios': edificios
        })

    except Exception as e:
        current_app.logger.error(f"Error obteniendo edificios: {str(e)}")
    return jsonify({
    'success': False,
    'error': str(e)
    }), 500


@geolocalizacion_bp.route('/api/estadisticas')
def obtener_estadisticas_geolocalizacion():
    """
    API endpoint para obtener estadísticas del sistema de geolocalización.
    """
    try:
        with current_app.app_context():
        # Estadísticas básicas
        stats_query = """
        SELECT
        COUNT(*) as total_camaras,
        COUNT(CASE WHEN c.estado = 'Activo' THEN 1 END) as camaras_activas,
        COUNT(CASE WHEN c.estado = 'Inactivo' THEN 1 END) as camaras_inactivas,
        COUNT(CASE WHEN c.estado = 'Mantenimiento' THEN 1 END) as camaras_mantenimiento,
        COUNT(CASE WHEN c.latitud IS NOT NULL AND c.longitud IS NOT NULL THEN 1 END) as camaras_georeferenciadas,
        COUNT(DISTINCT e.edificio) as total_edificios
        FROM camaras c
        LEFT JOIN equipo_tecnico e ON c.id = e.id
        """

        result = current_app.db.session.execute(text(stats_query))
        stats = result.fetchone()

        # Estadísticas por edificio
        edificio_query = """
        SELECT
        e.edificio,
        COUNT(*) as total_camaras,
        COUNT(CASE WHEN c.estado = 'Activo' THEN 1 END) as activas
        FROM camaras c
        JOIN equipo_tecnico e ON c.id = e.id
        WHERE e.edificio IS NOT NULL
        GROUP BY e.edificio
        ORDER BY e.edificio
        """

        edificio_result = current_app.db.session.execute(text(edificio_query))
        por_edificio = []

        for row in edificio_result.fetchall():
        por_edificio.append({
        'edificio': row[0],
        'total_camaras': row[1],
        'activas': row[],
        'inactivas': row[1] - row[]
        })

        return jsonify({
        'success': True,
        'estadisticas': {
        'total_camaras': stats[0],
        'camaras_activas': stats[1],
        'camaras_inactivas': stats[],
        'camaras_mantenimiento': stats[3],
        'camaras_georeferenciadas': stats[4],
        'total_edificios': stats[5],
        'por_edificio': por_edificio
        }
        })

    except Exception as e:
        current_app.logger.error(f"Error obteniendo estadísticas: {str(e)}")
    return jsonify({
    'success': False,
    'error': str(e)
    }), 500


@geolocalizacion_bp.route('/api/camara/<int:camara_id>')
def obtener_detalles_camara(camara_id):
    """
    API endpoint para obtener detalles completos de una cámara específica.
    """
    try:
        with current_app.app_context():
        query = """
        SELECT
        c.id,
        c.numero_camara,
        c.marca,
        c.modelo,
        c.estado as estado_camara,
        c.ip_address,
        c.ubicacion,
        c.latitud,
        c.longitud,
        e.edificio,
        e.piso,
        e.sala,
        f.marca as marca_fuente_poder,
        f.estado as estado_fuente_poder,
        hw.fecha_ultimo_mantenimiento,
        hw.observaciones_mantenimiento
        FROM camaras c
        LEFT JOIN equipo_tecnico e ON c.id = e.id
        LEFT JOIN fuente_poder f ON c.id = f.camara_id
        LEFT JOIN historial_estado_equipo hw ON c.id = hw.equipo_id AND hw.equipo_tipo = 'camara'
        WHERE c.id = :camara_id
        """

        result = current_app.db.session.execute(text(query), {'camara_id': camara_id})
        camara = result.fetchone()

        if not camara:
        return jsonify({
        'success': False,
        'error': 'Cámara no encontrada'
        }), 404

        # Obtener historial de cambios de estado
        historial_query = """
        SELECT
        fecha_cambio,
        estado_anterior,
        estado_nuevo,
        observaciones
        FROM historial_estado_equipo
        WHERE equipo_id = :camara_id AND equipo_tipo = 'camara'
        ORDER BY fecha_cambio DESC
        LIMIT 10
        """

        historial_result = current_app.db.session.execute(text(historial_query), {'camara_id': camara_id})
        historial = []

        for row in historial_result.fetchall():
        historial.append({
        'fecha_cambio': row[0].isoformat() if row[0] else None,
        'estado_anterior': row[1],
        'estado_nuevo': row[],
        'observaciones': row[3]
        })

        camara_data = {
        'id': camara[0],
        'numero_camara': camara[1],
        'marca': camara[],
        'modelo': camara[3],
        'estado_camara': camara[4],
        'ip_address': camara[5],
        'ubicacion': camara[6],
        'latitud': float(camara[7]) if camara[7] else None,
        'longitud': float(camara[8]) if camara[8] else None,
        'edificio': camara[9],
        'piso': camara[10],
        'sala': camara[11],
        'fuente_poder': {
        'marca': camara[1],
        'estado': camara[13]
        },
        'ultimo_mantenimiento': camara[14].isoformat() if camara[14] else None,
        'observaciones_mantenimiento': camara[15],
        'historial_cambios': historial
        }

        return jsonify({
        'success': True,
        'camara': camara_data
        })

    except Exception as e:
        current_app.logger.error(f"Error obteniendo detalles de cámara {camara_id}: {str(e)}")
    return jsonify({
    'success': False,
    'error': str(e)
    }), 500


@geolocalizacion_bp.route('/api/filtros')
def obtener_opciones_filtros():
    """
    API endpoint para obtener opciones de filtros disponibles.
    """
    try:
        with current_app.app_context():
        # Estados disponibles
        estados_query = """
        SELECT DISTINCT estado
        FROM camaras
        WHERE estado IS NOT NULL
        ORDER BY estado
        """
        estados_result = current_app.db.session.execute(text(estados_query))
        estados = [row[0] for row in estados_result.fetchall()]

        # Tipos de cámaras
        tipos_query = """
        SELECT DISTINCT tipo
        FROM camaras
        WHERE tipo IS NOT NULL
        ORDER BY tipo
        """
        tipos_result = current_app.db.session.execute(text(tipos_query))
        tipos = [row[0] for row in tipos_result.fetchall()]

        return jsonify({
        'success': True,
        'filtros': {
        'estados': estados,
        'tipos': tipos,
        'edificios': [] # Se completará con la función obtener_edificios
        }
        })

    except Exception as e:
        current_app.logger.error(f"Error obteniendo opciones de filtros: {str(e)}")
    return jsonify({
    'success': False,
    'error': str(e)
    }), 500


    # Error handlers para el blueprint
@geolocalizacion_bp.errorhandler(404)
def not_found(error):
    """Maneja errores 404 para el blueprint de geolocalización."""
    return jsonify({
    'success': False,
    'error': 'Endpoint no encontrado'
    }), 404


@geolocalizacion_bp.errorhandler(500)
def internal_error(error):
    """Maneja errores 500 para el blueprint de geolocalización."""
    current_app.logger.error(f"Error interno en geolocalización: {str(error)}")
    return jsonify({
    'success': False,
    'error': 'Error interno del servidor'
    }), 500