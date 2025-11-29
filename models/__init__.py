"""
Inicialización del módulo models - Sistema de Gestión de Cámaras UFRO

Este archivo reexporta todos los modelos y configuraciones de la base de datos
de forma segura, evitando dependencias circulares mediante imports diferidos.

PROBLEMA SOLUCIONADO:
- Eliminación de dependencia circular donde models/__init__.py importaba Usuario
  y usuario.py importaba db desde models/__init__.py
- Creación de database.py como punto central de inicialización de SQLAlchemy
- Lazy imports para evitar cargar todos los modelos al inicializar
"""

import logging
from .database import db

# Configurar logging
logger = logging.getLogger(__name__)

def init_models():
    """
    📦 Importar y registrar todos los modelos SQLAlchemy.
    
    Este método importa explícitamente cada clase de modelo para que
    SQLAlchemy las registre correctamente. Usa imports diferidos para
    evitar dependencias circulares.
    """
    logger.info("🔄 Importando modelos desde archivos individuales...")
    
    try:
        # Modelos principales del sistema - imports diferidos
        from .usuario import Usuario
        logger.info("✅ Usuario importado")
        
        from .camara import Camara
        logger.info("✅ Camara importada")
        
        from .base import Ubicacion
        logger.info("✅ Ubicacion importada")
        
        from .falla import Falla
        logger.info("✅ Falla importada")
        
        from .falla_comentario import FallaComentario
        logger.info("✅ FallaComentario importada")
        
        from .switch import Switch
        logger.info("✅ Switch importado")
        
        from .nvr import NVR
        logger.info("✅ NVR importado")
        
        # Alias para compatibilidad
        NvrDvr = NVR
        DVR = NVR
        logger.info("✅ NvrDvr y DVR definidos como alias de NVR")
        
        from .ups import UPS
        logger.info("✅ UPS importado")
        
        from .gabinete import Gabinete
        logger.info("✅ Gabinete importado")
        
        from .fuente_poder import FuentePoder
        logger.info("✅ FuentePoder importada")
        
        from .mantenimiento import Mantenimiento
        logger.info("✅ Mantenimiento importado")
        
        from .fotografia import Fotografia
        logger.info("✅ Fotografia importada")
        
        from .historial_estado_equipo import HistorialEstadoEquipo
        logger.info("✅ HistorialEstadoEquipo importada")
        
        from .catalogo_tipo_falla import CatalogoTipoFalla
        logger.info("✅ CatalogoTipoFalla importada")
        
        from .equipo_tecnico import EquipoTecnico
        logger.info("✅ EquipoTecnico importado")
        
        from .usuario_logs import UsuarioLog
        logger.info("✅ UsuarioLog importado")
        
        logger.info("🎉 Todos los modelos importados exitosamente")
        
        # Retornar todas las clases importadas
        return (
            Usuario, Camara, Ubicacion, NVR, DVR, Switch, UPS, Gabinete, 
            FuentePoder, Falla, Mantenimiento, Fotografia, 
            HistorialEstadoEquipo, CatalogoTipoFalla, EquipoTecnico,
            FallaComentario, UsuarioLog
        )
        
    except ImportError as e:
        logger.error(f"❌ Error al importar modelos: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Error inesperado en init_models: {e}")
        raise

def init_db(app):
    """
    🗄️ Inicializar base de datos con app Flask.
    
    Args:
        app: Instancia de Flask
    """
    global db
    db.init_app(app)
    
    # Importar todos los modelos
    try:
        models = init_models()
        logger.info(f"📊 {len(models)} modelos registrados con SQLAlchemy")
    except Exception as e:
        logger.error(f"❌ Fallo al registrar modelos: {e}")
        raise
    
    # Crear todas las tablas
    with app.app_context():
        try:
            logger.info("🏗️ Creando tablas de base de datos...")
            db.create_all()
            logger.info("✅ Tablas creadas exitosamente")
            
            # Crear usuario admin si no existe
            try:
                from .usuario import Usuario
                if not Usuario.query.filter_by(username='admin').first():
                    admin = Usuario(
                        username='admin',
                        email='admin.sistema@ufrontera.cl',
                        full_name='Administrador Sistema',
                        role='ADMIN'
                    )
                    admin.set_password('admin123')
                    db.session.add(admin)
                    db.session.commit()
                    logger.info("✅ Usuario admin creado: admin / admin123")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo crear usuario admin: {e}")
                
        except Exception as e:
            logger.error(f"❌ Error al crear tablas: {e}")
            raise

# ========================================
# 🔧 FUNCIONES DE IMPORT SEGURAS (LAZY IMPORTS)
# ========================================

def get_usuario():
    """Importa Usuario de forma segura (lazy import)."""
    from .usuario import Usuario
    return Usuario

def get_camara():
    """Importa Camara de forma segura (lazy import)."""
    from .camara import Camara
    return Camara

def get_falla():
    """Importa Falla de forma segura (lazy import)."""
    from .falla import Falla
    return Falla

def get_usuario_log():
    """Importa UsuarioLog de forma segura (lazy import)."""
    from .usuario_logs import UsuarioLog
    return UsuarioLog

# ========================================
# 🏷️ EXPORTACIONES PRINCIPALES
# ========================================

# Importar SQLAlchemy instance
__all__ = [
    # Base de datos
    'db',
    'init_db', 'init_models',
    
    # Modelos principales
    'Usuario', 'Camara', 'Falla', 'FallaComentario', 'Switch', 'NVR', 'UPS',
    'FuenteAlimentacion', 'Gabinete', 'Ubicacion', 'UsuarioLog', 'Mantenimiento',
    
    # Funciones de importación segura
    'get_usuario', 'get_camara', 'get_falla', 'get_usuario_log',
    
    # Enums disponibles
    'EquipmentStatus', 'EstadoCamara',
    
    # Mixins y clases base
    'ModelMixin', 'TimestampedModel', 'BaseModelMixin', 'BaseModel',
]

logger.info("🎉 models/__init__.py inicializado correctamente - dependencia circular eliminada")

# Importar modelos principales al nivel del módulo
try:
    from .usuario import Usuario
    from .camara import Camara
    from .falla import Falla
    from .falla_comentario import FallaComentario
    from .switch import Switch
    from .nvr import NVR
    from .ups import UPS
    from .fuente_alimentacion import FuenteAlimentacion
    from .gabinete import Gabinete
    from .ubicacion import Ubicacion
    from .usuario_log import UsuarioLog
    from .mantenimiento import Mantenimiento
    logger.debug("✅ Modelos principales importados al nivel del módulo")
except ImportError as e:
    logger.debug(f"⚠️ Algunos modelos no están disponibles: {e}")

# Importar enums disponibles al nivel del módulo (solo los seguros)
try:
    from .enums.equipment_status import EquipmentStatus
    from .enums.estado_camara import EstadoCamara
    logger.debug("✅ Enums principales importados")
except ImportError as e:
    logger.debug(f"⚠️ Algunos enums no están disponibles: {e}")

try:
    from .base import ModelMixin, TimestampedModel, BaseModelMixin, BaseModel
    logger.debug("✅ Mixins y clases base importados")
except ImportError as e:
    logger.debug(f"⚠️ Mixins no están disponibles: {e}")