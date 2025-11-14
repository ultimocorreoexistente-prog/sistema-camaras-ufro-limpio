from datetime import datetime 
import bcrypt
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db
from models.usuario_roles import UserRole

class Usuario(BaseModel, db.Model):
    __tablename__ = 'usuarios'
    
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default=UserRole.VISUALIZADOR)
    phone = Column(String(20), nullable=True)
    department = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, default=datetime.utcnow)
    must_change_password = Column(Boolean, default=False)
    preferences = Column(Text, nullable=True)
    
    logs = relationship("UsuarioLog", back_populates="usuario", cascade="all, delete-orphan")
    created_ubicaciones = relationship("Ubicacion", back_populates="created_by_user")
    created_camaras = relationship("Camara", back_populates="created_by_user")
    created_fallas = relationship("Falla", back_populates="created_by_user")
    created_mantenimientos = relationship("Mantenimiento", back_populates="created_by_user")
    created_fotografias = relationship("Fotografia", back_populates="created_by_user")

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.password_changed_at = datetime.utcnow()
        self.must_change_password = False
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def is_locked(self):
        return self.locked_until and self.locked_until > datetime.utcnow()
    
    def has_role(self, role):
        if self.role == UserRole.SUPERADMIN:
            return True
        return self.role == role
    
    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email, deleted=False).first()