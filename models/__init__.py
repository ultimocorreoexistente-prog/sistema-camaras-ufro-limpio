import os
import logging
from flask_sqlalchemy import SQLAlchemy

# Configurar logging para todo el módulo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar SQLAlchemy
db = SQLAlchemy()

def init_models():
    """
    📦 Importar y registrar todos los modelos SQLAlchemy.
    
    Este método importa explícitamente cada clase de modelo para que
    SQLAlchemy las registre correctamente y estén disponibles para import.
    """
    
    logger.info("🔄 Importando modelos desde archivos individuales...")
    
    try:
        # Modelos principales del sistema
        from .usuario import Usuario
        logger.info("✅ Usuario importado")
        
        from .camara import Camara
        logger.info("✅ Camara importada desde camara.py")
        
        from .base import Ubicacion
        logger.info("✅ Ubicacion importada")
        
        from .falla import Falla
        logger.info("✅ Falla importada")
        
        from .falla_comentario import FallaComentario
        logger.info("✅ FallaComentario importada")
        
        from .switch import Switch
        logger.info("✅ Switch importado")
        
        # NVR se importa directamente
        from .nvr import NVR
        logger.info("✅ NVR importado")
        # Alias para NvrDvr (mantener compatibilidad)
        NvrDvr = NVR
        logger.info("✅ NvrDvr definido como alias de NVR")
        
        from .ups import UPS  # Fixed: UPS class name
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
        
        # DVR también es alias de NVR (mantener compatibilidad)
        DVR = NVR
        logger.info("✅ DVR definido como alias de NVR")
        has_dvr = False  # No hay clase DVR separada
        
        logger.info("🎉 Todos los modelos importados exitosamente")
        
        # Retornar todas las clases importadas
        return (
            Usuario, Camara, Ubicacion, NVR, 
            DVR, Switch, UPS, Gabinete, 
            FuentePoder, Falla, Mantenimiento, Fotografia, 
            HistorialEstadoEquipo, CatalogoTipoFalla, EquipoTecnico
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
# 🔧 EXPORTACIONES PRINCIPALES
# ========================================

# Importar SQLAlchemy instance

# ========================================
# 🏷️ IMPORTACIONES DIRECTAS (Para compatibilidad)
# ========================================

logger.info("🔄 Inicializando imports directos en models/__init__.py...")

try:
    # Importaciones principales
    from .usuario import Usuario
    logger.debug("✅ Usuario importado directamente")
    
    from .camara import Camara
    logger.debug("✅ Camara importado directamente desde camara.py")
    
    from .base import Ubicacion
    logger.debug("✅ Ubicacion importado directamente")
    
    from .switch import Switch  # ✅ CORREGIDO: importa desde switch.py, no base.py
    logger.debug("✅ Switch importado directamente")
    
    from .nvr import NVR
    logger.debug("✅ NVR importado directamente")
    
    # Alias para NvrDvr y DVR (mantener compatibilidad)
    NvrDvr = NVR
    DVR = NVR
    logger.debug("✅ NvrDvr y DVR definidos como alias de NVR")
    
    from .ups import UPS  # Fixed: UPS class name
    logger.debug("✅ UPS importado directamente")
    
    from .gabinete import Gabinete
    logger.debug("✅ Gabinete importado directamente")
    
    from .fuente_poder import FuentePoder
    logger.debug("✅ FuentePoder importada directamente")
    
    from .falla import Falla
    logger.debug("✅ Falla importado directamente")
    
    from .mantenimiento import Mantenimiento
    logger.debug("✅ Mantenimiento importado directamente")
    
    from .fotografia import Fotografia
    logger.debug("✅ Fotografia importado directamente")
    
    from .historial_estado_equipo import HistorialEstadoEquipo
    logger.debug("✅ HistorialEstadoEquipo importado directamente")
    
    from .catalogo_tipo_falla import CatalogoTipoFalla
    logger.debug("✅ CatalogoTipoFalla importado directamente")
    
    from .equipo_tecnico import EquipoTecnico
    logger.debug("✅ EquipoTecnico importado directamente")
    
    from .usuario_logs import UsuarioLog
    logger.debug("✅ UsuarioLog importado directamente")
    
    # Importar enums
    from .enums.equipment_status import EquipmentStatus
    logger.debug("✅ EquipmentStatus importado directamente")
    globals()['EquipmentStatus'] = EquipmentStatus  # Hacer global
    
    from .enums.estado_camara import EstadoCamara
    logger.debug("✅ EstadoCamara importado directamente")
    globals()['EstadoCamara'] = EstadoCamara  # Hacer global
    
    # Importar desde base.py - Otros enums si existen
    try:
        from .base import RolEnum, TipoUbicacion, EstadoTicket, PrioridadEnum
        logger.debug("✅ Enums adicionales importados desde base.py")
    except ImportError as e:
        logger.debug(f"⚠️ Algunos enums no están en base.py: {e}")
        # Definir alias si no están disponibles
        RolEnum = None
        TipoUbicacion = None
        EstadoTicket = None
        PrioridadEnum = None
    
    # Importar desde base.py - Mixins y clases base
    from .base import ModelMixin, TimestampedModel, BaseModelMixin, BaseModel
    logger.debug("✅ Mixins y clases base importados directamente desde base.py")
    
    # Importar desde base.py - Modelos adicionales
    from .base import Rol, EventoCamara, Ticket, TrazabilidadMantenimiento, Inventario
    logger.debug("✅ Modelos adicionales importados directamente desde base.py")
    
    logger.info("🎉 models/__init__.py inicializado correctamente")
    
except ImportError as e:
    logger.error(f"❌ Error al importar clases directamente: {e}")
    logger.error("❌ Verifica que todos los archivos de modelo existan y tengan las clases correctas")
except Exception as e:
    logger.error(f"❌ Error inesperado en imports directos: {e}")

# ✅ CRITICAL: Exportar todas las clases para que sean importables
__all__ = [
    'db',
    'init_db', 'init_models',
    # Enums del sistema (solo los que existan)
    'EquipmentStatus', 'EstadoCamara',
    # Mixins y clases base
    'ModelMixin', 'TimestampedModel', 'BaseModelMixin', 'BaseModel',
    # Modelos principales
    'Usuario', 'Camara', 'Ubicacion', 'Falla', 'FallaComentario', 'Switch', 
    'NVR', 'NvrDvr', 'DVR', 'UPS', 'Gabinete', 'FuentePoder', 'Mantenimiento', 
    'Fotografia', 'HistorialEstadoEquipo', 'CatalogoTipoFalla', 'EquipoTecnico',
    'UsuarioLog',  # Logs de auditoría
]

# Fin del archivo models/__init__.py