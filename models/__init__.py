import os
import logging

# Configurar logging para todo el módulo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from flask_sqlalchemy import SQLAlchemy

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
        logger.info("✅ Camara importada")
        
        from .ubicacion import Ubicacion
        logger.info("✅ Ubicacion importada")
        
        from .falla import Falla
        logger.info("✅ Falla importada")
        
        from .falla_comentario import FallaComentario
        logger.info("✅ FallaComentario importada")
        
        from .switch import Switch
        logger.info("✅ Switch importado")
        
        from .nvr import NvrDvr  # Posible que NVR y DVR estén en el mismo archivo
        logger.info("✅ NvrDvr importado")
        
        from .ups import Ups
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
        
        # Verificar si DVR existe como clase separada en nvr.py
        try:
            from .nvr import DVR
            logger.info("✅ DVR importado")
            has_dvr = True
        except ImportError:
            logger.warning("⚠️ DVR no encontrada como clase separada, usando NvrDvr como DVR")
            DVR = NvrDvr  # Alias
            has_dvr = False
        
        logger.info("🎉 Todos los modelos importados exitosamente")
        
        # Retornar todas las clases importadas
        return (
            Usuario, Camara, Ubicacion, NVR if not has_dvr else NvrDvr, 
            DVR if has_dvr else NvrDvr, Switch, Ups, Gabinete, 
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
__all__ = [
    'db',
    'init_db', 
    'init_models',
    # Clases principales para importación directa
    'Usuario', 
    'Camara', 
    'Ubicacion', 
    'NVR', 
    'DVR',
    'Switch', 
    'UPS', 
    'Gabinete', 
    'FuentePoder', 
    'Falla', 
    'Mantenimiento', 
    'Fotografia', 
    'HistorialEstadoEquipo', 
    'CatalogoTipoFalla', 
    'EquipoTecnico'
]

# ========================================
# 🏷️ IMPORTACIONES DIRECTAS (Para compatibilidad)
# ========================================

logger.info("🔄 Inicializando imports directos en models/__init__.py...")

try:
    # Importaciones principales
    from .usuario import Usuario
    logger.debug("✅ Usuario importado directamente")
    
    from .camara import Camara
    logger.debug("✅ Camara importada directamente")
    
    from .ubicacion import Ubicacion
    logger.debug("✅ Ubicacion importada directamente")
    
    from .switch import Switch
    logger.debug("✅ Switch importado directamente")
    
    from .nvr import NvrDvr as NVR
    logger.debug("✅ NVR (NvrDvr) importado directamente")
    
    # Alias para DVR (puede ser la misma clase que NVR)
    DVR = NVR
    logger.debug("✅ DVR definido como alias de NVR")
    
    from .ups import Ups
    logger.debug("✅ UPS importado directamente")
    
    from .gabinete import Gabinete
    logger.debug("✅ Gabinete importado directamente")
    
    from .fuente_poder import FuentePoder
    logger.debug("✅ FuentePoder importada directamente")
    
    from .falla import Falla
    logger.debug("✅ Falla importada directamente")
    
    from .mantenimiento import Mantenimiento
    logger.debug("✅ Mantenimiento importado directamente")
    
    from .fotografia import Fotografia
    logger.debug("✅ Fotografia importada directamente")
    
    from .historial_estado_equipo import HistorialEstadoEquipo
    logger.debug("✅ HistorialEstadoEquipo importada directamente")
    
    from .catalogo_tipo_falla import CatalogoTipoFalla
    logger.debug("✅ CatalogoTipoFalla importada directamente")
    
    from .equipo_tecnico import EquipoTecnico
    logger.debug("✅ EquipoTecnico importado directamente")
    
    logger.info("🎉 models/__init__.py inicializado correctamente")
    
except ImportError as e:
    logger.error(f"❌ Error al importar clases directamente: {e}")
    logger.error("❌ Verifica que todos los archivos de modelo existan y tengan las clases correctas")
except Exception as e:
    logger.error(f"❌ Error inesperado en imports directos: {e}")

# Fin del archivo models/__init__.py