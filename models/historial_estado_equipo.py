# models/historial_estado_equipo.py
"""
Modelo para el historial de cambios de estado de equipos.
Registra todos los cambios de estado que ocurren en el sistema.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, 
    LargeBinary, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum as PyEnum

from models.base import db, TimestampedModel
from models.enums.equipment_status import EquipmentStatus

class HistorialEstadoEquipo(db.Model, TimestampedModel):
    """
    Modelo para registrar el historial de cambios de estado de equipos.
    
    Este modelo mantiene un registro completo de todos los cambios de estado
    que ocurren en los equipos del sistema, permitiendo auditoría y seguimiento.
    """
    __tablename__ = 'historial_estado_equipo'
    
    # === CAMPOS PRINCIPALES ===
    equipo_tipo = Column(
        String(50), 
        nullable=False, 
        index=True,
        comment="Tipo de equipo (camara, switch, nvr, ups, gabinete, fuente_poder)"
    )
    
    equipo_id = Column(
        Integer, 
        nullable=False, 
        index=True,
        comment="ID del equipo que cambió de estado"
    )
    
    estado_anterior = Column(
        String(30), 
        nullable=True,
        comment="Estado anterior del equipo"
    )
    
    estado_nuevo = Column(
        String(30), 
        nullable=False,
        comment="Nuevo estado del equipo"
    )
    
    fecha_cambio = Column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow,
        index=True,
        comment="Fecha y hora del cambio de estado"
    )
    
    motivo = Column(
        Text, 
        nullable=True,
        comment="Motivo o descripción del cambio de estado"
    )
    
    usuario_id = Column(
        Integer, 
        ForeignKey('usuarios.id'), 
        nullable=True,
        index=True,
        comment="ID del usuario que realizó el cambio"
    )
    
    # === CAMPOS ADICIONALES PARA AUDITORÍA ===
    metadata_adicional = Column(
        JSON, 
        nullable=True,
        comment="Información adicional en formato JSON (IP, ubicación, etc.)"
    )
    
    # === RELACIONES ===
    usuario = relationship(
        "Usuario", 
        back_populates="historial_cambios_estado",
        foreign_keys=[usuario_id]
    )
    
    # === MÉTODOS DE CLASE PARA REGISTRAR CAMBIOS ===
    
    @classmethod
    def registrar_cambio_estado(
        cls, 
        equipo_tipo, 
        equipo_id, 
        estado_nuevo, 
        usuario_id=None, 
        motivo=None,
        metadata=None,
        estado_anterior=None,
        fecha_cambio=None
    ):
        """
        Método de clase para registrar un cambio de estado de equipo.
        
        Args:
            equipo_tipo (str): Tipo de equipo
            equipo_id (int): ID del equipo
            estado_nuevo (str): Nuevo estado del equipo
            usuario_id (int, optional): ID del usuario que realizó el cambio
            motivo (str, optional): Motivo del cambio
            metadata (dict, optional): Metadata adicional
            estado_anterior (str, optional): Estado anterior (si no se proporciona, se obtendrá del equipo)
            fecha_cambio (datetime, optional): Fecha del cambio (default: ahora)
        
        Returns:
            HistorialEstadoEquipo: Instancia creada del historial
        
        Raises:
            ValueError: Si los parámetros requeridos son inválidos
        """
        if not equipo_tipo or not equipo_id or not estado_nuevo:
            raise ValueError("equipo_tipo, equipo_id y estado_nuevo son requeridos")
        
        if fecha_cambio is None:
            fecha_cambio = datetime.utcnow()
        
        # Crear instancia del historial
        historial = cls(
            equipo_tipo=equipo_tipo,
            equipo_id=equipo_id,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            fecha_cambio=fecha_cambio,
            motivo=motivo,
            usuario_id=usuario_id,
            metadata_adicional=metadata
        )
        
        # Guardar en la base de datos
        db.session.add(historial)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        
        return historial
    
    @classmethod
    def obtener_historial_equipo(cls, equipo_tipo, equipo_id, limite=50):
        """
        Obtiene el historial de cambios para un equipo específico.
        
        Args:
            equipo_tipo (str): Tipo de equipo
            equipo_id (int): ID del equipo
            limite (int): Límite de registros a retornar
        
        Returns:
            list: Lista de instancias de HistorialEstadoEquipo
        """
        return cls.query.filter_by(
            equipo_tipo=equipo_tipo,
            equipo_id=equipo_id,
            deleted=False
        ).order_by(cls.fecha_cambio.desc()).limit(limite).all()
    
    @classmethod
    def obtener_historial_por_usuario(cls, usuario_id, limite=100):
        """
        Obtiene el historial de cambios realizados por un usuario específico.
        
        Args:
            usuario_id (int): ID del usuario
            limite (int): Límite de registros a retornar
        
        Returns:
            list: Lista de instancias de HistorialEstadoEquipo
        """
        return cls.query.filter_by(
            usuario_id=usuario_id,
            deleted=False
        ).order_by(cls.fecha_cambio.desc()).limit(limite).all()
    
    @classmethod
    def obtener_historial_por_estado(cls, estado, limite=100):
        """
        Obtiene el historial de cambios que resultaron en un estado específico.
        
        Args:
            estado (str): Estado a filtrar
            limite (int): Límite de registros a retornar
        
        Returns:
            list: Lista de instancias de HistorialEstadoEquipo
        """
        return cls.query.filter_by(
            estado_nuevo=estado,
            deleted=False
        ).order_by(cls.fecha_cambio.desc()).limit(limite).all()
    
    @classmethod
    def obtener_estadisticas_cambios(cls, fecha_inicio, fecha_fin):
        """
        Obtiene estadísticas de cambios de estado en un rango de fechas.
        
        Args:
            fecha_inicio (datetime): Fecha de inicio
            fecha_fin (datetime): Fecha de fin
        
        Returns:
            dict: Diccionario con estadísticas
        """
        from sqlalchemy import func
        
        # Contar cambios por tipo de equipo
        cambios_por_tipo = db.session.query(
            cls.equipo_tipo,
            func.count(cls.id).label('total_cambios')
        ).filter(
            cls.fecha_cambio >= fecha_inicio,
            cls.fecha_cambio <= fecha_fin,
            cls.deleted == False
        ).group_by(cls.equipo_tipo).all()
        
        # Contar cambios por estado
        cambios_por_estado = db.session.query(
            cls.estado_nuevo,
            func.count(cls.id).label('total_cambios')
        ).filter(
            cls.fecha_cambio >= fecha_inicio,
            cls.fecha_cambio <= fecha_fin,
            cls.deleted == False
        ).group_by(cls.estado_nuevo).all()
        
        # Total de cambios
        total_cambios = cls.query.filter(
            cls.fecha_cambio >= fecha_inicio,
            cls.fecha_cambio <= fecha_fin,
            cls.deleted == False
        ).count()
        
        return {
            'total_cambios': total_cambios,
            'cambios_por_tipo': {item.equipo_tipo: item.total_cambios for item in cambios_por_tipo},
            'cambios_por_estado': {item.estado_nuevo: item.total_cambios for item in cambios_por_estado}
        }
    
    # === PROPIEDADES Y MÉTODOS DE INSTANCIA ===
    
    def es_cambio_critico(self):
        """
        Determina si el cambio de estado es crítico.
        
        Returns:
            bool: True si es un cambio crítico
        """
        estados_criticos = [
            EquipmentStatus.FALLANDO,
            EquipmentStatus.DADO_BAJA
        ]
        return self.estado_nuevo in estados_criticos
    
    def get_tiempo_transcurrido(self):
        """
        Obtiene el tiempo transcurrido desde el cambio.
        
        Returns:
            timedelta: Tiempo transcurrido
        """
        return datetime.utcnow() - self.fecha_cambio
    
    def get_descripcion_cambio(self):
        """
        Obtiene una descripción legible del cambio de estado.
        
        Returns:
            str: Descripción del cambio
        """
        if self.estado_anterior:
            return f"Cambio de {self.estado_anterior} a {self.estado_nuevo}"
        else:
            return f"Estado inicial: {self.estado_nuevo}"
    
    def __repr__(self):
        return (
            f"<HistorialEstadoEquipo("
            f"equipo_tipo='{self.equipo_tipo}', "
            f"equipo_id={self.equipo_id}, "
            f"estado_nuevo='{self.estado_nuevo}', "
            f"fecha_cambio='{self.fecha_cambio}'"
            f")>"
        )

# === MAPEO DE TIPOS POSTGRESQL → SQLALCHEMY ===
# 
# PostgreSQL Type     → SQLAlchemy Type
# -----------------------------------------
# VARCHAR(n)          → String(n)
# TEXT                → Text
# INTEGER             → Integer
# BIGINT              → BigInteger
# BOOLEAN             → Boolean
# DATE                → Date
# TIME                → Time
# DATETIME/TIMESTAMP  → DateTime
# UUID                → UUID (from sqlalchemy.dialects.postgresql)
# JSON                → JSON
# JSONB               → JSON
# BYTEA               → LargeBinary
# ENUM                → SQLEnum or String
# FLOAT/DOUBLE        → Float
# DECIMAL/NUMERIC     → Numeric
# ARRAY               → ARRAY (from sqlalchemy.dialects.postgresql)
#
# Para este modelo se utilizan principalmente:
# - String(50): Para equipo_tipo (tipos de equipos)
# - String(30): Para estados (EquipmentStatus values)
# - Text: Para motivo (descripciones variables)
# - DateTime: Para fecha_cambio (timestamps)
# - JSON: Para metadata_adicional (información flexible)
# - Integer: Para IDs numéricos
# - Boolean: Para flags y estados binarios