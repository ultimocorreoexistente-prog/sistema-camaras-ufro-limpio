from datetime import datetime, timezone
import bcrypt
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from . import db
from models.base import BaseModel

class Usuario(UserMixin, BaseModel):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default='visualizador')
    phone = Column(String(20), nullable=True)
    department = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, default=datetime.now(timezone.utc))
    must_change_password = Column(Boolean, default=False)
    preferences = Column(Text, nullable=True)

    def set_password(self, password):
        """Establecer contraseña con bcrypt (seguro)"""
        try:
            self.password_hash = bcrypt.hashpw(
                password.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            self.password_changed_at = datetime.now(timezone.utc)
            self.must_change_password = False
        except Exception as e:
            raise Exception(f"Error estableciendo contraseña: {e}")

    def check_password(self, password):
        """Verificar contraseña con bcrypt"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                self.password_hash.encode('utf-8')
            )
        except Exception:
            return False

    def is_locked(self):
        return self.locked_until and self.locked_until > datetime.now(timezone.utc)

    def has_role(self, role):
        """Verificación jerárquica de roles"""
        if self.role == 'superadmin':
            return True
        return self.role == role

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def __repr__(self):
        return f"<Usuario(id={self.id}, username='{self.username}', email='{self.email}')>"