"""
Ejemplo de uso del modelo PuertoSwitch.

Este script demuestra cómo crear, consultar y utilizar
el modelo de puertos de switches.
"""

from datetime import datetime, date
from models import db, Switch, PuertoSwitch


def ejemplo_uso_puerto_switch():
"""
Ejemplo completo de uso del modelo PuertoSwitch.
"""

# Crear un switch de ejemplo (asumiendo que ya existe uno)
switch_ejemplo = Switch.query.filter_by(codigo="SW-CENTRAL-01").first()

if not switch_ejemplo:
print("Error: No se encontró el switch SW-CENTRAL-01")
return

# Crear puertos para el switch
puertos_ejemplo = [
{
"numero_puerto": 1,
"nombre_puerto": "Uplink Principal",
"tipo_puerto": "SFP+",
"velocidad_puerto": "10Gbps",
"estado_puerto": "Activo",
"vlan_asignada": 100,
"descripcion": "Puerto de enlace principal al core",
"conecta_a": "Switch Core Principal",
"poe_habilitado": False,
"potencia_maxima_poe": None,
"duplex": "Full",
"mac_address": "AA:BB:CC:DD:EE:01",
"fecha_ultimo_mantenimiento": date(05, 1, 15),
"observaciones": "Puerto crítico para la conectividad"
},
{
"numero_puerto": ,
"nombre_puerto": "Uplink Secundario",
"tipo_puerto": "SFP+",
"velocidad_puerto": "10Gbps",
"estado_puerto": "Activo",
"vlan_asignada": 100,
"descripcion": "Puerto de enlace secundario (backup)",
"conecta_a": "Switch Core Secundario",
"poe_habilitado": False,
"potencia_maxima_poe": None,
"duplex": "Full",
"mac_address": "AA:BB:CC:DD:EE:0",
"fecha_ultimo_mantenimiento": date(05, 1, 15),
"observaciones": "Puerto de respaldo"
},
{
"numero_puerto": 3,
"nombre_puerto": "Cámara Lobby Norte",
"tipo_puerto": "Ethernet",
"velocidad_puerto": "1Gbps",
"estado_puerto": "Activo",
"vlan_asignada": 00,
"descripcion": "Cámara de seguridad del lobby norte",
"conecta_a": "Cámara IP - Lobby Norte",
"poe_habilitado": True,
"potencia_maxima_poe": 30.0,
"duplex": "Auto",
"mac_address": "11::33:44:55:66",
"fecha_ultimo_mantenimiento": date(05, , 10),
"observaciones": "Cámara HD con visión nocturna"
},
{
"numero_puerto": 4,
"nombre_puerto": "AP WiFi Planta 1",
"tipo_puerto": "Ethernet",
"velocidad_puerto": "1Gbps",
"estado_puerto": "Activo",
"vlan_asignada": 300,
"descripcion": "Access Point WiFi planta baja",
"conecta_a": "AP WiFi - Planta 1",
"poe_habilitado": True,
"potencia_maxima_poe": 15.0,
"duplex": "Auto",
"mac_address": None,
"fecha_ultimo_mantenimiento": date(05, , 5),
"observaciones": "AP dual band AC100"
},
{
"numero_puerto": 5,
"nombre_puerto": "Sin conexión",
"tipo_puerto": "Ethernet",
"velocidad_puerto": "1Gbps",
"estado_puerto": "Inactivo",
"vlan_asignada": None,
"descripcion": "Puerto disponible",
"conecta_a": None,
"poe_habilitado": True,
"potencia_maxima_poe": 30.0,
"duplex": "Auto",
"mac_address": None,
"fecha_ultimo_mantenimiento": date(05, 1, 0),
"observaciones": "Puerto libre para futuras conexiones"
}
]

print("=== EJEMPLO DE USO PUERTOS SWITCH ===")
print(f"Switch: {switch_ejemplo.codigo} - {switch_ejemplo.nombre}")
print(f"Marca: {switch_ejemplo.marca} {switch_ejemplo.modelo}")
print(f"Puertos totales: {switch_ejemplo.puertos_totales}")
print()

# Crear y guardar los puertos
puertos_creados = []
for puerto_data in puertos_ejemplo:
try:
puerto = PuertoSwitch(switch_id=switch_ejemplo.id, **puerto_data)
puerto.save() # Guardar con validaciones

puertos_creados.append(puerto)
print(f" Puerto {puerto.numero_puerto} creado: {puerto.nombre_puerto}")

except Exception as e:
print(f" Error creando puerto {puerto_data['numero_puerto']}: {e}")

print()
print("=== CONSULTA DE PUERTOS ===")

# Consultar puertos del switch
puertos_switch = PuertoSwitch.get_by_switch(switch_ejemplo.id)

for puerto in puertos_switch.order_by(PuertoSwitch.numero_puerto):
print(f"Puerto {puerto.numero_puerto}: {puerto.get_puerto_completo()}")
print(f" Estado: {puerto.get_estado_visual()}")
print(f" Tipo: {puerto.tipo_puerto} - Velocidad: {puerto.velocidad_puerto}")
if puerto.vlan_asignada:
print(f" VLAN: {puerto.vlan_asignada}")
if puerto.is_poe_disponible():
print(f" PoE: {puerto.potencia_maxima_poe}W")
if puerto.conecta_a:
print(f" Conectado a: {puerto.conecta_a}")
print()

print("=== ESTADÍSTICAS ===")

# Estadísticas de puertos
total_puertos = PuertoSwitch.get_by_switch(switch_ejemplo.id).count()
puertos_activos = PuertoSwitch.get_by_switch(switch_ejemplo.id).filter(
PuertoSwitch.estado_puerto.in_(['Activo', 'activo'])
).count()
puertos_con_poe = PuertoSwitch.get_by_switch(switch_ejemplo.id).filter(
PuertoSwitch.poe_habilitado == True
).count()

print(f"Total de puertos configurados: {total_puertos}")
print(f"Puertos activos: {puertos_activos}")
print(f"Puertos con PoE: {puertos_con_poe}")
print(f"Utilización de puertos: {(puertos_activos/total_puertos)*100:.1f}%")

print()
print("=== VALIDACIONES ===")

# Probar validaciones
puerto_test = PuertoSwitch(
switch_id=switch_ejemplo.id,
numero_puerto=99, # Puerto inválido
mac_address="invalid-mac", # MAC inválida
vlan_asignada=5000 # VLAN inválida
)

try:
puerto_test.save()
print(" Las validaciones no funcionaron")
except ValueError as e:
print(f" Validaciones funcionando: {e}")

print()
print("=== CONSULTA AVANZADA ===")

# Consulta por VLAN
print("Puertos en VLAN 00:")
puertos_vlan_00 = PuertoSwitch.get_por_vlan(00)
for puerto in puertos_vlan_00:
if puerto.switch_id == switch_ejemplo.id:
print(f" - Puerto {puerto.numero_puerto}: {puerto.nombre_puerto}")

print()
print(" Ejemplo completado exitosamente")


def demo_relaciones():
"""
Demuestra las relaciones bidireccionales entre Switch y PuertoSwitch.
"""

switch = Switch.query.filter_by(codigo="SW-CENTRAL-01").first()
if not switch:
print("No se encontró el switch SW-CENTRAL-01")
return

print("=== DEMO RELACIONES BIDIRECCIONALES ===")

# Desde Switch hacia PuertoSwitch
print(f"Switch: {switch.codigo}")
print(f"Total de puertos relacionados: {len(switch.puertos)}")

for puerto in switch.puertos:
print(f" - Puerto {puerto.numero_puerto}: {puerto.nombre_puerto} ({puerto.tipo_puerto})")

print()

# Desde PuertoSwitch hacia Switch
puerto = PuertoSwitch.query.filter_by(numero_puerto=3).first()
if puerto:
print(f"Puerto {puerto.numero_puerto}: {puerto.nombre_puerto}")
print(f"Pertenece al switch: {puerto.switch.codigo} - {puerto.switch.nombre}")
print(f"Marca del switch: {puerto.switch.marca} {puerto.switch.modelo}")

print()


def demo_actualizacion_estado():
"""
Demuestra cómo actualizar el estado de un puerto.
"""

puerto = PuertoSwitch.query.filter_by(numero_puerto=5).first()
if not puerto:
print("No se encontró el puerto 5")
return

print("=== DEMO ACTUALIZACIÓN DE ESTADO ===")
print(f"Estado actual: {puerto.get_estado_visual()}")

# Cambiar estado a activo
puerto.estado_puerto = "Activo"
puerto.conecta_a = "Nueva Cámara Seguridad"
puerto.update_ultima_conexion()

print(f"Nuevo estado: {puerto.get_estado_visual()}")
print(f"Conectado a: {puerto.conecta_a}")
print(f"Última conexión: {puerto.ultima_conexion}")


if __name__ == "__main__":
# Inicializar la aplicación Flask (necesario para SQLAlchemy)
from app import app

with app.app_context():
ejemplo_uso_puerto_switch()
demo_relaciones()
demo_actualizacion_estado()