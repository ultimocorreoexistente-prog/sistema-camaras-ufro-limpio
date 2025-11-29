#/usr/bin/env python3
"""
Script para insertar datos iniciales en la base de datos.

Este script crea datos de ejemplo y configuración inicial para el sistema.
"""

import os
import sys
from datetime import datetime, timedelta

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import init_db
from models.usuario import Usuario
from models.ubicacion import Ubicacion
from models.base import Camara
from models.nvr import NVR, NVRSystemType
from models.switch import Switch, SwitchType
from models.ups import UPS, UPSType
from models.gabinete import Gabinete, CabinetType
from models.network_connections import NetworkConnection, ConnectionType

def create_app():
"""Crear aplicación Flask."""
app = Flask(__name__)
database_url = os.getenv('DATABASE_URL', 'sqlite:///infraestructura.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
return app

def insert_initial_data():
"""Insertar datos iniciales en la base de datos."""
print(" INSERTANDO DATOS INICIALES")
print("=" * 40)

app = create_app()

with app.app_context():
try:
# 1. CREAR USUARIOS INICIALES
print("\n Creando usuarios iniciales...")

admin = Usuario(
username="admin",
email="admin.sistema@ufrontera.cl",
full_name="Administrador del Sistema",
role="administrador",
phone="+56 9 134 5678",
department="TI",
is_active=True
)
admin.set_password("admin13")
admin.save()
print(f" Usuario admin creado (ID: {admin.id})")

tecnico = Usuario(
username="tecnico",
email="tecnico@sistema.com",
full_name="Técnico Principal",
role="tecnico",
phone="+56 9 8765 431",
department="Soporte Técnico",
is_active=True
)
tecnico.set_password("tecnico13")
tecnico.save()
print(f" Usuario técnico creado (ID: {tecnico.id})")

operador = Usuario(
username="operador",
email="operador@sistema.com",
full_name="Operador de Sistema",
role="operador",
phone="+56 9 11 3344",
department="Operaciones",
is_active=True
)
operador.set_password("operador13")
operador.save()
print(f" Usuario operador creado (ID: {operador.id})")

# . CREAR UBICACIONES
print("\n Creando ubicaciones...")

campus_principal = Ubicacion(
name="Campus Principal",
description="Campus principal de la empresa",
address="Av. Universidad 1000, Santiago",
latitude=-33.4489,
longitude=-70.6693,
location_type="campus",
building="Campus Principal",
is_public=True,
created_by=admin.id
)
campus_principal.save()
print(f" Ubicación: {campus_principal.name} (ID: {campus_principal.id})")

edificio_a = Ubicacion(
name="Edificio A",
description="Edificio administrativo principal",
location_type="edificio",
building="Edificio A",
floor="Todos",
parent_id=campus_principal.id,
created_by=admin.id
)
edificio_a.save()
print(f" Ubicación: {edificio_a.name} (ID: {edificio_a.id})")

sala_servidores = Ubicacion(
name="Sala de Servidores",
description="Sala principal de servidores y equipos de red",
location_type="sala",
building="Edificio A",
floor="Sótano",
parent_id=edificio_a.id,
created_by=admin.id
)
sala_servidores.save()
print(f" Ubicación: {sala_servidores.name} (ID: {sala_servidores.id})")

recepcion = Ubicacion(
name="Recepción",
description="Área de recepción y hall principal",
location_type="area",
building="Edificio A",
floor="Piso 1",
parent_id=edificio_a.id,
created_by=admin.id
)
recepcion.save()
print(f" Ubicación: {recepcion.name} (ID: {recepcion.id})")

# 3. CREAR GABINETES
print("\n Creando gabinetes...")

rack_principal = Gabinete(
name="Rack Principal 01",
description="Rack principal para equipos de red",
cabinet_type=CabinetType.RACK,
material="steel",
rack_units=4,
usable_rack_units=40,
width_mm=600,
depth_mm=1000,
height_mm=000,
max_weight_kg=500,
ventilation_type="active",
cooling_fans=4,
temperature_monitoring=True,
humidity_monitoring=True,
security_lock=True,
cable_management=True,
pdus_included=True,
pdus_count=,
ubicacion_id=sala_servidores.id,
created_by=admin.id
)
rack_principal.save()
print(f" Gabinete: {rack_principal.name} (ID: {rack_principal.id})")

# 4. CREAR EQUIPOS NVR
print("\n Creando equipos NVR...")

nvr_principal = NVR(
name="NVR-Principal-01",
model="Hikvision DS-773NIX-4P",
manufacturer="Hikvision",
serial_number="HK040001",
inventory_number="INV-NVR-001",
ip_address="19.168.1.10",
hostname="nvr-principal01",
system_type=NVRSystemType.NVR,
channels=16,
max_channels=3,
storage_capacity=4000, # 4TB
storage_type="raid",
recording_mode="continuo",
poe_ports=4,
max_poe_power=60,
ubicacion_id=sala_servidores.id,
created_by=admin.id
)
nvr_principal.save()
print(f" NVR: {nvr_principal.name} (ID: {nvr_principal.id})")

# 5. CREAR SWITCHES
print("\n Creando switches...")

switch_core = Switch(
name="Switch-Core-01",
model="Cisco Catalyst 960X-48FPD-L",
manufacturer="Cisco",
serial_number="CSC040001",
inventory_number="INV-SW-001",
ip_address="19.168.1.",
switch_type=SwitchType.CORE,
total_ports=48,
poe_ports=0,
port_speed="1Gbps",
fiber_ports=4,
vlan_support=True,
qos_support=True,
managed=True,
layer_support="L3",
ubicacion_id=sala_servidores.id,
created_by=admin.id
)
switch_core.save()
print(f" Switch: {switch_core.name} (ID: {switch_core.id})")

switch_access = Switch(
name="Switch-Access-01",
model="TP-Link TL-SG48P",
manufacturer="TP-Link",
serial_number="TP040001",
inventory_number="INV-SW-00",
ip_address="19.168.1.3",
switch_type=SwitchType.ACCESS,
total_ports=4,
poe_ports=4,
max_poe_power=370,
port_speed="1Gbps",
vlan_support=True,
qos_support=True,
managed=True,
ubicacion_id=sala_servidores.id,
created_by=admin.id
)
switch_access.save()
print(f" Switch: {switch_access.name} (ID: {switch_access.id})")

# 6. CREAR UPS
print("\n Creando UPS...")

ups_principal = UPS(
name="UPS-Principal-01",
model="APC Smart-UPS SRT 6000VA",
manufacturer="APC",
serial_number="APC040001",
inventory_number="INV-UPS-001",
ip_address="19.168.1.4",
ups_type=UPSType.ONLINE,
capacity_va=6000,
capacity_watts=6000,
battery_type="vrla",
runtime_minutes=480, # 8 horas
load_percentage=0,
ubicacion_id=sala_servidores.id,
created_by=admin.id
)
ups_principal.save()
print(f" UPS: {ups_principal.name} (ID: {ups_principal.id})")

# 7. CREAR CÁMARAS
print("\n Creando cámaras...")

camara_recepcion = Camara(
name="Camara-Recepcion-01",
model="Hikvision DS-CD145FWD-I",
manufacturer="Hikvision",
serial_number="HK040101",
inventory_number="INV-CAM-001",
ip_address="19.168.1.101",
mac_address="AA:BB:CC:DD:EE:01",
port=554,
camera_type=CameraType.DOMO,
connection_type="ethernet",
power_over_ethernet=True,
resolution="190x1080",
frame_rate=30,
codec="H.64",
nvr_id=nvr_principal.id,
ubicacion_id=recepcion.id,
created_by=admin.id
)
camara_recepcion.save()
nvr_principal.add_camera(camara_recepcion)
print(f" Cámara: {camara_recepcion.name} (ID: {camara_recepcion.id})")

camara_entrada = Camara(
name="Camara-Entrada-Principal",
model="Hikvision DS-CD145FWD-I",
manufacturer="Hikvision",
serial_number="HK04010",
inventory_number="INV-CAM-00",
ip_address="19.168.1.10",
mac_address="AA:BB:CC:DD:EE:0",
port=554,
camera_type=CameraType.FIJA,
connection_type="ethernet",
power_over_ethernet=True,
resolution="190x1080",
frame_rate=5,
codec="H.64",
nvr_id=nvr_principal.id,
ubicacion_id=recepcion.id,
created_by=admin.id
)
camara_entrada.save()
nvr_principal.add_camera(camara_entrada)
print(f" Cámara: {camara_entrada.name} (ID: {camara_entrada.id})")

# 8. CREAR CONEXIONES DE RED
print("\n Creando conexiones de red...")

# Conectar NVR al switch
conexion_nvr = NetworkConnection(
source_equipment_id=nvr_principal.id,
source_equipment_type="nvr",
target_equipment_id=switch_access.id,
target_equipment_type="switch",
connection_type="ethernet",
cable_type="Cat6",
cable_length=5.0,
port_source="eth0",
port_target="GigabitEthernet1/0/1",
is_active=True,
bandwidth_limit=1000
)
conexion_nvr.save()
print(f" Conexión: NVR → Switch Access")

# Conectar cámaras al NVR
conexion_cam1 = NetworkConnection(
source_equipment_id=nvr_principal.id,
source_equipment_type="nvr",
target_equipment_id=camara_recepcion.id,
target_equipment_type="camara",
connection_type="ethernet",
cable_type="Cat6",
cable_length=30.0,
port_source="eth1",
port_target="eth0",
is_active=True,
bandwidth_limit=100
)
conexion_cam1.save()
print(f" Conexión: NVR → Cámara Recepción")

conexion_cam = NetworkConnection(
source_equipment_id=nvr_principal.id,
source_equipment_type="nvr",
target_equipment_id=camara_entrada.id,
target_equipment_type="camara",
connection_type="ethernet",
cable_type="Cat6",
cable_length=5.0,
port_source="eth",
port_target="eth0",
is_active=True,
bandwidth_limit=100
)
conexion_cam.save()
print(f" Conexión: NVR → Cámara Entrada")

# 9. RESUMEN FINAL
print("\n RESUMEN DE DATOS CREADOS:")
print(f" Usuarios: {Usuario.query.count()}")
print(f" Ubicaciones: {Ubicacion.query.count()}")
print(f" Gabinetes: {Gabinete.query.count()}")
print(f" NVRs: {NVR.query.count()}")
print(f" Switches: {Switch.query.count()}")
print(f" UPSs: {UPS.query.count()}")
print(f" Cámaras: {Camara.query.count()}")
print(f" Conexiones: {NetworkConnection.query.count()}")

print("\n DATOS INICIALES CREADOS EXITOSAMENTE")
print("\n CREDENCIALES DE ACCESO:")
print(" Administrador:")
print(" Usuario: admin")
print(" Contraseña: admin13")
print(" Técnico:")
print(" Usuario: tecnico")
print(" Contraseña: tecnico13")
print(" Operador:")
print(" Usuario: operador")
print(" Contraseña: operador13")
print("\n IMPORTANTE: Cambiar las contraseñas en producción")

return True

except Exception as e:
print(f"\n Error al insertar datos: {str(e)}")
import traceback
traceback.print_exc()
return False

def main():
"""Función principal."""
print(" SISTEMA DE DATOS INICIALES")
print("=" * 40)

respuesta = input("¿Quieres insertar datos de ejemplo? (s/n): ").lower().strip()

if respuesta in ['s', 'si', 'sí', 'yes', 'y']:
success = insert_initial_data()
if success:
print("\n Proceso completado exitosamente.")
else:
print("\n El proceso falló.")
else:
print(" Operación cancelada.")

if __name__ == "__main__":
main()