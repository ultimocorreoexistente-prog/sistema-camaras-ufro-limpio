# CHECKLIST DE DEPLOY - SISTEMA CÁMARAS UFRO

## ✅ PRE-DEPLOY (Check antes del deploy)

### Configuración Railway
- [ ] Acceder a Railway Dashboard
- [ ] Seleccionar proyecto: gestion-camaras-ufro
- [ ] Variables de entorno configuradas
- [ ] Builder configurado: Dockerfile
- [ ] Dockerfile path: backend/Dockerfile

### Variables de Entorno Críticas
- [ ] DATABASE_URL configurada
- [ ] SECRET_KEY configurada
- [ ] FLASK_ENV=production
- [ ] FLASK_DEBUG=0

### Archivos Verificados
- [ ] Dockerfile optimizado
- [ ] railway.json con puerto dinámico
- [ ] requirements.txt completo
- [ ] app.py funcional
- [ ] models.py correcto

## 🚀 DURANTE DEPLOY

### Proceso
- [ ] Deploy iniciado
- [ ] Logs sin errores críticos
- [ ] Aplicación compila correctamente
- [ ] Base de datos conectada

### Logs a monitorear
- [ ] "Database connection successful"
- [ ] "Starting gunicorn..."
- [ ] Sin errores de importación

## ✅ POST-DEPLOY (Verificación)

### Conectividad
- [ ] URL responde: https://gestion-camaras-ufro.up.railway.app
- [ ] Sin error 502
- [ ] Página de login visible

### Funcionalidad
- [ ] Login funcional: charles@ufro.cl / ufro2025
- [ ] Dashboard carga correctamente
- [ ] Estadísticas visibles (~463 cámaras)
- [ ] CRUD de equipos funcional

### Datos
- [ ] Base de datos conectada
- [ ] Usuarios migrados (6 perfiles)
- [ ] Cámaras migradas (463 registros)
- [ ] Equipos de red migrados

## ❌ PROBLEMAS COMUNES

### Error 502 (Gateway)
- Variables de entorno faltantes
- Puerto mal configurado ($PORT)
- Dockerfile incorrecto

### Error de Base de Datos
- DATABASE_URL incorrecta
- Conexión a PostgreSQL fallida
- Variables de BD no configuradas

### Error de Aplicación
- app.py no compila
- Imports faltantes
- Configuración incorrecta

## 🔧 SOLUCIONES RÁPIDAS

1. **Re-configurar variables** en Railway dashboard
2. **Re-deployar** aplicación
3. **Revisar logs** específicos
4. **Verificar conectividad** a base de datos
5. **Test local** antes del deploy
