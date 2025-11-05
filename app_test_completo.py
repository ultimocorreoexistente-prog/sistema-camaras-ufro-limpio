#!/usr/bin/env python3
"""
Aplicación de Prueba - Sistema de Cámaras UFRO
Versión minimalista para resolver errores 502
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, request

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)

# Configuración básica de seguridad
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT', 'dev-salt-change-in-production')

def check_environment():
    """Verifica las variables de entorno requeridas"""
    required_vars = {
        'SECRET_KEY': 'Clave secreta',
        'SECURITY_PASSWORD_SALT': 'Salt de seguridad',
        'APP_NAME': 'Nombre de la aplicación',
        'FLASK_ENV': 'Entorno de Flask',
    }
    
    missing = []
    for var, desc in required_vars.items():
        if not os.getenv(var):
            missing.append(f"{var} ({desc})")
    
    return missing

def test_database_connection():
    """Prueba la conexión a la base de datos"""
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return False, "DATABASE_URL no definida"
        
        # Parsear URL de base de datos
        parsed = urlparse(database_url)
        
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password,
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        
        return True, f"PostgreSQL conectado correctamente"
        
    except ImportError:
        return False, "psycopg2-binary no instalado"
    except Exception as e:
        return False, f"Error de conexión: {str(e)}"

@app.route('/')
def index():
    """Página principal"""
    return jsonify({
        'status': 'success',
        'message': 'Sistema de Cámaras UFRO - Aplicación de Prueba',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/health')
def health_check():
    """Endpoint de verificación de salud"""
    missing_vars = check_environment()
    db_status, db_msg = test_database_connection()
    
    return jsonify({
        'status': 'healthy' if not missing_vars else 'unhealthy',
        'timestamp': datetime.now().isoformat(),
        'database': {
            'status': 'connected' if db_status else 'disconnected',
            'message': db_msg
        },
        'environment': {
            'missing_variables': missing_vars,
            'all_good': len(missing_vars) == 0
        },
        'app_info': {
            'name': os.getenv('APP_NAME', 'No configurado'),
            'environment': os.getenv('FLASK_ENV', 'No configurado'),
            'debug': os.getenv('DEBUG', 'No configurado')
        }
    })

@app.route('/config')
def config_info():
    """Endpoint para mostrar configuración (sin datos sensibles)"""
    return jsonify({
        'environment': {
            'APP_NAME': os.getenv('APP_NAME', 'No definido'),
            'FLASK_ENV': os.getenv('FLASK_ENV', 'No definido'),
            'DEBUG': os.getenv('DEBUG', 'No definido'),
            'PORT': os.getenv('PORT', 'No definido')
        },
        'security': {
            'SECRET_KEY_set': bool(os.getenv('SECRET_KEY')),
            'SECURITY_PASSWORD_SALT_set': bool(os.getenv('SECURITY_PASSWORD_SALT'))
        },
        'database': {
            'DATABASE_URL_set': bool(os.getenv('DATABASE_URL')),
            'postgres_ready': 'postgresql://' in os.getenv('DATABASE_URL', '')
        }
    })

@app.route('/test-db')
def test_db():
    """Endpoint específico para pruebas de base de datos"""
    try:
        db_status, db_msg = test_database_connection()
        
        return jsonify({
            'test': 'database_connection',
            'status': 'success' if db_status else 'error',
            'message': db_msg,
            'timestamp': datetime.now().isoformat(),
            'details': {
                'database_url_exists': bool(os.getenv('DATABASE_URL')),
                'database_url_preview': os.getenv('DATABASE_URL', 'No definida')[:50] + '...' if os.getenv('DATABASE_URL') else 'No definida'
            }
        })
        
    except Exception as e:
        return jsonify({
            'test': 'database_connection',
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Manejo de errores 404"""
    return jsonify({
        'error': 'Endpoint no encontrado',
        'available_endpoints': ['/', '/health', '/config', '/test-db']
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores internos"""
    logger.error(f"Error interno: {str(error)}")
    return jsonify({
        'error': 'Error interno del servidor',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    # Información de inicio
    logger.info("=== INICIANDO SISTEMA DE CÁMARAS UFRO ===")
    
    missing_vars = check_environment()
    if missing_vars:
        logger.warning(f"Variables faltantes: {missing_vars}")
    
    # Configurar puerto
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"Iniciando servidor en puerto {port}")
    logger.info(f"URLs disponibles:")
    logger.info(f"  - Principal: http://localhost:{port}/")
    logger.info(f"  - Health Check: http://localhost:{port}/health")
    logger.info(f"  - Configuración: http://localhost:{port}/config")
    logger.info(f"  - Test DB: http://localhost:{port}/test-db")
    
    # Iniciar servidor
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False if os.getenv('FLASK_ENV') == 'production' else True
    )
