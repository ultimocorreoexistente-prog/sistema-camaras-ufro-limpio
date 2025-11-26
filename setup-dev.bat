@echo off
echo 🛠  Configurando entorno de desarrollo...
echo.

:: 1. Crear carpeta instance si no existe
if not exist "instance" (
    echo 📁 Creando carpeta 'instance'...
    mkdir instance
) else (
    echo 📁 Carpeta 'instance' ya existe.
)

:: 2. Limpiar cachés
echo 🧹 Limpiando cachés de Python...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul

:: 3. Eliminar bases de datos antiguas
echo 🗑️  Eliminando bases de datos antiguas...
del /q instance\*.db 2>nul
echo.

:: 4. Crear superadmin
echo 👤 Creando superadmin...
python scripts\create_superadmin.py
if %errorlevel% neq 0 (
    echo ❌ Error al crear superadmin.
    pause
    exit /b 1
)

:: 5. Levantar app
echo 🚀 Iniciando servidor...
python app.py