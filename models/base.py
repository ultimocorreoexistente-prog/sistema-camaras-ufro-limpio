<<<<<<< HEAD
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, Boolean, String
from datetime import datetime

# Base para todos los modelos
BaseModel = declarative_base()

class BaseModelMixin:
    """Mixin base para todos los modelos SQLAlchemy"""
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted = Column(Boolean, default=False)
    
    @property
    def is_active(self):
        """Property para compatibilidad"""
        return not self.deleted
    
    @is_active.setter  
    def is_active(self, value):
        """Setter para compatibilidad"""
        self.deleted = not value
    
    def save(self, session=None):
        """Guardar instancia en base de datos"""
        if session is None:
            from models import db
            session = db.session
        session.add(self)
        session.commit()
        return self
    
    def delete(self, session=None):
        """Soft delete"""
        if session is None:
            from models import db
            session = db.session
        self.deleted = True
        session.commit()
        return self
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
=======
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, event
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import enum

db = SQLAlchemy()

# Enums
class RolEnum(enum.Enum):
    ADMIN = 'ADMIN'
    TECNICO = 'TECNICO'
    LECTURA = 'LECTURA'

class PrioridadEnum(enum.Enum):
    ALTA = 'ALTA'
    MEDIA = 'MEDIA'
    BAJA = 'BAJA'

class EstadoFallaEnum(enum.Enum):
    PENDIENTE = 'PENDIENTE'
    EN_PROGRESO = 'EN_PROGRESO'
    CERRADA = 'CERRADA'

class EstadoEquipoEnum(enum.Enum):
    OPERATIVO = 'OPERATIVO'
    FALLA_MENOR = 'FALLA_MENOR'
    FUERA_DE_SERVICIO = 'FUERA_DE_SERVICIO'

# Catálogos
class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(Enum(RolEnum), unique=True, nullable=False)

class Prioridad(db.Model):
    __tablename__ = 'prioridades'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(Enum(PrioridadEnum), unique=True, nullable=False)

class EstadoFalla(db.Model):
    __tablename__ = 'estados_falla'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(Enum(EstadoFallaEnum), unique=True, nullable=False)

class EstadoEquipo(db.Model):
    __tablename__ = 'estados_equipo'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(Enum(EstadoEquipoEnum), unique=True, nullable=False)

# ✅ CORREGIDO: Ubicacion con campo `nombre` (no nombre_edificio)
class Ubicacion(db.Model):
    __tablename__ = 'ubicaciones'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)  # ✅ VARCHAR(255)
    campus = db.Column(db.String(100))
    edificio = db.Column(db.String(100))
    piso = db.Column(db.String(50))
    zona = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    latitud = db.Column(db.Float)
    longitud = db.Column(db.Float)
    activo = db.Column(db.Boolean, default=True)

# ✅ CORREGIDO: Usuario con `email`, no `nombre_usuario`
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)  # ✅ email UFRO
    password_hash = db.Column(db.String(256), nullable=False)
    nombre_completo = db.Column(db.String(120), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    rol = db.relationship('Rol', backref=db.backref('usuarios', lazy=True))
    activo = db.Column(db.Boolean, default=True)
    ultimo_acceso = db.Column(db.DateTime)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Modelo base para herencia
class EquipoBase(db.Model):
    __tablename__ = 'equipos_base'
    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(100), nullable=False)
    serie = db.Column(db.String(100), unique=True, nullable=False)
    fecha_instalacion = db.Column(db.DateTime, default=datetime.datetime.now)
    id_ubicacion = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey('estados_equipo.id'), nullable=False, default=1)
    estado = db.relationship('EstadoEquipo', backref='equipos_base', lazy=True)
    tipo = db.Column(db.String(50))
    __mapper_args__ = {
        'polymorphic_identity': 'equipo',
        'polymorphic_on': tipo
    }
    fallas = db.relationship('Falla', backref='equipo', lazy='dynamic')
    mantenimientos = db.relationship('Mantenimiento', backref='equipo', lazy='dynamic')

class Camara(EquipoBase):
    __tablename__ = 'camaras'
    id = db.Column(db.Integer, db.ForeignKey('equipos_base.id'), primary_key=True)
    resolucion = db.Column(db.String(50))
    tipo_lente = db.Column(db.String(50))
    __mapper_args__ = {'polymorphic_identity': 'camara'}

class Switch(EquipoBase):
    __tablename__ = 'switches'
    id = db.Column(db.Integer, db.ForeignKey('equipos_base.id'), primary_key=True)
    puertos_poe = db.Column(db.Integer)
    capacidad_total = db.Column(db.String(50))
    __mapper_args__ = {'polymorphic_identity': 'switch'}

class Nvr(EquipoBase):
    __tablename__ = 'nvrs'
    id = db.Column(db.Integer, db.ForeignKey('equipos_base.id'), primary_key=True)
    canales = db.Column(db.Integer)
    almacenamiento_tb = db.Column(db.Float)
    __mapper_args__ = {'polymorphic_identity': 'nvr'}

class Falla(db.Model):
    __tablename__ = 'fallas'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_reporte = db.Column(db.DateTime, default=datetime.datetime.now)
    id_equipo = db.Column(db.Integer, db.ForeignKey('equipos_base.id'), nullable=False)
    prioridad_id = db.Column(db.Integer, db.ForeignKey('prioridades.id'), nullable=False, default=3)
    prioridad = db.relationship('Prioridad', backref=db.backref('fallas', lazy=True))
    estado_id = db.Column(db.Integer, db.ForeignKey('estados_falla.id'), nullable=False, default=1)
    estado = db.relationship('EstadoFalla', backref=db.backref('fallas', lazy=True))
    id_usuario_reporta = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    usuario_reporta = db.relationship('Usuario', foreign_keys=[id_usuario_reporta])

class Mantenimiento(db.Model):
    __tablename__ = 'mantenimientos'
    id = db.Column(db.Integer, primary_key=True)
    fecha_inicio = db.Column(db.DateTime, default=datetime.datetime.now)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    tipo = db.Column(db.String(100), nullable=False)
    descripcion_trabajo = db.Column(db.Text, nullable=False)
    id_equipo = db.Column(db.Integer, db.ForeignKey('equipos_base.id'), nullable=False)
    id_tecnico = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tecnico = db.relationship('Usuario', foreign_keys=[id_tecnico])
    id_falla = db.Column(db.Integer, db.ForeignKey('fallas.id'), nullable=True)
    falla = db.relationship('Falla', backref=db.backref('mantenimientos', lazy=True, uselist=False))

# 🔑 Compatibilidad retroactiva
BaseModel = db.Model
BaseModelMixin = BaseModel

def create_all_tables():
    db.create_all()

def seed_initial_data():
    from config import get_config
    config = get_config()
    
    # Seed roles
    if not Rol.query.count():
        for name in config.ROLES:
            db.session.add(Rol(nombre=RolEnum(name)))
    db.session.commit()
    
    # Seed ubicaciones — ✅ USANDO `nombre`
    if not Ubicacion.query.count():
        db.session.add_all([
            Ubicacion(
                nombre='Campus Temuco - Edificio Central',
                campus='Temuco',
                edificio='Edificio Central',
                piso='1',
                zona='Entrada Principal'
            ),
            Ubicacion(
                nombre='Campus Temuco - Biblioteca Central',
                campus='Temuco',
                edificio='Biblioteca Central',
                piso='2',
                zona='Sala de Lectura'
            ),
            Ubicacion(
                nombre='Campus Pucón - Sede Principal',
                campus='Pucón',
                edificio='Edificio Administrativo',
                piso='PB',
                zona='Recepción'
            ),
        ])
        db.session.commit()
    
    # Seed usuarios — ✅ emails UFRO
    if not Usuario.query.count():
        rol_admin = Rol.query.filter_by(nombre=RolEnum.ADMIN).first()
        rol_tecnico = Rol.query.filter_by(nombre=RolEnum.TECNICO).first()
        rol_lectura = Rol.query.filter_by(nombre=RolEnum.LECTURA).first()
        
        admin = Usuario(
            email='charles.jelvez@ufrontera.cl',
            nombre_completo='Charles Jelvez',
            rol=rol_admin,
            activo=True
        )
        admin.set_password('Vivita0468')  # ✅ misma clave del deploy exitoso

        tecnico = Usuario(
            email='soporte.camaras@ufrontera.cl',
            nombre_completo='Soporte Cámaras',
            rol=rol_tecnico,
            activo=True
        )
        tecnico.set_password('tecnico123')

        lectura = Usuario(
            email='visualizador.seguridad@ufrontera.cl',
            nombre_completo='Visualizador Seguridad',
            rol=rol_lectura,
            activo=True
        )
        lectura.set_password('lectura123')

        db.session.add_all([admin, tecnico, lectura])
        db.session.commit()
        print("✅ Usuarios UFRO creados")
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
