import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from datetime import datetime
from sqlalchemy import or_, func
from werkzeug.security import generate_password_hash

from models import db, Usuario, Ubicacion, Camara, Gabinete, Switch, Puerto_Switch, UPS, NVR_DVR, Fuente_Poder, Catalogo_Tipo_Falla, Falla, Mantenimiento, Equipo_Tecnico, Historial_Estado_Equipo, init_database, fix_usuarios_structure

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Soportar SQLite (desarrollo) y PostgreSQL (producción)
database_url = os.environ.get('DATABASE_URL', 'sqlite:///sistema_camaras.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Inicializar y corregir la base de datos
with app.app_context():
    init_database()

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Decorador para verificar roles
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.rol not in roles:
                flash('No tienes permisos para acceder a esta página', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Función de validación anti-duplicados
def validar_falla_duplicada(equipo_tipo, equipo_id):
    """Valida si se puede insertar una nueva falla para un equipo"""
    falla_activa = Falla.query.filter_by(
        equipo_tipo=equipo_tipo,
        equipo_id=equipo_id
    ).filter(
        Falla.estado.in_(['Pendiente', 'Asignada', 'En Proceso'])
    ).order_by(Falla.fecha_reporte.desc()).first()
    
    if falla_activa:
        return {
            'permitir': False,
            'mensaje': f'Ya existe una falla {falla_activa.estado} para este equipo (ID: {falla_activa.id}, reportada el {falla_activa.fecha_reporte.strftime("%d/%m/%Y")}). Debe cerrar o cancelar la falla anterior antes de reportar una nueva.',
            'falla_existente': falla_activa
        }
    
    return {
        'permitir': True,
        'mensaje': 'OK',
        'falla_existente': None
    }

# ========== AUTENTICACIÓN ==========
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Usar email en lugar de username (más seguro y compatible)
        email = request.form.get('email') or request.form.get('username')
        password = request.form.get('password')
        
        # Buscar por email (más confiable)
        user = Usuario.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.activo:
            login_user(user)
            flash(f'Bienvenido {user.nombre_completo or user.email}', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login'))

# ========== DASHBOARD ==========
@app.route('/')
@login_required
def dashboard():
    # Estadísticas
    total_camaras = Camara.query.count()
    camaras_activas = Camara.query.filter_by(estado='Activo').count()
    fallas_pendientes = Falla.query.filter_by(estado='Pendiente').count()
    fallas_asignadas = Falla.query.filter_by(estado='Asignada').count()
    fallas_en_proceso = Falla.query.filter_by(estado='En Proceso').count()
    mantenimientos_mes = Mantenimiento.query.filter(
        func.extract('month', Mantenimiento.fecha) == datetime.now().month,
        func.extract('year', Mantenimiento.fecha) == datetime.now().year
    ).count()
    
    # Últimas fallas
    ultimas_fallas = Falla.query.order_by(Falla.fecha_reporte.desc()).limit(10).all()
    
    return render_template('dashboard.html',
                         total_camaras=total_camaras,
                         camaras_activas=camaras_activas,
                         fallas_pendientes=fallas_pendientes,
                         fallas_asignadas=fallas_asignadas,
                         fallas_en_proceso=fallas_en_proceso,
                         mantenimientos_mes=mantenimientos_mes,
                         ultimas_fallas=ultimas_fallas)

# ========== CÁMARAS ==========
@app.route('/camaras')
@login_required
def camaras_list():
    campus = request.args.get('campus', '')
    estado = request.args.get('estado', '')
    busqueda = request.args.get('busqueda', '')
    
    query = Camara.query.join(Ubicacion)
    
    if campus:
        query = query.filter(Ubicacion.campus == campus)
    if estado:
        query = query.filter(Camara.estado == estado)
    if busqueda:
        query = query.filter(or_(
            Camara.codigo.like(f'%{busqueda}%'),
            Camara.nombre.like(f'%{busqueda}%'),
            Camara.ip.like(f'%{busqueda}%')
        ))
    
    camaras = query.all()
    ubicaciones = Ubicacion.query.all()
    campus_list = db.session.query(Ubicacion.campus).distinct().all()
    
    return render_template('camaras_list.html', 
                         camaras=camaras, 
                         ubicaciones=ubicaciones,
                         campus_list=[c[0] for c in campus_list])

@app.route('/camaras/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'supervisor')
def camaras_nuevo():
    if request.method == 'POST':
        camara = Camara(
            codigo=request.form.get('codigo'),
            nombre=request.form.get('nombre'),
            ip=request.form.get('ip'),
            modelo=request.form.get('modelo'),
            fabricante=request.form.get('fabricante'),
            tipo_camara=request.form.get('tipo_camara'),
            ubicacion_id=request.form.get('ubicacion_id'),
            gabinete_id=request.form.get('gabinete_id') or None,
            switch_id=request.form.get('switch_id') or None,
            nvr_id=request.form.get('nvr_id') or None,
            estado=request.form.get('estado', 'Activo'),
            fecha_alta=datetime.strptime(request.form.get('fecha_alta'), '%Y-%m-%d').date() if request.form.get('fecha_alta') else None,
            latitud=float(request.form.get('latitud')) if request.form.get('latitud') else None,
            longitud=float(request.form.get('longitud')) if request.form.get('longitud') else None,
            observaciones=request.form.get('observaciones')
        )
        db.session.add(camara)
        db.session.commit()
        flash('Cámara creada exitosamente', 'success')
        return redirect(url_for('camaras_list'))
    
    ubicaciones = Ubicacion.query.filter_by(activo=True).all()
    gabinetes = Gabinete.query.filter_by(estado='Activo').all()
    switches = Switch.query.filter_by(estado='Activo').all()
    nvrs = NVR_DVR.query.filter_by(estado='Activo').all()
    
    return render_template('camaras_form.html', 
                         ubicaciones=ubicaciones,
                         gabinetes=gabinetes,
                         switches=switches,
                         nvrs=nvrs,
                         camara=None)

@app.route('/camaras/<int:id>')
@login_required
def camaras_detalle(id):
    camara = Camara.query.get_or_404(id)
    fallas = Falla.query.filter_by(equipo_tipo='Camara', equipo_id=id).order_by(Falla.fecha_reporte.desc()).all()
    mantenimientos = Mantenimiento.query.filter_by(equipo_tipo='Camara', equipo_id=id).order_by(Mantenimiento.fecha.desc()).all()
    historial = Historial_Estado_Equipo.query.filter_by(equipo_tipo='Camara', equipo_id=id).order_by(Historial_Estado_Equipo.fecha_cambio.desc()).all()
    
    return render_template('camaras_detalle.html', 
                         camara=camara,
                         fallas=fallas,
                         mantenimientos=mantenimientos,
                         historial=historial)

@app.route('/camaras/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'supervisor')
def camaras_editar(id):
    camara = Camara.query.get_or_404(id)
    
    if request.method == 'POST':
        estado_anterior = camara.estado
        
        camara.codigo = request.form.get('codigo')
        camara.nombre = request.form.get('nombre')
        camara.ip = request.form.get('ip')
        camara.modelo = request.form.get('modelo')
        camara.fabricante = request.form.get('fabricante')
        camara.tipo_camara = request.form.get('tipo_camara')
        camara.ubicacion_id = request.form.get('ubicacion_id')
        camara.estado = request.form.get('estado')
        camara.latitud = float(request.form.get('latitud')) if request.form.get('latitud') else None
        camara.longitud = float(request.form.get('longitud')) if request.form.get('longitud') else None
        camara.observaciones = request.form.get('observaciones')
        
        # Registrar cambio de estado
        if estado_anterior != camara.estado:
            historial = Historial_Estado_Equipo(
                equipo_tipo='Camara',
                equipo_id=id,
                estado_anterior=estado_anterior,
                estado_nuevo=camara.estado,
                motivo=request.form.get('motivo_cambio', ''),
                usuario_id=current_user.id
            )
            db.session.add(historial)
        
        db.session.commit()
        flash('Cámara actualizada exitosamente', 'success')
        return redirect(url_for('camaras_detalle', id=id))
    
    ubicaciones = Ubicacion.query.filter_by(activo=True).all()
    gabinetes = Gabinete.query.filter_by(estado='Activo').all()
    switches = Switch.query.filter_by(estado='Activo').all()
    nvrs = NVR_DVR.query.filter_by(estado='Activo').all()
    
    return render_template('camaras_form.html', 
                         camara=camara,
                         ubicaciones=ubicaciones,
                         gabinetes=gabinetes,
                         switches=switches,
                         nvrs=nvrs)

# ========== GABINETES ==========
@app.route('/gabinetes')
@login_required
def gabinetes_list():
    campus = request.args.get('campus', '')
    estado = request.args.get('estado', '')
    
    query = Gabinete.query.join(Ubicacion)
    
    if campus:
        query = query.filter(Ubicacion.campus == campus)
    if estado:
        query = query.filter(Gabinete.estado == estado)
    
    gabinetes = query.all()
    campus_list = db.session.query(Ubicacion.campus).distinct().all()
    
    return render_template('gabinetes_list.html', 
                         gabinetes=gabinetes,
                         campus_list=[c[0] for c in campus_list])

@app.route('/gabinetes/<int:id>/mantencion')
@login_required
def gabinetes_mantencion(id):
    """Vista especial de mantención de gabinetes"""
    gabinete = Gabinete.query.get_or_404(id)
    
    # Obtener todos los equipos contenidos en este gabinete
    switches = Switch.query.filter_by(gabinete_id=id).all()
    nvrs = NVR_DVR.query.filter_by(gabinete_id=id).all()
    ups_list = UPS.query.filter_by(gabinete_id=id).all()
    fuentes = Fuente_Poder.query.filter_by(gabinete_id=id).all()
    
    # Historial de mantenimientos del gabinete
    mantenimientos = Mantenimiento.query.filter_by(
        equipo_tipo='Gabinete', 
        equipo_id=id
    ).order_by(Mantenimiento.fecha.desc()).all()
    
    return render_template('gabinetes_mantencion.html',
                         gabinete=gabinete,
                         switches=switches,
                         nvrs=nvrs,
                         ups_list=ups_list,
                         fuentes=fuentes,
                         mantenimientos=mantenimientos)

# ========== FALLAS ==========
@app.route('/fallas')
@login_required
def fallas_list():
    estado = request.args.get('estado', '')
    campus = request.args.get('campus', '')
    
    query = Falla.query
    
    if estado:
        query = query.filter(Falla.estado == estado)
    
    if current_user.rol == 'tecnico':
        query = query.filter(Falla.tecnico_asignado_id == current_user.id)
    
    fallas = query.order_by(Falla.fecha_reporte.desc()).all()
    
    return render_template('fallas_list.html', fallas=fallas)

@app.route('/fallas/nueva', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'supervisor', 'tecnico')
def fallas_nueva():
    if request.method == 'POST':
        equipo_tipo = request.form.get('equipo_tipo')
        equipo_id = int(request.form.get('equipo_id'))
        
        # Validar anti-duplicados
        validacion = validar_falla_duplicada(equipo_tipo, equipo_id)
        if not validacion['permitir']:
            flash(validacion['mensaje'], 'warning')
            return redirect(url_for('fallas_nueva'))
        
        falla = Falla(
            equipo_tipo=equipo_tipo,
            equipo_id=equipo_id,
            tipo_falla_id=request.form.get('tipo_falla_id'),
            descripcion=request.form.get('descripcion'),
            prioridad=request.form.get('prioridad'),
            reportado_por_id=current_user.id,
            estado='Pendiente'
        )
        db.session.add(falla)
        db.session.commit()
        flash('Falla reportada exitosamente', 'success')
        return redirect(url_for('fallas_list'))
    
    tipos_falla = Catalogo_Tipo_Falla.query.all()
    camaras = Camara.query.filter_by(estado='Activo').all()
    gabinetes = Gabinete.query.filter_by(estado='Activo').all()
    switches = Switch.query.filter_by(estado='Activo').all()
    
    return render_template('fallas_form.html',
                         tipos_falla=tipos_falla,
                         camaras=camaras,
                         gabinetes=gabinetes,
                         switches=switches)

@app.route('/fallas/<int:id>')
@login_required
def fallas_detalle(id):
    falla = Falla.query.get_or_404(id)
    tecnicos = Usuario.query.filter_by(rol='tecnico', activo=True).all()
    return render_template('fallas_detalle.html', falla=falla, tecnicos=tecnicos)

@app.route('/fallas/<int:id>/asignar', methods=['POST'])
@login_required
@role_required('admin', 'supervisor')
def fallas_asignar(id):
    falla = Falla.query.get_or_404(id)
    falla.tecnico_asignado_id = request.form.get('tecnico_id')
    falla.estado = 'Asignada'
    falla.fecha_asignacion = datetime.now()
    db.session.commit()
    flash('Falla asignada correctamente', 'success')
    return redirect(url_for('fallas_detalle', id=id))

@app.route('/fallas/<int:id>/iniciar', methods=['POST'])
@login_required
def fallas_iniciar(id):
    falla = Falla.query.get_or_404(id)
    if falla.tecnico_asignado_id != current_user.id and current_user.rol not in ['admin', 'supervisor']:
        flash('No tienes permisos para iniciar esta falla', 'danger')
        return redirect(url_for('fallas_detalle', id=id))
    
    falla.estado = 'En Proceso'
    falla.fecha_inicio_reparacion = datetime.now()
    db.session.commit()
    flash('Reparación iniciada', 'success')
    return redirect(url_for('fallas_detalle', id=id))

@app.route('/fallas/<int:id>/reparar', methods=['GET', 'POST'])
@login_required
def fallas_reparar(id):
    falla = Falla.query.get_or_404(id)
    
    if request.method == 'POST':
        falla.estado = 'Reparada'
        falla.fecha_fin_reparacion = datetime.now()
        falla.solucion_aplicada = request.form.get('solucion_aplicada')
        falla.materiales_utilizados = request.form.get('materiales_utilizados')
        falla.costo_reparacion = float(request.form.get('costo_reparacion', 0))
        
        if falla.fecha_inicio_reparacion:
            delta = falla.fecha_fin_reparacion - falla.fecha_inicio_reparacion
            falla.tiempo_resolucion_horas = delta.total_seconds() / 3600
        
        db.session.commit()
        flash('Falla marcada como reparada', 'success')
        return redirect(url_for('fallas_detalle', id=id))
    
    return render_template('fallas_reparar.html', falla=falla)

@app.route('/fallas/<int:id>/cerrar', methods=['POST'])
@login_required
@role_required('admin', 'supervisor')
def fallas_cerrar(id):
    falla = Falla.query.get_or_404(id)
    falla.estado = 'Cerrada'
    falla.fecha_cierre = datetime.now()
    db.session.commit()
    flash('Falla cerrada correctamente', 'success')
    return redirect(url_for('fallas_detalle', id=id))

# ========== MANTENIMIENTOS ==========
@app.route('/mantenimientos')
@login_required
def mantenimientos_list():
    mantenimientos = Mantenimiento.query.order_by(Mantenimiento.fecha.desc()).all()
    return render_template('mantenimientos_list.html', mantenimientos=mantenimientos)

@app.route('/mantenimientos/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'supervisor', 'tecnico')
def mantenimientos_nuevo():
    if request.method == 'POST':
        mantenimiento = Mantenimiento(
            equipo_tipo=request.form.get('equipo_tipo'),
            equipo_id=request.form.get('equipo_id'),
            tipo=request.form.get('tipo'),
            fecha=datetime.now(),
            tecnico_id=current_user.id,
            descripcion=request.form.get('descripcion'),
            materiales_utilizados=request.form.get('materiales_utilizados'),
            tiempo_ejecucion_horas=float(request.form.get('tiempo_ejecucion_horas', 0)),
            costo=float(request.form.get('costo', 0)),
            observaciones=request.form.get('observaciones')
        )
        db.session.add(mantenimiento)
        db.session.commit()
        flash('Mantenimiento registrado exitosamente', 'success')
        return redirect(url_for('mantenimientos_list'))
    
    return render_template('mantenimientos_form.html')

# ========== MAPAS ==========
@app.route('/mapa-red')
@login_required
def mapa_red():
    campus = request.args.get('campus', '')
    
    # Obtener datos para generar diagrama Mermaid
    if campus:
        ubicaciones = Ubicacion.query.filter_by(campus=campus).all()
    else:
        ubicaciones = Ubicacion.query.all()
    
    gabinetes = Gabinete.query.join(Ubicacion).filter(Ubicacion.id.in_([u.id for u in ubicaciones])).all()
    switches = Switch.query.filter(Switch.gabinete_id.in_([g.id for g in gabinetes])).all()
    
    campus_list = db.session.query(Ubicacion.campus).distinct().all()
    
    return render_template('mapa_red.html',
                         campus_list=[c[0] for c in campus_list],
                         gabinetes=gabinetes,
                         switches=switches)

@app.route('/mapa-geolocalizacion')
@login_required
def mapa_geolocalizacion():
    camaras = Camara.query.filter(Camara.latitud.isnot(None), Camara.longitud.isnot(None)).all()
    gabinetes = Gabinete.query.filter(Gabinete.latitud.isnot(None), Gabinete.longitud.isnot(None)).all()
    
    return render_template('mapa_geolocalizacion.html',
                         camaras=camaras,
                         gabinetes=gabinetes)

@app.route('/informes-avanzados')
@login_required
def informes_avanzados():
    # Estadísticas generales
    stats_por_campus = db.session.query(
        Ubicacion.campus,
        func.count(Camara.id)
    ).join(Camara).group_by(Ubicacion.campus).all()
    
    fallas_por_tipo = db.session.query(
        Catalogo_Tipo_Falla.nombre,
        func.count(Falla.id)
    ).join(Falla).group_by(Catalogo_Tipo_Falla.nombre).all()
    
    return render_template('informes_avanzados.html',
                         stats_por_campus=stats_por_campus,
                         fallas_por_tipo=fallas_por_tipo)

# ========== API REST ==========
@app.route('/api/estadisticas')
@login_required
def api_estadisticas():
    stats = {
        'total_camaras': Camara.query.count(),
        'camaras_activas': Camara.query.filter_by(estado='Activo').count(),
        'fallas_pendientes': Falla.query.filter_by(estado='Pendiente').count(),
        'fallas_en_proceso': Falla.query.filter_by(estado='En Proceso').count()
    }
    return jsonify(stats)

@app.route('/api/fallas/validar')
@login_required
def api_validar_falla():
    equipo_tipo = request.args.get('equipo_tipo')
    equipo_id = request.args.get('equipo_id')
    
    if not equipo_tipo or not equipo_id:
        return jsonify({'error': 'Parámetros faltantes'}), 400
    
    resultado = validar_falla_duplicada(equipo_tipo, int(equipo_id))
    return jsonify(resultado)

@app.route('/api/gabinetes/<int:id>/equipos')
@login_required
def api_gabinete_equipos(id):
    """API para obtener todos los equipos de un gabinete"""
    gabinete = Gabinete.query.get_or_404(id)
    
    switches = Switch.query.filter_by(gabinete_id=id).all()
    nvrs = NVR_DVR.query.filter_by(gabinete_id=id).all()
    ups_list = UPS.query.filter_by(gabinete_id=id).all()
    fuentes = Fuente_Poder.query.filter_by(gabinete_id=id).all()
    
    return jsonify({
        'gabinete': {
            'id': gabinete.id,
            'codigo': gabinete.codigo,
            'nombre': gabinete.nombre
        },
        'switches': [{
            'id': s.id,
            'codigo': s.codigo,
            'modelo': s.modelo,
            'ip': s.ip,
            'estado': s.estado
        } for s in switches],
        'nvrs': [{
            'id': n.id,
            'codigo': n.codigo,
            'tipo': n.tipo,
            'modelo': n.modelo,
            'estado': n.estado
        } for n in nvrs],
        'ups': [{
            'id': u.id,
            'codigo': u.codigo,
            'modelo': u.modelo,
            'capacidad_va': u.capacidad_va,
            'estado': u.estado
        } for u in ups_list],
        'fuentes': [{
            'id': f.id,
            'codigo': f.codigo,
            'modelo': f.modelo,
            'voltaje': f.voltaje,
            'estado': f.estado
        } for f in fuentes]
    })

# ========== ENDPOINTS ADMINISTRATIVOS ==========
# Endpoint para primera inicialización (sin autenticación)
@app.route('/setup-first-time')
def setup_first_time():
    """SETUP INICIAL - Crea tablas y usuario admin (solo funciona si BD está vacía)"""
    try:
        # Seguridad: Solo permitir si NO hay usuarios (primera inicialización)
        if Usuario.query.count() > 0:
            return jsonify({
                'status': 'error',
                'message': 'Base de datos ya inicializada. Use credenciales de admin para otras operaciones.'
            }), 403
        
        db.create_all()
        
        # Crear usuarios por defecto
        usuarios = [
            Usuario(username='admin', rol='admin', nombre_completo='Administrador', activo=True),
            Usuario(username='supervisor', rol='supervisor', nombre_completo='Supervisor', activo=True),
            Usuario(username='tecnico1', rol='tecnico', nombre_completo='Técnico 1', activo=True),
            Usuario(username='visualizador', rol='visualizador', nombre_completo='Visualizador', activo=True)
        ]
        passwords = ['admin123', 'super123', 'tecnico123', 'viz123']
        for user, password in zip(usuarios, passwords):
            user.set_password(password)
            db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '✅ Base de datos inicializada correctamente. Ahora puede hacer login como admin/admin123',
            'total_usuarios': Usuario.query.count(),
            'next_step': 'Vaya a /admin/migrate-data para cargar los datos desde Excel'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/admin/migrate-data')
@login_required
@role_required('admin')
def admin_migrate_data():
    """Migra datos desde Excel a PostgreSQL (importando función directamente)"""
    try:
        # Importar la función migrar_datos desde migrate_data.py
        from migrate_data import migrar_datos
        
        # Ejecutar migración
        migrar_datos()
        
        return jsonify({
            'status': 'success',
            'message': 'Migración completada exitosamente',
            'datos': {
                'ubicaciones': Ubicacion.query.count(),
                'camaras': Camara.query.count(),
                'gabinetes': Gabinete.query.count(),
                'switches': Switch.query.count(),
                'fallas': Falla.query.count(),
                'mantenimientos': Mantenimiento.query.count()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/admin/database-status')
@login_required
def admin_database_status():
    """Verifica el estado de la base de datos"""
    try:
        status = {
            'database_connected': True,
            'tables': {
                'usuarios': Usuario.query.count(),
                'ubicaciones': Ubicacion.query.count(),
                'camaras': Camara.query.count(),
                'gabinetes': Gabinete.query.count(),
                'switches': Switch.query.count(),
                'ups': UPS.query.count(),
                'nvr_dvr': NVR_DVR.query.count(),
                'fuentes_poder': Fuente_Poder.query.count(),
                'fallas': Falla.query.count(),
                'mantenimientos': Mantenimiento.query.count(),
                'equipos_tecnicos': Equipo_Tecnico.query.count(),
                'tipos_fallas': Catalogo_Tipo_Falla.query.count()
            }
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({'database_connected': False, 'error': str(e)}), 500

@app.route('/admin/migrate-nomenclature', methods=['POST'])
@login_required
@role_required('admin')
def admin_migrate_nomenclature():
    """Endpoint para migrar nomenclatura usuario → usuarios"""
    try:
        from sqlalchemy import text
        
        # Solo ejecutar si la aplicación usa nomenclatura 'usuarios'
        if Usuario.__tablename__ != 'usuarios':
            return jsonify({
                'status': 'error',
                'message': 'La aplicación aún usa nomenclatura "usuario" (singular). Actualice models.py primero.'
            }), 400
        
        # Verificar conexión a BD
        with db.engine.connect() as conn:
            # Verificar tabla usuario existe
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'usuario'
                )
            """))
            usuario_exists = result.scalar()
            
            if not usuario_exists:
                return jsonify({
                    'status': 'error',
                    'message': 'Tabla "usuario" no existe en la BD'
                }), 400
            
            # Verificar tabla usuarios no existe
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'usuarios'
                )
            """))
            usuarios_exists = result.scalar()
            
            if usuarios_exists:
                return jsonify({
                    'status': 'error',
                    'message': 'La tabla "usuarios" ya existe. Migración ya ejecutada o en progreso.'
                }), 400
            
            # Ejecutar migración en transacción
            with conn.begin():
                # Renombrar tabla
                conn.execute(text("ALTER TABLE usuario RENAME TO usuarios"))
                
                # Actualizar foreign keys
                constraints = [
                    ("falla", "reportado_por_id", "falla_reportado_por_id_fkey"),
                    ("falla", "tecnico_asignado_id", "falla_tecnico_asignado_id_fkey"), 
                    ("mantenimiento", "tecnico_id", "mantenimiento_tecnico_id_fkey")
                ]
                
                for table, column, constraint_name in constraints:
                    # Drop constraint antiguo
                    conn.execute(text(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {constraint_name}"))
                    
                    # Crear nuevo constraint
                    new_constraint = constraint_name.replace('usuario', 'usuarios')
                    conn.execute(text(f"""
                        ALTER TABLE {table} 
                        ADD CONSTRAINT {new_constraint} 
                        FOREIGN KEY ({column}) REFERENCES usuarios(id)
                    """))
                
                # Verificar conteo
                result = conn.execute(text("SELECT COUNT(*) FROM usuarios"))
                user_count = result.scalar()
        
        return jsonify({
            'status': 'success',
            'message': f'Migración completada exitosamente. {user_count} usuarios preservados.',
            'next_step': 'Reiniciar la aplicación para aplicar cambios'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Inicializar base de datos y crear usuarios por defecto
@app.cli.command()
def init_db():
    """Inicializa la base de datos y crea usuarios por defecto"""
    db.create_all()
    
    # Verificar si ya existen usuarios
    if Usuario.query.count() == 0:
        usuarios = [
            Usuario(username='admin', rol='admin', nombre_completo='Administrador', activo=True),
            Usuario(username='supervisor', rol='supervisor', nombre_completo='Supervisor', activo=True),
            Usuario(username='tecnico1', rol='tecnico', nombre_completo='Técnico 1', activo=True),
            Usuario(username='visualizador', rol='visualizador', nombre_completo='Visualizador', activo=True)
        ]
        
        passwords = ['admin123', 'super123', 'tecnico123', 'viz123']
        
        for user, password in zip(usuarios, passwords):
            user.set_password(password)
            db.session.add(user)
        
        db.session.commit()
        print('Base de datos inicializada con usuarios por defecto')
    else:
        print('Los usuarios ya existen')

# Ejecutar inicialización al importar (usa la función de models.py)
with app.app_context():
    init_database()

# Endpoint temporal para corrección urgente
@app.route('/admin/fix-structure-temp', methods=['GET', 'POST'])
def fix_structure_temp():
    """Endpoint temporal sin autenticación para corrección urgente"""
    try:
        fix_usuarios_structure()
        return jsonify({
            'success': True,
            'message': 'Estructura corregida exitosamente. La aplicación se reiniciará automáticamente.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Endpoint temporal para ejecutar corrección SQL
@app.route('/admin/fix-database-temp', methods=['POST'])
def fix_database_temp():
    """Endpoint temporal para corregir la base de datos - SOLO PARA DESARROLLO"""
    try:
        import os
        DATABASE_URL = os.environ.get('DATABASE_URL')
        
        if not DATABASE_URL:
            return jsonify({'error': 'DATABASE_URL no encontrada'}), 500
        
        # Importar psycopg2 en tiempo de ejecución
        try:
            import psycopg2
            from psycopg2 import sql
        except ImportError:
            return jsonify({
                'error': 'psycopg2 no disponible',
                'message': 'Ejecutar SQL manualmente en Railway PostgreSQL'
            }), 500
        
        # Conectar y ejecutar corrección
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # SQL de corrección
        correction_sql = """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'usuarios' AND column_name = 'username'
            ) THEN
                ALTER TABLE usuarios ADD COLUMN username VARCHAR(80);
                UPDATE usuarios SET username = COALESCE(email, 'user_' || id::text) WHERE username IS NULL;
                ALTER TABLE usuarios ALTER COLUMN username SET NOT NULL;
                CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
            END IF;
            
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'usuarios' AND column_name = 'modo'
            ) THEN
                ALTER TABLE usuarios DROP COLUMN IF EXISTS modo;
            END IF;
        END $$;
        """
        
        cursor.execute(correction_sql)
        conn.commit()
        
        # Verificar usuario Charles
        cursor.execute("""
            SELECT id, email, username, nombre_completo, rol, activo 
            FROM usuarios 
            WHERE email = %s
        """, ('charles@ufro.cl',))
        
        charles = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Base de datos corregida exitosamente',
            'charles_user': {
                'id': charles[0] if charles else None,
                'email': charles[1] if charles else None,
                'username': charles[2] if charles else None,
                'nombre': charles[3] if charles else None,
                'rol': charles[4] if charles else None
            } if charles else 'No encontrado'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Error ejecutando corrección SQL'
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
