# Modelos SQLAlchemy - Sistema de Gestión de Infraestructura

## Descripción

Este paquete contiene modelos SQLAlchemy completos para un sistema de gestión de infraestructura tecnológica. Los modelos incluyen gestión de usuarios, ubicaciones, equipos de red, cámaras, fallas, mantenimientos y fotografías.

## Estructura de Modelos

### Modelos Principales

#### 1. **Usuario** (`usuario.py`)
- **Usuario**: Gestión de usuarios del sistema con roles y autenticación
- **UsuarioLog**: Log de actividad de usuarios
- **UsuarioRol**: Configuración de roles del sistema

**Características:**
- Sistema de roles (administrador, técnico, operador, visualizador)
- Bloqueo por intentos fallidos
- Tracking de actividad
- Gestión de contraseñas con hash seguro

#### . **Ubicacion** (`ubicacion.py`)
- **Ubicacion**: Gestión jerárquica de ubicaciones geográficas
- **UbicacionLog**: Log de cambios en ubicaciones

**Características:**
- Coordenadas GPS (latitud, longitud, altitud)
- Estructura jerárquica (padre-hijo)
- Cálculo de distancias
- Búsqueda por proximidad

#### 3. **Camara** (`camara.py`)
- **Camara**: Cámaras de seguridad con configuración completa
- **CamaraLog**: Log de actividad de cámaras

**Características:**
- Tipos de cámara (fija, PTZ, domo, bullet, etc.)
- Configuración de red (IP, puerto, protocolos)
- Monitoreo de estado y heartbeat
- Integración con NVR/DVR

#### 4. **Falla** (`falla.py`)
- **Falla**: Gestión de fallas con seguimiento completo
- **FallaHistorial**: Historial de cambios en fallas

**Características:**
- Tipos de falla (hardware, software, conectividad, etc.)
- Sistema de prioridades y escalamiento
- Asignación a técnicos
- Tracking de tiempos de resolución

#### 5. **Mantenimiento** (`mantenimiento.py`)
- **Mantenimiento**: Mantenimientos preventivos y correctivos
- **MantenimientoHistorial**: Historial de mantenimientos

**Características:**
- Tipos de mantenimiento (preventivo, correctivo, predictivo)
- Programación y seguimiento
- Gestión de costos
- Órdenes de trabajo

### Modelos de Equipos

#### 6. **NVR** (`nvr.py`)
- **NVR**: Network Video Recorder
- **NVRCameraChannel**: Configuración de canales

**Características:**
- Soporte para múltiples cámaras
- Gestión de almacenamiento
- Configuración de grabación
- Monitoreo de salud del sistema

#### 7. **Switch** (`switch.py`)
- **Switch**: Switches de red
- **SwitchPort**: Puertos de switch
- **SwitchVLAN**: Configuración de VLANs

**Características:**
- Gestión de puertos y conexiones
- Configuración de VLANs
- Monitoreo de utilización
- Soporte para stacking

#### 8. **UPS** (`ups.py`)
- **UPS**: Sistemas de alimentación ininterrumpida
- **UPSConnectedLoad**: Cargas conectadas

**Características:**
- Monitoreo de baterías
- Gestión de carga
- Cálculo de autonomía
- Alertas de mantenimiento

#### 9. **FuentePoder** (`fuente_poder.py`)
- **FuentePoder**: Fuentes de alimentación
- **FuentePoderConnection**: Conexiones de equipos

**Características:**
- Gestión de potencia y eficiencia
- Monitoreo térmico
- Control de carga
- Certificaciones de eficiencia

#### 10. **Gabinete** (`gabinete.py`)
- **Gabinete**: Racks y gabinetes de red
- **GabineteEquipment**: Equipos instalados

**Características:**
- Gestión de unidades de rack
- Monitoreo ambiental
- Control de acceso
- Organización física de equipos

#### 11. **Equipo Base** (`equipo.py`)
- **EquipmentBase**: Clase base para todos los equipos
- **NetworkConnection**: Conexiones de red entre equipos

**Características:**
- Campos comunes para todos los equipos
- Sistema de conexiones de red
- Monitoreo de estado y heartbeat
- Gestión de ubicación y configuración

### Modelos de Documentación

#### 1. **Fotografia** (`fotografia.py`)
- **Fotografia**: Gestión de imágenes y documentación
- **FotografiaMetadata**: Metadatos adicionales

**Características:**
- Múltiples formatos de imagen
- Análisis automático de calidad
- Gestión de versiones
- Tags y metadatos EXIF

### Clases Base y Utilidades

#### 13. **Base** (`base.py`)
- **BaseModel**: Clase base con funcionalidades comunes
- Soft delete y timestamps automáticos
- Métodos de utilidad para consultas

#### 14. **Configuración** (`__init__.py`)
- Configuración de base de datos
- Tipos enum comunes
- Funciones de inicialización

## Características Técnicas

### Funcionalidades Implementadas

1. **Timestamps Automáticos**
- `created_at`, `updated_at` en todos los modelos
- Soft delete con campo `deleted`

. **Relaciones Completas**
- Foreign keys apropiadas
- Relaciones bidireccionales
- Cascade delete donde corresponde

3. **Validaciones y Constraints**
- Campos únicos (username, email, serial numbers)
- Campos requeridos
- Índices para búsquedas frecuentes

4. **Enumeraciones**
- Estados de equipos y fallas
- Tipos de equipos y conexiones
- Prioridades y categorías

5. **Métodos de Utilidad**
- Cálculos automáticos (distancias, duraciones, costos)
- Búsquedas por criterios específicos
- Resúmenes y estadísticas

6. **Monitoreo y Logging**
- Campos para heartbeat y estado
- Logs de cambios en modelos críticos
- Métricas de rendimiento

### Consultas Implementadas

- **Búsquedas por ubicación geográfica**
- **Filtros por estado y tipo**
- **Consultas jerárquicas (padre-hijo)**
- **Agregaciones y resúmenes**
- **Consultas de tiempo real (heartbeats)**

## Instalación y Uso

### 1. Configuración

```python
from flask import Flask
from models import init_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:pass@localhost/dbname'

# Inicializar base de datos
init_db(app)
```

### . Crear Modelos

```python
from models import Usuario, Camara, NVR

# Crear usuario
usuario = Usuario(
username="admin",
email="admin@ejemplo.com",
full_name="Administrador",
role="administrador"
)
usuario.set_password("password13")
usuario.save()

# Crear NVR
nvr = NVR(
name="NVR-001",
model="Hikvision DS-773NIX",
ip_address="19.168.1.10",
ubicacion_id=1
)
nvr.save()

# Crear cámara
camara = Camara(
name="Camara Entrada",
model="Hikvision DS-CD145FWD-I",
ip_address="19.168.1.101",
nvr_id=nvr.id,
ubicacion_id=1
)
camara.save()
```

### 3. Consultas

```python
# Obtener cámaras por ubicación
camaras = Camara.get_by_location(1)

# Obtener fallas activas
fallas = Falla.get_active_fallas()

# Obtener mantenimientos programados
mantenimientos = Mantenimiento.get_scheduled_maintenances(
datetime.now(),
datetime.now() + timedelta(days=30)
)
```

## Ejemplo Completo

Ver el archivo `ejemplo_uso.py` para un ejemplo completo que demuestra:

- Creación de usuarios con diferentes roles
- Configuración de ubicaciones jerárquicas
- Instalación de equipos
- Gestión de fallas
- Programación de mantenimientos
- Subida de fotografías
- Configuración de conexiones de red
- Consultas y resúmenes

## Base de Datos Soportada

Los modelos están diseñados para funcionar con:
- **PostgreSQL** (recomendado)
- **MySQL**
- **SQLite** (para desarrollo)

## Extensibilidad

Los modelos están diseñados para ser fácilmente extensibles:

1. **Nuevos tipos de equipos**: Heredar de `EquipmentBase`
. **Nuevos estados**: Agregar valores a los enums
3. **Nuevos campos**: Agregar columnas a los modelos existentes
4. **Nuevas funcionalidades**: Agregar métodos a los modelos

## Consideraciones de Rendimiento

1. **Índices**: Se han agregado índices en campos de búsqueda frecuente
. **Relaciones**: Se han configurado lazy loading donde es apropiado
3. **Soft Delete**: Implementado para mantener integridad de datos
4. **Consultas optimizadas**: Métodos de consulta especializados

## Mantenimiento

Para mantener estos modelos:

1. **Actualizaciones de esquema**: Crear migraciones SQLAlchemy
. **Nuevas funcionalidades**: Seguir los patrones establecidos
3. **Validaciones**: Mantener integridad de datos
4. **Documentación**: Actualizar este README con cambios

## Soporte

Este sistema de modelos proporciona una base sólida para cualquier aplicación de gestión de infraestructura que requiera:
- Gestión de usuarios y permisos
- Inventario de equipos
- Mantenimiento preventivo y correctivo
- Monitoreo y alertas
- Documentación visual
- Reportes y análisis