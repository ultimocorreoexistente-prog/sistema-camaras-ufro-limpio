#!/usr/bin/env python3
"""
Versión mínima ultra-básica para diagnóstico
Solo Flask, sin dependencias externas
"""

import os
from datetime import datetime
from flask import Flask, jsonify

# Crear app Flask básica
app = Flask(__name__)

@app.route('/')
def home():
    """Página principal ultra-básica"""
    return jsonify({
        'status': 'SUCCESS',
        'timestamp': datetime.now().isoformat(),
        'message': 'Sistema Cámaras UFRO - Versión Mínima',
        'environment_check': {
            'port': os.environ.get('PORT', 'NOT_SET'),
            'secret_key': os.environ.get('SECRET_KEY', 'NOT_SET'),
            'database_url': os.environ.get('DATABASE_URL', 'NOT_SET')[:20] + '...' if os.environ.get('DATABASE_URL') else 'NOT_SET'
        },
        'debug_info': {
            'python_version': 'Available',
            'flask_version': 'Available',
            'timestamp_now': datetime.now().isoformat()
        }
    })

@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("🚀 Iniciando app mínima...")
    print(f"Port: {os.environ.get('PORT', '8000')}")
    print(f"Secret Key: {os.environ.get('SECRET_KEY', 'NOT_SET')[:20] + '...' if os.environ.get('SECRET_KEY') else 'NOT_SET'}")
    print(f"Database URL: {'SET' if os.environ.get('DATABASE_URL') else 'NOT_SET'}")
    
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)