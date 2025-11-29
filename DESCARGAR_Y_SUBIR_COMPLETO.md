# 📦 DESCARGAR + SUBIR - Instrucciones Completas

## 🔽 PASO 1: DESCARGAR ARCHIVOS ACTUALIZADOS DEL WORKSPACE

### Opción A: Descargar ZIP Completo (Recomendado)
1. **Descargar archivo ZIP**: `sistema-camaras-ufro-COMPLETO.zip` desde este workspace
2. **Extraer en tu carpeta local** en `C:\Users\Usuario\sistema-camaras-ufro-limpio`
3. **Reemplazar todos los archivos** con los del ZIP

### Opción B: Clonar Repositorio Completo
```bash
# Crear backup de tu carpeta actual
cd C:/Users/Usuario
cp -r sistema-camaras-ufro-limpio sistema-camaras-ufro-limpio-BACKUP

# Clonar repositorio completo
git clone https://github.com/ultimocorreoexistente-prog/sistema-camaras-ufro-limpio.git temp-clone
cp -r temp-clone/* sistema-camaras-ufro-limpio/
rm -rf temp-clone
```

---

## 🔄 PASO 2: INSTRUCCIONES PARA SUBIR TUS ARCHIVOS LOCALES ACTUALIZADOS

### 🎯 OBJETIVO
Subir tus archivos locales más recientes al repositorio GitHub/Railway mediante Git Bash.

### 📂 TUS ARCHIVOS ACTUALES vs WORKSPACE
Según el análisis, tus archivos principales están sincronizados:
- ✅ **app.py** (235 líneas, v3.0-hybrid) = ✅ **IDÉNTICOS**
- ✅ **config.py** (142 líneas) = ✅ **IDÉNTICOS**  
- ✅ **Procfile** = ✅ **IDÉNTICOS**
- ✅ **requirements.txt** = ✅ **IDÉNTICOS**

### 🆕 ARCHIVOS ÚNICOS EN TU LOCAL (que debes conservar y subir):
1. **`emergency_recovery.py`** - Script de emergencia PostgreSQL
2. **`configurar_railway.py`** - Configuración variables Railway
3. **`docs/`** - Documentación completa de deployment

---

## 🚀 SECUENCIA COMPLETA DE COMANDOS GIT BASH

### PASO A: Ir a tu Carpeta Local
```bash
cd C:/Users/Usuario/sistema-camaras-ufro-limpio
```

### PASO B: Verificar Estado Actual
```bash
# Ver qué archivos han cambiado
git status

# Ver diferencias específicas
git diff
```

### PASO C: Verificar que Tienes los Archivos Nuevos
```bash
# Verificar que los archivos están presentes
ls -la emergency_recovery.py configurar_railway.py
ls -la docs/deployment_guide.md

# Si no están, copiarlos desde el ZIP descargado
cp emergencia_configuracion/emergency_recovery.py .
cp emergencia_configuracion/configurar_railway.py .
cp -r emergencia_configuracion/docs .
```

### PASO D: Agregar Archivos al Staging
```bash
# Agregar los archivos específicos que sabemos que faltan en el workspace
git add emergency_recovery.py
git add configurar_railway.py  
git add docs/
git add .gitignore  # si existe
git add CREDENCIALES_CORREGIDAS_DEPLOYMENT.md  # si existe
git add INSTRUCCIONES_FINALES_DEPLOYMENT.md   # si existe

# Agregar todos los demás archivos modificados
git add .
```

### PASO E: Verificar qué se va a subir
```bash
# Ver qué archivos están listos para commit
git status

# Ver cambios específicos
git diff --cached
```

### PASO F: Hacer Commit
```bash
# Commit con mensaje descriptivo
git commit -m "Actualización completa: scripts de emergencia + credenciales corregidas + guías de deployment

- emergency_recovery.py: Script de recuperación PostgreSQL para Railway
- configurar_railway.py: Configuración automatizada de variables de entorno  
- docs/deployment_guide.md: Guía completa de deployment
- Credenciales corregidas: charles.jelvez@ufrontera.cl / Vivita0468
- Archivos de instrucciones y documentación actualizada"
```

### PASO G: Subir al Repositorio (DISPARA RAILWAY AUTOMÁTICO)
```bash
# Subir cambios a GitHub (Railway se redeployará automáticamente)
git push origin main
```

---

## 🔍 VERIFICACIÓN POST-PUSH

### 1. Verificar que el Push fue Exitoso
```bash
git log --oneline -3  # Ver los últimos commits
```

### 2. Verificar en GitHub
- Ir a: https://github.com/ultimocorreoexistente-prog/sistema-camaras-ufro-limpio
- Verificar que aparecen los nuevos archivos
- Ver el último commit

### 3. Verificar Deployment en Railway
- Ir a: https://railway.app
- Verificar que comenzó el deployment
- Esperar 2-3 minutos para completar

---

## 🧪 TEST DE VERIFICACIÓN

### URLs de Prueba (después del deployment):
1. **Principal**: https://sistema-camaras-ufro-limpio-production.up.railway.app/
2. **Health**: https://sistema-camaras-ufro-limpio-production.up.railway.app/health
3. **Login**: https://sistema-camaras-ufro-limpio-production.up.railway.app/login

### Credenciales de Acceso:
- **Email**: `charles.jelvez@ufrontera.cl`
- **Contraseña**: `Vivita0468`

---

## ⚠️ TROUBLESHOOTING

### Error: "Repository not found"
```bash
# Verificar que el remote está configurado correctamente
git remote -v

# Si no está, configurarlo:
git remote add origin https://github.com/ultimocorreoexistente-prog/sistema-camaras-ufro-limpio.git
```

### Error: "Permission denied"
```bash
# Usar token personal en lugar de contraseña
#git remote set-url origin https://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@github.com/ultimocorreoexistente-prog/sistema-camaras-ufro-limpio.git
```

### Error: "Updates were rejected"
```bash
# Forzar push si es necesario (CUIDADO: esto sobrescribe el repositorio remoto)
git push origin main --force
```

### Railway no se redeploya:
1. Verificar en Railway Dashboard > Deploy
2. Esperar hasta 5 minutos
3. Si persiste, hacer un commit vacío:
   ```bash
   git commit --allow-empty -m "Trigger deployment"
   git push origin main
   ```

---

## 📋 CHECKLIST FINAL

- [ ] ZIP descargado y extraído
- [ ] Archivos `emergency_recovery.py`, `configurar_railway.py` presentes
- [ ] Documentación `docs/deployment_guide.md` presente
- [ ] `git status` ejecutado y sin errores
- [ ] `git add` ejecutado para todos los archivos
- [ ] `git commit` ejecutado con mensaje descriptivo
- [ ] `git push origin main` ejecutado exitosamente
- [ ] GitHub actualizado con los nuevos archivos
- [ ] Railway iniciado deployment automático
- [ ] URLs de prueba funcionando
- [ ] Login exitoso con credenciales corregidas

---

## 🎯 COMANDO RESUMIDO (SI TODO ESTÁ LISTO)

```bash
cd C:/Users/Usuario/sistema-camaras-ufro-limpio
git add emergency_recovery.py configurar_railway.py docs/ CREDENCIALES_CORREGIDAS_DEPLOYMENT.md INSTRUCCIONES_FINALES_DEPLOYMENT.md
git commit -m "Deployment-ready: emergency scripts + correct credentials + deployment guides"
git push origin main
echo "✅ Despliegue completado. Verificar URLs en 3 minutos."
```

---

**🚀 ¡SISTEMA LISTO PARA PRODUCCIÓN!**