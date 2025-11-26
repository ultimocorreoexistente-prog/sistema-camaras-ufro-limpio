# INSTRUCCIONES DE DEPLOY - SISTEMA CÁMARAS UFRO

## 🎯 URL CORRECTA DEL PROYECTO
**URL:** https://gestion-camaras-ufro.up.railway.app
**NO usar:** web-production-12742.up.railway.app (es temporal/incorrecta)

## 📋 PASOS PARA RESOLVER ERROR 502

### 1. Acceder a Railway Dashboard
- Ir a: https://railway.app
- Login con cuenta del proyecto
- Seleccionar proyecto: "gestion-camaras-ufro"

### 2. Configurar Variables de Entorno
En Railway Dashboard > Variables, agregar:

```
DATABASE_URL=postgresql://postgres:WMQxvzTQsdkiAUOqfMgXmzgAHqxDkwRJ@postgres.railway.internal:5432/railway
SECRET_KEY=flask-secret-key-camaras-ufro-2025-production-secure
FLASK_ENV=production
FLASK_DEBUG=0
PORT=8000
LOG_LEVEL=INFO
```

### 3. Verificar Configuración de Deploy
En Railway Dashboard > Settings:

```
Builder: Dockerfile
Dockerfile path: backend/Dockerfile
```

### 4. Re-deployar Aplicación
- Railway redeployará automáticamente con los cambios
- O hacer deploy manual desde dashboard
- O comando: `railway deploy`

### 5. Verificar Logs
```bash
railway logs --service gestion-camaras-ufro
```

### 6. Probar Aplicación
- URL: https://gestion-camaras-ufro.up.railway.app
- Usuario: charles@ufro.cl
- Contraseña: ufro2025

## 🔧 Correcciones Aplicadas

### Problema resuelto:
- ✅ Dockerfile ahora copia app.py (no minimal.py)
- ✅ railway.json usa puerto dinámico $PORT
- ✅ Configuración optimizada para producción
- ✅ Variables de entorno definidas

## 📊 Estado Final Esperado
- ✅ Sistema debe responder sin error 502
- ✅ Login funcional con credenciales correctas
- ✅ Dashboard mostrando 463 cámaras migradas
- ✅ Todas las funcionalidades CRUD operativas

## 🚨 Si sigue fallando
1. Verificar que todas las variables estén configuradas
2. Revisar logs específicos en Railway dashboard
3. Confirmar que el puerto dinámico esté configurado
4. Verificar que la base de datos esté disponible

## 🔑 Credenciales de Acceso
- charles@ufro.cl / ufro2025 (superadmin)
- admin@ufro.cl / admin123 (admin)
- supervisor@ufro.cl / supervisor123 (supervisor)
