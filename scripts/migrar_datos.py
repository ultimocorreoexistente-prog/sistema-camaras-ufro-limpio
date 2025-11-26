#/usr/bin/env python3
"""
Script principal de migración de datos del Sistema de Cámaras UFRO
Migración de planillas Excel a base de datos PostgreSQL

Autor: Sistema de Migración UFRO
Fecha: 05-11-04
"""

import pandas as pd
import psycopg
from psycopg import extras
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
import argparse

# Configuración de logging
logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(levelname)s - %(message)s',
handlers=[
logging.FileHandler('migracion.log'),
logging.StreamHandler(sys.stdout)
]
)
logger = logging.getLogger(__name__)

class MigradorDatosUFRO:
"""Clase principal para la migración de datos del sistema de cámaras"""

def __init__(self, db_config):
"""
Inicializa el migrador con configuración de base de datos

Args:
db_config (dict): Configuración de conexión a la base de datos
"""
self.db_config = db_config
self.conexion = None
self.cursor = None
self.backup_data = {}
self.stats = {
'total_registros': 0,
'registros_migrados': 0,
'registros_error': 0,
'tiempo_inicio': None,
'tiempo_fin': None
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

def crear_backup(self, tabla):
"""
Crea backup de datos existentes de una tabla

Args:
tabla (str): Nombre de la tabla a respaldar
"""
try:
query = f"SELECT * FROM {tabla}"
self.cursor.execute(query)
datos = self.cursor.fetchall()
columnas = [desc[0] for desc in self.cursor.description]

self.backup_data[tabla] = {
'columnas': columnas,
'datos': datos,
'timestamp': datetime.now()
}
logger.info(f"Backup creado para tabla {tabla}: {len(datos)} registros")
except Exception as e:
logger.error(f"Error creando backup de {tabla}: {e}")

def restaurar_backup(self, tabla):
"""
Restaura datos desde el backup

Args:
tabla (str): Nombre de la tabla a restaurar
"""
if tabla not in self.backup_data:
logger.warning(f"No hay backup disponible para {tabla}")
return

try:
backup = self.backup_data[tabla]

# Limpiar tabla actual
self.cursor.execute(f"DELETE FROM {tabla}")

# Restaurar datos
query = f"""
INSERT INTO {tabla} ({', '.join(backup['columnas'])})
VALUES %s
"""
extras.execute_batch(self.cursor, query, backup['datos'])

logger.info(f"Datos restaurados para {tabla}: {len(backup['datos'])} registros")
except Exception as e:
logger.error(f"Error restaurando backup de {tabla}: {e}")

def leer_planilla_excel(self, archivo_path, hoja=None):
"""
Lee datos de una planilla Excel

Args:
archivo_path (str): Ruta al archivo Excel
hoja (str): Nombre de la hoja (opcional)

Returns:
pd.DataFrame: DataFrame con los datos leídos
"""
try:
if hoja:
df = pd.read_excel(archivo_path, sheet_name=hoja)
else:
df = pd.read_excel(archivo_path)

# Limpiar nombres de columnas
df.columns = df.columns.str.strip()

logger.info(f"Archivo {archivo_path} leído: {len(df)} registros, {len(df.columns)} columnas")
return df
except Exception as e:
logger.error(f"Error leyendo {archivo_path}: {e}")
return pd.DataFrame()

def limpiar_datos_camara(self, df):
"""Limpia y normaliza datos de la tabla cámaras"""
logger.info("Limpiando datos de cámaras...")

# Mapeo de columnas a nuevas
columnas_mapeo = {
'Nombre de Cámara': 'nombre_camara',
'IP de Cámara': 'ip_camara',
'Campus/Edificio': 'campus_edificio',
'NVR Asociado (Cámara)': 'nvr_asociado',
'Tipo de Cámara': 'tipo_camara',
'Estado de Funcionamiento': 'estado_funcionamiento',
'Estado de Conexión': 'estado_conexion',
'Horario de Grabación': 'horario_grabacion',
'Almacenamiento': 'almacenamiento',
'Observaciones': 'observaciones'
}

# Renombrar columnas
df_limpio = df.rename(columns=columnas_mapeo)

# Limpiar campos de texto
for col in df_limpio.select_dtypes(include=['object']).columns:
df_limpio[col] = df_limpio[col].astype(str).str.strip()
df_limpio[col] = df_limpio[col].replace('nan', None)

# Validar IPs
df_limpio['ip_camara'] = df_limpio['ip_camara'].apply(
lambda x: x if x and self._validar_ip(x) else None
)

# Normalizar estado
df_limpio['estado_funcionamiento'] = df_limpio['estado_funcionamiento'].fillna('Desconocido')

logger.info(f"Datos de cámaras limpiados: {len(df_limpio)} registros")
return df_limpio

def migrar_camaras(self, archivo_planilla):
"""Migra datos de cámaras desde Excel a PostgreSQL"""
try:
df = self.leer_planilla_excel(archivo_planilla)
if df.empty:
return False

df_limpio = self.limpiar_datos_camara(df)

# Crear backup si existen datos
self.cursor.execute("SELECT COUNT(*) FROM camaras")
if self.cursor.fetchone()[0] > 0:
self.crear_backup("camaras")
self.cursor.execute("DELETE FROM camaras")

# Insertar datos
for _, row in df_limpio.iterrows():
try:
query = """
INSERT INTO camaras (
nombre_camara, ip_camara, campus_edificio, nvr_asociado,
tipo_camara, estado_funcionamiento, estado_conexion,
horario_grabacion, almacenamiento, observaciones
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
valores = (
row.get('nombre_camara'),
row.get('ip_camara'),
row.get('campus_edificio'),
row.get('nvr_asociado'),
row.get('tipo_camara'),
row.get('estado_funcionamiento'),
row.get('estado_conexion'),
row.get('horario_grabacion'),
row.get('almacenamiento'),
row.get('observaciones')
)

self.cursor.execute(query, valores)
self.stats['registros_migrados'] += 1

except Exception as e:
logger.error(f"Error migrando cámara {row.get('nombre_camara', 'N/A')}: {e}")
self.stats['registros_error'] += 1

self.conexion.commit()
logger.info(f"Migración de cámaras completada: {self.stats['registros_migrados']} registros")
return True

except Exception as e:
logger.error(f"Error en migración de cámaras: {e}")
if self.conexion:
self.conexion.rollback()
return False

def migrar_nvr(self, archivo_planilla):
"""Migra datos de NVR/DVR"""
try:
df = self.leer_planilla_excel(archivo_planilla)
if df.empty:
return False

# Crear backup si existen datos
self.cursor.execute("SELECT COUNT(*) FROM nvr_dvr")
if self.cursor.fetchone()[0] > 0:
self.crear_backup("nvr_dvr")
self.cursor.execute("DELETE FROM nvr_dvr")

for _, row in df.iterrows():
try:
query = """
INSERT INTO nvr_dvr (
id_nvr, nombre_nvr, ip_nvr, campus_edificio,
modelo, marca, canales_total, canales_usados,
estado_nvr, ubicacion, observaciones
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
valores = (
row.get('ID NVR'),
row.get('Nombre NVR', row.get('ID NVR')),
row.get('IP', row.get('IP NVR')),
row.get('Campus', row.get('Campus/Edificio')),
row.get('Modelo'),
row.get('Marca', row.get('Fabricante')),
row.get('Número de Canales', row.get('Capacidad Canales')),
row.get('Canales Usados'),
row.get('Estado', row.get('Estado NVR')),
row.get('Ubicación'),
row.get('Observaciones')
)

self.cursor.execute(query, valores)
self.stats['registros_migrados'] += 1

except Exception as e:
logger.error(f"Error migrando NVR {row.get('ID NVR', 'N/A')}: {e}")
self.stats['registros_error'] += 1

self.conexion.commit()
return True

except Exception as e:
logger.error(f"Error en migración de NVR: {e}")
if self.conexion:
self.conexion.rollback()
return False

def migrar_switches(self, archivo_planilla):
"""Migra datos de switches"""
try:
df = self.leer_planilla_excel(archivo_planilla)
if df.empty:
return False

self.cursor.execute("SELECT COUNT(*) FROM switches")
if self.cursor.fetchone()[0] > 0:
self.crear_backup("switches")
self.cursor.execute("DELETE FROM switches")

for _, row in df.iterrows():
try:
query = """
INSERT INTO switches (
id_switch, nombre_switch, ip_switch, campus_edificio,
modelo, marca, serie, puertos_total, puertos_usados,
soporta_poe, estado, ubicacion, observaciones
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
valores = (
row.get('ID Switch'),
row.get('Nombre/Modelo'),
row.get('IP Switch'),
row.get('Campus', row.get('Campus/Edificio')),
row.get('Modelo'),
row.get('Marca'),
row.get('Número de Serie'),
row.get('Número Total de Puertos'),
row.get('Puertos Usados'),
row.get('Soporta PoE'),
row.get('Estado'),
row.get('Ubicación'),
row.get('Observaciones')
)

self.cursor.execute(query, valores)
self.stats['registros_migrados'] += 1

except Exception as e:
logger.error(f"Error migrando switch {row.get('ID Switch', 'N/A')}: {e}")
self.stats['registros_error'] += 1

self.conexion.commit()
return True

except Exception as e:
logger.error(f"Error en migración de switches: {e}")
if self.conexion:
self.conexion.rollback()
return False

def migrar_fallas(self, archivo_planilla):
"""Migra datos de fallas"""
try:
df = self.leer_planilla_excel(archivo_planilla)
if df.empty:
return False

self.cursor.execute("SELECT COUNT(*) FROM fallas")
if self.cursor.fetchone()[0] > 0:
self.crear_backup("fallas")
self.cursor.execute("DELETE FROM fallas")

for _, row in df.iterrows():
try:
query = """
INSERT INTO fallas (
id_falla, fecha_reporte, tipo_falla, camara_afectada,
ubicacion, descripcion, impacto_visibilidad,
estado, prioridad, tecnico_asignado, observaciones
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
valores = (
row.get('ID Falla'),
self._parsear_fecha(row.get('Fecha de Reporte')),
row.get('Tipo de Falla'),
row.get('Cámara Afectada'),
row.get('Ubicación'),
row.get('Descripción'),
row.get('Impacto en Visibilidad'),
row.get('Estado'),
row.get('Prioridad'),
row.get('Técnico Asignado'),
row.get('Observaciones')
)

self.cursor.execute(query, valores)
self.stats['registros_migrados'] += 1

except Exception as e:
logger.error(f"Error migrando falla {row.get('ID Falla', 'N/A')}: {e}")
self.stats['registros_error'] += 1

self.conexion.commit()
return True

except Exception as e:
logger.error(f"Error en migración de fallas: {e}")
if self.conexion:
self.conexion.rollback()
return False

def migrar_ubicaciones(self, archivo_planilla):
"""Migra datos de ubicaciones"""
try:
df = self.leer_planilla_excel(archivo_planilla)
if df.empty:
return False

self.cursor.execute("SELECT COUNT(*) FROM ubicaciones")
if self.cursor.fetchone()[0] > 0:
self.crear_backup("ubicaciones")
self.cursor.execute("DELETE FROM ubicaciones")

for _, row in df.iterrows():
try:
query = """
INSERT INTO ubicaciones (
id_ubicacion, campus, edificio, piso_nivel,
zona, gabinetes_ubicacion, cantidad_camaras, observaciones
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""
valores = (
row.get('ID Ubicación'),
row.get('Campus'),
row.get('Edificio'),
row.get('Piso/Nivel'),
row.get('Zona'),
row.get('Gabinetes en Ubicación'),
row.get('Cantidad de Cámaras'),
row.get('Observaciones')
)

self.cursor.execute(query, valores)
self.stats['registros_migrados'] += 1

except Exception as e:
logger.error(f"Error migrando ubicación {row.get('ID Ubicación', 'N/A')}: {e}")
self.stats['registros_error'] += 1

self.conexion.commit()
return True

except Exception as e:
logger.error(f"Error en migración de ubicaciones: {e}")
if self.conexion:
self.conexion.rollback()
return False

def _validar_ip(self, ip_str):
"""Valida si una cadena es una IP válida"""
import re
pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
if not re.match(pattern, str(ip_str)):
return False
partes = ip_str.split('.')
return all(0 <= int(parte) <= 55 for parte in partes)

def _parsear_fecha(self, fecha_str):
"""Parsea fecha desde diferentes formatos"""
if pd.isna(fecha_str) or not fecha_str:
return None

formatos = [
'%d/%m/%Y',
'%Y-%m-%d',
'%d-%m-%Y',
'%m/%d/%Y'
]

for formato in formatos:
try:
return datetime.strptime(str(fecha_str).strip(), formato)
except ValueError:
continue

logger.warning(f"No se pudo parsear fecha: {fecha_str}")
return None

def ejecutar_migracion_completa(self, directorio_planillas):
"""
Ejecuta la migración completa de todas las planillas

Args:
directorio_planillas (str): Directorio con las planillas Excel

Returns:
bool: True si la migración fue exitosa
"""
self.stats['tiempo_inicio'] = datetime.now()
logger.info("=== INICIANDO MIGRACIÓN COMPLETA ===")

try:
# Conectar a la base de datos
if not self.conectar_bd():
return False

# Definir archivos y sus correspondientes funciones de migración
migraciones = {
'Listadecámaras_modificada.xlsx': self.migrar_camaras,
'NVR_DVR.xlsx': self.migrar_nvr,
'Switches.xlsx': self.migrar_switches,
'Fallas_Actualizada.xlsx': self.migrar_fallas,
'Ejemplos_Fallas_Reales_corregido_051019_00501.xlsx': self.migrar_fallas,
'Ubicaciones.xlsx': self.migrar_ubicaciones
}

for archivo, funcion_migracion in migraciones.items():
archivo_path = Path(directorio_planillas) / archivo
if archivo_path.exists():
logger.info(f"Migrando: {archivo}")
if funcion_migracion(archivo_path):
logger.info(f" Migración exitosa de {archivo}")
else:
logger.error(f" Error en migración de {archivo}")
else:
logger.warning(f"Archivo no encontrado: {archivo_path}")

self.stats['tiempo_fin'] = datetime.now()
duracion = self.stats['tiempo_fin'] - self.stats['tiempo_inicio']

logger.info("=== MIGRACIÓN COMPLETADA ===")
logger.info(f"Tiempo total: {duracion}")
logger.info(f"Registros migrados: {self.stats['registros_migrados']}")
logger.info(f"Registros con error: {self.stats['registros_error']}")

return True

except Exception as e:
logger.error(f"Error en migración completa: {e}")
return False

finally:
self.cerrar_conexion()

def ejecutar_rollback(self, tabla):
"""Ejecuta rollback de una tabla específica"""
try:
if self.conectar_bd():
logger.info(f"Ejecutando rollback para tabla: {tabla}")
self.restaurar_backup(tabla)
self.conexion.commit()
return True
except Exception as e:
logger.error(f"Error en rollback de {tabla}: {e}")
finally:
self.cerrar_conexion()
return False


def main():
"""Función principal"""
parser = argparse.ArgumentParser(description='Migrador de Datos Sistema Cámaras UFRO')
parser.add_argument('--host', required=True, help='Host de la base de datos')
parser.add_argument('--database', required=True, help='Nombre de la base de datos')
parser.add_argument('--user', required=True, help='Usuario de la base de datos')
parser.add_argument('--password', required=True, help='Contraseña de la base de datos')
parser.add_argument('--port', type=int, default=543, help='Puerto de la base de datos')
parser.add_argument('--planillas-dir', required=True, help='Directorio con planillas Excel')
parser.add_argument('--rollback', help='Tabla para hacer rollback')

args = parser.parse_args()

# Configuración de base de datos
db_config = {
'host': args.host,
'database': args.database,
'user': args.user,
'password': args.password,
'port': args.port
}

# Crear instancia del migrador
migrador = MigradorDatosUFRO(db_config)

if args.rollback:
# Ejecutar rollback
migrador.ejecutar_rollback(args.rollback)
else:
# Ejecutar migración completa
migrador.ejecutar_migracion_completa(args.planillas_dir)


if __name__ == "__main__":
main()