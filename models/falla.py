"""
Modelo para gestión de fallas del sistema
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import TimestampedModel
from models import db

class Falla(db.Model, TimestampedModel):
    __tablename__ = 'fallas'

    # Campos principales
    id = Column(Integer, primary_key=True)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=False)
    prioridad = Column(String(20), nullable=False, default='media')  # baja, media, alta, critica
    estado = Column(String(20), nullable=False, default='abierta')   # abierta, en_proceso, cerrada
    tipo = Column(String(50), nullable=False)  # camara, nvr, switch, ups, fuente, gabinete
    
    # Referencias a equipos
    equipo_id = Column(Integer, nullable=True)  # ID del equipo del tipo especificado
    equipo_type = Column(String(50), nullable=False, default='camara')  # Tipo del equipo
    
    # Relaciones de usuario
    creado_por_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    asignado_a_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    
    # Fechas
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=True)
    fecha_resolucion = Column(DateTime, nullable=True)
    
    # Campos adicionales
    activo = Column(Boolean, default=True, nullable=False)
    
    # Campos adicionales de la segunda versión
    parent_falla_id = Column(Integer, ForeignKey('fallas.id'), nullable=True)
    related_falla = relationship(
        "Falla",
        foreign_keys=[parent_falla_id],
        remote_side=lambda: [Falla.id],
        backref="related_fallas"
    )
    
    created_by_user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    created_by_user = relationship("Usuario", foreign_keys=[created_by_user_id], back_populates="created_fallas")
    
    camara_id = Column(Integer, ForeignKey('camaras.id'), nullable=True)
    camara = relationship("Camara", back_populates="fallas")
    
    fecha_reporte = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolucion = Column(Text, nullable=True)
    solucion_aplicada = Column(Text, nullable=True)
    requiere_mantenimiento = Column(Boolean, default=False)
    
    # Relaciones
    creado_por = relationship("Usuario", foreign_keys=[creado_por_id], back_populates="fallas_creadas")
    asignado_a = relationship("Usuario", foreign_keys=[asignado_a_id], back_populates="fallas_asignadas")
    comentarios = relationship("FallaComentario", back_populates="falla", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Falla {self.id}: {self.titulo}>'

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'prioridad': self.prioridad,
            'estado': self.estado,
            'tipo': self.tipo,
            'equipo_id': self.equipo_id,
            'equipo_type': self.equipo_type,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'fecha_resolucion': self.fecha_resolucion.isoformat() if self.fecha_resolucion else None,
            'activo': self.activo
        }