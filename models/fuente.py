"""
Modelo simple para Fuentes de Alimentación (Power Supplies).
Compatible con el sistema existente y templates.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from models.base import db, TimestampedModel
import enum


class EstadoFuente(enum.Enum):
    """Estados de fuentes de alimentación."""
    OPERATIVA = "operativa"
    MANTENIMIENTO = "mantenimiento"
    FALLA = "falla"
    FUERA_SERVICIO = "fuera_servicio"


class Fuente(db.Model, TimestampedModel):
    """
    Modelo simple de fuentes de alimentación.
    Compatible con el sistema existente y templates.
    """
    __tablename__ = 'fuentes'

    # Identificador
    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID único de la fuente")
    
    # Información básica
    nombre = Column(String(255), nullable=False, comment="Nombre de la fuente")
    descripcion = Column(Text, nullable=True, comment="Descripción de la fuente")
    
    # Información técnica básica
    marca = Column(String(100), nullable=True, comment="Marca de la fuente")
    modelo = Column(String(100), nullable=True, comment="Modelo de la fuente")
    numero_serie = Column(String(100), nullable=True, comment="Número de serie")
    
    # Ubicación
    ubicacion = Column(String(255), nullable=True, comment="Ubicación física")
    
    # Estado
    estado = Column(String(50), default=EstadoFuente.OPERATIVA.value, nullable=False, comment="Estado de la fuente")
    
    # Especificaciones técnicas
    potencia = Column(Integer, nullable=True, comment="Potencia en watts")
    voltaje_entrada = Column(String(50), nullable=True, comment="Voltaje de entrada")
    voltaje_salida = Column(String(50), nullable=True, comment="Voltaje de salida")
    amperaje_salida = Column(Float, nullable=True, comment="Amperaje de salida")
    eficiencia = Column(Integer, nullable=True, comment="Eficiencia en porcentaje")
    
    # Temperatura y monitoreo
    temperatura_actual = Column(Float, nullable=True, comment="Temperatura actual en °C")
    carga_actual = Column(Integer, default=0, nullable=False, comment="Carga actual en watts")
    voltaje_salida_actual = Column(String(50), nullable=True, comment="Voltaje de salida actual")
    
    # Fechas importantes
    fecha_instalacion = Column(DateTime, nullable=True, comment="Fecha de instalación")
    fecha_ultimo_mantenimiento = Column(DateTime, nullable=True, comment="Fecha del último mantenimiento")
    fecha_proximo_mantenimiento = Column(DateTime, nullable=True, comment="Fecha del próximo mantenimiento")
    
    # Control de equipos
    activo = Column(Boolean, default=True, nullable=False, comment="Si está activo")
    
    # Relaciones (comentadas hasta implementar Usuario.back_populates)
    # created_by_user = relationship("Usuario", back_populates="created_equipos")
    
    # Relaciones con otros modelos
    # Relaciones temporalmente comentadas para evitar errores
    # mantenimientos = relationship("Mantenimiento", back_populates="fuente_poder", cascade="all, delete-orphan")
    # fotografias = relationship("Fotografia", back_populates="fuente_poder", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Fuente(nombre='{self.nombre}', potencia='{self.potencia}W', estado='{self.estado}')>"

    def get_consumption_percentage(self):
        """
        Calcula el porcentaje de consumo basado en la potencia máxima y carga actual.
        
        Returns:
            float: Porcentaje de consumo (0-100)
        """
        if not self.potencia or self.potencia == 0:
            return 0
        
        percentage = (self.carga_actual / self.potencia) * 100
        return min(100, max(0, percentage))

    def get_status_color(self):
        """
        Obtiene el color para el estado de la fuente.
        
        Returns:
            str: Código de color hex
        """
        colors = {
            EstadoFuente.OPERATIVA.value: "#28a745",      # Verde
            EstadoFuente.MANTENIMIENTO.value: "#ffc107",  # Amarillo
            EstadoFuente.FALLA.value: "#dc3545",          # Rojo
            EstadoFuente.FUERA_SERVICIO.value: "#6c757d"  # Gris
        }
        return colors.get(self.estado, "#6c757d")

    def is_maintenance_due(self):
        """
        Verifica si el mantenimiento está vencido.
        
        Returns:
            bool: True si el mantenimiento está vencido
        """
        if not self.fecha_proximo_mantenimiento:
            return False
        
        return datetime.utcnow() >= self.fecha_proximo_mantenimiento

    def update_monitoring_data(self, temperatura=None, carga=None, voltaje_salida=None):
        """
        Actualiza los datos de monitoreo de la fuente.
        
        Args:
            temperatura (float): Temperatura actual
            carga (int): Carga actual en watts
            voltaje_salida (str): Voltaje de salida actual
        """
        if temperatura is not None:
            self.temperatura_actual = temperatura
        
        if carga is not None:
            self.carga_actual = carga
        
        if voltaje_salida is not None:
            self.voltaje_salida_actual = voltaje_salida
        
        # Actualizar estado basado en condiciones
        self.update_status_based_on_conditions()
        
        self.fecha_actualizacion = datetime.utcnow()

    def update_status_based_on_conditions(self):
        """
        Actualiza el estado basado en las condiciones actuales.
        """
        # Si la temperatura es muy alta
        if self.temperatura_actual and self.temperatura_actual > 70:
            self.estado = EstadoFuente.FALLA.value
        # Si la carga es muy alta
        elif self.get_consumption_percentage() > 90:
            self.estado = EstadoFuente.FALLA.value
        # Si la carga está moderada
        elif self.get_consumption_percentage() > 75:
            self.estado = EstadoFuente.MANTENIMIENTO.value
        else:
            self.estado = EstadoFuente.OPERATIVA.value

    def schedule_maintenance(self, days_ahead=180):
        """
        Programa el próximo mantenimiento.
        
        Args:
            days_ahead (int): Días adelante para programar el mantenimiento
        """
        from datetime import timedelta
        self.fecha_proximo_mantenimiento = datetime.utcnow() + timedelta(days=days_ahead)
        self.fecha_actualizacion = datetime.utcnow()

    def get_health_summary(self):
        """
        Obtiene un resumen de la salud de la fuente.
        
        Returns:
            dict: Resumen de salud
        """
        return {
            'estado': self.estado,
            'temperatura_actual': self.temperatura_actual,
            'consumo_porcentaje': self.get_consumption_percentage(),
            'mantenimiento_vencido': self.is_maintenance_due(),
            'dias_proximo_mantenimiento': (
                (self.fecha_proximo_mantenimiento - datetime.utcnow()).days 
                if self.fecha_proximo_mantenimiento else None
            )
        }

    @classmethod
    def get_by_capacity_range(cls, min_watts, max_watts):
        """
        Obtiene fuentes por rango de capacidad.
        
        Args:
            min_watts (int): Potencia mínima
            max_watts (int): Potencia máxima
            
        Returns:
            list: Lista de fuentes que cumplen el criterio
        """
        return cls.query.filter(
            cls.potencia >= min_watts,
            cls.potencia <= max_watts,
            cls.deleted == False
        ).all()

    @classmethod
    def get_by_brand(cls, brand):
        """
        Obtiene fuentes por marca.
        
        Args:
            brand (str): Marca de las fuentes
            
        Returns:
            list: Lista de fuentes de la marca
        """
        return cls.query.filter(
            cls.marca.ilike(f'%{brand}%'),
            cls.deleted == False
        ).all()

    @classmethod
    def get_active_fuentes(cls):
        """
        Obtiene todas las fuentes activas.
        
        Returns:
            list: Lista de fuentes activas
        """
        return cls.query.filter_by(activo=True, deleted=False).all()

    @classmethod
    def get_fuentes_by_status(cls, status):
        """
        Obtiene fuentes por estado.
        
        Args:
            status (str): Estado a filtrar
            
        Returns:
            list: Lista de fuentes con el estado especificado
        """
        return cls.query.filter_by(estado=status, activo=True, deleted=False).all()