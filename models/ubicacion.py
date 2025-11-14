# models/ubicacion.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db

class Ubicacion(BaseModel, db.Model):
    __tablename__ = 'ubicaciones'

    nombre = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)
    codigo = Column(String(50), unique=True, nullable=True)

    parent_id = Column(Integer, ForeignKey('ubicaciones.id'), nullable=True)
    parent = relationship(
        "Ubicacion",
        foreign_keys=[parent_id],
        remote_side=lambda: [Ubicacion.id],  # ✅ lambda
        backref="children"
    )

    latitud = Column(String(20), nullable=True)
    longitud = Column(String(20), nullable=True)
    descripcion = Column(Text, nullable=True)

    created_by_user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    created_by_user = relationship("Usuario", back_populates="created_ubicaciones")

    camaras = relationship("Camara", back_populates="ubicacion")
    switches = relationship("Switch", back_populates="ubicacion")  # ✅ ahora sí existe Switch.ubicacion
    ups_list = relationship("UPS", back_populates="ubicacion")
    nvr_list = relationship("NVR", back_populates="ubicacion")
    gabinetes = relationship("Gabinete", back_populates="ubicacion")
    fuentes_poder = relationship("FuentePoder", back_populates="ubicacion")
    fotografias = relationship("Fotografia", back_populates="ubicacion")

    @classmethod
    def get_by_codigo(cls, codigo):
        return cls.query.filter_by(codigo=codigo, deleted=False).first()