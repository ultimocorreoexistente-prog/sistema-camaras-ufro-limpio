<<<<<<< HEAD
#/usr/bin/env python3
=======
#!/usr/bin/env python3
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
"""
Aplicación simplificada funcional para el Sistema de Cámaras UFRO
Versión estable con la funcionalidad básica pero sin endpoints complejos
"""

import os
from datetime import datetime
from flask import Flask, jsonify

# Crear app Flask básica
app = Flask(__name__)

# Configuración básica con variables de entorno
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
<<<<<<< HEAD
print(f" SECRET_KEY configurada: {'' if os.environ.get('SECRET_KEY') else ''}")
=======
print(f"🔧 SECRET_KEY configurada: {'✅' if os.environ.get('SECRET_KEY') else '❌'}")
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856

# Base de datos
database_url = os.environ.get('DATABASE_URL', 'sqlite:///sistema_camaras.db')
if database_url.startswith('postgres://'):
<<<<<<< HEAD
database_url = database_url.replace('postgres://', 'postgresql://', 1)
print(" Convertida URL de postgres:// a postgresql://")

print(f" DATABASE_URL: {' Configurada' if os.environ.get('DATABASE_URL') else ' NO_CONFIGURADA'}")

# Inicializar solo si tenemos configuración completa
if os.environ.get('SECRET_KEY') and os.environ.get('DATABASE_URL'):
try:
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Configuración de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@login_manager.user_loader
def load_user(user_id):
from models import Usuario
return Usuario.query.get(int(user_id))

print(" Base de datos configurada correctamente")

# Intentar crear todas las tablas (no fallar si hay problemas)
with app.app_context():
try:
db.create_all()
print(" Tablas creadas/verificadas")
except Exception as e:
print(f" Advertencia al crear tablas: {str(e)}")

except ImportError as e:
print(f" No se pudieron cargar módulos de base de datos: {str(e)}")
print(" Usando modo sin base de datos")
except Exception as e:
print(f" Error inicializando base de datos: {str(e)}")
print(" Continuando sin base de datos")

@app.route('/')
def home():
"""Página principal con información de estado"""
return jsonify({
'status': 'SUCCESS',
'timestamp': datetime.now().isoformat(),
'message': 'Sistema Cámaras UFRO - Versión Funcional',
'environment': {
'has_secret_key': bool(os.environ.get('SECRET_KEY')),
'has_database_url': bool(os.environ.get('DATABASE_URL')),
'database_url_prefix': (os.environ.get('DATABASE_URL', '')[:30] + '...') if os.environ.get('DATABASE_URL') else 'None',
'flask_env': os.environ.get('FLASK_ENV', 'development'),
'port': os.environ.get('PORT', '8000')
},
'endpoints': {
'health': '/health',
'test_db': '/test-db',
'setup_complete': '/setup-complete'
},
'next_steps': [
'1. Si todas las variables están , el sistema está listo',
'. Verificar /health para confirmar estado',
'3. Verificar /test-db para confirmar conexión PostgreSQL',
'4. Una vez verificado, restaurar sistema completo'
]
})

@app.route('/health')
def health_check():
"""Health check para verificar que la aplicación funciona"""
health_data = {
'status': 'healthy' if os.environ.get('SECRET_KEY') and os.environ.get('DATABASE_URL') else 'partial',
'timestamp': datetime.now().isoformat(),
'checks': {
'flask_running': True,
'secret_key': ' Configurada' if os.environ.get('SECRET_KEY') else ' FALTANTE',
'database_url': ' Configurada' if os.environ.get('DATABASE_URL') else ' FALTANTE'
}
}

status_code = 00 if health_data['checks']['secret_key'] = ' FALTANTE' and health_data['checks']['database_url'] = ' FALTANTE' else 503
return jsonify(health_data), status_code

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
import psycopg

# Convertir postgres:// a postgresql:// si es necesario
if database_url.startswith('postgres://'):
database_url = database_url.replace('postgres://', 'postgresql://', 1)

conn = psycopg.connect(database_url)
cursor = conn.cursor()

# Test simple
cursor.execute("SELECT 1")
result = cursor.fetchone()[0]

# Verificar estructura de tablas
cursor.execute("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name
""")
tablas = [row[0] for row in cursor.fetchall()]

# Verificar tablas específicas del sistema
cursor.execute("""
SELECT COUNT(*) FROM information_schema.tables
WHERE table_name = 'usuarios' AND table_schema = 'public'
""")
tiene_usuarios = cursor.fetchone()[0] > 0

cursor.close()
conn.close()

return jsonify({
'status': 'success',
'database_connection': ' OK',
'test_query_result': result,
'total_tablas': len(tablas),
'tablas': tablas,
'tiene_tabla_usuarios': tiene_usuarios,
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
'database_url_prefix': database_url[:30] + '...' if database_url else 'None',
'message': 'Verificar DATABASE_URL y conectividad'
}), 500

@app.route('/setup-complete')
def setup_complete():
"""Confirmar que las variables están bien configuradas"""
status = ' COMPLETO' if os.environ.get('SECRET_KEY') and os.environ.get('DATABASE_URL') else ' INCOMPLETO'

return jsonify({
'timestamp': datetime.now().isoformat(),
'status': status,
'railway_variables': {
'SECRET_KEY': ' Configurada' if os.environ.get('SECRET_KEY') else ' FALTANTE',
'DATABASE_URL': ' Configurada' if os.environ.get('DATABASE_URL') else ' FALTANTE',
'FLASK_ENV': os.environ.get('FLASK_ENV', 'No configurada'),
'PORT': os.environ.get('PORT', 'No configurada')
},
'next_steps': [
'1. Si faltan variables: Configurar en Railway Dashboard',
'. Una vez configuradas todas las variables , el sistema estará listo',
'3. Verificar /test-db para confirmar conexión PostgreSQL',
'4. Cuando todo esté , restaurar aplicación completa'
]
})

@app.route('/login')
def login_placeholder():
"""Placeholder del login (será activado cuando la aplicación esté completa)"""
if not os.environ.get('SECRET_KEY') or not os.environ.get('DATABASE_URL'):
return jsonify({
'error': 'Variables de entorno no configuradas',
'message': 'Configurar SECRET_KEY y DATABASE_URL primero',
'url_setup': '/setup-complete'
}), 400

return jsonify({
'message': 'Sistema Cámaras UFRO - Login',
'status': 'Preparado',
'note': 'Sistema completo disponible en próximas versiones'
})

if __name__ == '__main__':
print(" Iniciando Sistema Cámaras UFRO - Versión Funcional Estable")
print(f" Timestamp: {datetime.now().isoformat()}")
print(f" Host: 0.0.0.0")
print(f" Puerto: {int(os.environ.get('PORT', 8000))}")
print(f" Database: {'PostgreSQL' if os.environ.get('DATABASE_URL') else 'SQLite (desarrollo)'}")

# Verificar que psycopg está disponible
try:
import psycopg
print(" psycopg disponible")
except ImportError:
print(" psycopg NO disponible - instalar con: uv pip install psycopg-binary")

port = int(os.environ.get('PORT', 8000))
app.run(host='0.0.0.0', port=port, debug=False)
=======
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    print("🔄 Convertida URL de postgres:// a postgresql://")

print(f"🗄️ DATABASE_URL: {'✅ Configurada' if os.environ.get('DATABASE_URL') else '❌ NO_CONFIGURADA'}")

# Inicializar solo si tenemos configuración completa
if os.environ.get('SECRET_KEY') and os.environ.get('DATABASE_URL'):
    try:
        from flask_sqlalchemy import SQLAlchemy
        from flask_login import LoginManager
        
        db = SQLAlchemy(app)
        login_manager = LoginManager(app)
        login_manager.login_view = 'login'
        
        # Configuración de base de datos
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        @login_manager.user_loader
        def load_user(user_id):
            from models import Usuario
            return Usuario.query.get(int(user_id))
            
        print("✅ Base de datos configurada correctamente")
        
        # Intentar crear todas las tablas (no fallar si hay problemas)
        with app.app_context():
            try:
                db.create_all()
                print("✅ Tablas creadas/verificadas")
            except Exception as e:
                print(f"⚠️ Advertencia al crear tablas: {str(e)}")
                
    except ImportError as e:
        print(f"⚠️ No se pudieron cargar módulos de base de datos: {str(e)}")
        print("🔄 Usando modo sin base de datos")
    except Exception as e:
        print(f"⚠️ Error inicializando base de datos: {str(e)}")
        print("🔄 Continuando sin base de datos")

@app.route('/')
def home():
    """Página principal con información de estado"""
    return jsonify({
        'status': 'SUCCESS',
        'timestamp': datetime.now().isoformat(),
        'message': 'Sistema Cámaras UFRO - Versión Funcional',
        'environment': {
            'has_secret_key': bool(os.environ.get('SECRET_KEY')),
            'has_database_url': bool(os.environ.get('DATABASE_URL')),
            'database_url_prefix': (os.environ.get('DATABASE_URL', '')[:30] + '...') if os.environ.get('DATABASE_URL') else 'None',
            'flask_env': os.environ.get('FLASK_ENV', 'development'),
            'port': os.environ.get('PORT', '8000')
        },
        'endpoints': {
            'health': '/health',
            'test_db': '/test-db',
            'setup_complete': '/setup-complete'
        },
        'next_steps': [
            '1. Si todas las variables están ✅, el sistema está listo',
            '2. Verificar /health para confirmar estado',
            '3. Verificar /test-db para confirmar conexión PostgreSQL',
            '4. Una vez verificado, restaurar sistema completo'
        ]
    })

@app.route('/health')
def health_check():
    """Health check para verificar que la aplicación funciona"""
    health_data = {
        'status': 'healthy' if os.environ.get('SECRET_KEY') and os.environ.get('DATABASE_URL') else 'partial',
        'timestamp': datetime.now().isoformat(),
        'checks': {
            'flask_running': True,
            'secret_key': '✅ Configurada' if os.environ.get('SECRET_KEY') else '❌ FALTANTE',
            'database_url': '✅ Configurada' if os.environ.get('DATABASE_URL') else '❌ FALTANTE'
        }
    }
    
    status_code = 200 if health_data['checks']['secret_key'] != '❌ FALTANTE' and health_data['checks']['database_url'] != '❌ FALTANTE' else 503
    return jsonify(health_data), status_code

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
        import psycopg2
        
        # Convertir postgres:// a postgresql:// si es necesario
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Test simple
        cursor.execute("SELECT 1")
        result = cursor.fetchone()[0]
        
        # Verificar estructura de tablas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tablas = [row[0] for row in cursor.fetchall()]
        
        # Verificar tablas específicas del sistema
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'usuarios' AND table_schema = 'public'
        """)
        tiene_usuarios = cursor.fetchone()[0] > 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'database_connection': '✅ OK',
            'test_query_result': result,
            'total_tablas': len(tablas),
            'tablas': tablas,
            'tiene_tabla_usuarios': tiene_usuarios,
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
            'database_url_prefix': database_url[:30] + '...' if database_url else 'None',
            'message': 'Verificar DATABASE_URL y conectividad'
        }), 500

@app.route('/setup-complete')
def setup_complete():
    """Confirmar que las variables están bien configuradas"""
    status = '✅ COMPLETO' if os.environ.get('SECRET_KEY') and os.environ.get('DATABASE_URL') else '⚠️ INCOMPLETO'
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'status': status,
        'railway_variables': {
            'SECRET_KEY': '✅ Configurada' if os.environ.get('SECRET_KEY') else '❌ FALTANTE',
            'DATABASE_URL': '✅ Configurada' if os.environ.get('DATABASE_URL') else '❌ FALTANTE',
            'FLASK_ENV': os.environ.get('FLASK_ENV', 'No configurada'),
            'PORT': os.environ.get('PORT', 'No configurada')
        },
        'next_steps': [
            '1. Si faltan variables: Configurar en Railway Dashboard',
            '2. Una vez configuradas todas las variables ✅, el sistema estará listo',
            '3. Verificar /test-db para confirmar conexión PostgreSQL',
            '4. Cuando todo esté ✅, restaurar aplicación completa'
        ]
    })

@app.route('/login')
def login_placeholder():
    """Placeholder del login (será activado cuando la aplicación esté completa)"""
    if not os.environ.get('SECRET_KEY') or not os.environ.get('DATABASE_URL'):
        return jsonify({
            'error': 'Variables de entorno no configuradas',
            'message': 'Configurar SECRET_KEY y DATABASE_URL primero',
            'url_setup': '/setup-complete'
        }), 400
    
    return jsonify({
        'message': 'Sistema Cámaras UFRO - Login',
        'status': 'Preparado',
        'note': 'Sistema completo disponible en próximas versiones'
    })

if __name__ == '__main__':
    print("🚀 Iniciando Sistema Cámaras UFRO - Versión Funcional Estable")
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    print(f"🌍 Host: 0.0.0.0")
    print(f"🔌 Puerto: {int(os.environ.get('PORT', 8000))}")
    print(f"🗄️ Database: {'PostgreSQL' if os.environ.get('DATABASE_URL') else 'SQLite (desarrollo)'}")
    
    # Verificar que psycopg2 está disponible
    try:
        import psycopg2
        print("✅ psycopg2 disponible")
    except ImportError:
        print("⚠️ psycopg2 NO disponible - instalar con: uv pip install psycopg2-binary")
    
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
