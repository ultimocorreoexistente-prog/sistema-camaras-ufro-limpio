"""
Modelo SQLAlchemy para usuario_logs.

Este modelo registra todas las acciones y actividades realizadas por usuarios en el sistema.
Proporciona trazabilidad completa de operaciones para auditoría y monitoreo.

Estructura de 9 columnas:
- id: Clave primaria
- usuario_id: ForeignKey al usuario
- action: Acción realizada
- details: Detalles adicionales
- ip_address: Dirección IP del cliente
- user_agent: User agent del navegador
- created_at: Fecha de creación
- updated_at: Fecha de actualización
- deleted: Soft delete
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import TimestampedModel
from models import db


class UsuarioLog(db.Model, TimestampedModel):
    """
    Log de actividad de usuarios del sistema.

    Registra todas las acciones realizadas por usuarios para auditoría,
    monitoreo de seguridad y análisis de comportamiento.

    Campos:
    id (int): Clave primaria autoincremental
    usuario_id (int): ID del usuario que realizó la acción (FK)
    action (str): Tipo de acción realizada (login, logout, crear, editar, etc.)
    details (str): Detalles adicionales en formato texto
    ip_address (str): Dirección IP del cliente
    user_agent (str): User agent del navegador del cliente
    created_at (datetime): Fecha y hora de creación
    updated_at (datetime): Fecha y hora de última actualización
    deleted (bool): Soft delete
    created_by (int): ID del usuario que creó el registro
    updated_by (int): ID del usuario que actualizó el registro
    """

    __tablename__ = 'usuario_logs'

    # Identificador
    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID único del log")
    
    # Campos específicos del log
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False,
                        comment="ID del usuario que realizó la acción")
    action = Column(String(100), nullable=False,
                    comment="Tipo de acción realizada (login, logout, crear, editar, eliminar, etc.)")
    details = Column(Text, nullable=True,
                     comment="Detalles adicionales sobre la acción en formato texto libre")
    ip_address = Column(String(45), nullable=True,
                        comment="Dirección IP del cliente que realizó la acción")
    user_agent = Column(Text, nullable=True,
                        comment="User agent del navegador del cliente")

    # Relaciones
    usuario = relationship("Usuario", back_populates="logs")

    def __repr__(self):
        """Representación string del objeto UsuarioLog."""
        return f"<UsuarioLog(id={self.id}, usuario_id={self.usuario_id}, action='{self.action}')>"

    def to_dict(self):
        """
        Convierte el log a diccionario para serialización JSON.

        Returns:
        dict: Diccionario con todos los campos del log
        """
        data = {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted': self.deleted,
            'created_by': self.created_by,
            'updated_by': self.updated_by
        }
        return data

    @classmethod
    def create_log(cls, usuario_id, action, details=None, ip_address=None, user_agent=None, created_by=None):
        """
        Crea un nuevo log de actividad de usuario.

        Args:
            usuario_id (int): ID del usuario que realizó la acción
            action (str): Tipo de acción realizada
            details (str, optional): Detalles adicionales
            ip_address (str, optional): Dirección IP del cliente
            user_agent (str, optional): User agent del navegador
            created_by (int, optional): ID del usuario que crea el log

        Returns:
            UsuarioLog: Instancia del log creado
        """
        log = cls(
            usuario_id=usuario_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            created_by=created_by
        )
        return log.save(created_by)

    @classmethod
    def get_by_usuario(cls, usuario_id, include_deleted=False):
        """
        Obtiene todos los logs de un usuario específico.

        Args:
            usuario_id (int): ID del usuario
            include_deleted (bool): Si incluir logs eliminados

        Returns:
            Query: Query con los logs del usuario
        """
        query = cls.query.filter_by(usuario_id=usuario_id)
        if not include_deleted:
            query = query.filter_by(deleted=False)
        return query.order_by(cls.created_at.desc())

    @classmethod
    def get_by_action(cls, action, include_deleted=False):
        """
        Obtiene todos los logs de una acción específica.

        Args:
            action (str): Tipo de acción
            include_deleted (bool): Si incluir logs eliminados

        Returns:
            Query: Query con los logs de la acción
        """
        query = cls.query.filter_by(action=action)
        if not include_deleted:
            query = query.filter_by(deleted=False)
        return query.order_by(cls.created_at.desc())

    @classmethod
    def get_by_ip(cls, ip_address, include_deleted=False):
        """
        Obtiene todos los logs de una IP específica.

        Args:
            ip_address (str): Dirección IP
            include_deleted (bool): Si incluir logs eliminados

        Returns:
            Query: Query con los logs de la IP
        """
        query = cls.query.filter_by(ip_address=ip_address)
        if not include_deleted:
            query = query.filter_by(deleted=False)
        return query.order_by(cls.created_at.desc())

    @classmethod
    def get_recent_logs(cls, hours=4, include_deleted=False):
        """
        Obtiene los logs más recientes en un período de tiempo.

        Args:
            hours (int): Número de horas hacia atrás
            include_deleted (bool): Si incluir logs eliminados

        Returns:
            Query: Query con los logs recientes
        """
        from datetime import timedelta
        since = datetime.utcnow() - timedelta(hours=hours)

        query = cls.query.filter(cls.created_at >= since)
        if not include_deleted:
            query = query.filter_by(deleted=False)
        return query.order_by(cls.created_at.desc())

    @classmethod
    def log_user_action(cls, usuario_id, action, details=None, request=None, created_by=None):
        """
        Registra una acción de usuario automáticamente extrayendo datos del request.

        Args:
            usuario_id (int): ID del usuario
            action (str): Tipo de acción
            details (str, optional): Detalles adicionales
            request (Request, optional): Objeto request de Flask para extraer IP y user agent
            created_by (int, optional): ID del usuario que crea el log

        Returns:
            UsuarioLog: Instancia del log creado
        """
        ip_address = None
        user_agent = None

        if request:
            # Extraer IP (considerando proxies)
            ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ',' in ip_address:
                ip_address = ip_address.split(',')[0].strip()

            # Extraer user agent
            user_agent = request.headers.get('User-Agent')

        return cls.create_log(
            usuario_id=usuario_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            created_by=created_by
        )

    @classmethod
    def get_activity_summary(cls, usuario_id, days=30):
        """
        Obtiene un resumen de actividad de un usuario en un período.

        Args:
            usuario_id (int): ID del usuario
            days (int): Número de días hacia atrás

        Returns:
            dict: Resumen con conteos por acción
        """
        from datetime import timedelta
        since = datetime.utcnow() - timedelta(days=days)

        logs = cls.query.filter(
            cls.usuario_id == usuario_id,
            cls.created_at >= since,
            cls.deleted == False
        ).all()

        summary = {}
        for log in logs:
            action = log.action
            if action not in summary:
                summary[action] = 0
            summary[action] += 1

        return summary

    def log_action(self, action, details=None):
        """
        Registra una nueva acción para este log (actualiza el registro existente).

        Args:
            action (str): Nueva acción a registrar
            details (str, optional): Detalles adicionales
        """
        self.action = action
        if details:
            self.details = details
        self.updated_at = datetime.utcnow()
        return self.save()


# Función helper para registrar acciones comunes
def log_login_attempt(usuario_id, successful=True, request=None, details=None):
    """
    Registra un intento de login.

    Args:
        usuario_id (int): ID del usuario
        successful (bool): Si el login fue exitoso
        request (Request, optional): Objeto request de Flask
        details (str, optional): Detalles adicionales

    Returns:
        UsuarioLog: Log creado
    """
    action = 'login_success' if successful else 'login_failed'
    if details:
        details = f"Login {('exitoso' if successful else 'fallido')}: {details}"
    else:
        details = f"Login {'exitoso' if successful else 'fallido'}"

    return UsuarioLog.log_user_action(usuario_id, action, details, request)


def log_logout(usuario_id, request=None, details=None):
    """
    Registra un logout de usuario.

    Args:
        usuario_id (int): ID del usuario
        request (Request, optional): Objeto request de Flask
        details (str, optional): Detalles adicionales

    Returns:
        UsuarioLog: Log creado
    """
    return UsuarioLog.log_user_action(usuario_id, 'logout', details, request)


def log_crud_operation(usuario_id, operation, entity_type, entity_id=None, details=None, request=None):
    """
    Registra una operación CRUD (crear, leer, actualizar, eliminar).

    Args:
        usuario_id (int): ID del usuario
        operation (str): Tipo de operación (create, read, update, delete)
        entity_type (str): Tipo de entidad (usuario, camara, falla, etc.)
        entity_id (int, optional): ID de la entidad afectada
        details (str, optional): Detalles adicionales
        request (Request, optional): Objeto request de Flask

    Returns:
        UsuarioLog: Log creado
    """
    action = f"{operation}_{entity_type}"
    if entity_id and not details:
        details = f"{operation.capitalize()} {entity_type} ID: {entity_id}"
    elif details:
        details = f"{operation.capitalize()} {entity_type}: {details}"

    return UsuarioLog.log_user_action(usuario_id, action, details, request)


def log_system_action(usuario_id, action, details=None, request=None):
    """
    Registra una acción del sistema.

    Args:
        usuario_id (int): ID del usuario
        action (str): Acción del sistema
        details (str, optional): Detalles adicionales
        request (Request, optional): Objeto request de Flask

    Returns:
        UsuarioLog: Log creado
    """
    return UsuarioLog.log_user_action(usuario_id, f"system_{action}", details, request)
