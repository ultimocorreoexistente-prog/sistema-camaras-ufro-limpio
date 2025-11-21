from datetime import datetime, timedelta
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave-secreta-por-defecto')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///sistema_camaras.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelo Usuario corregido usando la estructura exacta de la base de datos
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='visualizador')
    phone = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    must_change_password = db.Column(db.Boolean, default=False)
    preferences = db.Column(db.Text, nullable=True)
    deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Establecer contraseña con bcrypt"""
        try:
            self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            self.password_changed_at = datetime.utcnow()
            self.must_change_password = False
        except Exception as e:
            raise Exception(f"Error estableciendo contraseña: {e}")
    
    def check_password(self, password):
        """Verificar contraseña con bcrypt"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except Exception as e:
            # Fallback a werkzeug si bcrypt falla
            try:
                return check_password_hash(self.password_hash, password)
            except:
                return False
    
    def is_locked(self):
        """Verificar si el usuario está bloqueado"""
        return self.locked_until and self.locked_until > datetime.utcnow()
    
    def has_role(self, role):
        """Verificar si tiene rol específico"""
        if self.role == 'superadmin':
            return True
        return self.role == role
    
    @classmethod
    def get_by_email(cls, email):
        """Obtener usuario por email"""
        return cls.query.filter_by(email=email, deleted=False).first()

@login_manager.user_loader
def load_user(user_id):
    try:
        return Usuario.query.get(int(user_id))
    except:
        return None

# Rutas principales
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email') or request.form.get('username')
            password = request.form.get('password')
            
            if not email or not password:
                flash('Por favor ingresa email y contraseña', 'error')
                return render_template('login.html')
            
            # Buscar usuario por email
            user = Usuario.query.filter_by(email=email, deleted=False).first()
            
            if user and user.is_active and not user.is_locked() and user.check_password(password):
                login_user(user)
                user.last_login = datetime.utcnow()
                user.failed_login_attempts = 0
                db.session.commit()
                
                flash(f'Bienvenido {user.full_name}', 'success')
                return redirect(url_for('dashboard'))
            else:
                if user:
                    user.failed_login_attempts += 1
                    if user.failed_login_attempts >= 5:
                        user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                    db.session.commit()
                
                flash('Credenciales inválidas o cuenta bloqueada', 'error')
        except Exception as e:
            flash(f'Error en autenticación: {str(e)}', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login'))

# Ruta de prueba para verificar conexión a base de datos
@app.route('/test-db')
def test_db():
    try:
        # Verificar que la tabla existe y podemos hacer consultas
        user_count = Usuario.query.count()
        return f"""
        <h2>✅ Conexión a Base de Datos Exitosa</h2>
        <p><strong>Usuarios en la base de datos:</strong> {user_count}</p>
        <p><strong>Modelo Usuario:</strong> Cargado correctamente</p>
        <p><strong>Timestamps:</strong> Creado en {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
    except Exception as e:
        return f"""
        <h2>❌ Error de Base de Datos</h2>
        <p><strong>Error:</strong> {str(e)}</p>
        <p><strong>Timestamp:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """

@app.route('/usuarios')
@login_required
def usuarios():
    try:
        usuarios = Usuario.query.filter_by(deleted=False).all()
        return render_template('usuarios_list.html', usuarios=usuarios)
    except Exception as e:
        flash(f'Error cargando usuarios: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

# Inicialización de la aplicación
if __name__ == '__main__':
    with app.app_context():
        # Crear todas las tablas si no existen
        db.create_all()
        
        # Verificar si existe el usuario administrador
        admin_user = Usuario.query.filter_by(email='charles.jelvez@ufrontera.cl').first()
        if not admin_user:
            # Crear usuario administrador si no existe
            admin = Usuario(
                username='admin',
                email='charles.jelvez@ufrontera.cl',
                full_name='Administrador Sistema',
                role='superadmin',
                is_active=True
            )
            admin.set_password('Vivita0468')
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario administrador creado exitosamente")
        else:
            print("✅ Usuario administrador ya existe")
    
    # Ejecutar en modo desarrollo
    app.run(debug=True, host='0.0.0.0', port=5000)
