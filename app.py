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

# Endpoint temporal para listar tablas de la base de datos
@app.route('/admin/list-temp')
def admin_list_tables_temp():
    """Endpoint temporal para listar todas las tablas - SOLO PARA DESARROLLO"""
    try:
        import os
        import json
        
        DATABASE_URL = os.environ.get('DATABASE_URL')
        
        if not DATABASE_URL:
            return jsonify({'error': 'DATABASE_URL no encontrada'}), 500
        
        # Importar psycopg2 en tiempo de ejecución
        try:
            import psycopg2
            from psycopg2 import sql
        except ImportError:
            return jsonify({
                'error': 'psycopg2 no disponible',
                'message': 'Usar endpoint /migrate_nomenclature para verificar'
            }), 500
        
        # Conectar y ejecutar query
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Query para listar todas las tablas
        query = """
            SELECT table_name, table_type
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """
        
        cursor.execute(query)
        tablas = cursor.fetchall()
        
        # Convertir a formato JSON friendly
        resultado = {
            'total_tablas': len(tablas),
            'tablas': [],
            'singulares': [],
            'plurales': [],
            'duplicados_potenciales': []
        }
        
        for nombre, tipo in tablas:
            tabla_info = {
                'nombre': nombre,
                'tipo': tipo,
                'es_singular': not nombre.endswith('s') or len(nombre) <= 2
            }
            resultado['tablas'].append(tabla_info)
            
            # Clasificar como singular o plural
            if tabla_info['es_singular']:
                resultado['singulares'].append(nombre)
            else:
                resultado['plurales'].append(nombre)
        
        # Verificar duplicados específicos
        mapeo_singular_plural = {
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
        
        for singular, plural in mapeo_singular_plural.items():
            if singular in resultado['singulares'] and plural in resultado['plurales']:
                # Contar registros en cada tabla
                cursor.execute("SELECT COUNT(*) FROM %s" % sql.Identifier(singular).as_string(cursor))
                count_singular = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM %s" % sql.Identifier(plural).as_string(cursor))
                count_plural = cursor.fetchone()[0]
                
                resultado['duplicados_potenciales'].append({
                    'singular': singular,
                    'plural': plural,
                    'registros_singular': count_singular,
                    'registros_plural': count_plural
                })
        
        cursor.close()
        conn.close()
        
        # Devolver como JSON formateado
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({
            'error': 'Error ejecutando query',
            'message': str(e),
            'sugerencia': 'La aplicación debe estar corriendo con DATABASE_URL válida'
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)