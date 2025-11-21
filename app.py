from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
#from forms import LoginForm, CamaraForm, CamaraEditForm
from models import db, Usuario, Camara
from config import get_config
import os

app = Flask(__name__)
app.config.from_object(get_config())

# Inicializar extensiones
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data.lower()).first()
        if user and user.activo and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            user.ultimo_acceso = datetime.utcnow()
            db.session.commit()
            flash('¡Bienvenido!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email o contraseña incorrectos', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'total_camaras': Camara.query.count(),
        'camaras_por_estado': db.session.query(Camara.estado, db.func.count()).group_by(Camara.estado).all(),
        'total_usuarios': Usuario.query.filter_by(activo=True).count(),
        'accesos_hoy': 0  # opcional: implementar con logs
    }
    return render_template('dashboard.html', stats=stats, user=current_user)


# === RUTAS DE CÁMARAS (IMPLEMENTADAS) ===

@app.route('/camaras')
@login_required
def listar_camaras():
    camaras = Camara.query.order_by(Camara.nombre).all()
    return render_template('camara.html', camaras=camaras, user=current_user)


@app.route('/camaras/nueva', methods=['GET', 'POST'])
@login_required
def nueva_camara():
    if current_user.rol not in ['admin', 'superadmin']:
        flash('No tienes permisos para crear cámaras', 'warning')
        return redirect(url_for('dashboard'))
    
    form = CamaraForm()
    if form.validate_on_submit():
        camara = Camara(
            codigo=form.codigo.data,
            nombre=form.nombre.data,
            ip_address=form.ip.data,
            marca=form.marca.data,
            modelo=form.modelo.data,
            tipo_camara=form.tipo_camara.data,
            ubicacion=form.ubicacion.data,
            estado=form.estado.data,
            fecha_instalacion=form.fecha_instalacion.data,
            latitud=form.latitud.data,
            longitud=form.longitud.data,
            observaciones=form.observaciones.data
        )
        db.session.add(camara)
        db.session.commit()
        flash('Cámara creada exitosamente', 'success')
        return redirect(url_for('listar_camaras'))
    
    return render_template('nueva_camara.html', form=form, user=current_user)


@app.route('/camaras/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_camara(id):
    if current_user.rol not in ['admin', 'superadmin']:
        flash('No tienes permisos para editar cámaras', 'warning')
        return redirect(url_for('dashboard'))
    
    camara = Camara.query.get_or_404(id)
    form = CamaraEditForm(obj=camara, camara_id=id)
    
    if form.validate_on_submit():
        form.populate_obj(camara)
        db.session.commit()
        flash('Cámara actualizada exitosamente', 'success')
        return redirect(url_for('listar_camaras'))
    
    return render_template('camaras_editar.html', form=form, camara=camara, user=current_user)


@app.route('/camaras/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_camara(id):
    if current_user.rol not in ['admin', 'superadmin']:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 403
    
    camara = Camara.query.get_or_404(id)
    db.session.delete(camara)
    db.session.commit()
    flash(f'Cámara "{camara.nombre}" eliminada', 'warning')
    return redirect(url_for('listar_camaras'))


@app.route('/api/camaras/<int:id>/test')
@login_required
def test_camara(id):
    camara = Camara.query.get_or_404(id)
    # Simulación segura (en producción, usar ping/requests con timeout)
    ip = camara.ip_address
    status = 'success' if ip and '127' not in ip and ip != '0.0.0.0' else 'error'
    return jsonify({
        'status': status,
        'message': f'Cámara {"accesible" if status == "success" else "inaccesible"}',
        'ip': ip
    })


# === Manejo de errores ===

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Acceso denegado'), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Página no encontrada'), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('error.html', code=500, message='Error interno'), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=(app.config['FLASK_ENV'] == 'development'))