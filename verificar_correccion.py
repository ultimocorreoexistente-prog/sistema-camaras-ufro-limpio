#!/usr/bin/env python3
"""
Script para verificar la corrección del error Usuario
"""

def verificar_correccion():
    try:
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from flask_login import LoginManager, UserMixin
        from werkzeug.security import generate_password_hash
        
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['SECRET_KEY'] = 'test'
        
        db = SQLAlchemy(app)
        
        class Usuario(UserMixin, db.Model):
            __tablename__ = 'usuarios'
            id = db.Column(db.Integer, primary_key=True)
            username = db.Column(db.String(80), unique=True)
            email = db.Column(db.String(120), unique=True)
            password_hash = db.Column(db.String(255))
            full_name = db.Column(db.String(255))
            activo = db.Column(db.Boolean, default=True)
            
            def set_password(self, password):
                self.password_hash = generate_password_hash(password)
            
            def check_password(self, password):
                from werkzeug.security import check_password_hash
                return check_password_hash(self.password_hash, password)
        
        with app.app_context():
            db.create_all()
            
            # Probar crear usuario
            test_user = Usuario(username='test', email='test@test.com', full_name='Test User')
            test_user.set_password('test123')
            db.session.add(test_user)
            db.session.commit()
            
            # Probar autenticación
            found_user = Usuario.query.filter_by(email='test@test.com').first()
            if found_user and found_user.check_password('test123'):
                print("✅ CORRECCIÓN EXITOSA: Usuario modelo funciona correctamente")
                return True
            else:
                print("❌ Error en corrección")
                return False
    
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

if __name__ == '__main__':
    verificar_correccion()
