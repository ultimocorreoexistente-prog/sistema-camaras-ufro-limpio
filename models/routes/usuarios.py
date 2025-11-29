"""
Rutas para gestión de usuarios
Sistema de Cámaras UFRO
Incluye CRUD completo con autenticación, validaciones y manejo de roles
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import text
import re
from datetime import datetime

# Blueprint para las rutas de usuarios
usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

# Importar db y modelo Usuario (se obtiene desde app.py)
# db = SQLAlchemy()
# Usuario = User.query model

def get_db_and_models():
    """Obtener instancia de db y modelo Usuario desde el contexto de la aplicación"""
    from flask import current_app
    return current_app.extensions['sqlalchemy'].db, current_app.extensions['sqlalchemy'].db.session.query().\
    _mapper_zero_or_none().class_

def require_admin():
    """Decorador para requerir permisos de administrador"""
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debe iniciar sesión para acceder a esta página.', 'error')
                return redirect(url_for('login'))

            # Verificar permisos según rol
            roles_permitidos = ['ADMIN', 'SUPERADMIN']
            if current_user.rol not in roles_permitidos:
                flash('No tiene permisos para acceder a esta funcionalidad.', 'error')
                return redirect(url_for('usuarios_listar'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_email(email):
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validar formato de teléfono chileno"""
    if not phone:
        return False
    # Patrones para números chilenos
    patterns = [
        r'^\+56\s?9\s?\d{4}\s?\d{4}$', # +56 9 XXXX XXXX
        r'^569\d{8}$', # 569XXXXXXXX
        r'^9\d{8}$', # 9XXXXXXXX
        r'^56\s?9\s?\d{4}\s?\d{4}$' # 56 9 XXXX XXXX
    ]
    return any(re.match(pattern, phone.replace(' ', '')) for pattern in patterns)


def get_role_permissions(role):
    """Obtener descripción de permisos según el rol"""
    permissions = {
    'SUPERADMIN': 'Control total del sistema, gestión de usuarios y configuración general.',
    'ADMIN': 'Gestión completa de equipos, usuarios, inventario y reportes avanzados.',
    'SUPERVISOR': 'Supervisión y asignación de tareas, reportes departamentales.',
    'TECNICO': 'Gestión de fallas asignadas, subida de fotografías y actualización de estados.',
    'VISUALIZADOR': 'Solo visualización de información del sistema.'
    }
    return permissions.get(role, 'Permisos no definidos')

@usuarios_bp.route('/')
@login_required
@require_admin()
def usuarios_listar():
    """Listar todos los usuarios del sistema"""
    try:
        db, Usuario = get_db_and_models()

        # Obtener parámetros de búsqueda y filtrado
        buscar = request.args.get('buscar', '').strip()
        filtrar_rol = request.args.get('rol', '')
        filtrar_estado = request.args.get('estado', '')

        # Construir query base
        query = Usuario.query

        # Aplicar filtros de búsqueda
        if buscar:
            query = query.filter(
                db.or_(
                    Usuario.nombre_completo.ilike(f'%{buscar}%'),
                    Usuario.nombre.ilike(f'%{buscar}%'),
                    Usuario.email.ilike(f'%{buscar}%'),
                    Usuario.telefono.ilike(f'%{buscar}%'),
                    Usuario.departamento.ilike(f'%{buscar}%')
        )
        )

        # Filtro por rol
        if filtrar_rol:
            query = query.filter(Usuario.rol == filtrar_rol)

        # Filtro por estado
        if filtrar_estado == 'activo':
            query = query.filter(Usuario.activo == True)
        elif filtrar_estado == 'inactivo':
            query = query.filter(Usuario.activo == False)

    # Ordenar por nombre completo y obtener resultados
    usuarios = query.order_by(Usuario.nombre_completo.asc()).all()

    # Obtener estadísticas
    total_usuarios = Usuario.query.count()
    usuarios_activos = Usuario.query.filter_by(activo=True).count()
    usuarios_admin = Usuario.query.filter(Usuario.rol.in_(['SUPERADMIN', 'ADMIN'])).count()
    usuarios_tecnico = Usuario.query.filter_by(rol='TECNICO').count()

    # Obtener roles únicos para el filtro
    roles_disponibles = [rol[0] for rol in db.session.query(Usuario.rol).distinct().all()]

    return render_template('usuarios_listar.html',
    usuarios=usuarios,
    buscar=buscar,
    filtrar_rol=filtrar_rol,
    filtrar_estado=filtrar_estado,
    total_usuarios=total_usuarios,
    usuarios_activos=usuarios_activos,
    usuarios_admin=usuarios_admin,
    usuarios_tecnico=usuarios_tecnico,
    roles_disponibles=roles_disponibles)

    except Exception as e:
        flash(f'Error al cargar usuarios: {str(e)}', 'error')
    return redirect(url_for('dashboard'))

@usuarios_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@require_admin()
def usuarios_crear():
    """Crear nuevo usuario"""
    try:
        db, Usuario = get_db_and_models()

        if request.method == 'POST':
            # Obtener datos del formulario
            nombre = request.form.get('nombre', '').strip()
            email = request.form.get('email', '').strip().lower()
            telefono = request.form.get('telefono', '').strip()
            departamento = request.form.get('departamento', '').strip()
            password = request.form.get('password', '')
            password_confirm = request.form.get('password_confirm', '')
            rol = request.form.get('rol', '')

            # Validaciones
            errores = []

            if not nombre:
                errores.append('El nombre completo es obligatorio.')

            if not email:
                errores.append('El email es obligatorio.')
            elif not validate_email(email):
                errores.append('El formato del email no es válido.')
            elif Usuario.query.filter_by(email=email).first():
                errores.append('Ya existe un usuario con ese email.')

            if telefono and not validate_phone(telefono):
                errores.append('El formato del teléfono no es válido.')

            if not password:
                errores.append('La contraseña es obligatoria.')
            elif len(password) < 8:
                errores.append('La contraseña debe tener al menos 8 caracteres.')

            if password == password_confirm:
                errores.append('Las contraseñas no coinciden.')

            if not rol:
                errores.append('Debe seleccionar un rol.')
            elif rol not in ['SUPERADMIN', 'ADMIN', 'SUPERVISOR', 'TECNICO', 'VISUALIZADOR']:
                errores.append('Rol no válido.')

            # Verificar permisos para crear SUPERADMIN
            if rol == 'SUPERADMIN' and current_user.rol == 'SUPERADMIN':
                errores.append('Solo un SUPERADMIN puede crear otros SUPERADMIN.')

            if errores:
                for error in errores:
                    flash(error, 'error')
                return render_template('usuarios_crear.html')

            # Crear nuevo usuario
            try:
                nuevo_usuario = Usuario(
                    nombre_completo=nombre,
                    nombre=nombre, # Campo adicional para compatibilidad
                    email=email,
                    telefono=telefono if telefono else None,
                    departamento=departamento if departamento else None,
                    rol=rol,
                    username=email.split('@')[0], # Generar username basado en email
                    activo=True,
                    fecha_creacion=datetime.utcnow()
                )

                # Encriptar contraseña
                nuevo_usuario.set_password(password)

                # Guardar en base de datos
                db.session.add(nuevo_usuario)
                db.session.commit()

                flash(f'Usuario "{nombre}" creado exitosamente.', 'success')
                return redirect(url_for('usuarios_listar'))

            except Exception as db_error:
                db.session.rollback()
                flash(f'Error al crear usuario: {str(db_error)}', 'error')
                return render_template('usuarios_crear.html')

        # GET request - mostrar formulario
        return render_template('usuarios_crear.html')

    except Exception as e:
        flash(f'Error inesperado: {str(e)}', 'error')
        return redirect(url_for('usuarios_listar'))

@usuarios_bp.route('/editar/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
@require_admin()
def usuarios_editar(usuario_id):
    """Editar usuario existente"""
    try:
        db, Usuario = get_db_and_models()

        # Obtener usuario
        usuario = Usuario.query.get_or_404(usuario_id)

        # Prevenir auto-eliminación
        if usuario.id == current_user.id:
            flash('No puede editar su propio usuario desde esta sección.', 'warning')
            return redirect(url_for('usuarios_listar'))

        if request.method == 'POST':
            # Obtener datos del formulario
            nombre = request.form.get('nombre', '').strip()
            email = request.form.get('email', '').strip().lower()
            telefono = request.form.get('telefono', '').strip()
            departamento = request.form.get('departamento', '').strip()
            rol = request.form.get('rol', '')
            activo = request.form.get('activo') == 'on'
            password = request.form.get('password', '')
            password_confirm = request.form.get('password_confirm', '')

            # Validaciones
            errores = []

            if not nombre:
                errores.append('El nombre completo es obligatorio.')

            if not email:
                errores.append('El email es obligatorio.')
            elif not validate_email(email):
                errores.append('El formato del email no es válido.')
            else:
                # Verificar email único (excluyendo el usuario actual)
                email_existente = Usuario.query.filter(
                    Usuario.email == email,
                    Usuario.id == usuario_id
                ).first()
                if email_existente:
                    errores.append('Ya existe otro usuario con ese email.')

            if telefono and not validate_phone(telefono):
                errores.append('El formato del teléfono no es válido.')

            if not rol:
                errores.append('Debe seleccionar un rol.')
            elif rol not in ['SUPERADMIN', 'ADMIN', 'SUPERVISOR', 'TECNICO', 'VISUALIZADOR']:
                errores.append('Rol no válido.')

            # Verificar permisos para modificar roles
            if rol == 'SUPERADMIN' and current_user.rol == 'SUPERADMIN':
                errores.append('Solo un SUPERADMIN puede asignar el rol SUPERADMIN.')

            if current_user.rol == 'SUPERADMIN' and usuario.rol == 'SUPERADMIN' and rol == 'SUPERADMIN':
                errores.append('Solo un SUPERADMIN puede cambiar el rol de otro SUPERADMIN.')

            # Validación de contraseña (solo si se proporciona)
            if password:
                if len(password) < 8:
                    errores.append('La nueva contraseña debe tener al menos 8 caracteres.')
                if password == password_confirm:
                    errores.append('Las contraseñas no coinciden.')

            if errores:
                for error in errores:
                    flash(error, 'error')
                return render_template('usuarios_editar.html', usuario=usuario)

            try:
                # Actualizar datos del usuario
                usuario.nombre_completo = nombre
                usuario.nombre = nombre # Campo adicional para compatibilidad
                usuario.email = email
                usuario.telefono = telefono if telefono else None
                usuario.departamento = departamento if departamento else None
                usuario.activo = activo
                usuario.rol = rol

                # Actualizar contraseña si se proporciona
                if password:
                    usuario.set_password(password)

                # Actualizar timestamp de modificación
                if hasattr(usuario, 'fecha_modificacion'):
                    usuario.fecha_modificacion = datetime.utcnow()

                # Guardar cambios
                db.session.commit()

                flash(f'Usuario "{nombre}" actualizado exitosamente.', 'success')
                return redirect(url_for('usuarios_listar'))

            except Exception as db_error:
                db.session.rollback()
                flash(f'Error al actualizar usuario: {str(db_error)}', 'error')
                return render_template('usuarios_editar.html', usuario=usuario)

        # GET request - mostrar formulario con datos del usuario
        return render_template('usuarios_editar.html', usuario=usuario)

    except Exception as e:
        flash(f'Error inesperado: {str(e)}', 'error')
        return redirect(url_for('usuarios_listar'))

@usuarios_bp.route('/eliminar/<int:usuario_id>', methods=['POST'])
@login_required
@require_admin()
def usuarios_eliminar(usuario_id):
    """Eliminar usuario (soft delete: desactivar usuario)"""
    try:
        db, Usuario = get_db_and_models()

        # Obtener usuario a eliminar
        usuario = Usuario.query.get_or_404(usuario_id)

        # Prevenir auto-eliminación
        if usuario.id == current_user.id:
            flash('No puede eliminar su propio usuario.', 'error')
            return redirect(url_for('usuarios_listar'))

        # Solo SUPERADMIN puede eliminar otros SUPERADMIN
        if usuario.rol == 'SUPERADMIN' and current_user.rol == 'SUPERADMIN':
            flash('Solo un SUPERADMIN puede eliminar otros SUPERADMIN.', 'error')
            return redirect(url_for('usuarios_listar'))

        # Verificar si es el último SUPERADMIN
        if usuario.rol == 'SUPERADMIN':
            superadmins_restantes = Usuario.query.filter(
                Usuario.rol == 'SUPERADMIN',
                Usuario.id != usuario_id,
                Usuario.activo == True
            ).count()

            if superadmins_restantes == 0:
                flash('No se puede eliminar el último SUPERADMIN activo del sistema.', 'error')
                return redirect(url_for('usuarios_listar'))

        try:
            # Soft delete: desactivar usuario en lugar de eliminar
            usuario.activo = False
            usuario.fecha_baja = datetime.utcnow()

            # Agregar información de quién eliminó el usuario
            if hasattr(usuario, 'eliminado_por'):
                usuario.eliminado_por = current_user.id
            if hasattr(usuario, 'motivo_baja'):
                usuario.motivo_baja = f'Eliminado por {current_user.nombre_completo}'

            db.session.commit()

            flash(f'Usuario "{usuario.nombre_completo}" eliminado exitosamente.', 'success')

        except Exception as db_error:
            db.session.rollback()
            flash(f'Error al eliminar usuario: {str(db_error)}', 'error')

        return redirect(url_for('usuarios_listar'))

    except Exception as e:
        flash(f'Error inesperado: {str(e)}', 'error')
        return redirect(url_for('usuarios_listar'))

@usuarios_bp.route('/activar/<int:usuario_id>', methods=['POST'])
@login_required
@require_admin()
def usuarios_activar(usuario_id):
    """Activar usuario desactivado"""
    try:
        db, Usuario = get_db_and_models()

        usuario = Usuario.query.get_or_404(usuario_id)

        # Solo ADMIN o SUPERADMIN pueden activar usuarios
        if current_user.rol not in ['ADMIN', 'SUPERADMIN']:
            flash('No tiene permisos para activar usuarios.', 'error')
            return redirect(url_for('usuarios_listar'))

        try:
            usuario.activo = True
            usuario.fecha_reactivacion = datetime.utcnow()

            # Agregar información de quién reactiva
            if hasattr(usuario, 'reactivado_por'):
                usuario.reactivado_por = current_user.id

            db.session.commit()

            flash(f'Usuario "{usuario.nombre_completo}" activado exitosamente.', 'success')

        except Exception as db_error:
            db.session.rollback()
            flash(f'Error al activar usuario: {str(db_error)}', 'error')

        return redirect(url_for('usuarios_listar'))

    except Exception as e:
        flash(f'Error inesperado: {str(e)}', 'error')
        return redirect(url_for('usuarios_listar'))

@usuarios_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def usuarios_perfil():
    """Ver/editar perfil del usuario actual"""
    try:
        db, Usuario = get_db_and_models()
        usuario = Usuario.query.get(current_user.id)

        if request.method == 'POST':
            # Obtener datos del formulario
            nombre = request.form.get('nombre', '').strip()
            telefono = request.form.get('telefono', '').strip()
            departamento = request.form.get('departamento', '').strip()
            password_actual = request.form.get('password_actual', '')
            password_nuevo = request.form.get('password_nuevo', '')
            password_confirm = request.form.get('password_confirm', '')

            errores = []

            if not nombre:
                errores.append('El nombre es obligatorio.')

            if telefono and not validate_phone(telefono):
                errores.append('El formato del teléfono no es válido.')

            # Validación de cambio de contraseña
            if password_nuevo or password_confirm:
                if not password_actual:
                    errores.append('Debe proporcionar su contraseña actual.')
                elif not usuario.check_password(password_actual):
                    errores.append('La contraseña actual es incorrecta.')

                if len(password_nuevo) < 8:
                    errores.append('La nueva contraseña debe tener al menos 8 caracteres.')

                if password_nuevo == password_confirm:
                    errores.append('Las nuevas contraseñas no coinciden.')

            if errores:
                for error in errores:
                    flash(error, 'error')
                return render_template('usuarios_perfil.html', usuario=usuario)

            try:
                # Actualizar datos básicos
                usuario.nombre_completo = nombre
                usuario.telefono = telefono if telefono else None
                usuario.departamento = departamento if departamento else None

                # Actualizar contraseña si se proporciona
                if password_nuevo:
                    usuario.set_password(password_nuevo)

                # Actualizar último acceso
                usuario.ultimo_acceso = datetime.utcnow()

                db.session.commit()
                flash('Perfil actualizado exitosamente.', 'success')

            except Exception as db_error:
                db.session.rollback()
                flash(f'Error al actualizar perfil: {str(db_error)}', 'error')

            return render_template('usuarios_perfil.html', usuario=usuario)

    except Exception as e:
        flash(f'Error inesperado: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@usuarios_bp.route('/exportar')
@login_required
@require_admin()
def usuarios_exportar():
    """Exportar lista de usuarios a CSV"""
    try:
        import csv
        from io import StringIO

        db, Usuario = get_db_and_models()

        # Crear archivo CSV en memoria
        output = StringIO()
        writer = csv.writer(output)

        # Escribir encabezados
        writer.writerow(['ID', 'Nombre', 'Email', 'Teléfono', 'Rol', 'Departamento', 'Activo', 'Fecha Registro'])

        # Escribir datos de usuarios
        usuarios = Usuario.query.order_by(Usuario.nombre_completo.asc()).all()
        for usuario in usuarios:
            writer.writerow([
                usuario.id,
                usuario.nombre_completo,
                usuario.email,
                usuario.telefono or '',
                usuario.rol,
                usuario.departamento or '',
                'Sí' if usuario.activo else 'No',
                usuario.fecha_creacion.strftime('%d/%m/%Y %H:%M') if usuario.fecha_creacion else ''
            ])

        # Preparar respuesta
        output.seek(0)
        response = current_app.response_class(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment;filename=usuarios_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
        )

        return response

    except Exception as e:
        flash(f'Error al exportar usuarios: {str(e)}', 'error')
        return redirect(url_for('usuarios_listar'))

@usuarios_bp.route('/api/info-rol/<rol>')
@login_required
def api_info_rol(rol):
    """API para obtener información sobre roles"""
    try:
        info = {
            'descripcion': get_role_permissions(rol),
            'permisos': [],
            'restricciones': []
        }

        # Definir permisos específicos por rol
        permisos_por_rol = {
            'SUPERADMIN': {
                'permisos': ['Gestión total de usuarios', 'Configuración del sistema', 'Acceso a todos los datos'],
                'restricciones': ['Ninguna']
            },
            'ADMIN': {
                'permisos': ['Gestión de equipos', 'Gestión de inventario', 'Reportes avanzados'],
                'restricciones': ['No puede modificar SUPERADMIN']
            },
            'SUPERVISOR': {
                'permisos': ['Asignación de tareas', 'Supervisión de técnicos', 'Reportes departamentales'],
                'restricciones': ['No puede modificar equipos directamente']
            },
            'TECNICO': {
                'permisos': ['Gestión de fallas asignadas', 'Subida de fotografías', 'Actualización de estados'],
                'restricciones': ['Solo puede modificar sus propias asignaciones']
            },
            'VISUALIZADOR': {
                'permisos': ['Visualización de datos'],
                'restricciones': ['Solo lectura, sin modificaciones']
            }
        }

        if rol in permisos_por_rol:
            info.update(permisos_por_rol[rol])

        from flask import jsonify
        return jsonify(info)

    except Exception as e:
        from flask import jsonify
        return jsonify({'error': str(e)}), 500

    # Error handlers personalizados
@usuarios_bp.errorhandler(404)
def not_found_error(error):
    flash('Usuario no encontrado.', 'error')
    return redirect(url_for('usuarios_listar'))

@usuarios_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    flash('Error interno del servidor.', 'error')
    return redirect(url_for('usuarios_listar'))