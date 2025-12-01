from datetime import datetime, timezone
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import db
from .base import TimestampedModel

try:
    from werkzeug.security import generate_password_hash, check_password_hash
    _has_werkzeug = True
except ImportError:
    _has_werkzeug = False

class Usuario(db.Model, UserMixin, TimestampedModel):
    __tablename__ = 'usuarios'
    
    # ✅ Clave primaria EXPLÍCITA (obligatoria en SQLAlchemy 2.0+)
    id = Column(Integer, primary_key=True)
    
    # Resto de campos (sin cambios)
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
    password_changed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    must_change_password = Column(Boolean, default=False)
    preferences = Column(Text, nullable=True)
    
    # Relación con Rol
    rol_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    rol = relationship("Rol", back_populates="usuarios")

    # Relaciones con fallas
    fallas_creadas = relationship("Falla", foreign_keys="Falla.creado_por_id", back_populates="creado_por")
    fallas_asignadas = relationship("Falla", foreign_keys="Falla.asignado_a_id", back_populates="asignado_a")
    falla_comentarios = relationship("FallaComentario", back_populates="usuario")
    
    # Relación con logs de usuario
    logs = relationship("UsuarioLog", back_populates="usuario", cascade="all, delete-orphan")

    def set_password(self, password):
        """Establecer contraseña usando werkzeug (compatible con Flask)"""
        try:
            if _has_werkzeug:
                self.password_hash = generate_password_hash(password)
            else:
                self.password_hash = password
            self.password_changed_at = datetime.now(timezone.utc)
            self.must_change_password = False
        except Exception as e:
            raise Exception(f"Error estableciendo contraseña: {e}")

    def check_password(self, password):
        """Verificar contraseña usando werkzeug"""
        try:
            if _has_werkzeug:
                return check_password_hash(self.password_hash, password)
            else:
                return self.password_hash == password
        except Exception:
            return False

    def is_locked(self):
        return self.locked_until and self.locked_until > datetime.now(timezone.utc)

    def has_role(self, role):
        if self.role == 'superadmin':
            return True
        return self.role == role

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email, is_active=True).first()

    def __repr__(self):
        return f"<Usuario(id={self.id}, username='{self.username}', email='{self.email}')>"