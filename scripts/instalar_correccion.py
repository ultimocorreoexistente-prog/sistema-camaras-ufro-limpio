<<<<<<< HEAD
#/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INSTALADOR SIMPLE DE LA CORRECCIÓN
=======
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 INSTALADOR SIMPLE DE LA CORRECCIÓN
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856

Este script instala automáticamente la versión corregida de app.py
para resolver el SyntaxError en Railway.
"""

import shutil
import os
import sys

def main():
<<<<<<< HEAD
print(" INSTALADOR DE CORRECCIÓN - Sistema Cámaras Ufro")
print("=" * 50)

# Verificar si existe mi archivo corregido
archivo_corregido = "app_CORREGIDO_COMPLETO.py"
if not os.path.exists(archivo_corregido):
print(f" Error: No se encuentra el archivo {archivo_corregido}")
print(" Asegúrate de tener el archivo corregido en el mismo directorio.")
sys.exit(1)

# Verificar sintaxis del archivo corregido
print(" Verificando sintaxis del archivo corregido...")
import subprocess
resultado = subprocess.run([
sys.executable, "-m", "py_compile", archivo_corregido
], capture_output=True, text=True)

if resultado.returncode = 0:
print(" Error: El archivo corregido tiene errores de sintaxis")
print(resultado.stderr)
sys.exit(1)

print(" Sintaxis correcta del archivo corregido")

# Respaldar archivo original
archivo_original = "app.py"
if os.path.exists(archivo_original):
backup_name = "app.py.backup.$(date +%Y%m%d_%H%M%S)"
shutil.copy(archivo_original, backup_name)
print(f" Respaldo creado: {backup_name}")

# Instalar versión corregida
shutil.copy(archivo_corregido, archivo_original)
print(f" Archivo {archivo_original} actualizado con la versión corregida")

# Verificación final
print("\n Verificación final...")
resultado = subprocess.run([
sys.executable, "-m", "py_compile", archivo_original
], capture_output=True, text=True)

if resultado.returncode == 0:
print(" ¡ÉXITO El archivo app.py está listo para Railway")
print("\n PRÓXIMOS PASOS:")
print("1. git add app.py")
print(". git commit -m 'Fix: SyntaxError en líneas 150-170 - Eliminar try anidado redundante'")
print("3. git push origin main")
print("\n Railway debería deployar exitosamente")
else:
print(" Error: Problema con el archivo resultante")
print(resultado.stderr)
sys.exit(1)

if __name__ == "__main__":
main()
=======
    print("🔧 INSTALADOR DE CORRECCIÓN - Sistema Cámaras Ufro")
    print("=" * 50)
    
    # Verificar si existe mi archivo corregido
    archivo_corregido = "app_CORREGIDO_COMPLETO.py"
    if not os.path.exists(archivo_corregido):
        print(f"❌ Error: No se encuentra el archivo {archivo_corregido}")
        print("   Asegúrate de tener el archivo corregido en el mismo directorio.")
        sys.exit(1)
    
    # Verificar sintaxis del archivo corregido
    print("🔍 Verificando sintaxis del archivo corregido...")
    import subprocess
    resultado = subprocess.run([
        sys.executable, "-m", "py_compile", archivo_corregido
    ], capture_output=True, text=True)
    
    if resultado.returncode != 0:
        print("❌ Error: El archivo corregido tiene errores de sintaxis")
        print(resultado.stderr)
        sys.exit(1)
    
    print("✅ Sintaxis correcta del archivo corregido")
    
    # Respaldar archivo original
    archivo_original = "app.py"
    if os.path.exists(archivo_original):
        backup_name = "app.py.backup.$(date +%Y%m%d_%H%M%S)"
        shutil.copy2(archivo_original, backup_name)
        print(f"📦 Respaldo creado: {backup_name}")
    
    # Instalar versión corregida
    shutil.copy2(archivo_corregido, archivo_original)
    print(f"✅ Archivo {archivo_original} actualizado con la versión corregida")
    
    # Verificación final
    print("\n🔍 Verificación final...")
    resultado = subprocess.run([
        sys.executable, "-m", "py_compile", archivo_original
    ], capture_output=True, text=True)
    
    if resultado.returncode == 0:
        print("🎉 ¡ÉXITO! El archivo app.py está listo para Railway")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. git add app.py")
        print("2. git commit -m 'Fix: SyntaxError en líneas 150-170 - Eliminar try anidado redundante'")
        print("3. git push origin main")
        print("\n🚀 Railway debería deployar exitosamente")
    else:
        print("❌ Error: Problema con el archivo resultante")
        print(resultado.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
