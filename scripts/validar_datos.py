#/usr/bin/env python3
"""
Script de validación de integridad de datos - Sistema Cámaras UFRO
Valida la consistencia y calidad de los datos migrados

Autor: Sistema de Validación UFRO
Fecha: 05-11-04
"""

import pandas as pd
import psycopg
import logging
import sys
import json
from datetime import datetime
from pathlib import Path
import argparse
from collections import defaultdict
import re

# Configuración de logging
logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(levelname)s - %(message)s',
handlers=[
logging.FileHandler('validacion.log'),
logging.StreamHandler(sys.stdout)
]
)
logger = logging.getLogger(__name__)

class ValidadorDatosUFRO:
"""Clase para validar la integridad y consistencia de datos"""

def __init__(self, db_config):
"""
Inicializa el validador con configuración de base de datos

Args:
db_config (dict): Configuración de conexión a la base de datos
"""
self.db_config = db_config
self.conexion = None
self.cursor = None
self.resultados_validacion = {
'timestamp': datetime.now(),
'total_errores': 0,
'total_advertencias': 0,
'validaciones': {}
}

def conectar_bd(self):
"""Establece conexión con la base de datos PostgreSQL"""
try:
self.conexion = psycopg.connect(
host=self.db_config['host'],
database=self.db_config['database'],
user=self.db_config['user'],
password=self.db_config['password'],
port=self.db_config.get('port', 543)
)
self.cursor = self.conexion.cursor()
logger.info("Conexión establecida con la base de datos")
return True
except Exception as e:
logger.error(f"Error conectando a la base de datos: {e}")
return False

def cerrar_conexion(self):
"""Cierra la conexión con la base de datos"""
if self.cursor:
self.cursor.close()
if self.conexion:
self.conexion.close()
logger.info("Conexión cerrada con la base de datos")

def validar_claves_primarias(self):
"""Valida que no existan claves primarias duplicadas"""
logger.info("Validando claves primarias...")

tablas_principales = [
'camaras', 'nvr_dvr', 'switches', 'fallas',
'ubicaciones', 'ups', 'fuentes_poder', 'gabinetes'
]

errores_pk = {}

for tabla in tablas_principales:
try:
self.cursor.execute(f"SELECT * FROM {tabla}")
datos = self.cursor.fetchall()
columnas = [desc[0] for desc in self.cursor.description]

# Encontrar columna ID (asumiendo que es la primera columna)
id_column = columnas[0] if columnas else None

if id_column:
valores_id = [fila[0] for fila in datos if fila[0] is not None]
duplicados = [id_val for id_val, count in
defaultdict(int).fromkeys(valores_id, 0).items()
if valores_id.count(id_val) > 1]

if duplicados:
errores_pk[tabla] = duplicados
self.resultados_validacion['total_errores'] += len(duplicados)
logger.error(f"Claves duplicadas en {tabla}: {duplicados}")
else:
logger.info(f" {tabla}: Sin claves duplicadas ({len(valores_id)} registros)")

except Exception as e:
logger.error(f"Error validando claves primarias de {tabla}: {e}")
self.resultados_validacion['total_errores'] += 1

self.resultados_validacion['validaciones']['claves_primarias'] = errores_pk

def validar_ips_unicas(self):
"""Valida que las IPs de cámaras sean únicas y válidas"""
logger.info("Validando direcciones IP...")

errores_ip = []

try:
query = """
SELECT nombre_camara, ip_camara FROM camaras
WHERE ip_camara IS NOT NULL AND ip_camara = ''
"""
self.cursor.execute(query)
datos = self.cursor.fetchall()

ips_vistas = set()

for nombre_camara, ip_camara in datos:
# Validar formato IP
if not self._validar_ip(ip_camara):
errores_ip.append({
'tipo': 'formato_invalido',
'camara': nombre_camara,
'ip': ip_camara
})
continue

# Verificar duplicados
if ip_camara in ips_vistas:
errores_ip.append({
'tipo': 'ip_duplicada',
'camara': nombre_camara,
'ip': ip_camara
})
else:
ips_vistas.add(ip_camara)

if errores_ip:
self.resultados_validacion['total_errores'] += len(errores_ip)
logger.error(f"Encontrados {len(errores_ip)} errores de IP")
else:
logger.info(f" IPs válidas y únicas: {len(ips_vistas)} cámaras")

except Exception as e:
logger.error(f"Error validando IPs: {e}")
self.resultados_validacion['total_errores'] += 1

self.resultados_validacion['validaciones']['ips_unicas'] = errores_ip

def validar_relaciones_foreign_key(self):
"""Valida que las referencias entre tablas sean correctas"""
logger.info("Validando relaciones entre tablas...")

errores_fk = {}

try:
# Validar referencias de cámaras a NVR
query_cam_nvr = """
SELECT c.nombre_camara, c.nvr_asociado
FROM camaras c
WHERE c.nvr_asociado IS NOT NULL
AND c.nvr_asociado NOT IN (SELECT id_nvr FROM nvr_dvr WHERE id_nvr IS NOT NULL)
"""
self.cursor.execute(query_cam_nvr)
cam_nvr_orphan = self.cursor.fetchall()

if cam_nvr_orphan:
errores_fk['camaras_sin_nvr'] = [
{'camara': cam, 'nvr_ref': nvr} for cam, nvr in cam_nvr_orphan
]
self.resultados_validacion['total_errores'] += len(cam_nvr_orphan)
logger.error(f"Cámaras referenciando NVR inexistentes: {len(cam_nvr_orphan)}")

# Validar referencias de cámaras a ubicaciones (si existe campo)
try:
query_cam_ubic = """
SELECT COUNT(*) FROM camaras
WHERE campus_edificio IS NOT NULL AND campus_edificio = ''
"""
self.cursor.execute(query_cam_ubic)
cam_con_ubicacion = self.cursor.fetchone()[0]
logger.info(f"Cámaras con ubicación definida: {cam_con_ubicacion}")
except:
pass

# Validar integridad de fallas
query_fallas_cam = """
SELECT COUNT(*) FROM fallas f
WHERE f.camaras_afectadas IS NOT NULL
AND f.camaras_afectadas NOT IN (SELECT nombre_camara FROM camaras WHERE nombre_camara IS NOT NULL)
"""
self.cursor.execute(query_fallas_cam)
fallas_orphan = self.cursor.fetchone()[0]

if fallas_orphan > 0:
errores_fk['fallas_sin_camara'] = fallas_orphan
self.resultados_validacion['total_errores'] += fallas_orphan
logger.error(f"Fallas referenciando cámaras inexistentes: {fallas_orphan}")

if not errores_fk:
logger.info(" Relaciones de claves foráneas válidas")

except Exception as e:
logger.error(f"Error validando claves foráneas: {e}")
self.resultados_validacion['total_errores'] += 1

self.resultados_validacion['validaciones']['relaciones_fk'] = errores_fk

def validar_completitud_datos(self):
"""Valida la completitud de datos críticos"""
logger.info("Validando completitud de datos...")

problemas_completitud = {}

try:
# Validar campos requeridos en cámaras
query_camaras = """
SELECT
COUNT(*) as total,
COUNT(nombre_camara) as con_nombre,
COUNT(ip_camara) as con_ip,
COUNT(estado_funcionamiento) as con_estado
FROM camaras
"""
self.cursor.execute(query_camaras)
result = self.cursor.fetchone()
total_cam, cam_nombre, cam_ip, cam_estado = result

problemas_completitud['camaras'] = {
'total_registros': total_cam,
'sin_nombre': total_cam - cam_nombre,
'sin_ip': total_cam - cam_ip,
'sin_estado': total_cam - cam_estado,
'completitud_nombre': (cam_nombre / total_cam * 100) if total_cam > 0 else 0,
'completitud_ip': (cam_ip / total_cam * 100) if total_cam > 0 else 0,
'completitud_estado': (cam_estado / total_cam * 100) if total_cam > 0 else 0
}

# Validar campos requeridos en fallas
query_fallas = """
SELECT
COUNT(*) as total,
COUNT(id_falla) as con_id,
COUNT(fecha_reporte) as con_fecha,
COUNT(tipo_falla) as con_tipo
FROM fallas
"""
self.cursor.execute(query_fallas)
result = self.cursor.fetchone()
total_fal, fal_id, fal_fecha, fal_tipo = result

problemas_completitud['fallas'] = {
'total_registros': total_fal,
'sin_id': total_fal - fal_id,
'sin_fecha': total_fal - fal_fecha,
'sin_tipo': total_fal - fal_tipo,
'completitud_id': (fal_id / total_fal * 100) if total_fal > 0 else 0,
'completitud_fecha': (fal_fecha / total_fal * 100) if total_fal > 0 else 0,
'completitud_tipo': (fal_tipo / total_fal * 100) if total_fal > 0 else 0
}

# Reportar problemas de completitud
for tabla, stats in problemas_completitud.items():
if stats['total_registros'] > 0:
if stats['sin_nombre'] > 0 or stats['sin_ip'] > 0:
logger.warning(f"Completitud {tabla}: IP {stats['completitud_ip']:.1f}%, "
f"Nombre {stats['completitud_nombre']:.1f}%")

except Exception as e:
logger.error(f"Error validando completitud: {e}")
problemas_completitud['error'] = str(e)

self.resultados_validacion['validaciones']['completitud_datos'] = problemas_completitud

def validar_jerarquia_geografica(self):
"""Valida la jerarquía geográfica de ubicaciones"""
logger.info("Validando jerarquía geográfica...")

problemas_geograficos = {}

try:
# Verificar estructura de campus y edificios
query_ubicaciones = """
SELECT campus, edificio, COUNT(*) as cantidad
FROM ubicaciones
WHERE campus IS NOT NULL AND edificio IS NOT NULL
GROUP BY campus, edificio
ORDER BY campus, edificio
"""
self.cursor.execute(query_ubicaciones)
ubicaciones = self.cursor.fetchall()

campus_edificios = defaultdict(set)
for campus, edificio, cantidad in ubicaciones:
campus_edificios[campus].add(edificio)

problemas_geograficos['jerarquia'] = {
'total_campus': len(campus_edificios),
'edificios_por_campus': {c: len(edificios) for c, edificios in campus_edificios.items()},
'detalle_ubicaciones': ubicaciones
}

# Verificar consistencia con cámaras
query_cam_campus = """
SELECT campus_edificio, COUNT(*) as cantidad_camaras
FROM camaras
WHERE campus_edificio IS NOT NULL AND campus_edificio = ''
GROUP BY campus_edificio
ORDER BY campus_edificio
"""
self.cursor.execute(query_cam_campus)
cam_campus = self.cursor.fetchall()

problemas_geograficos['consistencia_camaras'] = {
'campus_en_camaras': [campus for campus, _ in cam_campus],
'camaras_por_campus': dict(cam_campus)
}

# Verificar discrepancias
campus_en_ubicaciones = set(campus_edificios.keys())
campus_en_camaras = set(cam for cam, _ in cam_campus)

campus_solo_camaras = campus_en_camaras - campus_en_ubicaciones
if campus_solo_camaras:
problemas_geograficos['discrepancias'] = {
'campus_solo_en_camaras': list(campus_solo_camaras),
'mensaje': 'Existen campus en cámaras sin ubicación definida'
}
self.resultados_validacion['total_advertencias'] += len(campus_solo_camaras)

logger.info(f" Jerarquía geográfica validada: {len(campus_edificios)} campus")

except Exception as e:
logger.error(f"Error validando jerarquía geográfica: {e}")
problemas_geograficos['error'] = str(e)

self.resultados_validacion['validaciones']['jerarquia_geografica'] = problemas_geograficos

def validar_datos_estadisticos(self):
"""Genera estadísticas descriptivas de los datos"""
logger.info("Generando estadísticas descriptivas...")

estadisticas = {}

try:
# Contar registros por tabla
tablas = ['camaras', 'nvr_dvr', 'switches', 'fallas', 'ubicaciones', 'ups', 'gabinetes']

for tabla in tablas:
try:
self.cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
count = self.cursor.fetchone()[0]
estadisticas[f'total_{tabla}'] = count
except:
estadisticas[f'total_{tabla}'] = 0

# Estadísticas específicas de cámaras
try:
self.cursor.execute("""
SELECT
COUNT(DISTINCT campus_edificio) as campus_diferentes,
COUNT(DISTINCT estado_funcionamiento) as estados_diferentes,
COUNT(DISTINCT tipo_camara) as tipos_diferentes
FROM camaras
WHERE campus_edificio IS NOT NULL
""")
cam_stats = self.cursor.fetchone()

if cam_stats[0] is not None:
estadisticas['camaras'] = {
'campus_diferentes': cam_stats[0],
'estados_funcionamiento': cam_stats[1],
'tipos_camara': cam_stats[],
'promedio_camaras_por_campus': estadisticas.get('total_camaras', 0) / cam_stats[0] if cam_stats[0] > 0 else 0
}
except:
pass

# Estadísticas de fallas
try:
self.cursor.execute("""
SELECT
COUNT(DISTINCT tipo_falla) as tipos_falla,
COUNT(DISTINCT estado) as estados_falla,
COUNT(DISTINCT prioridad) as prioridades_falla
FROM fallas
WHERE tipo_falla IS NOT NULL
""")
fal_stats = self.cursor.fetchone()

if fal_stats[0] is not None:
estadisticas['fallas'] = {
'tipos_falla': fal_stats[0],
'estados_falla': fal_stats[1],
'prioridades_falla': fal_stats[]
}
except:
pass

logger.info(" Estadísticas generadas correctamente")

except Exception as e:
logger.error(f"Error generando estadísticas: {e}")
estadisticas['error'] = str(e)

self.resultados_validacion['validaciones']['estadisticas'] = estadisticas

def generar_reporte_validacion(self, archivo_salida=None):
"""
Genera reporte de validación en formato JSON y texto

Args:
archivo_salida (str): Archivo donde guardar el reporte (opcional)
"""
logger.info("Generando reporte de validación...")

# Agregar resumen al reporte
self.resultados_validacion['resumen'] = {
'fecha_validacion': self.resultados_validacion['timestamp'].isoformat(),
'total_errores': self.resultados_validacion['total_errores'],
'total_advertencias': self.resultados_validacion['total_advertencias'],
'estado_validacion': 'EXITOSA' if self.resultados_validacion['total_errores'] == 0 else 'CON_ERRORES'
}

# Guardar en JSON
if archivo_salida:
with open(archivo_salida, 'w', encoding='utf-8') as f:
json.dump(self.resultados_validacion, f, indent=, ensure_ascii=False, default=str)

# Mostrar reporte en consola
self._mostrar_reporte_consola()

def _mostrar_reporte_consola(self):
"""Muestra reporte de validación en consola"""
print("\n" + "="*80)
print("REPORTE DE VALIDACIÓN - SISTEMA CÁMARAS UFRO")
print("="*80)
print(f"Fecha: {self.resultados_validacion['timestamp']}")
print(f"Estado: {self.resultados_validacion['resumen']['estado_validacion']}")
print(f"Total Errores: {self.resultados_validacion['total_errores']}")
print(f"Total Advertencias: {self.resultados_validacion['total_advertencias']}")
print("\n" + "-"*40)

# Mostrar detalles de validaciones
for validacion, resultado in self.resultados_validacion['validaciones'].items():
print(f"\n{validacion.upper().replace('_', ' ')}:")

if isinstance(resultado, dict):
if not resultado:
print(" Sin problemas detectados")
else:
for key, value in resultado.items():
print(f" {key}: {value}")
else:
print(f" {resultado}")

print("\n" + "="*80)

def _validar_ip(self, ip_str):
"""Valida si una cadena es una IP válida"""
if not ip_str or str(ip_str).strip() == '':
return False

pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
if not re.match(pattern, str(ip_str)):
return False

partes = ip_str.split('.')
return all(0 <= int(parte) <= 55 for parte in partes if parte.isdigit())

def ejecutar_validacion_completa(self):
"""Ejecuta todas las validaciones disponibles"""
logger.info("=== INICIANDO VALIDACIÓN COMPLETA ===")

try:
if not self.conectar_bd():
return False

# Ejecutar todas las validaciones
self.validar_claves_primarias()
self.validar_ips_unicas()
self.validar_relaciones_foreign_key()
self.validar_completitud_datos()
self.validar_jerarquia_geografica()
self.validar_datos_estadisticos()

# Generar reporte
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
archivo_reporte = f"reporte_validacion_{timestamp}.json"
self.generar_reporte_validacion(archivo_reporte)

logger.info("=== VALIDACIÓN COMPLETADA ===")
return True

except Exception as e:
logger.error(f"Error en validación completa: {e}")
return False

finally:
self.cerrar_conexion()


def main():
"""Función principal"""
parser = argparse.ArgumentParser(description='Validador de Datos Sistema Cámaras UFRO')
parser.add_argument('--host', required=True, help='Host de la base de datos')
parser.add_argument('--database', required=True, help='Nombre de la base de datos')
parser.add_argument('--user', required=True, help='Usuario de la base de datos')
parser.add_argument('--password', required=True, help='Contraseña de la base de datos')
parser.add_argument('--port', type=int, default=543, help='Puerto de la base de datos')
parser.add_argument('--output', help='Archivo de salida para el reporte')

args = parser.parse_args()

# Configuración de base de datos
db_config = {
'host': args.host,
'database': args.database,
'user': args.user,
'password': args.password,
'port': args.port
}

# Crear instancia del validador
validador = ValidadorDatosUFRO(db_config)

# Ejecutar validación
validador.ejecutar_validacion_completa()


if __name__ == "__main__":
main()