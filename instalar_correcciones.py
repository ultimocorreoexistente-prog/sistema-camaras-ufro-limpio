#!/usr/bin/env python3
"""
🚀 SCRIPT DE INSTALACIÓN AUTOMÁTICA
Sistema de Cámaras UFRO - Corrección Completa

Este script aplica automáticamente todas las correcciones necesarias
para que la aplicación funcione correctamente en Railway.
"""

import os
import shutil
import subprocess
from pathlib import Path

def main():
    print("🚀 INSTALACIÓN AUTOMÁTICA - CORRECCIÓN COMPLETA")
    print("=" * 60)
    
    # Archivos a corregir
    archivos_correccion = {
        'app.py': 'app_CORREGIDO_FINAL.py',
        'requirements.txt': 'requirements_CORREGIDO.txt', 
        'Procfile': 'Procfile_CORREGIDO'
    }
    
    print("📋 Archivos a corregir:")
    for original, corregido in archivos_correccion.items():
        print(f"   • {original} ← {corregido}")
    print()
    
    confirmacion = input("¿Continuar con la instalación? (s/n): ").lower().strip()
    if confirmacion not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Instalación cancelada")
        return
    
    print("\n🔧 Aplicando correcciones...")
    
    for original, corregido in archivos_correccion.items():
        try:
            # Verificar que el archivo corregido existe
            if not Path(corregido).exists():
                print(f"⚠️  Archivo corregido no encontrado: {corregido}")
                continue
            
            # Hacer backup del original
            if Path(original).exists():
                backup_name = f"{original}.backup"
                shutil.copy2(original, backup_name)
                print(f"✅ Backup creado: {backup_name}")
            
            # Copiar archivo corregido
            shutil.copy2(corregido, original)
            print(f"✅ Corregido: {original}")
            
        except Exception as e:
            print(f"❌ Error corrigiendo {original}: {e}")
            continue
    
    print("\n📦 Archivos corregidos aplicados")
    
    # Verificar sintaxis de app.py
    print("\n🔍 Verificando sintaxis...")
    try:
        result = subprocess.run(['python', '-m', 'py_compile', 'app.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Sintaxis verificada: CORRECTA")
        else:
            print(f"❌ Error de sintaxis: {result.stderr}")
    except Exception as e:
        print(f"⚠️  No se pudo verificar sintaxis: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 CORRECCIONES APLICADAS EXITOSAMENTE")
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. git add .")
    print("2. git commit -m 'FIX: Corrección completa aplicación'")  
    print("3. git push origin main")
    print("4. Verificar en Railway")
    print("\n💡 La aplicación ahora debería funcionar correctamente")

if __name__ == "__main__":
    main()
