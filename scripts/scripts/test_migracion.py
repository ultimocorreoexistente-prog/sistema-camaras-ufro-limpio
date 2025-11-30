#/usr/bin/env python3
"""
Script de pruebas de migración - Sistema Cámaras UFRO
Ejecuta pruebas automatizadas de la migración de datos

Autor: Sistema de Pruebas UFRO
Fecha: 05-11-04
"""

import unittest
import pandas as pd
import psycopg
import logging
import sys
import json
from datetime import datetime
from pathlib import Path
import argparse
from unittest.mock import patch, MagicMock

# Importar clases principales
sys.path.append(str(Path(__file__).parent))
from migrar_datos import MigradorDatosUFRO
from limpiar_datos import LimpiadorDatosUFRO
from validar_datos import ValidadorDatosUFRO

# Configuración de logging
logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(levelname)s - %(message)s',
handlers=[
logging.FileHandler('pruebas.log'),
logging.StreamHandler(sys.stdout)
]
)
logger = logging.getLogger(__name__)

class TestMigracionDatos(unittest.TestCase):
"""Suite de pruebas para la migración de datos"""

@classmethod
def setUpClass(cls):
"""Configuración inicial para todas las pruebas"""
cls.config_test_db = {
'host': 'localhost',
'database': 'test_camaras_ufro',
'user': 'test_user',
'password': 'test_password',
'port': 543
}
cls.archivos_test = {
'camaras': '/tmp/test_camaras.xlsx',
'fallas': '/tmp/test_fallas.xlsx',
'nvr': '/tmp/test_nvr.xlsx'
}
cls._crear_datos_test()

@classmethod
def tearDownClass(cls):
"""Limpieza después de todas las pruebas"""
cls._limpiar_archivos_test()

@classmethod
def _crear_datos_test(cls):
"""Crea archivos Excel de prueba"""
# Datos de prueba para cámaras
datos_camaras = {
'Nombre de Cámara': ['CAM001', 'CAM00', 'CAM003'],
'IP de Cámara': ['19.168.1.100', '19.168.1.101', 'invalid_ip'],
'Campus/Edificio': ['Campus A', 'Campus B', 'Campus A'],
'Estado de Funcionamiento': ['Funcionando', 'Error', 'funcionando']
}
df_camaras = pd.DataFrame(datos_camaras)
df_camaras.to_excel(cls.archivos_test['camaras'], index=False)

# Datos de prueba para fallas
datos_fallas = {
'ID Falla': ['F001', 'F00', 'F003'],
'Fecha de Reporte': ['04-01-01', '04-01-0', 'invalid_date'],
'Tipo de Falla': ['Limpieza', 'Daño físico', 'Conectividad'],
'Cámara Afectada': ['CAM001', 'CAM00', 'CAM999'],
'Prioridad': ['alta', 'media', 'baja']
}
df_fallas = pd.DataFrame(datos_fallas)
df_fallas.to_excel(cls.archivos_test['fallas'], index=False)

# Datos de prueba para NVR
datos_nvr = {
'ID NVR': ['NVR001', 'NVR00', ''],
'Nombre NVR': ['NVR Principal', 'NVR Secundario', 'NVR Sin ID'],
'IP': ['19.168.1.00', '19.168.1.01', ''],
'Estado': ['Operativo', 'Funcionando', 'Error']
}
df_nvr = pd.DataFrame(datos_nvr)
df_nvr.to_excel(cls.archivos_test['nvr'], index=False)

@classmethod
def _limpiar_archivos_test(cls):
"""Limpia archivos de prueba"""
for archivo in cls.archivos_test.values():
if Path(archivo).exists():
Path(archivo).unlink()

def setUp(self):
"""Configuración antes de cada prueba"""
# Mock de conexión a base de datos
self.mock_db_connection = MagicMock()
self.migrador_test = MigradorDatosUFRO(self.config_test_db)

# Configurar mocks
with patch('psycopg.connect') as mock_connect:
mock_connect.return_value = self.mock_db_connection
self.mock_cursor = self.mock_db_connection.cursor.return_value
self.migrador_test.conectar_bd()

def test_limpiar_texto(self):
"""Prueba la limpieza de texto"""
limpiador = LimpiadorDatosUFRO()

# Casos de prueba
casos = [
(" texto con espacios ", "texto con espacios"),
("texto\ncon\nsaltos", "texto con saltos"),
("texto@#$%^&*()", "texto"),
(None, None),
("", None),
("nan", None)
]

for entrada, esperado in casos:
resultado = limpiador.limpiar_texto(entrada)
self.assertEqual(resultado, esperado, f"Error con entrada: {entrada}")

def test_limpiar_ip(self):
"""Prueba la limpieza de direcciones IP"""
limpiador = LimpiadorDatosUFRO()

# IPs válidas
ips_validas = [
"19.168.1.100",
"10.0.0.1",
"17.16.0.1",
"19-168-1-100" # Formato con guiones
]

for ip in ips_validas:
resultado = limpiador.limpiar_ip(ip)
self.assertIsNotNone(resultado, f"IP válida no reconocida: {ip}")

# IPs inválidas
ips_invalidas = [
"invalid_ip",
"56.56.56.56",
"19.168.1",
"",
None,
"texto"
]

for ip in ips_invalidas:
resultado = limpiador.limpiar_ip(ip)
self.assertIsNone(resultado, f"IP inválida aceptada: {ip}")

def test_parsear_fecha(self):
"""Prueba el parseo de fechas"""
limpiador = LimpiadorDatosUFRO()

# Fechas válidas
fechas_validas = [
("04-01-01", datetime(2004, 1, 1).date()),
("01/01/04", datetime(2004, 1, 1).date()),
("15-03-04", datetime(2004, 3, 15).date()),
("03/15/04", datetime(2004, 3, 15).date())
]

for fecha_str, esperado in fechas_validas:
resultado = limpiador.parsear_fecha(fecha_str)
self.assertEqual(resultado, esperado, f"Error parseando: {fecha_str}")

# Fechas inválidas
fechas_invalidas = [
"invalid_date",
"",
None,
"texto_fecha"
]

for fecha_str in fechas_invalidas:
resultado = limpiador.parsear_fecha(fecha_str)
self.assertIsNone(resultado, f"Fecha inválida aceptada: {fecha_str}")

def test_normalizar_valor(self):
"""Prueba la normalización de valores"""
limpiador = LimpiadorDatosUFRO()

diccionario_test = {
'alta': 'Alta',
'media': 'Media',
'baja': 'Baja',
'funcionando': 'Funcionando'
}

# Casos que deben mapearse
casos_mapeo = [
('alta', 'Alta'),
('MEDIA', 'Media'), # Debe preservar mayúsculas en entrada
('baja', 'Baja'),
('funcionando', 'Funcionando')
]

for entrada, esperado in casos_mapeo:
resultado = limpiador.normalizar_valor(entrada, diccionario_test)
self.assertEqual(resultado, esperado, f"Error normalizando: {entrada}")

# Casos que no deben mapearse
casos_sin_mapeo = [
('no_existe', 'no_existe'),
('', ''),
(None, None)
]

for entrada, esperado in casos_sin_mapeo:
resultado = limpiador.normalizar_valor(entrada, diccionario_test)
self.assertEqual(resultado, esperado, f"Error con valor no mapeado: {entrada}")

def test_limpiar_camaras(self):
"""Prueba la limpieza de datos de cámaras"""
logger.info("Probando limpieza de cámaras...")

# Leer archivo de prueba
df_test = pd.read_excel(self.archivos_test['camaras'])

# Ejecutar limpieza
limpiador = LimpiadorDatosUFRO()
df_limpio = limpiador.limpiar_camaras(df_test)

# Verificaciones
self.assertGreater(len(df_limpio), 0, "No se generaron datos limpios")

# Verificar que se creó la columna id_camara
self.assertIn('id_camara', df_limpio.columns, "Columna id_camara no creada")

# Verificar normalización de estados
estados_unicos = df_limpio['estado_funcionamiento'].dropna().unique()
logger.info(f"Estados únicos después de limpieza: {estados_unicos}")

def test_limpiar_fallas(self):
"""Prueba la limpieza de datos de fallas"""
logger.info("Probando limpieza de fallas...")

# Leer archivo de prueba
df_test = pd.read_excel(self.archivos_test['fallas'])

# Ejecutar limpieza
limpiador = LimpiadorDatosUFRO()
df_limpio = limpiador.limpiar_fallas(df_test)

# Verificaciones
self.assertGreater(len(df_limpio), 0, "No se generaron datos limpios")

# Verificar parseo de fechas
fechas_validas = df_limpio['fecha_reporte'].dropna()
self.assertGreater(len(fechas_validas), 0, "No se parsearon fechas")

# Verificar normalización de prioridades
prioridades_unicas = df_limpio['prioridad'].dropna().unique()
logger.info(f"Prioridades únicas después de limpieza: {prioridades_unicas}")

def test_validar_ip(self):
"""Prueba la validación de IP"""
# Usar el migrador para probar validación
migrador = MigradorDatosUFRO(self.config_test_db)

# IPs válidas
ips_validas = ['19.168.1.100', '10.0.0.1', '17.16.0.1']
for ip in ips_validas:
self.assertTrue(migrador._validar_ip(ip), f"IP válida no reconocida: {ip}")

# IPs inválidas
ips_invalidas = ['invalid_ip', '56.56.56.56', '19.168.1']
for ip in ips_invalidas:
self.assertFalse(migrador._validar_ip(ip), f"IP inválida aceptada: {ip}")

def test_estadisticas_limpieza(self):
"""Prueba el tracking de estadísticas de limpieza"""
limpiador = LimpiadorDatosUFRO()

# Ejecutar limpieza de un archivo
directorio_temp = Path('/tmp/test_limpieza')
directorio_temp.mkdir(exist_ok=True)

try:
# Usar archivo de prueba
datos_test = {
'Nombre de Cámara': ['CAM001', '', 'CAM003'],
'IP de Cámara': ['19.168.1.100', 'invalid_ip', '19.168.1.10']
}
df_test = pd.DataFrame(datos_test)
archivo_test = directorio_temp / 'test_camaras.xlsx'
df_test.to_excel(archivo_test, index=False)

# Ejecutar limpieza
limpiador.generar_datos_normalizados(str(directorio_temp), str(directorio_temp))

# Verificar que se generaron estadísticas
self.assertGreater(limpiador.stats_limpieza['archivos_procesados'], 0)
self.assertGreater(limpiador.stats_limpieza['registros_procesados'], 0)

finally:
# Limpiar
if archivo_test.exists():
archivo_test.unlink()
if directorio_temp.exists():
directorio_temp.rmdir()

def test_validaciones_bd_mock(self):
"""Prueba validaciones con base de datos mock"""
validador = ValidadorDatosUFRO(self.config_test_db)

# Mock de la conexión
with patch('psycopg.connect') as mock_connect:
mock_connection = MagicMock()
mock_cursor = MagicMock()
mock_connect.return_value = mock_connection
mock_cursor.return_value.fetchall.return_value = [
('CAM001', '19.168.1.100'),
('CAM00', '19.168.1.101')
]
mock_cursor.return_value.fetchone.return_value = (0,)
mock_connection.cursor.return_value = mock_cursor

# Ejecutar validación de IPs
validador.conectar_bd()
validador.validar_ips_unicas()

# Verificar que se ejecutaron las consultas
self.assertTrue(mock_cursor.execute.called)

def test_manejo_errores_conexion(self):
"""Prueba el manejo de errores de conexión"""
migrador = MigradorDatosUFRO(self.config_test_db)

# Mock de conexión fallida
with patch('psycopg.connect', side_effect=Exception("Error de conexión")):
resultado = migrador.conectar_bd()
self.assertFalse(resultado, "Debió fallar la conexión")

def test_consistencia_datos(self):
"""Prueba la consistencia entre datos limpios"""
logger.info("Probando consistencia de datos...")

limpiador = LimpiadorDatosUFRO()

# Crear datos inconsistentes
datos_inconsistentes = {
'Nombre de Cámara': ['CAM001', 'CAM001', 'CAM003'], # Duplicado
'IP de Cámara': ['19.168.1.100', '19.168.1.100', '19.168.1.10'], # IP duplicada
'Estado': ['Funcionando', 'Error', 'funcionando']
}
df_inconsistente = pd.DataFrame(datos_inconsistentes)

# Limpiar
df_limpio = limpiador.limpiar_camaras(df_inconsistente)

# Verificar que la limpieza maneja duplicados
nombres_unicos = df_limpio['nombre_camara'].unique()
logger.info(f"Cámaras únicas después de limpieza: {len(nombres_unicos)}")


class TestIntegracionCompleta(unittest.TestCase):
"""Pruebas de integración completa del proceso de migración"""

def setUp(self):
"""Configuración de prueba de integración"""
self.directorio_test = Path('/tmp/test_integracion')
self.directorio_test.mkdir(exist_ok=True)

self.config_test_db = {
'host': 'localhost',
'database': 'test_camaras_ufro',
'user': 'test_user',
'password': 'test_password',
'port': 543
}

self._crear_datos_completos_test()

def tearDown(self):
"""Limpieza después de pruebas"""
self._limpiar_directorio_test()

def _crear_datos_completos_test(self):
"""Crea un conjunto completo de datos de prueba"""

# Crear datos de cámaras
datos_camaras = {
'Nombre de Cámara': [f'CAM{i:03d}' for i in range(1, 1)],
'IP de Cámara': [f'19.168.1.{100+i}' for i in range(0)],
'Campus/Edificio': ['Campus A'] * 10 + ['Campus B'] * 10,
'Estado de Funcionamiento': ['Funcionando'] * 15 + ['Error'] * 3 + ['fuera de servicio'] * ,
'Tipo de Cámara': ['domo'] * 10 + ['bullet'] * 8 + ['ptz'] *
}

df_camaras = pd.DataFrame(datos_camaras)
archivo_camaras = self.directorio_test / 'camaras_test.xlsx'
df_camaras.to_excel(archivo_camaras, index=False)

# Crear datos de fallas relacionados
datos_fallas = {
'ID Falla': [f'F{i:03d}' for i in range(1, 11)],
'Fecha de Reporte': ['04-01-01'] * 10,
'Tipo de Falla': ['Limpieza'] * 4 + ['Daño físico'] * 3 + ['Conectividad'] * 3,
'Cámara Afectada': [f'CAM{i:03d}' for i in range(1, 11)],
'Prioridad': ['alta'] * + ['media'] * 5 + ['baja'] * 3,
'Estado': ['abierta'] * 6 + ['en proceso'] * 3 + ['cerrada'] * 1
}

df_fallas = pd.DataFrame(datos_fallas)
archivo_fallas = self.directorio_test / 'fallas_test.xlsx'
df_fallas.to_excel(archivo_fallas, index=False)

def _limpiar_directorio_test(self):
"""Limpia el directorio de prueba"""
if self.directorio_test.exists():
for archivo in self.directorio_test.iterdir():
archivo.unlink()
self.directorio_test.rmdir()

def test_pipeline_completo_limpieza(self):
"""Prueba el pipeline completo de limpieza"""
logger.info("Probando pipeline completo de limpieza...")

# Ejecutar limpieza
limpiador = LimpiadorDatosUFRO()
directorio_limpio = self.directorio_test / 'limpio'
directorio_limpio.mkdir(exist_ok=True)

resultado = limpiador.generar_datos_normalizados(
str(self.directorio_test),
str(directorio_limpio)
)

self.assertTrue(resultado, "Pipeline de limpieza falló")

# Verificar archivos generados
archivos_generados = list(directorio_limpio.glob('*.json'))
self.assertGreater(len(archivos_generados), 0, "No se generaron archivos JSON")

# Verificar contenido de archivos
for archivo in archivos_generados:
with open(archivo) as f:
datos = json.load(f)
self.assertGreater(len(datos), 0, f"Archivo vacío: {archivo}")

def test_integridad_post_limpieza(self):
"""Prueba la integridad de datos después de limpieza"""
logger.info("Probando integridad post-limpieza...")

# Ejecutar limpieza
limpiador = LimpiadorDatosUFRO()
directorio_limpio = self.directorio_test / 'limpio'
directorio_limpio.mkdir(exist_ok=True)

limpiador.generar_datos_normalizados(
str(self.directorio_test),
str(directorio_limpio)
)

# Validar datos limpiados
limpiador.validar_datos_limpios(str(directorio_limpio))

# Verificar archivos de reporte
reportes = list(directorio_limpio.glob('reporte_limpieza_*.json'))
self.assertGreater(len(reportes), 0, "No se generó reporte de limpieza")

def test_credenciales_fallidas(self):
"""Prueba el manejo de credenciales fallidas"""
config_falso = {
'host': 'localhost_inexistente',
'database': 'db_inexistente',
'user': 'usuario_falso',
'password': 'password_falso'
}

migrador = MigradorDatosUFRO(config_falso)

# Mock de conexión fallida para probar manejo de errores
with patch('psycopg.connect', side_effect=psycopg.Error("Credenciales inválidas")):
resultado = migrador.conectar_bd()
self.assertFalse(resultado, "Debió fallar con credenciales incorrectas")


def ejecutar_pruebas_automaticas():
"""Ejecuta todas las pruebas automáticamente"""
logger.info("=== INICIANDO PRUEBAS AUTOMÁTICAS ===")

# Configurar el test suite
loader = unittest.TestLoader()
suite = unittest.TestSuite()

# Agregar pruebas
suite.addTests(loader.loadTestsFromTestCase(TestMigracionDatos))
suite.addTests(loader.loadTestsFromTestCase(TestIntegracionCompleta))

# Ejecutar pruebas
runner = unittest.TextTestRunner(verbosity=)
resultado = runner.run(suite)

# Generar reporte final
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
reporte_final = {
'timestamp': timestamp,
'total_pruebas': resultado.testsRun,
'pruebas_exitosas': resultado.testsRun - len(resultado.failures) - len(resultado.errors),
'pruebas_fallidas': len(resultado.failures),
'pruebas_error': len(resultado.errors),
'tasa_exito': ((resultado.testsRun - len(resultado.failures) - len(resultado.errors)) / resultado.testsRun * 100) if resultado.testsRun > 0 else 0
}

logger.info("=== REPORTE FINAL DE PRUEBAS ===")
logger.info(f"Total de pruebas: {reporte_final['total_pruebas']}")
logger.info(f"Pruebas exitosas: {reporte_final['pruebas_exitosas']}")
logger.info(f"Pruebas fallidas: {reporte_final['pruebas_fallidas']}")
logger.info(f"Pruebas con error: {reporte_final['pruebas_error']}")
logger.info(f"Tasa de éxito: {reporte_final['tasa_exito']:.1f}%")

# Guardar reporte
archivo_reporte = Path(f"reporte_pruebas_{timestamp}.json")
with open(archivo_reporte, 'w', encoding='utf-8') as f:
json.dump(reporte_final, f, indent=, ensure_ascii=False)

logger.info(f"Reporte guardado en: {archivo_reporte}")

return resultado.wasSuccessful()


def main():
"""Función principal"""
parser = argparse.ArgumentParser(description='Pruebas Sistema Cámaras UFRO')
parser.add_argument('--host', help='Host de base de datos para pruebas')
parser.add_argument('--database', help='Base de datos para pruebas')
parser.add_argument('--user', help='Usuario para pruebas')
parser.add_argument('--password', help='Contraseña para pruebas')
parser.add_argument('--port', type=int, default=543, help='Puerto para pruebas')
parser.add_argument('--solo-unitarias', action='store_true', help='Solo ejecutar pruebas unitarias')
parser.add_argument('--solo-integracion', action='store_true', help='Solo ejecutar pruebas de integración')

args = parser.parse_args()

# Configurar credenciales si se proporcionan
config_test = {}
if args.host:
config_test = {
'host': args.host,
'database': args.database or 'test_camaras_ufro',
'user': args.user or 'test_user',
'password': args.password or 'test_password',
'port': args.port
}

# Ejecutar pruebas según parámetros
if args.solo_unitarias:
suite = unittest.TestLoader().loadTestsFromTestCase(TestMigracionDatos)
resultado = unittest.TextTestRunner(verbosity=).run(suite)
sys.exit(0 if resultado.wasSuccessful() else 1)
elif args.solo_integracion:
suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegracionCompleta)
resultado = unittest.TextTestRunner(verbosity=).run(suite)
sys.exit(0 if resultado.wasSuccessful() else 1)
else:
# Ejecutar todas las pruebas
exito = ejecutar_pruebas_automaticas()
sys.exit(0 if exito else 1)


if __name__ == "__main__":
main()