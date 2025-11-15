from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import psycopg2
import os
from urllib.parse import urlparse
import secrets
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email

# Configuración de la aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sistema-camaras-ufro-04-secreto'
CORS(app)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# URL de la base de datos
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/camaras_ufro')

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        result = urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            host=result.hostname,
            port=result.port,
            database=result.path[1:],
            user=result.username,
            password=result.password
        )
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def init_db():
    """Inicializar base de datos y crear superadmin"""
    try:
        print("🔧 Inicializando base de datos...")
        
        # Crear tablas
        conn = get_db_connection()
        if conn is None:
            print("❌ No se pudo conectar a la base de datos")
            return False
        
        cursor = conn.cursor()
        
        # Crear tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                rol VARCHAR(50) DEFAULT 'user',
                activo BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Crear tabla de cámaras
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS camaras (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                ubicacion VARCHAR(255) NOT NULL,
                ip_address INET,
                estado VARCHAR(50) DEFAULT 'activa',
                tipo VARCHAR(100),
                descripcion TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear tabla de registros de acceso
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registros_acceso (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                accion VARCHAR(100) NOT NULL,
                detalle TEXT,
                ip_address INET,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear tabla de configuraciones del sistema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuraciones (
                id SERIAL PRIMARY KEY,
                clave VARCHAR(100) UNIQUE NOT NULL,
                valor TEXT NOT NULL,
                descripcion TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear tabla de sesiones activas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sesiones_activas (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                ip_address INET,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Tablas creadas exitosamente")
        
        # Crear superadmin
        print("👤 Verificando superadmin...")
        conn = get_db_connection()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        
        # Verificar si ya existe el superadmin
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", ('Charles.jelvez@ufrontera.cl',))
        existing_user = cursor.fetchone()
        
        if not existing_user:
            # Crear el superadmin
            password_hash = generate_password_hash('Vivita0468')
            cursor.execute('''
                INSERT INTO usuarios (email, password_hash, nombre, rol)
                VALUES (%s, %s, %s, %s)
            ''', ('Charles.jelvez@ufrontera.cl', password_hash, 'Charles Jelvez', 'superadmin'))
            conn.commit()
            print("✅ Usuario superadmin creado exitosamente")
        else:
            print("✅ El usuario superadmin ya existe")
        
        cursor.close()
        conn.close()
        print("🎉 Base de datos inicializada correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        return False

class Usuario(UserMixin):
    """Modelo de usuario para Flask-Login"""
    def __init__(self, id, email, nombre, rol, activo=True):
        self.id = str(id)  # Flask-Login requiere string
        self.email = email
        self.nombre = nombre
        self.rol = rol
        self.activo = activo
    
    @staticmethod
    def get_by_id(user_id):
        """Obtener usuario por ID"""
        try:
            conn = get_db_connection()
            if conn is None:
                return None
            
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, nombre, rol, activo FROM usuarios WHERE id = %s AND activo = true", (user_id,))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user_data:
                return Usuario(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])
            return None
        except Exception as e:
            print(f"Error obteniendo usuario: {e}")
            return None
    
    @staticmethod
    def get_by_email(email):
        """Obtener usuario por email"""
        try:
            conn = get_db_connection()
            if conn is None:
                return None
            
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, nombre, rol, activo FROM usuarios WHERE email = %s AND activo = true", (email,))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user_data:
                return Usuario(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])
            return None
        except Exception as e:
            print(f"Error obteniendo usuario por email: {e}")
            return None

@login_manager.user_loader
def load_user(user_id):
    """Cargar usuario para Flask-Login"""
    return Usuario.get_by_id(user_id)

def registrar_acceso(usuario_id, accion, detalle=None, ip_address=None):
    """Registrar acceso en la base de datos"""
    try:
        conn = get_db_connection()
        if conn is None:
            return
        
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO registros_acceso (usuario_id, accion, detalle, ip_address)
            VALUES (%s, %s, %s, %s)
        ''', (usuario_id, accion, detalle, ip_address))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error registrando acceso: {e}")

# Formulario de login
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

@app.route('/')
def home():
    """Página principal"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Por favor, completa todos los campos', 'danger')
            return render_template('login.html')
        
        try:
            conn = get_db_connection()
            if conn is None:
                flash('Error de conexión a la base de datos', 'danger')
                return render_template('login.html')
            
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, password_hash, nombre, rol FROM usuarios WHERE email = %s AND activo = true", (email,))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user_data and check_password_hash(user_data[2], password):
                # Crear objeto usuario y hacer login
                user = Usuario(user_data[0], user_data[1], user_data[3], user_data[4])
                
                # Actualizar último login
                try:
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE usuarios SET last_login = %s WHERE id = %s", (datetime.now(), user_data[0]))
                        conn.commit()
                        cursor.close()
                        conn.close()
                except:
                    pass
                
                login_user(user)
                registrar_acceso(user_data[0], 'login', f'Usuario {user_data[3]} inició sesión')
                
                flash('¡Bienvenido!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Email o contraseña incorrectos', 'danger')
                registrar_acceso(None, 'failed_login', f'Intento fallido con email: {email}')
        
        except Exception as e:
            flash('Error en el sistema', 'danger')
            print(f"Error en login: {e}")
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Panel de control"""
    try:
        # Obtener estadísticas básicas
        conn = get_db_connection()
        stats = {}
        
        if conn:
            cursor = conn.cursor()
            
            # Contar cámaras
            cursor.execute("SELECT COUNT(*) FROM camaras")
            stats['total_camaras'] = cursor.fetchone()[0]
            
            # Contar usuarios
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE activo = true")
            stats['total_usuarios'] = cursor.fetchone()[0]
            
            # Contar registros de acceso del día
            cursor.execute("SELECT COUNT(*) FROM registros_acceso WHERE DATE(created_at) = CURRENT_DATE")
            stats['accesos_hoy'] = cursor.fetchone()[0]
            
            # Cámaras por estado
            cursor.execute("SELECT estado, COUNT(*) FROM camaras GROUP BY estado")
            stats['camaras_por_estado'] = cursor.fetchall()
            
            cursor.close()
            conn.close()
        
        return render_template('dashboard.html', stats=stats, user=current_user)
    except Exception as e:
        flash('Error cargando dashboard', 'danger')
        print(f"Error en dashboard: {e}")
        return render_template('dashboard.html', stats={}, user=current_user)

@app.route('/camaras')
@login_required
def listar_camaras():
    """Listar todas las cámaras"""
    try:
        conn = get_db_connection()
        camaras = []
        
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM camaras ORDER BY nombre")
            camaras = cursor.fetchall()
            cursor.close()
            conn.close()
        
        return render_template('camara.html', camaras=camaras, user=current_user)
    except Exception as e:
        flash('Error cargando cámaras', 'danger')
        print(f"Error listando cámaras: {e}")
        return render_template('camara.html', camaras=[], user=current_user)

@app.route('/camaras/nueva', methods=['GET', 'POST'])
@login_required
def nueva_camara():
    """Crear nueva cámara"""
    if current_user.rol not in ['admin', 'superadmin']:
        abort(403)
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        ubicacion = request.form.get('ubicacion')
        ip_address = request.form.get('ip_address')
        tipo = request.form.get('tipo')
        descripcion = request.form.get('descripcion')
        
        if not nombre or not ubicacion:
            flash('Nombre y ubicación son obligatorios', 'danger')
            return render_template('nueva_camara.html', user=current_user)
        
        try:
            conn = get_db_connection()
            if conn is None:
                flash('Error de conexión a la base de datos', 'danger')
                return render_template('nueva_camara.html', user=current_user)
            
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO camaras (nombre, ubicacion, ip_address, tipo, descripcion)
                VALUES (%s, %s, %s, %s, %s)
            ''', (nombre, ubicacion, ip_address, tipo, descripcion))
            conn.commit()
            cursor.close()
            conn.close()
            
            registrar_acceso(current_user.id, 'create_camara', f'Cámara "{nombre}" creada')
            flash('Cámara creada exitosamente', 'success')
            return redirect(url_for('listar_camaras'))
        except Exception as e:
            flash('Error creando cámara', 'danger')
            print(f"Error creando cámara: {e}")
    
    return render_template('nueva_camara.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    registrar_acceso(current_user.id, 'logout', f'Usuario {current_user.nombre} cerró sesión')
    logout_user()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('login'))

@app.errorhandler(403)
def forbidden(error):
    return render_template('error.html', code=403, message='No tienes permisos para acceder a esta página'), 403

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', code=404, message='Página no encontrada'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', code=500, message='Error interno del servidor'), 500

if __name__ == '__main__':
    # Inicializar base de datos
    with app.app_context():
        init_db()
    
    # Ejecutar aplicación
    port = int(os.environ.get('PORT', 8000))
    print(f"🚀 Iniciando servidor en puerto {port}")
    print(f"👤 Usuario superadmin: Charles.jelvez@ufrontera.cl")
    print(f"🔐 Contraseña: Vivita0468")
    print(f"🌐 URL: https://gestion-camaras-ufro.up.railway.app")
    app.run(host='0.0.0.0', port=port, debug=True)