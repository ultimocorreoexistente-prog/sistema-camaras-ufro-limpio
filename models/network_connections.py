"""
Modelo SQLAlchemy para network_connections
Maneja las conexiones de red entre equipos del sistema
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float,
    Index, Enum as SQLEnum, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError

from models.base import db, TimestampedModel


class ConnectionType(Enum):
    """Tipos de conexiones de red soportadas"""
    ETHERNET = 'ethernet'
    FIBRA_OPTICA = 'fibra_optica'
    WIRELESS = 'wireless'
    SERIAL = 'serial'
    USB = 'usb'
    POWER_OVER_ETHERNET = 'poe'
    INALAMBRICO = 'inalambrico'
    UTP = 'utp'
    STP = 'stp'


class CableType(Enum):
    """Tipos de cable utilizados en las conexiones"""
    CAT5E = 'cat5e'
    CAT6 = 'cat6'
    CAT6A = 'cat6a'
    CAT7 = 'cat7'
    FIBRA_MONOMODO = 'fibra_monomodo'
    FIBRA_MULTIMODO = 'fibra_multimodo'
    COAXIAL = 'coaxial'
    USB__0 = 'usb__0'
    USB_3_0 = 'usb_3_0'
    RS3 = 'rs3'
    RS485 = 'rs485'


class NetworkConnection(db.Model, TimestampedModel):
    """
    Modelo para conexiones de red entre equipos
    Permite conectar cualquier tipo de equipo con cualquier otro
    """
    __tablename__ = 'network_connections'
    
    id = Column(Integer, primary_key=True) # Agregando id, asumiendo que BaseModel no lo define explícitamente

    # === CAMPOS PRINCIPALES ===
    tipo_conexion = Column(
        SQLEnum(ConnectionType),
        nullable=False,
        default=ConnectionType.ETHERNET
    )

    ancho_banda = Column(
        Float,
        nullable=True,
        comment="Ancho de banda en Mbps"
    )

    latencia = Column(
        Float,
        nullable=True,
        comment="Latencia en milisegundos (ms)"
    )

    # === IDENTIFICACIÓN DE EQUIPOS ===
    equipo_origen_id = Column(Integer, ForeignKey('equipos.id'), nullable=False)
    equipo_destino_id = Column(Integer, ForeignKey('equipos.id'), nullable=False)

    # Tipo de cada equipo para validación
    equipo_origen_tipo = Column(String(50), nullable=False)
    equipo_destino_tipo = Column(String(50), nullable=False)

    # === DETALLES DE CONEXIÓN ===
    tipo_cable = Column(SQLEnum(CableType), nullable=True)
    longitud_cable = Column(Float, nullable=True, comment="Longitud en metros")

    puerto_origen = Column(String(50), nullable=True)
    puerto_destino = Column(String(50), nullable=True)

    # === CONFIGURACIÓN DE RED ===
    vlan_id = Column(Integer, nullable=True)
    ip_address = Column(String(45), nullable=True)
    mac_address = Column(String(17), nullable=True)

    # === ESTADO Y MONITOREO ===
    activa = Column(Boolean, default=True, nullable=False)
    perdida_paquetes = Column(
        Float,
        default=0.0,
        nullable=False,
        comment="Pérdida de paquetes en porcentaje"
    )
    calidad_conexion = Column(
        String(20), # CORRECCIÓN: Cambiado de String(0) a String(20)
        default='buena',
        nullable=False,
        comment="Calidad de la conexión (excelente, buena, regular, mala)"
    )

    # === METADATA ===
    descripcion = Column(Text, nullable=True)
    notas_tecnicas = Column(Text, nullable=True)

    # === RELACIONES ===
    equipo_origen = relationship(
        "Equipo",
        foreign_keys=[equipo_origen_id],
        back_populates="conexiones_origen",
        lazy="joined"
    )

    equipo_destino = relationship(
        "Equipo",
        foreign_keys=[equipo_destino_id],
        back_populates="conexiones_destino",
        lazy="joined"
    )

    # === ÍNDICES PARA RENDIMIENTO ===
    __table_args__ = (
        # Índices para búsquedas frecuentes
        Index('idx_network_connections_equipo_origen', 'equipo_origen_id'),
        Index('idx_network_connections_equipo_destino', 'equipo_destino_id'),
        Index('idx_network_connections_tipo_conexion', 'tipo_conexion'),
        Index('idx_network_connections_activa', 'activa'),
        Index('idx_network_connections_vlan', 'vlan_id'),

        # Índice compuesto para búsquedas de topología
        Index('idx_network_connections_topologia',
              'equipo_origen_id', 'equipo_destino_id', 'activa'),

        # Índice para análisis de rendimiento
        Index('idx_network_connections_rendimiento',
              'tipo_conexion', 'ancho_banda', 'latencia'),

        # Restricciones de validación
        CheckConstraint('ancho_banda > 0', name='chk_ancho_banda_positivo'),
        CheckConstraint('latencia >= 0', name='chk_latencia_no_negativa'),
        CheckConstraint('perdida_paquetes >= 0 AND perdida_paquetes <= 100',
                        name='chk_perdida_paquetes_valida'),
        
        # CORRECCIÓN: Cambiado de '=' a '!=' para prevenir la autoconeción (self-connection)
        CheckConstraint('equipo_origen_id != equipo_destino_id',
                        name='chk_no_auto_conexion'), 

        # Restricción única para evitar conexiones duplicadas
        UniqueConstraint('equipo_origen_id', 'equipo_destino_id', 'tipo_conexion',
                         name='uq_conexion_unica')
    )

    def __repr__(self):
        return f"<NetworkConnection(origen={self.equipo_origen_tipo}:{self.equipo_origen_id}, " \
               f"destino={self.equipo_destino_tipo}:{self.equipo_destino_id}, " \
               f"tipo={self.tipo_conexion.value})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la conexión a diccionario"""
        # Se asume que super().to_dict() existe en BaseModel
        data = super().to_dict()
        data.update({
            'tipo_conexion': self.tipo_conexion.value if self.tipo_conexion else None,
            'tipo_cable': self.tipo_cable.value if self.tipo_cable else None,
            'equipo_origen': {
                'id': self.equipo_origen_id,
                'tipo': self.equipo_origen_tipo
            } if self.equipo_origen_id else None,
            'equipo_destino': {
                'id': self.equipo_destino_id,
                'tipo': self.equipo_destino_tipo
            } if self.equipo_destino_id else None
        })
        return data

    # === MÉTODOS DE VALIDACIÓN ===

    def validar_conexion(self) -> List[str]:
        """
        Valida la conexión y retorna lista de errores
        Retorna lista vacía si es válida
        """
        errores = []

        # Validar que los equipos existen (solo IDs por ahora)
        if not self.equipo_origen_id:
            errores.append("ID del equipo origen es requerido")
        if not self.equipo_destino_id:
            errores.append("ID del equipo destino es requerido")

        # Validar que no es la misma conexión
        if self.equipo_origen_id and self.equipo_destino_id:
            if self.equipo_origen_id == self.equipo_destino_id:
                errores.append("No se puede conectar un equipo consigo mismo")

        # Validar ancho de banda
        if self.ancho_banda is not None and self.ancho_banda <= 0:
            errores.append("El ancho de banda debe ser mayor a 0")

        # Validar latencia
        if self.latencia is not None and self.latencia < 0:
            errores.append("La latencia no puede ser negativa")

        # Validar pérdida de paquetes
        if self.perdida_paquetes is not None and (self.perdida_paquetes < 0 or self.perdida_paquetes > 100):
            errores.append("La pérdida de paquetes debe estar entre 0 y 100%")

        return errores

    def es_conexion_valida(self) -> bool:
        """Retorna True si la conexión es válida"""
        return len(self.validar_conexion()) == 0

    # === MÉTODOS DE CREACIÓN ===

    @classmethod
    def crear_conexion(cls,
                       equipo_origen_id: int,
                       equipo_destino_id: int,
                       tipo_conexion: ConnectionType,
                       equipo_origen_tipo: str,
                       equipo_destino_tipo: str,
                       **kwargs) -> 'NetworkConnection':
        """
        Crea una nueva conexión con validación
        """
        conexion = cls(
            equipo_origen_id=equipo_origen_id,
            equipo_destino_id=equipo_destino_id,
            tipo_conexion=tipo_conexion,
            equipo_origen_tipo=equipo_origen_tipo,
            equipo_destino_tipo=equipo_destino_tipo,
            **kwargs
        )

        # Validar antes de guardar
        errores = conexion.validar_conexion()
        if errores:
            raise ValueError(f"Errores de validación: {', '.join(errores)}")

        return conexion

    def guardar(self) -> bool:
        """
        Guarda la conexión en la base de datos
        Retorna True si fue exitosa
        """
        try:
            errores = self.validar_conexion()
            if errores:
                raise ValueError(f"Errores de validación: {', '.join(errores)}")

            db.session.add(self)
            db.session.commit()
            return True

        except IntegrityError as e:
            db.session.rollback()
            if "uq_conexion_unica" in str(e):
                raise ValueError("Ya existe una conexión entre estos equipos con el mismo tipo")
            raise ValueError(f"Error de integridad: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error al guardar la conexión: {str(e)}")

    # === MÉTODOS DE UTILIDAD ===

    def obtener_velocidad_conexion(self) -> str:
        """Retorna la velocidad de conexión en formato legible"""
        if not self.ancho_banda:
            return "No especificada"

        if self.ancho_banda >= 1000:
            return f"{self.ancho_banda/1000:.1f} Gbps"
        else:
            return f"{self.ancho_banda:.0f} Mbps"

    def obtener_calidad_conexion(self) -> str:
        """Retorna la calidad de la conexión basada en métricas"""
        if not self.activa:
            return "Inactiva"

        # Criterios basados en métricas
        if self.perdida_paquetes is not None and self.perdida_paquetes > 10:
            return "Mala"
        elif self.perdida_paquetes is not None and self.perdida_paquetes > 5:
            return "Regular"
        elif self.latencia is not None and self.latencia > 100:
            return "Regular"
        elif self.ancho_banda is not None and self.ancho_banda < 10:
            return "Regular"
        else:
            # Si pasa los filtros anteriores y los defaults, se considera buena
            return "Buena"

    def obtener_ruta_completa(self) -> List[str]:
        """Retorna la ruta completa de la conexión en texto"""
        origen = f"{self.equipo_origen_tipo}#{self.equipo_origen_id}"
        destino = f"{self.equipo_destino_tipo}#{self.equipo_destino_id}"
        return [origen, destino]

    @classmethod
    def obtener_conexiones_por_equipo(cls, equipo_id: int) -> List['NetworkConnection']:
        """Obtiene todas las conexiones de un equipo (como origen o destino)"""
        return cls.query.filter(
            db.or_(
                cls.equipo_origen_id == equipo_id,
                cls.equipo_destino_id == equipo_id
            ),
            cls.deleted == False
        ).all()

    @classmethod
    def obtener_topologia_red(cls) -> Dict[str, List[Dict]]:
        """
        Obtiene la topología completa de la red
        Retorna diccionario con equipos y sus conexiones
        """
        conexiones = cls.query.filter_by(activa=True, deleted=False).all()

        topologia = {}
        for conexion in conexiones:
            # Agregar equipo origen si no existe
            origen_id = str(conexion.equipo_origen_id)
            if origen_id not in topologia:
                topologia[origen_id] = {
                    'equipo_id': conexion.equipo_origen_id,
                    'equipo_tipo': conexion.equipo_origen_tipo,
                    'conexiones': []
                }

            # Agregar conexión al equipo origen
            topologia[origen_id]['conexiones'].append({
                'equipo_destino_id': conexion.equipo_destino_id,
                'equipo_destino_tipo': conexion.equipo_destino_tipo,
                'tipo_conexion': conexion.tipo_conexion.value,
                'ancho_banda': conexion.ancho_banda,
                'latencia': conexion.latencia
            })

        return topologia