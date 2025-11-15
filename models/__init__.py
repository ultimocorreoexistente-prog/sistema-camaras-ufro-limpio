from flask_sqlalchemy import SQLAlchemy

# Inicializar SQLAlchemy
db = SQLAlchemy()

# Importaciones de modelos para que SQLAlchemy los registre
def init_models():
    """Inicializar todos los modelos"""
    from .usuario import Usuario
    from .camara import Camara
    return Usuario, Camara

def init_db(app):
    """Inicializar base de datos con app Flask"""
    global db
    db.init_app(app)
    
    # Importar todos los modelos para que SQLAlchemy los registre
    Usuario, Camara = init_models()
    
    # Crear todas las tablas
    with app.app_context():
        db.create_all()
        
        # Crear superadmin si no existe
        if not Usuario.query.filter_by(email='admin@ufro.cl').first():
            admin = Usuario(
                username='admin',
                email='admin@ufro.cl', 
                full_name='Administrador Sistema',
                role='superadmin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Superadmin creado: admin@ufro.cl / admin123")

# Importaciones directas para compatibilidad
__all__ = ['db', 'init_db', 'init_models']