#/usr/bin/env python3
"""
Script de limpieza y normalización de datos - Sistema Cámaras UFRO
Limpia, normaliza y prepara datos desde planillas Excel para migración

Autor: Sistema de Limpieza UFRO
Fecha: 05-11-04
"""

import pandas as pd
import re
import logging
import sys
import json
from datetime import datetime, date
from pathlib import Path
import argparse
from collections import defaultdict

# Configuración de logging
logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(levelname)s - %(message)s',
handlers=[
logging.FileHandler('limpieza.log'),
logging.StreamHandler(sys.stdout)
]
)
logger = logging.getLogger(__name__)

class LimpiadorDatosUFRO:
"""Clase para limpieza y normalización de datos"""

def __init__(self):
"""Inicializa el limpiador de datos"""
self.stats_limpieza = {
'timestamp': datetime.now(),
'archivos_procesados': 0,
'registros_procesados': 0,
'registros_limpios': 0,
'registros_con_errores': 0,
'transformaciones': {}
}

# Diccionarios de normalización
self.normalizar_estados = {
'funcionando': 'Funcionando',
'funcionando correctamente': 'Funcionando',
'operativo': 'Operativo',
'activo': 'Activo',
'ok': 'Funcionando',
'error': 'Error',
'falla': 'Falla',
'fuera de servicio': 'Fuera de Servicio',
'mantenimiento': 'Mantenimiento',
'desconocido': 'Desconocido'
}

self.normalizar_tipos_camara = {
'domo': 'Domo',
'bullet': 'Bullet',
'ptz': 'PTZ',
'fisheye': 'Fisheye',
'caja': 'Cámara Caja'
}

self.normalizar_prioridades = {
'alta': 'Alta',
'baja': 'Baja',
'media': 'Media',
'critica': 'Crítica',
'urgente': 'Urgente'
}

def leer_planilla_excel(self, archivo_path, hoja=None):
"""
Lee datos de una planilla Excel con manejo de errores mejorado

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

# Remover filas completamente vacías
df = df.dropna(how='all')

logger.info(f"Archivo leído: {archivo_path.name} - {len(df)} registros, {len(df.columns)} columnas")
return df

except Exception as e:
logger.error(f"Error leyendo {archivo_path}: {e}")
return pd.DataFrame()

def limpiar_texto(self, texto):
"""Limpia y normaliza texto"""
if pd.isna(texto) or str(texto).strip() in ['nan', '', 'None']:
return None

texto = str(texto).strip()

# Remover caracteres especiales innecesarios
texto = re.sub(r'[^\w\s\-\.\,\(\)]', ' ', texto)
texto = re.sub(r'\s+', ' ', texto) # Múltiples espacios a uno solo
texto = texto.strip()

return texto if texto else None

def limpiar_ip(self, ip_str):
"""Limpia y valida direcciones IP"""
if pd.isna(ip_str) or str(ip_str).strip() in ['nan', '', 'None']:
return None

ip_str = str(ip_str).strip()

# Patrones comunes de IP
patrones_ip = [
r'^(\d{1,3}\.){3}\d{1,3}$', # 19.168.1.1
r'^(\d{1,3}\-\d{1,3}\-\d{1,3}\-\d{1,3})$', # 19-168-1-1
]

for patron in patrones_ip:
if re.match(patron, ip_str):
# Normalizar puntos
ip_normalizada = ip_str.replace('-', '.')

# Validar rangos
partes = ip_normalizada.split('.')
if len(partes) == 4 and all(0 <= int(p) <= 55 for p in partes):
return ip_normalizada

# Si no es una IP válida, registrar pero retornar None
logger.warning(f"IP inválida encontrada: {ip_str}")
return None

def parsear_fecha(self, fecha_str):
"""Parsea fecha desde diferentes formatos Excel"""
if pd.isna(fecha_str) or str(fecha_str).strip() in ['nan', '', 'None']:
return None

fecha_str = str(fecha_str).strip()

# Si es un número (fecha de Excel), convertir
try:
if fecha_str.replace('.', '').isdigit():
# Fecha de Excel (días desde 1900-01-01)
fecha_excel = pd.to_datetime('1900-01-01') + pd.Timedelta(days=float(fecha_str) - )
return fecha_excel.date()
except:
pass

# Patrones de fecha comunes
patrones_fecha = [
'%d/%m/%Y', # 15/03/04
'%Y-%m-%d', # 04-03-15
'%d-%m-%Y', # 15-03-04
'%m/%d/%Y', # 03/15/04
'%d/%m/%y', # 15/03/4
'%Y/%m/%d', # 04/03/15
'%d.%m.%Y', # 15.03.04
]

for patron in patrones_fecha:
try:
return datetime.strptime(fecha_str, patron).date()
except ValueError:
continue

# Si no se pudo parsear, intentar pandas
try:
fecha_pd = pd.to_datetime(fecha_str)
return fecha_pd.date()
except:
pass

logger.warning(f"No se pudo parsear fecha: {fecha_str}")
return None

def normalizar_valor(self, valor, diccionario_normalizacion):
"""Normaliza un valor usando un diccionario de mapeo"""
if valor is None:
return valor

valor_str = str(valor).strip().lower()
return diccionario_normalizacion.get(valor_str, valor)

def limpiar_camaras(self, df):
"""Limpia y normaliza datos de cámaras"""
logger.info("Limpiando datos de cámaras...")

if df.empty:
return df

df_limpio = df.copy()

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

# Renombrar columnas existentes
for col_viejo, col_nuevo in columnas_mapeo.items():
if col_viejo in df_limpio.columns:
df_limpio[col_nuevo] = df_limpio[col_viejo]

# Limpiar campos de texto
for col in ['nombre_camara', 'campus_edificio', 'nvr_asociado', 'tipo_camara',
'estado_funcionamiento', 'estado_conexion', 'horario_grabacion',
'almacenamiento', 'observaciones']:
if col in df_limpio.columns:
df_limpio[col] = df_limpio[col].apply(self.limpiar_texto)

# Limpiar IPs
if 'ip_camara' in df_limpio.columns:
df_limpio['ip_camara'] = df_limpio['ip_camara'].apply(self.limpiar_ip)

# Normalizar estados
if 'estado_funcionamiento' in df_limpio.columns:
df_limpio['estado_funcionamiento'] = df_limpio['estado_funcionamiento'].apply(
lambda x: self.normalizar_valor(x, self.normalizar_estados)
)

# Normalizar tipos de cámara
if 'tipo_camara' in df_limpio.columns:
df_limpio['tipo_camara'] = df_limpio['tipo_camara'].apply(
lambda x: self.normalizar_valor(x, self.normalizar_tipos_camara)
)

# Generar ID único si no existe
if 'id_camara' not in df_limpio.columns:
df_limpio['id_camara'] = range(1, len(df_limpio) + 1)

# Remover registros sin nombre de cámara
df_limpio = df_limpio.dropna(subset=['nombre_camara'])

self.stats_limpieza['transformaciones']['camaras'] = {
'registros_originales': len(df),
'registros_limpios': len(df_limpio),
'registros_sin_nombre': len(df) - len(df_limpio)
}

logger.info(f"Cámaras limpiadas: {len(df_limpio)} registros válidos")
return df_limpio

def limpiar_fallas(self, df):
"""Limpia y normaliza datos de fallas"""
logger.info("Limpiando datos de fallas...")

if df.empty:
return df

df_limpio = df.copy()

# Mapeo de columnas
columnas_mapeo = {
'ID Falla': 'id_falla',
'Fecha de Reporte': 'fecha_reporte',
'Tipo de Falla': 'tipo_falla',
'Cámara Afectada': 'camara_afectada',
'Ubicación': 'ubicacion',
'Descripción': 'descripcion',
'Impacto en Visibilidad': 'impacto_visibilidad',
'Estado': 'estado',
'Prioridad': 'prioridad',
'Técnico Asignado': 'tecnico_asignado',
'Observaciones': 'observaciones'
}

# Renombrar columnas
for col_viejo, col_nuevo in columnas_mapeo.items():
if col_viejo in df_limpio.columns:
df_limpio[col_nuevo] = df_limpio[col_viejo]

# Limpiar campos de texto
for col in ['id_falla', 'tipo_falla', 'camara_afectada', 'ubicacion',
'descripcion', 'impacto_visibilidad', 'estado', 'prioridad',
'tecnico_asignado', 'observaciones']:
if col in df_limpio.columns:
df_limpio[col] = df_limpio[col].apply(self.limpiar_texto)

# Parsear fechas
if 'fecha_reporte' in df_limpio.columns:
df_limpio['fecha_reporte'] = df_limpio['fecha_reporte'].apply(self.parsear_fecha)

# Normalizar prioridades
if 'prioridad' in df_limpio.columns:
df_limpio['prioridad'] = df_limpio['prioridad'].apply(
lambda x: self.normalizar_valor(x, self.normalizar_prioridades)
)

# Normalizar estados
if 'estado' in df_limpio.columns:
df_limpio['estado'] = df_limpio['estado'].apply(
lambda x: self.normalizar_valor(x, self.normalizar_estados)
)

# Remover registros sin ID de falla
df_limpio = df_limpio.dropna(subset=['id_falla'])

self.stats_limpieza['transformaciones']['fallas'] = {
'registros_originales': len(df),
'registros_limpios': len(df_limpio),
'registros_sin_id': len(df) - len(df_limpio)
}

logger.info(f"Fallas limpiadas: {len(df_limpio)} registros válidos")
return df_limpio

def limpiar_nvr(self, df):
"""Limpia y normaliza datos de NVR"""
logger.info("Limpiando datos de NVR...")

if df.empty:
return df

df_limpio = df.copy()

# Mapeo de columnas
columnas_mapeo = {
'ID NVR': 'id_nvr',
'Nombre NVR': 'nombre_nvr',
'IP': 'ip_nvr',
'IP NVR': 'ip_nvr',
'Campus': 'campus',
'Campus/Edificio': 'campus_edificio',
'Modelo': 'modelo',
'Marca': 'marca',
'Fabricante': 'marca',
'Número de Canales': 'canales_total',
'Capacidad Canales': 'canales_total',
'Canales Usados': 'canales_usados',
'Estado': 'estado',
'Estado NVR': 'estado',
'Ubicación': 'ubicacion',
'Observaciones': 'observaciones'
}

# Renombrar columnas
for col_viejo, col_nuevo in columnas_mapeo.items():
if col_viejo in df_limpio.columns:
df_limpio[col_nuevo] = df_limpio[col_viejo]

# Limpiar campos de texto
for col in ['id_nvr', 'nombre_nvr', 'campus', 'campus_edificio', 'modelo',
'marca', 'estado', 'ubicacion', 'observaciones']:
if col in df_limpio.columns:
df_limpio[col] = df_limpio[col].apply(self.limpiar_texto)

# Limpiar IPs
if 'ip_nvr' in df_limpio.columns:
df_limpio['ip_nvr'] = df_limpio['ip_nvr'].apply(self.limpiar_ip)

# Limpiar campos numéricos
for col in ['canales_total', 'canales_usados']:
if col in df_limpio.columns:
df_limpio[col] = pd.to_numeric(df_limpio[col], errors='coerce')

# Normalizar estados
if 'estado' in df_limpio.columns:
df_limpio['estado'] = df_limpio['estado'].apply(
lambda x: self.normalizar_valor(x, self.normalizar_estados)
)

# Remover registros sin ID
df_limpio = df_limpio.dropna(subset=['id_nvr'])

self.stats_limpieza['transformaciones']['nvr'] = {
'registros_originales': len(df),
'registros_limpios': len(df_limpio)
}

logger.info(f"NVR limpiados: {len(df_limpio)} registros válidos")
return df_limpio

def limpiar_ubicaciones(self, df):
"""Limpia y normaliza datos de ubicaciones"""
logger.info("Limpiando datos de ubicaciones...")

if df.empty:
return df

df_limpio = df.copy()

# Limpiar campos de texto
for col in ['ID Ubicación', 'Campus', 'Edificio', 'Piso/Nivel', 'Zona', 'Observaciones']:
if col in df_limpio.columns:
df_limpio[col] = df_limpio[col].apply(self.limpiar_texto)

# Renombrar columnas
columnas_mapeo = {
'ID Ubicación': 'id_ubicacion',
'Campus': 'campus',
'Edificio': 'edificio',
'Piso/Nivel': 'piso_nivel',
'Zona': 'zona',
'Gabinetes en Ubicación': 'gabinetes_ubicacion',
'Cantidad de Cámaras': 'cantidad_camaras',
'Observaciones': 'observaciones'
}

for col_viejo, col_nuevo in columnas_mapeo.items():
if col_viejo in df_limpio.columns:
df_limpio[col_nuevo] = df_limpio[col_viejo]

# Limpiar cantidad de cámaras
if 'cantidad_camaras' in df_limpio.columns:
df_limpio['cantidad_camaras'] = pd.to_numeric(df_limpio['cantidad_camaras'], errors='coerce')

# Remover registros sin ID
df_limpio = df_limpio.dropna(subset=['id_ubicacion'])

self.stats_limpieza['transformaciones']['ubicaciones'] = {
'registros_originales': len(df),
'registros_limpios': len(df_limpio)
}

logger.info(f"Ubicaciones limpiadas: {len(df_limpio)} registros válidos")
return df_limpio

def generar_datos_normalizados(self, directorio_entrada, directorio_salida):
"""
Genera datos normalizados desde planillas Excel

Args:
directorio_entrada (str): Directorio con planillas originales
directorio_salida (str): Directorio donde guardar datos normalizados

Returns:
bool: True si el proceso fue exitoso
"""
logger.info("=== INICIANDO LIMPIEZA Y NORMALIZACIÓN ===")

try:
# Crear directorio de salida
Path(directorio_salida).mkdir(parents=True, exist_ok=True)

# Definir archivos y funciones de limpieza
archivos_limpieza = {
'Listadecámaras_modificada.xlsx': self.limpiar_camaras,
'NVR_DVR.xlsx': self.limpiar_nvr,
'Switches.xlsx': self.limpiar_nvr, # Reutilizar limpieza similar
'Ubicaciones.xlsx': self.limpiar_ubicaciones,
'Fallas_Actualizada.xlsx': self.limpiar_fallas,
'Ejemplos_Fallas_Reales_corregido_051019_00501.xlsx': self.limpiar_fallas
}

datos_normalizados = {}

# Procesar cada archivo
for archivo, funcion_limpieza in archivos_limpieza.items():
archivo_path = Path(directorio_entrada) / archivo

if archivo_path.exists():
logger.info(f"Procesando: {archivo}")

# Leer archivo
df = self.leer_planilla_excel(archivo_path)

if not df.empty:
# Limpiar datos
df_limpio = funcion_limpieza(df)

if not df_limpio.empty:
# Guardar datos normalizados
archivo_salida = Path(directorio_salida) / f"normalizado_{archivo}"
df_limpio.to_excel(archivo_salida, index=False)

# Guardar en JSON también
json_salida = Path(directorio_salida) / f"normalizado_{archivo.replace('.xlsx', '.json')}"
df_limpio.to_json(json_salida, orient='records', date_format='iso', indent=)

datos_normalizados[archivo] = {
'registros_originales': len(df),
'registros_limpios': len(df_limpio),
'archivo_excel': str(archivo_salida),
'archivo_json': str(json_salida)
}

self.stats_limpieza['archivos_procesados'] += 1
self.stats_limpieza['registros_procesados'] += len(df)
self.stats_limpieza['registros_limpios'] += len(df_limpio)

logger.info(f" {archivo}: {len(df)} → {len(df_limpio)} registros")
else:
logger.warning(f"No se pudieron limpiar datos de {archivo}")
else:
logger.warning(f"Archivo vacío: {archivo}")
else:
logger.warning(f"Archivo no encontrado: {archivo}")

# Generar reporte de limpieza
self._generar_reporte_limpieza(directorio_salida)

logger.info("=== LIMPIEZA COMPLETADA ===")
logger.info(f"Archivos procesados: {self.stats_limpieza['archivos_procesados']}")
logger.info(f"Registros procesados: {self.stats_limpieza['registros_procesados']}")
logger.info(f"Registros limpios: {self.stats_limpieza['registros_limpios']}")

return True

except Exception as e:
logger.error(f"Error en limpieza: {e}")
return False

def _generar_reporte_limpieza(self, directorio_salida):
"""Genera reporte de limpieza en JSON"""
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
archivo_reporte = Path(directorio_salida) / f"reporte_limpieza_{timestamp}.json"

self.stats_limpieza['timestamp'] = self.stats_limpieza['timestamp'].isoformat()

with open(archivo_reporte, 'w', encoding='utf-8') as f:
json.dump(self.stats_limpieza, f, indent=, ensure_ascii=False, default=str)

logger.info(f"Reporte de limpieza guardado: {archivo_reporte}")

def validar_datos_limpios(self, directorio_datos_limpios):
"""Valida la calidad de los datos limpiados"""
logger.info("Validando datos limpiados...")

archivos_json = list(Path(directorio_datos_limpios).glob("*.json"))

for archivo_json in archivos_json:
try:
df = pd.read_json(archivo_json)

# Validaciones básicas
validaciones = {
'total_registros': len(df),
'columnas_vacias': df.columns[df.isnull().all()].tolist(),
'registros_completos': len(df.dropna()),
'porcentaje_completitud': (len(df.dropna()) / len(df) * 100) if len(df) > 0 else 0
}

# Validaciones específicas por tipo
if 'nombre_camara' in df.columns:
validaciones['camaras_sin_nombre'] = df['nombre_camara'].isnull().sum()

if 'ip_camara' in df.columns:
validaciones['ips_invalidas'] = df['ip_camara'].apply(
lambda x: not self._validar_ip_simple(x) if x else True
).sum()

logger.info(f" Validación {archivo_json.name}: {validaciones['porcentaje_completitud']:.1f}% completo")

except Exception as e:
logger.error(f"Error validando {archivo_json}: {e}")

def _validar_ip_simple(self, ip_str):
"""Validación simple de IP"""
if not ip_str:
return False

partes = str(ip_str).split('.')
return len(partes) == 4 and all(p.isdigit() and 0 <= int(p) <= 55 for p in partes)


def main():
"""Función principal"""
parser = argparse.ArgumentParser(description='Limpiador de Datos Sistema Cámaras UFRO')
parser.add_argument('--entrada', required=True, help='Directorio con planillas originales')
parser.add_argument('--salida', required=True, help='Directorio para datos normalizados')
parser.add_argument('--validar', action='store_true', help='Validar datos después de limpieza')

args = parser.parse_args()

# Crear instancia del limpiador
limpiador = LimpiadorDatosUFRO()

# Ejecutar limpieza
if limpiador.generar_datos_normalizados(args.entrada, args.salida):
logger.info("Limpieza completada exitosamente")

if args.validar:
limpiador.validar_datos_limpios(args.salida)
else:
logger.error("Error en el proceso de limpieza")
sys.exit(1)


if __name__ == "__main__":
main()