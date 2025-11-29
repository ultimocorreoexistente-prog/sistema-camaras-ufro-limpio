"""
Modelo para comentarios de fallas
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import db, TimestampedModel

class FallaComentario(db.Model, TimestampedModel):
    __tablename__ = 'falla_comentarios'

    falla_id = Column(Integer, ForeignKey('fallas.id'), nullable=False)
    comentario = Column(Text, nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)

    # Relaciones
    falla = relationship("Falla", back_populates="comentarios")
    usuario = relationship("Usuario", back_populates="falla_comentarios")

    def __repr__(self):
        return f'<FallaComentario {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'falla_id': self.falla_id,
            'comentario': self.comentario,
            'usuario_id': self.usuario_id,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'activo': self.activo
        }