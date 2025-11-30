# Guía Completa de Deployment - Sistema Cámaras UFRO

## 📋 Información del Proyecto

- **Nombre**: Sistema de Cámaras UFRO
- **Tecnología**: Python Flask + PostgreSQL
- **Hosting**: Railway
- **URL Producción**: https://sistema-camaras-ufro-limpio-production.up.railway.app
- **Repositorio**: https://github.com/ultimocorreoexistente-prog/sistema-camaras-ufro-limpio.git

## 🚀 Pasos de Deployment

### Paso 1: Configurar Variables de Entorno en Railway

Ejecuta el script de configuración:

```bash
python configurar_railway.py
```

O configura manualmente estas variables en Railway Dashboard > Variables:

| Variable | Valor |
|----------|-------|
| `DATABASE_URL` | `postgresql://postgres:WMQxvzTQsdkiAUOqfMgXmzgAHqxDkwRJ@postgres.railway.internal:5432/railway` |
| `SECRET_KEY` | `flask-secret-key-camaras-ufro-2025-production-secure` |
| `FLASK_ENV` | `production` |
| `FLASK_DEBUG` | `0` |
| `PORT` | `8000` |
| `LOG_LEVEL` | `INFO` |
| `API_BASE_URL` | `https://sistema-camaras-ufro-limpio-production.up.railway.app` |

### Paso 2: Hacer Push al Repositorio

Desde tu directorio local:

```bash
cd C:\Users\Usuario\sistema-camaras-ufro-limpio
git add .
git commit -m "Add unique files: emergency_recovery.py, configurar_railway.py, deployment guide"
git push origin main
```

### Paso 3: Verificar el Deployment

1. **Espera 2-3 minutos** para que Railway complete el deployment
2. **Verifica la URL**: https://sistema-camaras-ufro-limpio-production.up.railway.app/
3. **Test de salud**: https://sistema-camaras-ufro-limpio-production.up.railway.app/health

## 🛠️ Herramientas de Emergencia

### Script de Recuperación de Emergencia

Si el sistema no funciona correctamente, ejecuta:

```bash
python emergency_recovery.py
```

**Funciones**:
- Conecta directamente a PostgreSQL
- Hace rollback de transacciones pendientes
- Elimina tablas duplicadas
- Verifica la integridad de la base de datos

### Script de Configuración Railway

Para reconfigurar variables de entorno:

```bash
python configurar_railway.py
```

**Funciones**:
- Muestra todas las variables requeridas
- Crea archivo .env de referencia
- Guía paso a paso para configuración

## 📁 Estructura de Archivos Importantes

```
sistema-camaras-ufro-limpio/
├── app.py                     # Aplicación principal Flask
├── config.py                  # Configuración avanzada
├── requirements.txt           # Dependencias Python
├── Procfile                   # Configuración Railway
├── emergency_recovery.py      # 🔧 NUEVO - Script de emergencia
├── configurar_railway.py      # 🔧 NUEVO - Configuración variables
├── docs/
│   └── deployment_guide.md    # 🔧 NUEVO - Esta guía
└── templates/                 # Templates HTML
    ├── dashboard.html
    ├── login.html
    └── ...
```

## 🔍 Verificación Post-Deployment

### URLs de Prueba

1. **Página principal**: https://sistema-camaras-ufro-limpio-production.up.railway.app/
   - Debe mostrar: "SUCCESS" con timestamp

2. **Health check**: https://sistema-camaras-ufro-limpio-production.up.railway.app/health
   - Debe mostrar: `{"status": "healthy"}`

3. **Login**: https://sistema-camaras-ufro-limpio-production.up.railway.app/login
   - Debe mostrar formulario de login

### Credenciales de Acceso

- **Usuario**: charles.jelvez@ufrontera.cl
- **Contraseña**: Vivita0468
- **Rol**: superadmin

## ⚠️ Solución de Problemas

### Error 502 - Bad Gateway

1. **Verificar variables de entorno** en Railway Dashboard
2. **Esperar 5 minutos adicionales** para el deployment
3. **Revisar logs** en Railway Dashboard > Deploy
4. **Ejecutar script de emergencia** si es necesario

### Problemas de Base de Datos

1. **Ejecutar recovery script**:
   ```bash
   python emergency_recovery.py
   ```

2. **Verificar conexión** en logs de Railway
3. **Confirmar que DATABASE_URL esté correcta**

### Logs y Debugging

- **Logs en tiempo real**: Railway Dashboard > Deploy > View Logs
- **Health check**: Agregar `/health` a la URL base
- **Database debugging**: Usar `emergency_recovery.py`

## 📞 Contacto y Soporte

Para problemas técnicos:
1. Revisar esta guía primero
2. Ejecutar scripts de emergencia
3. Verificar logs en Railway Dashboard
4. Contactar al administrador del sistema

---

**Última actualización**: 2025-11-29
**Versión**: 3.0-hybrid-production
**Estado**: Ready for Production