"""
Script de ejemplo para demostrar el uso del modelo EquipoTecnico.

Este script muestra cómo:
1. Crear técnicos
. Asignar fallas y mantenimientos
3. Calcular métricas de rendimiento
4. Buscar técnicos por especialidad
5. Gestionar disponibilidad
"""

from datetime import datetime, date
from models import db, EquipoTecnico, TecnicoStatus, Falla, Mantenimiento

def ejemplo_uso_equipo_tecnico():
"""
Ejemplo completo de uso del modelo EquipoTecnico.
"""

# Crear técnicos de ejemplo
print("=== CREANDO EQUIPO TÉCNICO ===")

tecnico1 = EquipoTecnico(
nombre="Juan",
apellido="Pérez",
especialidad="Cámaras de Seguridad",
telefono="+5691345678",
email="juan.perez@ufrontera.cl",
estado=TecnicoStatus.ACTIVO.value,
fecha_ingreso=date(03, 1, 15),
cargo="Técnico Senior",
departamento="Infraestructura",
nivel_experiencia="Avanzado",
disponibilidad_horario={
"lunes_viernes": "08:00-17:00",
"sabado": "08:00-1:00",
"domingo": "descanso"
}
)

tecnico = EquipoTecnico(
nombre="María",
apellido="González",
especialidad="Sistemas de Red",
telefono="+5698765431",
email="maria.gonzalez@ufrontera.cl",
estado=TecnicoStatus.DISPONIBLE.value,
fecha_ingreso=date(03, 3, 0),
cargo="Técnico Especialista",
departamento="Redes",
nivel_experiencia="Intermedio"
)

tecnico3 = EquipoTecnico(
nombre="Carlos",
apellido="Rodríguez",
especialidad="UPS y Energía",
telefono="+569113344",
email="carlos.rodriguez@ufrontera.cl",
estado=TecnicoStatus.OCUPADO.value,
fecha_ingreso=date(0, 8, 10),
cargo="Técnico Senior",
departamento="Mantenimiento",
nivel_experiencia="Experto"
)

# Añadir habilidades y certificaciones
tecnico1.habilidades = {
"camaras_ip": 5,
"camaras_analogicas": 4,
"nvr": 5,
"cableado": 4
}

tecnico1.add_certification("Certificación en Instalación de Cámaras IP", date(03, 6, 15))
tecnico1.add_certification("Certificación en Sistemas de Videovigilancia", date(03, 8, 0))

tecnico.add_skill("Switches Cisco", 5)
tecnico.add_skill("VLAN", 4)
tecnico.add_skill("Protocolos de Red", 5)

tecnico3.certificaciones = [
{
"certification": "Certificación en Mantenimiento UPS",
"date_obtained": "0-10-01",
"added_date": datetime.utcnow().isoformat()
}
]

# Guardar técnicos
db.session.add_all([tecnico1, tecnico, tecnico3])
db.session.commit()

print(f" Creados {len([tecnico1, tecnico, tecnico3])} técnicos")
print(f" - {tecnico1.get_nombre_completo()} ({tecnico1.get_iniciales()})")
print(f" - {tecnico.get_nombre_completo()} ({tecnico.get_iniciales()})")
print(f" - {tecnico3.get_nombre_completo()} ({tecnico3.get_iniciales()})")

# Consultar técnicos
print("\n=== CONSULTANDO EQUIPO TÉCNICO ===")

# Obtener técnicos activos
activos = EquipoTecnico.get_active_technicians()
print(f"Técnicos activos: {len(activos)}")
for t in activos:
print(f" - {t.get_nombre_completo()}: {t.estado}")

# Buscar por especialidad
print("\n=== BÚSQUEDA POR ESPECIALIDAD ===")
especialistas_red = EquipoTecnico.get_by_specialty("Red")
print(f"Técnicos en redes: {len(especialistas_red)}")
for t in especialistas_red:
print(f" - {t.get_nombre_completo()}: {t.especialidad}")

# Obtener técnicos disponibles
print("\n=== TÉCNICOS DISPONIBLES ===")
disponibles = EquipoTecnico.get_available_technicians()
print(f"Técnicos disponibles: {len(disponibles)}")
for t in disponibles:
print(f" - {t.get_nombre_completo()}: {t.get_iniciales()}")

# Consultar carga de trabajo
print("\n=== CARGA DE TRABAJO ===")
for t in [tecnico1, tecnico, tecnico3]:
workload = t.get_workload()
print(f"{t.get_nombre_completo()}:")
print(f" - Fallas activas: {workload['fallas_activas']}")
print(f" - Mantenimientos activos: {workload['mantenimientos_activos']}")
print(f" - Total asignaciones: {workload['total_asignaciones']}")
print(f" - Disponible: {'Sí' if t.is_available() else 'No'}")

# Consultar especialidades
print("\n=== ESPECIALIDADES ===")
for t in [tecnico1, tecnico, tecnico3]:
especialidades = t.get_specialties()
print(f"{t.get_nombre_completo()}:")
print(f" - Especialidades: {especialidades}")
print(f" - Habilidades: {t.habilidades}")

# Ejemplo de uso de métodos
print("\n=== MÉTODOS DE UTILIDAD ===")

# Verificar habilidades
print(f"¿Juan puede trabajar con cámaras IP? {tecnico1.has_skill('camaras_ip')}")
print(f"Nivel de Juan en cámaras IP: {tecnico1.get_skill_level('camaras_ip')}")

# Buscar técnicos
print("\n=== BÚSQUEDA GENERAL ===")
resultados = EquipoTecnico.search("Juan")
print(f"Búsqueda 'Juan': {len(resultados)} resultados")
for r in resultados:
print(f" - {r.get_nombre_completo()}")

resultados_red = EquipoTecnico.search("María", "Red")
print(f"Búsqueda 'María' + especialidad 'Red': {len(resultados_red)} resultados")

# Convertir a diccionario
print("\n=== EXPORTAR A DICT ===")
dict_tecnico1 = tecnico1.to_dict()
print("Datos del técnico 1:")
print(f" - Nombre: {dict_tecnico1['nombre_completo']}")
print(f" - Estado: {dict_tecnico1['estado']}")
print(f" - Especialidades: {dict_tecnico1['specialties']}")
print(f" - Carga de trabajo: {dict_tecnico1['workload']}")
print(f" - Métricas: {dict_tecnico1['performance_metrics']}")

print("\n=== EJEMPLO COMPLETADO ===")
print("El modelo EquipoTecnico está funcionando correctamente")

return [tecnico1, tecnico, tecnico3]

def ejemplo_asignacion_tareas(tecnicos):
"""
Ejemplo de asignación de fallas y mantenimientos.
"""
print("\n=== EJEMPLO DE ASIGNACIÓN DE TAREAS ===")

tecnico1, tecnico, tecnico3 = tecnicos

# Crear falla de ejemplo
falla_ejemplo = Falla(
title="Cámara IP no responde",
descripcion="La cámara IP en el pasillo principal no está enviando señal",
tipo="conectividad",
prioridad="alta",
estado="abierta",
camara_afectada="PAS_001"
)

db.session.add(falla_ejemplo)
db.session.commit()

# Asignar falla al técnico
tecnico1.assign_falla(falla_ejemplo.id)

print(f" Falla asignada a {tecnico1.get_nombre_completo()}")
print(f" - Falla ID: {falla_ejemplo.id}")
print(f" - Título: {falla_ejemplo.title}")
print(f" - Técnico asignado: {falla_ejemplo.tecnico_asignado}")

# Crear mantenimiento de ejemplo
mantenimiento_ejemplo = Mantenimiento(
titulo="Mantenimiento preventivo Switch Core",
descripcion="Limpieza de ventiladores y verificación de conexiones",
tipo="preventivo",
categoria="sistema_red",
estado="programado",
fecha_programada=date(04, 1, 1)
)

db.session.add(mantenimiento_ejemplo)
db.session.commit()

# Asignar mantenimiento al técnico
tecnico.assign_mantenimiento(mantenimiento_ejemplo.id)

print(f" Mantenimiento asignado a {tecnico.get_nombre_completo()}")
print(f" - Mantenimiento ID: {mantenimiento_ejemplo.id}")
print(f" - Título: {mantenimiento_ejemplo.titulo}")
print(f" - Técnico asignado: {mantenimiento_ejemplo.tecnico_responsable}")

# Actualizar métricas de rendimiento
tecnico1.update_performance_metrics()
tecnico.update_performance_metrics()

print("\n=== MÉTRICAS ACTUALIZADAS ===")
for t in [tecnico1, tecnico]:
metrics = t.get_performance_metrics()
print(f"{t.get_nombre_completo()}:")
print(f" - Total fallas: {metrics['total_fallas']}")
print(f" - Fallas resueltas: {metrics['fallas_resueltas']}")
print(f" - Tasa resolución: {metrics['tasa_resolucion_fallas']}%")

if __name__ == "__main__":
"""
Ejecutar ejemplos del modelo EquipoTecnico.
"""

print("INICIANDO EJEMPLOS DEL MODELO EQUIPO_TECNICO")
print("=" * 50)

# Crear técnicos y realizar operaciones básicas
tecnicos = ejemplo_uso_equipo_tecnico()

# Ejemplo de asignación de tareas
ejemplo_asignacion_tareas(tecnicos)

print("\n" + "=" * 50)
print("EJEMPLOS COMPLETADOS EXITOSAMENTE")
print("El modelo EquipoTecnico incluye:")
print(" Gestión de personal técnico")
print(" Relaciones con fallas y mantenimientos")
print(" Cálculo de métricas de rendimiento")
print(" Gestión de disponibilidad y carga de trabajo")
print(" Búsqueda y filtrado avanzado")
print(" Exportación de datos completa")
print("=" * 50)