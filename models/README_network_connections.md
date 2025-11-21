# Modelo Network Connections

## Descripción

El modelo `NetworkConnection` proporciona una solución completa para gestionar las conexiones de red entre equipos en el sistema de gestión de infraestructura tecnológica.

## Características Principales

### Conexiones Flexibles
- Conecta cualquier tipo de equipo con cualquier otro
- Soporte para múltiples tipos de conexión (Ethernet, Fibra Óptica, PoE, etc.)
- Validación automática de compatibilidad

### Métricas de Rendimiento
- Ancho de banda en Mbps
- Latencia en milisegundos
- Pérdida de paquetes en porcentaje
- Calidad de conexión automática

### Topología de Red
- Generación automática de topología
- Rutas de conexión completas
- Visualización de relaciones entre equipos

### Índices Optimizados
- Búsquedas rápidas por equipo
- Consultas eficientes por tipo de conexión
- Análisis de rendimiento optimizado

## Tipos de Conexión Soportados

```python
from models.network_connections import ConnectionType

# Tipos disponibles
ConnectionType.ETHERNET # Conexión Ethernet estándar
ConnectionType.FIBRA_OPTICA # Fibra óptica
ConnectionType.WIRELESS # Conexión inalámbrica
ConnectionType.SERIAL # Conexión serial
ConnectionType.USB # Conexión USB
ConnectionType.POWER_OVER_ETHERNET # PoE
ConnectionType.INALAMBRICO # Inalámbrico
ConnectionType.UTP # Cable UTP
ConnectionType.STP # Cable STP
```

## Tipos de Cable Soportados

```python
from models.network_connections import CableType

# Cables de red
CableType.CAT5E # Cat5e
CableType.CAT6 # Cat6
CableType.CAT6A # Cat6a
CableType.CAT7 # Cat7

# Fibra óptica
CableType.FIBRA_MONOMODO # Fibra monomodo
CableType.FIBRA_MULTIMODO # Fibra multimodo

# Otros cables
CableType.COAXIAL # Coaxial
CableType.USB__0 # USB .0
CableType.USB_3_0 # USB 3.0
CableType.RS3 # RS3
CableType.RS485 # RS485
```

## Uso Básico

### Crear una Conexión

```python
from models.network_connections import NetworkConnection, ConnectionType, CableType
from models.equipo import Equipo

# Obtener equipos
switch = Equipo.query.get(1)
nvr = Equipo.query.get()

# Crear conexión
conexion = NetworkConnection.crear_conexion(
equipo_origen_id=switch.id,
equipo_destino_id=nvr.id,
tipo_conexion=ConnectionType.ETHERNET,
equipo_origen_tipo="equipo",
equipo_destino_tipo="equipo",
ancho_banda=1000.0, # 1 Gbps
latencia=.5, # .5 ms
tipo_cable=CableType.CAT6,
longitud_cable=15.0, # 15 metros
puerto_origen="GigabitEthernet0/1",
puerto_destino="LAN1",
vlan_id=100,
descripcion="Conexión principal Switch-NVR"
)

# Guardar en base de datos
conexion.guardar()
```

### Validar Conexiones

```python
# Validar antes de guardar
errores = conexion.validar_conexion()
if errores:
print("Errores encontrados:", errores)
else:
print("Conexión válida")

# O verificar directamente
if conexion.es_conexion_valida():
print("La conexión es válida")
```

### Consultar Conexiones

```python
# Obtener todas las conexiones de un equipo
conexiones = NetworkConnection.obtener_conexiones_por_equipo(equipo_id=1)

# Obtener todas las conexiones activas
conexiones_activas = NetworkConnection.get_active_connections()

# Consultas personalizadas
from models import db

# Conexiones de alta velocidad
alta_velocidad = NetworkConnection.query.filter(
NetworkConnection.ancho_banda > 500,
NetworkConnection.deleted == False
).all()

# Conexiones por tipo
ethernet = NetworkConnection.query.filter_by(
tipo_conexion=ConnectionType.ETHERNET,
deleted=False
).all()
```

### Topología de Red

```python
# Obtener topología completa
topologia = NetworkConnection.obtener_topologia_red()

for equipo_id, info in topologia.items():
print(f"Equipo: {info['equipo_tipo']}#{info['equipo_id']}")
for conexion in info['conexiones']:
print(f" → {conexion['equipo_destino_tipo']}#{conexion['equipo_destino_id']}")
```

### Métricas de Rendimiento

```python
# Velocidad de conexión
velocidad = conexion.obtener_velocidad_conexion()
print(f"Velocidad: {velocidad}") # "1.0 Gbps"

# Calidad de conexión
calidad = conexion.obtener_calidad_conexion()
print(f"Calidad: {calidad}") # "Buena", "Regular", "Mala", "Inactiva"

# Ruta completa
ruta = conexion.obtener_ruta_completa()
print(f"Ruta: {' → '.join(ruta)}") # "equipo#1 → equipo#"
```

## Estructura de Base de Datos

### Campos Principales

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | Clave primaria |
| `equipo_origen_id` | Integer | ID del equipo origen (FK a equipos) |
| `equipo_destino_id` | Integer | ID del equipo destino (FK a equipos) |
| `tipo_conexion` | Enum | Tipo de conexión |
| `ancho_banda` | Float | Ancho de banda en Mbps |
| `latencia` | Float | Latencia en milisegundos |
| `activa` | Boolean | Si la conexión está activa |
| `created_at` | DateTime | Fecha de creación |
| `updated_at` | DateTime | Fecha de última actualización |

### Índices Creados

- `idx_network_connections_equipo_origen` - Búsquedas por equipo origen
- `idx_network_connections_equipo_destino` - Búsquedas por equipo destino
- `idx_network_connections_tipo_conexion` - Filtros por tipo
- `idx_network_connections_activa` - Conexiones activas
- `idx_network_connections_topologia` - Análisis de topología
- `idx_network_connections_rendimiento` - Métricas de rendimiento

### Restricciones

- **CheckConstraint**: Ancho de banda > 0
- **CheckConstraint**: Latencia >= 0
- **CheckConstraint**: Pérdida de paquetes entre 0-100%
- **CheckConstraint**: No auto-conexión (equipo_origen_id = equipo_destino_id)
- **UniqueConstraint**: No conexiones duplicadas

## Relaciones

### Con Equipo

```python
class Equipo(EquipmentBase):
# Relaciones bidireccionales
conexiones_origen = relationship(
"NetworkConnection",
foreign_keys="NetworkConnection.equipo_origen_id",
back_populates="equipo_origen"
)

conexiones_destino = relationship(
"NetworkConnection",
foreign_keys="NetworkConnection.equipo_destino_id",
back_populates="equipo_destino"
)
```

## Ejemplo Completo

Ver el archivo `ejemplo_network_connections.py` para un ejemplo completo de uso que incluye:

1. Creación de equipos de prueba
. Establecimiento de conexiones
3. Validación automática
4. Consultas de topología
5. Análisis de rendimiento
6. Manejo de errores

## Migración

Para usar el modelo en una base de datos existente:

```python
# Crear las tablas
from models import db
with app.app_context():
db.create_all()
```

## Consideraciones de Rendimiento

1. **Índices**: Los índices están optimizados para consultas comunes
. **Lazy Loading**: Las relaciones usan `lazy="joined"` para minimizar consultas
3. **Validación**: La validación ocurre antes de guardar para evitar errores de BD
4. **Cascada**: Las eliminaciones en cascada mantienen la integridad referencial

## Extensibilidad

El modelo está diseñado para ser extensible:

- Fácil agregar nuevos tipos de conexión
- Campos adicionales para configuraciones específicas
- Métodos personalizables para métricas de rendimiento
- Soporte para múltiples protocolos de red

## Troubleshooting

### Error: "No module named 'models.equipo'"
```python
# Asegúrate de que las importaciones estén correctas
from models.equipo import Equipo
from models.network_connections import NetworkConnection
```

### Error: "relation 'equipos' does not exist"
```python
# Crear las tablas primero
with app.app_context():
db.create_all()
```

### Validación Falla
```python
# Revisar errores específicos
errores = conexion.validar_conexion()
for error in errores:
print(f"Error: {error}")
```

## Changelog

### v1.0.0
- Implementación inicial del modelo NetworkConnection
- Soporte para múltiples tipos de conexión
- Sistema de validación completo
- Índices optimizados para rendimiento
- Relaciones bidireccionales con equipos
- Generación automática de topología