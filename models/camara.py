from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from models.base import BaseModelMixin

db = SQLAlchemy()

class Camara(BaseModelMixin, db.Model):
    __tablename__ = 'camaras'

    codigo = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    modelo = Column(String(100), nullable=True)  # Corregido: era String(0)
    marca = Column(String(50), nullable=True)    # Corregido: era String(0)
    tipo_camara = Column(String(50), nullable=False, default='IP')  # Campo faltante
    estado = Column(String(20), nullable=False, default='activo')   # Corregido: era String(0)
    
    # Relaciones opcionales
    # ubicacion_id = Column(Integer, ForeignKey('ubicaciones.id'), nullable=False)
    # ubicacion = relationship("Ubicacion", back_populates="camaras")
    
    # created_by_user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    # created_by_user = relationship("Usuario", back_populates="created_camaras")
    
    # switch_id = Column(Integer, ForeignKey('switches.id'), nullable=True)
    # switch = relationship("Switch", back_populates="camaras")
    
    # nvr_id = Column(Integer, ForeignKey('nvr.id'), nullable=True)
    # nvr = relationship("NVR", back_populates="camaras")
    
    ip_address = Column(String(45), nullable=True)  # Corregido: era String(0)
    mac_address = Column(String(17), nullable=True)
    fecha_instalacion = Column(DateTime, default=datetime.utcnow)
    observaciones = Column(Text, nullable=True)     # Corregido: era String(0)

    # Relaciones opcionales (pueden causar problemas)
    # fallas = relationship("Falla", back_populates="camara")
    # mantenimientos = relationship("Mantenimiento", back_populates="camara")
    # fotografias = relationship("Fotografia", back_populates="camara")

    @property
    def ip(self):
        """Property para compatibilidad con templates"""
        return self.ip_address

    def __repr__(self):
        return f"<Camara(codigo='{self.codigo}', nombre='{self.nombre}')>"