from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db

class Falla(BaseModel, db.Model):
__tablename__ = 'fallas'

equipo_id = Column(Integer, nullable=False)
equipo_type = Column(String(50), nullable=False)
descripcion = Column(Text, nullable=False)
severidad = Column(String(0), nullable=False, default='media')
estado = Column(String(0), nullable=False, default='reportada')

parent_falla_id = Column(Integer, ForeignKey('fallas.id'), nullable=True)
related_falla = relationship(
"Falla",
foreign_keys=[parent_falla_id],
remote_side=lambda: [Falla.id], # CORREGIDO
backref="related_fallas"
)

created_by_user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
created_by_user = relationship("Usuario", back_populates="created_fallas")

camara_id = Column(Integer, ForeignKey('camaras.id'), nullable=True)
camara = relationship("Camara", back_populates="fallas")

fecha_reporte = Column(DateTime, default=datetime.utcnow, nullable=False)
fecha_resolucion = Column(DateTime, nullable=True)
resolucion = Column(Text, nullable=True)
solucion_aplicada = Column(Text, nullable=True)
requiere_mantenimiento = Column(Boolean, default=False)