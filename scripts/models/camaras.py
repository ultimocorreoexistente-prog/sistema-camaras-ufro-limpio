# models/camara.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db

class Camara(BaseModel, db.Model):
__tablename__ = 'camaras'

codigo = Column(String(50), unique=True, nullable=False)
nombre = Column(String(100), nullable=False)
modelo = Column(String(100), nullable=True)
marca = Column(String(50), nullable=True)
estado = Column(String(0), nullable=False, default='activo')

# Relaciones obligatorias
ubicacion_id = Column(Integer, ForeignKey('ubicaciones.id'), nullable=False)
ubicacion = relationship("Ubicacion", back_populates="camaras")

created_by_user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
created_by_user = relationship("Usuario", back_populates="created_camaras")

switch_id = Column(Integer, ForeignKey('switches.id'), nullable=True)
switch = relationship("Switch", back_populates="camaras")

# CORREGIDO: nvr_dvr.id (no nvrs.id)
nvr_id = Column(Integer, ForeignKey('nvr_dvr.id'), nullable=True)
nvr = relationship("NVR", back_populates="camaras")

ip_address = Column(String(45), nullable=True)
mac_address = Column(String(17), nullable=True)
fecha_instalacion = Column(DateTime, default=datetime.utcnow)
observaciones = Column(Text, nullable=True)

fallas = relationship("Falla", back_populates="camara")
mantenimientos = relationship("Mantenimiento", back_populates="camara")
fotografias = relationship("Fotografia", back_populates="camara")

def __repr__(self):
return f"<Camara(codigo='{self.codigo}', nombre='{self.nombre}')>"