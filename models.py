from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # admin, supervisor, tecnico, visualizador
    nombre_completo = db.Column(db.String(200))
    email = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Ubicacion(db.Model):
    __tablename__ = 'ubicacion'
    id = db.Column(db.Integer, primary_key=True)
    campus = db.Column(db.String(100), nullable=False)
    edificio = db.Column(db.String(200), nullable=False)
    piso = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    latitud = db.Column(db.Float)
    longitud = db.Column(db.Float)
    activo = db.Column(db.Boolean, default=True)

class Gabinete(db.Model):
    __tablename__ = 'gabinete'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(200))
    tipo_ubicacion_general = db.Column(db.String(50))  # Interior/Exterior/Subterraneo
    tipo_ubicacion_detallada = db.Column(db.String(200))
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicacion.id'))
    capacidad = db.Column(db.Integer)
    tiene_ups = db.Column(db.Boolean, default=False)
    tiene_switch = db.Column(db.Boolean, default=False)
    tiene_nvr = db.Column(db.Boolean, default=False)
    conexion_fibra = db.Column(db.Boolean, default=False)
    estado = db.Column(db.String(20), default='Activo')
    fecha_alta = db.Column(db.Date)
    fecha_baja = db.Column(db.Date)
    motivo_baja = db.Column(db.Text)
    fecha_ultima_revision = db.Column(db.Date)
    observaciones = db.Column(db.Text)
    latitud = db.Column(db.Float)
    longitud = db.Column(db.Float)
    
    ubicacion = db.relationship('Ubicacion', backref='gabinetes')

class Switch(db.Model):
    __tablename__ = 'switch'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(200))
    ip = db.Column(db.String(45))
    modelo = db.Column(db.String(100))
    marca = db.Column(db.String(100))
    numero_serie = db.Column(db.String(100))
    gabinete_id = db.Column(db.Integer, db.ForeignKey('gabinete.id'))
    puertos_totales = db.Column(db.Integer)
    puertos_usados = db.Column(db.Integer, default=0)
    puertos_disponibles = db.Column(db.Integer)
    capacidad_poe = db.Column(db.Boolean, default=False)
    estado = db.Column(db.String(20), default='Activo')
    fecha_alta = db.Column(db.Date)
    fecha_baja = db.Column(db.Date)
    motivo_baja = db.Column(db.Text)
    fecha_mantenimiento = db.Column(db.Date)
    observaciones = db.Column(db.Text)
    latitud = db.Column(db.Float)
    longitud = db.Column(db.Float)
    
    gabinete = db.relationship('Gabinete', backref='switches')

class Puerto_Switch(db.Model):
    __tablename__ = 'puerto_switch'
    id = db.Column(db.Integer, primary_key=True)
    switch_id = db.Column(db.Integer, db.ForeignKey('switch.id'), nullable=False)
    numero_puerto = db.Column(db.Integer, nullable=False)
    camara_id = db.Column(db.Integer, db.ForeignKey('camaras.id'))
    ip_dispositivo = db.Column(db.String(45))
    estado = db.Column(db.String(20), default='Disponible')  # En uso/Disponible/Averiado
    tipo_conexion = db.Column(db.String(20))  # PoE/Fibra/Normal
    nvr_id = db.Column(db.Integer, db.ForeignKey('nvr_dvr.id'))
    puerto_nvr = db.Column(db.String(20))
    
    switch = db.relationship('Switch', backref='puertos')
    camara = db.relationship('Camaras', foreign_keys='Puerto_Switch.camara_id', backref='puerto_asignado')

class UPS(db.Model):
    __tablename__ = 'ups'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    modelo = db.Column(db.String(100))
    marca = db.Column(db.String(100))
    capacidad_va = db.Column(db.Integer)
    numero_baterias = db.Column(db.Integer)
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicacion.id'))
    gabinete_id = db.Column(db.Integer, db.ForeignKey('gabinete.id'))
    equipos_que_alimenta = db.Column(db.Text)
    estado = db.Column(db.String(20), default='Activo')
    fecha_alta = db.Column(db.Date)
    fecha_baja = db.Column(db.Date)
    motivo_baja = db.Column(db.Text)
    fecha_instalacion = db.Column(db.Date)
    ultimo_mantenimiento = db.Column(db.Date)
    observaciones = db.Column(db.Text)
    latitud = db.Column(db.Float)
    longitud = db.Column(db.Float)
    
    ubicacion = db.relationship('Ubicacion', backref='ups_list')
    gabinete = db.relationship('Gabinete', backref='ups_list')

class NVR_DVR(db.Model):
    __tablename__ = 'nvr_dvr'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # NVR/DVR
    modelo = db.Column(db.String(100))
    marca = db.Column(db.String(100))
    canales_totales = db.Column(db.Integer)
    canales_usados = db.Column(db.Integer, default=0)
    ip = db.Column(db.String(45))
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicacion.id'))
    gabinete_id = db.Column(db.Integer, db.ForeignKey('gabinete.id'))
    estado = db.Column(db.String(20), default='Activo')
    fecha_alta = db.Column(db.Date)
    fecha_baja = db.Column(db.Date)
    motivo_baja = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    latitud = db.Column(db.Float)
    longitud = db.Column(db.Float)
    
    ubicacion = db.relationship('Ubicacion', backref='nvr_dvr_list')
    gabinete = db.relationship('Gabinete', backref='nvr_dvr_list')

class Fuente_Poder(db.Model):
    __tablename__ = 'fuente_poder'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    modelo = db.Column(db.String(100))
    voltaje = db.Column(db.String(20))
    amperaje = db.Column(db.String(20))
    equipos_que_alimenta = db.Column(db.Text)
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicacion.id'))
    gabinete_id = db.Column(db.Integer, db.ForeignKey('gabinete.id'))
    estado = db.Column(db.String(20), default='Activo')
    fecha_alta = db.Column(db.Date)
    fecha_baja = db.Column(db.Date)
    motivo_baja = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    
    ubicacion = db.relationship('Ubicacion', backref='fuentes_poder')
    gabinete = db.relationship('Gabinete', backref='fuentes_poder')

class Camara(db.Model):
    __tablename__ = 'camaras'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(200))
    ip = db.Column(db.String(45))
    modelo = db.Column(db.String(100))
    fabricante = db.Column(db.String(100))
    tipo_camara = db.Column(db.String(20))  # Domo/PTZ/Bullet
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicacion.id'))
    gabinete_id = db.Column(db.Integer, db.ForeignKey('gabinete.id'))
    switch_id = db.Column(db.Integer, db.ForeignKey('switch.id'))
    puerto_switch_id = db.Column(db.Integer, db.ForeignKey('puerto_switch.id'))
    nvr_id = db.Column(db.Integer, db.ForeignKey('nvr_dvr.id'))
    puerto_nvr = db.Column(db.String(20))
    requiere_poe_adicional = db.Column(db.Boolean, default=False)
    tipo_conexion = db.Column(db.String(20))
    estado = db.Column(db.String(20), default='Activo')  # Activo/Inactivo/Mantenimiento/Baja
    fecha_alta = db.Column(db.Date)
    fecha_baja = db.Column(db.Date)
    motivo_baja = db.Column(db.Text)
    instalador = db.Column(db.String(200))
    fecha_instalacion = db.Column(db.Date)
    observaciones = db.Column(db.Text)
    latitud = db.Column(db.Float)
    longitud = db.Column(db.Float)
    
    ubicacion = db.relationship('Ubicacion', backref='camaras')
    gabinete = db.relationship('Gabinete', backref='camaras')
    switch = db.relationship('Switch', backref='camaras')
    puerto_switch = db.relationship('Puerto_Switch', foreign_keys=[puerto_switch_id])
    nvr = db.relationship('NVR_DVR', backref='camaras')

class Catalogo_Tipo_Falla(db.Model):
    __tablename__ = 'catalogo_tipo_falla'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    gravedad = db.Column(db.String(20))  # Baja/Media/Alta/Critica
    tiempo_estimado_resolucion = db.Column(db.Integer)  # en horas

class Falla(db.Model):
    __tablename__ = 'falla'
    id = db.Column(db.Integer, primary_key=True)
    equipo_tipo = db.Column(db.String(50), nullable=False)  # Camara/Gabinete/Switch/UPS/NVR/Fuente
    equipo_id = db.Column(db.Integer, nullable=False)
    tipo_falla_id = db.Column(db.Integer, db.ForeignKey('catalogo_tipo_falla.id'))
    descripcion = db.Column(db.Text)
    prioridad = db.Column(db.String(20))  # Baja/Media/Alta/Critica
    fecha_reporte = db.Column(db.DateTime, default=datetime.utcnow)
    reportado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    estado = db.Column(db.String(20), default='Pendiente')  # Pendiente/Asignada/En Proceso/Reparada/Cerrada/Cancelada
    fecha_asignacion = db.Column(db.DateTime)
    tecnico_asignado_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    fecha_inicio_reparacion = db.Column(db.DateTime)
    fecha_fin_reparacion = db.Column(db.DateTime)
    tiempo_resolucion_horas = db.Column(db.Float)
    solucion_aplicada = db.Column(db.Text)
    materiales_utilizados = db.Column(db.Text)
    costo_reparacion = db.Column(db.Float)
    observaciones = db.Column(db.Text)
    fecha_cierre = db.Column(db.DateTime)
    
    tipo_falla = db.relationship('Catalogo_Tipo_Falla', backref='fallas')
    reportado_por = db.relationship('Usuario', foreign_keys=[reportado_por_id], backref='fallas_reportadas')
    tecnico_asignado = db.relationship('Usuario', foreign_keys=[tecnico_asignado_id], backref='fallas_asignadas')

class Mantenimiento(db.Model):
    __tablename__ = 'mantenimiento'
    id = db.Column(db.Integer, primary_key=True)
    equipo_tipo = db.Column(db.String(50), nullable=False)
    equipo_id = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # Preventivo/Correctivo/Predictivo
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    tecnico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    descripcion = db.Column(db.Text)
    materiales_utilizados = db.Column(db.Text)
    equipos_afectados = db.Column(db.Text)
    tiempo_ejecucion_horas = db.Column(db.Float)
    costo = db.Column(db.Float)
    observaciones = db.Column(db.Text)
    
    tecnico = db.relationship('Usuario', backref='mantenimientos')

class Equipo_Tecnico(db.Model):
    __tablename__ = 'equipo_tecnico'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(200))
    estado = db.Column(db.String(20), default='Activo')  # Activo/Inactivo
    fecha_ingreso = db.Column(db.Date)

class Historial_Estado_Equipo(db.Model):
    __tablename__ = 'historial_estado_equipo'
    id = db.Column(db.Integer, primary_key=True)
    equipo_tipo = db.Column(db.String(50), nullable=False)
    equipo_id = db.Column(db.Integer, nullable=False)
    estado_anterior = db.Column(db.String(20))
    estado_nuevo = db.Column(db.String(20), nullable=False)
    fecha_cambio = db.Column(db.DateTime, default=datetime.utcnow)
    motivo = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    usuario = db.relationship('Usuario', backref='cambios_estado')
