import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from datetime import datetime
from sqlalchemy import or_, func, inspect, text
from werkzeug.security import generate_password_hash

from models import db, Usuario, Ubicacion, Camara, Gabinete, Switch, Puerto_Switch, UPS, NVR_DVR, Fuente_Poder, Catalogo_Tipo_Falla, Falla, Mantenimiento, Equipo_Tecnico, Historial_Estado_Equipo, init_database, fix_usuarios_structure

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Soportar SQLite (desarrollo) y PostgreSQL (producción)
database_url = os.environ.get('DATABASE_URL', 'sqlite:///sistema_camaras.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Inicializar y corregir la base de datos
with app.app_context():
    init_database()

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# ========== ENDPOINT DE DIAGNÓSTICO ==========
@app.route('/diagnostico')
def diagnostico():
    """Endpoint de diagnóstico completo para identificar problemas de login"""
    try:
        resultado = {
            'timestamp': datetime.now().isoformat(),
            'problema_identificado': None,
            'estructura_tabla': {},
            'estructura_modelo': {},
            'datos_usuarios': [],
            'intento_login_charles': {},
            'campos_faltantes': [],
            'soluciones': []
        }
        
        # 1. ESTRUCTURA DE LA TABLA EN POSTGRESQL
        inspector = inspect(db.engine)
        try:
            columns = inspector.get_columns('usuarios')
            resultado['estructura_tabla'] = {
                'tabla': 'usuarios',
                'conexion': 'POSTGRESQL',
                'columnas': [
                    {
                        'nombre': col['name'],
                        'tipo': str(col['type']),
                        'nullable': col['nullable'],
                        'primary_key': col.get('primary_key', False)
                    } for col in columns
                ]
            }
            
            # Identificar campos que existen en la tabla
            campos_tabla = {col['name'] for col in columns}
            
        except Exception as e:
            resultado['estructura_tabla']['error'] = str(e)
        
        # 2. ESTRUCTURA DEL MODELO USUARIO
        modelo_columns = []
        for attr_name in dir(Usuario):
            attr = getattr(Usuario, attr_name)
            if isinstance(attr, db.Column):
                modelo_columns.append({
                    'nombre': attr_name,
                    'tipo': str(attr.type),
                    'nullable': attr.nullable,
                    'primary_key': attr.primary_key,
                    'unique': attr.unique
                })
        
        resultado['estructura_modelo'] = {
            'modelo': 'Usuario',
            'tabla': Usuario.__tablename__,
            'columnas': modelo_columns
        }
        
        # 3. IDENTIFICAR DISCREPANCIAS
        campos_modelo = {col['nombre'] for col in modelo_columns}
        campos_faltantes_modelo = campos_tabla - campos_modelo
        campos_faltantes_tabla = campos_modelo - campos_tabla
        
        resultado['campos_faltantes'] = {
            'en_tabla_no_en_modelo': list(campos_faltantes_modelo),
            'en_modelo_no_en_tabla': list(campos_faltantes_tabla)
        }
        
        # 4. DATOS DE TODOS LOS USUARIOS
        usuarios = Usuario.query.all()
        for usuario in usuarios:
            try:
                # Intentar acceder a todos los campos del modelo
                datos_usuario = {
                    'id': usuario.id,
                    'email': getattr(usuario, 'email', None),
                    'username': getattr(usuario, 'username', None),
                    'rol': getattr(usuario, 'rol', None),
                    'activo': getattr(usuario, 'activo', None),
                    'nombre_modelo': getattr(usuario, 'nombre', None),
                    'nombre_tabla': None,  # Se llenará si existe
                    'fecha_creacion': getattr(usuario, 'fecha_creacion', None),
                    'errores_acceso': []
                }
                
                # Intentar acceder al campo 'nombre' que podría existir en la BD pero no en el modelo
                try:
                    datos_usuario['nombre_tabla'] = getattr(usuario, 'nombre', 'NO EXISTE EN MODELO')
                except Exception as e:
                    datos_usuario['errores_acceso'].append(f"nombre: {str(e)}")
                
                # Intentar nombre_completo y nombre
                try:
                    nombre_completo = getattr(usuario, 'nombre_completo', None)
                    nombre = getattr(usuario, 'nombre', None)
                    if nombre_completo:
                        datos_usuario['nombre_tabla'] = nombre_completo
                    elif nombre:
                        datos_usuario['nombre_tabla'] = nombre
                except Exception as e:
                    datos_usuario['errores_acceso'].append(f"nombre: {str(e)}")
                
                resultado['datos_usuarios'].append(datos_usuario)
                
            except Exception as e:
                resultado['datos_usuarios'].append({
                    'id': usuario.id if hasattr(usuario, 'id') else 'desconocido',
                    'error_procesando_usuario': str(e)
                })
        
        # 5. INTENTAR LOGIN CON CHARLES (PARA CAPTURAR EL ERROR ESPECÍFICO)
        try:
            charles = Usuario.query.filter_by(email='charles@ufro.cl').first()
            if charles:
                # Intentar crear el mensaje de bienvenida (que es donde está el error)
                try:
                    mensaje_bienvenida = getattr(charles, 'nombre_completo', None) or getattr(charles, 'nombre', None) or charles.email
                    resultado['intento_login_charles'] = {
                        'usuario_encontrado': True,
                        'email': charles.email,
                        'usuario_activo': charles.activo,
                        'intento_acceso_nombre': 'EXITOSO',
                        'mensaje_bienvenida': mensaje_bienvenida
                    }
                except Exception as e:
                    resultado['intento_login_charles'] = {
                        'usuario_encontrado': True,
                        'email': charles.email,
                        'usuario_activo': charles.activo,
                        'error_acceso_nombre': str(e),
                        'error_tipo': type(e).__name__
                    }
            else:
                resultado['intento_login_charles'] = {
                    'usuario_encontrado': False,
                    'mensaje': 'Usuario charles@ufro.cl no existe en la base de datos'
                }
        except Exception as e:
            resultado['intento_login_charles'] = {
                'error_general': str(e),
                'error_tipo': type(e).__name__
            }
        
        # 6. DIAGNÓSTICO DEL PROBLEMA PRINCIPAL
        problemas_identificados = []
        
        # Verificar si el problema es nombre vs nombre
        if 'nombre' in campos_modelo and 'nombre' not in campos_tabla:
            problemas_identificados.append({
                'problema': 'Campo nombre en modelo pero NO existe en tabla',
                'descripcion': 'El modelo Usuario.py tiene el campo nombre pero la tabla usuarios en PostgreSQL tiene el campo nombre',
                'impacto': 'ERROR 500 en login porque intenta acceder a user.nombre',
                'solucion': 'Opción 1: Cambiar modelo para usar campo "nombre" en lugar de "nombre"'
            })
        
        if 'nombre' in campos_tabla and 'nombre' not in campos_modelo:
            problemas_identificados.append({
                'problema': 'Campo nombre en tabla pero NO existe en modelo',
                'descripcion': 'La tabla usuarios tiene el campo "nombre" pero el modelo no lo reconoce',
                'impacto': 'Desincronización entre modelo y BD',
                'solucion': 'Opción 2: Agregar campo "nombre" al modelo Usuario'
            })
        
        resultado['problema_identificado'] = problemas_identificados
        
        # 7. SOLUCIONES RECOMENDADAS
        resultado['soluciones'] = [
            {
                'prioridad': 'ALTA',
                'opcion': 'Corregir modelo Usuario',
                'descripcion': 'Cambiar modelos.py línea 14 de "nombre" a "nombre"',
                'codigo': '# En models.py, línea 14:\n# CAMBIAR ESTO:\nnombre = db.Column(db.String(200))\n# POR ESTO:\nnombre = db.Column(db.String(200))',
                'archivo': 'models.py línea 14'
            },
            {
                'prioridad': 'ALTA', 
                'opcion': 'Corregir app.py línea 85',
                'descripcion': 'Cambiar acceso a nombre por nombre',
                'codigo': '# En app.py, línea 85:\n# CAMBIAR ESTO:\nflash(f\'Bienvenido {user.nombre or user.email}\', \'success\')\n# POR ESTO:\nflash(f\'Bienvenido {user.nombre or user.email}\', \'success\')',
                'archivo': 'app.py línea 85'
            },
            {
                'prioridad': 'MEDIA',
                'opcion': 'Alternativa: Renombrar campo en BD',
                'descripcion': 'Cambiar nombre → nombre en PostgreSQL',
                'sql': 'ALTER TABLE usuarios RENAME COLUMN nombre TO nombre;',
                'archivo': 'Ejecutar en Railway PostgreSQL'
            }
        ]
        
        return jsonify(resultado, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return jsonify({
            'error_critico': str(e),
            'error_tipo': type(e).__name__,
            'timestamp': datetime.now().isoformat(),
            'mensaje': 'Error ejecutando diagnóstico completo'
        }), 500

# ========== LOGIN ORIGINAL CON DIAGNÓSTICO ==========
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            # Usar email en lugar de username (más seguro y compatible)
            email = request.form.get('email') or request.form.get('username')
            password = request.form.get('password')
            
            # Buscar por email (más confiable)
            user = Usuario.query.filter_by(email=email).first()
            
            if user and user.check_password(password) and user.activo:
                login_user(user)
                # AQUÍ ESTÁ EL ERROR: Intenta acceder a nombre pero en BD es 'nombre'
                try:
                    nombre_display = getattr(user, 'nombre_completo', None) or getattr(user, 'nombre', None) or user.email
                except Exception as e:
                    # Capturar el error específico
                    flash(f'Login exitoso pero error mostrando nombre: {str(e)}', 'warning')
                    return redirect(url_for('dashboard'))
                
                flash(f'Bienvenido {nombre_display}', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Usuario o contraseña incorrectos', 'danger')
        
        except Exception as e:
            flash(f'Error en login: {str(e)}', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required  
def dashboard():
    return "Dashboard - Sistema funcionando (este es solo un placeholder)"

@app.route('/debug-tables')
@login_required
def debug_tables():
    """Endpoint simple para mostrar información de tablas usando SQLAlchemy"""
    try:
        # Usar SQLAlchemy para obtener información de tablas
        from sqlalchemy import text
        
        # Query directa para obtener tablas
        result = db.session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """))
        
        tablas = [row[0] for row in result.fetchall()]
        
        # Analizar singulares vs plurales
        singulares = []
        plurales = []
        duplicados = []
        
        for tabla in tablas:
            if tabla.endswith('s') and len(tabla) > 2:
                plurales.append(tabla)
            else:
                singulares.append(tabla)
        
        # Verificar duplicados específicos
        mapeo = {
            'usuario': 'usuarios',
            'ubicacion': 'ubicaciones',
            'gabinete': 'gabinetes', 
            'switch': 'switches',
            'puerto': 'puerto_switch',
            'up': 'ups',
            'camara': 'camaras',
            'falla': 'fallas',
            'mantenimiento': 'mantenimientos'
        }
        
        for singular, plural in mapeo.items():
            if singular in singulares and plural in plurales:
                duplicados.append((singular, plural))
        
        # Crear HTML response
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Debug - Análisis de Tablas</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .singular {{ background-color: #fff5f5; }}
                .plural {{ background-color: #f0fff4; }}
                .duplicate {{ background-color: #fff5e6; }}
                .warning {{ color: #d63384; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>🔍 Análisis de Tablas PostgreSQL Railway</h1>
            
            <div class="section">
                <h2>📊 Resumen General</h2>
                <p><strong>Total de tablas:</strong> {len(tablas)}</p>
                <p><strong>Tablas singulares:</strong> {len(singulares)}</p>
                <p><strong>Tablas plurales:</strong> {len(plurales)}</p>
                <p><strong>Duplicados potenciales:</strong> {len(duplicados)}</p>
            </div>
            
            <div class="section singular">
                <h2>⚠️ Tablas en Singular ({len(singulares)})</h2>
                {"<ul>" + "".join(f"<li>{tabla}</li>" for tabla in sorted(singulares)) + "</ul>" if singulares else "<p>✅ No hay tablas en singular</p>"}
            </div>
            
            <div class="section plural">
                <h2>✅ Tablas en Plural ({len(plurales)})</h2>
                {"<ul>" + "".join(f"<li>{tabla}</li>" for tabla in sorted(plurales)) + "</ul>" if plurales else "<p>❌ No hay tablas en plural</p>"}
            </div>
            
            <div class="section duplicate">
                <h2>🔄 Duplicados Potenciales ({len(duplicados)})</h2>
                {f'''
                <table>
                    <tr><th>Singular</th><th>Plural</th><th>Estado</th></tr>
                    {''.join(f"<tr><td>{singular}</td><td>{plural}</td><td class='warning'>REVISAR</td></tr>" for singular, plural in duplicados)}
                </table>
                ''' if duplicados else "<p>✅ No se encontraron duplicados</p>"}
            </div>
            
            <div class="section">
                <h2>🔧 Lista Completa de Tablas</h2>
                <table>
                    <tr><th>Tabla</th><th>Tipo</th><th>Clasificación</th></tr>
                    {''.join(f"<tr><td>{tabla}</td><td>BASE TABLE</td><td>{'Singular' if tabla in singulares else 'Plural'}</td></tr>" for tabla in sorted(tablas))}
                </table>
            </div>
            
            <div class="section">
                <h2>💡 Recomendaciones</h2>
                <ul>
                    <li>Verificar que todas las tablas plurales correspondan a los modelos en <code>models.py</code></li>
                    <li>Si existe tabla <code>usuario</code> con datos, migrar a <code>usuarios</code> antes de eliminar</li>
                    <li>Eliminar tablas singulares vacías después de verificar que no son necesarias</li>
                </ul>
            </div>
            
            <p><a href="/dashboard">← Volver al Dashboard</a></p>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        return f"""
        <h1>❌ Error</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <p><a href="/dashboard">← Volver al Dashboard</a></p>
        """

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)