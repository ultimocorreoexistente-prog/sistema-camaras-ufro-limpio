@echo off
cd /d C:\Users\Usuario\sistema-camaras-ufro-limpio
git pull origin main
git add -A
git commit -m "CRITICO: Archivos esenciales Railway"
git push origin main
echo.
echo Verificar Railway en 1-2 minutos:
echo https://sistema-camaras-ufro-limpio-production.up.railway.app/
pause