# Modelo CatalogoTipoFalla

## Descripción

El modelo `CatalogoTipoFalla` proporciona una estructura completa para gestionar el catálogo de tipos de fallas del sistema de gestión de infraestructura tecnológica. Permite clasificar, categorizar y gestionar información sobre los diferentes tipos de fallas que pueden ocurrir en el sistema.

## Estructura

### Tabla: `catalogo_tipo_falla`

| Campo | Tipo | Nullable | Descripción |
|-------|------|----------|-------------|
| id | INTEGER | NO | Clave primaria |
| nombre | VARCHAR(100) | NO | Nombre único del tipo de falla |
| categoria | VARCHAR(50) | SÍ | Categoría de la falla |
| descripcion | TEXT | SÍ | Descripción detallada |
| gravedad | VARCHAR(0) | SÍ | Nivel de gravedad |
| tiempo_estimado_resolucion | INTEGER | SÍ | Tiempo estimado en minutos |

## Enumeraciones

### CategoriaFalla
Categorías estándar para tipos de fallas:

```python
from models import CategoriaFalla

# Valores disponibles
CategoriaFalla.HARDWARE # "hardware"
CategoriaFalla.SOFTWARE # "software"
CategoriaFalla.CONECTIVIDAD # "conectividad"
CategoriaFalla.ALIMENTACION # "alimentacion"
CategoriaFalla.SISTEMA # "sistema"
CategoriaFalla.CONFIGURACION # "configuracion"
CategoriaFalla.MANTENIMIENTO # "mantenimiento"
CategoriaFalla.SEGURIDAD # "seguridad"
CategoriaFalla.RENDIMIENTO # "rendimiento"
CategoriaFalla.DISPONIBILIDAD # "disponibilidad"
```

### GravedadFalla
Niveles de gravedad para tipos de fallas:

```python
from models import GravedadFalla

# Valores disponibles
GravedadFalla.CRITICA # "critica"
GravedadFalla.ALTA # "alta"
GravedadFalla.MEDIA # "media"
GravedadFalla.BAJA # "baja"
GravedadFalla.INFORMATIVA # "informativa"
```

## Uso Básico

### Importación

```python
from models import db, CatalogoTipoFalla, CategoriaFalla, GravedadFalla
```

### Crear un Tipo de Falla

```python
# Método 1: Creación directa
tipo_falla = CatalogoTipoFalla(
nombre="Falla de Cámara",
categoria=CategoriaFalla.HARDWARE,
descripcion="La cámara no transmite imagen",
gravedad=GravedadFalla.MEDIA,
tiempo_estimado_resolucion=90
)
tipo_falla.save()

# Método : Usando método helper
tipo_falla = CatalogoTipoFalla.create_tipo_falla(
nombre="Problema de Red",
categoria=CategoriaFalla.CONECTIVIDAD,
descripcion="Conectividad intermitente",
gravedad=GravedadFalla.ALTA,
tiempo_estimado_resolucion=10
)
```

### Consultar Tipos de Falla

```python
# Obtener todos los tipos
todos_tipos = CatalogoTipoFalla.query.all()

# Por categoría
tipos_hardware = CatalogoTipoFalla.get_by_categoria(CategoriaFalla.HARDWARE)

# Por gravedad
tipos_criticos = CatalogoTipoFalla.get_by_gravedad(GravedadFalla.CRITICA)

# Búsqueda por nombre
resultados = CatalogoTipoFalla.search_by_nombre("cámara")
```

### Métodos de Utilidad

```python
tipo_falla = CatalogoTipoFalla.query.first()

# Métodos de visualización
nombre_display = tipo_falla.get_display_name() # "Falla de Cámara (hardware)"
categoria_legible = tipo_falla.get_categoria_display() # "Hardware"
gravedad_legible = tipo_falla.get_gravedad_display() # "Media"

# Métodos de tiempo
tiempo_horas = tipo_falla.get_tiempo_estimado_horas() # 1.5
valor_numerico = tipo_falla.get_numeric_gravedad() # 3

# Validaciones
es_valido = tipo_falla.is_valid_categoria() # True
es_valido = tipo_falla.is_valid_gravedad() # True
```

### Estadísticas y Reportes

```python
# Obtener tipos con conteo de fallas
tipos_con_conteo = CatalogoTipoFalla.get_with_fallas_count()

# Tipos más frecuentes
frecuentes = CatalogoTipoFalla.get_most_frequent_tipos(limit=5)

# Estadísticas por categoría
stats = CatalogoTipoFalla.get_estadisticas_categoria()
# {'hardware': {'total_tipos': 5, 'tiempo_promedio': 85.5}, ...}

# Listas de opciones
categorias_disponibles = CatalogoTipoFalla.get_categorias_disponibles()
gravedades_disponibles = CatalogoTipoFalla.get_gravedades_disponibles()
```

## Relaciones

### Con el Modelo Falla

El modelo `CatalogoTipoFalla` se relaciona con `Falla` mediante:

```python
# En el modelo Falla
tipo_falla_id = Column(Integer, ForeignKey('catalogo_tipo_falla.id'))
tipo_falla = relationship("CatalogoTipoFalla", back_populates="fallas")

# En el modelo CatalogoTipoFalla
fallas = relationship("Falla", back_populates="tipo_falla")
```

### Usar la Relación

```python
# Obtener fallas de un tipo específico
tipo_falla = CatalogoTipoFalla.query.first()
fallas_del_tipo = tipo_falla.fallas

# Obtener el tipo desde una falla
falla = Falla.query.first()
if falla.tipo_falla:
nombre_tipo = falla.tipo_falla.nombre
categoria_tipo = falla.tipo_falla.categoria
```

## Serialización

```python
# Diccionario básico
data = tipo_falla.to_dict()

# Con relaciones incluidas
data_completa = tipo_falla.to_dict(include_relations=True)

# Salida ejemplo:
# {
# 'id': 1,
# 'nombre': 'Falla de Cámara',
# 'categoria': 'hardware',
# 'descripcion': 'La cámara no transmite imagen',
# 'gravedad': 'media',
# 'tiempo_estimado_resolucion': 90,
# 'created_at': '05-11-14T11:1:18',
# 'updated_at': '05-11-14T11:1:18',
# 'deleted': False
# }
```

## Índices

Se crean automáticamente los siguientes índices para optimizar consultas:

- `idx_catalogo_tipo_falla_nombre` - Búsquedas por nombre
- `idx_catalogo_tipo_falla_categoria` - Filtros por categoría
- `idx_catalogo_tipo_falla_gravedad` - Filtros por gravedad
- `idx_catalogo_tipo_falla_composite` - Filtros combinados por categoría y gravedad

## Ejemplo Completo

```python
from models import db, CatalogoTipoFalla, CategoriaFalla, GravedadFalla, Falla

# Crear tipos de falla
hardware = CatalogoTipoFalla.create_tipo_falla(
nombre="Falla de Cámara",
categoria=CategoriaFalla.HARDWARE,
descripcion="La cámara no transmite imagen",
gravedad=GravedadFalla.MEDIA,
tiempo_estimado_resolucion=90
)

software = CatalogoTipoFalla.create_tipo_falla(
nombre="Error de Software",
categoria=CategoriaFalla.SOFTWARE,
descripcion="Error en el software del NVR",
gravedad=GravedadFalla.ALTA,
tiempo_estimado_resolucion=60
)

# Crear una falla y asignarle el tipo
falla = Falla(
title="Cámara principal sin señal",
descripcion="La cámara del pasillo principal no transmite",
tipo_falla_id=hardware.id
)
falla.save()

# Consultar fallas por tipo
fallas_hardware = Falla.query.join(CatalogoTipoFalla).filter(
CatalogoTipoFalla.categoria == CategoriaFalla.HARDWARE
).all()

# Obtener estadísticas
stats = CatalogoTipoFalla.get_estadisticas_categoria()
print(f"Tipos de hardware: {stats.get('hardware', {}).get('total_tipos', 0)}")
```

## Notas de Implementación

1. **Validaciones**: El modelo valida automáticamente que las categorías y gravedades estén en las listas de valores válidos.

. **Soft Delete**: Utiliza el campo `deleted` inherited de `BaseModel` para eliminación lógica.

3. **Timestamps**: Mantiene `created_at` y `updated_at` automáticamente.

4. **Relaciones**: Implementa `back_populates` para mantener consistencia en las relaciones bidireccionales.

5. **Índices**: Se crean automáticamente para optimizar consultas frecuentes.

6. **Métodos de Clase**: Proporciona métodos de clase para consultas complejas y reportes.

Este modelo está diseñado para ser flexible y extensible, permitiendo agregar nuevos tipos de fallas sin modificar la estructura de base de datos existente.
