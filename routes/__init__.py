"""
Configuración de Blueprints para el Sistema de Gestión de Cámaras UFRO
Versión 3.0 Híbrida - Compatible con importación modular
"""

# Los blueprints se importan directamente desde cada módulo individual
# para evitar duplicación y mantener la estructura modular

# Esta importación permite que los módulos puedan importar sus propios blueprints
# sin necesidad de estar definidos en __init__.py

def get_blueprint_info():
    """
    Retorna información sobre los blueprints disponibles
    """
    return {
        'auth': 'Blueprint de autenticación (login, logout, registro)',
        'dashboard': 'Blueprint del dashboard principal con estadísticas',
        'api': 'Blueprint de APIs RESTful',
        'fallas': 'Blueprint de gestión de fallas',
        'camaras': 'Blueprint de gestión de cámaras',
        'nvr': 'Blueprint de gestión de NVRs',
        'switches': 'Blueprint de gestión de switches',
        'ups': 'Blueprint de gestión de UPS',
        'fuentes': 'Blueprint de gestión de fuentes de poder',
        'gabinetes': 'Blueprint de gestión de gabinetes',
        'mantenimientos': 'Blueprint de gestión de mantenimientos'
    }