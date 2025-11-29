from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import db, TimestampedModel

class Camara(db.Model, TimestampedModel):
    __tablename__ = 'camaras'
    id = Column(Integer, primary_key=True)

    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    modelo = Column(String(100), nullable=True)
    marca = Column(String(50), nullable=True)
    tipo_camara = Column(String(50), nullable=False, default='IP')
    estado = Column(String(20), nullable=False, default='activo')
    
    # Campos de red y sistema
    ip_address = Column(String(45), unique=True, nullable=True, index=True)
    mac_address = Column(String(17), nullable=True)
    serie = Column(String(100), nullable=True)
    ultima_conexion = Column(DateTime, nullable=True)
    fecha_instalacion = Column(DateTime, nullable=True)
    observaciones = Column(Text, nullable=True)

    # Relaciones
    ubicacion_id = Column(Integer, ForeignKey('ubicaciones.id'), nullable=True)
    ubicacion = relationship("Ubicacion", back_populates="camaras")

    switch_id = Column(Integer, ForeignKey('switches.id'), nullable=True)
    switch = relationship("Switch", back_populates="camaras")

    nvr_id = Column(Integer, ForeignKey('nvrs.id'), nullable=True)
    nvr = relationship("NVR", back_populates="camaras")

    # Relación con gabinete
    gabinete_id = Column(Integer, ForeignKey('gabinetes.id'), nullable=True)
    gabinete = relationship("Gabinete", back_populates="camaras")

    @property
    def ip(self):
        """Property para compatibilidad con templates"""
        return self.ip_address

    def __repr__(self):
        return f"<Camara(codigo='{self.codigo}', nombre='{self.nombre}')>"
