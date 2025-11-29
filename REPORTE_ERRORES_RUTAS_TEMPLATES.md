# Reporte de Errores - Análisis de Rutas y Plantillas
## Sistema de Cámaras UFRO

**Fecha de análisis:** 15 de noviembre de 2025  
**Archivos analizados:** 13 rutas, 4 modelos, 7 plantillas  
**Total de errores encontrados:** 25+

---

## 1. ERRORES CRÍTICOS 🚨
*Errores que impiden el funcionamiento del sistema*

### 1.1 Algoritmo JWT Incorrecto
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/routes/auth.py`  
**Líneas:** 31, 89, 181  
**Problema:** Uso de algoritmo JWT inexistente 'HS56'  
**Código actual:**
```python
jwt.encode(payload, secret_key, algorithm='HS56')
```
**Solución:** Cambiar a `'HS256'`
```python
jwt.encode(payload, secret_key, algorithm='HS256')
```

### 1.2 Error SQL Crítico en Filtro UPS
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/routes/ups.py`  
**Línea:** 324  
**Problema:** Condición SQL incorrecta usando '=' en lugar de '!='  
**Código actual:**
```python
Ups.marca = ''
```
**Solución:**
```python
Ups.marca != ''
```

---

## 2. INCOMPATIBILIDADES MODELO-TEMPLATE ⚠️
*Campos que no coinciden entre modelos y plantillas*

### 2.1 Modelo Usuario - Incompatibilidades de Campos

#### 2.1.1 Campo nombre_completo vs full_name
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/templates/01_usuarios_listar.html`  
**Líneas:** 28, 41  
**Problema:** Plantilla usa `usuario.nombre_completo` pero modelo tiene `full_name`  
**Código actual:**
```html
{{ usuario.nombre_completo }}
```
**Solución:** Cambiar a `{{ usuario.full_name }}`

#### 2.1.2 Campo nombre vs full_name
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/templates/base.html`  
**Línea:** 22  
**Problema:** Template usa `current_user.nombre` pero modelo tiene `full_name`  
**Código actual:**
```html
{{ current_user.nombre }}
```
**Solución:** Cambiar a `{{ current_user.full_name }}`

#### 2.1.3 Campo rol vs role
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/templates/01_usuarios_listar.html`  
**Línea:** 43  
**Problema:** Plantilla usa `usuario.rol` pero modelo tiene `role`  
**Código actual:**
```html
{{ usuario.rol }}
```
**Solución:** Cambiar a `{{ usuario.role }}`

#### 2.1.4 Campo telefono vs phone
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/templates/01_usuarios_listar.html`  
**Línea:** 42  
**Problema:** Plantilla usa `usuario.telefono` pero modelo tiene `phone`  
**Código actual:**
```html
{{ usuario.telefono }}
```
**Solución:** Cambiar a `{{ usuario.phone }}`

#### 2.1.5 Campo departamento vs department
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/templates/01_usuarios_listar.html`  
**Línea:** 44  
**Problema:** Plantilla usa `usuario.departamento` pero modelo tiene `department`  
**Código actual:**
```html
{{ usuario.departamento }}
```
**Solución:** Cambiar a `{{ usuario.department }}`

#### 2.1.6 Campo activo vs is_active
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/templates/01_usuarios_listar.html`  
**Línea:** 45  
**Problema:** Plantilla usa `usuario.activo` pero modelo tiene `is_active`  
**Código actual:**
```html
{{ usuario.activo }}
```
**Solución:** Cambiar a `{{ usuario.is_active }}`

#### 2.1.7 Campo ultimo_acceso vs last_login
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/templates/01_usuarios_listar.html`  
**Línea:** 46  
**Problema:** Plantilla usa `usuario.ultimo_acceso` pero modelo tiene `last_login`  
**Código actual:**
```html
{{ usuario.ultimo_acceso }}
```
**Solución:** Cambiar a `{{ usuario.last_login }}`

### 2.2 Modelo Camara - Incompatibilidades de Campos

#### 2.2.1 Campo ip vs ip_address
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/templates/camaras_list.html`  
**Línea:** 37  
**Problema:** Plantilla usa `camara.ip` pero modelo tiene `ip_address`  
**Código actual:**
```html
{{ camara.ip }}
```
**Solución:** Cambiar a `{{ camara.ip_address }}`

### 2.3 Modelo Falla - Incompatibilidades de Campos

#### 2.3.1 Campo prioridad vs severidad
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/templates/fallas_list.html`  
**Línea:** 45  
**Problema:** Plantilla usa `falla.prioridad` pero modelo tiene `severidad`  
**Código actual:**
```html
{{ falla.prioridad }}
```
**Solución:** Cambiar a `{{ falla.severidad }}`

#### 2.3.2 Relación tecnico_asignado inexistente
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/templates/fallas_list.html`  
**Línea:** 46  
**Problema:** Plantilla usa `falla.tecnico_asignado.nombre_completo` pero no existe la relación  
**Código actual:**
```html
{{ falla.tecnico_asignado.nombre_completo }}
```
**Solución:** Definir relación en modelo o usar campo de modelo existente

---

## 3. PLANTILLAS INEXISTENTES 📄
*Plantillas referenciadas en rutas que no existen*

### 3.1 Módulo Fotografías
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/routes/fotografias.py`  
**Líneas:** 97, 109, 191, 213, 304  
**Problema:** 5 plantillas referenciadas no existen  
**Plantillas faltantes:**
- `fotografias_listar.html` (línea 97)
- `fotografias_subir.html` (línea 109)
- `fotografias_ver.html` (línea 191)
- `fotografias_editar.html` (línea 213)
- `fotografias_dragdrop.html` (línea 304)

**Solución:** Crear las 5 plantillas faltantes en `/templates/`

### 3.2 Módulo Usuarios
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/routes/usuarios.py`  
**Líneas:** 477, 499  
**Problema:** 2 plantillas referenciadas no existen  
**Plantillas faltantes:**
- `usuarios_perfil.html` (línea 477)
- `usuarios_perfil.html` (línea 499)

**Solución:** Crear la plantilla `usuarios_perfil.html`

### 3.3 Módulo Topología
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/routes/topologia.py`  
**Líneas:** 151, 186  
**Problema:** 2 plantillas referenciadas no existen  
**Plantillas faltantes:**
- `topologia_campus.html` (línea 151)
- `topologia_equipo.html` (línea 186)

**Solución:** Crear las 2 plantillas faltantes

---

## 4. ERRORES DE SINTAXIS 🔧
*Errores de código que impiden compilación/ejecución*

### 4.1 Patrón Regex Incompleto
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/routes/auth.py`  
**Línea:** 119  
**Problema:** Patrón regex mal formado `{,}`  
**Código actual:**
```python
[a-zA-Z]{,}
```
**Solución:**
```python
[a-zA-Z]{2,}
```

### 4.2 Código de Estado HTTP Incorrecto
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/routes/auth.py`  
**Línea:** 146  
**Problema:** Código de estado HTTP incorrecto '01'  
**Código actual:**
```python
return jsonify({'error': 'Invalid token'}), 01
```
**Solución:**
```python
return jsonify({'error': 'Invalid token'}), 401
```

### 4.3 Función round() Incompleta
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/routes/fallas.py`  
**Línea:** 527  
**Problema:** Llamada a round() sin segundo parámetro  
**Código actual:**
```python
porcentaje = round(100 * completadas / total)
```
**Solución:**
```python
porcentaje = round(100 * completadas / total, 1)
```

---

## 5. CAMPOS Y RELACIONES FALTANTES ➕
*Campos referenciados en plantillas que no existen en modelos*

### 5.1 Modelo Camara - Campo tipo_camara Faltante
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/templates/camaras_list.html`  
**Línea:** 38  
**Problema:** Plantilla referencia `camara.tipo_camara` que no existe en modelo  
**Código actual:**
```html
{{ camara.tipo_camara }}
```
**Solución:** Agregar campo `tipo_camara` al modelo Camara o usar campo existente

### 5.2 Modelo Camara - Relación ubicacion Faltante
**Archivo:** `/workspace/sistema-camaras-ufro-limpio/templates/camaras_list.html`  
**Línea:** 39  
**Problema:** Plantilla usa `camara.ubicacion.campus` pero modelo no tiene relación ubicacion  
**Código actual:**
```html
{{ camara.ubicacion.campus }}
```
**Solución:** Definir relación ubicacion en modelo Camara o usar campo existente

---

## RESUMEN DE CORRECCIONES PRIORITARIAS

### 🚨 CRÍTICAS (Corregir inmediatamente)
1. Cambiar 'HS56' por 'HS256' en auth.py (3 líneas)
2. Corregir condición SQL en ups.py línea 324

### ⚠️ ALTAS (Corregir antes de producción)
3. Unificar nomenclatura Usuario: full_name, role, phone, department, is_active, last_login
4. Crear 10 plantillas faltantes
5. Corregir incompatibilidades en Camara y Falla

### 📋 MEDIAS (Corregir en próximo sprint)
6. Corregir errores de sintaxis (regex, HTTP status, round())
7. Agregar campos faltantes en modelos

---

## IMPACTO EN FUNCIONALIDAD

- **Autenticación:** Sistema JWT no funcional
- **Gestión UPS:** Filtros de marca incorrectos
- **CRUD Usuarios:** Campos no se muestran correctamente
- **CRUD Cámaras:** Campos no se muestran correctamente  
- **Gestión Fallas:** Campos no se muestran correctamente
- **Módulo Fotografías:** Completamente no funcional (plantillas faltantes)
- **Perfil Usuario:** No funcional (plantilla faltante)
- **Topología:** Funcionalidad parcial (plantillas faltantes)

---

## RECOMENDACIONES

1. **Priorizar correcciones críticas** para restaurar funcionalidad básica
2. **Estandarizar nomenclatura** en todos los modelos y plantillas
3. **Crear sistema de validación** para verificar existencia de plantillas antes de referenciarlas
4. **Implementar tests** para detectar estos errores automáticamente
5. **Documentar convenciones** de nomenclatura para futuros desarrollos

---
*Reporte generado automáticamente el 15 de noviembre de 2025*