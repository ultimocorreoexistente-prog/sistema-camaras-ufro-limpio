# Modelo EquipoTecnico - Documentación Completa

## Resumen

El modelo `EquipoTecnico` ha sido creado exitosamente basándose en la estructura extraída de Railway con 8 columnas principales. Este modelo gestiona el personal técnico del sistema de cámaras UFRO.

## Estructura de la Tabla

### Campos Principales (Railway)
- `id` (Integer, Primary Key): ID único del técnico
- `nombre` (String(100), Not Null): Nombre del técnico
- `apellido` (String(100), Not Null): Apellido del técnico
- `especialidad` (String(100)): Especialidad técnica
- `telefono` (String(0)): Número de teléfono
- `email` (String(00)): Correo electrónico
- `estado` (String(0)): Estado actual del técnico
- `fecha_ingreso` (Date): Fecha de ingreso al equipo

### Campos Adicionales
- `codigo_empleado`: Código único de empleado
- `cargo`: Cargo o posición
- `departamento`: Departamento de trabajo
- `nivel_experiencia`: Nivel de experiencia
- `certificaciones`: Certificaciones técnicas (JSON)
- `habilidades`: Habilidades técnicas (JSON)
- `disponibilidad_horario`: Horario de disponibilidad (JSON)
- `ubicacion_asignada`: Ubicación de trabajo asignada
- `supervisor_id`: ID del supervisor directo

### Métricas de Rendimiento
- `evaluaciones_desempeno`: Evaluaciones de desempeño (JSON)
- `horas_trabajadas_mes`: Horas trabajadas en el mes
- `promedio_tiempo_resolucion`: Promedio de tiempo de resolución
- `total_fallas_asignadas`: Total de fallas asignadas
- `total_mantenimientos_asignados`: Total de mantenimientos asignados

## Estados del Técnico

```python
class TecnicoStatus(enum.Enum):
ACTIVO = "activo"
INACTIVO = "inactivo"
DISPONIBLE = "disponible"
OCUPADO = "ocupado"
VACACIONES = "vacaciones"
LICENCIA = "licencia"
```

## Relaciones

### Relaciones con Fallas
```python
# Campo en Falla
assigned_to = Column(Integer, ForeignKey('equipo_tecnico.id'))

# Relación en EquipoTecnico
fallas_asignadas = relationship("Falla", back_populates="tecnico_asignado_obj")
```

### Relaciones con Mantenimientos
```python
# Campo en Mantenimiento
technician_id = Column(Integer, ForeignKey('equipo_tecnico.id'))

# Relación en EquipoTecnico
mantenimientos_asignados = relationship("Mantenimiento", back_populates="tecnico_asignado_obj")
```

### Relaciones con Fotografías
```python
# Campo en Fotografia
tecnico_responsable = Column(Integer, ForeignKey('equipo_tecnico.id'))

# Relación en EquipoTecnico
fotografias_subidas = relationship("Fotografia", back_populates="tecnico_responsable")
```

## Métodos Principales

### Gestión de Estado
```python
# Activar/desactivar técnico
tecnico.activate()
tecnico.deactivate()

# Cambiar disponibilidad
tecnico.set_available()
tecnico.set_busy()

# Verificar disponibilidad
tecnico.is_available() # Retorna bool
```

### Información del Técnico
```python
# Obtener nombre completo
nombre_completo = tecnico.get_nombre_completo()

# Obtener iniciales
iniciales = tecnico.get_iniciales()

# Consultar especialidades
especialidades = tecnico.get_specialties()

# Verificar habilidad específica
tiene_habilidad = tecnico.has_skill("camaras_ip")
nivel_habilidad = tecnico.get_skill_level("camaras_ip")
```

### Carga de Trabajo
```python
# Obtener carga de trabajo actual
workload = tecnico.get_workload()
# Retorna: {
# 'fallas_activas': int,
# 'mantenimientos_activos': int,
# 'total_asignaciones': int
# }
```

### Métricas de Rendimiento
```python
# Obtener métricas de desempeño
metrics = tecnico.get_performance_metrics()
# Retorna: {
# 'total_fallas': int,
# 'fallas_resueltas': int,
# 'tasa_resolucion_fallas': float,
# 'total_mantenimientos': int,
# 'mantenimientos_completados': int,
# 'tasa_completado_mantenimientos': float,
# 'promedio_tiempo_resolucion': int
# }
```

### Asignación de Tareas
```python
# Asignar falla
tecnico.assign_falla(falla_id)

# Asignar mantenimiento
tecnico.assign_mantenimiento(mantenimiento_id)
```

### Gestión de Habilidades
```python
# Añadir habilidad
tecnico.add_skill("camaras_ip", level=5)

# Añadir certificación
tecnico.add_certification("Certificación IP", date_obtained=date(04, 1, 1))
```

### Actualización de Datos
```python
# Actualizar última actividad
tecnico.update_last_activity()

# Actualizar métricas de rendimiento
tecnico.update_performance_metrics()
```

## Métodos de Clase

### Consultas Básicas
```python
# Obtener técnicos activos
activos = EquipoTecnico.get_active_technicians()

# Obtener técnicos disponibles
disponibles = EquipoTecnico.get_available_technicians()

# Buscar por especialidad
especialistas = EquipoTecnico.get_by_specialty("Red")

# Buscar por carga de trabajo
baja_carga = EquipoTecnico.get_by_workload(max_assignments=5)

# Buscar con bajo rendimiento
bajo_rendimiento = EquipoTecnico.get_with_low_performance(min_completion_rate=70.0)
```

### Búsqueda Avanzada
```python
# Búsqueda por nombre, apellido o email
resultados = EquipoTecnico.search("Juan")

# Búsqueda con filtro de especialidad
resultados = EquipoTecnico.search("María", specialty="Red")
```

## Exportación de Datos

### Convertir a Diccionario
```python
# Obtener datos completos incluyendo relaciones
datos_completos = tecnico.to_dict()
# Incluye: campos básicos, datos calculados, relaciones activas
```

## Ejemplo de Uso Completo

```python
from datetime import date
from models import db, EquipoTecnico, TecnicoStatus

# Crear técnico
tecnico = EquipoTecnico(
nombre="Juan",
apellido="Pérez",
especialidad="Cámaras de Seguridad",
telefono="+5691345678",
<<<<<<< HEAD
email="juan.perez@ufro.cl",
=======
email="juan.perez@ufrontera.cl",
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
estado=TecnicoStatus.ACTIVO.value,
fecha_ingreso=date(03, 1, 15)
)

# Añadir habilidades
tecnico.add_skill("camaras_ip", 5)
tecnico.add_skill("nvr", 4)

# Añadir certificación
tecnico.add_certification("Certificación en Cámaras IP")

# Guardar en base de datos
db.session.add(tecnico)
db.session.commit()

# Consultar disponibilidad
if tecnico.is_available():
# Asignar falla
tecnico.assign_falla(falla_id)

# Obtener carga de trabajo
workload = tecnico.get_workload()
print(f"Fallas activas: {workload['fallas_activas']}")

# Obtener métricas
metrics = tecnico.get_performance_metrics()
print(f"Tasa resolución: {metrics['tasa_resolucion_fallas']}%")

# Buscar técnicos similares
especialistas = EquipoTecnico.get_by_speciality("Cámaras")
disponibles = EquipoTecnico.get_available_technicians()
```

## Archivos Creados/Modificados

1. **Creados:**
- `/workspace/models/equipo_tecnico.py` - Modelo principal (406 líneas)
- `/workspace/models/ejemplo_equipo_tecnico.py` - Script de ejemplo (57 líneas)
- `/workspace/models/README_EQUIPO_TECNICO.md` - Esta documentación

. **Modificados:**
- `/workspace/models/__init__.py` - Añadido import y export del modelo
- `/workspace/models/falla.py` - Añadida relación bidireccional
- `/workspace/models/mantenimiento.py` - Añadida relación bidireccional
- `/workspace/models/fotografia.py` - Añadida relación con técnico responsable

## Compatibilidad

- Compatible con estructura de Railway
- Mapeo correcto PostgreSQL → SQLAlchemy
- Hereda de BaseModel para funcionalidad común
- Campos en español como se solicitó
- Métodos to_dict() y __repr__() incluidos
- Relaciones bidireccionales con fallas y mantenimientos
- Enums para estados y tipos
- JSON fields para datos flexibles
- Métodos de consulta avanzados
- Cálculo de métricas y rendimiento

## Validación

El modelo ha sido creado siguiendo exactamente las especificaciones:
- 8 columnas principales de Railway
- Import necesarios incluidos
- Basado en BaseModel
- Campos en español
- Métodos to_dict() y __repr__()
- Relaciones con fallas y mantenimientos
- Mapeo correcto de tipos PostgreSQL → SQLAlchemy

El script de ejemplo demuestra todas las funcionalidades y sirve como documentación práctica del uso del modelo.