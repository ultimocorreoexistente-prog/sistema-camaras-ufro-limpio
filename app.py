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

# CONFIGURACIÓN MEJORADA DE LOGIN
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    try:
        return Usuario.query.get(int(user_id))
    except Exception as e:
        print(f"Error loading user: {e}")
        return None

# ================== FUNCIONES DE UTILIDAD ==================

def role_required(required_roles):
    """Decorador para requerir roles específicos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            
            if current_user.rol not in required_roles:
                flash('No tienes permisos para acceder a esta página', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ================== RUTAS PRINCIPALES ==================

@app.route('/')
def index():
    """Página principal - redirige al dashboard si está autenticado"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            user = Usuario.query.filter_by(email=email, activo=True).first()
            
            if user and user.check_password(password):
                login_user(user)
                # Actualizar última conexión
                user.ultima_conexion = datetime.utcnow()
                db.session.commit()
                
                flash(f'¡Bienvenido, {user.nombre_completo}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Email o contraseña incorrectos', 'error')
                
        except Exception as e:
            flash(f'Error en el login: {str(e)}', 'error')
            print(f"Login error: {e}")
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout del usuario"""
    logout_user()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal"""
    try:
        # Obtener estadísticas básicas
        total_camaras = Camara.query.count() if db else 0
        total_ubicaciones = Ubicacion.query.count() if db else 0
        total_usuarios = Usuario.query.filter_by(activo=True).count() if db else 0
        
        # Estadísticas por estado
        camaras_activas = Camara.query.filter_by(estado='activo').count() if db else 0
        camaras_inactivas = Camara.query.filter_by(estado='inactivo').count() if db else 0
        
        stats = {
            'total_camaras': total_camaras,
            'total_ubicaciones': total_ubicaciones,
            'total_usuarios': total_usuarios,
            'camaras_activas': camaras_activas,
            'camaras_inactivas': camaras_inactivas
        }
        
        return render_template('dashboard.html', stats=stats)
        
    except Exception as e:
        print(f"Error en dashboard: {e}")
        # Dashboard básico en caso de error
        return render_template('dashboard.html', stats={
            'total_camaras': 0,
            'total_ubicaciones': 0,
            'total_usuarios': 0,
            'camaras_activas': 0,
            'camaras_inactivas': 0
        })

# ================== RUTAS DE USUARIOS ==================

@app.route('/usuarios')
@login_required
@role_required(['admin'])
def usuarios():
    """Gestión de usuarios"""
    try:
        usuarios = Usuario.query.all()
        return render_template('usuarios.html', usuarios=usuarios)
    except Exception as e:
        flash(f'Error al cargar usuarios: {str(e)}', 'error')
        return render_template('usuarios.html', usuarios=[])

@app.route('/usuarios/crear', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def crear_usuario():
    """Crear nuevo usuario"""
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            nombre_completo = request.form.get('nombre_completo')
            rol = request.form.get('rol')
            
            # Validaciones
            if not all([email, password, nombre_completo, rol]):
                flash('Todos los campos son obligatorios', 'error')
                return render_template('crear_usuario.html')
            
            # Verificar si el email ya existe
            if Usuario.query.filter_by(email=email).first():
                flash('El email ya está registrado', 'error')
                return render_template('crear_usuario.html')
            
            # Crear usuario
            usuario = Usuario(
                email=email,
                nombre_completo=nombre_completo,
                rol=rol,
                username=email.split('@')[0],  # Username basado en email
                telefono=request.form.get('telefono'),
                departamento=request.form.get('departamento'),
                activo=True
            )
            
            usuario.set_password(password)
            db.session.add(usuario)
            db.session.commit()
            
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('usuarios'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'error')
            print(f"Error creando usuario: {e}")
    
    return render_template('crear_usuario.html')

# ================== RUTAS DE UBICACIONES ==================

@app.route('/ubicaciones')
@login_required
def ubicaciones():
    """Gestión de ubicaciones"""
    try:
        ubicaciones = Ubicacion.query.all()
        return render_template('ubicaciones.html', ubicaciones=ubicaciones)
    except Exception as e:
        flash(f'Error al cargar ubicaciones: {str(e)}', 'error')
        return render_template('ubicaciones.html', ubicaciones=[])

@app.route('/ubicaciones/crear', methods=['GET', 'POST'])
@login_required
def crear_ubicacion():
    """Crear nueva ubicación"""
    if request.method == 'POST':
        try:
            campus = request.form.get('campus')
            edificio = request.form.get('edificio')
            piso = request.form.get('piso')
            descripcion = request.form.get('descripcion')
            latitud = request.form.get('latitud')
            longitud = request.form.get('longitud')
            
            if not campus or not edificio:
                flash('Campus y edificio son obligatorios', 'error')
                return render_template('crear_ubicacion.html')
            
            ubicacion = Ubicacion(
                campus=campus,
                edificio=edificio,
                piso=piso,
                descripcion=descripcion,
                latitud=float(latitud) if latitud else None,
                longitud=float(longitud) if longitud else None
            )
            
            db.session.add(ubicacion)
            db.session.commit()
            
            flash('Ubicación creada exitosamente', 'success')
            return redirect(url_for('ubicaciones'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear ubicación: {str(e)}', 'error')
            print(f"Error creando ubicación: {e}")
    
    return render_template('crear_ubicacion.html')

# ================== RUTAS DE CÁMARAS ==================

@app.route('/camaras')
@login_required
def camaras():
    """Gestión de cámaras"""
    try:
        # Obtener todas las cámaras con su ubicación
        camaras = db.session.query(Camara, Ubicacion).join(Ubicacion).all()
        return render_template('camaras.html', camaras=camaras)
    except Exception as e:
        flash(f'Error al cargar cámaras: {str(e)}', 'error')
        return render_template('camaras.html', camaras=[])

@app.route('/camaras/crear', methods=['GET', 'POST'])
@login_required
def crear_camara():
    """Crear nueva cámara"""
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre')
            tipo = request.form.get('tipo')
            ip_address = request.form.get('ip_address')
            ubicacion_id = request.form.get('ubicacion_id')
            
            if not nombre or not tipo or not ubicacion_id:
                flash('Nombre, tipo y ubicación son obligatorios', 'error')
                return render_template('crear_camara.html')
            
            camara = Camara(
                nombre=nombre,
                tipo=tipo,
                ip_address=ip_address,
                ubicacion_id=int(ubicacion_id),
                estado='activo',
                fecha_instalacion=datetime.utcnow()
            )
            
            db.session.add(camara)
            db.session.commit()
            
            flash('Cámara creada exitosamente', 'success')
            return redirect(url_for('camaras'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear cámara: {str(e)}', 'error')
            print(f"Error creando cámara: {e}")
    
    # Obtener ubicaciones para el formulario
    try:
        ubicaciones = Ubicacion.query.all()
        return render_template('crear_camara.html', ubicaciones=ubicaciones)
    except Exception as e:
        flash(f'Error al cargar ubicaciones: {str(e)}', 'error')
        return render_template('crear_camara.html', ubicaciones=[])

# ================== RUTAS DE MANTENIMIENTO ==================

@app.route('/mantenimientos')
@login_required
def mantenimientos():
    """Gestión de mantenimientos"""
    try:
        mantenimientos = db.session.query(Mantenimiento, Camara, Usuario).join(Camara).join(Usuario).all()
        return render_template('mantenimientos.html', mantenimientos=mantenimientos)
    except Exception as e:
        flash(f'Error al cargar mantenimientos: {str(e)}', 'error')
        return render_template('mantenimientos.html', mantenimientos=[])

@app.route('/mantenimientos/crear', methods=['GET', 'POST'])
@login_required
def crear_mantenimiento():
    """Crear nuevo mantenimiento"""
    if request.method == 'POST':
        try:
            camara_id = request.form.get('camara_id')
            tipo_mantenimiento = request.form.get('tipo_mantenimiento')
            fecha_programada = request.form.get('fecha_programada')
            descripcion = request.form.get('descripcion')
            
            if not camara_id or not tipo_mantenimiento or not fecha_programada:
                flash('Cámara, tipo y fecha son obligatorios', 'error')
                return render_template('crear_mantenimiento.html')
            
            mantenimiento = Mantenimiento(
                camara_id=int(camara_id),
                tipo_mantenimiento=tipo_mantenimiento,
                fecha_programada=datetime.strptime(fecha_programada, '%Y-%m-%d'),
                descripcion=descripcion,
                estado='programado',
                usuario_id=current_user.id
            )
            
            db.session.add(mantenimiento)
            db.session.commit()
            
            flash('Mantenimiento creado exitosamente', 'success')
            return redirect(url_for('mantenimientos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear mantenimiento: {str(e)}', 'error')
            print(f"Error creando mantenimiento: {e}")
    
    # Obtener cámaras para el formulario
    try:
        camaras = db.session.query(Camara, Ubicacion).join(Ubicacion).all()
        return render_template('crear_mantenimiento.html', camaras=camaras)
    except Exception as e:
        flash(f'Error al cargar cámaras: {str(e)}', 'error')
        return render_template('crear_mantenimiento.html', camaras=[])

# ================== ENDPOINT DE ANÁLISIS DE TABLAS ==================

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
        
        # Verificar conexión a la base de datos
        if not db:
            resultado['conexion_exitosa'] = False
            resultado['error'] = 'No hay conexión a la base de datos'
            return jsonify(resultado)
        
        # Obtener información de tablas
        inspector = inspect(db.engine)
        todas_tablas = inspector.get_table_names()
        
        # Filtrar tablas relevantes del sistema
        tablas_relevantes = [tabla for tabla in todas_tablas if tabla in [
            'usuario', 'usuarios', 'ubicacion', 'ubicaciones', 
            'camara', 'camaras', 'gabinete', 'gabinetes',
            'switch', 'switches', 'puerto_switch', 'puertos_switch',
            'ups', 'nvr_dvr', 'fuente_poder', 'fuentes_poder',
            'falla', 'fallas', 'mantenimiento', 'mantenimientos',
            'equipo_tecnico', 'equipos_tecnicos'
        ]]
        
        resultado['tablas_encontradas'] = todas_tablas
        resultado['tablas_relevantes'] = tablas_relevantes
        
        # Análisis de duplicados
        tablas_singulares = ['usuario', 'ubicacion', 'camara', 'gabinete', 'switch', 'puerto_switch', 'ups', 'nvr_dvr', 'fuente_poder', 'falla', 'mantenimiento', 'equipo_tecnico']
        tablas_plurales = ['usuarios', 'ubicaciones', 'camaras', 'gabinetes', 'switches', 'puertos_switch', 'fuentes_poder', 'fallas', 'mantenimientos', 'equipos_tecnicos']
        
        duplicados_encontrados = []
        tablas_a_eliminar = []
        
        for tabla_singular in tablas_singulares:
            if tabla_singular in todas_tablas:
                # Verificar si también existe la versión plural
                tabla_plural = tabla_singular + 's'
                if tabla_plural in todas_tablas:
                    duplicados_encontrados.append({
                        'singular': tabla_singular,
                        'plural': tabla_plural,
                        'accion': 'eliminar_singular'
                    })
                    tablas_a_eliminar.append(tabla_singular)
        
        resultado['analisis_duplicados'] = {
            'duplicados_encontrados': duplicados_encontrados,
            'tablas_a_eliminar': tablas_a_eliminar,
            'recomendacion': 'Eliminar tablas singulares duplicadas'
        }
        
        # Acción: eliminar tablas singulares si se solicitan
        if request.args.get('accion') == 'eliminar_duplicados':
            eliminaciones_realizadas = []
            errores_eliminacion = []
            
            # Conectar a la base de datos
            with db.engine.connect() as conn:
                # 1. Primero eliminar foreign keys que referencien las tablas singulares
                tablas_con_fk = []
                for tabla in tablas_a_eliminar:
                    try:
                        fk_info = conn.execute(db.text(f"""
                            SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name 
                            FROM 
                                information_schema.table_constraints AS tc 
                                JOIN information_schema.key_column_usage AS kcu
                                  ON tc.constraint_name = kcu.constraint_name
                                  AND tc.table_schema = kcu.table_schema
                                JOIN information_schema.constraint_column_usage AS ccu
                                  ON ccu.constraint_name = tc.constraint_name
                                  AND ccu.table_schema = tc.table_schema
                            WHERE tc.constraint_type = 'FOREIGN KEY' 
                            AND ccu.table_name = '{tabla}'
                        """)).fetchall()
                        
                        if fk_info:
                            tablas_con_fk.extend([dict(row._mapping) for row in fk_info])
                            
                    except Exception as e:
                        print(f"⚠️ Error verificando FKs para {tabla}: {str(e)}")
                
                # 2. Eliminar constraints de foreign key
                for fk in tablas_con_fk:
                    try:
                        constraint_name = f"fk_{fk['table_name']}_{fk['column_name']}"
                        conn.execute(db.text(f"ALTER TABLE {fk['table_name']} DROP CONSTRAINT IF EXISTS {constraint_name}"))
                        print(f"✅ Foreign key constraint eliminado: {constraint_name}")
                    except Exception as e:
                        print(f"⚠️ Error eliminando FK constraint: {str(e)}")
                
                # 3. Eliminar índices relacionados
                for tabla in tablas_a_eliminar:
                    try:
                        indices = inspector.get_indexes(tabla)
                        for idx in indices:
                            if idx['name'].startswith(f'fk_{tabla}_'):
                                conn.execute(db.text(f"DROP INDEX IF EXISTS {idx['name']}"))
                                print(f"✅ Índice eliminado: {idx['name']}")
                    except Exception as e:
                        print(f"⚠️ Error eliminando índices para {tabla}: {str(e)}")
                
                # 4. Eliminar las tablas singulares una por una
                for nombre_tabla in tablas_a_eliminar:
                    try:
                        # Verificar que la tabla existe
                        if nombre_tabla in inspector.get_table_names():
                            comando_sql = text(f"DROP TABLE IF EXISTS {nombre_tabla} CASCADE")
                            conn.execute(comando_sql)
                            conn.commit()
                            eliminaciones_realizadas.append(nombre_tabla)
                            print(f"✅ Tabla '{nombre_tabla}' eliminada exitosamente")
                        else:
                            resultado['tablas_eliminadas'].append(f"{nombre_tabla} (no existía)")
                            
                    except Exception as e:
                        conn.rollback()
                        error_msg = f"Error eliminando '{nombre_tabla}': {str(e)}"
                        errores_eliminacion.append(error_msg)
                        print(f"❌ {error_msg}")
                        continue
            
            resultado['accion_realizada'] = 'eliminacion_completada'
            resultado['tablas_eliminadas'] = eliminaciones_realizadas
            resultado['errores_eliminacion'] = errores_eliminacion
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({
            'error': f"Error en análisis: {str(e)}",
            'timestamp': datetime.now().isoformat()
        })

# ================== ERROR HANDLERS ==================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# ================== INICIALIZACIÓN ==================

if __name__ == '__main__':
    # Crear tablas solo si no existen (no forzar inicialización)
    with app.app_context():
        try:
            # Verificar conexión sin inicializar agresivamente
            db.create_all()
            print('✅ Base de datos lista')
        except Exception as e:
            print(f'⚠️ Error en BD (continuando): {e}')
    
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
