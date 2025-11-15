# models/equipo.py
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db

class NetworkConnection(BaseModel, db.Model):
__tablename__ = 'network_connections'
source_equipment_id = Column(Integer, nullable=False)
source_equipment_type = Column(String(30), nullable=False)
target_equipment_id = Column(Integer, nullable=False)
target_equipment_type = Column(String(30), nullable=False)
connection_type = Column(String(0), nullable=False)
cable_type = Column(String(50), nullable=True)
cable_length = Column(Float, nullable=True)
port_source = Column(String(0), nullable=True)
port_target = Column(String(0), nullable=True)
is_active = Column(Boolean, default=True, nullable=False)
vlan_id = Column(Integer, nullable=True)
bandwidth_limit = Column(Integer, nullable=True)
latency_ms = Column(Float, nullable=True)
packet_loss = Column(Float, default=0.0, nullable=False)
notes = Column(Text, nullable=True)

class Switch(BaseModel, db.Model):
__tablename__ = 'switches'
name = Column(String(100), nullable=False)
ip_address = Column(String(45), nullable=True)
created_by = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
created_by_user = relationship("Usuario", foreign_keys=[created_by])

# CORREGIDO: relación con Ubicacion
ubicacion_id = Column(Integer, ForeignKey('ubicaciones.id'), nullable=True)
ubicacion = relationship("Ubicacion", back_populates="switches")

fotografias = relationship("Fotografia", back_populates="switch")

def __repr__(self):
return f"<Switch(name='{self.name}')>"

class UPS(BaseModel, db.Model):
__tablename__ = 'ups'
name = Column(String(100), nullable=False)
created_by = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
created_by_user = relationship("Usuario", foreign_keys=[created_by])
fotografias = relationship("Fotografia", back_populates="ups")

def __repr__(self):
return f"<UPS(name='{self.name}')>"

class NVR(BaseModel, db.Model):
__tablename__ = 'nvr_dvr' # nombre real
name = Column(String(100), nullable=False)
created_by = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
created_by_user = relationship("Usuario", foreign_keys=[created_by])
camaras = relationship("Camara", back_populates="nvr")
fotografias = relationship("Fotografia", back_populates="nvr")

def __repr__(self):
return f"<NVR(name='{self.name}')>"

class Gabinete(BaseModel, db.Model):
__tablename__ = 'gabinetes'
name = Column(String(100), nullable=False)
created_by = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
created_by_user = relationship("Usuario", foreign_keys=[created_by])
fotografias = relationship("Fotografia", back_populates="gabinete")

def __repr__(self):
return f"<Gabinete(name='{self.name}')>"

class FuentePoder(BaseModel, db.Model):
__tablename__ = 'fuente_poder' # singular, como en tu DB
name = Column(String(100), nullable=False)
created_by = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
created_by_user = relationship("Usuario", foreign_keys=[created_by])
fotografias = relationship("Fotografia", back_populates="fuente_poder")

def __repr__(self):
return f"<FuentePoder(name='{self.name}')>"