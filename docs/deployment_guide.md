# Guía de Deployment - Sistema de Cámaras UFRO

Esta guía cubre el deployment del sistema en Railway para producción.

## Prerrequisitos

- Cuenta en Railway
- Repositorio Git configurado
- Variable de entorno `SECRET_KEY` configurada

## Pasos para Deployment

### 1. Configuración Inicial en Railway

1. Crear nuevo proyecto en Railway
2. Conectar repositorio Git
3. Railway detectará automáticamente el `Procfile`

### 2. Configuración de Variables de Entorno

En Railway Dashboard, configurar:

```
SECRET_KEY=genera-una-clave-secreta-fuerte-aqui
DATABASE_URL=postgresql://usuario:password@host:puerto/database
FLASK_ENV=production
LOG_LEVEL=INFO
PORT=8000
```

### 3. Configuración de PostgreSQL

1. Agregar PostgreSQL addon en Railway
2. Railway generará automáticamente `DATABASE_URL`
3. No es necesario configurar manualmente

### 4. Deployment Automático

Railway ejecutará automáticamente:
```bash
pip install -r requirements.txt
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 4
```

## Verificación de Deployment

### Endpoints de Diagnóstico

- `/debug-db`: Verificar conexión a base de datos
- `/debug-tables`: Verificar estructura de tablas
- `/analisis-tablas`: Análisis completo de BD

### Logs

Acceder a logs en Railway Dashboard para troubleshooting.

## Monitoreo

### Métricas Importantes
- Tiempo de respuesta de endpoints
- Uso de memoria y CPU
- Conexiones a base de datos
- Errores 5xx

### Alertas
- Configurar alertas para errores críticos
- Monitoreo de disponibilidad
- Notificaciones por email

## Backup y Recuperación

### Backups Automáticos
Railway mantiene backups automáticos de PostgreSQL.

### Backup Manual
```bash
pg_dump -h host -U usuario database > backup.sql
```

## Troubleshooting

### Problemas Comunes

1. **Error de conexión a BD**
   - Verificar `DATABASE_URL`
   - Revisar credenciales PostgreSQL

2. **Error 500 en endpoints**
   - Revisar logs de aplicación
   - Verificar estructura de tablas

3. **Timeout en requests**
   - Ajustar timeout en Procfile
   - Optimizar queries de BD

## Optimización de Performance

### Gunicorn Configuration
```bash
web: gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 4 --worker-class sync
```

### Database Optimization
- Indexar columnas frequently queried
- Optimizar queries complejas
- Configurar connection pooling

## Seguridad en Producción

### Variables de Entorno
- `SECRET_KEY`: Clave criptográfica fuerte
- `DATABASE_URL`: Credenciales de BD seguras
- `FLASK_ENV=production`: Modo producción

### SSL/TLS
Railway proporciona SSL automático para HTTPS.

### Headers de Seguridad
Implementar headers de seguridad en la aplicación.

---

**Última actualización:** 2024  
**Versión:** 1.0.0