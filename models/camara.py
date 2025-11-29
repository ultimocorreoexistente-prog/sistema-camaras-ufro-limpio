#!/usr/bin/env python3
"""
Modelo de Cámara - Sistema de Gestión de Cámaras UFRO
Versión 2.0 - 29 nov 2025

Características:
- Modelo básico heredando de EquipmentBase
- Relaciones correctas con back_populates
- Campos esenciales para gestión de cámaras
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, Enum, Float, Text
from sqlalchemy.orm import relationship
from models.base import TimestampedModel, EstadoCamara, TipoUbicacion
from models import db
import enum


class EquipmentBase(db.Model, TimestampedModel):
    """Base para equipos con campos comunes"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6
    status = Column(String(50), default='activo', nullable=False)
    ubicacion_id = Column(Integer, ForeignKey('ubicaciones.id'), nullable=True)
    deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Camara(EquipmentBase):
    """
    Modelo de Cámara de Seguridad
    
    Campos esenciales:
    - id: ID único de la cámara
    - name: Nombre de la cámara
    - ip_address: Dirección IP de la cámara
    - status: Estado actual (activo, inactivo, mantenimiento, etc.)
    - ubicacion_id: ID de la ubicación donde está instalada
    """
    
    __tablename__ = 'camaras'
    
    # Campos adicionales específicos de cámara
    codigo_interno = Column(String(50), unique=True, nullable=False, comment="Código interno único")
    marca = Column(String(50), nullable=True, comment="Marca de la cámara")
    modelo = Column(String(50), nullable=True, comment="Modelo de la cámara")
    numero_serie = Column(String(100), nullable=True, comment="Número de serie")
    
    # Configuración técnica
    puerto = Column(Integer, nullable=True, comment="Puerto de conexión")
    protocolo = Column(String(20), default='HTTP', comment="Protocolo de comunicación")
    username_camara = Column(String(50), nullable=True, comment="Usuario de la cámara")
    password_camara = Column(String(100), nullable=True, comment="Contraseña de la cámara")
    
    # Configuración de video
    resolucion = Column(String(20), nullable=True, comment="Resolución (1080p, 720p, etc)")
    fps = Column(Integer, nullable=True, comment="Frames por segundo")
    codec = Column(String(20), nullable=True, comment="Codec de video")
    
    # Fechas importantes
    fecha_instalacion = Column(Date, nullable=True, comment="Fecha de instalación")
    fecha_garantia_hasta = Column(Date, nullable=True, comment="Fecha fin de garantía")
    
    # Mantenimiento
    ultimo_mantenimiento = Column(Date, nullable=True, comment="Último mantenimiento")
    proximo_mantenimiento = Column(Date, nullable=True, comment="Próximo mantenimiento")
    
    # Observaciones
    observaciones = Column(Text, nullable=True, comment="Observaciones generales")
    
    # Relaciones
    ubicacion_obj = relationship("Ubicacion", back_populates="camaras")
    
    # Relaciones con otros modelos
    eventos = relationship("EventoCamara", back_populates="camara_obj", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="camara_obj", cascade="all, delete-orphan")
    trazabilidades = relationship("TrazabilidadMantenimiento", back_populates="camara_obj", cascade="all, delete-orphan")
    
    # Relaciones con fallas (si existen)
    fallas = relationship("Falla", back_populates="camara", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Camara(id={self.id}, name='{self.name}', ip_address='{self.ip_address}', status='{self.status}')>"
    
    def get_nombre_completo(self):
        """Obtiene el nombre completo de la cámara."""
        return f"{self.codigo_interno} - {self.name}" if self.codigo_interno else self.name
    
    def is_active(self):
        """Verifica si la cámara está activa."""
        return self.status.lower() in ['activo', 'active', 'online']
    
    def needs_maintenance(self):
        """Verifica si la cámara necesita mantenimiento."""
        if not self.proximo_mantenimiento:
            return False
        return datetime.now().date() >= self.proximo_mantenimiento
    
    def get_uptime_days(self):
        """Calcula los días de funcionamiento desde la instalación."""
        if not self.fecha_instalacion:
            return 0
        return (datetime.now().date() - self.fecha_instalacion).days
    
    def to_dict(self):
        """Convierte el modelo a diccionario incluyendo relaciones."""
        result = super().to_dict()
        
        # Añadir datos calculados
        result['nombre_completo'] = self.get_nombre_completo()
        result['is_active'] = self.is_active()
        result['needs_maintenance'] = self.needs_maintenance()
        result['uptime_days'] = self.get_uptime_days()
        
        # Añadir relaciones (solo IDs para evitar recursión)
        result['ubicacion_id'] = self.ubicacion_id
        result['eventos_ids'] = [e.id for e in self.eventos]
        result['tickets_ids'] = [t.id for t in self.tickets]
        result['trazabilidades_ids'] = [t.id for t in self.trazabilidades]
        result['fallas_ids'] = [f.id for f in self.fallas]
        
        return result
    
    @classmethod
    def get_active_cameras(cls):
        """Obtiene todas las cámaras activas."""
        return cls.query.filter(
            cls.status.in_(['activo', 'active', 'online']),
            cls.deleted == False
        ).all()
    
    @classmethod
    def get_by_location(cls, location_id):
        """Obtiene cámaras por ubicación."""
        return cls.query.filter(
            cls.ubicacion_id == location_id,
            cls.deleted == False
        ).all()
    
    @classmethod
    def get_needing_maintenance(cls):
        """Obtiene cámaras que necesitan mantenimiento."""
        today = datetime.now().date()
        return cls.query.filter(
            cls.proximo_mantenimiento <= today,
            cls.deleted == False
        ).all()
    
    @classmethod
    def search(cls, query):
        """Busca cámaras por nombre, código interno o IP."""
        search_filter = (
            (cls.name.ilike(f'%{query}%')) |
            (cls.codigo_interno.ilike(f'%{query}%')) |
            (cls.ip_address.ilike(f'%{query}%'))
        )
        
        return cls.query.filter(search_filter, cls.deleted == False).all()