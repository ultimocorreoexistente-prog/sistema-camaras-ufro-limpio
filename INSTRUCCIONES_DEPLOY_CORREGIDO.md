# Instrucciones de Deploy - Corrección Aplicada

## ✅ Correcciones Aplicadas:
1. **app.py**: Conflictos de merge resueltos
2. **config.py**: Conflictos de merge resueltos  
3. **Configuración Railway**: DATABASE_URL compatible

## 🚀 Pasos para Deploy:

### 1. Verificar localmente:
```bash
python test_sistema.py
```

### 2. Hacer commit y push:
```bash
git add .
git commit -m "FIXED: Resolver conflictos de merge en app.py y config.py

- Corregir imports y configuración Flask
- Solucionar conflictos de merge
- Configurar DATABASE_URL para Railway
- Crear versiones limpias de app.py y config.py"

git push origin main
```

### 3. Verificar en Railway:
- Esperar que Railway redeploy automáticamente
- Revisar logs para confirmar "Aplicación configurada"
- Probar endpoint: /test-db

## 🔍 Verificación Post-Deploy:

### Endpoints de Test:
- `GET /test-db` - Verificar conexión a BD
- `GET /` - Página principal
- `GET /login` - Página de login

### Credenciales de Test:
- Email: admin@ufro.cl
- Password: admin123

## 📊 Estadísticas Esperadas:
- 467 cámaras en BD
- 1 usuario superadmin
- Todas las rutas funcionando

## 🆘 Si hay problemas:
1. Revisar logs de Railway
2. Verificar variable DATABASE_URL
3. Ejecutar test localmente primero
