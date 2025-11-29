from flask import Blueprint, jsonify, request
# Asegúrate de que los modelos se importen correctamente desde models/__init__.py
from models import db, Camara, Switch, FuentePoder, NVR, Gabinete, GabineteEquipment, NetworkConnection, EquipmentType, EquipmentStatus
from sqlalchemy.exc import IntegrityError

# 1. Definición del Blueprint
inventario_bp = Blueprint('inventario', __name__)

# ======================================================================
# 2. CRUD: CÁMARAS
# ======================================================================

@inventario_bp.route('/camara', methods=['POST'])
def crear_camara():
    """Registra una nueva cámara y su conexión a su Switch de origen."""
    data = request.get_json()
    
    campos_requeridos = ['nombre', 'modelo', 'id_ubicacion', 'id_switch_origen', 'puerto_switch', 'latitud', 'longitud']
    if not all(campo in data for campo in campos_requeridos):
        return jsonify({"error": "Faltan datos requeridos para la cámara y/o conexión."}), 400

    try:
        # 2. Crear el Equipo: Camara
        nueva_camara = Camara(
            nombre=data['nombre'],
            modelo=data['modelo'],
            id_ubicacion=data['id_ubicacion'],
            latitud=data['latitud'],
            longitud=data['longitud'],
            estado=EquipmentStatus.ACTIVO.value,
        )
        db.session.add(nueva_camara)
        db.session.flush() # Obtiene el ID de la nueva_camara
        
        # 3. Crear la Conexión de Red (Switch -> Camara)
        conexion = NetworkConnection(
            id_equipo_origen=data['id_switch_origen'],
            tipo_equipo_origen=EquipmentType.SWITCH.value,
            puerto_origen=data['puerto_switch'],
            
            id_equipo_destino=nueva_camara.id,
            tipo_equipo_destino=EquipmentType.CAMARA.value,
            puerto_destino='N/A', 
            tipo_conexion='PoE',
            esta_activo=True
        )
        db.session.add(conexion)
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Cámara y conexión creadas exitosamente.',
            'id_camara': nueva_camara.id,
            'id_conexion': conexion.id
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Error de integridad de datos. Verifique IDs de Switch o Ubicación."}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado al crear cámara: {str(e)}"}), 500


# ======================================================================
# 3. CRUD: SWITCHES
# ======================================================================

@inventario_bp.route('/switch', methods=['POST'])
def crear_switch():
    """
    Registra un nuevo Switch.
    Opcionalmente, registra su conexión de energía (id_fuente_poder) y su Uplink (id_switch_uplink).
    """
    data = request.get_json()
    
    try:
        # 1. Crear el Equipo: Switch
        nuevo_switch = Switch(
            nombre=data['nombre'],
            modelo=data['modelo'],
            id_ubicacion=data['id_ubicacion'],
            total_puertos=data['total_puertos'],
            id_fuente_poder=data.get('id_fuente_poder'),
            estado=EquipmentStatus.ACTIVO.value,
        )
        db.session.add(nuevo_switch)
        db.session.flush()

        # 2. Crear la Conexión de Uplink (Switch Superior -> Nuevo Switch)
        if data.get('id_switch_uplink') and data.get('puerto_origen_uplink'):
            conexion_uplink = NetworkConnection(
                id_equipo_origen=data['id_switch_uplink'],
                tipo_equipo_origen=EquipmentType.SWITCH.value,
                puerto_origen=data['puerto_origen_uplink'],
                
                id_equipo_destino=nuevo_switch.id,
                tipo_equipo_destino=EquipmentType.SWITCH.value,
                puerto_destino=data.get('puerto_destino_uplink', 'UPLINK'),
                tipo_conexion=data.get('tipo_conexion_uplink', 'Fibra Óptica'),
                esta_activo=True
            )
            db.session.add(conexion_uplink)
        
        db.session.commit()

        return jsonify({
            'mensaje': 'Switch creado exitosamente.',
            'id_switch': nuevo_switch.id,
            'conexion_uplink_creada': data.get('id_switch_uplink') is not None
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Error de integridad. La fuente de poder o ubicación no existen."}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado al crear Switch: {str(e)}"}), 500

# ======================================================================
# 4. CRUD: FUENTES DE PODER
# ======================================================================

@inventario_bp.route('/fuente_poder', methods=['POST'])
def crear_fuente_poder():
    """Registra una nueva Fuente de Poder."""
    data = request.get_json()
    
    try:
        nueva_fp = FuentePoder(
            nombre=data['nombre'],
            modelo=data['modelo'],
            id_ubicacion=data['id_ubicacion'],
            capacidad_watts=data.get('capacidad_watts', 0),
            estado=EquipmentStatus.ACTIVO.value,
        )
        db.session.add(nueva_fp)
        db.session.commit()

        return jsonify({
            'mensaje': 'Fuente de Poder registrada exitosamente.',
            'id_fuente_poder': nueva_fp.id,
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Error de integridad. Verifique el ID de Ubicación."}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado al crear Fuente de Poder: {str(e)}"}), 500

# ======================================================================
# 5. CRUD: NVR (Grabadores de Video en Red)
# ======================================================================

@inventario_bp.route('/nvr', methods=['POST'])
def crear_nvr():
    """
    Registra un nuevo NVR y su conexión a su Switch de red (Uplink).
    """
    data = request.get_json()
    
    campos_requeridos = ['nombre', 'modelo', 'id_ubicacion', 'id_switch_uplink', 'puerto_switch_nvr']
    if not all(campo in data for campo in campos_requeridos):
        return jsonify({"error": "Faltan datos requeridos para el NVR y/o su conexión de red."}), 400

    try:
        # 1. Crear el Equipo: NVR
        nuevo_nvr = NVR(
            nombre=data['nombre'],
            modelo=data['modelo'],
            id_ubicacion=data['id_ubicacion'],
            capacidad_almacenamiento_tb=data.get('capacidad_almacenamiento_tb', 0),
            total_canales=data.get('total_canales', 0),
            estado=EquipmentStatus.ACTIVO.value,
        )
        db.session.add(nuevo_nvr)
        db.session.flush() # Obtener el ID del nuevo_nvr
        
        # 2. Crear la Conexión de Red (Switch -> NVR)
        conexion_red_nvr = NetworkConnection(
            id_equipo_origen=data['id_switch_uplink'],
            tipo_equipo_origen=EquipmentType.SWITCH.value,
            puerto_origen=data['puerto_switch_nvr'],
            
            id_equipo_destino=nuevo_nvr.id,
            tipo_equipo_destino=EquipmentType.NVR.value,
            puerto_destino='RED',
            tipo_conexion='Cobre',
            esta_activo=True
        )
        db.session.add(conexion_red_nvr)
        db.session.commit()
        
        return jsonify({
            'mensaje': 'NVR y conexión de red creadas exitosamente.',
            'id_nvr': nuevo_nvr.id,
            'id_conexion': conexion_red_nvr.id
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Error de integridad de datos. Verifique IDs de Switch o Ubicación."}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado al crear NVR: {str(e)}"}), 500

# ======================================================================
# 6. CRUD: GABINETES
# ======================================================================

@inventario_bp.route('/gabinete', methods=['POST'])
def crear_gabinete():
    """Registra un nuevo Gabinete como contenedor físico en una Ubicación."""
    data = request.get_json()
    
    campos_requeridos = ['nombre', 'id_ubicacion', 'capacidad_u']
    if not all(campo in data for campo in campos_requeridos):
        return jsonify({"error": "Faltan datos requeridos para el Gabinete."}), 400

    try:
        # 1. Crear el Gabinete
        nuevo_gabinete = Gabinete(
            nombre=data['nombre'],
            id_ubicacion=data['id_ubicacion'],
            capacidad_u=data['capacidad_u'],
        )
        db.session.add(nuevo_gabinete)
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Gabinete registrado exitosamente.',
            'id_gabinete': nuevo_gabinete.id,
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Error de integridad de datos. Verifique el ID de Ubicación."}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado al crear Gabinete: {str(e)}"}), 500


@inventario_bp.route('/gabinete/asociar', methods=['POST'])
def asociar_equipo_a_gabinete():
    """Asocia un equipo existente (Switch, NVR, UPS) a un Gabinete."""
    data = request.get_json()
    
    campos_requeridos = ['id_gabinete', 'id_equipo', 'tipo_equipo', 'u_posicion']
    if not all(campo in data for campo in campos_requeridos):
        return jsonify({"error": "Faltan datos requeridos para la asociación."}), 400

    try:
        # 1. Crear el registro de asociación
        asociacion = GabineteEquipment(
            id_gabinete=data['id_gabinete'],
            id_equipo=data['id_equipo'],
            tipo_equipo=data['tipo_equipo'],
            u_posicion=data['u_posicion']
        )
        db.session.add(asociacion)
        db.session.commit()
        
        return jsonify({
            'mensaje': f"{data['tipo_equipo'].capitalize()} ID {data['id_equipo']} asociado a Gabinete ID {data['id_gabinete']}."
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Error de integridad. Gabinete o Equipo no encontrado."}), 409
    except Exception as e:
        db.session.rollback() # <-- CORRECCIÓN APLICADA AQUÍ
        return jsonify({"error": f"Error inesperado al asociar equipo: {str(e)}"}), 500 # <-- CORRECCIÓN APLICADA AQUÍ