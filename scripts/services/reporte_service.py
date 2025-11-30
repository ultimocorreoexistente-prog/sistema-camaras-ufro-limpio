# services/reporte_service.py
"""
Servicio de reportes
Genera reportes completos del sistema en múltiples formatos
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import io
from collections import defaultdict

class ReporteService:
"""Servicio para generar reportes del sistema"""

def __init__(self, db_session=None):
self.db = db_session

def generate_dashboard_report(self) -> Dict[str, Any]:
"""
Genera reporte principal del dashboard
"""
try:
report = {
'timestamp': datetime.now().isoformat(),
'resumen_ejecutivo': self._get_ejecutive_summary(),
'estadisticas_generales': self._get_general_statistics(),
'estado_equipos': self._get_equipment_status(),
'fallas_recientes': self._get_recent_failures(),
'mantenimientos_pendientes': self._get_pending_maintenance(),
'tendencias': self._get_trends(),
'alertas': self._get_alerts()
}

return {
'success': True,
'report': report
}

except Exception as e:
return {
'success': False,
'error': f'Error generando reporte dashboard: {str(e)}'
}

def _get_ejecutive_summary(self) -> Dict[str, Any]:
"""
Genera resumen ejecutivo del sistema
"""
try:
# Estadísticas principales
total_camaras = self.db.execute(
"SELECT COUNT(*) FROM camaras"
).fetchone()[0]

camaras_operativas = self.db.execute(
"SELECT COUNT(*) FROM camaras WHERE estado = 'operativa'"
).fetchone()[0]

total_fallas = self.db.execute(
"SELECT COUNT(*) FROM fallas"
).fetchone()[0]

fallas_abiertas = self.db.execute(
"SELECT COUNT(*) FROM fallas WHERE estado = 'cerrada'"
).fetchone()[0]

uptime_percentage = (camaras_operativas / total_camaras * 100) if total_cameras > 0 else 0

return {
'total_equipos': total_cameras,
'equipos_operativos': camaras_operativas,
'porcentaje_uptime': round(uptime_percentage, ),
'total_fallas_historicas': total_fallas,
'fallas_abiertas': fallas_abiertas,
'estado_general': self._calculate_overall_status(uptime_percentage, fallas_abiertas),
'recomendaciones': self._generate_recommendations(uptime_percentage, fallas_abiertas)
}

except Exception as e:
print(f"Error en resumen ejecutivo: {e}")
return {}

def _calculate_overall_status(self, uptime: float, open_failures: int) -> str:
"""
Calcula el estado general del sistema
"""
if uptime >= 95 and open_failures <= 5:
return "Excelente"
elif uptime >= 90 and open_failures <= 10:
return "Bueno"
elif uptime >= 80 and open_failures <= 0:
return "Regular"
else:
return "Crítico"

def _generate_recommendations(self, uptime: float, open_failures: int) -> List[str]:
"""
Genera recomendaciones basadas en métricas
"""
recommendations = []

if uptime < 90:
recommendations.append("Revisar cámaras con problemas de conectividad")

if open_failures > 10:
recommendations.append("Priorizar resolución de fallas abiertas")

if uptime < 80:
recommendations.append("Considerar mantenimiento preventivo general")

return recommendations

def _get_general_statistics(self) -> Dict[str, Any]:
"""
Obtiene estadísticas generales del sistema
"""
try:
stats = {}

# Estadísticas por tipo de equipo
equipos_stats = self.db.execute("""
SELECT tipo, estado, COUNT(*) as cantidad
FROM camaras
GROUP BY tipo, estado
""").fetchall()

stats['por_tipo'] = defaultdict(dict)
for row in equipos_stats:
stats['por_tipo'][row.tipo][row.estado] = row.cantidad

# Distribución geográfica
ubicaciones_stats = self.db.execute("""
SELECT l.nombre as ubicacion, COUNT(c.id) as cantidad
FROM camaras c
JOIN ubicaciones l ON c.ubicacion_id = l.id
GROUP BY l.nombre
ORDER BY cantidad DESC
""").fetchall()

stats['por_ubicacion'] = {row.ubicacion: row.cantidad for row in ubicaciones_stats}

# Estadísticas de red
switches_stats = self.db.execute("""
SELECT estado, COUNT(*) as cantidad
FROM switches
GROUP BY estado
""").fetchall()

stats['switches'] = {row.estado: row.cantidad for row in switches_stats}

return stats

except Exception as e:
print(f"Error obteniendo estadísticas generales: {e}")
return {}

def _get_equipment_status(self) -> Dict[str, Any]:
"""
Obtiene estado detallado de equipos
"""
try:
equipment = {}

# Cámaras con problemas
problematic_cameras = self.db.execute("""
SELECT c.nombre, c.tipo, c.estado, l.nombre as ubicacion, c.observaciones
FROM camaras c
LEFT JOIN ubicaciones l ON c.ubicacion_id = l.id
WHERE c.estado = 'operativa'
ORDER BY c.estado, c.nombre
""").fetchall()

equipment['camaras_problematicas'] = [{
'nombre': row.nombre,
'tipo': row.tipo,
'estado': row.estado,
'ubicacion': row.ubicacion,
'observaciones': row.observaciones
} for row in problematic_cameras]

# Switches con problemas
problematic_switches = self.db.execute("""
SELECT s.nombre, s.ip, s.estado, s.observaciones
FROM switches s
WHERE s.estado = 'operativo'
ORDER BY s.estado, s.nombre
""").fetchall()

equipment['switches_problematicos'] = [{
'nombre': row.nombre,
'ip': row.ip,
'estado': row.estado,
'observaciones': row.observaciones
} for row in problematic_switches]

return equipment

except Exception as e:
print(f"Error obteniendo estado de equipos: {e}")
return {}

def _get_recent_failures(self, days: int = 30) -> List[Dict[str, Any]]:
"""
Obtiene fallas recientes
"""
try:
since_date = datetime.now() - timedelta(days=days)

failures = self.db.execute("""
SELECT f.id, f.titulo, f.severidad, f.estado, f.fecha_reporte,
c.nombre as camara, u.nombre as reportado_por
FROM fallas f
LEFT JOIN camaras c ON f.camara_id = c.id
LEFT JOIN usuarios u ON f.usuario_reporta_id = u.id
WHERE f.fecha_reporte >= %s
ORDER BY f.fecha_reporte DESC
""", (since_date,)).fetchall()

return [{
'id': row.id,
'titulo': row.titulo,
'severidad': row.severidad,
'estado': row.estado,
'fecha_reporte': row.fecha_reporte,
'camara': row.camara,
'reportado_por': row.reportado_por
} for row in failures]

except Exception as e:
print(f"Error obteniendo fallas recientes: {e}")
return []

def _get_pending_maintenance(self) -> List[Dict[str, Any]]:
"""
Obtiene mantenimientos pendientes
"""
try:
now = datetime.now()

maintenance = self.db.execute("""
SELECT m.id, m.tipo, m.descripcion, m.fecha_programada,
c.nombre as camara, u.nombre as tecnico
FROM mantenimientos m
LEFT JOIN camaras c ON m.camara_id = c.id
LEFT JOIN usuarios u ON m.tecnico_id = u.id
WHERE m.estado = 'programado' AND m.fecha_programada >= %s
ORDER BY m.fecha_programada ASC
""", (now,)).fetchall()

return [{
'id': row.id,
'tipo': row.tipo,
'descripcion': row.descripcion,
'fecha_programada': row.fecha_programada,
'camara': row.camara,
'tecnico': row.tecnico
} for row in maintenance]

except Exception as e:
print(f"Error obteniendo mantenimientos pendientes: {e}")
return []

def _get_trends(self) -> Dict[str, Any]:
"""
Obtiene tendencias y análisis de patrones
"""
try:
trends = {}

# Tendencia de fallas por mes
monthly_failures = self.db.execute("""
SELECT
DATE_TRUNC('month', fecha_reporte) as mes,
COUNT(*) as cantidad,
COUNT(CASE WHEN estado = 'cerrada' THEN 1 END) as resueltas
FROM fallas
WHERE fecha_reporte >= %s
GROUP BY DATE_TRUNC('month', fecha_reporte)
ORDER BY mes
""", (datetime.now() - timedelta(days=365),)).fetchall()

trends['fallas_por_mes'] = [{
'mes': row.mes.strftime('%Y-%m'),
'total': row.cantidad,
'resueltas': row.resueltas,
'pendientes': row.cantidad - row.resueltas
} for row in monthly_failures]

# Análisis de severidad
severity_analysis = self.db.execute("""
SELECT severidad, COUNT(*) as cantidad,
AVG(EXTRACT(EPOCH FROM (fecha_solucion - fecha_reporte))/3600) as tiempo_promedio_horas
FROM fallas
WHERE fecha_reporte >= %s
GROUP BY severidad
""", (datetime.now() - timedelta(days=90),)).fetchall()

trends['analisis_severidad'] = [{
'severidad': row.severidad,
'cantidad': row.cantidad,
'tiempo_promedio_resolucion': round(row.tiempo_promedio_horas or 0, )
} for row in severity_analysis]

return trends

except Exception as e:
print(f"Error obteniendo tendencias: {e}")
return {}

def _get_alerts(self) -> List[Dict[str, Any]]:
"""
Obtiene alertas del sistema
"""
alerts = []

try:
# Cámaras fuera de línea por más de 4 horas
offline_cameras = self.db.execute("""
SELECT c.nombre, c.ultima_actualizacion
FROM camaras c
WHERE c.estado = 'offline' AND c.ultima_actualizacion < %s
""", (datetime.now() - timedelta(hours=4),)).fetchall()

for camera in offline_cameras:
alerts.append({
'tipo': 'critical',
'titulo': 'Cámara desconectada',
'descripcion': f'La cámara {camera.nombre} ha estado desconectada por más de 4 horas',
'timestamp': camera.ultima_actualizacion,
'recomendacion': 'Verificar conectividad de red y alimentación eléctrica'
})

# Mantenimientos vencidos
overdue_maintenance = self.db.execute("""
SELECT m.tipo, c.nombre as camara, m.fecha_programada
FROM mantenimientos m
JOIN camaras c ON m.camara_id = c.id
WHERE m.estado = 'programado' AND m.fecha_programada < %s
""", (datetime.now(),)).fetchall()

for maint in overdue_maintenance:
alerts.append({
'tipo': 'warning',
'titulo': 'Mantenimiento vencido',
'descripcion': f'Mantenimiento {maint.tipo} vencido para cámara {maint.camara}',
'timestamp': maint.fecha_programada,
'recomendacion': 'Programar mantenimiento inmediatamente'
})

return alerts

except Exception as e:
print(f"Error obteniendo alertas: {e}")
return []

def generate_failure_analysis_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
"""
Genera reporte de análisis de fallas
"""
try:
report = {
'periodo': {'inicio': start_date, 'fin': end_date},
'resumen_fallas': self._analyze_failures_period(start_date, end_date),
'analisis_por_camara': self._analyze_failures_by_camera(start_date, end_date),
'analisis_temporal': self._analyze_failures_temporal(start_date, end_date),
'metricas_rendimiento': self._calculate_failure_metrics(start_date, end_date)
}

return {
'success': True,
'report': report
}

except Exception as e:
return {
'success': False,
'error': f'Error generando reporte de fallas: {str(e)}'
}

def _analyze_failures_period(self, start_date: str, end_date: str) -> Dict[str, Any]:
"""
Analiza fallas en un período específico
"""
try:
# Estadísticas generales del período
stats = self.db.execute("""
SELECT
COUNT(*) as total_fallas,
COUNT(CASE WHEN estado = 'cerrada' THEN 1 END) as fallas_resueltas,
COUNT(CASE WHEN estado = 'cerrada' THEN 1 END) as fallas_abiertas,
COUNT(CASE WHEN severidad = 'alta' THEN 1 END) as severidad_alta,
COUNT(CASE WHEN severidad = 'media' THEN 1 END) as severidad_media,
COUNT(CASE WHEN severidad = 'baja' THEN 1 END) as severidad_baja
FROM fallas
WHERE fecha_reporte >= %s AND fecha_reporte <= %s
""", (start_date, end_date)).fetchone()

return {
'total_fallas': stats.total_fallas or 0,
'fallas_resueltas': stats.fallas_resueltas or 0,
'fallas_abiertas': stats.fallas_abiertas or 0,
'por_severidad': {
'alta': stats.severidad_alta or 0,
'media': stats.severidad_media or 0,
'baja': stats.severidad_baja or 0
},
'tasa_resolucion': round((stats.fallas_resueltas or 0) / (stats.total_fallas or 1) * 100, )
}

except Exception as e:
print(f"Error analizando fallas del período: {e}")
return {}

def _analyze_failures_by_camera(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
"""
Analiza fallas agrupadas por cámara
"""
try:
results = self.db.execute("""
SELECT
c.nombre as camara,
c.tipo,
l.nombre as ubicacion,
COUNT(f.id) as total_fallas,
COUNT(CASE WHEN f.estado = 'cerrada' THEN 1 END) as resueltas,
COUNT(CASE WHEN f.severidad = 'alta' THEN 1 END) as severidad_alta
FROM camaras c
LEFT JOIN fallas f ON c.id = f.camara_id
AND f.fecha_reporte >= %s AND f.fecha_reporte <= %s
LEFT JOIN ubicaciones l ON c.ubicacion_id = l.id
GROUP BY c.id, c.nombre, c.tipo, l.nombre
HAVING COUNT(f.id) > 0
ORDER BY total_fallas DESC
""", (start_date, end_date)).fetchall()

return [{
'camara': row.camara,
'tipo': row.tipo,
'ubicacion': row.ubicacion,
'total_fallas': row.total_fallas,
'resueltas': row.resueltas,
'severidad_alta': row.severidad_alta,
'tasa_resolucion': round((row.resueltas or 0) / row.total_fallas * 100, )
} for row in results]

except Exception as e:
print(f"Error analizando fallas por cámara: {e}")
return []

def _analyze_failures_temporal(self, start_date: str, end_date: str) -> Dict[str, Any]:
"""
Analiza patrones temporales de fallas
"""
try:
# Fallas por día de la semana
by_weekday = self.db.execute("""
SELECT
EXTRACT(dow FROM fecha_reporte) as dia_semana,
COUNT(*) as cantidad
FROM fallas
WHERE fecha_reporte >= %s AND fecha_reporte <= %s
GROUP BY EXTRACT(dow FROM fecha_reporte)
ORDER BY dia_semana
""", (start_date, end_date)).fetchall()

# Fallas por hora del día
by_hour = self.db.execute("""
SELECT
EXTRACT(hour FROM fecha_reporte) as hora,
COUNT(*) as cantidad
FROM fallas
WHERE fecha_reporte >= %s AND fecha_reporte <= %s
GROUP BY EXTRACT(hour FROM fecha_reporte)
ORDER BY hora
""", (start_date, end_date)).fetchall()

return {
'por_dia_semana': {int(row.dia_semana): row.cantidad for row in by_weekday},
'por_hora': {int(row.hora): row.cantidad for row in by_hour}
}

except Exception as e:
print(f"Error analizando fallas temporal: {e}")
return {}

def _calculate_failure_metrics(self, start_date: str, end_date: str) -> Dict[str, Any]:
"""
Calcula métricas de rendimiento de fallas
"""
try:
metrics = {}

# Tiempo promedio de resolución
avg_resolution = self.db.execute("""
SELECT AVG(EXTRACT(EPOCH FROM (fecha_solucion - fecha_reporte))/3600) as avg_hours
FROM fallas
WHERE fecha_reporte >= %s AND fecha_reporte <= %s
AND fecha_solucion IS NOT NULL
""", (start_date, end_date)).fetchone()

metrics['tiempo_promedio_resolucion_horas'] = round(avg_resolution.avg_hours or 0, )

# Tiempo máximo de resolución
max_resolution = self.db.execute("""
SELECT MAX(EXTRACT(EPOCH FROM (fecha_solucion - fecha_reporte))/3600) as max_hours
FROM fallas
WHERE fecha_reporte >= %s AND fecha_reporte <= %s
AND fecha_solucion IS NOT NULL
""", (start_date, end_date)).fetchone()

metrics['tiempo_maximo_resolucion_horas'] = round(max_resolution.max_hours or 0, )

return metrics

except Exception as e:
print(f"Error calculando métricas: {e}")
return {}

def export_report_to_json(self, report_data: Dict[str, Any]) -> bytes:
"""
Exporta un reporte a formato JSON
"""
try:
json_data = json.dumps(report_data, indent=, default=str, ensure_ascii=False)
return json_data.encode('utf-8')

except Exception as e:
raise Exception(f"Error exportando reporte a JSON: {str(e)}")

def save_report(self, nombre: str, tipo: str, data: Dict[str, Any]) -> int:
"""
Guarda un reporte en la base de datos
"""
try:
result = self.db.execute(
"""
INSERT INTO reportes (nombre, tipo, data, created_at)
VALUES (%s, %s, %s, %s)
RETURNING id
""",
(nombre, tipo, json.dumps(data, default=str), datetime.now())
)
self.db.commit()
return result.fetchone()[0]

except Exception as e:
print(f"Error guardando reporte: {e}")
self.db.rollback()
return 0