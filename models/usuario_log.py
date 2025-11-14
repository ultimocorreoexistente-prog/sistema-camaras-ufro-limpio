#from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db

class UsuarioLog(BaseModel, db.Model):
    __tablename__ = 'usuario_logs'
    
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    action = Column(String(50), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    usuario = relationship("Usuario", back_populates="logs")
    
    def __repr__(self):
        return f"<UsuarioLog(usuario_id={self.usuario_id}, action='{self.action}')>"