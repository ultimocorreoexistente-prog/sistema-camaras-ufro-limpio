# models/equipo.py
"""
Modelo base para equipos de red y hardware.
Proporciona funcionalidades comunes para todos los tipos de equipos.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, or_
from sqlalchemy.orm import relationship, declared_attr
from models.base import BaseModel  # Correcto: Hereda metadatos base incluyendo id
from models import db
from models.enums.equipment_status import EquipmentStatus
# import enum  # Removed - enum moved to network_connections.py
import json

# ConnectionType enum moved to models/network_connections.py# NetworkConnection class moved to models/network_connections.py for complete definition

class EquipmentBase(BaseModel):
    """
    Clase base abstracta para todos los equipos.
    Proporciona atributos comunes y funcionalidades de monitoreo.
    """
    __abstract__ = True

    # id, created_at, updated_at, deleted heredados de BaseModelMixin

    # Información básica
    name = Column(String(100), nullable=False, index=True,
                  comment="Nombre identificador del equipo")
    model = Column(String(50), nullable=True,
                   comment="Modelo del equipo")
    manufacturer = Column(String(50), nullable=True,
                          comment="Fabricante del equipo")
    serial_number = Column(String(100), nullable=True, unique=True,
                          comment="Número de serie del equipo")
    inventory_number = Column(String(50), nullable=True, unique=True,
                              comment="Número de inventario interno")

    # Identificación de red
    ip_address = Column(String(45), nullable=True, index=True,
                        comment="Dirección IP del equipo (IPv4 o IPv6)")
    mac_address = Column(String(17), nullable=True, unique=True,
                          comment="Dirección MAC del equipo (formato XX:XX:XX:XX:XX:XX)")
    hostname = Column(String(100), nullable=True,
                      comment="Nombre del host")

    # Ubicación y estado
    ubicacion_id = Column(Integer, ForeignKey('ubicaciones.id'), nullable=True,
                          comment="ID de la ubicación donde está instalado")
    # ✅ Corregido para usar la clase EquipmentStatus directamente
    status = Column(String(20), nullable=False, default=EquipmentStatus.ACTIVO,
                    comment="Estado actual del equipo")

    # Configuración
    firmware_version = Column(String(20), nullable=True,
                              comment="Versión del firmware")
    configuration_backup = Column(Text, nullable=True,
                                  comment="Respaldo de configuración en formato JSON")

    # Fechas importantes
    purchase_date = Column(DateTime(timezone=True), nullable=True, # ✅ Usar timezone=True
                           comment="Fecha de compra")
    warranty_expiry = Column(DateTime(timezone=True), nullable=True, # ✅ Usar timezone=True
                             comment="Fecha de vencimiento de garantía")
    installation_date = Column(DateTime(timezone=True), nullable=True, # ✅ Usar timezone=True
                               comment="Fecha de instalación")

    # Especificaciones técnicas
    power_consumption = Column(Float, nullable=True,
                              comment="Consumo de energía en watts")
    operating_temperature = Column(String(50), nullable=True,
                                  comment="Temperatura de operación (ej: 0°C a 40°C)")
    dimensions = Column(String(50), nullable=True,
                        comment="Dimensiones del equipo (ej: 44x440x280 mm)")
    weight = Column(Float, nullable=True,
                    comment="Peso en kilogramos")

    # Monitoreo
    last_heartbeat = Column(DateTime(timezone=True), nullable=True, # ✅ Usar timezone=True
                            comment="Último heartbeat del equipo")
    uptime_percentage = Column(Float, default=100.0, nullable=False,
                               comment="Porcentaje de tiempo de actividad")

    # Metadatos
    notes = Column(Text, nullable=True,
                  comment="Notas adicionales")

    # Relaciones
    @declared_attr
    def ubicacion(cls):
        # Asume que el modelo Ubicacion tiene un back_populates llamado 'equipos'
        return relationship("Ubicacion", back_populates="equipos")
    
    # Método para serializar la configuración de respaldo si existe
    def get_configuration_backup_dict(self):
        if not self.configuration_backup:
            return None
        try:
            return json.loads(self.configuration_backup)
        except json.JSONDecodeError:
            return {"error": "Configuración de respaldo no es JSON válido"}

    # Métodos de monitoreo
    def is_online(self):
        """Verifica si el equipo está online basado en el último heartbeat (dentro de 5 minutos)."""
        if not self.last_heartbeat:
            return False
        # Asume que last_heartbeat fue guardado con timezone=True
        time_diff = datetime.now(timezone.utc) - self.last_heartbeat
        return time_diff.total_seconds() < 300  # 5 minutos

    def update_heartbeat(self, session=None):
        """Actualiza el timestamp del último heartbeat."""
        session = session or db.session
        self.last_heartbeat = datetime.now(timezone.utc)
        session.add(self)
        session.commit()

    def get_age_in_years(self):
        """Calcula la edad del equipo en años."""
        if not self.installation_date:
            return None
        age = datetime.now(timezone.utc) - self.installation_date
        return round(age.days / 365.25, 2)


# Clase Switch movida a models/switch.py para definición completa


# Clase UPS movida a models/ups.py para definición completa


# Clase NVR movida a models/nvr.py para definición completa


# Clase Gabinete movida a models/gabinete.py para definición completa


# Clase FuentePoder movida a models/fuente_poder.py para definición completa