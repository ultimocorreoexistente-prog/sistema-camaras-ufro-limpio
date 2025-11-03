"""
Clase base para todos los modelos SQLAlchemy.

Proporciona funcionalidades comunes como timestamps, soft delete y métodos de utilidad.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean, String, Text
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from models import db


class BaseModel:
    """
    Clase base abstracta que proporciona campos comunes a todos los modelos.
    
    Atributos:
        id (int): Clave primaria autoincremental
        created_at (datetime): Fecha y hora de creación del registro
        updated_at (datetime): Fecha y hora de la última actualización
        deleted (bool): Indica si el registro ha sido eliminado (soft delete)
        created_by (int): ID del usuario que creó el registro
        updated_by (int): ID del usuario que actualizó el registro
    """
    
    @declared_attr
    def id(cls):
        return Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.utcnow, nullable=False, 
                     comment="Fecha y hora de creación")
    
    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, 
                     nullable=False, comment="Fecha y hora de última actualización")
    
    @declared_attr
    def deleted(cls):
        return Column(Boolean, default=False, nullable=False,
                     comment="Indica si el registro ha sido eliminado")
    
    @declared_attr
    def created_by(cls):
        return Column(Integer, nullable=True,
                     comment="ID del usuario que creó el registro")
    
    @declared_attr
    def updated_by(cls):
        return Column(Integer, nullable=True,
                     comment="ID del usuario que actualizó el registro")
    
    def __repr__(self):
        """Representación string del objeto."""
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', None)})>"
    
    def to_dict(self):
        """
        Convierte el modelo a un diccionario.
        
        Returns:
            dict: Diccionario con los atributos del modelo
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def soft_delete(self, user_id=None):
        """
        Realiza un soft delete del registro.
        
        Args:
            user_id (int): ID del usuario que realiza la eliminación
        """
        self.deleted = True
        self.updated_at = datetime.utcnow()
        if user_id:
            self.updated_by = user_id
        db.session.commit()
    
    def restore(self, user_id=None):
        """
        Restaura un registro eliminado (soft delete).
        
        Args:
            user_id (int): ID del usuario que realiza la restauración
        """
        self.deleted = False
        self.updated_at = datetime.utcnow()
        if user_id:
            self.updated_by = user_id
        db.session.commit()
    
    @classmethod
    def get_active(cls):
        """
        Obtiene todos los registros activos (no eliminados).
        
        Returns:
            Query: Query con los registros activos
        """
        return cls.query.filter_by(deleted=False)
    
    @classmethod
    def get_deleted(cls):
        """
        Obtiene todos los registros eliminados.
        
        Returns:
            Query: Query con los registros eliminados
        """
        return cls.query.filter_by(deleted=True)
    
    @classmethod
    def get_by_id(cls, id):
        """
        Obtiene un registro por ID, solo si no está eliminado.
        
        Args:
            id (int): ID del registro
            
        Returns:
            Model: Registro encontrado o None
        """
        return cls.query.filter_by(id=id, deleted=False).first()
    
    @classmethod
    def get_all(cls, include_deleted=False):
        """
        Obtiene todos los registros.
        
        Args:
            include_deleted (bool): Si incluir registros eliminados
            
        Returns:
            Query: Query con todos los registros
        """
        if include_deleted:
            return cls.query
        return cls.get_active()
    
    def save(self, user_id=None):
        """
        Guarda el registro en la base de datos.
        
        Args:
            user_id (int): ID del usuario que realiza la operación
        """
        if user_id:
            self.updated_by = user_id
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self, user_id=None):
        """
        Elimina el registro de la base de datos.
        
        Args:
            user_id (int): ID del usuario que realiza la operación
        """
        self.updated_by = user_id
        db.session.delete(self)
        db.session.commit()


def get_model_table_name(model_name):
    """
    Obtiene el nombre de tabla para un modelo.
    
    Args:
        model_name (str): Nombre del modelo
        
    Returns:
        str: Nombre de la tabla en minúsculas
    """
    # Convertir camelCase a snake_case y agregar 's' para plural
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', model_name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    table_name = re.sub(r'\s+', '_', s2.lower())
    
    # Pluralizar (lógica simple)
    if not table_name.endswith('s'):
        table_name += 's'
    
    return table_name