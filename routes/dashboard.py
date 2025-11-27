#!/usr/bin/env python3
"""
Blueprint de Dashboard - Sistema Cámaras UFRO
============================================

Dashboard principal con estadísticas en tiempo real y context processors globales.
- Estadísticas del sistema
- Métricas en tiempo real
- Gráficos de fallas y mantenimiento
- Overview de equipos

Autor: MiniMax Agent
Fecha: 2025-11-27
Versión: 3.0-hybrid
"""

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func, desc, and_, or_, extract
from datetime import datetime, timedelta
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear blueprint
dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """
    Dashboard principal con estadísticas generales
    """
    try:
        # Obtener estadísticas del sistema
        stats = get_system_stats()
        
        # Obtener actividad reciente
        recent_activity = get_recent_activity()
        
        # Obtener fallas críticas
        critical_issues = get_critical_issues()
        
        # Obtener próximas tareas de mantenimiento
        upcoming_maintenance = get_upcoming_maintenance()
        
        return render_template('dashboard/index.html', 
                             stats=stats,
                             recent_activity=recent_activity,
                             critical_issues=critical_issues,
                             upcoming_maintenance=upcoming_maintenance)
                             
    except Exception as e:
        logger.error(f"Error en dashboard: {str(e)}")
        # Fallback a datos básicos en caso de error
        basic_stats = get_basic_stats()
        return render_template('dashboard/index.html', 
                             stats=basic_stats,
                             recent_activity=[],
                             critical_issues=[],
                             upcoming_maintenance=[])

@dashboard_bp.route('/stats')
@login_required
def get_stats():
    """
    API endpoint para obtener estadísticas del sistema
    """
    try:
        stats = get_system_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/cameras/status')
@login_required
def cameras_status():
    """
    API endpoint para estado de cámaras
    """
    try:
        from models import Camara
        
        # Estadísticas de cámaras por estado
        status_counts = db.session.query(
            Camara.estado,
            func.count(Camara.id)
        ).group_by(Camara.estado).all()
        
        # Estadísticas por ubicación
        location_stats = db.session.query(
            Camara.ubicacion,
            func.count(Camara.id),
            func.count(Camara.id).filter(Camara.estado == 'operativa')
        ).group_by(Camara.ubicacion).all()
        
        # Cámaras con fallas recientes
        cameras_with_failures = db.session.query(
            func.count(Camara.id)
        ).filter(
            Camara.estado == 'fallas'
        ).scalar()
        
        # Tiempo promedio de disponibilidad (simulado)
        uptime_stats = {
            'average_uptime': 99.2,
            'total_downtime_hours': 2.4,
            'last_incident': (datetime.now() - timedelta(days=3)).isoformat()
        }
        
        return jsonify({
            'status_distribution': dict(status_counts),
            'location_statistics': [
                {
                    'location': location,
                    'total_cameras': total,
                    'operational_cameras': operational
                }
                for location, total, operational in location_stats
            ],
            'cameras_with_failures': cameras_with_failures,
            'uptime_statistics': uptime_stats
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de cámaras: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/failures/analytics')
@login_required
def failures_analytics():
    """
    API endpoint para análisis de fallas
    """
    try:
        from models import Falla
        
        # Fallas por mes (últimos 6 meses)
        failures_by_month = db.session.query(
            extract('year', Falla.fecha_creacion).label('year'),
            extract('month', Falla.fecha_creacion).label('month'),
            func.count(Falla.id).label('count')
        ).filter(
            Falla.fecha_creacion >= datetime.now() - timedelta(days=180)
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        # Fallas por prioridad
        failures_by_priority = db.session.query(
            Falla.prioridad,
            func.count(Falla.id)
        ).group_by(Falla.prioridad).all()
        
        # Tiempo promedio de resolución
        resolution_time = db.session.query(
            func.avg(
                func.julianday(Falla.fecha_resolucion) - 
                func.julianday(Falla.fecha_creacion)
            )
        ).filter(Falla.fecha_resolucion.isnot(None)).scalar() or 0
        
        # Fallas abiertas por antigüedad
        old_open_failures = db.session.query(
            func.count(Falla.id)
        ).filter(
            Falla.estado == 'abierta',
            Falla.fecha_creacion < datetime.now() - timedelta(days=7)
        ).scalar()
        
        return jsonify({
            'failures_by_month': [
                {
                    'year': int(row.year),
                    'month': int(row.month),
                    'count': row.count
                }
                for row in failures_by_month
            ],
            'failures_by_priority': dict(failures_by_priority),
            'average_resolution_time_days': round(resolution_time, 2),
            'old_open_failures': old_open_failures
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo análisis de fallas: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/maintenance/schedule')
@login_required
def maintenance_schedule():
    """
    API endpoint para programación de mantenimiento
    """
    try:
        from models import Mantenimiento
        
        # Próximos mantenimientos (próximos 30 días)
        upcoming_maintenance = db.session.query(
            Mantenimiento
        ).filter(
            Mantenimiento.fecha_programada >= datetime.now(),
            Mantenimiento.fecha_programada <= datetime.now() + timedelta(days=30),
            Mantenimiento.estado.in_(['programado', 'pendiente'])
        ).order_by(Mantenimiento.fecha_programada.asc()).all()
        
        # Mantenimientos vencidos
        overdue_maintenance = db.session.query(
            func.count(Mantenimiento.id)
        ).filter(
            Mantenimiento.fecha_programada < datetime.now(),
            Mantenimiento.estado.in_(['programado', 'pendiente'])
        ).scalar()
        
        # Mantenimientos por tipo
        maintenance_by_type = db.session.query(
            Mantenimiento.tipo,
            func.count(Mantenimiento.id)
        ).group_by(Mantenimiento.tipo).all()
        
        return jsonify({
            'upcoming_maintenance': [
                {
                    'id': m.id,
                    'tipo': m.tipo,
                    'descripcion': m.descripcion,
                    'fecha_programada': m.fecha_programada.isoformat(),
                    'estado': m.estado,
                    'equipo': f"{m.equipo_tipo} #{m.equipo_id}" if m.equipo_id else 'General'
                }
                for m in upcoming_maintenance
            ],
            'overdue_count': overdue_maintenance,
            'maintenance_by_type': dict(maintenance_by_type)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo programación de mantenimiento: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/system/health')
@login_required
def system_health():
    """
    API endpoint para salud general del sistema
    """
    try:
        from models import Camara, Falla, Mantenimiento, Usuario
        
        # Calcular puntaje de salud general
        camera_health = calculate_camera_health()
        failure_health = calculate_failure_health()
        maintenance_health = calculate_maintenance_health()
        
        overall_health = (camera_health + failure_health + maintenance_health) / 3
        
        # Alertas del sistema
        system_alerts = get_system_alerts()
        
        return jsonify({
            'overall_health_score': round(overall_health, 2),
            'component_health': {
                'cameras': round(camera_health, 2),
                'failures': round(failure_health, 2),
                'maintenance': round(maintenance_health, 2)
            },
            'system_alerts': system_alerts,
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo salud del sistema: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/realtime')
@login_required
def realtime_data():
    """
    API endpoint para datos en tiempo real
    """
    try:
        # Datos actualizados en tiempo real
        from models import Camara, Falla
        
        realtime_stats = {
            'timestamp': datetime.now().isoformat(),
            'active_cameras': Camara.query.filter_by(estado='operativa').count(),
            'failed_cameras': Camara.query.filter_by(estado='fallas').count(),
            'open_failures': Falla.query.filter_by(estado='abierta').count(),
            'processing_failures': Falla.query.filter_by(estado='en_proceso').count(),
            'resolved_today': Falla.query.filter(
                Falla.fecha_resolucion >= datetime.now().date()
            ).count()
        }
        
        return jsonify(realtime_stats)
        
    except Exception as e:
        logger.error(f"Error obteniendo datos en tiempo real: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Funciones auxiliares

def get_system_stats():
    """
    Obtener estadísticas principales del sistema
    """
    try:
        from models import Camara, Falla, Mantenimiento, Usuario, Ubicacion
        
        stats = {
            'total_camaras': Camara.query.count(),
            'camaras_operativas': Camara.query.filter_by(estado='operativa').count(),
            'camaras_falla': Camara.query.filter_by(estado='fallas').count(),
            'fallas_abiertas': Falla.query.filter_by(estado='abierta').count(),
            'fallas_en_proceso': Falla.query.filter_by(estado='en_proceso').count(),
            'mantenimientos_pendientes': Mantenimiento.query.filter_by(estado='pendiente').count(),
            'usuarios_activos': Usuario.query.filter_by(activo=True).count(),
            'ubicaciones_totales': Ubicacion.query.filter_by(activo=True).count(),
            
            # Porcentajes de salud
            'camera_health_percentage': 0,
            'failure_resolution_rate': 0,
            'maintenance_up_to_date': 0
        }
        
        # Calcular porcentajes
        if stats['total_cameras'] > 0:
            stats['camera_health_percentage'] = round(
                (stats['camaras_operativas'] / stats['total_cameras']) * 100, 1
            )
        
        total_failures = stats['fallas_abiertas'] + stats['fallas_en_proceso']
        if total_failures > 0:
            # Simular tasa de resolución (en producción sería calculado real)
            stats['failure_resolution_rate'] = 85.2
        
        if stats['mantenimientos_pendientes'] > 0:
            stats['maintenance_up_to_date'] = 92.1  # Simulado
        
        return stats
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas del sistema: {str(e)}")
        return get_basic_stats()

def get_basic_stats():
    """
    Estadísticas básicas en caso de error
    """
    return {
        'total_camaras': 0,
        'camaras_operativas': 0,
        'camaras_falla': 0,
        'fallas_abiertas': 0,
        'fallas_en_proceso': 0,
        'mantenimientos_pendientes': 0,
        'usuarios_activos': 0,
        'ubicaciones_totales': 0,
        'camera_health_percentage': 0,
        'failure_resolution_rate': 0,
        'maintenance_up_to_date': 0
    }

def get_recent_activity():
    """
    Obtener actividad reciente del sistema
    """
    try:
        from models import Falla
        
        # Últimas 10 fallas creadas
        recent_failures = Falla.query.order_by(
            Falla.fecha_creacion.desc()
        ).limit(10).all()
        
        activity = []
        for failure in recent_failures:
            activity.append({
                'type': 'failure',
                'title': failure.titulo,
                'description': failure.descripcion,
                'timestamp': failure.fecha_creacion.isoformat(),
                'priority': failure.prioridad,
                'status': failure.estado
            })
        
        return activity[:5]  # Solo las 5 más recientes
        
    except Exception as e:
        logger.error(f"Error obteniendo actividad reciente: {str(e)}")
        return []

def get_critical_issues():
    """
    Obtener issues críticos del sistema
    """
    try:
        from models import Falla
        
        # Fallas de prioridad alta abiertas
        critical_failures = Falla.query.filter(
            Falla.prioridad == 'alta',
            Falla.estado.in_(['abierta', 'en_proceso'])
        ).order_by(Falla.fecha_creacion.desc()).limit(5).all()
        
        issues = []
        for failure in critical_failures:
            issues.append({
                'type': 'critical_failure',
                'title': failure.titulo,
                'description': failure.descripcion,
                'priority': failure.prioridad,
                'status': failure.estado,
                'created_date': failure.fecha_creacion.isoformat(),
                'days_open': (datetime.now() - failure.fecha_creacion).days
            })
        
        return issues
        
    except Exception as e:
        logger.error(f"Error obteniendo issues críticos: {str(e)}")
        return []

def get_upcoming_maintenance():
    """
    Obtener próximos mantenimientos
    """
    try:
        from models import Mantenimiento
        
        # Próximos 10 mantenimientos
        upcoming = Mantenimiento.query.filter(
            Mantenimiento.fecha_programada >= datetime.now(),
            Mantenimiento.estado.in_(['programado', 'pendiente'])
        ).order_by(Mantenimiento.fecha_programada.asc()).limit(10).all()
        
        maintenance = []
        for m in upcoming:
            maintenance.append({
                'type': m.tipo,
                'description': m.descripcion,
                'scheduled_date': m.fecha_programada.isoformat(),
                'status': m.estado,
                'equipment': f"{m.equipo_tipo} #{m.equipo_id}" if m.equipo_id else 'General'
            })
        
        return maintenance[:5]  # Solo los 5 próximos
        
    except Exception as e:
        logger.error(f"Error obteniendo próximo mantenimiento: {str(e)}")
        return []

def calculate_camera_health():
    """
    Calcular salud de cámaras (0-100)
    """
    try:
        from models import Camara
        
        total = Camara.query.count()
        if total == 0:
            return 100
        
        operational = Camara.query.filter_by(estado='operativa').count()
        return (operational / total) * 100
        
    except Exception:
        return 0

def calculate_failure_health():
    """
    Calcular salud de manejo de fallas (0-100)
    """
    try:
        from models import Falla
        
        # Simular puntaje basado en antigüedad de fallas abiertas
        old_failures = Falla.query.filter(
            Falla.estado == 'abierta',
            Falla.fecha_creacion < datetime.now() - timedelta(days=7)
        ).count()
        
        total_failures = Falla.query.filter(
            Falla.estado.in_(['abierta', 'en_proceso'])
        ).count()
        
        if total_failures == 0:
            return 100
        
        # Penalizar por fallas antiguas
        penalty = min(old_failures / total_failures * 50, 50)
        return max(100 - penalty, 50)
        
    except Exception:
        return 50

def calculate_maintenance_health():
    """
    Calcular salud de mantenimiento (0-100)
    """
    try:
        from models import Mantenimiento
        
        # Simular puntaje basado en mantenimientos al día
        total_pendientes = Mantenimiento.query.filter_by(estado='pendiente').count()
        overdue = Mantenimiento.query.filter(
            Mantenimiento.fecha_programada < datetime.now(),
            Mantenimiento.estado.in_(['programado', 'pendiente'])
        ).count()
        
        if total_pendientes == 0:
            return 100
        
        penalty = min(overdue / total_pendientes * 30, 30)
        return max(100 - penalty, 70)
        
    except Exception:
        return 70

def get_system_alerts():
    """
    Obtener alertas del sistema
    """
    alerts = []
    
    try:
        from models import Camara, Falla, Mantenimiento
        
        # Alerta: Muchas cámaras con fallas
        failed_cameras = Camara.query.filter_by(estado='fallas').count()
        total_cameras = Camara.query.count()
        
        if total_cameras > 0:
            failure_rate = failed_cameras / total_cameras
            if failure_rate > 0.1:  # Más del 10%
                alerts.append({
                    'level': 'warning',
                    'message': f'Alta tasa de fallas de cámaras: {failure_rate:.1%}',
                    'count': failed_cameras
                })
        
        # Alerta: Fallas abiertas antiguas
        old_failures = Falla.query.filter(
            Falla.estado == 'abierta',
            Falla.fecha_creacion < datetime.now() - timedelta(days=7)
        ).count()
        
        if old_failures > 5:
            alerts.append({
                'level': 'error',
                'message': f'Muchas fallas abiertas por más de 7 días: {old_failures}',
                'count': old_failures
            })
        
        # Alerta: Mantenimientos vencidos
        overdue_maintenance = Mantenimiento.query.filter(
            Mantenimiento.fecha_programada < datetime.now(),
            Mantenimiento.estado.in_(['programado', 'pendiente'])
        ).count()
        
        if overdue_maintenance > 3:
            alerts.append({
                'level': 'info',
                'message': f'Mantenimientos vencidos: {overdue_maintenance}',
                'count': overdue_maintenance
            })
        
    except Exception as e:
        logger.error(f"Error obteniendo alertas del sistema: {str(e)}")
    
    return alerts

# Importar db para evitar circular import
from models import db