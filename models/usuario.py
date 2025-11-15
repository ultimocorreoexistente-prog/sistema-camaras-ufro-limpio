from datetime import datetime
import bcrypt
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from models.base import BaseModelMixin

db = SQLAlchemy()

class Usuario(BaseModelMixin, db.Model):
    __tablename__ = 'usuarios'

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # Corregido: era String(18)
    full_name = Column(String(100), nullable=False)  # Campo correcto para templates
    role = Column(String(20), nullable=False, default='visualizador')  # Corregido: era String(0)
    phone = Column(String(20), nullable=True)  # Corregido: era String(0)
    department = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, default=datetime.utcnow)
    must_change_password = Column(Boolean, default=False)
    preferences = Column(Text, nullable=True)

    # Relaciones opcionales (pueden causar problemas)
    # logs = relationship("UsuarioLog", back_populates="usuario", cascade="all, delete-orphan")

    def set_password(self, password):
        """Establecer contraseña con bcrypt"""
        try:
            self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            self.password_changed_at = datetime.utcnow()
            self.must_change_password = False
        except Exception as e:
            raise Exception(f"Error estableciendo contraseña: {e}")

    def check_password(self, password):
        """Verificar contraseña"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except Exception as e:
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

    def __repr__(self):
        return f"<Usuario(username='{self.username}', email='{self.email}');>"