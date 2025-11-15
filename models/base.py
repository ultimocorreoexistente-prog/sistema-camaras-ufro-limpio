from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, Boolean, String
from datetime import datetime

# Base para todos los modelos
BaseModel = declarative_base()

class BaseModelMixin:
    """Mixin base para todos los modelos SQLAlchemy"""
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted = Column(Boolean, default=False)
    
    @property
    def is_active(self):
        """Property para compatibilidad"""
        return not self.deleted
    
    @is_active.setter  
    def is_active(self, value):
        """Setter para compatibilidad"""
        self.deleted = not value
    
    def save(self, session=None):
        """Guardar instancia en base de datos"""
        if session is None:
            from models import db
            session = db.session
        session.add(self)
        session.commit()
        return self
    
    def delete(self, session=None):
        """Soft delete"""
        if session is None:
            from models import db
            session = db.session
        self.deleted = True
        session.commit()
        return self
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}