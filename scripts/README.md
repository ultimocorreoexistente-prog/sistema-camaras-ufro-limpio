# Scripts de Migración de Datos - Sistema Cámaras UFRO

Este conjunto de scripts permite migrar los datos de las planillas Excel del Sistema de Cámaras UFRO a una base de datos PostgreSQL, con validaciones, limpieza y pruebas automatizadas.

## Estructura de Scripts

### scripts/
- **`migrar_datos.py`** - Script principal de migración
- **`validar_datos.py`** - Validación de integridad de datos
- **`limpiar_datos.py`** - Limpieza y normalización de datos
- **`test_migracion.py`** - Pruebas automatizadas de migración

## Datos a Migrar

Basado en el análisis de las planillas Excel, se migrarán:

### Entidades Principales
- **467 registros de cámaras** - Dispositivos de video vigilancia
- **Fallas** - Registro de incidentes y problemas
- **NVR/DVR** - Equipos de grabación y gestión de video
- **Switches** - Equipos de red para conectividad
- **UPS** - Sistemas de alimentación ininterrumpida
- **Fuentes de poder** - Alimentación eléctrica
- **Gabinetes** - Estructuras que alojan equipos
- **Ubicaciones** - Definición geográfica y estructural
- **Mantenimientos** - Actividades preventivas y correctivas
- **Equipos técnicos** - Personal técnico
- **Catálogo de fallas** - Clasificación de tipos de fallas
- **Puertos de switch** - Configuración de puertos

### Ubicaciones de Planillas
- `/workspace/user_input_files/planillas-web/`
- `/workspace/user_input_files/sistema-camaras-ufro-main/sistema-camaras-ufro-main/planillas/`

## Requisitos

### Dependencias Python
```bash
pip install pandas psycopg-binary openpyxl
```

### Base de Datos PostgreSQL
- PostgreSQL 1+
- Crear base de datos: `camaras_ufro`
- Usuario con permisos de lectura/escritura

## Uso de los Scripts

### 1. Limpieza de Datos (Obligatorio)

Primero limpiar y normalizar las planillas Excel:

```bash
python scripts/limpiar_datos.py \
--entrada "/workspace/user_input_files/planillas-web" \
--salida "/workspace/datos_limpios" \
--validar
```

**Qué hace:**
- Normaliza nombres de columnas inconsistentes
- Limpia y valida direcciones IP
- Estandariza fechas en múltiples formatos
- Normaliza estados, prioridades y tipos
- Elimina registros incompletos
- Genera archivos JSON y Excel limpios

### . Migración a Base de Datos

Ejecutar la migración principal:

```bash
python scripts/migrar_datos.py \
--host "localhost" \
--database "camaras_ufro" \
--user "postgres" \
--password "tu_password" \
--port 543 \
--planillas-dir "/workspace/datos_limpios"
```

**Qué hace:**
- Establece conexión con PostgreSQL
- Crea backups automáticos de datos existentes
- Migra datos por entidad (cámaras, NVR, switches, fallas, etc.)
- Maneja errores y rollback automático
- Registra estadísticas de migración

### 3. Validación de Datos (Post-Migración)

Validar la integridad de los datos migrados:

```bash
python scripts/validar_datos.py \
--host "localhost" \
--database "camaras_ufro" \
--user "postgres" \
--password "tu_password" \
--port 543 \
--output "reporte_validacion.json"
```

**Qué valida:**
- Claves primarias duplicadas
- Direcciones IP únicas y válidas
- Relaciones entre tablas (Foreign Keys)
- Completitud de datos críticos
- Jerarquía geográfica
- Generación de estadísticas

### 4. Ejecución de Pruebas

Ejecutar pruebas automatizadas:

```bash
# Todas las pruebas
python scripts/test_migracion.py

# Solo pruebas unitarias
python scripts/test_migracion.py --solo-unitarias

# Solo pruebas de integración
python scripts/test_migracion.py --solo-integracion

# Con configuración de BD de prueba
python scripts/test_migracion.py \
--host "localhost" \
--database "test_camaras_ufro" \
--user "test_user" \
--password "test_password"
```

## Proceso de Migración Completo

### Secuencia Recomendada

1. **Análisis inicial:**
```bash
python inspect_excel_files.py
```

. **Limpieza:**
```bash
python scripts/limpiar_datos.py \
--entrada "/workspace/user_input_files/planillas-web" \
--salida "/workspace/datos_limpios" \
--validar
```

3. **Migración:**
```bash
python scripts/migrar_datos.py \
--host "localhost" \
--database "camaras_ufro" \
--user "postgres" \
--password "password" \
--planillas-dir "/workspace/datos_limpios"
```

4. **Validación:**
```bash
python scripts/validar_datos.py \
--host "localhost" \
--database "camaras_ufro" \
--user "postgres" \
--password "password" \
--output "reporte_final.json"
```

5. **Pruebas (opcional):**
```bash
python scripts/test_migracion.py
```

## Características Principales

### Validaciones y Seguridad
- **Backup automático** antes de cada migración
- **Rollback automático** en caso de error
- **Validación de IPs** únicas y bien formateadas
- **Integridad referencial** entre tablas
- **Manejo robusto de errores**

### Limpieza Automática
- **Normalización de estados** (Funcionando, Error, etc.)
- **Limpieza de texto** y eliminación de caracteres especiales
- **Parseo inteligente de fechas** (múltiples formatos)
- **Eliminación de duplicados**
- **Estandarización de tipos** (cámara, prioridad, etc.)

### Reporting y Monitoreo
- **Logs detallados** de cada proceso
- **Estadísticas de migración** (registros procesados, errores, etc.)
- **Reportes JSON** con métricas de calidad
- **Validación de completitud** de datos

### Pruebas Automatizadas
- **Pruebas unitarias** de funciones de limpieza
- **Pruebas de integración** del proceso completo
- **Validación de integridad** post-migración
- **Manejo de casos edge** y errores

## Problemas Identificados y Solucionados

### Datos con Issues Comunes
- **Campos vacíos** (hasta 100% en algunas columnas)
- **IPs duplicadas** o mal formateadas
- **Fechas inconsistentes** (múltiples formatos)
- **Estados no normalizados**
- **Referencias entre tablas faltantes**

### Soluciones Implementadas
- Limpieza automática de campos vacíos
- Validación y normalización de IPs
- Parseo inteligente de fechas
- Normalización de estados y tipos
- Generación de IDs únicos cuando faltan
- Backup y rollback automático

## Logs y Archivos Generados

### Archivos de Log
- `migracion.log` - Log principal de migración
- `limpieza.log` - Log del proceso de limpieza
- `validacion.log` - Log de validaciones
- `pruebas.log` - Log de pruebas

### Archivos de Salida
- `datos_limpios/normalizado_*.xlsx` - Datos normalizados en Excel
- `datos_limpios/normalizado_*.json` - Datos normalizados en JSON
- `reporte_limpieza_*.json` - Reporte de limpieza
- `reporte_validacion_*.json` - Reporte de validación
- `reporte_pruebas_*.json` - Reporte de pruebas

## Estructura de Base de Datos Esperada

### Tablas Principales
```sql
-- Cámaras (467 registros esperados)
CREATE TABLE camaras (
id_camara SERIAL PRIMARY KEY,
nombre_camara VARCHAR(55) NOT NULL,
ip_camara INET UNIQUE,
campus_edificio VARCHAR(55),
nvr_asociado VARCHAR(55),
tipo_camara VARCHAR(100),
estado_funcionamiento VARCHAR(50),
estado_conexion VARCHAR(50),
observaciones TEXT,
created_at TIMESTAMP DEFAULT NOW()
);

-- Fallas
CREATE TABLE fallas (
id_falla VARCHAR(50) PRIMARY KEY,
fecha_reporte DATE,
tipo_falla VARCHAR(100),
camara_afectada VARCHAR(55),
ubicacion TEXT,
prioridad VARCHAR(0),
estado VARCHAR(50),
created_at TIMESTAMP DEFAULT NOW()
);

-- NVR/DVR
CREATE TABLE nvr_dvr (
id_nvr VARCHAR(50) PRIMARY KEY,
nombre_nvr VARCHAR(55),
ip_nvr INET,
campus_edificio VARCHAR(55),
modelo VARCHAR(55),
marca VARCHAR(100),
canales_total INTEGER,
canales_usados INTEGER,
estado VARCHAR(50),
created_at TIMESTAMP DEFAULT NOW()
);

-- Switches
CREATE TABLE switches (
id_switch VARCHAR(50) PRIMARY KEY,
nombre_switch VARCHAR(55),
ip_switch INET,
campus_edificio VARCHAR(55),
modelo VARCHAR(55),
marca VARCHAR(100),
puertos_total INTEGER,
puertos_usados INTEGER,
soporta_poe BOOLEAN,
estado VARCHAR(50),
created_at TIMESTAMP DEFAULT NOW()
);

-- Ubicaciones
CREATE TABLE ubicaciones (
id_ubicacion VARCHAR(50) PRIMARY KEY,
campus VARCHAR(55),
edificio VARCHAR(55),
piso_nivel VARCHAR(100),
zona VARCHAR(55),
created_at TIMESTAMP DEFAULT NOW()
);
```

## Troubleshooting

### Error: "No se pudo conectar a la base de datos"
- Verificar credenciales de PostgreSQL
- Confirmar que el servicio está corriendo
- Verificar firewall/puertos

### Error: "Archivo no encontrado"
- Verificar rutas de archivos Excel
- Confirmar que existen las planillas
- Revisar permisos de lectura

### Error: "IP inválida"
- Validar formato de IPs en planillas
- Revisar IPs con valores como "N/A", "TBD", etc.

### Datos migrados incompletos
- Revisar logs de limpieza
- Verificar campos requeridos en base de datos
- Ejecutar validación post-migración

### Rollback necesario
```bash
python scripts/migrar_datos.py \
--host "localhost" \
--database "camaras_ufro" \
--user "postgres" \
--password "password" \
--rollback "camaras"
```

## Soporte y Documentación

- **Logs detallados** en cada paso del proceso
- **Validaciones automáticas** de integridad
- **Backup automático** antes de cambios
- **Documentación completa** en código fuente
- **Pruebas automatizadas** para verificación

## Estadísticas de Migración Esperadas

- **Cámaras:** 467 registros
- **Fallas:** ~6-50 registros (según archivo)
- **NVR/DVR:** 6-10 equipos
- **Switches:** 6-10 equipos
- **Ubicaciones:** 8-0 ubicaciones
- **Tasa de éxito:** >95% (datos limpios)
- **Tiempo estimado:** 5-15 minutos

---

**Autor:** Sistema de Migración UFRO
**Fecha:** 05-11-04
**Versión:** 1.0
**Estado:** Listo para producción