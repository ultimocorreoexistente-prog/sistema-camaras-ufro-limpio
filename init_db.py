from app import app, db
from models import Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    print('Tablas creadas exitosamente')
    
    if Usuario.query.count() == 0:
        usuarios = [
            Usuario(username='admin', rol='admin', nombre_completo='Administrador', activo=True),
            Usuario(username='supervisor', rol='supervisor', nombre_completo='Supervisor', activo=True),
            Usuario(username='tecnico1', rol='tecnico', nombre_completo='Técnico 1', activo=True),
            Usuario(username='visualizador', rol='visualizador', nombre_completo='Visualizador', activo=True)
        ]
        
        passwords = ['admin123', 'super123', 'tecnico123', 'viz123']
        
        for user, password in zip(usuarios, passwords):
            user.set_password(password)
            db.session.add(user)
        
        db.session.commit()
        print('Usuarios creados exitosamente')
    else:
        print('Los usuarios ya existen')
    
    print(f'\nTotal usuarios: {Usuario.query.count()}')
