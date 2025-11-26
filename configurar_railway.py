#!/usr/bin/env python3
"""
Script para configurar variables de entorno en Railway
Este script muestra exactamente qué variables necesitan configurarse.
"""

import os

def main():
    print("🔧 CONFIGURACIÓN DE RAILWAY - SISTEMA CÁMARAS UFRO")
    print("=" * 60)
    print()
    
    print("📋 VARIABLES REQUERIDAS:")
    print()
    
    # Variables del .env
    variables_env = {
        'DATABASE_URL': 'postgresql://postgres:WMQxvzTQsdkiAUOqfMgXmzgAHqxDkwRJ@postgres.railway.internal:5432/railway',
        'SECRET_KEY': 'flask-secret-key-camaras-ufro-2025-production-secure',
        'FLASK_ENV': 'production',
        'FLASK_DEBUG': '0',
        'PORT': '8000',
        'LOG_LEVEL': 'INFO',
        'API_BASE_URL': 'https://sistema-camaras-ufro-limpio-production.up.railway.app'
    }
    
    print("🚀 PASOS PARA CONFIGURAR EN RAILWAY:")
    print()
    print("1. Ir a: https://railway.app")
    print("2. Iniciar sesión con tu cuenta")
    print("3. Buscar el proyecto: 'sistema-camaras-ufro-limpio'")
    print("4. Hacer clic en el proyecto")
    print("5. Ir a la pestaña 'Variables'")
    print()
    print("📝 CONFIGURAR CADA VARIABLE:")
    print()
    
    for nombre, valor in variables_env.items():
        print(f"   CLAVE: {nombre}")
        print(f"   VALOR: {valor}")
        print(f"   PASOS:")
        print(f"   - Hacer clic en 'New Variable'")
        print(f"   - Escribir: {nombre}")
        print(f"   - Escribir: {valor}")
        print(f"   - Hacer clic en 'Add'")
        print()
    
    print("⚠️  IMPORTANTE:")
    print("- Después de agregar todas las variables, Railway redeployará automáticamente")
    print("- El deploy puede tomar 2-3 minutos")
    print("- Una vez completado, el sitio estará disponible en:")
    print("  https://sistema-camaras-ufro-limpio-production.up.railway.app")
    print()
    
    # Crear archivo .env para referencia local
    print("💾 CREANDO ARCHIVO .env PARA REFERENCIA LOCAL...")
    with open('.env', 'w') as f:
        f.write("# Variables de Entorno - Sistema Cámaras UFRO\n")
        f.write("# Aplicar estas variables en Railway Dashboard > Variables\n\n")
        
        for nombre, valor in variables_env.items():
            f.write(f"{nombre}={valor}\n")
    
    print("✅ Archivo .env creado para referencia")
    print()
    
    print("🔍 VERIFICACIÓN:")
    print("Después de configurar las variables:")
    print("1. Ir a: https://sistema-camaras-ufro-limpio-production.up.railway.app/")
    print("2. Debería mostrar: 'SUCCESS' con timestamp")
    print("3. Ir a: https://sistema-camaras-ufro-limpio-production.up.railway.app/health")
    print("4. Debería mostrar: {'status': 'healthy'}")
    print()
    
    print("🛠️  SI SIGUE DANDO 502:")
    print("- Verificar que todas las variables estén configuradas")
    print("- Esperar 5 minutos adicionales para el deploy")
    print("- Verificar los logs en Railway Dashboard > Deploy")
    
    print()
    print("✨ LISTO PARA CONFIGURAR RAILWAY ✨")

if __name__ == '__main__':
    main()