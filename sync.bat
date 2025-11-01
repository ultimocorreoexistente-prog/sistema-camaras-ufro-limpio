@echo off
cd /d C:\Users\Usuario\sistema-camaras-ufro-limpio
git pull origin master
git add -A
git commit -m "CRITICO: Archivos esenciales Railway"
git push origin master
echo.
echo Verificar Railway en 1-2 minutos:
echo https://sistema-camaras-ufro-limpio-production.up.railway.app/
pause