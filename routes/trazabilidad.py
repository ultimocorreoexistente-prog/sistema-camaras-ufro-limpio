from flask import Blueprint, jsonify, request
# Importa la instancia de DB y tus modelos. Asegúrate de que las rutas de importación sean correctas.
<<<<<<< HEAD
from models import db, Falla, Mantenimiento, Usuario
from sqlalchemy.exc import IntegrityError
from datetime import datetime

# 2. Status endpoint
@trazabilidad_bp.route('/status', methods=['GET'])
def status():
    """API Status - Temporary maintenance message"""
    return jsonify({
        'status': 'maintenance',
        'message': 'Traceability API temporarily under maintenance. Advanced features disabled.',
        'available_models': ['Falla', 'Mantenimiento', 'Usuario'],
        'disabled_features': [
            'NetworkConnection management',
            'Photo documentation',
            'Equipment type enums',
            'Impact analysis (FIA)',
            'Network connection state tracking'
        ]
    }), 200

# 3. Health check endpoint  
@trazabilidad_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Traceability API is running but features are disabled'}), 200

# ⚠️ TEMPORARILY DISABLED: Routes using non-existent models (NetworkConnection, Fotografia, EquipmentType, fia_logic)
# These routes will be re-enabled once the missing models and logic are implemented

# @trazabilidad_bp.route('/falla/registrar', methods=['POST'])
# def registrar_falla_polimorfica():
#     """
#     Ruta para registrar una nueva falla en cualquier activo (incluyendo conexiones de red).
#     POST data debe contener: id_equipo (o id_conexion), tipo_equipo, descripcion, id_tecnico_asignado.
#     """
#     data = request.get_json()
#     
#     id_activo = data.get('id_equipo') 
#     tipo_activo = data.get('tipo_equipo')
#     
#     if not id_activo or not tipo_activo or not data.get('id_tecnico_asignado'):
#         return jsonify({"error": "Faltan campos obligatorios (id_equipo, tipo_equipo, id_tecnico_asignado)."}), 400
# 
#     if tipo_activo == 'conexion_red':
#         id_conexion = id_activo
#     else:
#         id_conexion = None # La falla es en el equipo, no en la conexión
# 
#     try:
#         # 1. Si la falla es en una conexión (ej. fibra suelta), la marcamos como inactiva.
#         if tipo_activo == 'conexion_red':
#             conexion = NetworkConnection.query.get(id_conexion)
#             if not conexion:
#                 return jsonify({"error": f"Conexión ID {id_conexion} no encontrada."}), 404
#             
#             # CRÍTICO: Marca la conexión como Down, disparando el impacto en el FIA
#             conexion.esta_activo = False 
#             db.session.add(conexion)
#         
#         # 2. Crear el registro de Falla
#         nueva_falla = Falla(
#             id_equipo=id_activo,
#             tipo_equipo=tipo_activo, 
#             descripcion=data.get('descripcion', f"Falla reportada en {tipo_activo.upper()} ID {id_activo}"),
#             estado='PENDIENTE',
#             gravedad=data.get('gravedad', 'MEDIA'),
#             id_tecnico_asignado=data.get('id_tecnico_asignado')
#         )
#         
#         db.session.add(nueva_falla)
#         db.session.commit()
#         
#         # 3. Ejecutar FIA para obtener el impacto (para informar al operador/dashboard)
#         afectados = analizar_impacto(tipo_activo, id_activo, db.session)
#         
#         return jsonify({
#             'mensaje': 'Falla registrada y técnico asignado.',
#             'id_falla': nueva_falla.id,
#             'impacto_inicial': afectados,
#             'conteo_afectados': len(afectados)
#         }), 201
#     
#     except IntegrityError:
#         db.session.rollback()
#         return jsonify({"error": "Error de integridad de datos (FK o unicidad)."}), 500
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

# @trazabilidad_bp.route('/mantenimiento/cerrar', methods=['POST'])
# def cerrar_mantenimiento_y_subir_fotos():
#     """Cierra la falla y el mantenimiento, restablece la conexión (si aplica) y registra fotos."""
#     data = request.get_json()
#     
#     id_falla = data.get('id_falla')
#     id_conexion_reparada = data.get('id_conexion_reparada') # Opcional: solo si es falla de conexión
#     
#     if not id_falla:
#         return jsonify({"error": "Falta id_falla obligatorio."}), 400
#         
#     try:
#         falla = Falla.query.get(id_falla)
#         if not falla:
#             return jsonify({"error": "Falla no encontrada."}), 404
#             
#         # 1. Restablecer Conexión/Equipo (Si aplica)
#         if falla.tipo_equipo == 'conexion_red' and id_conexion_reparada:
#             conexion = NetworkConnection.query.get(id_conexion_reparada)
#             if conexion:
#                 conexion.esta_activo = True # ¡El enlace vuelve a funcionar!
#                 db.session.add(conexion)
# 
#         # 2. Crear y Cerrar el Mantenimiento
#         nuevo_mantenimiento = Mantenimiento(
#             id_falla=id_falla,
#             tipo='CORRECTIVO',
#             id_equipo=falla.id_equipo,
#             tipo_equipo=falla.tipo_equipo,
#             id_tecnico_asignado=falla.id_tecnico_asignado,
#             solucion=data.get('solucion', 'Reparación completada.'),
#             estado='FINALIZADO'
#         )
#         db.session.add(nuevo_mantenimiento)
#         db.session.flush() # Asegura que se obtenga el ID del mantenimiento para vincular fotos
#         
#         # 3. Registrar Documentación Fotográfica
#         fotos_subidas = data.get('fotos_urls', []) # Espera una lista de URLs de Drive/Cloud
#         for url_foto in fotos_subidas:
#             nueva_foto = Fotografia(
#                 id_falla=id_falla,
#                 id_mantenimiento=nuevo_mantenimiento.id,
#                 tipo_entidad='mantenimiento',
#                 url_archivo=url_foto
#             )
#             db.session.add(nueva_foto)
#         
#         # 4. Cerrar la Falla
#         falla.estado = 'RESUELTA'
#         falla.solucion = nuevo_mantenimiento.solucion
#         falla.fecha_resolucion = datetime.now()
#         
#         db.session.commit()
#         
#         return jsonify({
#             'mensaje': 'Falla resuelta y trazabilidad completa.',
#             'id_mantenimiento': nuevo_mantenimiento.id,
#             'fotos_registradas': len(fotos_subidas)
#         }), 200
# 
#     except IntegrityError:
#         db.session.rollback()
#         return jsonify({"error": "Error de integridad de datos."}), 500
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": f"Error inesperado durante el cierre: {str(e)}"}), 500
=======
from models import db, Falla, NetworkConnection, Mantenimiento, Fotografia, EquipmentType 
# Importa la lógica de análisis de impacto
from fia_logic import analizar_impacto 
from sqlalchemy.exc import IntegrityError
from datetime import datetime

# 1. Definición del Blueprint
trazabilidad_bp = Blueprint('trazabilidad', __name__)

@trazabilidad_bp.route('/falla/registrar', methods=['POST'])
def registrar_falla_polimorfica():
    """
    Ruta para registrar una nueva falla en cualquier activo (incluyendo conexiones de red).
    POST data debe contener: id_equipo (o id_conexion), tipo_equipo, descripcion, id_tecnico_asignado.
    """
    data = request.get_json()
    
    id_activo = data.get('id_equipo') 
    tipo_activo = data.get('tipo_equipo')
    
    if not id_activo or not tipo_activo or not data.get('id_tecnico_asignado'):
        return jsonify({"error": "Faltan campos obligatorios (id_equipo, tipo_equipo, id_tecnico_asignado)."}), 400

    if tipo_activo == 'conexion_red':
        id_conexion = id_activo
    else:
        id_conexion = None # La falla es en el equipo, no en la conexión

    try:
        # 1. Si la falla es en una conexión (ej. fibra suelta), la marcamos como inactiva.
        if tipo_activo == 'conexion_red':
            conexion = NetworkConnection.query.get(id_conexion)
            if not conexion:
                return jsonify({"error": f"Conexión ID {id_conexion} no encontrada."}), 404
            
            # CRÍTICO: Marca la conexión como Down, disparando el impacto en el FIA
            conexion.esta_activo = False 
            db.session.add(conexion)
        
        # 2. Crear el registro de Falla
        nueva_falla = Falla(
            id_equipo=id_activo,
            tipo_equipo=tipo_activo, 
            descripcion=data.get('descripcion', f"Falla reportada en {tipo_activo.upper()} ID {id_activo}"),
            estado='PENDIENTE',
            gravedad=data.get('gravedad', 'MEDIA'),
            id_tecnico_asignado=data.get('id_tecnico_asignado')
        )
        
        db.session.add(nueva_falla)
        db.session.commit()
        
        # 3. Ejecutar FIA para obtener el impacto (para informar al operador/dashboard)
        afectados = analizar_impacto(tipo_activo, id_activo, db.session)
        
        return jsonify({
            'mensaje': 'Falla registrada y técnico asignado.',
            'id_falla': nueva_falla.id,
            'impacto_inicial': afectados,
            'conteo_afectados': len(afectados)
        }), 201
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Error de integridad de datos (FK o unicidad)."}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

@trazabilidad_bp.route('/mantenimiento/cerrar', methods=['POST'])
def cerrar_mantenimiento_y_subir_fotos():
    """Cierra la falla y el mantenimiento, restablece la conexión (si aplica) y registra fotos."""
    data = request.get_json()
    
    id_falla = data.get('id_falla')
    id_conexion_reparada = data.get('id_conexion_reparada') # Opcional: solo si es falla de conexión
    
    if not id_falla:
        return jsonify({"error": "Falta id_falla obligatorio."}), 400
        
    try:
        falla = Falla.query.get(id_falla)
        if not falla:
            return jsonify({"error": "Falla no encontrada."}), 404
            
        # 1. Restablecer Conexión/Equipo (Si aplica)
        if falla.tipo_equipo == 'conexion_red' and id_conexion_reparada:
            conexion = NetworkConnection.query.get(id_conexion_reparada)
            if conexion:
                conexion.esta_activo = True # ¡El enlace vuelve a funcionar!
                db.session.add(conexion)

        # 2. Crear y Cerrar el Mantenimiento
        nuevo_mantenimiento = Mantenimiento(
            id_falla=id_falla,
            tipo='CORRECTIVO',
            id_equipo=falla.id_equipo,
            tipo_equipo=falla.tipo_equipo,
            id_tecnico_asignado=falla.id_tecnico_asignado,
            solucion=data.get('solucion', 'Reparación completada.'),
            estado='FINALIZADO'
        )
        db.session.add(nuevo_mantenimiento)
        db.session.flush() # Asegura que se obtenga el ID del mantenimiento para vincular fotos
        
        # 3. Registrar Documentación Fotográfica
        fotos_subidas = data.get('fotos_urls', []) # Espera una lista de URLs de Drive/Cloud
        for url_foto in fotos_subidas:
            nueva_foto = Fotografia(
                id_falla=id_falla,
                id_mantenimiento=nuevo_mantenimiento.id,
                tipo_entidad='mantenimiento',
                url_archivo=url_foto
            )
            db.session.add(nueva_foto)
        
        # 4. Cerrar la Falla
        falla.estado = 'RESUELTA'
        falla.solucion = nuevo_mantenimiento.solucion
        falla.fecha_resolucion = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Falla resuelta y trazabilidad completa.',
            'id_mantenimiento': nuevo_mantenimiento.id,
            'fotos_registradas': len(fotos_subidas)
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Error de integridad de datos."}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado durante el cierre: {str(e)}"}), 500
>>>>>>> cdbdbe569d8335333b42b0aa946977f011b91270
