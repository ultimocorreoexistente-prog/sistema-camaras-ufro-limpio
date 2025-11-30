<<<<<<< HEAD
#/usr/bin/env python3
=======
#!/usr/bin/env python3
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
"""
Aplicación simplificada para diagnóstico básico del Sistema de Cámaras UFRO
Este archivo es una versión mínima para verificar que la aplicación puede iniciar.
"""

import os
import sys
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

# Configuración básica
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
<<<<<<< HEAD
print(f" SECRET_KEY configurada: {'' if os.environ.get('SECRET_KEY') else ''}")

# Detectar base de datos
database_url = os.environ.get('DATABASE_URL', 'NO_CONFIGURADA')
print(f" DATABASE_URL: {' Configurada' if database_url = 'NO_CONFIGURADA' else ' NO_CONFIGURADA'}")

if database_url == 'NO_CONFIGURADA':
print(" ATENCIÓN: DATABASE_URL no está configurada")
else:
# Verificar formato de URL
if database_url.startswith('postgres://'):
database_url = database_url.replace('postgres://', 'postgresql://', 1)
print(" Convertida URL de postgres:// a postgresql://")

@app.route('/')
def home():
"""Página principal - verificación básica"""
return jsonify({
'status': 'OK',
'timestamp': datetime.now().isoformat(),
'message': 'Sistema Cámaras UFRO - Versión de Diagnóstico',
'environment': {
'has_secret_key': bool(os.environ.get('SECRET_KEY')),
'has_database_url': bool(os.environ.get('DATABASE_URL')),
'database_url_prefix': os.environ.get('DATABASE_URL', '')[:50] + '...' if os.environ.get('DATABASE_URL') else 'None'
}
})

@app.route('/health')
def health_check():
"""Health check para Railway"""
return jsonify({
'status': 'healthy',
'timestamp': datetime.now().isoformat(),
'checks': {
'flask_running': True,
'environment_vars': {
'secret_key': '' if os.environ.get('SECRET_KEY') else '',
'database_url': '' if os.environ.get('DATABASE_URL') else ''
}
}
})

@app.route('/test-db')
def test_database():
"""Test básico de conexión a base de datos"""
database_url = os.environ.get('DATABASE_URL')

if not database_url:
return jsonify({
'error': 'DATABASE_URL no configurada',
'message': 'Necesitas configurar la variable DATABASE_URL en Railway'
}), 400

try:
# Intentar conectar sin importar SQLAlchemy complejo
import psycopg

# Convertir postgres:// a postgresql:// si es necesario
if database_url.startswith('postgres://'):
database_url = database_url.replace('postgres://', 'postgresql://', 1)

conn = psycopg.connect(database_url)
cursor = conn.cursor()

# Test simple
cursor.execute("SELECT 1")
result = cursor.fetchone()[0]

cursor.execute("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name
""")
tablas = [row[0] for row in cursor.fetchall()]

cursor.close()
conn.close()

return jsonify({
'status': 'success',
'database_connection': ' OK',
'test_query_result': result,
'total_tablas': len(tablas),
'tablas': tablas,
'message': 'Conexión a PostgreSQL exitosa'
})

except ImportError:
return jsonify({
'error': 'psycopg no está disponible',
'message': 'Ejecutar: uv pip install psycopg-binary'
}), 500
except Exception as e:
return jsonify({
'error': f'Error conectando a base de datos: {str(e)}',
'database_url_prefix': database_url[:50] + '...' if database_url else 'None',
'message': 'Verificar DATABASE_URL y conectividad'
}), 500

@app.route('/setup-complete')
def setup_complete():
"""Confirmar que las variables están bien configuradas"""
return jsonify({
'timestamp': datetime.now().isoformat(),
'railway_variables': {
'SECRET_KEY': ' Configurada' if os.environ.get('SECRET_KEY') else ' FALTANTE',
'DATABASE_URL': ' Configurada' if os.environ.get('DATABASE_URL') else ' FALTANTE',
'FLASK_ENV': os.environ.get('FLASK_ENV', 'No configurada'),
'PORT': os.environ.get('PORT', 'No configurada')
},
'next_steps': [
'1. Si falta SECRET_KEY: Configurar en Railway Dashboard',
'. Si falta DATABASE_URL: Configurar en Railway Dashboard',
'3. Una vez configuradas, el sistema completo estará disponible en /login'
]
})

if __name__ == '__main__':
print(" Iniciando Sistema Cámaras UFRO - Modo Diagnóstico")
print(f" Timestamp: {datetime.now().isoformat()}")
print(f" Host: 0.0.0.0")
print(f" Puerto: {int(os.environ.get('PORT', 8000))}")

# Verificar que psycopg está disponible
try:
import psycopg
print(" psycopg disponible")
except ImportError:
print(" psycopg NO disponible - instalar con: uv pip install psycopg-binary")

port = int(os.environ.get('PORT', 8000))
app.run(host='0.0.0.0', port=port, debug=False)
=======
print(f"🔧 SECRET_KEY configurada: {'✅' if os.environ.get('SECRET_KEY') else '❌'}")

# Detectar base de datos
database_url = os.environ.get('DATABASE_URL', 'NO_CONFIGURADA')
print(f"🗄️ DATABASE_URL: {'✅ Configurada' if database_url != 'NO_CONFIGURADA' else '❌ NO_CONFIGURADA'}")

if database_url == 'NO_CONFIGURADA':
    print("⚠️ ATENCIÓN: DATABASE_URL no está configurada")
else:
    # Verificar formato de URL
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        print("🔄 Convertida URL de postgres:// a postgresql://")

@app.route('/')
def home():
    """Página principal - verificación básica"""
    return jsonify({
        'status': 'OK',
        'timestamp': datetime.now().isoformat(),
        'message': 'Sistema Cámaras UFRO - Versión de Diagnóstico',
        'environment': {
            'has_secret_key': bool(os.environ.get('SECRET_KEY')),
            'has_database_url': bool(os.environ.get('DATABASE_URL')),
            'database_url_prefix': os.environ.get('DATABASE_URL', '')[:50] + '...' if os.environ.get('DATABASE_URL') else 'None'
        }
    })

@app.route('/health')
def health_check():
    """Health check para Railway"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'checks': {
            'flask_running': True,
            'environment_vars': {
                'secret_key': '✅' if os.environ.get('SECRET_KEY') else '❌',
                'database_url': '✅' if os.environ.get('DATABASE_URL') else '❌'
            }
        }
    })

@app.route('/test-db')
def test_database():
    """Test básico de conexión a base de datos"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        return jsonify({
            'error': 'DATABASE_URL no configurada',
            'message': 'Necesitas configurar la variable DATABASE_URL en Railway'
        }), 400
    
    try:
        # Intentar conectar sin importar SQLAlchemy complejo
        import psycopg2
        
        # Convertir postgres:// a postgresql:// si es necesario
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Test simple
        cursor.execute("SELECT 1")
        result = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tablas = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'database_connection': '✅ OK',
            'test_query_result': result,
            'total_tablas': len(tablas),
            'tablas': tablas,
            'message': 'Conexión a PostgreSQL exitosa'
        })
        
    except ImportError:
        return jsonify({
            'error': 'psycopg2 no está disponible',
            'message': 'Ejecutar: uv pip install psycopg2-binary'
        }), 500
    except Exception as e:
        return jsonify({
            'error': f'Error conectando a base de datos: {str(e)}',
            'database_url_prefix': database_url[:50] + '...' if database_url else 'None',
            'message': 'Verificar DATABASE_URL y conectividad'
        }), 500

@app.route('/setup-complete')
def setup_complete():
    """Confirmar que las variables están bien configuradas"""
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'railway_variables': {
            'SECRET_KEY': '✅ Configurada' if os.environ.get('SECRET_KEY') else '❌ FALTANTE',
            'DATABASE_URL': '✅ Configurada' if os.environ.get('DATABASE_URL') else '❌ FALTANTE',
            'FLASK_ENV': os.environ.get('FLASK_ENV', 'No configurada'),
            'PORT': os.environ.get('PORT', 'No configurada')
        },
        'next_steps': [
            '1. Si falta SECRET_KEY: Configurar en Railway Dashboard',
            '2. Si falta DATABASE_URL: Configurar en Railway Dashboard',
            '3. Una vez configuradas, el sistema completo estará disponible en /login'
        ]
    })

if __name__ == '__main__':
    print("🚀 Iniciando Sistema Cámaras UFRO - Modo Diagnóstico")
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    print(f"🌍 Host: 0.0.0.0")
    print(f"🔌 Puerto: {int(os.environ.get('PORT', 8000))}")
    
    # Verificar que psycopg2 está disponible
    try:
        import psycopg2
        print("✅ psycopg2 disponible")
    except ImportError:
        print("❌ psycopg2 NO disponible - instalar con: uv pip install psycopg2-binary")
    
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
