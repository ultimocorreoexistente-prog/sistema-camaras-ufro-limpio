"""
Blueprint del Dashboard principal para Sistema de Cámaras UFRO
Dashboard con estadísticas y resumen general del sistema
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import logging

dashboard_bp = Blueprint('dashboard_bp', __name__)
logger = logging.getLogger(__name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard principal con estadísticas globales"""
    try:
        # Importar modelos
        from models import Usuario, Camara, Falla, Mantenimiento, Ubicacion
        from models import EstadoEquipoEnum, EstadoFallaEnum
        
        # Obtener estadísticas generales
        stats = {
            'total_usuarios': Usuario.query.count() if Usuario.query.first() else 0,
            'total_camaras': Camara.query.count() if Camara.query.first() else 0,
            'camaras_activas': Camara.query.filter_by(estado=EstadoEquipoEnum.ACTIVO.value).count() if Camara.query.first() else 0,
            'total_fallas': Falla.query.count() if Falla.query.first() else 0,
            'fallas_abiertas': Falla.query.filter_by(estado=EstadoFallaEnum.ABIERTA.value).count() if Falla.query.first() else 0,
            'fallas_en_proceso': Falla.query.filter_by(estado=EstadoFallaEnum.EN_PROCESO.value).count() if Falla.query.first() else 0,
            'total_mantenimientos': Mantenimiento.query.count() if Mantenimiento.query.first() else 0,
            'total_ubicaciones': Ubicacion.query.count() if Ubicacion.query.first() else 0
        }
        
        # Calcular porcentajes y métricas adicionales
        if stats['total_camaras'] > 0:
            stats['porcentaje_camaras_activas'] = round((stats['camaras_activas'] / stats['total_camaras']) * 100, 1)
        else:
            stats['porcentaje_camaras_activas'] = 0
            
        if stats['total_fallas'] > 0:
            stats['porcentaje_fallas_abiertas'] = round((stats['fallas_abiertas'] / stats['total_fallas']) * 100, 1)
        else:
            stats['porcentaje_fallas_abiertas'] = 0
        
        # Obtener fallas recientes (últimas 5)
        fallas_recientes = []
        try:
            from models import Falla
            fallas_recientes = Falla.query.order_by(Falla.fecha_creacion.desc()).limit(5).all()
        except:
            pass
        
        # Obtener mantenimientos próximos (próximos 5)
        mantenimientos_proximos = []
        try:
            from models import Mantenimiento
            hoy = datetime.now()
            proxima_semana = hoy + timedelta(days=7)
            mantenimientos_proximos = Mantenimiento.query.filter(
                Mantenimiento.fecha_programada >= hoy,
                Mantenimiento.fecha_programada <= proxima_semana,
                Mantenimiento.estado != 'completado'
            ).order_by(Mantenimiento.fecha_programada.asc()).limit(5).all()
        except:
            pass
        
        # Obtener cámaras críticas (con fallas abiertas)
        camaras_criticas = []
        try:
            from models import Camara, Falla
            camaras_criticas = Camara.query.join(Falla, Falla.equipo_id == Camara.id).filter(
                Falla.tipo == 'camara',
                Falla.estado.in_([EstadoFallaEnum.ABIERTA.value, EstadoFallaEnum.EN_PROCESO.value])
            ).distinct().limit(5).all()
        except:
            pass
        
        # Calcular health score general
        health_score = calcular_health_score(stats)
        
        return render_template('dashboard.html', 
                             stats=stats,
                             fallas_recientes=fallas_recientes,
                             mantenimientos_proximos=mantenimientos_proximos,
                             camaras_criticas=camaras_criticas,
                             health_score=health_score,
                             user=current_user,
                             titulo="Dashboard - Sistema Cámaras UFRO v3.0-Hybrid")
                             
    except Exception as e:
        logger.error(f"Error cargando dashboard: {e}")
        flash('Error cargando estadísticas del dashboard', 'danger')
        return render_template('dashboard.html', 
                             stats={},
                             fallas_recientes=[],
                             mantenimientos_proximos=[],
                             camaras_criticas=[],
                             health_score=0,
                             user=current_user,
                             titulo="Dashboard - Sistema Cámaras UFRO")

@dashboard_bp.route('/stats')
@login_required
def dashboard_stats():
    """API para estadísticas del dashboard en formato JSON"""
    try:
        # Importar modelos
        from models import Usuario, Camara, Falla, Mantenimiento, Ubicacion
        from models import EstadoEquipoEnum, EstadoFallaEnum
        
        # Estadísticas generales
        stats = {
            'timestamp': datetime.utcnow().isoformat(),
            'general': {
                'total_usuarios': Usuario.query.count() if Usuario.query.first() else 0,
                'total_camaras': Camara.query.count() if Camara.query.first() else 0,
                'camaras_activas': Camara.query.filter_by(estado=EstadoEquipoEnum.ACTIVO.value).count() if Camara.query.first() else 0,
                'total_fallas': Falla.query.count() if Falla.query.first() else 0,
                'fallas_abiertas': Falla.query.filter_by(estado=EstadoFallaEnum.ABIERTA.value).count() if Falla.query.first() else 0,
                'total_mantenimientos': Mantenimiento.query.count() if Mantenimiento.query.first() else 0,
                'total_ubicaciones': Ubicacion.query.count() if Ubicacion.query.first() else 0
            }
        }
        
        # Calcular porcentajes
        if stats['general']['total_camaras'] > 0:
            stats['general']['porcentaje_camaras_activas'] = round(
                (stats['general']['camaras_activas'] / stats['general']['total_camaras']) * 100, 1
            )
        else:
            stats['general']['porcentaje_camaras_activas'] = 0
            
        if stats['general']['total_fallas'] > 0:
            stats['general']['porcentaje_fallas_abiertas'] = round(
                (stats['general']['fallas_abiertas'] / stats['general']['total_fallas']) * 100, 1
            )
        else:
            stats['general']['porcentaje_fallas_abiertas'] = 0
        
        # Health score
        stats['health_score'] = calcular_health_score(stats['general'])
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error obteniendo stats: {e}")
        return jsonify({'error': 'Error obteniendo estadísticas'}), 500

@dashboard_bp.route('/alerts')
@login_required
def get_alerts():
    """Obtener alertas críticas del sistema"""
    try:
        from models import Camara, Falla, Mantenimiento
        from models import EstadoEquipoEnum, EstadoFallaEnum
        
        alertas = []
        
        # Cámaras en estado crítico
        try:
            camaras_criticas = Camara.query.filter(
                Camara.estado.in_([EstadoEquipoEnum.INACTIVO.value, EstadoEquipoEnum.MANTENIMIENTO.value])
            ).limit(3).all()
            
            for camara in camaras_criticas:
                alertas.append({
                    'tipo': 'critical',
                    'titulo': f'Cámara crítica: {camara.nombre}',
                    'descripcion': f'Cámara {camara.nombre} en estado {camara.estado}',
                    'timestamp': camara.fecha_actualizacion.isoformat() if camara.fecha_actualizacion else None
                })
        except:
            pass
        
        # Fallas abiertas
        try:
            fallas_criticas = Falla.query.filter(
                Falla.estado == EstadoFallaEnum.ABIERTA.value
            ).order_by(Falla.fecha_creacion.desc()).limit(3).all()
            
            for falla in fallas_criticas:
                alertas.append({
                    'tipo': 'warning',
                    'titulo': f'Falla abierta: {falla.titulo}',
                    'descripcion': f'Falla de prioridad {falla.prioridad}',
                    'timestamp': falla.fecha_creacion.isoformat() if falla.fecha_creacion else None
                })
        except:
            pass
        
        # Mantenimientos vencidos o próximos
        try:
            hoy = datetime.now()
            mantenimientos_urgentes = Mantenimiento.query.filter(
                Mantenimiento.fecha_programada <= hoy,
                Mantenimiento.estado != 'completado'
            ).limit(2).all()
            
            for mantenimiento in mantenimientos_urgentes:
                alertas.append({
                    'tipo': 'info',
                    'titulo': f'Mantenimiento urgente: {mantenimiento.tipo}',
                    'descripcion': f'Mantenimiento programado el {mantenimiento.fecha_programada.strftime("%Y-%m-%d")}',
                    'timestamp': mantenimiento.fecha_programada.isoformat()
                })
        except:
            pass
        
        return jsonify({'alertas': alertas})
        
    except Exception as e:
        logger.error(f"Error obteniendo alertas: {e}")
        return jsonify({'alertas': []})

def calcular_health_score(stats):
    """Calcula un score de salud general del sistema (0-100)"""
    try:
        score = 100
        
        # Penalizar cámaras inactivas
        if stats['total_camaras'] > 0:
            porcentaje_inactivas = ((stats['total_camaras'] - stats['camaras_activas']) / stats['total_camaras']) * 100
            score -= porcentaje_inactivas * 0.3
        
        # Penalizar fallas abiertas
        if stats['total_fallas'] > 0:
            porcentaje_fallas_abiertas = (stats['fallas_abiertas'] / stats['total_fallas']) * 100
            score -= porcentaje_fallas_abiertas * 0.4
        
        # Penalizar si no hay mantenimientos recientes
        if stats['total_mantenimientos'] == 0:
            score -= 10
        
        # Penalizar si no hay usuarios (sistema sin usar)
        if stats['total_usuarios'] == 0:
            score -= 20
        
        # Limitar score entre 0 y 100
        score = max(0, min(100, score))
        
        return round(score, 1)
        
    except Exception as e:
        logger.error(f"Error calculando health score: {e}")
        return 50  # Score neutral por defecto