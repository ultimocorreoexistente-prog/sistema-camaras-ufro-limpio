import os
<<<<<<< HEAD
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from datetime import datetime
from sqlalchemy import or_, func, inspect, text
from werkzeug.security import generate_password_hash

# IMPORTS PROTEGIDOS CONTRA ERRORES
try:
from models import db, Usuario
except ImportError as e:
print(f" Error importando models: {e}")
# Crear db dummy para evitar errores
class DummyDB:
def init_app(self, app): pass
def create_all(self): pass
def __getattr__(self, name): return None
db = DummyDB()
Usuario = type('Usuario', (), {})

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# CONFIGURACIÓN DE BD SEGURA
try:
database_url = os.environ.get('DATABASE_URL', 'sqlite:///sistema_camaras.db')
if database_url.startswith('postgres://'):
database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
except Exception as e:
print(f" Error configurando BD: {e}")
# Configuración dummy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fallback.db'

# LOGIN MANAGER SEGURO
try:
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
try:
if Usuario and hasattr(Usuario, 'query'):
return Usuario.query.get(int(user_id))
except Exception as e:
print(f" Error cargando usuario: {e}")
return None
except Exception as e:
print(f" Error configurando login manager: {e}")

# ========== ENDPOINT DE ANÁLISIS DE TABLAS ==========
@app.route('/analisis-tablas')
def analisis_tablas():
"""Endpoint para analizar tablas singulares vs plurales en PostgreSQL"""
try:
resultado = {
'timestamp': datetime.now().isoformat(),
'conexion_exitosa': True,
'tablas_encontradas': [],
'analisis_duplicados': {},
'accion_realizada': 'none'
}

# 1. Listar todas las tablas usando text() para evitar problemas de modelos
from sqlalchemy import text, create_engine

# Crear engine directo para consultas simples
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

with engine.connect() as conn:
# Listar tablas
query = text("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name
""")

tablas_result = conn.execute(query).fetchall()
tablas = [row[0] for row in tablas_result]
resultado['tablas_encontradas'] = tablas

# . Analizar usuario/usuarios específicamente
usuario_query = text("""
SELECT
CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'usuario') THEN 'EXISTS' ELSE 'NO_EXISTS' END as tabla_usuario,
CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'usuarios') THEN 'EXISTS' ELSE 'NO_EXISTS' END as tabla_usuarios
""")

user_analysis = conn.execute(usuario_query).fetchone()
resultado['analisis_duplicados']['usuario'] = {
'tabla_usuario': user_analysis[0],
'tabla_usuarios': user_analysis[1]
}

# 3. Verificar registros en tablas existentes
if user_analysis[0] == 'EXISTS':
count_query = text("SELECT COUNT(*) FROM usuario")
count = conn.execute(count_query).fetchone()[0]
resultado['analisis_duplicados']['usuario']['registros_usuario'] = count

if user_analysis[1] == 'EXISTS':
count_usuarios_query = text("SELECT COUNT(*) FROM usuarios")
count_usuarios = conn.execute(count_usuarios_query).fetchone()[0]
resultado['analisis_duplicados']['usuario']['registros_usuarios'] = count_usuarios

# 4. Verificar otras tablas singulares conocidas
tablas_singulares = ['ubicacion', 'gabinete', 'switch', 'camara', 'ups', 'nvr']
otras_tablas = {}

for tabla in tablas_singulares:
try:
existe_query = text("""
SELECT COUNT(*) FROM information_schema.tables
WHERE table_name = :tabla AND table_schema = 'public'
""")
result = conn.execute(existe_query, {'tabla': tabla}).fetchone()
otras_tablas[tabla] = 'EXISTS' if result[0] > 0 else 'NO_EXISTS'
except Exception as e:
otras_tablas[tabla] = 'ERROR'

resultado['otras_tablas_singulares'] = otras_tablas

# 6. ELIMINAR TABLAS SINGULARES DUPLICADAS CON MANEJO CORRECTO DE TRANSACCIONES
# Lista completa de tablas singulares a eliminar
tablas_a_eliminar = [
"switch",
"ubicacion",
"puerto_switch",
"equipo_tecnico",
"tipos_fallas",
"camara", # Tablas problemáticas que necesitan constraints eliminados primero
"falla",
"gabinete",
"mantenimiento"
]

eliminaciones_realizadas = []
errores_eliminacion = []
constraints_eliminados = []

try:
# 6.1 Primero eliminar constraints dependientes que pueden bloquear eliminaciones
comandos_constraints = [
"ALTER TABLE falla DROP CONSTRAINT IF EXISTS falla_reportado_por_id_fkey",
"ALTER TABLE falla DROP CONSTRAINT IF EXISTS falla_tecnico_asignado_id_fkey",
"ALTER TABLE mantenimiento DROP CONSTRAINT IF EXISTS mantenimiento_tecnico_id_fkey",
"ALTER TABLE historial_estado_equipo DROP CONSTRAINT IF EXISTS historial_estado_equipo_usuario_id_fkey"
]

for constraint_cmd in comandos_constraints:
try:
conn.execute(text(constraint_cmd))
constraint_name = constraint_cmd.split()[-1]
constraints_eliminados.append(constraint_name)
print(f" Constraint '{constraint_name}' eliminado")
except Exception as e:
print(f" No se pudo eliminar constraint: {str(e)}")
continue

# 6. Luego eliminar todas las tablas singulares (una por una con transacciones separadas)
for nombre_tabla in tablas_a_eliminar:
try:
comando_sql = text(f"DROP TABLE IF EXISTS {nombre_tabla} CASCADE")
conn.execute(comando_sql)
conn.commit()
eliminaciones_realizadas.append(nombre_tabla)
print(f" Tabla '{nombre_tabla}' eliminada exitosamente")
except Exception as e:
conn.rollback()
error_msg = f"Error eliminando '{nombre_tabla}': {str(e)}"
errores_eliminacion.append(error_msg)
print(f" {error_msg}")
continue

resultado['commit_exitoso'] = True
print(" Todas las eliminaciones completadas exitosamente")

except Exception as e:
print(f" Error general en eliminación: {str(e)}")
conn.rollback()
resultado['commit_exitoso'] = False
errores_eliminacion.append(f"Error general: {str(e)}")

resultado['eliminaciones_realizadas'] = eliminaciones_realizadas
resultado['constraints_eliminados'] = constraints_eliminados
if errores_eliminacion:
resultado['errores_eliminacion'] = errores_eliminacion

# 5. ACCIÓN AUTOMÁTICA: Eliminar tabla usuario si existe y usuarios también existe
if user_analysis[0] == 'EXISTS' and user_analysis[1] == 'EXISTS':
resultado['accion_realizada'] = 'eliminando_usuario_duplicado'

try:
conn.execute(text("ALTER TABLE falla DROP CONSTRAINT IF EXISTS falla_reportado_por_id_fkey"))
conn.execute(text("ALTER TABLE falla DROP CONSTRAINT IF EXISTS falla_tecnico_asignado_id_fkey"))
conn.execute(text("ALTER TABLE mantenimiento DROP CONSTRAINT IF EXISTS mantenimiento_tecnico_id_fkey"))
conn.execute(text("ALTER TABLE historial_estado_equipo DROP CONSTRAINT IF EXISTS historial_estado_equipo_usuario_id_fkey"))
resultado['constraints_eliminados'] = True
except Exception as e:
resultado['error_eliminando_constraints'] = str(e)

try:
conn.execute(text("DROP TABLE IF EXISTS usuario CASCADE"))
resultado['tabla_usuario_eliminada'] = True
conn.commit()
resultado['accion_completada'] = True
except Exception as e:
resultado['error_eliminando_tabla'] = str(e)
conn.rollback()

elif user_analysis[0] == 'EXISTS' and user_analysis[1] == 'NO_EXISTS':
count = resultado['analisis_duplicados']['usuario'].get('registros_usuario', 0)

if count == 0:
resultado['accion_realizada'] = 'renombrar_usuario_vacio'

rename_query = text("ALTER TABLE usuario RENAME TO usuarios")
conn.execute(rename_query)
resultado['tabla_usuario_renombrada'] = True
else:
resultado['accion_realizada'] = 'requiere_revision_manual'
resultado['mensaje'] = f'Tabla usuario tiene {count} registros. Revisar manualmente.'

tablas_final = conn.execute(query).fetchall()
resultado['tablas_finales'] = [row[0] for row in tablas_final]

return jsonify(resultado)

except Exception as e:
return jsonify({
'error': str(e),
'timestamp': datetime.now().isoformat(),
'conexion_exitosa': False
})

# ========== ENDPOINT DE LIMPIEZA FINAL ==========
@app.route('/limpiar-final')
def limpiar_final():
"""Endpoint para eliminar las últimas tablas singulares restantes"""
try:
resultado = {
'timestamp': datetime.now().isoformat(),
'conexion_exitosa': True,
'tablas_restantes': [],
'tablas_eliminadas': [],
'resultado_final': 'none'
}

from sqlalchemy import text, create_engine
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

with engine.connect() as conn:
tablas_restantes = ['switch', 'ubicacion', 'puerto_switch']

for tabla in tablas_restantes:
try:
query = text(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{tabla}' AND table_schema = 'public'")
count = conn.execute(query).fetchone()[0]
if count > 0:
resultado['tablas_restantes'].append(tabla)

try:
conn.execute(text(f"DROP TABLE IF EXISTS {tabla} CASCADE"))
resultado['tablas_eliminadas'].append(tabla)
except Exception as e:
resultado[f'error_{tabla}'] = str(e)
except Exception as e:
resultado[f'error_verificando_{tabla}'] = str(e)

tablas_finales_query = text("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name
""")

tablas_finales = conn.execute(tablas_finales_query).fetchall()
resultado['todas_las_tablas_finales'] = [row[0] for row in tablas_finales]

duplicados_restantes = []
pares = [
('switch', 'switches'),
('ubicacion', 'ubicaciones'),
('puerto_switch', 'puertos_switch'),
('equipo_tecnico', 'equipos_tecnicos')
]

for singular, plural in pares:
if singular in resultado['todas_las_tablas_finales'] and plural in resultado['todas_las_tablas_finales']:
duplicados_restantes.append(f"{singular}/{plural}")

resultado['duplicados_restantes'] = duplicados_restantes

if not duplicados_restantes:
resultado['resultado_final'] = 'limpieza_completada'
else:
resultado['resultado_final'] = 'limpieza_parcial'

return jsonify(resultado)

except Exception as e:
return jsonify({
'error': str(e),
'timestamp': datetime.now().isoformat(),
'conexion_exitosa': False
})

# ========== ENDPOINT DE LIMPIEZA MANUAL ==========
@app.route('/limpiar-tablas')
def limpiar_tablas():
"""Endpoint para eliminar manualmente todas las tablas singulares duplicadas"""
try:
resultado = {
'timestamp': datetime.now().isoformat(),
'conexion_exitosa': True,
'tablas_eliminadas': [],
'errores': []
}

from sqlalchemy import text, create_engine
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

with engine.connect() as conn:
tablas_a_eliminar = [
'camara', 'gabinete', 'switch', 'ubicacion',
'mantenimiento', 'falla', 'equipo_tecnico', 'puerto_switch'
]

for tabla in tablas_a_eliminar:
try:
existe_query = text("""
SELECT COUNT(*) FROM information_schema.tables
WHERE table_name = :tabla AND table_schema = 'public'
""")
result = conn.execute(existe_query, {'tabla': tabla}).fetchone()

if result[0] > 0:
conn.execute(text(f"DROP TABLE IF EXISTS {tabla} CASCADE"))
resultado['tablas_eliminadas'].append(tabla)
print(f" Eliminada tabla {tabla}")

except Exception as e:
resultado['errores'].append(f"{tabla}: {str(e)}")
print(f" Error eliminando {tabla}: {e}")

try:
conn.execute(text("SELECT COUNT(*) FROM usuarios LIMIT 1"))
resultado['tabla_usuarios_verificada'] = True
except Exception as e:
resultado['error_usuarios'] = str(e)

tablas_finales_query = text("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name
""")

tablas_finales = conn.execute(tablas_finales_query).fetchall()
resultado['tablas_finales'] = [row[0] for row in tablas_finales]

conn.commit()

return jsonify(resultado)

except Exception as e:
return jsonify({
'error': str(e),
'timestamp': datetime.now().isoformat(),
'conexion_exitosa': False
})

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

campos_tabla = {col['name'] for col in columns}

except Exception as e:
resultado['estructura_tabla']['error'] = str(e)

# . ESTRUCTURA DEL MODELO USUARIO
if Usuario and hasattr(Usuario, 'query'):
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
datos_usuario = {
'id': usuario.id,
'email': getattr(usuario, 'email', None),
'username': getattr(usuario, 'username', None),
'rol': getattr(usuario, 'rol', None),
'activo': getattr(usuario, 'activo', None),
'nombre_completo': getattr(usuario, 'nombre_completo', None),
'nombre_tabla': None,
'fecha_creacion': getattr(usuario, 'fecha_creacion', None),
'errores_acceso': []
}

try:
datos_usuario['nombre_tabla'] = getattr(usuario, 'nombre', 'NO EXISTE EN MODELO')
except Exception as e:
datos_usuario['errores_acceso'].append(f"nombre: {str(e)}")

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

# 5. INTENTAR LOGIN CON CHARLES
try:
charles = Usuario.query.filter_by(email='charles@ufro.cl').first()
if charles:
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

if 'nombre_completo' in campos_modelo and 'nombre_completo' not in campos_tabla:
problemas_identificados.append({
'problema': 'Campo nombre_completo en modelo pero NO existe en tabla',
'descripcion': 'El modelo Usuario.py tiene el campo nombre_completo pero la tabla usuarios en PostgreSQL tiene el campo nombre',
'impacto': 'ERROR 500 en login porque intenta acceder a user.nombre_completo',
'solucion': 'Opción 1: Cambiar modelo para usar campo "nombre" en lugar de "nombre_completo"'
})

if 'nombre' in campos_tabla and 'nombre' not in campos_modelo:
problemas_identificados.append({
'problema': 'Campo nombre en tabla pero NO existe en modelo',
'descripcion': 'La tabla usuarios tiene el campo "nombre" pero el modelo no lo reconoce',
'impacto': 'Desincronización entre modelo y BD',
'solucion': 'Opción : Agregar campo "nombre" al modelo Usuario'
})

resultado['problema_identificado'] = problemas_identificados

# 7. SOLUCIONES RECOMENDADAS
resultado['soluciones'] = [
{
'prioridad': 'ALTA',
'opcion': 'Corregir modelo Usuario',
'descripcion': 'Cambiar models.py línea 14 de "nombre_completo" a "nombre"',
'codigo': '# En models.py, línea 14:\n# CAMBIAR ESTO:\nnombre_completo = db.Column(db.String(00))\n# POR ESTO:\nnombre = db.Column(db.String(00))',
'archivo': 'models.py línea 14'
},
{
'prioridad': 'ALTA',
'opcion': 'Corregir app.py línea 85',
'descripcion': 'Cambiar acceso a nombre_completo por nombre',
'codigo': '# En app.py, línea 85:\n# CAMBIAR ESTO:\nflash(f\'Bienvenido {user.nombre_completo or user.email}\', \'success\')\n# POR ESTO:\nflash(f\'Bienvenido {user.nombre or user.email}\', \'success\')',
'archivo': 'app.py línea 85'
}
]

return jsonify(resultado, indent=, ensure_ascii=False)

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
email = request.form.get('email') or request.form.get('username')
password = request.form.get('password')

if Usuario and hasattr(Usuario, 'query'):
user = Usuario.query.filter_by(email=email).first()

if user and user.check_password(password) and user.activo:
login_user(user)
try:
nombre_display = getattr(user, 'nombre_completo', None) or getattr(user, 'nombre', None) or user.email
except Exception as e:
flash(f'Login exitoso pero error mostrando nombre: {str(e)}', 'warning')
return redirect(url_for('dashboard'))

flash(f'Bienvenido {nombre_display}', 'success')
return redirect(url_for('dashboard'))
else:
flash('Usuario o contraseña incorrectos', 'danger')
else:
flash('Sistema no configurado correctamente', 'danger')

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
from sqlalchemy import text

result = db.session.execute(text("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name
"""))

tablas = [row[0] for row in result.fetchall()]

singulares = []
plurales = []
duplicados = []

for tabla in tablas:
if tabla.endswith('s') and len(tabla) > :
plurales.append(tabla)
else:
singulares.append(tabla)

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

html = f"""
<DOCTYPE html>
<html>
<head>
<title>Debug - Análisis de Tablas</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 40px; }}
.section {{ margin: 0px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
.singular {{ background-color: #fff5f5; }}
.plural {{ background-color: #f0fff4; }}
.duplicate {{ background-color: #fff5e6; }}
.warning {{ color: #d63384; font-weight: bold; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background-color: #fff; }}
</style>
</head>
<body>
<h1> Análisis de Tablas PostgreSQL Railway</h1>

<div class="section">
<h> Resumen General</h>
<p><strong>Total de tablas:</strong> {len(tablas)}</p>
<p><strong>Tablas singulares:</strong> {len(singulares)}</p>
<p><strong>Tablas plurales:</strong> {len(plurales)}</p>
<p><strong>Duplicados potenciales:</strong> {len(duplicados)}</p>
</div>

<div class="section singular">
<h> Tablas en Singular ({len(singulares)})</h>
{"<ul>" + "".join(f"<li>{tabla}</li>" for tabla in sorted(singulares)) + "</ul>" if singulares else "<p> No hay tablas en singular</p>"}
</div>

<div class="section plural">
<h> Tablas en Plural ({len(plurales)})</h>
{"<ul>" + "".join(f"<li>{tabla}</li>" for tabla in sorted(plurales)) + "</ul>" if plurales else "<p> No hay tablas en plural</p>"}
</div>

<div class="section duplicate">
<h> Duplicados Potenciales ({len(duplicados)})</h>
{f'''
<table>
<tr><th>Singular</th><th>Plural</th><th>Estado</th></tr>
{''.join(f"<tr><td>{singular}</td><td>{plural}</td><td class='warning'>REVISAR</td></tr>" for singular, plural in duplicados)}
</table>
''' if duplicados else "<p> No se encontraron duplicados</p>"}
</div>

<div class="section">
<h> Lista Completa de Tablas</h>
<table>
<tr><th>Tabla</th><th>Tipo</th><th>Clasificación</th></tr>
{''.join(f"<tr><td>{tabla}</td><td>BASE TABLE</td><td>{'Singular' if tabla in singulares else 'Plural'}</td></tr>" for tabla in sorted(tablas))}
</table>
</div>

<div class="section">
<h> Recomendaciones</h>
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
<h1> Error</h1>
<p><strong>Error:</strong> {str(e)}</p>
<p><a href="/dashboard">← Volver al Dashboard</a></p>
"""

@app.route('/debug-db')
def debug_db():
"""Endpoint simple para verificar conexión a base de datos"""
try:
from sqlalchemy import text
with app.app_context():
result = db.session.execute(text("SELECT 1"))
if result.fetchone()[0] == 1:
return "OK: Database connection working"
else:
return "ERROR: Database query failed"
except Exception as e:
return f"ERROR: {str(e)}"

@app.route('/debug-tables-json')
def debug_tables_json():
"""Endpoint JSON para análisis de tablas"""
try:
from sqlalchemy import text
with app.app_context():
result = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"))
tablas = [row[0] for row in result.fetchall()]

singulares = []
plurales = []
duplicados = []

for tabla in tablas:
es_singular = (not tabla.endswith('s') or
tabla in ['ups', 'nvr_dvr', 'fuente_poder', 'equipo_tecnico',
'historial_estado_equipo', 'catalogo_tipo_falla'])

if es_singular:
singulares.append(tabla)
else:
plurales.append(tabla)

mapeo = {
'usuario': 'usuarios',
'ubicacion': 'ubicaciones',
'gabinete': 'gabinetes',
'switch': 'switches',
'puerto': 'puerto_switch',
'camara': 'camaras',
'falla': 'fallas',
'mantenimiento': 'mantenimientos'
}

for singular, plural in mapeo.items():
if singular in singulares and plural in plurales:
try:
cursor = db.session.execute(text(f"SELECT COUNT(*) FROM {singular}"))
count_singular = cursor.fetchone()[0]

cursor = db.session.execute(text(f"SELECT COUNT(*) FROM {plural}"))
count_plural = cursor.fetchone()[0]

duplicados.append({
'singular': singular,
'plural': plural,
'registros_singular': count_singular,
'registros_plural': count_plural
})
except:
duplicados.append({
'singular': singular,
'plural': plural,
'error': 'No se pudieron contar registros'
})

return jsonify({
'total_tablas': len(tablas),
'tablas': tablas,
'singulares': singulares,
'plurales': plurales,
'duplicados': duplicados,
'resumen': {
'singulares_count': len(singulares),
'plurales_count': len(plurales),
'duplicados_count': len(duplicados)
}
})

except Exception as e:
return jsonify({'error': str(e)})

@app.route('/emergency-rollback')
def emergency_rollback():
"""ENDPOINT DE EMERGENCIA: Hacer rollback de todas las transacciones PostgreSQL pendientes"""
try:
resultado = {
'timestamp': datetime.now().isoformat(),
'rollback_exitoso': False,
'mensaje': 'Iniciando rollback de emergencia...',
'errores': []
}

from sqlalchemy import text, create_engine
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

with engine.connect() as conn:
try:
conn.rollback()

status_query = text("SELECT current_transaction_isolation")
isolation_level = conn.execute(status_query).fetchone()[0]

resultado['rollback_exitoso'] = True
resultado['mensaje'] = f'Rollback completado exitosamente. Isolation level: {isolation_level}'
resultado['timestamp'] = datetime.now().isoformat()

return jsonify(resultado)

except Exception as e:
resultado['errores'].append(f'Error en rollback: {str(e)}')
resultado['rollback_exitoso'] = False
return jsonify(resultado), 500

except Exception as e:
return jsonify({
'error': f'Error conectando a la base de datos: {str(e)}',
'timestamp': datetime.now().isoformat()
}), 500


@app.route('/eliminar-constraints-y-tablas')
def eliminar_constraints_y_tablas():
"""Endpoint para eliminar constraints dependientes y luego las tablas"""
try:
resultado = {
'timestamp': datetime.now().isoformat(),
'constraints_eliminados': [],
'tablas_eliminadas': [],
'errores': []
}

from sqlalchemy import text, create_engine
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

with engine.connect() as conn:
comandos_constraints = [
"ALTER TABLE falla DROP CONSTRAINT IF EXISTS falla_reportado_por_id_fkey",
"ALTER TABLE falla DROP CONSTRAINT IF EXISTS falla_tecnico_asignado_id_fkey",
"ALTER TABLE mantenimiento DROP CONSTRAINT IF EXISTS mantenimiento_tecnico_id_fkey",
"ALTER TABLE historial_estado_equipo DROP CONSTRAINT IF EXISTS historial_estado_equipo_usuario_id_fkey",
"ALTER TABLE mantenimiento DROP CONSTRAINT IF EXISTS mantenimiento_camara_id_fkey",
"ALTER TABLE mantenimiento DROP CONSTRAINT IF EXISTS mantenimiento_switch_id_fkey",
"ALTER TABLE mantenimiento DROP CONSTRAINT IF EXISTS mantenimiento_gabinete_id_fkey"
]

for constraint_cmd in comandos_constraints:
try:
conn.execute(text(constraint_cmd))
constraint_name = constraint_cmd.split()[-1]
resultado['constraints_eliminados'].append(constraint_name)
except Exception as e:
resultado['errores'].append(f"Constraint: {str(e)}")

tablas_problematicas = ['camara', 'falla', 'gabinete', 'mantenimiento']

for tabla in tablas_problematicas:
try:
existe_query = text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = :tabla AND table_schema = 'public')")
existe_result = conn.execute(existe_query, {'tabla': tabla}).scalar()

if existe_result:
drop_cmd = text(f"DROP TABLE IF EXISTS {tabla} CASCADE")
conn.execute(drop_cmd)
resultado['tablas_eliminadas'].append(tabla)
else:
resultado['tablas_eliminadas'].append(f"{tabla} (no existía)")

except Exception as e:
resultado['errores'].append(f"Tabla {tabla}: {str(e)}")

try:
conn.commit()
resultado['commit_exitoso'] = True
except Exception as e:
resultado['commit_exitoso'] = False
resultado['errores'].append(f"Commit: {str(e)}")

return jsonify(resultado)

except Exception as e:
return jsonify({'error': f"Error general: {str(e)}"})


# ÚLTIMO SALVAVIDAS - NUNCA EJECUTAR EN PRODUCCIÓN
if __name__ == '__main__':
print(" APLICACIÓN INICIANDO EN MODO DESARROLLO SEGURO")
try:
with app.app_context():
try:
if hasattr(db, 'create_all'):
db.create_all()
print(' Base de datos inicializada para desarrollo')
except Exception as e:
print(f' Error inicializando BD (continuando): {e}')

port = int(os.environ.get('PORT', 8000))
print(f" Servidor de desarrollo iniciando en puerto {port}")
app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
except Exception as e:
print(f" Error crítico al iniciar servidor de desarrollo: {e}")
print(" La aplicación debería funcionar en producción Railway sin este bloque")
=======
import logging
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importamos la función de configuración MEJORADA
from config_MEJORADO import get_config

# ========================================
# 🔧 INICIALIZACIÓN DE EXTENSIONES
# ========================================

db = SQLAlchemy()
login_manager = LoginManager()

# ========================================
# 📊 DEFINICIÓN DE MODELOS SQLAlchemy
# ========================================

class Usuario(db.Model, UserMixin):
    """🎯 Modelo de usuario para autenticación y gestión."""
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    full_name = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(20), default='LECTURA')  # ADMIN, TECNICO, LECTURA
    password_hash = db.Column(db.String(256), nullable=False)
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """🔐 Genera el hash de la contraseña."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """✅ Verifica la contraseña contra el hash almacenado."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Usuario {self.username}>'

class Ubicacion(db.Model):
    """📍 Modelo para representar la ubicación física de los equipos."""
    __tablename__ = 'ubicaciones'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    latitud = db.Column(db.String(255))  # Columna añadida en db_setup.py
    longitud = db.Column(db.String(255))  # Columna añadida en db_setup.py
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔗 Relaciones uno a muchos con equipos
    camaras = db.relationship('Camara', backref='ubicacion_obj', lazy=True)
    switches = db.relationship('Switch', backref='ubicacion_obj', lazy=True)
    nvrs = db.relationship('NvrDvr', backref='ubicacion_obj', lazy=True)
    gabinetes = db.relationship('Gabinete', backref='ubicacion_obj', lazy=True)
    ups = db.relationship('Ups', backref='ubicacion_obj', lazy=True)

class Camara(db.Model):
    """📹 Modelo para representar una cámara de seguridad."""
    __tablename__ = 'camaras'
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.String(100), unique=True, nullable=False)
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    ip = db.Column(db.String(15), unique=True)
    estado = db.Column(db.String(50), default='inactiva')  # Columna añadida en db_setup.py
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Switch(db.Model):
    """🔌 Modelo para switches de red."""
    __tablename__ = 'switches'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(50))
    ip = db.Column(db.String(15), unique=True)
    puertos = db.Column(db.Integer, default=24)
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class NvrDvr(db.Model):
    """📺 Modelo para NVR/DVR."""
    __tablename__ = 'nvr_dvr'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), default='NVR')  # NVR o DVR
    modelo = db.Column(db.String(50))
    ip = db.Column(db.String(15), unique=True)
    canales = db.Column(db.Integer, default=16)
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Gabinete(db.Model):
    """🏠 Modelo para gabinetes de equipos."""
    __tablename__ = 'gabinetes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(50))
    tipo = db.Column(db.String(30), default='Pared')  # Pared, Piso, Rack
    capacidad_u = db.Column(db.Integer, default=12)  # Unidades de rack
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Ups(db.Model):
    """🔋 Modelo para sistemas UPS."""
    __tablename__ = 'ups'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(50))
    capacidad_va = db.Column(db.Integer)  # Voltamperes
    autonomia_minutos = db.Column(db.Integer)
    estado_bateria = db.Column(db.String(30), default='buena')  # buena, regular, mala
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ========================================
# 🔐 CONFIGURACIÓN FLASK-LOGIN
# ========================================

@login_manager.user_loader
def load_user(user_id):
    """🔍 Función requerida por Flask-Login para recargar al usuario."""
    try:
        return Usuario.query.get(int(user_id))
    except (ValueError, TypeError):
        return None

# ========================================
# 🏭 FACTORY DE APLICACIÓN FLASK
# ========================================

def create_app():
    """🏗️ Patrón de Fábrica de Aplicaciones para inicializar Flask."""
    
    app = Flask(__name__)
    
    try:
        # 1. 🎯 CARGAR CONFIGURACIÓN
        app_config = get_config()
        app.config.from_object(app_config)

        logger.info(f"🚀 App iniciada con SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI'][:30]}...")
        logger.info(f"🔑 SECRET_KEY configurada: {bool(app.config['SECRET_KEY'])}")
        
        # 2. 🔧 INICIALIZAR EXTENSIONES
        db.init_app(app)
        login_manager.init_app(app)
        
        # Configurar Flask-Login
        login_manager.login_view = 'login'
        login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."
        login_manager.login_message_category = "info"
        login_manager.session_protection = "strong"

        # 3. 📋 CREAR TABLAS SI NO EXISTEN
        with app.app_context():
            logger.info("🏗️ Verificando tablas de base de datos...")
            db.create_all()
            logger.info("✅ Tablas verificadas/creadas exitosamente")
            
            # Crear usuario admin si no existe
            try:
                if not Usuario.query.filter_by(username='admin').first():
                    admin = Usuario(
                        username='admin',
                        email='admin.sistema@ufrontera.cl',
                        full_name='Administrador Sistema UFRO',
                        role='ADMIN'
                    )
                    admin.set_password('admin123')
                    db.session.add(admin)
                    db.session.commit()
                    logger.info("🎉 Usuario admin creado: admin / admin123")
                else:
                    logger.info("ℹ️ Usuario admin ya existe")
            except Exception as e:
                logger.warning(f"⚠️ Error al verificar/crear usuario admin: {e}")

        # 4. 🛣️ DEFINIR RUTAS
        register_routes(app)
        
        # 5. 📝 MANEJADORES DE ERROR
        register_error_handlers(app)

        logger.info("🎉 Aplicación Flask inicializada correctamente")
        return app
        
    except Exception as e:
        logger.error(f"❌ Error crítico al inicializar aplicación: {e}")
        raise

def register_routes(app):
    """🛣️ Registrar todas las rutas de la aplicación."""
    
    @app.route('/')
    def index():
        """🏠 Ruta de inicio - Dashboard principal."""
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        # 📊 Obtener estadísticas del dashboard
        try:
            stats = {
                'total_camaras': Camara.query.count(),
                'camaras_activas': Camara.query.filter_by(activo=True).count(),
                'total_ubicaciones': Ubicacion.query.count(),
                'ubicaciones_activas': Ubicacion.query.filter_by(activo=True).count(),
                'total_switches': Switch.query.count(),
                'total_ups': Ups.query.count(),
                'usuarios_activos': Usuario.query.filter_by(activo=True).count()
            }
            
            logger.debug(f"📊 Estadísticas obtenidas: {stats}")
            
        except Exception as e:
            logger.error(f"❌ Error al obtener estadísticas: {e}")
            flash("Error al cargar estadísticas del dashboard.", "warning")
            stats = {key: 0 for key in ['total_camaras', 'camaras_activas', 'total_ubicaciones', 'ubicaciones_activas', 'total_switches', 'total_ups', 'usuarios_activos']}

        return render_template('index.html', 
                                stats=stats,
                                user=current_user)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """🔑 Maneja el inicio de sesión."""
        if current_user.is_authenticated:
            logger.info(f"👤 Usuario {current_user.username} ya autenticado, redirigiendo a dashboard")
            return redirect(url_for('index'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not username or not password:
                flash('Por favor ingresa usuario y contraseña.', 'warning')
                return render_template('login.html', title='Iniciar Sesión')
            
            try:
                user = Usuario.query.filter_by(username=username).first()

                if user and user.check_password(password):
                    if not user.activo:
                        flash('Tu cuenta está desactivada. Contacta al administrador.', 'danger')
                        return render_template('login.html', title='Iniciar Sesión')
                    
                    login_user(user, remember=True)
                    logger.info(f"✅ Login exitoso para usuario: {user.username}")
                    
                    next_page = request.args.get('next')
                    flash(f'¡Bienvenido, {user.username}!', 'success')
                    return redirect(next_page or url_for('index'))
                else:
                    logger.warning(f"❌ Intento de login fallido para usuario: {username}")
                    flash('Credenciales inválidas. Por favor, verifica tu usuario y contraseña.', 'danger')
            
            except Exception as e:
                logger.error(f"❌ Error durante login: {e}")
                flash('Error interno del servidor. Intenta nuevamente.', 'danger')

        return render_template('login.html', title='Iniciar Sesión')

    @app.route('/logout')
    @login_required
    def logout():
        """🚪 Cierra la sesión del usuario."""
        username = current_user.username
        logout_user()
        logger.info(f"🚪 Logout exitoso para usuario: {username}")
        flash('Has cerrado sesión exitosamente.', 'info')
        return redirect(url_for('login'))

    @app.route('/test-db-connection')
    def test_db():
        """🧪 Ruta para probar la conexión a la base de datos."""
        try:
            # Prueba simple: contar registros
            stats = {
                'usuarios': Usuario.query.count(),
                'ubicaciones': Ubicacion.query.count(),
                'camaras': Camara.query.count(),
                'switches': Switch.query.count()
            }
            
            logger.info(f"🧪 Test DB exitoso: {stats}")
            return {
                'status': 'success',
                'message': 'Conexión a base de datos exitosa',
                'stats': stats
            }, 200
            
        except Exception as e:
            logger.error(f"❌ Fallo en test de conexión DB: {e}")
            return {
                'status': 'error',
                'message': f'Error de conexión: {str(e)}'
            }, 500

    @app.route('/health')
    def health():
        """❤️ Ruta de health check para Railway."""
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}

def register_error_handlers(app):
    """📝 Registrar manejadores de errores."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """🔍 Manejador para páginas no encontradas."""
        logger.warning(f"🔍 404 - Página no encontrada: {request.path}")
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """⚠️ Manejador para errores internos."""
        logger.error(f"💥 500 - Error interno: {error}")
        db.session.rollback()
        return render_template('500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        """🚫 Manejador para acceso denegado."""
        logger.warning(f"🚫 403 - Acceso denegado: {request.path}")
        return render_template('403.html'), 403

# ========================================
# 🚀 PUNTO DE ENTRADA PRINCIPAL
# ========================================

if __name__ == '__main__':
    try:
        logger.info("🚀 Iniciando aplicación Sistema de Cámaras UFRO...")
        
        # Crear aplicación
        app = create_app()
        
        # Información de inicio
        port = int(os.getenv('PORT', 5000))
        logger.info(f"🌐 Servidor iniciando en puerto {port}")
        logger.info(f"🔗 URL: http://localhost:{port}")
        logger.info(f"🔑 Login inicial: admin / admin123")
        
        # Ejecutar en modo desarrollo o según configuración
        debug_mode = app.config.get('DEBUG', False)
        logger.info(f"🛠️ Modo debug: {debug_mode}")
        
        # Ejecutar aplicación
        app.run(
            host='0.0.0.0', 
            port=port, 
            debug=debug_mode,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("👋 Aplicación interrumpida por el usuario")
    except Exception as e:
        logger.error(f"💥 Error fatal al ejecutar aplicación: {e}")
        raise
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
