from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

class BaseModel:
    @declared_attr
    def id(cls):
        return Column(Integer, primary_key=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted = Column(Boolean, default=False)
    
    @declared_attr
    def __tablename__(cls):
        name = cls.__name__.lower()
        if name.endswith('y'):
            return name[:-1] + 'ies'
        elif name.endswith(('s', 'x', 'z')):
            return name + 'es'
        else:
            return name + 's'

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}