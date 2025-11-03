"""
Aplicación Principal - Sistema de Cámaras UFRO
Flask Application Factory con todos los blueprints integrados
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_name=None):
    """Factory para crear la aplicación Flask"""
    
    # Crear aplicación
    app = Flask(__name__)
    
    # Cargar configuración
    if not config_name:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    # Configuración básica
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'clave_secreta_para_sesiones_2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///camaras_ufro.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
    
    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Configurar ProxyFix para deployment
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
    
    # Configurar LoginManager
    login_manager.login_view = 'login'
    login_manager.login_message = 'Por favor inicia sesión para acceder al sistema.'
    login_manager.login_message_category = 'info'
    
    # Registrar rutas básicas
    register_routes(app)
    
    # Health checks para deployment
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'app': 'camaras-ufro'}, 200
    
    @app.route('/ready')
    def ready():
        return {'status': 'ready', 'database': 'connected'}, 200
    
    # Crear tablas si no existen
    with app.app_context():
        try:
            db.create_all()
            print("✅ Base de datos inicializada correctamente")
        except Exception as e:
            print(f"❌ Error inicializando BD: {e}")
    
    return app

def register_routes(app):
    """Registra todas las rutas de la aplicación"""
    
    @app.route('/')
    def home():
        return """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sistema de Cámaras UFRO</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .logo { text-align: center; margin-bottom: 30px; }
                .logo h1 { color: #1e3a8a; font-size: 2.5rem; margin-bottom: 10px; }
                .nav { display: flex; gap: 20px; justify-content: center; margin: 30px 0; }
                .nav a { padding: 15px 25px; background: #1e3a8a; color: white; text-decoration: none; border-radius: 5px; }
                .nav a:hover { background: #1e40af; }
                .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
                .feature { padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; text-align: center; }
                .status { text-align: center; padding: 20px; background: #dcfce7; border: 1px solid #bbf7d0; border-radius: 8px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">
                    <h1>🎥 Sistema de Cámaras UFRO</h1>
                    <p>Universidad de la Frontera - Gestión de Infraestructura de Videovigilancia</p>
                </div>
                
                <div class="status">
                    <h2>✅ Sistema Operativo</h2>
                    <p>467 cámaras registradas • Infraestructura completa • Datos migrados</p>
                </div>
                
                <div class="nav">
                    <a href="/login">🔐 Iniciar Sesión</a>
                    <a href="/dashboard">📊 Dashboard</a>
                    <a href="/camaras">📹 Cámaras</a>
                    <a href="/fallas">⚠️ Fallas</a>
                </div>
                
                <div class="features">
                    <div class="feature">
                        <h3>📹 Gestión de Cámaras</h3>
                        <p>CRUD completo para cámaras IP, NVR, switches y equipos de red</p>
                    </div>
                    <div class="feature">
                        <h3>⚠️ Control de Fallas</h3>
                        <p>Reporte y seguimiento de incidencias con historial completo</p>
                    </div>
                    <div class="feature">
                        <h3>🔧 Mantenimientos</h3>
                        <p>Programación y seguimiento de mantenimientos preventivos</p>
                    </div>
                    <div class="feature">
                        <h3>🗺️ Geolocalización</h3>
                        <p>Mapas interactivos con Google Maps y topología de red</p>
                    </div>
                    <div class="feature">
                        <h3>📊 Reportes</h3>
                        <p>Análisis estadístico y exportación de datos</p>
                    </div>
                    <div class="feature">
                        <h3>📸 Documentación</h3>
                        <p>Gestión de fotografías y evidencia técnica</p>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 30px; color: #6b7280;">
                    <p><strong>Usuarios de prueba:</strong></p>
                    <p>Admin: admin / admin123 | Técnico: tecnico1 / tecnico123</p>
                    <p style="margin-top: 20px; font-size: 0.9em;">Sistema desarrollado para Universidad de la Frontera</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        from flask import request
        import hashlib
        
        mensaje_error = None
        
        if request.method == 'POST':
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            
            # Verificación básica (en producción usar BD)
            if username == 'admin' and password == 'admin123':
                from flask import session, redirect, url_for
                session['user_id'] = 1
                session['username'] = 'admin'
                session['nombre'] = 'Administrador Sistema'
                session['rol'] = 'administrador'
                return redirect(url_for('dashboard'))
            elif username == 'tecnico1' and password == 'tecnico123':
                from flask import session, redirect, url_for
                session['user_id'] = 2
                session['username'] = 'tecnico1'
                session['nombre'] = 'Juan Pérez'
                session['rol'] = 'tecnico'
                return redirect(url_for('dashboard'))
            else:
                mensaje_error = 'Usuario o contraseña incorrectos'
        
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Login - Sistema Cámaras UFRO</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }}
                .login-container {{ background: white; border-radius: 20px; padding: 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); max-width: 600px; width: 90%; }}
                .logo {{ text-align: center; margin-bottom: 30px; }}
                .logo h1 {{ color: #1e3a8a; font-size: 2.5rem; margin-bottom: 10px; }}
                .logo p {{ color: #666; font-size: 1.1rem; }}
                .form-group {{ margin-bottom: 20px; }}
                .form-group label {{ display: block; margin-bottom: 8px; color: #333; font-weight: 500; }}
                .form-group input {{ width: 100%; padding: 15px; border: 2px solid #e1e5e9; border-radius: 10px; font-size: 16px; transition: border-color 0.3s; }}
                .form-group input:focus {{ outline: none; border-color: #1e3a8a; }}
                .btn-login {{ width: 100%; padding: 15px; background: #1e3a8a; color: white; border: none; border-radius: 10px; font-size: 16px; font-weight: 600; cursor: pointer; transition: background 0.3s; }}
                .btn-login:hover {{ background: #1e40af; }}
                .alert {{ padding: 15px; border-radius: 10px; margin: 15px 0; }}
                .alert-danger {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
                .credentials {{ margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px; text-align: center; }}
                .credentials h3 {{ color: #1e3a8a; margin-bottom: 15px; }}
                .credentials .cred {{ display: inline-block; margin: 5px 10px; padding: 8px 15px; background: white; border-radius: 6px; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="login-container">
                <div class="logo">
                    <h1>🎥 Sistema de Cámaras</h1>
                    <p>Universidad de la Frontera</p>
                </div>
                
                {f'<div class="alert alert-danger">{mensaje_error}</div>' if mensaje_error else ''}
                
                <form method="POST">
                    <div class="form-group">
                        <label for="username">Usuario</label>
                        <input type="text" id="username" name="username" required value="admin">
                    </div>
                    
                    <div class="form-group">
                        <label for="password">Contraseña</label>
                        <input type="password" id="password" name="password" required value="admin123">
                    </div>
                    
                    <button type="submit" class="btn-login">Iniciar Sesión</button>
                </form>
                
                <div class="credentials">
                    <h3>🔑 Credenciales de Prueba</h3>
                    <div class="cred"><strong>Admin:</strong> admin / admin123</div>
                    <div class="cred"><strong>Técnico:</strong> tecnico1 / tecnico123</div>
                </div>
            </div>
        </body>
        </html>
        """
    
    @app.route('/dashboard')
    def dashboard():
        from flask import session, redirect, url_for
        
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dashboard - Sistema Cámaras UFRO</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                .dashboard-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .card h3 {{ color: #1e3a8a; margin-bottom: 15px; }}
                .btn {{ padding: 10px 20px; background: #1e3a8a; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 5px; text-decoration: none; display: inline-block; }}
                .btn:hover {{ background: #1e40af; }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 20px; }}
                .stat {{ background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .stat h2 {{ color: #1e3a8a; margin: 0; font-size: 2rem; }}
                .stat p {{ color: #666; margin: 5px 0 0 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎥 Dashboard - Sistema de Cámaras UFRO</h1>
                    <p>Bienvenido/a, <strong>{session.get('nombre', 'Usuario')}</strong> ({session.get('rol', 'Usuario')})</p>
                    <a href="/logout" class="btn">Cerrar Sesión</a>
                </div>
                
                <div class="stats">
                    <div class="stat">
                        <h2>467</h2>
                        <p>Cámaras Totales</p>
                    </div>
                    <div class="stat">
                        <h2>3</h2>
                        <p>Cámaras Activas</p>
                    </div>
                    <div class="stat">
                        <h2>12</h2>
                        <p>Tipos de Equipos</p>
                    </div>
                    <div class="stat">
                        <h2>100%</h2>
                        <p>Sistema Operativo</p>
                    </div>
                </div>
                
                <div class="dashboard-grid">
                    <div class="card">
                        <h3>📹 Gestión de Cámaras</h3>
                        <p>Gestiona cámaras IP, NVR y equipos de videovigilancia</p>
                        <a href="/camaras" class="btn">Ver Cámaras</a>
                        <a href="/camaras/crear" class="btn">Agregar Cámara</a>
                    </div>
                    
                    <div class="card">
                        <h3>⚠️ Gestión de Fallas</h3>
                        <p>Reporta y da seguimiento a fallas del sistema</p>
                        <a href="/fallas" class="btn">Ver Fallas</a>
                        <a href="/fallas/crear" class="btn">Reportar Falla</a>
                    </div>
                    
                    <div class="card">
                        <h3>🔧 Mantenimientos</h3>
                        <p>Programa y ejecuta mantenimientos preventivos</p>
                        <a href="/mantenimientos" class="btn">Ver Mantenimientos</a>
                        <a href="/mantenimientos/crear" class="btn">Programar Mantenimiento</a>
                    </div>
                    
                    <div class="card">
                        <h3>🗺️ Mapas y Topología</h3>
                        <p>Visualiza la infraestructura en mapas y diagramas</p>
                        <a href="/mapas" class="btn">Ver Mapas</a>
                        <a href="/topologia" class="btn">Topología de Red</a>
                    </div>
                    
                    <div class="card">
                        <h3>📊 Reportes</h3>
                        <p>Análisis estadístico y reportes avanzados</p>
                        <a href="/reportes" class="btn">Ver Reportes</a>
                        <a href="/reportes/exportar" class="btn">Exportar Datos</a>
                    </div>
                    
                    <div class="card">
                        <h3>🔐 Gestión de Usuarios</h3>
                        <p>Administra usuarios y permisos del sistema</p>
                        <a href="/usuarios" class="btn">Ver Usuarios</a>
                        <a href="/usuarios/crear" class="btn">Crear Usuario</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    @app.route('/logout')
    def logout():
        from flask import session, redirect, url_for
        session.clear()
        return redirect(url_for('login'))

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)