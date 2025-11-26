<<<<<<< HEAD
# models/fotografia.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db

class Fotografia(BaseModel, db.Model):
__tablename__ = 'fotografias'

equipo_id = Column(Integer, nullable=True)
equipo_type = Column(String(50), nullable=True)

ubicacion_id = Column(Integer, ForeignKey('ubicaciones.id'), nullable=True)
ubicacion = relationship("Ubicacion", back_populates="fotografias")

filename = Column(String(55), nullable=False)
filepath = Column(String(500), nullable=False)
description = Column(Text, nullable=True)
status = Column(String(0), nullable=False, default='procesando')

parent_id = Column(Integer, ForeignKey('fotografias.id'), nullable=True)
parent_photo = relationship(
"Fotografia",
foreign_keys=[parent_id],
remote_side=lambda: [Fotografia.id], # lambda para evitar builtins.id
backref="versions"
)

created_by_user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
created_by_user = relationship("Usuario", back_populates="created_fotografias")

# RELACIONES COMPLETAS — todas con FKs y relationship
camara_id = Column(Integer, ForeignKey('camaras.id'), nullable=True)
camara = relationship("Camara", back_populates="fotografias")

nvr_id = Column(Integer, ForeignKey('nvr_dvr.id'), nullable=True)
nvr = relationship("NVR", back_populates="fotografias")

ups_id = Column(Integer, ForeignKey('ups.id'), nullable=True)
ups = relationship("UPS", back_populates="fotografias")

gabinete_id = Column(Integer, ForeignKey('gabinetes.id'), nullable=True)
gabinete = relationship("Gabinete", back_populates="fotografias")

fuente_poder_id = Column(Integer, ForeignKey('fuente_poder.id'), nullable=True)
fuente_poder = relationship("FuentePoder", back_populates="fotografias")

switch_id = Column(Integer, ForeignKey('switches.id'), nullable=True)
switch = relationship("Switch", back_populates="fotografias")

captured_at = Column(DateTime, nullable=True)
uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
metadata_json = Column(Text, nullable=True)

def __repr__(self):
return f"<Fotografia(id={self.id}, filename='{self.filename}', status='{self.status}')>"
=======
"""
Modelo de fotografías del sistema de cámaras.
Representa imágenes asociadas a equipos, ubicaciones, fallas, etc.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db


class Fotografia(BaseModel, db.Model):
    """
    Modelo de fotografías del sistema.

    Attributes:
        titulo (str): Título descriptivo
        descripcion (str): Descripción detallada
        archivo (str): Ruta del archivo en el sistema
        tipo (str): Tipo de fotografía (instalación, mantenimiento, falla, etc.)
        entidad_tipo (str): Tipo de entidad a la que está asociada
        entidad_id (int): ID de la entidad asociada
        usuario_id (int): ID del usuario que subió la foto
    """

    __tablename__ = 'fotografias'

    # ✅ Corrección crítica: primary key obligatoria
    id = Column(Integer, primary_key=True)

    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    archivo = Column(String(300), nullable=False)
    tipo = Column(String(50))
    entidad_tipo = Column(String(50))
    entidad_id = Column(Integer)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    usuario = relationship("Usuario", back_populates="fotografias")

    def __repr__(self):
        return f"<Fotografia(id={self.id}, titulo='{self.titulo}', archivo='{self.archivo}')>"

    @property
    def url(self):
        """Obtiene la URL pública de la fotografía."""
        return f"/uploads/fotos/{self.archivo}"

    def es_valida(self):
        """Verifica si la fotografía es válida para mostrar."""
        return self.activo and self.archivo and self.titulo
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
