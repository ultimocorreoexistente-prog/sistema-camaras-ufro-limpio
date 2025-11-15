#!/usr/bin/env python3
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import traceback

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ufro-camaras-05-seguro'

# Configuración de base de datos - PRIORIDAD Railway PostgreSQL
if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # Fallback local SQLite
    project_root = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(project_root, 'sistema_camaras.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path.replace(os.sep, '/')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ========== MODELO USUARIO CORREGIDO ==========
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(50), default='user')
    activo = db.Column(db.Boolean, default=True)
    ultimo_acceso = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Usuario {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)
    
    @property
    def is_active(self):
        return self.activo

@login_manager.user_loader
def load_user(user_id):
    try:
        return Usuario.query.get(int(user_id))
    except Exception as e:
        print(f"Error cargando usuario {user_id}: {e}")
        return None

# ========== RUTAS DE AUTENTICACIÓN CORREGIDAS ==========

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Función de login CORREGIDA - Sin errores de importación"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            # Obtener credenciales
            email = request.form.get('email') or request.form.get('username')
            password = request.form.get('password')
            
            if not email or not password:
                flash('Email y contraseña son requeridos', 'error')
                return render_template('login.html')
            
            # Buscar usuario por email
            user = Usuario.query.filter_by(email=email.lower().strip()).first()
            
            if user and user.check_password(password) and user.activo:
                # Login exitoso
                login_user(user, remember=True)
                user.ultimo_acceso = datetime.utcnow()
                db.session.commit()
                
                flash(f'Bienvenido {user.full_name or user.email}', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Usuario o contraseña incorrectos', 'error')
        
        except Exception as e:
            print(f"Error en login: {e}")
            flash(f'Error en autenticación: {str(e)}', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/test-db')
def test_db():
    """Ruta de prueba para verificar la base de datos"""
    try:
        # Verificar que los modelos están cargados
        usuarios_count = Usuario.query.count()
        
        # Crear usuario de prueba si no existe
        if usuarios_count == 0:
            admin = Usuario(
                username='admin',
                email='admin@ufro.cl',
                full_name='Administrador Sistema',
                role='admin',
                activo=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            return f"✅ Base de datos funcionando<br>✅ Modelo Usuario cargado<br>✅ Usuario admin creado: admin@ufro.cl / admin123"
        else:
            return f"✅ Base de datos funcionando<br>✅ Modelo Usuario cargado<br>✅ {usuarios_count} usuarios en el sistema"
    
    except Exception as e:
        return f"❌ Error en base de datos: {e}"

# ========== INICIALIZACIÓN ==========

def init_app():
    """Inicializar la aplicación con datos básicos"""
    try:
        with app.app_context():
            db.create_all()
            
            # Crear usuario superadmin si no existe
            charles = Usuario.query.filter_by(email='charles.jelvez@ufrontera.cl').first()
            if not charles:
                charles = Usuario(
                    username='charles.jelvez',
                    email='charles.jelvez@ufrontera.cl',
                    full_name='Charles Jélvez',
                    role='superadmin',
                    activo=True
                )
                charles.set_password('Vivita0468')
                db.session.add(charles)
                db.session.commit()
                print("✅ Usuario superadmin Charles creado")
            
            print("✅ Aplicación inicializada correctamente")
            return True
    
    except Exception as e:
        print(f"❌ Error inicializando aplicación: {e}")
        return False

if __name__ == '__main__':
    if init_app():
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
