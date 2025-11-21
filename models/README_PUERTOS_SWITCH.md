# Modelo PuertoSwitch

## Descripción

El modelo `PuertoSwitch` representa los puertos individuales de cada switch de red en el sistema. Cada puerto tiene su propia configuración, estado y relaciones, permitiendo un control granular sobre la infraestructura de red.

## Características

- **15 columnas**: Estructura completa con todos los campos necesarios
- **Foreign Key**: Relación con el modelo Switch
- **Relaciones bidireccionales**: Navegación desde Switch hacia puertos y viceversa
- **Validaciones**: Métodos de validación para MAC, VLAN y número de puerto
- **Métodos de utilidad**: Funciones para obtener estado visual, validar conexiones, etc.

## Estructura de la Tabla

| Campo | Tipo | Descripción | Nullable |
|-------|------|-------------|----------|
| id | Integer | Clave primaria | No |
| created_at | DateTime | Fecha de creación | No |
| updated_at | DateTime | Fecha de actualización | No |
| deleted | Boolean | Soft delete | No |
| created_by | Integer | Usuario creador | Sí |
| updated_by | Integer | Usuario actualizador | Sí |
| **switch_id** | Integer | **FK a switches.id** | **No** |
| numero_puerto | Integer | Número del puerto (1-5) | No |
| nombre_puerto | String(100) | Nombre descriptivo | Sí |
| tipo_puerto | String(50) | Tipo (Ethernet, SFP, SFP+) | Sí |
| velocidad_puerto | String(0) | Velocidad (10Mbps-10Gbps) | Sí |
| estado_puerto | String(50) | Estado (Activo, Inactivo, etc.) | Sí |
| vlan_asignada | Integer | VLAN asignada (1-4094) | Sí |
| descripcion | Text | Descripción del puerto | Sí |
| conecta_a | String(00) | Dispositivo conectado | Sí |
| poe_habilitado | Boolean | Si tiene PoE habilitado | No |
| potencia_maxima_poe | Float | Potencia PoE máxima (W) | Sí |
| duplex | String(0) | Modo duplex | Sí |
| mac_address | String(17) | Dirección MAC | Sí |
| fecha_ultimo_mantenimiento | Date | Fecha mantenimiento | Sí |
| ultima_conexion | DateTime | Última detección | Sí |
| observaciones | Text | Observaciones adicionales | Sí |

## Relaciones

### Con Switch (One-to-Many)
```python
# Desde Switch hacia PuertoSwitch
switch = Switch.query.get(switch_id)
puertos = switch.puertos # Lista de puertos del switch

# Desde PuertoSwitch hacia Switch
puerto = PuertoSwitch.query.get(puerto_id)
switch = puerto.switch # Switch al que pertenece
```

## Métodos Principales

### Métodos de Validación
- `validate_numero_puerto()`: Valida rango 1-5
- `validate_mac_address()`: Valida formato MAC (XX:XX:XX:XX:XX:XX)
- `validate_vlan()`: Valida rango VLAN 1-4094

### Métodos de Estado
- `is_activo()`: Retorna True si el puerto está activo
- `is_poe_disponible()`: Retorna True si PoE está habilitado y disponible
- `get_estado_visual()`: Retorna estado con emojis para UI

### Métodos de Información
- `get_puerto_completo()`: Retorna string completo del puerto
- `update_ultima_conexion()`: Actualiza timestamp de última conexión

### Métodos de Consulta Estática
- `get_by_switch(switch_id)`: Puertos de un switch específico
- `get_activos()`: Todos los puertos activos del sistema
- `get_por_vlan(vlan)`: Puertos asignados a una VLAN específica

## Ejemplos de Uso

### Crear un Puerto
```python
from models import PuertoSwitch, Switch

# Obtener switch
switch = Switch.query.filter_by(codigo="SW-001").first()

# Crear puerto
puerto = PuertoSwitch(
switch_id=switch.id,
numero_puerto=1,
nombre_puerto="Uplink Principal",
tipo_puerto="SFP+",
velocidad_puerto="10Gbps",
estado_puerto="Activo",
vlan_asignada=100,
poe_habilitado=False,
duplex="Full",
mac_address="AA:BB:CC:DD:EE:01"
)

# Guardar con validaciones
puerto.save(user_id=1)
```

### Consultar Puertos
```python
# Puertos de un switch específico
switch = Switch.query.get(1)
for puerto in switch.puertos:
print(f"Puerto {puerto.numero_puerto}: {puerto.get_puerto_completo()}")

# Puertos activos
puertos_activos = PuertoSwitch.get_activos()

# Puertos por VLAN
puertos_vlan_00 = PuertoSwitch.get_por_vlan(00)

# Verificar estado
puerto = PuertoSwitch.query.get(1)
if puerto.is_activo():
print(f"Puerto {puerto.numero_puerto} está activo")
print(f"Estado visual: {puerto.get_estado_visual()}")
```

### Actualizar Puerto
```python
puerto = PuertoSwitch.query.get(1)

# Cambiar estado
puerto.estado_puerto = "Mantenimiento"
puerto.observaciones = "Mantenimiento programado"

# Actualizar última conexión
puerto.update_ultima_conexion()

# Guardar
puerto.save(user_id=1)
```

### Validaciones
```python
# El método save() ejecuta validaciones automáticamente
try:
puerto = PuertoSwitch(
switch_id=1,
numero_puerto=99, # Inválido
mac_address="invalid-format", # Inválido
vlan_asignada=5000 # Inválido
)
puerto.save()
except ValueError as e:
print(f"Error de validación: {e}")
```

## Estados Predefinidos

### Estados de Puerto
- **Activo/Up/Conectado**: Puerto funcionando
- **Inactivo/Down/Desconectado**: Sin conexión
- **Fallo/Error/Fault**: Problema detectado
- **Mantenimiento/Maintenance**: En mantenimiento

### Tipos de Puerto
- **Ethernet**: Puerto RJ45 estándar
- **SFP**: Small Form-Factor Pluggable (1Gbps)
- **SFP+**: SFP Plus (10Gbps)

### Velocidades de Puerto
- 10Mbps
- 100Mbps
- 1Gbps
- 10Gbps

### Modos Duplex
- **Auto**: Negociación automática
- **Full**: Dúplex completo
- **Half**: Dúplex medio

## Integración con Frontend

El modelo está diseñado para integrarse fácilmente con interfaces web:

```javascript
// Ejemplo de uso en templates Flask
{% for puerto in switch.puertos %}
<div class="puerto-card">
<h4>Puerto {{ puerto.numero_puerto }}</h4>
<p>Estado: {{ puerto.get_estado_visual() }}</p>
<p>VLAN: {{ puerto.vlan_asignada or 'Sin asignar' }}</p>
{% if puerto.is_poe_disponible() %}
<span class="badge badge-success">PoE {{ puerto.potencia_maxima_poe }}W</span>
{% endif %}
</div>
{% endfor %}
```

## Migración a Railway

Para usar este modelo en Railway, asegúrate de:

1. Importar el modelo en el archivo principal:
```python
from models.puertos_switch import PuertoSwitch
```

. Crear la tabla en la base de datos:
```python
with app.app_context():
db.create_all()
```

3. Ejecutar las migraciones necesarias para crear la tabla `puertos_switch`.

## Consideraciones de Rendimiento

- Los campos `switch_id`, `numero_puerto` e `id` están indexados automáticamente
- Las consultas por `switch_id` son eficientes gracias a la relación FK
- Se recomienda paginar consultas con muchos resultados
- El método `get_estado_visual()` genera strings optimizados para UI

## Troubleshooting

### Error de Foreign Key
```
sqlalchemy.exc.IntegrityError: (psycopg.errors.ForeignKeyViolation)
```
**Solución**: Verificar que el `switch_id` exista en la tabla `switches`.

### Error de Validación
```
ValueError: Número de puerto inválido: X
```
**Solución**: El número de puerto debe estar entre 1 y 5.

### Error de MAC Inválida
```
ValueError: Dirección MAC inválida: XX:XX:XX:XX:XX:XX
```
**Solución**: Usar formato correcto: `AA:BB:CC:DD:EE:FF` o `AA-BB-CC-DD-EE-FF`.