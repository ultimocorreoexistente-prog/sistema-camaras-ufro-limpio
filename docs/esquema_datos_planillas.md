# Esquema de Datos - Sistema de Cámaras UFRO

**Fecha de análisis:** 2025-11-04

**Archivos analizados:** 28 archivos Excel

## Resumen Ejecutivo

Este análisis examina la estructura de datos del Sistema de Cámaras de la Universidad de La Frontera (UFRO), identificando **12 entidades principales** que conforman el ecosistema de video vigilancia.

### Entidades Identificadas:

- **CÁMARA**: Dispositivos de video vigilancia con IP, ubicación y configuración técnica
- **FALLA**: Registro de incidentes y problemas en el sistema de cámaras
- **NVR_DVR**: Equipos de grabación y gestión de video (Network Video Recorder)
- **SWITCH**: Equipos de red para conectividad de cámaras
- **UPS**: Sistemas de alimentación ininterrumpida
- **FUENTE_PODER**: Fuentes de alimentación eléctrica para equipos
- **GABINETE**: Estructuras que alojan equipos de red y alimentación
- **UBICACION**: Definición geográfica y estructural de espacios
- **MANTENIMIENTO**: Registro de actividades de mantenimiento preventivo y correctivo
- **EQUIPO_TECNICO**: Personal técnico encargado de mantenimiento e instalación
- **CATALOGO_FALLAS**: Clasificación y categorización de tipos de fallas
- **PUERTO_SWITCH**: Configuración de puertos individuales en switches

## Análisis Detallado por Entidad

### CÁMARA

**Descripción:** Dispositivos de video vigilancia con IP, ubicación y configuración técnica

**Archivos que contienen esta entidad:**
- Listadecámaras_modificada.xlsx
- Listadecámaras.xlsx

**Campos principales:**
- Nombre de Cámara
- IP de Cámara
- Campus/Edificio
- NVR Asociado (Cámara)
- Tipo de Cámara
- Estado de Funcionamiento
- Estado de Conexión

### FALLA

**Descripción:** Registro de incidentes y problemas en el sistema de cámaras

**Archivos que contienen esta entidad:**
- Ejemplos_Fallas_Reales_corregido_20251019_005201.xlsx
- Ejemplos_Fallas_Reales.xlsx
- Fallas_Actualizada.xlsx

**Campos principales:**
- ID Falla
- Fecha de Reporte
- Tipo de Falla
- Cámara Afectada
- Ubicación
- Impacto en Visibilidad
- Estado
- Prioridad
- Técnico Asignado

### NVR_DVR

**Descripción:** Equipos de grabación y gestión de video (Network Video Recorder)

**Archivos que contienen esta entidad:**
- NVR_DVR.xlsx

**Campos principales:**
- Nombre NVR
- IP NVR
- Campus/Edificio
- Número de Cámaras Conectadas
- Estado NVR
- Fabricante
- Modelo
- Versión Firmware

### SWITCH

**Descripción:** Equipos de red para conectividad de cámaras

**Archivos que contienen esta entidad:**
- Switches.xlsx

**Campos principales:**
- Nombre Switch
- IP Switch
- Campus/Edificio
- Número de Puertos
- Estado Switch
- Fabricante
- Modelo
- Ubicación

### UPS

**Descripción:** Sistemas de alimentación ininterrumpida

**Archivos que contienen esta entidad:**
- UPS.xlsx

**Campos principales:**
- Nombre UPS
- Campus/Edificio
- Potencia (VA)
- Autonomía (min)
- Estado UPS
- Número de Equipos Conectados
- Fecha Instalación

### FUENTE_PODER

**Descripción:** Fuentes de alimentación eléctrica para equipos

**Archivos que contienen esta entidad:**
- Fuentes_Poder.xlsx

**Campos principales:**
- Nombre Fuente
- Campus/Edificio
- Potencia (W)
- Voltaje Salida
- Estado Fuente
- Equipos que Alimenta
- Ubicación

### GABINETE

**Descripción:** Estructuras que alojan equipos de red y alimentación

**Archivos que contienen esta entidad:**
- Gabinetes.xlsx

**Campos principales:**
- Nombre Gabinete
- Campus/Edificio
- Piso/Nivel
- Estado Gabinete
- Equipos que Contiene
- Temperatura
- Acceso

### UBICACION

**Descripción:** Definición geográfica y estructural de espacios

**Archivos que contienen esta entidad:**
- Ubicaciones.xlsx

**Campos principales:**
- Nombre Ubicación
- Campus
- Edificio
- Piso/Nivel
- Zona
- Coordenadas
- Descripción

### MANTENIMIENTO

**Descripción:** Registro de actividades de mantenimiento preventivo y correctivo

**Archivos que contienen esta entidad:**
- Mantenimientos.xlsx

**Campos principales:**
- ID Mantenimiento
- Fecha
- Tipo Mantenimiento
- Equipo Afectado
- Técnico Responsable
- Descripción Trabajo
- Costo

### EQUIPO_TECNICO

**Descripción:** Personal técnico encargado de mantenimiento e instalación

**Archivos que contienen esta entidad:**
- Equipos_Tecnicos.xlsx

**Campos principales:**
- Nombre Técnico
- Especialidad
- Certificaciones
- Estado
- Disponibilidad
- Contacto

### CATALOGO_FALLAS

**Descripción:** Clasificación y categorización de tipos de fallas

**Archivos que contienen esta entidad:**
- Catalogo_Tipos_Fallas.xlsx

**Campos principales:**
- Tipo Falla
- Subtipo
- Descripción
- Impacto
- Tiempo Estimado Reparación
- Prioridad

### PUERTO_SWITCH

**Descripción:** Configuración de puertos individuales en switches

**Archivos que contienen esta entidad:**
- Puertos_Switch.xlsx

**Campos principales:**
- Switch
- Número Puerto
- Equipo Conectado
- Estado Puerto
- VLAN
- Velocidad

## Modelo de Relaciones

Las entidades se relacionan de la siguiente manera:

```
UBICACION (1) ──── (N) CÁMARA
UBICACION (1) ──── (N) NVR_DVR
UBICACION (1) ──── (N) SWITCH
UBICACION (1) ──── (N) UPS
UBICACION (1) ──── (N) FUENTE_PODER
UBICACION (1) ──── (N) GABINETE

NVR_DVR (1) ──── (N) CÁMARA
SWITCH (1) ──── (N) CÁMARA
SWITCH (1) ──── (N) PUERTO_SWITCH
UPS (1) ──── (N) EQUIPO (NVR/Switch/Cámara)
GABINETE (1) ──── (N) EQUIPO (NVR/Switch/Fuente)

CÁMARA (1) ──── (N) FALLA
MANTENIMIENTO (N) ──── (1) EQUIPO
EQUIPO_TECNICO (1) ──── (N) MANTENIMIENTO
CATALOGO_FALLAS (1) ──── (N) FALLA
```

## Arquitectura de Datos

### Jerarquía Geográfica:
1. **Campus** → Edificios → Pisos/Niveles → Zonas/Ubicaciones específicas
2. Cada ubicación puede contener múltiples equipos

### Jerarquía de Equipos:
1. **Equipos de Conectividad**: Switches → Puertos → Cámaras
2. **Equipos de Gestión**: NVR/DVR → Cámaras
3. **Equipos de Soporte**: UPS → Gabinetes → Equipos alimentados

## Estadísticas del Sistema

Basado en el análisis de los archivos:

- **Total de cámaras registradas**: ~467 cámaras
- **Edificios monitoreados**: Múltiples edificios en campus principal
- **Tipos de cámara**: Principalmente IP con conectividad PoE
- **NVR/DVR**: Sistemas Hikvision con capacidades de 32-128 canales
- **Tipos de fallas**: Problemas de conectividad, daños físicos, limpieza

## Problemas Identificados en los Datos

### Inconsistencias:
- **Campos vacíos**: Muchos registros tienen campos como ID Ubicación, Ubicación Específica vacíos
- **Duplicación**: Archivos similares en diferentes directorios
- **Nomenclatura**: Inconsistencias en nombres de campos entre archivos
- **Tipos de datos**: Mezcla de formatos de fecha y numeración

### Oportunidades de Mejora:
- **Normalización**: Establecer claves primarias únicas
- **Relaciones explícitas**: Definir foreign keys claramente
- **Validación**: Implementar reglas de validación de datos
- **Automatización**: Migrar a sistema de base de datos

## Recomendaciones Técnicas

### 1. Consolidación de Datos
- Unificar archivos duplicados (ej: múltiples versiones de Listadecámaras)
- Establecer archivo maestro para cada entidad
- Implementar control de versiones

### 2. Esquema de Base de Datos
- **Tabla Ubicaciones**: id_ubicacion, campus, edificio, piso, zona
- **Tabla Cámaras**: id_camara, nombre, ip, id_ubicacion, id_nvr, estado
- **Tabla NVR**: id_nvr, nombre, ip, id_ubicacion, estado
- **Tabla Fallas**: id_falla, id_camara, tipo_falla, fecha_reporte, estado
- Y así sucesivamente para cada entidad...

### 3. Migración a Base de Datos
- **PostgreSQL**: Para datos complejos y relaciones
- **MongoDB**: Para flexibilidad en estructura de fallas
- **API REST**: Para integración con aplicaciones web

### 4. Aplicación Web Propuesta
- **Frontend**: React con módulos por entidad
- **Backend**: Node.js/Express o Python/FastAPI
- **Base de datos**: PostgreSQL con relaciones normalizadas
- **Funcionalidades**:
  - Dashboard ejecutivo con métricas
  - Gestión de cámaras en tiempo real
  - Sistema de reportes de fallas
  - Calendario de mantenimientos
  - Mapas interactivos de ubicaciones

## Conclusiones

El Sistema de Cámaras UFRO cuenta con una estructura de datos comprehensiva que abarca todos los aspectos del ecosistema de video vigilancia. Sin embargo, la gestión actual basada en archivos Excel presenta limitaciones en cuanto a integridad de datos, relaciones explícitas y capacidades de análisis.

La migración a una base de datos relacional proporcionaría:
- Mayor integridad y consistencia de datos
- Capacidades de análisis avanzadas
- Automatización de procesos
- Escalabilidad para crecimiento futuro
- Integración con sistemas de monitoreo en tiempo real

**Próximos pasos recomendados:**
1. Diseñar esquema de base de datos normalizado
2. Desarrollar herramientas de migración de datos
3. Crear aplicación web para gestión
4. Implementar sistema de alertas y monitoreo
