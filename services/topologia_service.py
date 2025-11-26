# services/topologia_service.py
"""
Servicio de topología de red
Genera diagramas Mermaid para visualizar la infraestructura de red
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class TopologiaService:
"""Servicio para generar diagramas de topología de red"""

def __init__(self, db_session=None):
self.db = db_session

def generate_network_topology(self, level: str = 'general') -> str:
"""
Genera diagrama Mermaid de topología de red
"""
try:
if level == 'camaras':
return self._generate_camera_topology()
elif level == 'switches':
return self._generate_switch_topology()
elif level == 'nvr':
return self._generate_nvr_topology()
else:
return self._generate_general_topology()

except Exception as e:
return self._generate_error_diagram(str(e))

def _generate_general_topology(self) -> str:
"""
Genera topología general del sistema
"""
mermaid_code = """graph TD
Internet[ Internet]
Firewall[ Firewall]
Router[ Router Principal]
CoreSwitch[ Switch Core]
NVR[ NVR Principal]
UPS[ Sistema UPS]

CameraNet[ Red de Cámaras]
Switches[ Switches de Acceso]
ManagementNet[ Red de Gestión]

Internet --> Firewall
Firewall --> Router
Router --> CoreSwitch
CoreSwitch --> NVR
CoreSwitch --> ManagementNet
CoreSwitch --> CameraNet
CameraNet --> Switches
Switches --> UPS

style Internet fill:#e1f5fe
style Firewall fill:#ffebee
style NVR fill:#e8f5e8
style UPS fill:#fff3e0
"""
return mermaid_code

def _generate_camera_topology(self) -> str:
"""
Genera topología específica de cámaras
"""
try:
# Obtener cámaras de la base de datos
cameras = self.db.execute(
"""
SELECT c.id, c.nombre, c.ip, c.tipo, c.estado,
s.nombre as switch_nombre, s.ip as switch_ip,
l.nombre as ubicacion
FROM camaras c
LEFT JOIN switches s ON c.switch_id = s.id
LEFT JOIN ubicaciones l ON c.ubicacion_id = l.id
ORDER BY c.nombre
"""
).fetchall()

if not cameras:
return self._generate_empty_diagram("No hay cámaras registradas")

mermaid_parts = ["graph TD"]

# Nodo principal NVR
mermaid_parts.append(' NVR[ NVR Principal]')

# Agrupar por switches
switches = {}
for camera in cameras:
switch_key = camera.switch_ip or 'sin-switch'
if switch_key not in switches:
switches[switch_key] = {
'nombre': camera.switch_nombre or 'Switch Desconocido',
'camaras': []
}
switches[switch_key]['camaras'].append(camera)

# Agregar switches
for switch_ip, switch_data in switches.items():
switch_id = switch_ip.replace('.', '_')
status_color = "#e8f5e8" # verde por defecto

mermaid_parts.append(f' Switch_{switch_id}[ {switch_data["nombre"]}]')
mermaid_parts.append(f' NVR --> Switch_{switch_id}')

# Agregar cámaras
for switch_ip, switch_data in switches.items():
switch_id = switch_ip.replace('.', '_')

for camera in switch_data['camaras']:
camera_id = f"camera_{camera.id}"
camera_status = "" if camera.estado == 'operativa' else ""
camera_type = self._get_camera_icon(camera.tipo)

# Texto del nodo
node_text = f'{camera_status} {camera.nombre}\\n{camera.tipo}\\n{camera.ip}'
if camera.ubicacion:
node_text += f'\\n {camera.ubicacion}'

mermaid_parts.append(f' {camera_id}[{node_text}]')
mermaid_parts.append(f' Switch_{switch_id} --> {camera_id}')

# Aplicar estilos
mermaid_parts.append("")
mermaid_parts.append(" classDef operative fill:#e8f5e8,stroke:#4caf50,color:#000")
mermaid_parts.append(" classDef offline fill:#ffebee,stroke:#f44336,color:#000")
mermaid_parts.append(" classDef unknown fill:#f3e5f5,stroke:#9c7b0,color:#000")

# Aplicar clases
for camera in cameras:
camera_id = f"camera_{camera.id}"
if camera.estado == 'operativa':
mermaid_parts.append(f" class {camera_id} operative")
elif camera.estado == 'offline':
mermaid_parts.append(f" class {camera_id} offline")
else:
mermaid_parts.append(f" class {camera_id} unknown")

return "\\n".join(mermaid_parts)

except Exception as e:
return self._generate_error_diagram(f"Error generando topología de cámaras: {str(e)}")

def _generate_switch_topology(self) -> str:
"""
Genera topología de switches
"""
try:
switches = self.db.execute(
"""
SELECT s.*, p.nombre as puerto_conectado, p.tipo as tipo_puerto
FROM switches s
LEFT JOIN puertos p ON s.puerto_uplink = p.id
ORDER BY s.nombre
"""
).fetchall()

if not switches:
return self._generate_empty_diagram("No hay switches registrados")

mermaid_parts = ["graph TD"]

# Nodo principal
mermaid_parts.append(' CoreSwitch[ Switch Core]')

# Agregar switches
for switch in switches:
switch_id = f"switch_{switch.id}"
status_color = "#e8f5e8" if switch.estado == 'operativo' else "#ffebee"

switch_info = f' {switch.nombre}\\n{switch.ip}\\n{switch.modelo}'
if switch.puerto_conectado:
switch_info += f'\\n↗ {switch.puerto_conectado}'

mermaid_parts.append(f' {switch_id}[{switch_info}]')

if switch.puerto_uplink:
mermaid_parts.append(f' CoreSwitch <--> {switch_id}')
else:
mermaid_parts.append(f' CoreSwitch --> {switch_id}')

return "\\n".join(mermaid_parts)

except Exception as e:
return self._generate_error_diagram(f"Error generando topología de switches: {str(e)}")

def _generate_nvr_topology(self) -> str:
"""
Genera topología de NVR y dispositivos
"""
try:
nvrs = self.db.execute("SELECT * FROM nvr ORDER BY nombre").fetchall()
ups_systems = self.db.execute("SELECT * FROM ups ORDER BY nombre").fetchall()

mermaid_parts = ["graph TD"]

# Nodo principal de red
mermaid_parts.append(' Network[ Red Principal]')

# NVRs
for nvr in nvrs:
nvr_id = f"nvr_{nvr.id}"
status_color = "#e8f5e8" if nvr.estado == 'operativo' else "#ffebee"

nvr_info = f' {nvr.nombre}\\n{nvr.ip}\\n{nvr.modelo}'
if nvr.capacidad_camaras:
nvr_info += f'\\n {nvr.capacidad_camaras} cámaras'

mermaid_parts.append(f' {nvr_id}[{nvr_info}]')
mermaid_parts.append(f' Network --> {nvr_id}')

# Sistemas UPS
for ups in ups_systems:
ups_id = f"ups_{ups.id}"
ups_info = f' {ups.nombre}\\n{ups.capacidad}VA\\n{ups.autonomia}min'

mermaid_parts.append(f' {ups_id}[{ups_info}]')
mermaid_parts.append(f' Network -.-> {ups_id}')

return "\\n".join(mermaid_parts)

except Exception as e:
return self._generate_error_diagram(f"Error generando topología NVR: {str(e)}")

def _get_camera_icon(self, camera_type: str) -> str:
"""
Obtiene el icono apropiado para el tipo de cámara
"""
icons = {
'domo': '',
'bullet': '',
'ptz': '',
'fisheye': '',
'thermal': ''
}
return icons.get(camera_type.lower(), '')

def _generate_empty_diagram(self, message: str) -> str:
"""
Genera diagrama vacío con mensaje
"""
return f"""graph TD
Empty[ {message}]
style Empty fill:#f3e5f5,stroke:#9c7b0,color:#000"""

def _generate_error_diagram(self, error_message: str) -> str:
"""
Genera diagrama de error
"""
return f"""graph TD
Error[ Error\\n{error_message}]
style Error fill:#ffebee,stroke:#f44336,color:#000"""

def save_topology_diagram(self, nombre: str, diagrama: str, tipo: str = 'general') -> int:
"""
Guarda un diagrama de topología en la base de datos
"""
try:
result = self.db.execute(
"INSERT INTO topologia_diagramas (nombre, diagrama, tipo, created_at) "
"VALUES (%s, %s, %s, %s) RETURNING id",
(nombre, diagrama, tipo, datetime.now())
)
self.db.commit()
return result.fetchone()[0]

except Exception as e:
print(f"Error guardando diagrama: {e}")
self.db.rollback()
return 0

def get_saved_diagrams(self, tipo: str = None) -> List[Dict[str, Any]]:
"""
Obtiene diagramas guardados
"""
try:
query = "SELECT * FROM topologia_diagramas"
params = []

if tipo:
query += " WHERE tipo = %s"
params.append(tipo)

query += " ORDER BY created_at DESC"

results = self.db.execute(query, params).fetchall()

return [{
'id': row.id,
'nombre': row.nombre,
'tipo': row.tipo,
'created_at': row.created_at,
'updated_at': row.updated_at
} for row in results]

except Exception as e:
print(f"Error obteniendo diagramas: {e}")
return []

def get_topology_statistics(self) -> Dict[str, Any]:
"""
Obtiene estadísticas de la topología
"""
try:
stats = {}

# Contar cámaras por estado
camera_stats = self.db.execute(
"""
SELECT estado, COUNT(*) as cantidad
FROM camaras
GROUP BY estado
"""
).fetchall()

stats['camaras'] = {
'total': sum(row.cantidad for row in camera_stats),
'por_estado': {row.estado: row.cantidad for row in camera_stats}
}

# Contar switches
switch_stats = self.db.execute(
"""
SELECT estado, COUNT(*) as cantidad
FROM switches
GROUP BY estado
"""
).fetchall()

stats['switches'] = {
'total': sum(row.cantidad for row in switch_stats),
'por_estado': {row.estado: row.cantidad for row in switch_stats}
}

# Contar NVRs
nvr_count = self.db.execute("SELECT COUNT(*) as total FROM nvr").fetchone()
stats['nvr'] = {'total': nvr_count.total}

# Contar UPS
ups_count = self.db.execute("SELECT COUNT(*) as total FROM ups").fetchone()
stats['ups'] = {'total': ups_count.total}

return stats

except Exception as e:
print(f"Error obteniendo estadísticas: {e}")
return {}

def generate_infrastructure_report(self) -> str:
"""
Genera reporte de infraestructura en formato Mermaid
"""
stats = self.get_topology_statistics()

report = f"""---
title: Reporte de Infraestructura - Sistema de Cámaras UFRO
---

graph TB
subgraph " Resumen General"
TotalCamaras[" Total Cámaras: {stats.get('camaras', {}).get('total', 0)}"]
TotalSwitches[" Total Switches: {stats.get('switches', {}).get('total', 0)}"]
TotalNVR[" Total NVR: {stats.get('nvr', {}).get('total', 0)}"]
TotalUPS[" Total UPS: {stats.get('ups', {}).get('total', 0)}"]
end

subgraph " Estado de Cámaras"
Operativas[" Operativas: {stats.get('camaras', {}).get('por_estado', {}).get('operativa', 0)}"]
Offline[" Fuera de línea: {stats.get('camaras', {}).get('por_estado', {}).get('offline', 0)}"]
Mantenimiento[" Mantenimiento: {stats.get('camaras', {}).get('por_estado', {}).get('mantenimiento', 0)}"]
end

subgraph " Estado de Switches"
SwitchOperativos[" Operativos: {stats.get('switches', {}).get('por_estado', {}).get('operativo', 0)}"]
SwitchOffline[" Fuera de línea: {stats.get('switches', {}).get('por_estado', {}).get('offline', 0)}"]
end

TotalCamaras --> Operativas
TotalCamaras --> Offline
TotalSwitches --> SwitchOperativos
TotalSwitches --> SwitchOffline

style TotalCamaras fill:#e8f5e8
style Operativas fill:#e8f5e8
style Operativas stroke:#4caf50
style Offline fill:#ffebee
style Offline stroke:#f44336"""

return report