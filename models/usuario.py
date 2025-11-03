"""
Modelo de usuarios con sistema de roles y autenticación.

Incluye funcionalidades para gestión de usuarios, roles, permisos y logs de actividad.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db, UserRole


class Usuario(BaseModel, db.Model):
    """
    Modelo de usuario del sistema.
    
    Attributes:
        username (str): Nombre de usuario único
        email (str): Correo electrónico único
        password_hash (str): Hash de la contraseña
        full_name (str): Nombre completo
        role (str): Rol del usuario
        is_active (bool): Estado del usuario
        last_login (datetime): Última fecha de inicio de sesión
        failed_login_attempts (int): Intentos fallidos de inicio de sesión
        locked_until (datetime): Fecha hasta la cual está bloqueado
        password_changed_at (datetime): Fecha del último cambio de contraseña
        must_change_password (bool): Debe cambiar la contraseña
    """
    
    __tablename__ = 'usuarios'
    
    # Campos de autenticación
    username = Column(String(50), unique=True, nullable=False, index=True,
                     comment="Nombre de usuario único")
    email = Column(String(100), unique=True, nullable=False, index=True,
                  comment="Correo electrónico único")
    password_hash = Column(String(255), nullable=False,
                          comment="Hash de la contraseña")
    
    # Campos de perfil
    full_name = Column(String(100), nullable=False,
                      comment="Nombre completo del usuario")
    role = Column(String(20), nullable=False, default=UserRole.VISUALIZADOR,
                 comment="Rol del usuario en el sistema")
    phone = Column(String(20), nullable=True,
                  comment="Teléfono de contacto")
    department = Column(String(50), nullable=True,
                       comment="Departamento o área")
    
    # Estado y seguridad
    is_active = Column(Boolean, default=True, nullable=False,
                      comment="Estado del usuario (activo/inactivo)")
    last_login = Column(DateTime, nullable=True,
                       comment="Fecha y hora del último inicio de sesión")
    failed_login_attempts = Column(Integer, default=0, nullable=False,
                                  comment="Intentos fallidos de inicio de sesión")
    locked_until = Column(DateTime, nullable=True,
                         comment="Fecha hasta la cual está bloqueado")
    password_changed_at = Column(DateTime, default=datetime.utcnow, nullable=False,
                                comment="Fecha del último cambio de contraseña")
    must_change_password = Column(Boolean, default=False, nullable=False,
                                 comment="Debe cambiar la contraseña en el próximo inicio de sesión")
    
    # Configuraciones
    preferences = Column(Text, nullable=True,
                        comment="Configuraciones del usuario en formato JSON")
    
    # Relaciones
    logs = relationship("UsuarioLog", back_populates="usuario", cascade="all, delete-orphan")
    created_ubicaciones = relationship("Ubicacion", back_populates="created_by_user")
    created_camaras = relationship("Camara", back_populates="created_by_user")
    created_fallas = relationship("Falla", back_populates="created_by_user")
    created_mantenimientos = relationship("Mantenimiento", back_populates="created_by_user")
    created_fotografias = relationship("Fotografia", back_populates="created_by_user")
    
    def set_password(self, password):
        """
        Establece la contraseña del usuario.
        
        Args:
            password (str): Contraseña en texto plano
        """
        self.password_hash = generate_password_hash(password)
        self.password_changed_at = datetime.utcnow()
        self.must_change_password = False
    
    def check_password(self, password):
        """
        Verifica la contraseña del usuario.
        
        Args:
            password (str): Contraseña en texto plano
            
        Returns:
            bool: True si la contraseña es correcta
        """
        return check_password_hash(self.password_hash, password)
    
    def is_locked(self):
        """
        Verifica si el usuario está bloqueado.
        
        Returns:
            bool: True si el usuario está bloqueado
        """
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def lock_user(self, duration_minutes=30):
        """
        Bloquea al usuario por un período determinado.
        
        Args:
            duration_minutes (int): Duración del bloqueo en minutos
        """
        from datetime import timedelta
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.save()
    
    def unlock_user(self):
        """
        Desbloquea al usuario.
        """
        self.locked_until = None
        self.failed_login_attempts = 0
        self.save()
    
    def record_login_attempt(self, successful=True):
        """
        Registra un intento de inicio de sesión.
        
        Args:
            successful (bool): True si el intento fue exitoso
        """
        if successful:
            self.last_login = datetime.utcnow()
            self.failed_login_attempts = 0
            self.unlock_user()
        else:
            self.failed_login_attempts += 1
            # Bloquear después de 5 intentos fallidos
            if self.failed_login_attempts >= 5:
                self.lock_user()
        
        self.save()
    
    def has_role(self, role):
        """
        Verifica si el usuario tiene un rol específico.
        
        Args:
            role (str): Rol a verificar
            
        Returns:
            bool: True si tiene el rol
        """
        # Super admin tiene todos los roles
        if self.role == UserRole.ADMINISTRADOR:
            return True
        
        return self.role == role
    
    def can_access_resource(self, resource, action):
        """
        Verifica si el usuario puede realizar una acción en un recurso.
        
        Args:
            resource (str): Tipo de recurso
            action (str): Acción a realizar
            
        Returns:
            bool: True si tiene permisos
        """
        permissions = {
            UserRole.ADMINISTRADOR: ['*'],
            UserRole.TECNICO: ['view', 'create', 'update', 'maintain'],
            UserRole.OPERADOR: ['view', 'create', 'update'],
            UserRole.VISUALIZADOR: ['view']
        }
        
        user_permissions = permissions.get(self.role, [])
        
        return '*' in user_permissions or action in user_permissions
    
    def log_activity(self, action, details=None, ip_address=None):
        """
        Registra actividad del usuario.
        
        Args:
            action (str): Acción realizada
            details (str): Detalles adicionales
            ip_address (str): Dirección IP
        """
        log = UsuarioLog(
            usuario_id=self.id,
            action=action,
            details=details,
            ip_address=ip_address
        )
        log.save()
    
    @classmethod
    def get_by_username(cls, username):
        """
        Obtiene un usuario por nombre de usuario.
        
        Args:
            username (str): Nombre de usuario
            
        Returns:
            Usuario: Usuario encontrado o None
        """
        return cls.query.filter_by(username=username, deleted=False).first()
    
    @classmethod
    def get_by_email(cls, email):
        """
        Obtiene un usuario por correo electrónico.
        
        Args:
            email (str): Correo electrónico
            
        Returns:
            Usuario: Usuario encontrado o None
        """
        return cls.query.filter_by(email=email, deleted=False).first()
    
    @classmethod
    def get_active_users(cls):
        """
        Obtiene todos los usuarios activos.
        
        Returns:
            list: Lista de usuarios activos
        """
        return cls.query.filter_by(is_active=True, deleted=False).all()
    
    def to_dict(self):
        """
        Convierte el usuario a diccionario (sin contraseña).
        
        Returns:
            dict: Diccionario con los datos del usuario
        """
        data = super().to_dict()
        # Remover datos sensibles
        data.pop('password_hash', None)
        return data


class UsuarioLog(BaseModel, db.Model):
    """
    Log de actividad de usuarios.
    
    Attributes:
        usuario_id (int): ID del usuario
        action (str): Acción realizada
        details (str): Detalles adicionales
        ip_address (str): Dirección IP
        user_agent (str): User agent del navegador
    """
    
    __tablename__ = 'usuario_logs'
    
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False,
                       comment="ID del usuario")
    action = Column(String(50), nullable=False,
                   comment="Acción realizada")
    details = Column(Text, nullable=True,
                    comment="Detalles adicionales")
    ip_address = Column(String(45), nullable=True,
                       comment="Dirección IP del cliente")
    user_agent = Column(Text, nullable=True,
                       comment="User agent del navegador")
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="logs")
    
    def __repr__(self):
        return f"<UsuarioLog(usuario_id={self.usuario_id}, action='{self.action}')>"


class UsuarioRol(BaseModel, db.Model):
    """
    Tabla de configuración de roles.
    
    Attributes:
        role_name (str): Nombre del rol
        description (str): Descripción del rol
        permissions (str): Permisos en formato JSON
    """
    
    __tablename__ = 'usuario_roles'
    
    role_name = Column(String(50), unique=True, nullable=False,
                      comment="Nombre único del rol")
    description = Column(String(200), nullable=True,
                        comment="Descripción del rol")
    permissions = Column(Text, nullable=True,
                        comment="Permisos en formato JSON")
    
    def __repr__(self):
        return f"<UsuarioRol(role_name='{self.role_name}')>"