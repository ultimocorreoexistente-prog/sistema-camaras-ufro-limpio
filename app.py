import os
import logging
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importamos la función de configuración MEJORADA
from config import get_config

# ========================================
# 🔧 INICIALIZACIÓN DE EXTENSIONES
# ========================================

db = SQLAlchemy()
login_manager = LoginManager()

# ========================================
# 📊 DEFINICIÓN DE MODELOS SQLAlchemy
# ========================================

class Usuario(db.Model, UserMixin):
    """🎯 Modelo de usuario para autenticación y gestión."""
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    full_name = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(20), default='LECTURA')  # ADMIN, TECNICO, LECTURA
    password_hash = db.Column(db.String(256), nullable=False)
    activo = db.Column(db.Boolean, default=True)  # NOTA: Esta columna requiere migración de BD
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """🔐 Genera el hash de la contraseña."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """✅ Verifica la contraseña contra el hash almacenado."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Usuario {self.username}>'

class Ubicacion(db.Model):
    """📍 Modelo para representar la ubicación física de los equipos."""
    __tablename__ = 'ubicaciones'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    latitud = db.Column(db.String(255))  # Columna añadida en db_setup.py
    longitud = db.Column(db.String(255))  # Columna añadida en db_setup.py
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔗 Relaciones uno a muchos con equipos
    camaras = db.relationship('Camara', backref='ubicacion_obj', lazy=True)
    switches = db.relationship('Switch', backref='ubicacion_obj', lazy=True)
    nvrs = db.relationship('NvrDvr', backref='ubicacion_obj', lazy=True)
    gabinetes = db.relationship('Gabinete', backref='ubicacion_obj', lazy=True)
    ups = db.relationship('Ups', backref='ubicacion_obj', lazy=True)

class Camara(db.Model):
    """📹 Modelo para representar una cámara de seguridad."""
    __tablename__ = 'camaras'
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.String(100), unique=True, nullable=False)
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    ip = db.Column(db.String(15), unique=True)
    estado = db.Column(db.String(50), default='inactiva')  # Columna añadida en db_setup.py
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Switch(db.Model):
    """🔌 Modelo para switches de red."""
    __tablename__ = 'switches'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(50))
    ip = db.Column(db.String(15), unique=True)
    puertos = db.Column(db.Integer, default=24)
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class NvrDvr(db.Model):
    """📺 Modelo para NVR/DVR."""
    __tablename__ = 'nvr_dvr'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), default='NVR')  # NVR o DVR
    modelo = db.Column(db.String(50))
    ip = db.Column(db.String(15), unique=True)
    canales = db.Column(db.Integer, default=16)
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Gabinete(db.Model):
    """🏠 Modelo para gabinetes de equipos."""
    __tablename__ = 'gabinetes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(50))
    tipo = db.Column(db.String(30), default='Pared')  # Pared, Piso, Rack
    capacidad_u = db.Column(db.Integer, default=12)  # Unidades de rack
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Ups(db.Model):
    """🔋 Modelo para sistemas UPS."""
    __tablename__ = 'ups'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(50))
    capacidad_va = db.Column(db.Integer)  # Voltamperes
    autonomia_minutos = db.Column(db.Integer)
    estado_bateria = db.Column(db.String(30), default='buena')  # buena, regular, mala
    activo = db.Column(db.Boolean, default=True)  # Columna añadida en db_setup.py
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ========================================
# 🗃️ MODELOS FALTANTES - SISTEMA COMPLETO UFRO
# ========================================

class CatalogoTipoFalla(db.Model):
    """🛠️ Catálogo de tipos de fallas."""
    __tablename__ = 'catalogo_tipo_falla'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    categoria = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    gravedad = db.Column(db.String(50))
    tiempo_estimado_resolucion = db.Column(db.Integer)

class EquipoTecnico(db.Model):
    """👨‍🔧 Equipo técnico disponible."""
    __tablename__ = 'equipo_tecnico'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    estado = db.Column(db.String(20), default='activo')
    fecha_ingreso = db.Column(db.DateTime)

class Equipos(db.Model):
    """💻 Equipos generales del sistema."""
    __tablename__ = 'equipos'
    id = db.Column(db.Integer, primary_key=True)
    equipment_name = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    serie = db.Column(db.String(100))
    ip_address = db.Column(db.String(15))
    estado = db.Column(db.String(20), default='activo')
    activo = db.Column(db.Boolean, default=True)
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False)
    hostname = db.Column(db.String(100))
    mac_address = db.Column(db.String(17))
    firmware_version = db.Column(db.String(50))
    warranty_expiry = db.Column(db.Date)
    installation_date = db.Column(db.Date)
    last_heartbeat = db.Column(db.DateTime)
    uptime_percentage = db.Column(db.Float)
    notes = db.Column(db.Text)

class EquiposBase(db.Model):
    """🏠 Base de equipos."""
    __tablename__ = 'equipos_base'
    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(100), nullable=False)
    serie = db.Column(db.String(100), nullable=False)
    fecha_instalacion = db.Column(db.Date)
    id_ubicacion = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'))
    estado_id = db.Column(db.Integer)
    tipo = db.Column(db.String(50), nullable=False)

class EstadosEquipo(db.Model):
    """📊 Estados de equipos."""
    __tablename__ = 'estados_equipo'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class EstadosFalla(db.Model):
    """⚠️ Estados de fallas."""
    __tablename__ = 'estados_falla'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Fallas(db.Model):
    """🚨 Registro de fallas."""
    __tablename__ = 'fallas'
    id = db.Column(db.Integer, primary_key=True)
    fecha_reporte = db.Column(db.DateTime, default=datetime.utcnow)
    reportado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    tipo = db.Column(db.String(100))
    subtipo = db.Column(db.String(100))
    camara_id = db.Column(db.Integer, db.ForeignKey('camaras.id'))
    camara_afectada = db.Column(db.String(255))
    ubicacion = db.Column(db.Text)
    descripcion = db.Column(db.Text)
    impacto_visibilidad = db.Column(db.String(20))
    afecta_vision_nocturna = db.Column(db.Boolean)
    estado = db.Column(db.String(20), default='reportado')
    prioridad = db.Column(db.String(20))
    tecnico_asignado = db.Column(db.Integer, db.ForeignKey('equipo_tecnico.id'))
    fecha_inicio = db.Column(db.DateTime)
    fecha_resolucion = db.Column(db.DateTime)
    solucion = db.Column(db.Text)
    gravedad = db.Column(db.String(20))
    componente_afectado = db.Column(db.String(100))
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

class Fotografias(db.Model):
    """📷 Fotografías del sistema."""
    __tablename__ = 'fotografias'
    id = db.Column(db.Integer, primary_key=True)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    white_balance = db.Column(db.String(50))
    web_optimized_path = db.Column(db.String(255))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    url = db.Column(db.String(255))
    updated_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'))
    titulo = db.Column(db.String(255))
    tipo = db.Column(db.String(50))
    thumbnail_path = db.Column(db.String(255))
    tags = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    sort_order = db.Column(db.Integer)
    software_used = db.Column(db.String(100))
    quality_score = db.Column(db.Float)
    public_url = db.Column(db.String(255))
    preview_path = db.Column(db.String(255))
    original_camera = db.Column(db.String(100))
    notes = db.Column(db.Text)
    mime_type = db.Column(db.String(100))
    metadata_info = db.Column(db.Text)
    last_accessed = db.Column(db.DateTime)
    iso = db.Column(db.Integer)
    is_featured = db.Column(db.Boolean, default=False)
    gps_coordinates = db.Column(db.String(100))
    full_size_path = db.Column(db.String(255))
    focal_length = db.Column(db.Float)
    flash = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    falla_id = db.Column(db.Integer, db.ForeignKey('fallas.id'))
    exposure_time = db.Column(db.Float)
    entidad_tipo = db.Column(db.String(50))
    entidad_id = db.Column(db.Integer)
    download_count = db.Column(db.Integer, default=0)
    descripcion = db.Column(db.Text)
    deleted = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    compression_quality = db.Column(db.Integer)
    color_profile = db.Column(db.String(50))
    categoria = db.Column(db.String(100))
    capture_date = db.Column(db.DateTime)
    archivo = db.Column(db.String(255))
    approved_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    approval_date = db.Column(db.DateTime)
    aperture = db.Column(db.Float)
    access_count = db.Column(db.Integer, default=0)

class FuentesPoder(db.Model):
    """⚡ Fuentes de poder."""
    __tablename__ = 'fuentes_poder'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    serial = db.Column(db.String(100))
    tipo = db.Column(db.String(50))
    voltaje_entrada = db.Column(db.String(50))
    voltaje_salida = db.Column(db.String(50))
    corriente_salida = db.Column(db.String(50))
    potencia = db.Column(db.String(50))
    capacidad_ah = db.Column(db.Integer)
    tecnologia = db.Column(db.String(50))
    estado = db.Column(db.String(20), default='activo')
    ubicacion = db.Column(db.String(255))
    dependencia = db.Column(db.String(255))
    fecha_instalacion = db.Column(db.Date)
    fecha_mantenimiento = db.Column(db.Date)
    fecha_ultima_revision = db.Column(db.Date)
    fecha_proxima_revision = db.Column(db.Date)
    observaciones = db.Column(db.Text)
    garantia_meses = db.Column(db.Integer)
    proveedor = db.Column(db.String(100))
    costo = db.Column(db.Float)
    nivel_bateria = db.Column(db.String(20))
    temperatura_operacion = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class HistorialEstadoEquipo(db.Model):
    """📈 Historial de cambios de estado."""
    __tablename__ = 'historial_estado_equipo'
    id = db.Column(db.Integer, primary_key=True)
    equipo_tipo = db.Column(db.String(50), nullable=False)
    equipo_id = db.Column(db.Integer, nullable=False)
    estado_anterior = db.Column(db.String(50))
    estado_nuevo = db.Column(db.String(50))
    fecha_cambio = db.Column(db.DateTime, default=datetime.utcnow)
    motivo = db.Column(db.Text)

class Mantenimientos(db.Model):
    """🔧 Registro de mantenimientos."""
    __tablename__ = 'mantenimientos'
    id = db.Column(db.Integer, primary_key=True)
    fecha_programada = db.Column(db.DateTime)
    fecha_realizacion = db.Column(db.DateTime)
    tipo = db.Column(db.String(50))
    categoria = db.Column(db.String(50))
    equipo_gabinete = db.Column(db.String(255))
    ubicacion = db.Column(db.String(255))
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(20), default='programado')
    tecnico_responsable = db.Column(db.Integer, db.ForeignKey('equipo_tecnico.id'))
    materiales_utilizados = db.Column(db.Text)
    costo_aproximado = db.Column(db.Float)
    equipos_camaras_afectadas = db.Column(db.Text)
    tiempo_ejecucion = db.Column(db.Integer)
    observaciones = db.Column(db.Text)
    titulo = db.Column(db.String(255))
    equipment_id = db.Column(db.Integer)
    equipment_type = db.Column(db.String(50))
    camara_id = db.Column(db.Integer, db.ForeignKey('camaras.id'))
    nvr_id = db.Column(db.Integer, db.ForeignKey('nvr_dvr.id'))
    switch_id = db.Column(db.Integer, db.ForeignKey('switches.id'))
    ups_id = db.Column(db.Integer, db.ForeignKey('ups.id'))
    fuente_poder_id = db.Column(db.Integer, db.ForeignKey('fuentes_poder.id'))
    gabinete_id = db.Column(db.Integer, db.ForeignKey('gabinetes.id'))
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.id'))
    falla_id = db.Column(db.Integer, db.ForeignKey('fallas.id'))
    priority = db.Column(db.String(20))
    scheduled_start = db.Column(db.DateTime)
    scheduled_end = db.Column(db.DateTime)
    actual_start = db.Column(db.DateTime)
    duration_estimated = db.Column(db.Integer)
    duration_actual = db.Column(db.Integer)
    technician_id = db.Column(db.Integer, db.ForeignKey('equipo_tecnico.id'))
    supervisor_id = db.Column(db.Integer, db.ForeignKey('equipo_tecnico.id'))
    completion_criteria = db.Column(db.Text)
    maintenance_cost = db.Column(db.Float)
    parts_cost = db.Column(db.Float)
    labor_cost = db.Column(db.Float)
    downtime_minutes = db.Column(db.Integer)
    is_recurring = db.Column(db.Boolean, default=False)
    next_maintenance_date = db.Column(db.Date)
    quality_score = db.Column(db.Float)
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.Date)
    approved_by = db.Column(db.Integer, db.ForeignKey('equipo_tecnico.id'))
    approval_date = db.Column(db.DateTime)
    photos_taken = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

class NetworkConnections(db.Model):
    """🌐 Conexiones de red."""
    __tablename__ = 'network_connections'
    id = db.Column(db.Integer, primary_key=True)
    source_equipment_id = db.Column(db.Integer, nullable=False)
    source_equipment_type = db.Column(db.String(50), nullable=False)
    target_equipment_id = db.Column(db.Integer, nullable=False)
    target_equipment_type = db.Column(db.String(50), nullable=False)
    connection_type = db.Column(db.String(50))
    cable_type = db.Column(db.String(50))
    cable_length = db.Column(db.Float)
    port_source = db.Column(db.String(20))
    port_target = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    vlan_id = db.Column(db.Integer)
    bandwidth_limit = db.Column(db.Integer)
    latency_ms = db.Column(db.Float)
    packet_loss = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False)

class Nvrs(db.Model):
    """📺 NVRs adicionales."""
    __tablename__ = 'nvrs'
    id = db.Column(db.Integer, primary_key=True)
    canales = db.Column(db.Integer, default=16)
    almacenamiento_tb = db.Column(db.Float, default=1.0)

class Prioridades(db.Model):
    """🔝 Sistema de prioridades."""
    __tablename__ = 'prioridades'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class PuertosSwitch(db.Model):
    """🔌 Puertos de switch."""
    __tablename__ = 'puertos_switch'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    serial = db.Column(db.String(100))
    puertos_total = db.Column(db.Integer, default=24)
    puertos_usados = db.Column(db.Integer, default=0)
    puertos_libres = db.Column(db.Integer, default=24)
    puertos_gigabit = db.Column(db.Integer, default=24)
    puertos_10g = db.Column(db.Integer, default=0)
    puertos_sfp = db.Column(db.Integer, default=0)
    velocidad_puertos = db.Column(db.String(20), default='1Gbps')
    protocolos_soportados = db.Column(db.Text)
    table_mac = db.Column(db.Integer)
    memoria_buffer = db.Column(db.String(50))
    capacidad_switching = db.Column(db.String(50))
    apilable = db.Column(db.Boolean, default=False)
    poe_support = db.Column(db.Boolean, default=False)
    poe_puertos = db.Column(db.Integer, default=0)
    poe_presupuesto = db.Column(db.Float)
    consumo_energia = db.Column(db.String(20))
    ip_management = db.Column(db.String(15))
    vlan_support = db.Column(db.Boolean, default=True)
    protocolos_gestion = db.Column(db.Text)
    interfaz_web = db.Column(db.Boolean, default=True)
    cli_support = db.Column(db.Boolean, default=True)
    estado = db.Column(db.String(20), default='activo')
    ubicacion = db.Column(db.String(255))
    temperatura_sistema = db.Column(db.String(20))
    uso_ancho_banda = db.Column(db.Float)
    errores_puertos = db.Column(db.Integer, default=0)
    fecha_instalacion = db.Column(db.Date)
    fecha_mantenimiento = db.Column(db.Date)
    fecha_ultimo_firmware = db.Column(db.Date)
    fecha_proximo_mantenimiento = db.Column(db.Date)
    observaciones = db.Column(db.Text)
    garantia_meses = db.Column(db.Integer)
    proveedor = db.Column(db.String(100))
    costo = db.Column(db.Float)
    version_firmware = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class Roles(db.Model):
    """👥 Sistema de roles."""
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class UsuarioLogs(db.Model):
    """📋 Logs de usuarios."""
    __tablename__ = 'usuario_logs'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False)

# ========================================
# 🔐 CONFIGURACIÓN FLASK-LOGIN
# ========================================

@login_manager.user_loader
def load_user(user_id):
    """🔍 Función requerida por Flask-Login para recargar al usuario."""
    try:
        return Usuario.query.get(int(user_id))
    except (ValueError, TypeError):
        return None

# ========================================
# 🏭 FACTORY DE APLICACIÓN FLASK
# ========================================

def create_app():
    """🏗️ Patrón de Fábrica de Aplicaciones para inicializar Flask."""
    
    app = Flask(__name__)
    
    try:
        # 1. 🎯 CARGAR CONFIGURACIÓN
        app_config = get_config()
        app.config.from_object(app_config)

        logger.info(f"🚀 App iniciada con SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI'][:30]}...")
        logger.info(f"🔑 SECRET_KEY configurada: {bool(app.config['SECRET_KEY'])}")
        
        # 2. 🔧 INICIALIZAR EXTENSIONES
        db.init_app(app)
        login_manager.init_app(app)
        
        # Configurar Flask-Login
        login_manager.login_view = 'login'
        login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."
        login_manager.login_message_category = "info"
        login_manager.session_protection = "strong"

        # 3. 📋 CREAR TABLAS SI NO EXISTEN
        with app.app_context():
            logger.info("🏗️ Verificando tablas de base de datos...")
            db.create_all()
            logger.info("✅ Tablas verificadas/creadas exitosamente")
            
            # Verificar usuario existente para credenciales de producción
            try:
                user_email = 'charles.jelvez@ufrontera.cl'
                if not Usuario.query.filter_by(username=user_email).first():
                    admin = Usuario(
                        username=user_email,  # USUARIO = EMAIL COMPLETO
                        email=user_email,
                        full_name='Charles Jelvez - Administrador UFRO',
                        role='ADMIN'
                    )
                    admin.set_password('Vivita0468')
                    db.session.add(admin)
                    db.session.commit()
                    logger.info("🎉 Usuario Charles Jelvez creado: charles.jelvez@ufrontera.cl")
                else:
                    logger.info("ℹ️ Usuario Charles Jelvez ya existe")
            except Exception as e:
                logger.warning(f"⚠️ Error al verificar/crear usuario admin: {e}")

        # 4. 🛣️ DEFINIR RUTAS
        register_routes(app)
        
        # 5. 📝 MANEJADORES DE ERROR
        register_error_handlers(app)

        logger.info("🎉 Aplicación Flask inicializada correctamente")
        return app
        
    except Exception as e:
        logger.error(f"❌ Error crítico al inicializar aplicación: {e}")
        raise

def register_routes(app):
    """🛣️ Registrar todas las rutas de la aplicación."""
    
    @app.route('/')
    def index():
        """🏠 Ruta de inicio - Dashboard principal."""
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        # 📊 Obtener estadísticas del dashboard
        try:
            stats = {
                'total_camaras': Camara.query.count(),
                'camaras_activas': Camara.query.filter_by(activo=True).count(),
                'total_ubicaciones': Ubicacion.query.count(),
                'ubicaciones_activas': Ubicacion.query.filter_by(activo=True).count(),
                'total_switches': Switch.query.count(),
                'total_nvr_dvr': NvrDvr.query.count(),
                'total_gabinetes': Gabinete.query.count(),
                'total_ups': Ups.query.count(),
                'usuarios_activos': Usuario.query.filter_by(activo=True).count()
            }
            
            logger.debug(f"📊 Estadísticas obtenidas: {stats}")
            
        except Exception as e:
            logger.error(f"❌ Error al obtener estadísticas: {e}")
            flash("Error al cargar estadísticas del dashboard.", "warning")
            stats = {key: 0 for key in ['total_camaras', 'camaras_activas', 'total_ubicaciones', 'ubicaciones_activas', 'total_switches', 'total_nvr_dvr', 'total_gabinetes', 'total_ups', 'usuarios_activos']}

        return render_template('dashboard.html', 
                                stats=stats,
                                user=current_user)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """🔑 Maneja el inicio de sesión."""
        if current_user.is_authenticated:
            logger.info(f"👤 Usuario {current_user.username} ya autenticado, redirigiendo a dashboard")
            return redirect(url_for('index'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not username or not password:
                flash('Por favor ingresa usuario y contraseña.', 'warning')
                return render_template('login.html', title='Iniciar Sesión')
            
            try:
                logger.info(f"🔍 Intentando login para usuario: {username}")
                user = Usuario.query.filter_by(username=username).first()
                logger.info(f"👤 Usuario encontrado: {bool(user)}")

                if user and user.check_password(password):
                    logger.info(f"🔐 Contraseña verificada para usuario: {user.username}")
                    logger.info(f"🟢 Estado activo del usuario: {user.activo}")
                    
                    if not user.activo:
                        flash('Tu cuenta está desactivada. Contacta al administrador.', 'danger')
                        return render_template('login.html', title='Iniciar Sesión')
                    
                    logger.info(f"🔑 Iniciando sesión para usuario: {user.username}")
                    login_user(user, remember=True)
                    logger.info(f"✅ Login exitoso para usuario: {user.username}")
                    
                    next_page = request.args.get('next')
                    flash(f'¡Bienvenido, {user.username}!', 'success')
                    logger.info(f"📄 Redirigiendo a página: {next_page or 'index'}")
                    return redirect(next_page or url_for('index'))
                else:
                    logger.warning(f"❌ Intento de login fallido para usuario: {username}")
                    flash('Credenciales inválidas. Por favor, verifica tu usuario y contraseña.', 'danger')
            
            except Exception as e:
                logger.error(f"❌ Error durante login: {e}")
                logger.error(f"📋 Tipo de error: {type(e).__name__}")
                import traceback
                logger.error(f"🔍 Traceback: {traceback.format_exc()}")
                flash('Error interno del servidor. Intenta nuevamente.', 'danger')

        return render_template('login.html', title='Iniciar Sesión')

    @app.route('/logout')
    @login_required
    def logout():
        """🚪 Cierra la sesión del usuario."""
        username = current_user.username
        logout_user()
        logger.info(f"🚪 Logout exitoso para usuario: {username}")
        flash('Has cerrado sesión exitosamente.', 'info')
        return redirect(url_for('login'))

    @app.route('/test-db-connection')
    def test_db():
        """🧪 Ruta para probar la conexión a la base de datos."""
        try:
            # Prueba simple: contar registros
            stats = {
                'usuarios': Usuario.query.count(),
                'ubicaciones': Ubicacion.query.count(),
                'camaras': Camara.query.count(),
                'switches': Switch.query.count(),
                'nvr_dvr': NvrDvr.query.count(),
                'gabinetes': Gabinete.query.count(),
                'ups': Ups.query.count()
            }
            
            logger.info(f"🧪 Test DB exitoso: {stats}")
            return {
                'status': 'success',
                'message': 'Conexión a base de datos exitosa',
                'stats': stats
            }, 200
            
        except Exception as e:
            logger.error(f"❌ Fallo en test de conexión DB: {e}")
            return {
                'status': 'error',
                'message': f'Error de conexión: {str(e)}'
            }, 500

    @app.route('/health')
    def health():
        """❤️ Ruta de health check para Railway."""
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}

def register_error_handlers(app):
    """📝 Registrar manejadores de errores."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """🔍 Manejador para páginas no encontradas."""
        logger.warning(f"🔍 404 - Página no encontrada: {request.path}")
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """⚠️ Manejador para errores internos."""
        logger.error(f"💥 500 - Error interno: {error}")
        db.session.rollback()
        return render_template('500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        """🚫 Manejador para acceso denegado."""
        logger.warning(f"🚫 403 - Acceso denegado: {request.path}")
        return render_template('403.html'), 403

# ========================================
# 🚀 INSTANCIA PARA GUNICORN
# ========================================

# ✅ CORRECCIÓN CRÍTICA: Crear instancia de app para Gunicorn
# Esto es lo que Gunicorn necesita para ejecutar app:app
try:
    app = create_app()
    logger.info("✅ Instancia de app creada para Gunicorn")
except Exception as e:
    logger.error(f"❌ Error al crear instancia de app: {e}")
    # Crear app básica como fallback
    app = Flask(__name__)
    logger.warning("⚠️ Usando app básica como fallback")

# ========================================
# 🚀 PUNTO DE ENTRADA PRINCIPAL
# ========================================

if __name__ == '__main__':
    try:
        logger.info("🚀 Iniciando aplicación Sistema de Cámaras UFRO...")
        
        # Crear aplicación
        app = create_app()
        
        # Información de inicio
        port = int(os.getenv('PORT', 5000))
        logger.info(f"🌐 Servidor iniciando en puerto {port}")
        logger.info(f"🔗 URL: http://localhost:{port}")
        logger.info(f"🔑 Login inicial: charles.jelvez@ufrontera.cl / Vivita0468")
        
        # Ejecutar en modo desarrollo o según configuración
        debug_mode = app.config.get('DEBUG', False)
        logger.info(f"🛠️ Modo debug: {debug_mode}")
        
        # Ejecutar aplicación
        app.run(
            host='0.0.0.0', 
            port=port, 
            debug=debug_mode,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("👋 Aplicación interrumpida por el usuario")
    except Exception as e:
        logger.error(f"💥 Error fatal al ejecutar aplicación: {e}")
        raise