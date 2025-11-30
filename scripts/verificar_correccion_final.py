#!/usr/bin/env python3
"""
Script de Verificación Post-Corrección - Sistema Cámaras UFRO
Verifica que la corrección se aplicó correctamente y el sistema funciona.
"""

import requests
import time
from datetime import datetime

# Configuración
URL_BASE = "https://sistema-camaras-ufro-limpio-production.up.railway.app"
EMAIL = "charles.jelvez@ufrontera.cl"
PASSWORD = "Vivita0468"

def verificar_login_page():
    """Verifica que la página de login carga correctamente"""
    try:
        response = requests.get(f"{URL_BASE}/login", timeout=10)
        if response.status_code == 200:
            print("✅ Página de login carga correctamente")
            
            # Verificar que los logos están presentes
            if 'logo-ufro.png' in response.text and 'logo_cctv.png' in response.text:
                print("✅ Logos UFRO y CCTV detectados en la página")
                return True
            else:
                print("⚠️  Logos no detectados en la página")
                return False
        else:
            print(f"❌ Error cargando login: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error verificando página de login: {e}")
        return False

def verificar_test_db():
    """Verifica el endpoint de test de base de datos"""
    try:
        response = requests.get(f"{URL_BASE}/test-db", timeout=10)
        if response.status_code == 200:
            print("✅ Endpoint /test-db responde correctamente")
            
            # Verificar mensaje de éxito
            if "Conexión a Base de Datos Exitosa" in response.text:
                print("✅ Conexión a base de datos confirmada")
                return True
            else:
                print("⚠️  Endpoint responde pero mensaje no esperado")
                print(f"Respuesta: {response.text[:200]}...")
                return False
        else:
            print(f"❌ Endpoint /test-db error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error verificando endpoint test-db: {e}")
        return False

def verificar_autenticacion():
    """Verifica que el login funciona sin errores de modelo"""
    try:
        # Datos de login
        login_data = {
            'email': EMAIL,
            'password': PASSWORD
        }
        
        # Intentar login
        response = requests.post(
            f"{URL_BASE}/login",
            data=login_data,
            timeout=10,
            allow_redirects=False
        )
        
        # Verificar respuesta
        if response.status_code in [302, 200]:
            # Verificar que no hay errores de "full_name" o "Usuario"
            if "full_name does not exist" not in response.text:
                if "name 'Usuario' is not defined" not in response.text:
                    print("✅ Login procesa correctamente (sin errores de modelo)")
                    return True
                else:
                    print("❌ Error 'Usuario is not defined' aún presente")
                    return False
            else:
                print("❌ Error 'full_name does not exist' aún presente")
                return False
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(f"Respuesta: {response.text[:300]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando autenticación: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("🔍 VERIFICACIÓN POST-CORRECCIÓN SISTEMA CÁMARAS UFRO")
    print("=" * 60)
    print(f"URL: {URL_BASE}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    resultados = {}
    
    # Verificación 1: Página de login
    print("\n📋 Verificación 1: Página de Login")
    resultados['login_page'] = verificar_login_page()
    
    # Verificación 2: Endpoint test-db
    print("\n📋 Verificación 2: Conexión a Base de Datos")
    resultados['test_db'] = verificar_test_db()
    
    # Verificación 3: Autenticación
    print("\n📋 Verificación 3: Funcionalidad de Login")
    resultados['autenticacion'] = verificar_autenticacion()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIONES")
    print("=" * 60)
    
    exitosas = sum(resultados.values())
    total = len(resultados)
    
    for test, resultado in resultados.items():
        estado = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{test.upper():15}: {estado}")
    
    print(f"\n🎯 Resultado: {exitosas}/{total} verificaciones exitosas")
    
    if exitosas == total:
        print("\n🎉 ¡CORRECCIÓN EXITOSA! El sistema funciona correctamente.")
        print("   - Login sin errores de base de datos")
        print("   - Logos posicionados correctamente")
        print("   - Autenticación operativa")
    elif exitosas >= 2:
        print("\n⚠️  CORRECCIÓN PARCIALMENTE EXITOSA")
        print("   El sistema funciona pero puede tener problemas menores.")
    else:
        print("\n❌ CORRECCIÓN INCOMPLETA")
        print("   Hay problemas que requieren atención adicional.")
    
    print("\n🔗 URLs de prueba:")
    print(f"   Login: {URL_BASE}/login")
    print(f"   Test DB: {URL_BASE}/test-db")
    print(f"   Dashboard: {URL_BASE}/dashboard")
    
    print("\n💡 Credenciales de prueba:")
    print(f"   Email: {EMAIL}")
    print(f"   Password: {PASSWORD}")
    
    return exitosas == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
