"""
Script de ejemplo para demostrar el uso del modelo NetworkConnection

Este script muestra cómo:
1. Crear conexiones de red entre equipos
. Validar conexiones
3. Obtener topología de red
4. Realizar consultas de rendimiento
"""

from datetime import datetime
from models import db, Usuario, Ubicacion
from models.network_connections import NetworkConnection, ConnectionType, CableType
from models.equipo import Equipo


def ejemplo_uso_network_connections():
"""
Demuestra el uso completo del modelo NetworkConnection
"""
print("=== EJEMPLO DE USO DE NETWORK CONNECTION ===\n")

# 1. Crear equipos de prueba
print("1. Creando equipos de prueba...")

# Crear ubicación de prueba
ubicacion_test = Ubicacion(
nombre="Laboratorio de Pruebas",
direccion="Campus UFRO",
latitud=-38.7394,
longitud=-7.5904
)
db.session.add(ubicacion_test)
db.session.flush() # Para obtener el ID

# Crear usuario de prueba
usuario_test = Usuario(
username="admin_test",
<<<<<<< HEAD
email="test@ufro.cl",
=======
email="test.sistema@ufrontera.cl",
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
role="administrador"
)
db.session.add(usuario_test)
db.session.flush()

# Crear equipos de prueba
equipo1 = Equipo(
name="Switch Principal Lab",
tipo="switch",
marca="Cisco",
modelo="Catalyst 960",
ip_address="19.168.1.10",
ubicacion_id=ubicacion_test.id,
created_by=usuario_test.id,
estado="activo"
)

equipo = Equipo(
name="NVR Principal Lab",
tipo="nvr",
marca="Hikvision",
modelo="DS-7716NI",
ip_address="19.168.1.0",
ubicacion_id=ubicacion_test.id,
created_by=usuario_test.id,
estado="activo"
)

equipo3 = Equipo(
name="Camara IP Entrance",
tipo="camara",
marca="Axis",
modelo="M3007-PV",
ip_address="19.168.1.30",
ubicacion_id=ubicacion_test.id,
created_by=usuario_test.id,
estado="activo"
)

db.session.add_all([equipo1, equipo, equipo3])
db.session.flush()

print(f" Equipo 1 creado: {equipo1.name} (ID: {equipo1.id})")
print(f" Equipo creado: {equipo.name} (ID: {equipo.id})")
print(f" Equipo 3 creado: {equipo3.name} (ID: {equipo3.id})")

# . Crear conexiones de red
print("\n. Creando conexiones de red...")

# Conexión Switch -> NVR (Ethernet, 1Gbps)
conexion1 = NetworkConnection.crear_conexion(
equipo_origen_id=equipo1.id,
equipo_destino_id=equipo.id,
tipo_conexion=ConnectionType.ETHERNET,
equipo_origen_tipo="switch",
equipo_destino_tipo="nvr",
ancho_banda=1000.0, # 1 Gbps
latencia=.5,
tipo_cable=CableType.CAT6,
longitud_cable=15.0,
puerto_origen="GigabitEthernet0/1",
puerto_destino="LAN1",
vlan_id=100,
activa=True,
descripcion="Conexión principal entre Switch y NVR"
)

# Conexión NVR -> Camara (PoE)
conexion = NetworkConnection.crear_conexion(
equipo_origen_id=equipo.id,
equipo_destino_id=equipo3.id,
tipo_conexion=ConnectionType.POWER_OVER_ETHERNET,
equipo_origen_tipo="nvr",
equipo_destino_tipo="camara",
ancho_banda=100.0, # 100 Mbps
latencia=5.,
tipo_cable=CableType.CAT5E,
longitud_cable=5.0,
puerto_origen="PoE1",
puerto_destino="LAN",
vlan_id=100,
activa=True,
descripcion="Alimentación y datos para cámara de entrada"
)

print(f" Conexión creada: {conexion1}")
print(f" Conexión creada: {conexion}")

# 3. Validar conexiones
print("\n3. Validando conexiones...")

for conexion in [conexion1, conexion]:
errores = conexion.validar_conexion()
if errores:
print(f" Errores en {conexion}: {errores}")
else:
print(f" Conexión válida: {conexion}")

# 4. Guardar conexiones
print("\n4. Guardando conexiones en la base de datos...")

try:
conexion1.guardar()
print(" Conexión 1 guardada exitosamente")
conexion.guardar()
print(" Conexión guardada exitosamente")
except Exception as e:
print(f" Error al guardar: {str(e)}")

# 5. Consultar conexiones
print("\n5. Consultando conexiones...")

# Obtener conexiones por equipo
conexiones_switch = NetworkConnection.obtener_conexiones_por_equipo(equipo1.id)
print(f"Conexiones del Switch (ID {equipo1.id}): {len(conexiones_switch)}")

conexiones_nvr = NetworkConnection.obtener_conexiones_por_equipo(equipo.id)
print(f"Conexiones del NVR (ID {equipo.id}): {len(conexiones_nvr)}")

# 6. Mostrar topología
print("\n6. Topología de red:")
topologia = NetworkConnection.obtener_topologia_red()

for equipo_id, info in topologia.items():
print(f"Equipo: {info['equipo_tipo']}#{info['equipo_id']}")
for conexion in info['conexiones']:
print(f" → {conexion['equipo_destino_tipo']}#{conexion['equipo_destino_id']} "
f"({conexion['tipo_conexion']}, {conexion['ancho_banda'] or 'N/A'} Mbps)")

# 7. Mostrar métricas de rendimiento
print("\n7. Métricas de rendimiento:")

for conexion in [conexion1, conexion]:
print(f"\nConexión: {conexion}")
print(f" Velocidad: {conexion.obtener_velocidad_conexion()}")
print(f" Calidad: {conexion.obtener_calidad_conexion()}")
print(f" Latencia: {conexion.latencia or 'N/A'} ms")
print(f" Pérdida de paquetes: {conexion.perdida_paquetes}%")

# 8. Probar validación de errores
print("\n8. Probando validación de errores...")

# Intentar crear conexión inválida (mismo equipo)
conexion_invalida = NetworkConnection(
equipo_origen_id=equipo1.id,
equipo_destino_id=equipo1.id, # ¡Mismo equipo
tipo_conexion=ConnectionType.ETHERNET,
equipo_origen_tipo="switch",
equipo_destino_tipo="switch",
ancho_banda=-100 # Valor inválido
)

errores = conexion_invalida.validar_conexion()
print(f"Errores de validación detectados: {len(errores)}")
for error in errores:
print(f" - {error}")

# 9. Consulta avanzada
print("\n9. Consultas avanzadas:")

# Obtener todas las conexiones activas
conexiones_activas = NetworkConnection.query.filter_by(activa=True, deleted=False).all()
print(f"Total de conexiones activas: {len(conexiones_activas)}")

# Obtener conexiones por tipo
conexiones_ethernet = NetworkConnection.query.filter_by(
tipo_conexion=ConnectionType.ETHERNET,
deleted=False
).all()
print(f"Conexiones Ethernet: {len(conexiones_ethernet)}")

# Obtener conexiones de alta velocidad (> 500 Mbps)
conexiones_alta_velocidad = NetworkConnection.query.filter(
NetworkConnection.ancho_banda > 500,
NetworkConnection.deleted == False
).all()
print(f"Conexiones de alta velocidad: {len(conexiones_alta_velocidad)}")

print("\n=== EJEMPLO COMPLETADO ===")

# Retornar datos para pruebas adicionales
return {
'ubicacion': ubicacion_test,
'usuario': usuario_test,
'equipos': [equipo1, equipo, equipo3],
'conexiones': [conexion1, conexion]
}


def limpiar_datos_prueba(datos):
"""
Limpia los datos de prueba creados
"""
print("\n Limpiando datos de prueba...")

try:
# Eliminar conexiones
for conexion in datos['conexiones']:
db.session.delete(conexion)

# Eliminar equipos
for equipo in datos['equipos']:
db.session.delete(equipo)

# Eliminar usuario y ubicación
db.session.delete(datos['usuario'])
db.session.delete(datos['ubicacion'])

db.session.commit()
print(" Datos de prueba limpiados exitosamente")

except Exception as e:
print(f" Error al limpiar datos: {str(e)}")
db.session.rollback()


if __name__ == "__main__":
"""
Ejecutar el ejemplo de uso
"""
# En una aplicación real, esto estaría en el contexto de Flask
# with app.app_context():

# Crear datos de prueba
datos_prueba = ejemplo_uso_network_connections()

# Opcional: Limpiar datos
# limpiar_datos_prueba(datos_prueba)