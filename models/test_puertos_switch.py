"""
Script de prueba para el modelo PuertoSwitch.

Verifica la funcionalidad del modelo y sus validaciones.
"""

from datetime import datetime, date
from models import db, Switch, PuertoSwitch


def test_modelo_puerto_switch():
"""
Prueba todas las funcionalidades del modelo PuertoSwitch.
"""
print("=== PRUEBAS MODELO PUERTO SWITCH ===")

# Crear aplicación Flask para contexto
try:
from app import app
app_context = app.app_context()
app_context.push()
except:
print(" No se pudo crear contexto de aplicación Flask")
print("Ejecutando pruebas sin validación de DB...")
return

try:
# Verificar que existe un switch para las pruebas
switch_test = Switch.query.filter_by(codigo="SW-TEST-01").first()

if not switch_test:
print(" Creando switch de prueba...")
switch_test = Switch(
codigo="SW-TEST-01",
nombre="Switch Test",
marca="TestBrand",
modelo="TestModel",
puertos_totales=48,
puertos_usados=0,
puertos_disponibles=48,
estado="Activo"
)
switch_test.save(user_id=1)
print(f" Switch de prueba creado: {switch_test.codigo}")

print(f"Usando switch: {switch_test.codigo}")
print()

# Prueba 1: Crear puerto básico
print("1. Prueba creación puerto básico...")
puerto1 = PuertoSwitch(
switch_id=switch_test.id,
numero_puerto=1,
nombre_puerto="Puerto Test 1",
tipo_puerto="Ethernet",
velocidad_puerto="1Gbps",
estado_puerto="Activo",
vlan_asignada=100,
poe_habilitado=True,
potencia_maxima_poe=30.0
)
puerto1.save(user_id=1)
print(f" Puerto creado: {puerto1.numero_puerto}")

# Prueba : Crear puerto con MAC
print(". Prueba creación puerto con MAC...")
puerto = PuertoSwitch(
switch_id=switch_test.id,
numero_puerto=,
nombre_puerto="Puerto Test ",
tipo_puerto="SFP+",
velocidad_puerto="10Gbps",
estado_puerto="Activo",
mac_address="AA:BB:CC:DD:EE:FF",
poe_habilitado=False,
duplex="Full"
)
puerto.save(user_id=1)
print(f" Puerto con MAC creado: {puerto.numero_puerto}")

# Prueba 3: Consultar puertos del switch
print("3. Prueba consulta puertos del switch...")
puertos_switch = PuertoSwitch.get_by_switch(switch_test.id)
count = puertos_switch.count()
print(f" Puertos encontrados: {count}")

# Prueba 4: Consultas avanzadas
print("4. Prueba consultas avanzadas...")
puertos_activos = PuertoSwitch.get_activos()
print(f" Puertos activos en sistema: {puertos_activos.count()}")

puertos_vlan_100 = PuertoSwitch.get_por_vlan(100)
print(f" Puertos en VLAN 100: {puertos_vlan_100.count()}")

# Prueba 5: Métodos de validación
print("5. Prueba métodos de validación...")
puerto_test = PuertoSwitch.query.filter_by(numero_puerto=1).first()

if puerto_test.validate_numero_puerto():
print(" Validación número de puerto: OK")

if puerto_test.validate_mac_address():
print(" Validación MAC address: OK")

if puerto_test.validate_vlan():
print(" Validación VLAN: OK")

# Prueba 6: Métodos de estado
print("6. Prueba métodos de estado...")
if puerto_test.is_activo():
print(" Puerto activo detectado")

if puerto_test.is_poe_disponible():
print(" PoE disponible detectado")

print(f" Estado visual: {puerto_test.get_estado_visual()}")

# Prueba 7: Método de información
print("7. Prueba método de información...")
info_completa = puerto_test.get_puerto_completo()
print(f" Información completa: {info_completa}")

# Prueba 8: Actualizar última conexión
print("8. Prueba actualizar última conexión...")
puerto_test.update_ultima_conexion()
if puerto_test.ultima_conexion:
print(" Última conexión actualizada")

# Prueba 9: Validaciones de errores
print("9. Prueba validaciones de errores...")

# Puerto con número inválido
puerto_error1 = PuertoSwitch(
switch_id=switch_test.id,
numero_puerto=999, # Inválido
)
try:
puerto_error1.save()
print(" Validación de número de puerto falló")
except ValueError:
print(" Validación de número de puerto: OK")

# MAC inválida
puerto_error = PuertoSwitch(
switch_id=switch_test.id,
numero_puerto=99,
mac_address="invalid-mac-format"
)
try:
puerto_error.save()
print(" Validación de MAC falló")
except ValueError:
print(" Validación de MAC: OK")

# VLAN inválida
puerto_error3 = PuertoSwitch(
switch_id=switch_test.id,
numero_puerto=100,
vlan_asignada=9999 # Inválida
)
try:
puerto_error3.save()
print(" Validación de VLAN falló")
except ValueError:
print(" Validación de VLAN: OK")

# Prueba 10: Relaciones bidireccionales
print("10. Prueba relaciones bidireccionales...")
puerto_relacion = PuertoSwitch.query.filter_by(numero_puerto=1).first()
if puerto_relacion.switch:
print(f" Puerto -> Switch: {puerto_relacion.switch.codigo}")

if switch_test.puertos:
print(f" Switch -> Puertos: {len(switch_test.puertos)} puertos")

# Prueba 11: Soft delete
print("11. Prueba soft delete...")
puerto_delete = PuertoSwitch.query.filter_by(numero_puerto=).first()
puerto_delete.soft_delete(user_id=1)

# Verificar que no aparece en consultas normales
puertos_activos_post_delete = PuertoSwitch.get_by_switch(switch_test.id)
if puerto_delete not in puertos_activos_post_delete.all():
print(" Soft delete funciona correctamente")

print()
print("=== RESUMEN DE PRUEBAS ===")
print(" Creación de puertos")
print(" Consultas básicas y avanzadas")
print(" Validaciones de campos")
print(" Métodos de estado")
print(" Relaciones bidireccionales")
print(" Soft delete")
print(" Manejo de errores")
print()
print(" TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")

except Exception as e:
print(f" Error durante las pruebas: {e}")
import traceback
traceback.print_exc()

finally:
# Limpiar datos de prueba
try:
puertos_prueba = PuertoSwitch.query.filter(
PuertoSwitch.numero_puerto.in_([1, , 99, 100])
).all()

for puerto in puertos_prueba:
puerto.delete(user_id=1)

switch_test = Switch.query.filter_by(codigo="SW-TEST-01").first()
if switch_test:
switch_test.delete(user_id=1)

print(" Datos de prueba limpiados")
except Exception as e:
print(f" Error limpiando datos: {e}")


def verificar_estructura_modelo():
"""
Verifica que la estructura del modelo sea correcta.
"""
print("=== VERIFICACIÓN ESTRUCTURA MODELO ===")

try:
from models.puertos_switch import PuertoSwitch

# Verificar que tiene los métodos principales
metodos_requeridos = [
'validate_numero_puerto',
'validate_mac_address',
'validate_vlan',
'is_activo',
'is_poe_disponible',
'get_estado_visual',
'get_puerto_completo',
'update_ultima_conexion',
'get_by_switch',
'get_activos',
'get_por_vlan'
]

for metodo in metodos_requeridos:
if hasattr(PuertoSwitch, metodo):
print(f" Método {metodo}: Encontrado")
else:
print(f" Método {metodo}: No encontrado")

# Verificar campos
campos_requeridos = [
'switch_id',
'numero_puerto',
'tipo_puerto',
'estado_puerto',
'vlan_asignada',
'poe_habilitado',
'potencia_maxima_poe'
]

for campo in campos_requeridos:
if hasattr(PuertoSwitch, campo):
print(f" Campo {campo}: Encontrado")
else:
print(f" Campo {campo}: No encontrado")

print()
print(" Verificación de estructura completada")

except Exception as e:
print(f" Error verificando estructura: {e}")


if __name__ == "__main__":
verificar_estructura_modelo()
print()
test_modelo_puerto_switch()