"""
Lógica de análisis de impacto de fallas (FIA - Failure Impact Analysis)
Sistema de Trazabilidad de Cámaras UFRO

Este módulo contiene la lógica para analizar el impacto de fallas en equipos
y conexiones de red, determinando qué equipos se ven afectados cuando falla
un componente específico del sistema.
"""

from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

# Importar modelos
from models import (
    NetworkConnection, Camara, Switch, NVR, UPS, FuentePoder, Gabinete, 
    Equipo, Falla
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImpactoEquipo:
    """Representa un equipo afectado por una falla"""
    
    def __init__(self, equipo_id: int, tipo_equipo: str, nombre: str, 
                 razon_impacto: str, severidad: str = "MEDIA"):
        self.id = equipo_id
        self.tipo = tipo_equipo
        self.nombre = nombre
        self.razon_impacto = razon_impacto
        self.severidad = severidad
        self.conexiones_perdidas = []
        self.equipos_dependientes = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'tipo': self.tipo,
            'nombre': self.nombre,
            'razon_impacto': self.razon_impacto,
            'severidad': self.severidad,
            'conexiones_perdidas': self.conexiones_perdidas,
            'equipos_dependientes': [eq.to_dict() if hasattr(eq, 'to_dict') else str(eq) 
                                   for eq in self.equipos_dependientes]
        }
    
    def __repr__(self):
        return f"<ImpactoEquipo(id={self.id}, tipo='{self.tipo}', nombre='{self.nombre}')>"


def analizar_impacto(tipo_activo: str, id_activo: int, db_session: Session) -> List[Dict[str, Any]]:
    """
    Analiza el impacto de una falla en un activo específico
    
    Args:
        tipo_activo: Tipo del activo fallido ('camara', 'switch', 'nvr', 'conexion_red', etc.)
        id_activo: ID del activo fallido
        db_session: Sesión de base de datos SQLAlchemy
    
    Returns:
        List[Dict[str, Any]]: Lista de equipos afectados con detalles del impacto
    """
    logger.info(f"Iniciando análisis de impacto para {tipo_activo} ID {id_activo}")
    
    equipos_afectados = []
    conexiones_perdidas = set()
    
    try:
        # 1. ANÁLISIS POR TIPO DE ACTIVO
        if tipo_activo == 'conexion_red':
            equipos_afectados, conexiones_perdidas = _analizar_falla_conexion(id_activo, db_session)
        elif tipo_activo == 'camara':
            equipos_afectados, conexiones_perdidas = _analizar_falla_camara(id_activo, db_session)
        elif tipo_activo in ['switch', 'nvr', 'ups', 'fuente_poder', 'gabinete']:
            equipos_afectados, conexiones_perdidas = _analizar_falla_equipo(tipo_activo, id_activo, db_session)
        else:
            logger.warning(f"Tipo de activo no reconocido: {tipo_activo}")
            return []
        
        # 2. ANÁLISIS DE DEPENDENCIAS INDIRECTAS
        equipos_afectados = _analizar_dependencias_indirectas(equipos_afectados, db_session)
        
        # 3. EVALUACIÓN DE SEVERIDAD
        equipos_afectados = _evaluar_severidad_impacto(equipos_afectados, tipo_activo, id_activo)
        
        # 4. CONVERSIÓN A DICCIONARIOS
        resultado = [equipo.to_dict() for equipo in equipos_afectados]
        
        logger.info(f"Análisis completado: {len(resultado)} equipos afectados")
        return resultado
        
    except Exception as e:
        logger.error(f"Error durante análisis de impacto: {str(e)}")
        # Retornar información básica de error
        return [{
            'error': 'No se pudo completar el análisis de impacto',
            'detalle': str(e),
            'equipo_afectado_directo': {'id': id_activo, 'tipo': tipo_activo}
        }]


def _analizar_falla_conexion(id_conexion: int, db_session: Session) -> tuple:
    """
    Analiza el impacto cuando falla una conexión de red
    
    Args:
        id_conexion: ID de la conexión
        db_session: Sesión de base de datos
    
    Returns:
        tuple: (equipos_afectados, conexiones_perdidas)
    """
    equipos_afectados = []
    conexiones_perdidas = set()
    
    # Buscar la conexión
    conexion = db_session.query(NetworkConnection).filter_by(id=id_conexion).first()
    if not conexion:
        logger.warning(f"Conexión ID {id_conexion} no encontrada")
        return equipos_afectados, conexiones_perdidas
    
    # Si la conexión no estaba activa, el impacto es mínimo
    if not conexion.activa:
        logger.info(f"Conexión {id_conexion} ya estaba inactiva, impacto mínimo")
        return equipos_afectados, conexiones_perdidas
    
    # Determinar equipos origen y destino
    equipos_impactados = []
    
    # Equipo origen
    if conexion.equipo_origen_id:
        equipo_origen = _obtener_equipo_por_tipo(
            conexion.equipo_origen_id, 
            conexion.equipo_origen_tipo, 
            db_session
        )
        if equipo_origen:
            equipos_impactados.append(equipo_origen)
    
    # Equipo destino
    if conexion.equipo_destino_id:
        equipo_destino = _obtener_equipo_por_tipo(
            conexion.equipo_destino_id, 
            conexion.equipo_destino_tipo, 
            db_session
        )
        if equipo_destino:
            equipos_impactados.append(equipo_destino)
    
    # Crear objetos de impacto
    razon = f"Pérdida de conexión {conexion.tipo_conexion.value}"
    if conexion.descripcion:
        razon += f": {conexion.descripcion}"
    
    for equipo in equipos_impactados:
        impacto = ImpactoEquipo(
            equipo_id=equipo.id,
            tipo_equipo=equipo.__class__.__name__.lower(),
            nombre=getattr(equipo, 'nombre', str(equipo)),
            razon_impacto=razon,
            severidad="ALTA" if isinstance(equipo, (Camara, NVR)) else "MEDIA"
        )
        impacto.conexiones_perdidas.append({
            'conexion_id': id_conexion,
            'tipo': conexion.tipo_conexion.value,
            'puerto_origen': conexion.puerto_origen,
            'puerto_destino': conexion.puerto_destino
        })
        equipos_afectados.append(impacto)
    
    conexiones_perdidas.add(id_conexion)
    return equipos_afectados, conexiones_perdidas


def _analizar_falla_camara(id_camara: int, db_session: Session) -> tuple:
    """
    Analiza el impacto cuando falla una cámara
    
    Args:
        id_camara: ID de la cámara
        db_session: Sesión de base de datos
    
    Returns:
        tuple: (equipos_afectados, conexiones_perdidas)
    """
    equipos_afectados = []
    conexiones_perdidas = set()
    
    # Buscar la cámara
    camara = db_session.query(Camara).filter_by(id=id_camara).first()
    if not camara:
        logger.warning(f"Cámara ID {id_camara} no encontrada")
        return equipos_afectados, conexiones_perdidas
    
    # La cámara es afectada directamente
    impacto_camara = ImpactoEquipo(
        equipo_id=camara.id,
        tipo_equipo='camara',
        nombre=camara.nombre,
        razon_impacto=f"Falla en cámara: {camara.descripcion or 'Sin descripción'}",
        severidad="CRITICA"
    )
    equipos_afectados.append(impacto_camara)
    
    # Impacto en Switch (si está conectado)
    if camara.switch_id:
        switch = db_session.query(Switch).filter_by(id=camara.switch_id).first()
        if switch:
            impacto_switch = ImpactoEquipo(
                equipo_id=switch.id,
                tipo_equipo='switch',
                nombre=switch.nombre,
                razon_impacto=f"Cámara conectada ({camara.nombre}) fuera de servicio",
                severidad="BAJA"
            )
            equipos_afectados.append(impacto_switch)
    
    # Impacto en NVR (si está grabando)
    if camara.nvr_id:
        nvr = db_session.query(NVR).filter_by(id=camara.nvr_id).first()
        if nvr:
            impacto_nvr = ImpactoEquipo(
                equipo_id=nvr.id,
                tipo_equipo='nvr',
                nombre=nvr.nombre,
                razon_impacto=f"Cámara conectada ({camara.nombre}) no disponible para grabación",
                severidad="MEDIA"
            )
            equipos_afectados.append(impacto_nvr)
    
    # Buscar conexiones de red afectadas
    conexiones_camara = db_session.query(NetworkConnection).filter(
        or_(
            and_(NetworkConnection.equipo_origen_id == id_camara, 
                 NetworkConnection.equipo_origen_tipo == 'camara'),
            and_(NetworkConnection.equipo_destino_id == id_camara,
                 NetworkConnection.equipo_destino_tipo == 'camara')
        )
    ).all()
    
    for conexion in conexiones_camara:
        if conexion.activa:
            conexiones_perdidas.add(conexion.id)
    
    return equipos_afectados, conexiones_perdidas


def _analizar_falla_equipo(tipo_equipo: str, id_equipo: int, db_session: Session) -> tuple:
    """
    Analiza el impacto cuando falla cualquier tipo de equipo
    
    Args:
        tipo_equipo: Tipo del equipo (switch, nvr, ups, etc.)
        id_equipo: ID del equipo
        db_session: Sesión de base de datos
    
    Returns:
        tuple: (equipos_afectados, conexiones_perdidas)
    """
    equipos_afectados = []
    conexiones_perdidas = set()
    
    # Obtener el equipo
    equipo = _obtener_equipo_por_tipo(id_equipo, tipo_equipo, db_session)
    if not equipo:
        logger.warning(f"{tipo_equipo} ID {id_equipo} no encontrado")
        return equipos_afectados, conexiones_perdidas
    
    # Impacto directo en el equipo
    impacto_directo = ImpactoEquipo(
        equipo_id=equipo.id,
        tipo_equipo=tipo_equipo,
        nombre=getattr(equipo, 'nombre', str(equipo)),
        razon_impacto=f"Falla en {tipo_equipo}",
        severidad=_determinar_severidad_por_tipo(tipo_equipo)
    )
    equipos_afectados.append(impacto_directo)
    
    # Buscar equipos conectados o dependientes
    equipos_dependientes = _encontrar_equipos_dependientes(tipo_equipo, id_equipo, db_session)
    
    for dep_tipo, dep_id, razon in equipos_dependientes:
        equipo_dep = _obtener_equipo_por_tipo(dep_id, dep_tipo, db_session)
        if equipo_dep:
            impacto_dep = ImpactoEquipo(
                equipo_id=equipo_dep.id,
                tipo_equipo=dep_tipo,
                nombre=getattr(equipo_dep, 'nombre', str(equipo_dep)),
                razon_impacto=razon,
                severidad="MEDIA"
            )
            equipos_afectados.append(impacto_dep)
    
    # Buscar conexiones de red afectadas
    conexiones_equipo = db_session.query(NetworkConnection).filter(
        or_(
            and_(NetworkConnection.equipo_origen_id == id_equipo,
                 NetworkConnection.equipo_origen_tipo == tipo_equipo),
            and_(NetworkConnection.equipo_destino_id == id_equipo,
                 NetworkConnection.equipo_destino_tipo == tipo_equipo)
        )
    ).all()
    
    for conexion in conexiones_equipo:
        if conexion.activa:
            conexiones_perdidas.add(conexion.id)
    
    return equipos_afectados, conexiones_perdidas


def _obtener_equipo_por_tipo(equipo_id: int, tipo_equipo: str, db_session: Session):
    """
    Obtiene un equipo específico por su tipo
    
    Args:
        equipo_id: ID del equipo
        tipo_equipo: Tipo del equipo
        db_session: Sesión de base de datos
    
    Returns:
        Equipo o None
    """
    modelos = {
        'camara': Camara,
        'switch': Switch,
        'nvr': NVR,
        'ups': UPS,
        'fuente_poder': FuentePoder,
        'gabinete': Gabinete,
        'equipo': Equipo
    }
    
    modelo = modelos.get(tipo_equipo.lower())
    if modelo:
        return db_session.query(modelo).filter_by(id=equipo_id).first()
    
    return None


def _encontrar_equipos_dependientes(tipo_equipo: str, id_equipo: int, db_session: Session) -> List[tuple]:
    """
    Encuentra equipos que dependen del equipo especificado
    
    Args:
        tipo_equipo: Tipo del equipo
        id_equipo: ID del equipo
        db_session: Sesión de base de datos
    
    Returns:
        Lista de tuplas (tipo, id, razon_dependencia)
    """
    dependencias = []
    
    if tipo_equipo == 'switch':
        # Cámaras conectadas al switch
        camaras = db_session.query(Camara).filter_by(switch_id=id_equipo).all()
        for camara in camaras:
            dependencias.append(('camara', camara.id, f"Dependiente de Switch {id_equipo} para conectividad"))
        
        # NVRs en el mismo switch
        nvrs = db_session.query(NVR).filter_by(switch_id=id_equipo).all()
        for nvr in nvrs:
            dependencias.append(('nvr', nvr.id, f"Conectado al Switch {id_equipo}"))
    
    elif tipo_equipo == 'nvr':
        # Cámaras grabadas por el NVR
        camaras = db_session.query(Camara).filter_by(nvr_id=id_equipo).all()
        for camara in camaras:
            dependencias.append(('camara', camara.id, f"Grabada por NVR {id_equipo}"))
    
    elif tipo_equipo == 'ups':
        # Equipos alimentados por este UPS
        # Esto requeriría una tabla de relaciones UPS-Equipos
        pass
    
    return dependencias


def _analizar_dependencias_indirectas(equipos_afectados: List[ImpactoEquipo], db_session: Session) -> List[ImpactoEquipo]:
    """
    Analiza dependencias indirectas y secundarias
    
    Args:
        equipos_afectados: Lista de equipos directamente afectados
        db_session: Sesión de base de datos
    
    Returns:
        Lista actualizada con equipos afectados indirectamente
    """
    # Esta función podría implementar análisis más profundo:
    # - Redes de dependencia
    # - Cascadas de fallas
    # - Rutas de backup/redundancia
    pass
    
    return equipos_afectados


def _evaluar_severidad_impacto(equipos_afectados: List[ImpactoEquipo], tipo_activo: str, id_activo: int) -> List[ImpactoEquipo]:
    """
    Evalúa y ajusta la severidad del impacto basado en contexto
    
    Args:
        equipos_afectados: Lista de equipos afectados
        tipo_activo: Tipo del activo original que falló
        id_activo: ID del activo original que falló
    
    Returns:
        Lista con severidad actualizada
    """
    # Ajustar severidades basadas en reglas de negocio
    for equipo in equipos_afectados:
        # Cámaras en áreas críticas tienen severidad mayor
        if equipo.tipo == 'camara':
            equipo.severidad = "CRITICA"
        
        # NVRs que manejan múltiples cámaras
        elif equipo.tipo == 'nvr':
            equipo.severidad = "ALTA"
        
        # Switches core tienen mayor impacto
        elif equipo.tipo == 'switch':
            equipo.severidad = "ALTA"
    
    return equipos_afectados


def _determinar_severidad_por_tipo(tipo_equipo: str) -> str:
    """
    Determina la severidad base basada en el tipo de equipo
    
    Args:
        tipo_equipo: Tipo del equipo
    
    Returns:
        Severidad como string
    """
    severidades = {
        'camara': 'CRITICA',
        'nvr': 'ALTA',
        'switch': 'ALTA',
        'ups': 'CRITICA',
        'fuente_poder': 'ALTA',
        'gabinete': 'MEDIA'
    }
    
    return severidades.get(tipo_equipo, 'MEDIA')


# === FUNCIONES DE UTILIDAD ===

def obtener_resumen_impacto(equipos_afectados: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Obtiene un resumen del impacto total
    
    Args:
        equipos_afectados: Lista de equipos afectados
    
    Returns:
        Dict con resumen del impacto
    """
    if not equipos_afectados:
        return {
            'total_afectados': 0,
            'severidad_promedio': 'NINGUNA',
            'tipos_afectados': [],
            'recomendaciones': ['No se requieren acciones']
        }
    
    # Contar por tipo y severidad
    tipos_afectados = {}
    severidades = {'CRITICA': 0, 'ALTA': 0, 'MEDIA': 0, 'BAJA': 0}
    
    for equipo in equipos_afectados:
        tipo = equipo.get('tipo', 'desconocido')
        severidad = equipo.get('severidad', 'MEDIA')
        
        tipos_afectados[tipo] = tipos_afectados.get(tipo, 0) + 1
        if severidad in severidades:
            severidades[severidad] += 1
    
    # Determinar severidad promedio
    severidad_promedio = 'BAJA'
    if severidades['CRITICA'] > 0:
        severidad_promedio = 'CRITICA'
    elif severidades['ALTA'] > 0:
        severidad_promedio = 'ALTA'
    elif severidades['MEDIA'] > 0:
        severidad_promedio = 'MEDIA'
    
    # Generar recomendaciones
    recomendaciones = []
    if severidades['CRITICA'] > 0:
        recomendaciones.append("Acción inmediata requerida")
    if severidades['ALTA'] > 0:
        recomendaciones.append("Priorizar atención en equipos críticos")
    if len(equipos_afectados) > 10:
        recomendaciones.append("Considerar escalamiento a equipo de respuesta")
    
    return {
        'total_afectados': len(equipos_afectados),
        'severidad_promedio': severidad_promedio,
        'tipos_afectados': tipos_afectados,
        'conteo_severidad': severidades,
        'recomendaciones': recomendaciones
    }


def calcular_tiempo_recuperacion_estimado(equipos_afectados: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Calcula tiempo estimado de recuperación basado en equipos afectados
    
    Args:
        equipos_afectados: Lista de equipos afectados
    
    Returns:
        Dict con tiempos estimados en horas
    """
    # Tiempos base por tipo de equipo (en horas)
    tiempos_base = {
        'camara': 2,
        'nvr': 4,
        'switch': 6,
        'ups': 8,
        'fuente_poder': 4,
        'gabinete': 12
    }
    
    tiempo_maximo = 0
    tiempo_promedio = 0
    
    if equipos_afectados:
        tiempos_equipos = []
        for equipo in equipos_afectados:
            tipo = equipo.get('tipo', 'equipo')
            tiempo_equipo = tiempos_base.get(tipo, 8)
            tiempos_equipos.append(tiempo_equipo)
        
        tiempo_maximo = max(tiempos_equipos)
        tiempo_promedio = sum(tiempos_equipos) / len(tiempos_equipos)
    
    return {
        'tiempo_minimo': int(tiempo_promedio * 0.5),  # Escenario optimista
        'tiempo_estimado': int(tiempo_promedio),      # Escenario más probable
        'tiempo_maximo': int(tiempo_maximo * 1.5)     # Escenario pesimista
    }


# === FUNCIÓN PRINCIPAL EXPORTADA ===

__all__ = ['analizar_impacto', 'ImpactoEquipo', 'obtener_resumen_impacto', 'calcular_tiempo_recuperacion_estimado']