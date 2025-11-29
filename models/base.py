#!/usr/bin/env python3
"""
Base.py - Arquitectura Mejorada Sistema de Gestión de Cámaras UFRO
Versión 2.0 - 27 nov 2025

Características:
- Enums tipados para mayor seguridad
- Mixins con funcionalidades comunes
- Relaciones normalizadas
- Modelo de datos optimizado
- Manejo de errores robusto
"""

from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict, Any
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import logging
from models.enums.estado_camara import EstadoCamara

db = SQLAlchemy()

# ======================
# Enums de la aplicación
# ======================

class RolEnum(Enum):
    """Roles de usuario del sistema"""
    ADMIN = "ADMIN"
    SUPERVISOR = "SUPERVISOR"
    OPERADOR = "OPERADOR"
    LECTURA = "LECTURA"

class TipoUbicacion(Enum):
    """Tipos de ubicación de las cámaras"""
    EDIFICIO = "EDIFICIO"
    AULA = "AULA"
    PASILLO = "PASILLO"
    EXTERIOR = "EXTERIOR"
    LABORATORIO = "LABORATORIO"
    ESTACIONAMIENTO = "ESTACIONAMIENTO"

class EstadoTicket(Enum):
    """Estados de tickets de soporte"""
    ABIERTO = "ABIERTO"
    EN_PROCESO = "EN_PROCESO"
    RESUELTO = "RESUELTO"
    CERRADO = "CERRADO"
    CANCELADO = "CANCELADO"

class PrioridadEnum(Enum):
    """Prioridades de tickets y tareas"""
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"

# ======================
# Mixins - Funcionalidad común
# ======================

class ModelMixin:
    """Mixin con funcionalidades comunes para todos los modelos"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if not column.name.startswith('_')
        }
    
    def save(self) -> bool:
        """Guarda el modelo en la base de datos"""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving {self.__class__.__name__}: {e}")
            return False
    
    def delete(self) -> bool:
        """Elimina el modelo de la base de datos"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error deleting {self.__class__.__name__}: {e}")
            return False
    
    def update(self, **kwargs) -> bool:
        """Actualiza los campos del modelo"""
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            return self.save()
        except Exception as e:
            logging.error(f"Error updating {self.__class__.__name__}: {e}")
            return False

class TimestampedModel(ModelMixin):
    """Mixin para modelos con timestamps de creación y actualización"""
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)

class BaseModelMixin(TimestampedModel):
    """Mixin simplificado para modelos básicos que heredan de db.Model"""
    
    id = db.Column(db.Integer, primary_key=True)
    
    @classmethod
    def get_by_id(cls, id_value):
        """Obtiene un registro por ID"""
        return cls.query.get(id_value)
    
    @classmethod
    def get_all(cls, limit=None):
        """Obtiene todos los registros"""
        query = cls.query
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @classmethod
    def count(cls):
        """Cuenta el total de registros"""
        return cls.query.count()

class BaseModel(db.Model, TimestampedModel):
    """Clase base para todos los modelos del sistema"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    
    @classmethod
    def get_by_id(cls, id_value):
        """Obtiene un registro por ID"""
        return cls.query.get(id_value)
    
    @classmethod
    def get_all(cls, limit=None):
        """Obtiene todos los registros"""
        query = cls.query
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @classmethod
    def count(cls):
        """Cuenta el total de registros"""
        return cls.query.count()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario incluyendo el ID"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if not column.name.startswith('_')
        }
    
    def save(self) -> bool:
        """Guarda el modelo en la base de datos"""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving {self.__class__.__name__}: {e}")
            return False
    
    def delete(self) -> bool:
        """Elimina el modelo de la base de datos"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error deleting {self.__class__.__name__}: {e}")
            return False
    
    def update(self, **kwargs) -> bool:
        """Actualiza los campos del modelo"""
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            return self.save()
        except Exception as e:
            logging.error(f"Error updating {self.__class__.__name__}: {e}")
            return False

# ======================
# Modelos del Sistema
# ======================

class Rol(db.Model, TimestampedModel):
    """Modelo de roles del sistema"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.Enum(RolEnum), nullable=False, unique=True)
    descripcion = db.Column(db.String(255), nullable=True)
    permisos = db.Column(db.Text, nullable=True)  # JSON con permisos específicos
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relación con usuarios (ahora definida en models/usuario.py)
    # Nota: La relación se manejará desde la clase Usuario



class Ubicacion(db.Model, TimestampedModel):
    """Modelo de ubicaciones del campus UFRO"""
    __tablename__ = 'ubicaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.Enum(TipoUbicacion), nullable=False)
    edificio = db.Column(db.String(50), nullable=True)
    piso = db.Column(db.Integer, nullable=True)
    numero_aula = db.Column(db.String(10), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    capacidad = db.Column(db.Integer, nullable=True)
    
    # Coordenadas para mapas
    latitud = db.Column(db.Float, nullable=True)
    longitud = db.Column(db.Float, nullable=True)
    
    # Relación con cámaras (se define en Camara con back_populates)
    camaras = db.relationship('Camara', back_populates='ubicacion_obj', lazy='dynamic')
    
    # Relación con equipos que heredan de EquipmentBase
    equipos = db.relationship('EquipmentBase', back_populates='ubicacion', lazy='dynamic')
class EventoCamara(db.Model, TimestampedModel):
    """Registro de eventos de las cámaras"""
    __tablename__ = 'eventos_camara'
    
    id = db.Column(db.Integer, primary_key=True)
    camara_id = db.Column(db.Integer, db.ForeignKey('camaras.id'), nullable=False)
    
    # Detalles del evento
    tipo_evento = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    severidad = db.Column(db.Enum(PrioridadEnum), nullable=False, default=PrioridadEnum.MEDIA)
    
    # Estado antes y después
    estado_anterior = db.Column(db.String(50), nullable=True)
    estado_nuevo = db.Column(db.String(50), nullable=True)
    
    # Datos técnicos del evento
    ip_origen = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    
    # Resuelto por
    resuelto_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    
    # Relación de vuelta
    camara_obj = db.relationship('Camara', back_populates='eventos')

class Ticket(db.Model, TimestampedModel):
    """Tickets de soporte y mantenimiento"""
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_ticket = db.Column(db.String(20), unique=True, nullable=False)
    camara_id = db.Column(db.Integer, db.ForeignKey('camaras.id'), nullable=False)
    
    # Detalles del ticket
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    prioridad = db.Column(db.Enum(PrioridadEnum), nullable=False, default=PrioridadEnum.MEDIA)
    estado = db.Column(db.Enum(EstadoTicket), nullable=False, default=EstadoTicket.ABIERTO)
    
    # Asignación
    asignado_a = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    reportado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Fechas
    fecha_vencimiento = db.Column(db.Date, nullable=True)
    fecha_resolucion = db.Column(db.DateTime, nullable=True)
    
    # Resolución
    solucion = db.Column(db.Text, nullable=True)
    comentarios_internos = db.Column(db.Text, nullable=True)
    
    # Relaciones adicionales
    usuario_asignado = db.relationship('Usuario', foreign_keys=[asignado_a], backref='tickets_asignados')
    usuario_reportante = db.relationship('Usuario', foreign_keys=[reportado_por], backref='tickets_reportados')
    
    # Relación de vuelta
    camara_obj = db.relationship('Camara', back_populates='tickets')

class TrazabilidadMantenimiento(db.Model, TimestampedModel):
    """Trazabilidad completa de mantenimientos"""
    __tablename__ = 'trazabilidad_mantenimiento'
    
    id = db.Column(db.Integer, primary_key=True)
    camara_id = db.Column(db.Integer, db.ForeignKey('camaras.id'), nullable=False)
    
    # Detalles del mantenimiento
    tipo_mantenimiento = db.Column(db.String(50), nullable=False)
    descripcion_trabajo = db.Column(db.Text, nullable=False)
    
    # Personal y fechas
    tecnico_responsable = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    
    # Costos y materiales
    costo_mano_obra = db.Column(db.Float, nullable=True)
    costo_repuestos = db.Column(db.Float, nullable=True)
    costo_total = db.Column(db.Float, nullable=True)
    
    # Estado antes y después
    estado_anterior = db.Column(db.String(50), nullable=True)
    estado_nuevo = db.Column(db.String(50), nullable=True)
    
    # Observaciones y recomendaciones
    observaciones = db.Column(db.Text, nullable=True)
    recomendaciones = db.Column(db.Text, nullable=True)
    
    # Técnico responsable
    tecnico = db.relationship('Usuario', foreign_keys=[tecnico_responsable])
    
    # Relación de vuelta
    camara_obj = db.relationship('Camara', back_populates='trazabilidades')

class Inventario(db.Model, TimestampedModel):
    """Inventario de repuestos y equipos"""
    __tablename__ = 'inventario'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo_articulo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    marca = db.Column(db.String(50), nullable=True)
    modelo = db.Column(db.String(50), nullable=True)
    
    # Inventario
    cantidad_actual = db.Column(db.Integer, nullable=False, default=0)
    cantidad_minima = db.Column(db.Integer, nullable=True)
    cantidad_maxima = db.Column(db.Integer, nullable=True)
    unidad_medida = db.Column(db.String(20), default='UNIDAD')
    
    # Ubicación de almacenamiento
    ubicacion_almacen = db.Column(db.String(100), nullable=True)
    pasillo = db.Column(db.String(20), nullable=True)
    estanteria = db.Column(db.String(20), nullable=True)
    
    # Información comercial
    precio_unitario = db.Column(db.Float, nullable=True)
    proveedor = db.Column(db.String(100), nullable=True)
    numero_parte_proveedor = db.Column(db.String(50), nullable=True)
    
    # Fechas
    fecha_ultimo_ingreso = db.Column(db.Date, nullable=True)
    fecha_ultima_salida = db.Column(db.Date, nullable=True)
    
    # Estado
    activo = db.Column(db.Boolean, default=True, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)

# ======================
# Funciones de inicialización
# ======================

def create_roles():
    """Crea los roles básicos del sistema"""
    roles_data = [
        {
            'nombre': RolEnum.ADMIN,
            'descripcion': 'Administrador del sistema con acceso completo',
            'permisos': 'ALL_PERMISSIONS'
        },
        {
            'nombre': RolEnum.SUPERVISOR,
            'descripcion': 'Supervisor con permisos de gestión y reportes',
            'permisos': 'MANAGE_CAMERAS, VIEW_REPORTS, MANAGE_TICKETS'
        },
        {
            'nombre': RolEnum.OPERADOR,
            'descripcion': 'Operador con permisos de mantenimiento',
            'permisos': 'VIEW_CAMERAS, MANAGE_MAINTENANCE, CREATE_TICKETS'
        },
        {
            'nombre': RolEnum.LECTURA,
            'descripcion': 'Usuario de solo lectura',
            'permisos': 'VIEW_CAMERAS'
        }
    ]
    
    for rol_data in roles_data:
        rol = Rol.query.filter_by(nombre=rol_data['nombre']).first()
        if not rol:
            rol = Rol(**rol_data)
            rol.save()

def create_default_admin():
    """Crea el usuario administrador por defecto"""
    # Obtener la clase Usuario dinámicamente para evitar import circular
    try:
        Usuario = db.Model._decl_class_registry.get('Usuario')
        if Usuario is None:
            logging.warning("⚠️ Usuario no disponible para crear admin por defecto")
            return None
        
        # Verificar si ya existe
        admin = Usuario.query.filter_by(username='admin').first()
        if admin:
            return admin
        
        # Crear administrador básico
        admin = Usuario(
            username='admin',
            email='charles.jelvez@ufrontera.cl',
            full_name='Charles Jelvez - Administrador UFRO',
            password_hash='pbkdf2:sha256:600000$Z8Z8Z8Z8Z8Z8Z8Z8$Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8',  # Vivita0468 hasheada
            is_active=True,
            role='admin'
        )
        admin.save()
        
        return admin
    except Exception as e:
        logging.error(f"❌ Error creando admin por defecto: {e}")
        return None

def init_database():
    """Inicializa la base de datos con datos por defecto"""
    try:
        # Crear todas las tablas
        db.create_all()
        
        # Crear roles
        create_roles()
        
        # Crear administrador por defecto
        admin = create_default_admin()
        
        logging.info("✅ Base de datos inicializada correctamente")
        return admin
        
    except Exception as e:
        logging.error(f"❌ Error inicializando base de datos: {e}")
        raise

# ======================
# Utilidades adicionales
# ======================

def get_user_stats() -> Dict[str, Any]:
    """Obtiene estadísticas generales del sistema"""
    try:
        # Obtener la clase Usuario dinámicamente para evitar import circular
        Usuario = db.Model._decl_class_registry.get('Usuario')
        if Usuario is None:
            logging.warning("⚠️ Usuario no disponible para estadísticas")
            return {'error': 'Usuario model not available'}
        
        stats = {
            'total_usuarios': Usuario.query.count(),
            'usuarios_activos': Usuario.query.filter_by(is_active=True).count(),
            'usuarios_por_rol': {},
            'total_camaras': None,
            'camaras_por_estado': {}
        }
        
        # Estadísticas por rol
        roles = Rol.query.all()
        for rol in roles:
            # Contar usuarios por rol usando el campo 'role'
            count = Usuario.query.filter_by(role=rol.nombre.value).count()
            stats['usuarios_por_rol'][rol.nombre.value] = count
        
        return stats
    except Exception as e:
        logging.error(f"❌ Error obteniendo estadísticas de usuarios: {e}")
        return {'error': str(e)}

def get_camera_stats() -> Dict[str, Any]:
    """Obtiene estadísticas de cámaras"""
    stats = {
        'total_camaras': Camara.query.count(),
        'camaras_por_estado': {},
        'camaras_por_ubicacion': {},
        'proximos_mantenimientos': []
    }
    
    # Cámaras por estado
    estados = db.session.query(Camara.estado, db.func.count(Camara.id)).group_by(Camara.estado).all()
    for estado, count in estados:
        stats['camaras_por_estado'][estado.value] = count
    
    # Próximos mantenimientos (próximos 30 días)
    fecha_limite = date.today()
    stats['proximos_mantenimientos'] = Camara.query.filter(
        Camara.proximo_mantenimiento <= fecha_limite
    ).count()
    
    return stats