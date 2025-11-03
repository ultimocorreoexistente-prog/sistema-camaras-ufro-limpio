# Resumen de Archivos Excel Analizados - Sistema Cámaras UFRO

**Fecha de análisis:** 2025-11-04  
**Total de archivos procesados:** 28 archivos Excel

## Archivos por Directorio

### 1. Directorio Principal: `/sistema-camaras-ufro-main/sistema-camaras-ufro-main/planillas/`

#### Archivos Principales:
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

### 2. Directorio Web: `/planillas-web/`

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
3. **Historial de fallas**: Registro histórico de problemas y soluciones
4. **Trazabilidad**: Identificación de técnicos responsables y fechas

## Estadísticas Generales

- **Total de cámaras documentadas**: ~467 cámaras
- **Tipos de cámara identificados**: Principalmente IP con PoE
- **Fabricantes principales**: Hikvision (NVR/DVR)
- **Edificios monitoreados**: Múltiples edificios en campus principal y extensiones
- **Tipos de fallas más comunes**: 
  - Problemas de conectividad
  - Daños físicos (mica rallada)
  - Problemas de limpieza
  - Fallas eléctricas

## Recomendaciones Inmediatas

1. **Consolidar archivos duplicados** en directorios únicos por entidad
2. **Completar campos vacíos** críticos para relaciones
3. **Normalizar nomenclatura** de campos y valores
4. **Implementar validación** de datos antes de la migración
5. **Crear backup** consolidado antes de cualquier migración

Este análisis proporciona la base para el diseño de la nueva arquitectura de datos del Sistema de Cámaras UFRO.