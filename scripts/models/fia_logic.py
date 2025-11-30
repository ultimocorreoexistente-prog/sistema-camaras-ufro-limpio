"""
Lógica central para el Análisis de Impacto de Fallas (FIA).
Contiene funciones recursivas para trazar la propagación de fallas 
por Energía y por Red.
"""

# Importar las clases necesarias (Ajustar rutas de importación si es necesario)
from sqlalchemy.orm import Session
# Asegúrate de importar tus modelos y enums
from models import NetworkConnection, Switch, EquipmentType # Asumiendo estos nombres

# ----------------------------------------------------------------------
# 1. FUNCIONES PRINCIPALES DE PROPAGACIÓN
# ----------------------------------------------------------------------

def propagar_por_red(id_origen: int, tipo_origen: str, afectados: dict, db_session: Session):
    """
    Recorre las conexiones salientes (downstream) para propagar fallas de conectividad.
    Afecta: Cámaras, NVRs, Switches secundarios.
    """
    
    # Buscar todas las conexiones salientes activas (DOWNSTREAM)
    # Nota: Filtramos por esta_activo=True, ya que la conexión fallida (ej: fibra rota) 
    # debe ser tratada marcando esa conexión específica como 'esta_activo=False' en la BD antes de llamar al FIA.
    conexiones_salientes = db_session.query(NetworkConnection).filter(
        NetworkConnection.id_equipo_origen == id_origen,
        NetworkConnection.tipo_equipo_origen == tipo_origen,
        NetworkConnection.esta_activo == True 
    ).all()

    for conn in conexiones_salientes:
        id_destino = conn.id_equipo_destino
        tipo_destino = conn.tipo_equipo_destino
        
        # Usamos una tupla (ID, TIPO) como clave para evitar duplicados, ignorando el motivo temporalmente.
        if (id_destino, tipo_destino) in [(k, v[0]) for k, v in afectados.items()]:
            continue
            
        motivo = f"Pérdida de Conectividad (Desde {tipo_origen.capitalize()} ID {id_origen})"
        
        # Agregar al diccionario de afectados: {ID: (TIPO, MOTIVO)}
        afectados[id_destino] = (tipo_destino, motivo)
            
        # Recursividad: Si el destino es otro equipo que puede propagar (Switch, NVR), continuar.
        if tipo_destino in [EquipmentType.SWITCH.value, EquipmentType.NVR.value]:
            propagar_por_red(id_destino, tipo_destino, afectados, db_session)


def propagar_por_energia(id_origen: int, tipo_origen: str, afectados: dict, db_session: Session):
    """
    Recorre los equipos que dependen energéticamente del equipo fallido (downstream).
    Afecta: Switches, NVRs (alimentados por Fuente/UPS).
    """
    
    # Lógica de propagación de Fuente de Poder
    if tipo_origen == EquipmentType.FUENTE_PODER.value:
        
        # Buscar Switches directamente alimentados por esta Fuente
        switches_dependientes = db_session.query(Switch).filter(Switch.id_fuente_poder == id_origen).all()
        
        for sw in switches_dependientes:
            
            # Usamos una tupla (ID, TIPO) como clave para evitar duplicados.
            if (sw.id, EquipmentType.SWITCH.value) in [(k, v[0]) for k, v in afectados.items()]:
                continue
                
            motivo = f"Pérdida de Energía (Alimentado por Fuente de Poder {id_origen})"
            
            # Agregar al diccionario de afectados
            afectados[sw.id] = (EquipmentType.SWITCH.value, motivo)
                
            # CRÍTICO: Una vez que el Switch cae por energía, debe propagar la falla por RED.
            propagar_por_red(sw.id, EquipmentType.SWITCH.value, afectados, db_session)
            
    # Lógica similar para UPS (propagaría a Switches, Fuentes o NVRs conectados al UPS)
    # ... (Se añadiría lógica para UPSConnection)

# ----------------------------------------------------------------------
# 2. FUNCIÓN DE PUNTO DE ENTRADA (API CALL)
# ----------------------------------------------------------------------

def analizar_impacto(tipo_equipo_origen: str, id_equipo_origen: int, db_session: Session) -> list:
    """
    Función principal llamada por la API para iniciar el análisis.
    Devuelve una lista de diccionarios con el impacto.
    """
    
    # {ID: (TIPO, MOTIVO)}
    afectados = {
        id_equipo_origen: (tipo_equipo_origen, "Falla Inicial")
    }
    
    # 1. Propagación de Energía
    if tipo_equipo_origen in [EquipmentType.UPS.value, EquipmentType.FUENTE_PODER.value]:
        propagar_por_energia(id_equipo_origen, tipo_equipo_origen, afectados, db_session)

    # 2. Propagación de Red
    # Se ejecuta si el origen es un equipo de red o si la propagación de energía afectó a un Switch.
    if tipo_equipo_origen in [EquipmentType.SWITCH.value, EquipmentType.NVR.value] or \
       any(tipo == EquipmentType.SWITCH.value for _, (tipo, _) in afectados.items()):
        
        # En caso de que la falla inicial sea un Switch, empezamos por él.
        if tipo_equipo_origen in [EquipmentType.SWITCH.value, EquipmentType.NVR.value]:
            propagar_por_red(id_equipo_origen, tipo_equipo_origen, afectados, db_session)
        
        # Aseguramos que cualquier Switch que cayó por energía también propague su falla
        for id_eq, (tipo_eq, motivo) in list(afectados.items()): # Usamos list() para iterar sobre una copia
            if tipo_eq == EquipmentType.SWITCH.value and 'Energía' in motivo:
                 propagar_por_red(id_eq, tipo_eq, afectados, db_session)


    # 3. Formatear la salida para la API
    resultados_finales = []
    for id_eq, (tipo_eq, motivo) in afectados.items():
         # Se puede mejorar la serialización buscando el nombre del equipo aquí si es necesario
         resultados_finales.append({
             "id": id_eq,
             "tipo": tipo_eq,
             "motivo_impacto": motivo
         })

    return resultados_finales