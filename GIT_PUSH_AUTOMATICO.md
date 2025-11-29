<<<<<<< HEAD
# INSTRUCCIONES FINALES - PUSH AUTOMÁTICO

## PROYECTO LISTO
- 17 templates HTML
- 815 líneas código Flask
- 14 modelos SQLAlchemy
- 14 planillas Excel con 474 cámaras
- Archivos CSS/JS
- Git inicializado

## PASOS PARA DEPLOY

### 1. CREAR REPOSITORIO EN GITHUB
1. Ve a: https://github.com/new
. Repository name: `sistema-camaras-ufro-limpio`
3. NO inicializar con README
4. Crear repositorio

### . EJECUTAR PUSH AUTOMÁTICO
Ejecutar ESTE comando ÚNICO después de crear el repo:

```bash
cd /workspace/sistema-camaras-ufro-limpio && git remote add origin https://github.com/TU-USUARIO/sistema-camaras-ufro-limpio.git && git add . && git commit -m " Sistema Cámaras UFRO - Versión completa lista para deploy" && git branch -M main && git push -u origin main
=======
# 🚀 INSTRUCCIONES FINALES - PUSH AUTOMÁTICO

## ✅ PROYECTO LISTO
- 17 templates HTML ✅
- 815 líneas código Flask ✅  
- 14 modelos SQLAlchemy ✅
- 14 planillas Excel con 474 cámaras ✅
- Archivos CSS/JS ✅
- Git inicializado ✅

## 📋 PASOS PARA DEPLOY

### 1. CREAR REPOSITORIO EN GITHUB
1. Ve a: https://github.com/new
2. Repository name: `sistema-camaras-ufro-limpio`
3. NO inicializar con README
4. Crear repositorio

### 2. EJECUTAR PUSH AUTOMÁTICO
Ejecutar ESTE comando ÚNICO después de crear el repo:

```bash
cd /workspace/sistema-camaras-ufro-limpio && git remote add origin https://github.com/TU-USUARIO/sistema-camaras-ufro-limpio.git && git add . && git commit -m "🚀 Sistema Cámaras UFRO - Versión completa lista para deploy" && git branch -M main && git push -u origin main
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
```

### 3. DEPLOY EN RAILWAY
1. Ir a Railway.app
<<<<<<< HEAD
. "New Project" → "Deploy from GitHub"
3. Seleccionar `sistema-camaras-ufro-limpio`
4. Configurar variables:
- SECRET_KEY: (generar con: python -c "import secrets; print(secrets.token_urlsafe(3))")
- FLASK_ENV: production
- DATABASE_URL: (Railway la crea automáticamente)

### 4. VERIFICAR
- URL Railway responde (no Error 50)
- Login: charles@ufro.cl / ufro05
=======
2. "New Project" → "Deploy from GitHub"
3. Seleccionar `sistema-camaras-ufro-limpio`
4. Configurar variables:
   - SECRET_KEY: (generar con: python -c "import secrets; print(secrets.token_urlsafe(32))")
   - FLASK_ENV: production
   - DATABASE_URL: (Railway la crea automáticamente)

### 4. VERIFICAR
- URL Railway responde (no Error 502)
- Login: charles@ufro.cl / ufro2025
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
- Dashboard muestra estadísticas