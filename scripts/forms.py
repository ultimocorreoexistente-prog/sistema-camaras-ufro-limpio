from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SelectField, TextAreaField,
    BooleanField, DateField, FloatField, SubmitField
)
from wtforms.validators import (
    DataRequired, Email, Length, Optional, ValidationError, Regexp
)
from models import db, Camara, Usuario
import re
from ipaddress import ip_address


def validate_ufro_email(form, field):
    email = field.data.lower()
    if not re.match(r'^[a-zA-Z0-9._%+-]+@(ufrontera\.cl|ufro\.cl)$', email):
        raise ValidationError('El correo debe pertenecer al dominio @ufrontera.cl o @ufro.cl')


def validate_ip_address(form, field):
    if not field.data:
        return
    try:
        ip = ip_address(field.data)
        if ip.is_loopback and field.data not in ['127.0.0.1', '::1']:
            raise ValidationError('No se permiten direcciones de loopback en cámaras')
    except ValueError:
        raise ValidationError('Dirección IP inválida')


def validate_codigo_unico(exclude_id=None):
    def _validate(form, field):
        if not field.data:
            return
        query = Camara.query.filter(Camara.codigo.ilike(field.data.strip()))
        if exclude_id:
            query = query.filter(Camara.id != exclude_id)
        if query.first():
            raise ValidationError(f'El código "{field.data}" ya está en uso')
    return _validate


def validate_nombre_unico(exclude_id=None):
    def _validate(form, field):
        if not field.data:
            return
        query = Camara.query.filter(Camara.nombre.ilike(field.data.strip()))
        if exclude_id:
            query = query.filter(Camara.id != exclude_id)
        if query.first():
            raise ValidationError(f'Ya existe una cámara con el nombre "{field.data}"')
    return _validate


class LoginForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[
        DataRequired('El correo es obligatorio'),
        Email('Formato de correo inválido'),
        validate_ufro_email
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired('La contraseña es obligatoria')
    ])
    remember = BooleanField('Recordar sesión')
    submit = SubmitField('Iniciar Sesión')


class CamaraForm(FlaskForm):
    codigo = StringField('Código', validators=[
        DataRequired('El código es obligatorio'),
        Length(min=3, max=50, message='El código debe tener entre 3 y 50 caracteres'),
        validate_codigo_unico()
    ])
    nombre = StringField('Nombre', validators=[
        DataRequired('El nombre es obligatorio'),
        Length(min=3, max=200, message='El nombre debe tener entre 3 y 200 caracteres'),
        validate_nombre_unico()
    ])
    ip = StringField('Dirección IP', validators=[
        Optional(),
        validate_ip_address
    ])
    marca = StringField('Marca', validators=[DataRequired('La marca es obligatoria')])
    modelo = StringField('Modelo', validators=[DataRequired('El modelo es obligatorio')])
    tipo_camara = SelectField('Tipo de Cámara', choices=[
        ('Domo', 'Domo'),
        ('PTZ', 'PTZ'),
        ('Bullet', 'Bullet'),
        ('Caja', 'Caja'),
        ('Oculta', 'Oculta')
    ], validators=[DataRequired('El tipo es obligatorio')])
    
    ubicacion = StringField('Ubicación Detallada', validators=[
        DataRequired('La ubicación es obligatoria')
    ])
    estado = SelectField('Estado', choices=[
        ('activa', 'Activa'),
        ('inactiva', 'Inactiva'),
        ('mantenimiento', 'Mantenimiento'),
        ('baja', 'Baja')
    ], default='activa')
    
    fecha_instalacion = DateField('Fecha de Instalación', validators=[Optional()])
    latitud = FloatField('Latitud', validators=[Optional()])
    longitud = FloatField('Longitud', validators=[Optional()])
    observaciones = TextAreaField('Observaciones', validators=[Optional()])
    
    submit = SubmitField('Guardar Cámara')

    def validate_latitud(self, field):
        if field.data is not None and (field.data < -90 or field.data > 90):
            raise ValidationError('La latitud debe estar entre -90 y 90 grados')

    def validate_longitud(self, field):
        if field.data is not None and (field.data < -180 or field.data > 180):
            raise ValidationError('La longitud debe estar entre -180 y 180 grados')


class CamaraEditForm(CamaraForm):
    def __init__(self, camara_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.camara_id = camara_id
        if camara_id:
            self.codigo.validators = [
                v if not callable(v) or v.__name__ != '_validate'
                else validate_codigo_unico(exclude_id=camara_id)
                for v in self.codigo.validators[:-1]
            ] + [validate_codigo_unico(exclude_id=camara_id)]

            self.nombre.validators = [
                v if not callable(v) or v.__name__ != '_validate'
                else validate_nombre_unico(exclude_id=camara_id)
                for v in self.nombre.validators[:-1]
            ] + [validate_nombre_unico(exclude_id=camara_id)]