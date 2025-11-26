"""
Configuración de Blueprints para el Sistema de Gestión de Equipos de Red
"""
from flask import Blueprint

# Crear blueprints para cada módulo
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
api_bp = Blueprint('api', __name__, url_prefix='/api')
fallas_bp = Blueprint('fallas', __name__, url_prefix='/fallas')
camaras_bp = Blueprint('camaras', __name__, url_prefix='/camaras')
nvr_bp = Blueprint('nvr', __name__, url_prefix='/nvr')
switches_bp = Blueprint('switches', __name__, url_prefix='/switches')
ups_bp = Blueprint('ups', __name__, url_prefix='/ups')
fuentes_bp = Blueprint('fuentes', __name__, url_prefix='/fuentes')
gabinetes_bp = Blueprint('gabinetes', __name__, url_prefix='/gabinetes')
mantenimientos_bp = Blueprint('mantenimientos', __name__, url_prefix='/mantenimientos')

def register_blueprints(app):
    """
    Registrar todos los blueprints en la aplicación Flask
    """
    from . import auth, dashboard, api, fallas, camaras, nvr, switches, ups, fuentes, gabinetes, mantenimientos
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(fallas_bp)
    app.register_blueprint(camaras_bp)
    app.register_blueprint(nvr_bp)
    app.register_blueprint(switches_bp)
    app.register_blueprint(ups_bp)
    app.register_blueprint(fuentes_bp)
    app.register_blueprint(gabinetes_bp)
    app.register_blueprint(mantenimientos_bp)