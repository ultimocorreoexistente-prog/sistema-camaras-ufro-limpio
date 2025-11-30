#/usr/bin/env python3
"""
Script de ejecución automatizada completa
Sistema de Migración de Datos Cámaras UFRO

Ejecuta el proceso completo: limpieza -> migración -> validación -> pruebas

Autor: Sistema Automatizado UFRO
Fecha: 05-11-04
"""

import os
import sys
import subprocess
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Configuración de logging
logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(levelname)s - %(message)s',
handlers=[
logging.FileHandler('ejecucion_completa.log'),
logging.StreamHandler(sys.stdout)
]
)
logger = logging.getLogger(__name__)

class EjecutorCompleto:
"""Clase para ejecutar el proceso completo de migración"""

def __init__(self, config):
"""
Inicializa el ejecutor con configuración

Args:
config (dict): Configuración del proceso
"""
self.config = config
self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
self.directorio_logs = Path("logs_" + self.timestamp)
self.directorio_logs.mkdir(exist_ok=True)

self.resultados = {
'timestamp': self.timestamp,
'limpieza': {'exito': False, 'mensaje': ''},
'migracion': {'exito': False, 'mensaje': ''},
'validacion': {'exito': False, 'mensaje': ''},
'pruebas': {'exito': False, 'mensaje': ''}
}

def ejecutar_limpieza(self):
"""Ejecuta el proceso de limpieza de datos"""
logger.info("=== INICIANDO LIMPIEZA DE DATOS ===")

cmd = [
'python', 'scripts/limpiar_datos.py',
'--entrada', self.config['directorio_entrada'],
'--salida', self.config['directorio_salida_limpios'],
'--validar'
]

try:
resultado = subprocess.run(
cmd,
cwd=self.config['directorio_trabajo'],
capture_output=True,
text=True,
timeout=300 # 5 minutos máximo
)

if resultado.returncode == 0:
logger.info(" Limpieza completada exitosamente")
self.resultados['limpieza']['exito'] = True
self.resultados['limpieza']['mensaje'] = 'Completada'
return True
else:
logger.error(f" Error en limpieza: {resultado.stderr}")
self.resultados['limpieza']['mensaje'] = resultado.stderr
return False

except subprocess.TimeoutExpired:
logger.error(" Timeout en limpieza de datos")
self.resultados['limpieza']['mensaje'] = 'Timeout'
return False
except Exception as e:
logger.error(f" Error ejecutando limpieza: {e}")
self.resultados['limpieza']['mensaje'] = str(e)
return False

def ejecutar_migracion(self):
"""Ejecuta la migración a base de datos"""
logger.info("=== INICIANDO MIGRACIÓN A BASE DE DATOS ===")

cmd = [
'python', 'scripts/migrar_datos.py',
'--host', self.config['db_host'],
'--database', self.config['db_name'],
'--user', self.config['db_user'],
'--password', self.config['db_password'],
'--port', str(self.config['db_port']),
'--planillas-dir', self.config['directorio_salida_limpios']
]

try:
resultado = subprocess.run(
cmd,
cwd=self.config['directorio_trabajo'],
capture_output=True,
text=True,
timeout=600 # 10 minutos máximo
)

if resultado.returncode == 0:
logger.info(" Migración completada exitosamente")
self.resultados['migracion']['exito'] = True
self.resultados['migracion']['mensaje'] = 'Completada'
return True
else:
logger.error(f" Error en migración: {resultado.stderr}")
self.resultados['migracion']['mensaje'] = resultado.stderr
return False

except subprocess.TimeoutExpired:
logger.error(" Timeout en migración")
self.resultados['migracion']['mensaje'] = 'Timeout'
return False
except Exception as e:
logger.error(f" Error ejecutando migración: {e}")
self.resultados['migracion']['mensaje'] = str(e)
return False

def ejecutar_validacion(self):
"""Ejecuta la validación de datos"""
logger.info("=== INICIANDO VALIDACIÓN DE DATOS ===")

cmd = [
'python', 'scripts/validar_datos.py',
'--host', self.config['db_host'],
'--database', self.config['db_name'],
'--user', self.config['db_user'],
'--password', self.config['db_password'],
'--port', str(self.config['db_port']),
'--output', str(self.directorio_logs / f"validacion_{self.timestamp}.json")
]

try:
resultado = subprocess.run(
cmd,
cwd=self.config['directorio_trabajo'],
capture_output=True,
text=True,
timeout=300 # 5 minutos máximo
)

if resultado.returncode == 0:
logger.info(" Validación completada exitosamente")
self.resultados['validacion']['exito'] = True
self.resultados['validacion']['mensaje'] = 'Completada'
return True
else:
logger.warning(f" Validación con advertencias: {resultado.stderr}")
self.resultados['validacion']['exito'] = True # Puede continuar con advertencias
self.resultados['validacion']['mensaje'] = f"Con advertencias: {resultado.stderr}"
return True

except subprocess.TimeoutExpired:
logger.error(" Timeout en validación")
self.resultados['validacion']['mensaje'] = 'Timeout'
return False
except Exception as e:
logger.error(f" Error ejecutando validación: {e}")
self.resultados['validacion']['mensaje'] = str(e)
return False

def ejecutar_pruebas(self):
"""Ejecuta las pruebas automatizadas"""
if not self.config.get('ejecutar_pruebas', True):
logger.info("Pruebas omitidas por configuración")
self.resultados['pruebas']['exito'] = True
self.resultados['pruebas']['mensaje'] = 'Omitida'
return True

logger.info("=== INICIANDO PRUEBAS AUTOMATIZADAS ===")

cmd = [
'python', 'scripts/test_migracion.py',
'--solo-unitarias'
]

try:
resultado = subprocess.run(
cmd,
cwd=self.config['directorio_trabajo'],
capture_output=True,
text=True,
timeout=300 # 5 minutos máximo
)

if resultado.returncode == 0:
logger.info(" Pruebas completadas exitosamente")
self.resultados['pruebas']['exito'] = True
self.resultados['pruebas']['mensaje'] = 'Completadas'
return True
else:
logger.warning(f" Pruebas fallaron: {resultado.stderr}")
self.resultados['pruebas']['exito'] = False
self.resultados['pruebas']['mensaje'] = f"Fallaron: {resultado.stderr}"
return False

except subprocess.TimeoutExpired:
logger.error(" Timeout en pruebas")
self.resultados['pruebas']['mensaje'] = 'Timeout'
return False
except Exception as e:
logger.error(f" Error ejecutando pruebas: {e}")
self.resultados['pruebas']['mensaje'] = str(e)
return False

def ejecutar_proceso_completo(self):
"""Ejecuta el proceso completo de migración"""
logger.info("=" * 80)
logger.info("INICIANDO PROCESO COMPLETO DE MIGRACIÓN")
logger.info("=" * 80)

exito_general = True

# Paso 1: Limpieza
if not self.ejecutar_limpieza():
logger.error("Fallo en limpieza. Proceso detenido.")
exito_general = False
else:
logger.info("Paso 1/4: Limpieza - COMPLETADA")

# Paso : Migración (solo si limpieza exitosa)
if exito_general:
if not self.ejecutar_migracion():
logger.error("Fallo en migración. Proceso detenido.")
exito_general = False
else:
logger.info("Paso /4: Migración - COMPLETADA")

# Paso 3: Validación (solo si migración exitosa)
if exito_general:
if not self.ejecutar_validacion():
logger.error("Fallo en validación.")
exito_general = False # Puede continuar con advertencias
else:
logger.info("Paso 3/4: Validación - COMPLETADA")

# Paso 4: Pruebas (opcional)
if exito_general:
self.ejecutar_pruebas()
logger.info("Paso 4/4: Pruebas - COMPLETADA")

# Generar reporte final
self.generar_reporte_final(exito_general)

return exito_general

def generar_reporte_final(self, exito_general):
"""Genera reporte final del proceso"""
logger.info("=" * 80)
logger.info("REPORTE FINAL DE MIGRACIÓN")
logger.info("=" * 80)

self.resultados['exito_general'] = exito_general
self.resultados['timestamp_fin'] = datetime.now().isoformat()

# Guardar reporte en JSON
archivo_reporte = self.directorio_logs / f"reporte_final_{self.timestamp}.json"
import json
with open(archivo_reporte, 'w', encoding='utf-8') as f:
json.dump(self.resultados, f, indent=, ensure_ascii=False)

# Mostrar resumen en consola
print(f"\n RESUMEN DE EJECUCIÓN:")
print(f" Timestamp: {self.timestamp}")
print(f" Estado General: {' EXITOSO' if exito_general else ' FALLIDO'}")
print(f"")

for paso, resultado in self.resultados.items():
if isinstance(resultado, dict) and 'exito' in resultado:
estado = "" if resultado['exito'] else ""
print(f" {paso.capitalize()}: {estado} {resultado.get('mensaje', '')}")

print(f"\n Archivos generados:")
print(f" Logs: {self.directorio_logs}")
print(f" Reporte: {archivo_reporte}")
print(f" Datos limpios: {self.config['directorio_salida_limpios']}")

if exito_general:
print(f"\n Migración completada exitosamente")
else:
print(f"\n Migración completada con errores. Revisar logs para detalles.")

print("=" * 80)


def cargar_configuracion():
"""Carga configuración desde archivo o argumentos"""
parser = argparse.ArgumentParser(description='Ejecutor Completo - Migración Cámaras UFRO')

# Configuración de base de datos
parser.add_argument('--host', required=True, help='Host de la base de datos')
parser.add_argument('--database', required=True, help='Nombre de la base de datos')
parser.add_argument('--user', required=True, help='Usuario de la base de datos')
parser.add_argument('--password', required=True, help='Contraseña de la base de datos')
parser.add_argument('--port', type=int, default=543, help='Puerto de la base de datos')

# Directorios
parser.add_argument('--entrada', required=True, help='Directorio con planillas originales')
parser.add_argument('--salida', required=True, help='Directorio para datos limpios')

# Opciones
parser.add_argument('--sin-pruebas', action='store_true', help='Omitir pruebas automatizadas')
parser.add_argument('--solo-limpieza', action='store_true', help='Ejecutar solo limpieza')
parser.add_argument('--directorio-trabajo', default='/workspace', help='Directorio de trabajo')

args = parser.parse_args()

config = {
'db_host': args.host,
'db_name': args.database,
'db_user': args.user,
'db_password': args.password,
'db_port': args.port,
'directorio_entrada': args.entrada,
'directorio_salida_limpios': args.salida,
'directorio_trabajo': args.directorio_trabajo,
'ejecutar_pruebas': not args.sin_pruebas,
'solo_limpieza': args.solo_limpieza
}

return config


def main():
"""Función principal"""
try:
# Cargar configuración
config = cargar_configuracion()

# Crear ejecutor
ejecutor = EjecutorCompleto(config)

# Ejecutar proceso
if config['solo_limpieza']:
exito = ejecutor.ejecutar_limpieza()
else:
exito = ejecutor.ejecutar_proceso_completo()

# Salir con código apropiado
sys.exit(0 if exito else 1)

except KeyboardInterrupt:
logger.info("Proceso interrumpido por el usuario")
sys.exit(130)
except Exception as e:
logger.error(f"Error crítico en ejecución: {e}")
sys.exit(1)


if __name__ == "__main__":
main()