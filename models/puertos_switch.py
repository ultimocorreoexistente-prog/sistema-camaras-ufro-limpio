"""
Modelo de puertos de switches de red.

Representa los puertos individuales de cada switch con su configuración
y estado específico.
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db
import re


class PuertoSwitch(BaseModel, db.Model):
    """
    Modelo de puertos de switches de red.

    Attributes:
    switch_id (int): ID del switch al que pertenece el puerto
    numero_puerto (int): Número del puerto (1-48 típicamente)
    nombre_puerto (str): Nombre descriptivo del puerto
    tipo_puerto (str): Tipo de puerto (Ethernet, SFP, SFP+, etc.)
    velocidad_puerto (str): Velocidad del puerto (10Mbps, 100Mbps, 1Gbps, 10Gbps)
    estado_puerto (str): Estado del puerto (Activo, Inactivo, Fallo, Mantenimiento)
    vlan_asignada (int): VLAN asignada al puerto
    descripcion (str): Descripción del puerto
    conecta_a (str): Qué dispositivo/conexión está conectada
    poe_habilitado (bool): Si tiene PoE habilitado
    potencia_maxima_poe (float): Potencia máxima PoE en Watts
    duplex (str): Modo de duplex (Half, Full, Auto)
    mac_address (str): Dirección MAC si aplica
    fecha_ultimo_mantenimiento (date): Fecha de último mantenimiento
    ultima_conexion (datetime): Última vez que se detectó conexión
    observaciones (str): Observaciones adicionales
    """

    __tablename__ = 'puertos_switch'

    # ✅ Corrección crítica: primary key obligatoria en SQLAlchemy 2.x
    id = Column(Integer, primary_key=True)

    # Foreign Key al switch
    switch_id = Column(Integer, ForeignKey('switches.id'), nullable=False,
                       comment="ID del switch al que pertenece el puerto")

    # Configuración del puerto
    numero_puerto = Column(Integer, nullable=False,
                           comment="Número del puerto en el switch")
    nombre_puerto = Column(String(100), nullable=True,
                           comment="Nombre descriptivo del puerto")
    tipo_puerto = Column(String(50), nullable=True,
                         comment="Tipo de puerto (Ethernet, SFP, SFP+)")
    velocidad_puerto = Column(String(20), nullable=True,  # ✅ Corregido String(0) → String(20)
                              comment="Velocidad del puerto")
    estado_puerto = Column(String(50), nullable=True,
                           comment="Estado del puerto")
    vlan_asignada = Column(Integer, nullable=True,
                           comment="VLAN asignada al puerto")

    # Información de conectividad
    descripcion = Column(Text, nullable=True,
                         comment="Descripción del puerto")
    conecta_a = Column(String(200), nullable=True,  # ✅ Corregido String(00) → String(200)
                       comment="Dispositivo/conexión al que está conectado")

    # Configuración PoE
    poe_habilitado = Column(Boolean, default=False,
                            comment="Si tiene PoE habilitado")
    potencia_maxima_poe = Column(Float, nullable=True,
                                 comment="Potencia máxima PoE en Watts")

    # Configuración de red
    duplex = Column(String(20), nullable=True,  # ✅ Corregido String(0) → String(20)
                    comment="Modo de duplex")
    mac_address = Column(String(17), nullable=True,
                         comment="Dirección MAC del puerto")

    # Fechas y registros
    fecha_ultimo_mantenimiento = Column(Date, nullable=True,
                                        comment="Fecha de último mantenimiento")
    ultima_conexion = Column(DateTime, nullable=True,
                             comment="Última vez que se detectó conexión")

    # Información adicional
    observaciones = Column(Text, nullable=True,
                           comment="Observaciones adicionales")

    # Relaciones bidireccionales
    switch = relationship("Switch", back_populates="puertos")

    def __repr__(self):
        return f"<PuertoSwitch(switch_id={self.switch_id}, numero_puerto={self.numero_puerto}, tipo_puerto='{self.tipo_puerto}')>"

    def get_puerto_completo(self):
        """
        Obtiene una representación completa del puerto.

        Returns:
            str: String con información completa del puerto
        """
        switch_info = self.switch.codigo if self.switch else "Unknown"
        return f"Switch {switch_info} - Puerto {self.numero_puerto} ({self.tipo_puerto})"

    def is_activo(self):
        """
        Verifica si el puerto está activo.

        Returns:
            bool: True si el puerto está activo
        """
        return self.estado_puerto and self.estado_puerto.lower() in ['activo', 'up', 'conectado']

    def is_poe_disponible(self):
        """
        Verifica si el puerto tiene PoE disponible.

        Returns:
            bool: True si PoE está disponible
        """
        return self.poe_habilitado and self.potencia_maxima_poe and self.potencia_maxima_poe > 0

    def validate_numero_puerto(self):
        """
        Valida que el número de puerto esté en rango válido.

        Returns:
            bool: True si es válido
        """
        if not self.numero_puerto:
            return False
        # Validar que el puerto esté entre 1 y 5 (ajusta según necesidad)
        return 1 <= self.numero_puerto <= 50

    def validate_mac_address(self):
        """
        Valida el formato de la dirección MAC.

        Returns:
            bool: True si es válida
        """
        if not self.mac_address:
            return True
        # Formato MAC: XX:XX:XX:XX:XX:XX
        mac_pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        return bool(re.match(mac_pattern, self.mac_address))

    def validate_vlan(self):
        """
        Valida que la VLAN esté en rango válido.

        Returns:
            bool: True si es válida
        """
        if not self.vlan_asignada:
            return True
        # VLANs válidas van de 1 a 4094
        return 1 <= self.vlan_asignada <= 4094

    def get_estado_visual(self):
        """
        Obtiene el estado visual del puerto para la interfaz.

        Returns:
            str: Estado con icono/color correspondiente
        """
        if not self.estado_puerto:
            return "Sin estado"
        estado_lower = self.estado_puerto.lower()
        if estado_lower in ['activo', 'up', 'conectado']:
            return f"✅ {self.estado_puerto}"
        elif estado_lower in ['inactivo', 'down', 'desconectado']:
            return f"⚠️ {self.estado_puerto}"
        elif estado_lower in ['fallo', 'error', 'fault']:
            return f"❌ {self.estado_puerto}"
        elif estado_lower in ['mantenimiento', 'maintenance']:
            return f"🔧 {self.estado_puerto}"
        else:
            return f"⚪ {self.estado_puerto}"

    def save(self, user_id=None):
        """
        Guarda el puerto con validaciones adicionales.

        Args:
            user_id (int): ID del usuario que realiza la operación

        Returns:
            self: El objeto guardado
        """
        if not self.validate_numero_puerto():
            raise ValueError(f"Número de puerto inválido: {self.numero_puerto}")
        if not self.validate_mac_address():
            raise ValueError(f"Dirección MAC inválida: {self.mac_address}")
        if not self.validate_vlan():
            raise ValueError(f"VLAN inválida: {self.vlan_asignada}")
        return super().save(user_id)

    def update_ultima_conexion(self):
        """Actualiza la timestamp de última conexión."""
        self.ultima_conexion = datetime.utcnow()
        db.session.commit()

    @classmethod
    def get_by_switch(cls, switch_id):
        """Obtiene todos los puertos de un switch específico."""
        return cls.query.filter_by(switch_id=switch_id, deleted=False)

    @classmethod
    def get_activos(cls):
        """Obtiene todos los puertos activos."""
        return cls.query.filter(
            cls.deleted == False,
            cls.estado_puerto.in_(['Activo', 'activo', 'Up', 'up', 'Conectado', 'conectado'])
        )

    @classmethod
    def get_por_vlan(cls, vlan):
        """Obtiene todos los puertos asignados a una VLAN específica."""
        return cls.query.filter_by(vlan_asignada=vlan, deleted=False)