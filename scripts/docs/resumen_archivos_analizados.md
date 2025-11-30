# Resumen de Archivos Excel Analizados - Sistema Cámaras UFRO

<<<<<<< HEAD
**Fecha de análisis:** 05-11-04
**Total de archivos procesados:** 8 archivos Excel
=======
**Fecha de análisis:** 2025-11-04  
**Total de archivos procesados:** 28 archivos Excel
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856

## Archivos por Directorio

### 1. Directorio Principal: `/sistema-camaras-ufro-main/sistema-camaras-ufro-main/planillas/`

#### Archivos Principales:
<<<<<<< HEAD
- **Ejemplos_Fallas_Reales_corregido_051019_00501.xlsx** (6 filas, 8 columnas)
- Contiene ejemplos reales de fallas reportadas
- Campos: ID Falla, Fecha de Reporte, Tipo de Falla, Cámara Afectada, etc.
- Casos reales documentados con soluciones

- **Listadecámaras_modificada.xlsx** (467 filas, 6 columnas)
- Lista principal de cámaras del sistema
- Campos: Nombre, IP, Campus/Edificio, NVR Asociado, Estado, etc.
- Registro más completo de cámaras instaladas

- **SISTEMA_CAMARAS_UFRO_DATOS_REALES_051018_08435.xlsx** (Múltiples hojas)
- Hoja: RESUMEN_EJECUTIVO
- Hoja: TODAS_LAS_CAMARAS
- Hoja: ANALISIS_POR_EDIFICIO
- Hoja: EDIFICIOS
- Hoja: CAMARAS_FUNCIONANDO
- Hoja: CAMARAS_CON_PROBLEMAS
- Archivo consolidado con análisis y métricas
=======
- **Ejemplos_Fallas_Reales_corregido_20251019_005201.xlsx** (6 filas, 28 columnas)
  - Contiene ejemplos reales de fallas reportadas
  - Campos: ID Falla, Fecha de Reporte, Tipo de Falla, Cámara Afectada, etc.
  - Casos reales documentados con soluciones

- **Listadecámaras_modificada.xlsx** (467 filas, 26 columnas)
  - Lista principal de cámaras del sistema
  - Campos: Nombre, IP, Campus/Edificio, NVR Asociado, Estado, etc.
  - Registro más completo de cámaras instaladas

- **SISTEMA_CAMARAS_UFRO_DATOS_REALES_20251018_084235.xlsx** (Múltiples hojas)
  - Hoja: RESUMEN_EJECUTIVO
  - Hoja: TODAS_LAS_CAMARAS
  - Hoja: ANALISIS_POR_EDIFICIO
  - Hoja: EDIFICIOS
  - Hoja: CAMARAS_FUNCIONANDO
  - Hoja: CAMARAS_CON_PROBLEMAS
  - Archivo consolidado con análisis y métricas
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856

#### Subdirectorio: `extracted_planillas/`
- **Catalogo_Tipos_Fallas.xlsx** - Catálogo de tipos de fallas
- **Ejemplos_Fallas_Reales.xlsx** - Ejemplos de fallas (versión original)
- **Ejemplos_Fallas_Reales_backup.xlsx** - Copia de respaldo
- **Equipos_Tecnicos.xlsx** - Información de personal técnico
- **Fallas_Actualizada.xlsx** - Registro de fallas actualizado
- **Gabinetes.xlsx** - Información de gabinetes de equipos
- **Listadecámaras.xlsx** - Lista de cámaras (versión original)
- **Listadecámaras_modificada.xlsx** - Lista modificada
- **Mantenimientos.xlsx** - Registro de mantenimientos
- **Puertos_Switch.xlsx** - Configuración de puertos de switches
- **Switches.xlsx** - Información de switches de red
- **Ubicaciones.xlsx** - Definición de ubicaciones

<<<<<<< HEAD
### . Directorio Web: `/planillas-web/`
=======
### 2. Directorio Web: `/planillas-web/`
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856

#### Archivos de Entidades:
- **Catalogo_Tipos_Fallas.xlsx** - Catálogo de tipos de fallas
- **Ejemplos_Fallas_Reales.xlsx** - Ejemplos de fallas reportadas
- **Equipos_Tecnicos.xlsx** - Personal técnico del sistema
- **Fallas_Actualizada.xlsx** - Fallas registradas y actualizadas
- **Fuentes_Poder.xlsx** - Fuentes de alimentación eléctrica
- **Gabinetes.xlsx** - Gabinetes que alojan equipos
- **Listadecámaras_modificada.xlsx** - Lista principal de cámaras
- **Mantenimientos.xlsx** - Actividades de mantenimiento
- **NVR_DVR.xlsx** - Equipos de grabación de video
- **Puertos_Switch.xlsx** - Configuración de puertos
- **Switches.xlsx** - Switches de conectividad de red
- **UPS.xlsx** - Sistemas de alimentación ininterrumpida
- **Ubicaciones.xlsx** - Definiciones geográficas y estructurales

## Análisis de Integridad de Datos

### Problemas Identificados:
<<<<<<< HEAD
1. **Campos vacíos significativos**:
- ID Ubicación: 467 registros vacíos en Listadecámaras_modificada
- Gabinetes Asociados: 467 registros vacíos
- Switches Asociados: 467 registros vacíos

. **Duplicación de archivos**:
- Múltiples versiones de la misma entidad en diferentes directorios
- Ejemplos: Listadecámaras.xlsx y Listadecámaras_modificada.xlsx

3. **Inconsistencias en nomenclatura**:
- Variaciones en nombres de campos entre archivos
- Formatos de fecha inconsistentes

### Fortalezas del Sistema Actual:
1. **Cobertura completa**: Todas las entidades del sistema están documentadas
. **Información detallada**: Campos específicos para cada tipo de equipo
=======
1. **Campos vacíos significativos**: 
   - ID Ubicación: 467 registros vacíos en Listadecámaras_modificada
   - Gabinetes Asociados: 467 registros vacíos
   - Switches Asociados: 467 registros vacíos

2. **Duplicación de archivos**:
   - Múltiples versiones de la misma entidad en diferentes directorios
   - Ejemplos: Listadecámaras.xlsx y Listadecámaras_modificada.xlsx

3. **Inconsistencias en nomenclatura**:
   - Variaciones en nombres de campos entre archivos
   - Formatos de fecha inconsistentes

### Fortalezas del Sistema Actual:
1. **Cobertura completa**: Todas las entidades del sistema están documentadas
2. **Información detallada**: Campos específicos para cada tipo de equipo
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
3. **Historial de fallas**: Registro histórico de problemas y soluciones
4. **Trazabilidad**: Identificación de técnicos responsables y fechas

## Estadísticas Generales

- **Total de cámaras documentadas**: ~467 cámaras
- **Tipos de cámara identificados**: Principalmente IP con PoE
- **Fabricantes principales**: Hikvision (NVR/DVR)
- **Edificios monitoreados**: Múltiples edificios en campus principal y extensiones
<<<<<<< HEAD
- **Tipos de fallas más comunes**:
- Problemas de conectividad
- Daños físicos (mica rallada)
- Problemas de limpieza
- Fallas eléctricas
=======
- **Tipos de fallas más comunes**: 
  - Problemas de conectividad
  - Daños físicos (mica rallada)
  - Problemas de limpieza
  - Fallas eléctricas
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856

## Recomendaciones Inmediatas

1. **Consolidar archivos duplicados** en directorios únicos por entidad
<<<<<<< HEAD
. **Completar campos vacíos** críticos para relaciones
=======
2. **Completar campos vacíos** críticos para relaciones
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
3. **Normalizar nomenclatura** de campos y valores
4. **Implementar validación** de datos antes de la migración
5. **Crear backup** consolidado antes de cualquier migración

Este análisis proporciona la base para el diseño de la nueva arquitectura de datos del Sistema de Cámaras UFRO.