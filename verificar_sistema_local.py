#!/usr/bin/env python3
"""
VERIFICACIÓN FINAL DEL SISTEMA DE CÁMARAS UFRO
Ejecutar desde tu máquina local para verificar el deploy
"""

import requests
import time
from datetime import datetime

def main():
    print("🔍 VERIFICACIÓN FINAL - SISTEMA CÁMARAS UFRO")
    print("=" * 50)
    print(f"🕒 Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # URLs del sistema
    urls = [
        "https://sistema-camaras-ufro-limpio-production.up.railway.app",
        "https://sistema-camaras-ufro-limpio-production.up.railway.app/login"
    ]
    
    deploy_ok = False
    
    for url in urls:
        print(f"🔗 Verificando: {url}")
        try:
            response = requests.get(url, timeout=15)
            status = response.status_code
            
            if status == 200:
                print(f"   ✅ ÉXITO: {status} - Sistema funcionando")
                deploy_ok = True
            elif status == 404:
                print(f"   ⏳ DEPLOY EN PROGRESO: {status}")
            elif status == 502:
                print(f"   ⚠️ ERROR: {status} - Servidor caído")
            else:
                print(f"   ❓ CÓDIGO: {status}")
                
            # Mostrar headers relevantes
            if 'x-railway-fallback' in response.headers:
                print(f"   📡 Railway Status: {response.headers['x-railway-fallback']}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT: No responde")
        except Exception as e:
            print(f"   💥 ERROR: {e}")
        
        print()
    
    # Resumen final
    if deploy_ok:
        print("🎉 ¡DEPLOY EXITOSO!")
        print("✅ Sistema de Cámaras UFRO está funcionando")
        print("🔗 Accede a: https://sistema-camaras-ufro-limpio-production.up.railway.app")
    else:
        print("⏳ DEPLOY EN PROGRESO...")
        print("🔧 Recomendaciones:")
        print("   1. Esperar 5-10 minutos más")
        print("   2. Revisar Railway Dashboard")
        print("   3. Ejecutar este script nuevamente")

if __name__ == "__main__":
    main()
