"""
<<<<<<< HEAD
Modelos simplificados para el Sistema de Cámaras UFRO
Compatible con PostgreSQL y Flask-Login
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# Usuario con Flask-Login
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    telefono = db.Column(db.String(20))
    departamento = db.Column(db.String(100))
    rol = db.Column(db.String(50), nullable=False, default='visualizador')
    activo = db.Column(db.Boolean, default=True)
    ultimo_acceso = db.Column(db.DateTime)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Usuario {self.username}>'


# Ubicación
class Ubicacion(db.Model):
    __tablename__ = 'ubicaciones'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    edificio = db.Column(db.String(100))
    piso = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    latitud = db.Column(db.Float)
    longitud = db.Column(db.Float)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Ubicacion {self.nombre}>'


# Cámara
class Camara(db.Model):
    __tablename__ = 'camaras'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False, index=True)
    ip_address = db.Column(db.String(45), unique=True, nullable=False, index=True)
    ubicacion = db.Column(db.String(200))
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    serie = db.Column(db.String(100))
    estado = db.Column(db.String(50), default='activa')
    ultima_conexion = db.Column(db.DateTime)
    fecha_instalacion = db.Column(db.DateTime)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    fallas = db.relationship('Falla', backref='camara', lazy='dynamic')

    def __repr__(self):
        return f'<Camara {self.nombre}>'


# Falla
class Falla(db.Model):
    __tablename__ = 'fallas'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, index=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    tipo = db.Column(db.String(50))
    prioridad = db.Column(db.String(20), default='media')
    estado = db.Column(db.String(30), default='abierta')
    camara_id = db.Column(db.Integer, db.ForeignKey('camaras.id'))
    fecha_reporte = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_resolucion = db.Column(db.DateTime)
    reportado_por = db.Column(db.String(100))
    causa_raiz = db.Column(db.Text)
    solucion = db.Column(db.Text)
    tiempo_resolucion = db.Column(db.Float)
    costo_reparacion = db.Column(db.Float, default=0)
    equipos_afectados = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Falla {self.codigo}>'


# Mantenimiento
class Mantenimiento(db.Model):
    __tablename__ = 'mantenimientos'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, index=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    tipo = db.Column(db.String(50))
    equipo_tipo = db.Column(db.String(50))
    equipo_id = db.Column(db.Integer)
    fecha_programada = db.Column(db.DateTime)
    fecha_inicio = db.Column(db.DateTime)
    fecha_fin = db.Column(db.DateTime)
    estado = db.Column(db.String(30), default='programado')
    prioridad = db.Column(db.String(20), default='media')
    responsable = db.Column(db.String(100))
    costo = db.Column(db.Float, default=0)
    observaciones = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Mantenimiento {self.codigo}>'


# Gabinete/Rack
class Gabinete(db.Model):
    __tablename__ = 'gabinetes'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(200), nullable=False)
    ubicacion = db.Column(db.String(200))
    tipo = db.Column(db.String(50))
    estado = db.Column(db.String(30), default='activo')
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Gabinete {self.codigo}>'


# UPS
class UPS(db.Model):
    __tablename__ = 'ups'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(200), nullable=False)
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    capacidad_va = db.Column(db.Integer)
    capacidad_watts = db.Column(db.Integer)
    gabinete_id = db.Column(db.Integer, db.ForeignKey('gabinetes.id'))
    estado = db.Column(db.String(30), default='activo')
    observaciones = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<UPS {self.codigo}>'


# Switch
class Switch(db.Model):
    __tablename__ = 'switches'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(200), nullable=False)
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    puertos_total = db.Column(db.Integer)
    tipo = db.Column(db.String(50))
    poe = db.Column(db.Boolean, default=False)
    gabinete_id = db.Column(db.Integer, db.ForeignKey('gabinetes.id'))
    ip_address = db.Column(db.String(45))
    estado = db.Column(db.String(30), default='activo')
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Switch {self.codigo}>'


# NVR/DVR
class NVR(db.Model):
    __tablename__ = 'nvr'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(200), nullable=False)
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    canales = db.Column(db.Integer)
    ip_address = db.Column(db.String(45))
    gabinete_id = db.Column(db.Integer, db.ForeignKey('gabinetes.id'))
    estado = db.Column(db.String(30), default='activo')
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<NVR {self.codigo}>'


# Fuente de Poder
class FuentePoder(db.Model):
    __tablename__ = 'fuentes_poder'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(200), nullable=False)
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    capacidad = db.Column(db.Integer)
    voltaje = db.Column(db.String(50))
    estado = db.Column(db.String(30), default='activo')
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<FuentePoder {self.codigo}>'


# Fotografía
class Fotografia(db.Model):
    __tablename__ = 'fotografias'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    archivo = db.Column(db.String(300), nullable=False)
    tipo = db.Column(db.String(50))
    entidad_tipo = db.Column(db.String(50))
    entidad_id = db.Column(db.Integer)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Fotografia {self.titulo}>'
=======
Módulos de Modelos - Sistema de Cámaras UFRO
Consolida todos los modelos SQLAlchemy para imports simples
"""

# Importar base de datos
from models.base import db

# Importar todos los modelos
from models.usuario import Usuario
from models.camara import Camara
from models.ubicacion import Ubicacion
from models.nvr import NVR
from models.dvr import DVR
from models.switch import Switch
from models.ups import UPS
from models.gabinete import Gabinete
from models.fuente_poder import FuentePoder
from models.falla import Falla
from models.mantenimiento import Mantenimiento
from models.fotografia import Fotografia
from models.historial_estado_equipo import HistorialEstadoEquipo
from models.catalogo_tipo_falla import CatalogoTipoFalla
from models.equipo_tecnico import EquipoTecnico

# Importar enums
from models.enums.equipment_status import EquipmentStatus
from models.enums.estado_camara import EstadoCamara
from models.enums.mantenimiento_status import MantenimientoStatus
from models.enums.gravedad_falla import GravedadFalla
from models.enums.categoria_falla import CategoriaFalla

__all__ = [
    'db',
    'Usuario', 'Camara', 'Ubicacion', 'NVR', 'DVR', 'Switch', 'UPS',
    'Gabinete', 'FuentePoder', 'Falla', 'Mantenimiento', 'Fotografia',
    'HistorialEstadoEquipo', 'CatalogoTipoFalla', 'EquipoTecnico',
    'EquipmentStatus', 'EstadoCamara', 'MantenimientoStatus', 
    'GravedadFalla', 'CategoriaFalla'
]
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
