"""
Modelo de fotografías del sistema de cámaras.
Representa imágenes asociadas a equipos, ubicaciones, fallas, etc.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from models.base import db, TimestampedModel


class Fotografia(db.Model, TimestampedModel):
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
