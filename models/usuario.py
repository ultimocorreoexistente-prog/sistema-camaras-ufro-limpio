
from datetime import datetime
import bcrypt
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from models.base import BaseModelMixin
=======
from datetime import datetime, timezone # ✅ Corregido: Importar timezone
import bcrypt
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from . import db
from models.base import BaseModel  # ✅ Usa BaseModel (que sí existe)


db = SQLAlchemy()


class Usuario(BaseModelMixin, db.Model):
    __tablename__ = 'usuarios'

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # Corregido: era String(18)
    full_name = Column(String(100), nullable=False)  # Campo correcto para templates
    role = Column(String(20), nullable=False, default='visualizador')  # Corregido: era String(0)
    phone = Column(String(20), nullable=True)  # Corregido: era String(0)

class Usuario(UserMixin, BaseModel):  # ✅ Hereda solo de BaseModel
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

    password_changed_at = Column(DateTime, default=datetime.utcnow)
    must_change_password = Column(Boolean, default=False)
    preferences = Column(Text, nullable=True)

    # Relaciones con fallas
    fallas_creadas = relationship("Falla", foreign_keys="Falla.creado_por_id", back_populates="creado_por")
    fallas_asignadas = relationship("Falla", foreign_keys="Falla.asignado_a_id", back_populates="asignado_a")
    falla_comentarios = relationship("FallaComentario", back_populates="usuario")

    # Relaciones opcionales (pueden causar problemas)
    # logs = relationship("UsuarioLog", back_populates="usuario", cascade="all, delete-orphan")

    def set_password(self, password):
        """Establecer contraseña con bcrypt"""
        try:
            self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            self.password_changed_at = datetime.utcnow()
=======
    password_changed_at = Column(DateTime, default=datetime.now(timezone.utc)) # ✅ Corregido
    must_change_password = Column(Boolean, default=False)
    preferences = Column(Text, nullable=True)

    def set_password(self, password):
        """Establecer contraseña con bcrypt (seguro)"""
        try:
            self.password_hash = bcrypt.hashpw(
                password.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            self.password_changed_at = datetime.now(timezone.utc) # ✅ Corregido

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
=======
        """Verificar contraseña con bcrypt"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                self.password_hash.encode('utf-8')
            )
        except Exception:
            # Es importante no revelar el motivo de la falla por seguridad
            return False

    def is_locked(self):
        return self.locked_until and self.locked_until > datetime.now(timezone.utc) # ✅ Corregido

    def has_role(self, role):
        """Verificación jerárquica de roles"""

        if self.role == 'superadmin':
            return True
        return self.role == role

    @classmethod
    def get_by_email(cls, email):

        """Obtener usuario por email"""
        return cls.query.filter_by(email=email, deleted=False).first()

    def __repr__(self):
        return f"<Usuario(username='{self.username}', email='{self.email}');>"

        return cls.query.filter_by(email=email).first()

    def __repr__(self):
        return f"<Usuario(id={self.id}, username='{self.username}', email='{self.email}')>"

