"""
Modelo de ubicaciones para el sistema de geolocalización.

Incluye gestión de ubicaciones con coordenadas GPS, direcciones y jerarquías.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db


class Ubicacion(BaseModel, db.Model):
    """
    Modelo de ubicaciones geográficas.
    
    Attributes:
        name (str): Nombre de la ubicación
        description (str): Descripción detallada
        address (str): Dirección física
        latitude (float): Latitud GPS
        longitude (float): Longitud GPS
        altitude (float): Altitud en metros
        location_type (str): Tipo de ubicación
        parent_id (int): ID de la ubicación padre (jerárquico)
        building (str): Edificio o estructura
        floor (str): Piso o nivel
        room (str): Sala o habitación
        area (str): Área específica
        zone (str): Zona o sector
        campus (str): Campus (para instituciones educativas)
    """
    
    __tablename__ = 'ubicaciones'
    
    # Información básica
    name = Column(String(100), nullable=False, index=True,
                 comment="Nombre de la ubicación")
    description = Column(Text, nullable=True,
                        comment="Descripción detallada de la ubicación")
    address = Column(String(200), nullable=True,
                    comment="Dirección física completa")
    
    # Coordenadas GPS
    latitude = Column(Float, nullable=True,
                     comment="Latitud en grados decimales")
    longitude = Column(Float, nullable=True,
                      comment="Longitud en grados decimales")
    altitude = Column(Float, nullable=True,
                     comment="Altitud en metros sobre el nivel del mar")
    
    # Tipo y jerarquía
    location_type = Column(String(30), nullable=False,
                          comment="Tipo de ubicación (campus, edificio, sala, etc.)")
    parent_id = Column(Integer, ForeignKey('ubicaciones.id'), nullable=True,
                      comment="ID de la ubicación padre (jerárquico)")
    
    # Información específica del lugar
    building = Column(String(50), nullable=True,
                     comment="Edificio o estructura")
    floor = Column(String(20), nullable=True,
                  comment="Piso o nivel")
    room = Column(String(50), nullable=True,
                 comment="Sala o habitación específica")
    area = Column(String(50), nullable=True,
                 comment="Área específica")
    zone = Column(String(50), nullable=True,
                 comment="Zona o sector")
    campus = Column(String(50), nullable=True,
                   comment="Campus (para instituciones educativas)")
    
    # Metadatos
    is_public = Column(Boolean, default=True, nullable=False,
                      comment="Si la ubicación es pública")
    access_restricted = Column(Boolean, default=False, nullable=False,
                              comment="Si requiere permisos especiales")
    notes = Column(Text, nullable=True,
                  comment="Notas adicionales")
    
    # Relaciones
    parent = relationship("Ubicacion", remote_side=[id], backref="children")
    
    # Relaciones con otros modelos
    created_by_user = relationship("Usuario", back_populates="created_ubicaciones")
    camaras = relationship("Camara", back_populates="ubicacion")
    equipos = relationship("Equipo", back_populates="ubicacion")
    nvr_dvrs = relationship("NVR", back_populates="ubicacion")
    switches = relationship("Switch", back_populates="ubicacion")
    ups_devices = relationship("UPS", back_populates="ubicacion")
    fuentes_poder = relationship("FuentePoder", back_populates="ubicacion")
    gabinetes = relationship("Gabinete", back_populates="ubicacion")
    fallas = relationship("Falla", back_populates="ubicacion")
    mantenimientos = relationship("Mantenimiento", back_populates="ubicacion")
    
    def __repr__(self):
        return f"<Ubicacion(name='{self.name}', type='{self.location_type}')>"
    
    def get_full_path(self):
        """
        Obtiene la ruta completa de la ubicación (jerarquía).
        
        Returns:
            str: Ruta completa de la ubicación
        """
        if not self.parent:
            return self.name
        
        path_parts = []
        current = self
        
        # Construir la ruta desde la raíz hasta la ubicación actual
        while current:
            path_parts.append(current.name)
            current = current.parent
        
        return " > ".join(reversed(path_parts))
    
    def get_coordinates(self):
        """
        Obtiene las coordenadas como tupla.
        
        Returns:
            tuple: (latitude, longitude) o None si no hay coordenadas
        """
        if self.latitude is not None and self.longitude is not None:
            return (self.latitude, self.longitude)
        return None
    
    def calculate_distance_to(self, other_location):
        """
        Calcula la distancia a otra ubicación usando la fórmula de Haversine.
        
        Args:
            other_location (Ubicacion): Otra ubicación
            
        Returns:
            float: Distancia en kilómetros
        """
        import math
        
        lat1, lon1 = self.latitude, self.longitude
        lat2, lon2 = other_location.latitude, other_location.longitude
        
        if None in [lat1, lon1, lat2, lon2]:
            return None
        
        # Convertir a radianes
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Fórmula de Haversine
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radio de la Tierra en kilómetros
        r = 6371
        
        return c * r
    
    def is_within_radius(self, center_location, radius_km):
        """
        Verifica si la ubicación está dentro de un radio específico.
        
        Args:
            center_location (Ubicacion): Ubicación del centro
            radius_km (float): Radio en kilómetros
            
        Returns:
            bool: True si está dentro del radio
        """
        distance = self.calculate_distance_to(center_location)
        if distance is None:
            return False
        return distance <= radius_km
    
    def get_equipment_count(self):
        """
        Obtiene el número total de equipos en esta ubicación.
        
        Returns:
            int: Número de equipos
        """
        return len(self.equipos) + len(self.camaras) + len(self.nvr_dvrs) + \
               len(self.switches) + len(self.ups_devices) + len(self.fuentes_poder) + \
               len(self.gabinetes)
    
    def get_active_equipment_count(self):
        """
        Obtiene el número de equipos activos en esta ubicación.
        
        Returns:
            int: Número de equipos activos
        """
        from models import EquipmentStatus
        
        count = 0
        
        # Contar cámaras activas
        for camara in self.camaras:
            if camara.status == EquipmentStatus.ACTIVO:
                count += 1
        
        # Contar otros equipos activos
        for equipo in self.equipos:
            if equipo.status == EquipmentStatus.ACTIVO:
                count += 1
        
        # Contar NVRs/DVRs activos
        for nvr in self.nvr_dvrs:
            if nvr.status == EquipmentStatus.ACTIVO:
                count += 1
        
        # Contar switches activos
        for switch in self.switches:
            if switch.status == EquipmentStatus.ACTIVO:
                count += 1
        
        # Contar UPSs activos
        for ups in self.ups_devices:
            if ups.status == EquipmentStatus.ACTIVO:
                count += 1
        
        return count
    
    @classmethod
    def get_by_coordinates(cls, latitude, longitude, tolerance_km=0.1):
        """
        Busca ubicaciones cerca de las coordenadas especificadas.
        
        Args:
            latitude (float): Latitud
            longitude (float): Longitud
            tolerance_km (float): Tolerancia en kilómetros
            
        Returns:
            list: Lista de ubicaciones cercanas
        """
        # Esta implementación es simplificada
        # En producción se debería usar PostGIS para búsquedas geoespaciales
        locations = cls.query.all()
        nearby_locations = []
        
        for location in locations:
            if location.latitude and location.longitude:
                # Calcular distancia aproximada
                import math
                lat1, lon1 = math.radians(latitude), math.radians(longitude)
                lat2, lon2 = math.radians(location.latitude), math.radians(location.longitude)
                
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
                c = 2 * math.asin(math.sqrt(a))
                distance_km = 6371 * c
                
                if distance_km <= tolerance_km:
                    nearby_locations.append(location)
        
        return nearby_locations
    
    @classmethod
    def get_by_type(cls, location_type):
        """
        Obtiene ubicaciones de un tipo específico.
        
        Args:
            location_type (str): Tipo de ubicación
            
        Returns:
            list: Lista de ubicaciones del tipo especificado
        """
        return cls.query.filter_by(location_type=location_type, deleted=False).all()
    
    @classmethod
    def get_tree(cls):
        """
        Obtiene el árbol jerárquico completo de ubicaciones.
        
        Returns:
            list: Lista de ubicaciones raíz con sus hijos
        """
        return cls.query.filter_by(parent_id=None, deleted=False).all()


class UbicacionLog(BaseModel, db.Model):
    """
    Log de cambios en ubicaciones.
    
    Attributes:
        ubicacion_id (int): ID de la ubicación
        action (str): Acción realizada
        changes (str): Cambios realizados en formato JSON
        ip_address (str): Dirección IP del usuario
    """
    
    __tablename__ = 'ubicacion_logs'
    
    ubicacion_id = Column(Integer, ForeignKey('ubicaciones.id'), nullable=False,
                         comment="ID de la ubicación")
    action = Column(String(50), nullable=False,
                   comment="Acción realizada")
    changes = Column(Text, nullable=True,
                    comment="Cambios realizados en formato JSON")
    ip_address = Column(String(45), nullable=True,
                       comment="Dirección IP del usuario")
    
    # Relaciones
    # ubicacion = relationship("Ubicacion", backref="logs")
    
    def __repr__(self):
        return f"<UbicacionLog(ubicacion_id={self.ubicacion_id}, action='{self.action}')>"