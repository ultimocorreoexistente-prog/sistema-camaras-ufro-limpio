import pandas as pd
from datetime import datetime
from app import app, db
<<<<<<< HEAD
<<<<<<< HEAD
from models import (Usuario, Ubicacion, Camara, Gabinete, Switch, Puerto_Switch,
UPS, NVR_DVR, Fuente_Poder, Catalogo_Tipo_Falla, Falla,
Mantenimiento, Equipo_Tecnico)
=======
=======
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
from sqlalchemy import text
from models import (
    Usuario, Ubicacion, Camara, Gabinete, Switch, PuertoSwitch,
    UPS, NVR, FuentePoder, CatalogoTipoFalla, Falla,
    Mantenimiento, EquipoTecnico, Fotografia
)
<<<<<<< HEAD
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
=======
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
from werkzeug.security import generate_password_hash
import os
import re


def safe_int(value):
<<<<<<< HEAD
<<<<<<< HEAD
"""Convierte valor a int manejando NaN"""
try:
if pd.isna(value):
return None
return int(value)
except:
return None
=======
=======
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
    """Convierte valor a int manejando NaN"""
    try:
        if pd.isna(value):
            return None
        if isinstance(value, (str, float)):
            return int(float(value)) if str(value).replace('.', '', 1).isdigit() else None
        return int(value)
    except:
        return None
<<<<<<< HEAD
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4


def safe_float(value):
"""Convierte valor a float manejando NaN"""
try:
if pd.isna(value):
return None
return float(value)
except:
return None


def safe_str(value):
"""Convierte valor a string manejando NaN"""
if pd.isna(value):
return None
return str(value).strip() if str(value).strip() else None


def safe_date(value):
<<<<<<< HEAD
"""Convierte valor a date manejando NaN"""
try:
if pd.isna(value):
return None
if isinstance(value, str):
return datetime.strptime(value, '%Y-%m-%d').date()
return value.date() if hasattr(value, 'date') else None
except:
return None
=======
=======


def safe_float(value):
    """Convierte valor a float manejando NaN"""
    try:
        if pd.isna(value):
            return None
        return float(value)
    except:
        return None


def safe_str(value):
    """Convierte valor a string manejando NaN"""
    if pd.isna(value):
        return None
    return str(value).strip() if str(value).strip() else None


def safe_date(value):
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
    """Convierte valor a date manejando NaN"""
    try:
        if pd.isna(value):
            return None
        if isinstance(value, str):
            formatos = ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y']
            for fmt in formatos:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
            if isinstance(value, (int, float)) and value > 0:
                return pd.to_datetime(value, unit='D', origin='1899-12-30').date()
        return value.date() if hasattr(value, 'date') else None
    except:
        return None
<<<<<<< HEAD
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4


def validar_falla_duplicada(equipo_tipo, equipo_id):
"""Valida si se puede insertar una nueva falla"""
falla_activa = Falla.query.filter_by(
equipo_tipo=equipo_tipo,
equipo_id=equipo_id
).filter(
Falla.estado.in_(['Pendiente', 'Asignada', 'En Proceso'])
).order_by(Falla.fecha_reporte.desc()).first()

if falla_activa:
return False, f'Falla duplicada rechazada (Equipo {equipo_tipo} ID {equipo_id})'
return True, 'OK'


def extraer_fallas_informe():
<<<<<<< HEAD
"""Extrae fallas del INFORME DE CAMARAS.docx (convertido a markdown)"""
informe_path = 'docs/INFORME_DE_CAMARAS.md'
fallas_extraidas = []

if not os.path.exists(informe_path):
print(f" Archivo {informe_path} no encontrado")
return fallas_extraidas

with open(informe_path, 'r', encoding='utf-8') as f:
contenido = f.read()

# Patrones de fallas comunes en las observaciones
patrones_fallas = [
(r'([\w\-_\.]+)\s*\(Telas de araña\)', 'Telas de araña', 'Baja'),
(r'([\w\-_\.]+)\s*\(Borrosa\)', 'Imagen borrosa', 'Media'),
(r'([\w\-_\.]+)\s*\(mica rallada\)', 'Mica rallada', 'Media'),
(r'([\w\-_\.]+)\s*\(DESCONECTADA\)', 'Desconectada', 'Alta'),
(r'([\w\-_\.]+)\s*\(mancha en el lente\)', 'Mancha en lente', 'Baja'),
(r'([\w\-_\.]+)\s*\(empañada\)', 'Empañada', 'Baja'),
(r'([\w\-_\.]+)\s*\(EMPAÑADA\)', 'Empañada', 'Baja'),
(r'([\w\-_\.]+).*?sin conexión', 'Sin conexión', 'Alta'),
(r'([\w\-_\.]+).*?intermitencia', 'Intermitencia', 'Media'),
(r'Camera\s+(\d+).*?\(Borrosa\)', 'Imagen borrosa', 'Media'),
(r'([\w\-_\.]+).*?destruida', 'Vandalismo/Destruida', 'Crítica'),
(r'([\w\-_\.]+).*?borrosa', 'Imagen borrosa', 'Media'),
]

lineas = contenido.split('\n')
zona_actual = 'Desconocida'

for linea in lineas:
# Detectar zona/ubicación (primera columna de la tabla)
if '|' in linea and not linea.strip().startswith('| |'):
partes = linea.split('|')
if len(partes) >= 5:
zona_candidata = partes[0].strip()
if zona_candidata and zona_candidata = '' and not zona_candidata.isspace():
zona_actual = zona_candidata

observacion = partes[4].strip() if len(partes) > 4 else ''

# Buscar fallas en la observación
if observacion and observacion = 'OBSERVACION':
for patron, tipo_falla, prioridad in patrones_fallas:
matches = re.finditer(patron, observacion, re.IGNORECASE)
for match in matches:
nombre_camara = match.group(1)
fallas_extraidas.append({
'nombre_camara': nombre_camara,
'tipo_falla': tipo_falla,
'prioridad': prioridad,
'zona': zona_actual,
'observacion': observacion[:00]
})

return fallas_extraidas
=======
=======


def validar_falla_duplicada(equipo_tipo, equipo_id):
    """Valida si se puede insertar una nueva falla"""
    falla_activa = Falla.query.filter_by(
        equipo_tipo=equipo_tipo,
        equipo_id=equipo_id
    ).filter(
        Falla.estado.in_(['Pendiente', 'Asignada', 'En Proceso'])
    ).order_by(Falla.fecha_reporte.desc()).first()
    
    if falla_activa:
        return False, f'Falla duplicada rechazada (Equipo {equipo_tipo} ID {equipo_id})'
    return True, 'OK'


def extraer_fallas_informe():
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
    """Extrae fallas del INFORME DE CAMARAS.docx (convertido a markdown)"""
    informe_path = 'docs/INFORME_DE_CAMARAS.md'
    fallas_extraidas = []
    
    if not os.path.exists(informe_path):
        print(f"    ⚠ Archivo {informe_path} no encontrado")
        return fallas_extraidas
    
    with open(informe_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    patrones_fallas = [
        (r'([\w\-_\.]+)\s*\(Telas de araña\)', 'Telas de araña', 'Baja'),
        (r'([\w\-_\.]+)\s*\(Borrosa\)', 'Imagen borrosa', 'Media'),
        (r'([\w\-_\.]+)\s*\(mica rallada\)', 'Mica rallada', 'Media'),
        (r'([\w\-_\.]+)\s*\(DESCONECTADA\)', 'Desconectada', 'Alta'),
        (r'([\w\-_\.]+)\s*\(mancha en el lente\)', 'Mancha en lente', 'Baja'),
        (r'([\w\-_\.]+)\s*\(empañada\)', 'Empañada', 'Baja'),
        (r'([\w\-_\.]+).*?sin conexión', 'Sin conexión', 'Alta'),
        (r'([\w\-_\.]+).*?intermitencia', 'Intermitencia', 'Media'),
        (r'Camera\s+(\d+).*?\(Borrosa\)', 'Imagen borrosa', 'Media'),
        (r'([\w\-_\.]+).*?destruida', 'Vandalismo/Destruida', 'Crítica'),
        (r'([\w\-_\.]+).*?borrosa', 'Imagen borrosa', 'Media'),
    ]
    
    lineas = contenido.split('\n')
    zona_actual = 'Desconocida'
    
    for linea in lineas:
        if '|' in linea and not linea.strip().startswith('|---|'):
            partes = [p.strip() for p in linea.split('|') if p.strip()]
            if len(partes) >= 5:
                zona_candidata = partes[0].strip()
                if zona_candidata and zona_candidata.lower() not in ('ubicacion', 'zona'):
                    zona_actual = zona_candidata
                observacion = partes[4].strip() if len(partes) > 4 else ''
                if observacion and observacion.upper() != 'OBSERVACION':
                    for patron, tipo_falla, prioridad in patrones_fallas:
                        matches = re.finditer(patron, observacion, re.IGNORECASE)
                        for match in matches:
                            nombre_camara = match.group(1).strip()
                            fallas_extraidas.append({
                                'nombre_camara': nombre_camara,
                                'tipo_falla': tipo_falla,
                                'prioridad': prioridad,
                                'zona': zona_actual,
                                'observacion': observacion[:200]
                            })
    return fallas_extraidas
<<<<<<< HEAD
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4


def migrar_datos():
<<<<<<< HEAD
"""Migra todas las planillas Excel a la base de datos"""

print("=== INICIANDO MIGRACIÓN DE DATOS ===\n")

base_path = 'planillas/'

try:
# 1. UBICACIONES
print("1. Migrando Ubicaciones...")
df = pd.read_excel(f'{base_path}Ubicaciones.xlsx')
count = 0
for _, row in df.iterrows():
ubicacion = Ubicacion(
campus=safe_str(row.get('Campus')),
edificio=safe_str(row.get('Edificio')),
piso=safe_str(row.get('Piso')),
descripcion=safe_str(row.get('Descripcion')),
latitud=safe_float(row.get('Latitud')),
longitud=safe_float(row.get('Longitud')),
activo=True
)
db.session.add(ubicacion)
count += 1
db.session.commit()
print(f" {count} ubicaciones insertadas\n")

# . EQUIPOS TÉCNICOS
print(". Migrando Equipos Técnicos...")
df = pd.read_excel(f'{base_path}Equipos_Tecnicos.xlsx')
count = 0
for _, row in df.iterrows():
equipo = Equipo_Tecnico(
nombre=safe_str(row.get('Nombre')),
apellido=safe_str(row.get('Apellido')),
especialidad=safe_str(row.get('Especialidad')),
telefono=safe_str(row.get('Telefono')),
email=safe_str(row.get('Email')),
estado=safe_str(row.get('Estado', 'Activo')),
fecha_ingreso=safe_date(row.get('Fecha_Ingreso'))
)
db.session.add(equipo)
count += 1
db.session.commit()
print(f" {count} equipos técnicos insertados\n")

# 3. CATÁLOGO TIPOS DE FALLAS
print("3. Migrando Catálogo de Tipos de Fallas...")
df = pd.read_excel(f'{base_path}Catalogo_Tipos_Fallas.xlsx')
count = 0
for _, row in df.iterrows():
tipo_falla = Catalogo_Tipo_Falla(
nombre=safe_str(row.get('Nombre')),
categoria=safe_str(row.get('Categoria')),
descripcion=safe_str(row.get('Descripcion')),
gravedad=safe_str(row.get('Gravedad', 'Media')),
tiempo_estimado_resolucion=safe_int(row.get('Tiempo_Estimado_Resolucion'))
)
db.session.add(tipo_falla)
count += 1
db.session.commit()
print(f" {count} tipos de fallas insertados\n")

# 4. GABINETES
print("4. Migrando Gabinetes...")
df = pd.read_excel(f'{base_path}Gabinetes.xlsx')
count = 0
for _, row in df.iterrows():
gabinete = Gabinete(
codigo=safe_str(row.get('Codigo')),
nombre=safe_str(row.get('Nombre')),
tipo_ubicacion_general=safe_str(row.get('Tipo_Ubicacion_General')),
tipo_ubicacion_detallada=safe_str(row.get('Tipo_Ubicacion_Detallada')),
ubicacion_id=safe_int(row.get('ID_Ubicacion')),
capacidad=safe_int(row.get('Capacidad')),
tiene_ups=bool(row.get('Tiene_UPS', False)),
tiene_switch=bool(row.get('Tiene_Switch', False)),
tiene_nvr=bool(row.get('Tiene_NVR', False)),
conexion_fibra=bool(row.get('Conexion_Fibra', False)),
estado=safe_str(row.get('Estado', 'Activo')),
fecha_alta=safe_date(row.get('Fecha_Alta')),
observaciones=safe_str(row.get('Observaciones')),
latitud=safe_float(row.get('Latitud')),
longitud=safe_float(row.get('Longitud'))
)
db.session.add(gabinete)
count += 1
db.session.commit()
print(f" {count} gabinetes insertados\n")

# 5. SWITCHES
print("5. Migrando Switches...")
df = pd.read_excel(f'{base_path}Switches.xlsx')
count = 0
for _, row in df.iterrows():
switch = Switch(
codigo=safe_str(row.get('Codigo')),
nombre=safe_str(row.get('Nombre')),
ip=safe_str(row.get('IP')),
modelo=safe_str(row.get('Modelo')),
marca=safe_str(row.get('Marca')),
numero_serie=safe_str(row.get('Numero_Serie')),
gabinete_id=safe_int(row.get('ID_Gabinete')),
puertos_totales=safe_int(row.get('Puertos_Totales')),
puertos_usados=safe_int(row.get('Puertos_Usados', 0)),
puertos_disponibles=safe_int(row.get('Puertos_Disponibles')),
capacidad_poe=bool(row.get('Capacidad_PoE', False)),
estado=safe_str(row.get('Estado', 'Activo')),
fecha_alta=safe_date(row.get('Fecha_Alta')),
observaciones=safe_str(row.get('Observaciones')),
latitud=safe_float(row.get('Latitud')),
longitud=safe_float(row.get('Longitud'))
)
db.session.add(switch)
count += 1
db.session.commit()
print(f" {count} switches insertados\n")

# 6. PUERTOS SWITCH
print("6. Migrando Puertos de Switch...")
df = pd.read_excel(f'{base_path}Puertos_Switch.xlsx')
count = 0
for _, row in df.iterrows():
puerto = Puerto_Switch(
switch_id=safe_int(row.get('ID_Switch')),
numero_puerto=safe_int(row.get('Numero_Puerto')),
camara_id=safe_int(row.get('ID_Camara')),
ip_dispositivo=safe_str(row.get('IP_Dispositivo')),
estado=safe_str(row.get('Estado', 'Disponible')),
tipo_conexion=safe_str(row.get('Tipo_Conexion')),
nvr_id=safe_int(row.get('ID_NVR')),
puerto_nvr=safe_str(row.get('Puerto_NVR'))
)
db.session.add(puerto)
count += 1
db.session.commit()
print(f" {count} puertos de switch insertados\n")

# 7. UPS
print("7. Migrando UPS...")
df = pd.read_excel(f'{base_path}UPS.xlsx')
count = 0
for _, row in df.iterrows():
ups = UPS(
codigo=safe_str(row.get('Codigo')),
modelo=safe_str(row.get('Modelo')),
marca=safe_str(row.get('Marca')),
capacidad_va=safe_int(row.get('Capacidad_VA')),
numero_baterias=safe_int(row.get('Numero_Baterias')),
ubicacion_id=safe_int(row.get('ID_Ubicacion')),
gabinete_id=safe_int(row.get('ID_Gabinete')),
equipos_que_alimenta=safe_str(row.get('Equipos_Que_Alimenta')),
estado=safe_str(row.get('Estado', 'Activo')),
fecha_alta=safe_date(row.get('Fecha_Alta')),
observaciones=safe_str(row.get('Observaciones')),
latitud=safe_float(row.get('Latitud')),
longitud=safe_float(row.get('Longitud'))
)
db.session.add(ups)
count += 1
db.session.commit()
print(f" {count} UPS insertados\n")

# 8. NVR/DVR
print("8. Migrando NVR/DVR...")
df = pd.read_excel(f'{base_path}NVR_DVR.xlsx')
count = 0
for _, row in df.iterrows():
nvr = NVR_DVR(
codigo=safe_str(row.get('Codigo')),
tipo=safe_str(row.get('Tipo', 'NVR')),
modelo=safe_str(row.get('Modelo')),
marca=safe_str(row.get('Marca')),
canales_totales=safe_int(row.get('Canales_Totales')),
canales_usados=safe_int(row.get('Canales_Usados', 0)),
ip=safe_str(row.get('IP')),
ubicacion_id=safe_int(row.get('ID_Ubicacion')),
gabinete_id=safe_int(row.get('ID_Gabinete')),
estado=safe_str(row.get('Estado', 'Activo')),
fecha_alta=safe_date(row.get('Fecha_Alta')),
observaciones=safe_str(row.get('Observaciones')),
latitud=safe_float(row.get('Latitud')),
longitud=safe_float(row.get('Longitud'))
)
db.session.add(nvr)
count += 1
db.session.commit()
print(f" {count} NVR/DVR insertados\n")

# 9. FUENTES DE PODER
print("9. Migrando Fuentes de Poder...")
df = pd.read_excel(f'{base_path}Fuentes_Poder.xlsx')
count = 0
for _, row in df.iterrows():
fuente = Fuente_Poder(
codigo=safe_str(row.get('Codigo')),
modelo=safe_str(row.get('Modelo')),
voltaje=safe_str(row.get('Voltaje')),
amperaje=safe_str(row.get('Amperaje')),
equipos_que_alimenta=safe_str(row.get('Equipos_Que_Alimenta')),
ubicacion_id=safe_int(row.get('ID_Ubicacion')),
gabinete_id=safe_int(row.get('ID_Gabinete')),
estado=safe_str(row.get('Estado', 'Activo')),
fecha_alta=safe_date(row.get('Fecha_Alta')),
observaciones=safe_str(row.get('Observaciones'))
)
db.session.add(fuente)
count += 1
db.session.commit()
print(f" {count} fuentes de poder insertadas\n")

# 10. CÁMARAS (474 unidades)
print("10. Migrando Cámaras...")
df = pd.read_excel(f'{base_path}Listadecámaras_modificada.xlsx')
count = 0
for _, row in df.iterrows():
camara = Camara(
codigo=safe_str(row.get('Codigo')),
nombre=safe_str(row.get('Nombre')),
ip=safe_str(row.get('IP')),
modelo=safe_str(row.get('Modelo')),
fabricante=safe_str(row.get('Fabricante')),
tipo_camara=safe_str(row.get('Tipo_Camara', 'Domo')),
ubicacion_id=safe_int(row.get('ID_Ubicacion')),
gabinete_id=safe_int(row.get('ID_Gabinete')),
switch_id=safe_int(row.get('ID_Switch')),
puerto_switch_id=safe_int(row.get('ID_Puerto_Switch')),
nvr_id=safe_int(row.get('ID_NVR')),
puerto_nvr=safe_str(row.get('Puerto_NVR')),
requiere_poe_adicional=bool(row.get('Requiere_PoE_Adicional', False)),
tipo_conexion=safe_str(row.get('Tipo_Conexion')),
estado=safe_str(row.get('Estado', 'Activo')),
fecha_alta=safe_date(row.get('Fecha_Alta')),
instalador=safe_str(row.get('Instalador')),
fecha_instalacion=safe_date(row.get('Fecha_Instalacion')),
observaciones=safe_str(row.get('Observaciones')),
latitud=safe_float(row.get('Latitud')),
longitud=safe_float(row.get('Longitud'))
)
db.session.add(camara)
count += 1
db.session.commit()
print(f" {count} cámaras insertadas\n")

# 11. FALLAS (con validación anti-duplicados)
print("11. Migrando Fallas (con validación anti-duplicados)...")

# Obtener usuario admin para reportado_por
admin_user = Usuario.query.filter_by(username='admin').first()
if not admin_user:
print(" Usuario admin no existe, creando...")
admin_user = Usuario(
username='admin',
rol='admin',
nombre_completo='Administrador',
activo=True
)
admin_user.set_password('admin13')
db.session.add(admin_user)
db.session.commit()

count = 0
rechazadas = 0

# Fallas_Actualizada.xlsx
try:
df1 = pd.read_excel(f'{base_path}Fallas_Actualizada.xlsx')
for _, row in df1.iterrows():
equipo_tipo = safe_str(row.get('Equipo_Tipo', 'Camara'))
equipo_id = safe_int(row.get('Equipo_ID'))

if equipo_id:
# Validar anti-duplicados
permitir, mensaje = validar_falla_duplicada(equipo_tipo, equipo_id)
if not permitir:
rechazadas += 1
continue

falla = Falla(
equipo_tipo=equipo_tipo,
equipo_id=equipo_id,
tipo_falla_id=safe_int(row.get('Tipo_Falla_ID')),
descripcion=safe_str(row.get('Descripcion')),
prioridad=safe_str(row.get('Prioridad', 'Media')),
fecha_reporte=datetime.now(),
reportado_por_id=admin_user.id,
estado=safe_str(row.get('Estado', 'Pendiente'))
)
db.session.add(falla)
count += 1
except Exception as e:
print(f" Error procesando Fallas_Actualizada.xlsx: {e}")

# Ejemplos_Fallas_Reales.xlsx
try:
df = pd.read_excel(f'{base_path}Ejemplos_Fallas_Reales.xlsx')
for _, row in df.iterrows():
equipo_tipo = safe_str(row.get('Equipo_Tipo', 'Camara'))
equipo_id = safe_int(row.get('Equipo_ID'))

if equipo_id:
# Validar anti-duplicados
permitir, mensaje = validar_falla_duplicada(equipo_tipo, equipo_id)
if not permitir:
rechazadas += 1
continue

falla = Falla(
equipo_tipo=equipo_tipo,
equipo_id=equipo_id,
tipo_falla_id=safe_int(row.get('Tipo_Falla_ID')),
descripcion=safe_str(row.get('Descripcion')),
prioridad=safe_str(row.get('Prioridad', 'Media')),
fecha_reporte=datetime.now(),
reportado_por_id=admin_user.id,
estado=safe_str(row.get('Estado', 'Pendiente'))
)
db.session.add(falla)
count += 1
except Exception as e:
print(f" Error procesando Ejemplos_Fallas_Reales.xlsx: {e}")

# INFORME DE CAMARAS - Fallas documentadas 1-10-05
print("\n Extrayendo fallas del INFORME DE CAMARAS (1-10-05)...")
try:
fallas_informe = extraer_fallas_informe()
print(f" Total fallas extraídas del informe: {len(fallas_informe)}")

if fallas_informe:
# Mapear tipos de falla a IDs del catálogo
tipo_falla_map = {
'Telas de araña': 1, # Limpieza
'Imagen borrosa': 1, # Limpieza
'Mica rallada': , # Reparación
'Desconectada': 3, # Técnica
'Mancha en lente': 1, # Limpieza
'Empañada': 1, # Limpieza
'Sin conexión': 3, # Técnica
'Intermitencia': 3, # Técnica
'Vandalismo/Destruida': # Reparación
}

informe_insertadas = 0
informe_rechazadas = 0

for falla_info in fallas_informe:
# Buscar cámara por nombre
camara = Camara.query.filter(
Camara.nombre.ilike(f"%{falla_info['nombre_camara']}%")
).first()

if not camara:
# Intentar por código
camara = Camara.query.filter(
Camara.codigo.ilike(f"%{falla_info['nombre_camara']}%")
).first()

if camara:
# Validar anti-duplicados
permitir, mensaje = validar_falla_duplicada('Camara', camara.id)
if not permitir:
informe_rechazadas += 1
continue

# Crear falla
tipo_falla_id = tipo_falla_map.get(falla_info['tipo_falla'], 1)

falla = Falla(
equipo_tipo='Camara',
equipo_id=camara.id,
tipo_falla_id=tipo_falla_id,
descripcion=f"{falla_info['tipo_falla']} en {camara.nombre}",
prioridad=falla_info['prioridad'],
fecha_reporte=datetime(2005, 10, 1), # Fecha del informe
reportado_por_id=admin_user.id,
estado='Pendiente',
observaciones=falla_info['observacion']
)
db.session.add(falla)
informe_insertadas += 1

db.session.commit()
count += informe_insertadas
rechazadas += informe_rechazadas
print(f" {informe_insertadas} fallas del informe insertadas")
print(f" {informe_rechazadas} fallas del informe rechazadas por duplicado")
except Exception as e:
print(f" Error procesando INFORME DE CAMARAS: {e}")

db.session.commit()
print(f"\n TOTAL: {count} fallas insertadas ({rechazadas} rechazadas por duplicado)\n")

# 1. MANTENIMIENTOS
print("1. Migrando Mantenimientos...")
try:
df = pd.read_excel(f'{base_path}Mantenimientos.xlsx')
count = 0
for _, row in df.iterrows():
mantenimiento = Mantenimiento(
equipo_tipo=safe_str(row.get('Equipo_Tipo', 'Camara')),
equipo_id=safe_int(row.get('Equipo_ID')),
tipo=safe_str(row.get('Tipo', 'Preventivo')),
fecha=datetime.now(),
tecnico_id=admin_user.id,
descripcion=safe_str(row.get('Descripcion')),
materiales_utilizados=safe_str(row.get('Materiales_Utilizados')),
tiempo_ejecucion_horas=safe_float(row.get('Tiempo_Ejecucion_Horas')),
costo=safe_float(row.get('Costo')),
observaciones=safe_str(row.get('Observaciones'))
)
db.session.add(mantenimiento)
count += 1
db.session.commit()
print(f" {count} mantenimientos insertados\n")
except Exception as e:
print(f" Error procesando Mantenimientos.xlsx: {e}\n")

print("=== MIGRACIÓN COMPLETADA EXITOSAMENTE ===")

# Resumen final
print("\n=== RESUMEN DE DATOS ===")
print(f"Ubicaciones: {Ubicacion.query.count()}")
print(f"Equipos Técnicos: {Equipo_Tecnico.query.count()}")
print(f"Tipos de Fallas: {Catalogo_Tipo_Falla.query.count()}")
print(f"Gabinetes: {Gabinete.query.count()}")
print(f"Switches: {Switch.query.count()}")
print(f"Puertos Switch: {Puerto_Switch.query.count()}")
print(f"UPS: {UPS.query.count()}")
print(f"NVR/DVR: {NVR_DVR.query.count()}")
print(f"Fuentes de Poder: {Fuente_Poder.query.count()}")
print(f"Cámaras: {Camara.query.count()}")
print(f"Fallas: {Falla.query.count()}")
print(f"Mantenimientos: {Mantenimiento.query.count()}")
print(f"Usuarios: {Usuario.query.count()}")

except Exception as e:
print(f"\n ERROR EN MIGRACIÓN: {e}")
db.session.rollback()
raise
=======
=======


def migrar_datos():
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
    """Migra todas las planillas Excel a la base de datos"""
    print("=== INICIANDO MIGRACIÓN DE DATOS ===\n")
    base_path = 'planillas/'
    
    try:
        # 1. UBICACIONES
        print("1. Migrando Ubicaciones...")
        df = pd.read_excel(f'{base_path}Ubicaciones.xlsx')
        count = 0
        for _, row in df.iterrows():
            ubicacion = Ubicacion(
                campus=safe_str(row.get('Campus')),
                edificio=safe_str(row.get('Edificio')),
                piso=safe_str(row.get('Piso')),
                descripcion=safe_str(row.get('Descripcion')),
                latitud=safe_float(row.get('Latitud')),
                longitud=safe_float(row.get('Longitud')),
                activo=True
            )
            db.session.add(ubicacion)
            count += 1
        db.session.commit()
        print(f"    ✓ {count} ubicaciones insertadas\n")
        
        # 2. EQUIPOS TÉCNICOS
        print("2. Migrando Equipos Técnicos...")
        df = pd.read_excel(f'{base_path}Equipos_Tecnicos.xlsx')
        count = 0
        for _, row in df.iterrows():
            equipo = EquipoTecnico(
                nombre=safe_str(row.get('Nombre')),
                apellido=safe_str(row.get('Apellido')),
                especialidad=safe_str(row.get('Especialidad')),
                telefono=safe_str(row.get('Telefono')),
                email=safe_str(row.get('Email')),
                estado=safe_str(row.get('Estado', 'Activo')),
                fecha_ingreso=safe_date(row.get('Fecha_Ingreso'))
            )
            db.session.add(equipo)
            count += 1
        db.session.commit()
        print(f"    ✓ {count} equipos técnicos insertados\n")
        
        # 3. CATÁLOGO TIPOS DE FALLAS
        print("3. Migrando Catálogo de Tipos de Fallas...")
        df = pd.read_excel(f'{base_path}Catalogo_Tipos_Fallas.xlsx')
        count = 0
        for _, row in df.iterrows():
            tipo_falla = CatalogoTipoFalla(
                nombre=safe_str(row.get('Nombre')),
                categoria=safe_str(row.get('Categoria')),
                descripcion=safe_str(row.get('Descripcion')),
                gravedad=safe_str(row.get('Gravedad', 'Media')),
                tiempo_estimado_resolucion=safe_int(row.get('Tiempo_Estimado_Resolucion'))
            )
            db.session.add(tipo_falla)
            count += 1
        db.session.commit()
        print(f"    ✓ {count} tipos de fallas insertados\n")
        
        # 4. GABINETES
        print("4. Migrando Gabinetes...")
        df = pd.read_excel(f'{base_path}Gabinetes.xlsx')
        count = 0
        for _, row in df.iterrows():
            gabinete = Gabinete(
                codigo=safe_str(row.get('Codigo')),
                nombre=safe_str(row.get('Nombre')),
                tipo_ubicacion_general=safe_str(row.get('Tipo_Ubicacion_General')),
                tipo_ubicacion_detallada=safe_str(row.get('Tipo_Ubicacion_Detallada')),
                ubicacion_id=safe_int(row.get('ID_Ubicacion')),
                capacidad=safe_int(row.get('Capacidad')),
                tiene_ups=bool(row.get('Tiene_UPS', False)),
                tiene_switch=bool(row.get('Tiene_Switch', False)),
                tiene_nvr=bool(row.get('Tiene_NVR', False)),
                conexion_fibra=bool(row.get('Conexion_Fibra', False)),
                estado=safe_str(row.get('Estado', 'Activo')),
                fecha_alta=safe_date(row.get('Fecha_Alta')),
                observaciones=safe_str(row.get('Observaciones')),
                latitud=safe_float(row.get('Latitud')),
                longitud=safe_float(row.get('Longitud'))
            )
            db.session.add(gabinete)
            count += 1
        db.session.commit()
        print(f"    ✓ {count} gabinetes insertados\n")
        
        # 5. SWITCHES
        print("5. Migrando Switches...")
        df = pd.read_excel(f'{base_path}Switches.xlsx')
        count = 0
        for _, row in df.iterrows():
            switch = Switch(
                codigo=safe_str(row.get('Codigo')),
                nombre=safe_str(row.get('Nombre')),
                ip=safe_str(row.get('IP')),
                modelo=safe_str(row.get('Modelo')),
                marca=safe_str(row.get('Marca')),
                numero_serie=safe_str(row.get('Numero_Serie')),
                gabinete_id=safe_int(row.get('ID_Gabinete')),
                puertos_totales=safe_int(row.get('Puertos_Totales')),
                puertos_usados=safe_int(row.get('Puertos_Usados', 0)),
                puertos_disponibles=safe_int(row.get('Puertos_Disponibles')),
                capacidad_poe=bool(row.get('Capacidad_PoE', False)),
                estado=safe_str(row.get('Estado', 'Activo')),
                fecha_alta=safe_date(row.get('Fecha_Alta')),
                observaciones=safe_str(row.get('Observaciones')),
                latitud=safe_float(row.get('Latitud')),
                longitud=safe_float(row.get('Longitud'))
            )
            db.session.add(switch)
            count += 1
        db.session.commit()
        print(f"    ✓ {count} switches insertados\n")
        
        # 6. PUERTOS SWITCH
        print("6. Migrando Puertos de Switch...")
        df = pd.read_excel(f'{base_path}Puertos_Switch.xlsx')
        count = 0
        for _, row in df.iterrows():
            puerto = PuertoSwitch(
                switch_id=safe_int(row.get('ID_Switch')),
                numero_puerto=safe_int(row.get('Numero_Puerto')),
                camara_id=safe_int(row.get('ID_Camara')),
                ip_dispositivo=safe_str(row.get('IP_Dispositivo')),
                estado=safe_str(row.get('Estado', 'Disponible')),
                tipo_conexion=safe_str(row.get('Tipo_Conexion')),
                nvr_id=safe_int(row.get('ID_NVR')),
                puerto_nvr=safe_str(row.get('Puerto_NVR'))
            )
            db.session.add(puerto)
            count += 1
        db.session.commit()
        print(f"    ✓ {count} puertos de switch insertados\n")
        
        # 7. UPS
        print("7. Migrando UPS...")
        df = pd.read_excel(f'{base_path}UPS.xlsx')
        count = 0
        for _, row in df.iterrows():
            ups = UPS(
                codigo=safe_str(row.get('Codigo')),
                modelo=safe_str(row.get('Modelo')),
                marca=safe_str(row.get('Marca')),
                capacidad_va=safe_int(row.get('Capacidad_VA')),
                numero_baterias=safe_int(row.get('Numero_Baterias')),
                ubicacion_id=safe_int(row.get('ID_Ubicacion')),
                gabinete_id=safe_int(row.get('ID_Gabinete')),
                equipos_que_alimenta=safe_str(row.get('Equipos_Que_Alimenta')),
                estado=safe_str(row.get('Estado', 'Activo')),
                fecha_alta=safe_date(row.get('Fecha_Alta')),
                observaciones=safe_str(row.get('Observaciones')),
                latitud=safe_float(row.get('Latitud')),
                longitud=safe_float(row.get('Longitud'))
            )
            db.session.add(ups)
            count += 1
        db.session.commit()
        print(f"    ✓ {count} UPS insertados\n")
        
        # 8. NVR/DVR
        print("8. Migrando NVR/DVR...")
        df = pd.read_excel(f'{base_path}NVR_DVR.xlsx')
        count = 0
        for _, row in df.iterrows():
            nvr = NVR(
                codigo=safe_str(row.get('Codigo')),
                tipo=safe_str(row.get('Tipo', 'NVR')),
                modelo=safe_str(row.get('Modelo')),
                marca=safe_str(row.get('Marca')),
                canales_totales=safe_int(row.get('Canales_Totales')),
                canales_usados=safe_int(row.get('Canales_Usados', 0)),
                ip=safe_str(row.get('IP')),
                ubicacion_id=safe_int(row.get('ID_Ubicacion')),
                gabinete_id=safe_int(row.get('ID_Gabinete')),
                estado=safe_str(row.get('Estado', 'Activo')),
                fecha_alta=safe_date(row.get('Fecha_Alta')),
                observaciones=safe_str(row.get('Observaciones')),
                latitud=safe_float(row.get('Latitud')),
                longitud=safe_float(row.get('Longitud'))
            )
            db.session.add(nvr)
            count += 1
        db.session.commit()
        print(f"    ✓ {count} NVR/DVR insertados\n")
        
        # 9. FUENTES DE PODER
        print("9. Migrando Fuentes de Poder...")
        df = pd.read_excel(f'{base_path}Fuentes_Poder.xlsx')
        count = 0
        for _, row in df.iterrows():
            fuente = FuentePoder(
                codigo=safe_str(row.get('Codigo')),
                modelo=safe_str(row.get('Modelo')),
                voltaje=safe_str(row.get('Voltaje')),
                amperaje=safe_str(row.get('Amperaje')),
                equipos_que_alimenta=safe_str(row.get('Equipos_Que_Alimenta')),
                ubicacion_id=safe_int(row.get('ID_Ubicacion')),
                gabinete_id=safe_int(row.get('ID_Gabinete')),
                estado=safe_str(row.get('Estado', 'Activo')),
                fecha_alta=safe_date(row.get('Fecha_Alta')),
                observaciones=safe_str(row.get('Observaciones'))
            )
            db.session.add(fuente)
            count += 1
        db.session.commit()
        print(f"    ✓ {count} fuentes de poder insertadas\n")
        
        # 10. CÁMARAS
        print("10. Migrando Cámaras...")
        df = pd.read_excel(f'{base_path}Listadecámaras_modificada.xlsx')
        count = 0
        for _, row in df.iterrows():
            camara = Camara(
                codigo=safe_str(row.get('Codigo')),
                nombre=safe_str(row.get('Nombre')),
                ip=safe_str(row.get('IP')),
                modelo=safe_str(row.get('Modelo')),
                fabricante=safe_str(row.get('Fabricante')),
                tipo_camara=safe_str(row.get('Tipo_Camara', 'Domo')),
                ubicacion_id=safe_int(row.get('ID_Ubicacion')),
                gabinete_id=safe_int(row.get('ID_Gabinete')),
                switch_id=safe_int(row.get('ID_Switch')),
                puerto_switch_id=safe_int(row.get('ID_Puerto_Switch')),
                nvr_id=safe_int(row.get('ID_NVR')),
                puerto_nvr=safe_str(row.get('Puerto_NVR')),
                requiere_poe_adicional=bool(row.get('Requiere_PoE_Adicional', False)),
                tipo_conexion=safe_str(row.get('Tipo_Conexion')),
                estado=safe_str(row.get('Estado', 'Activo')),
                fecha_alta=safe_date(row.get('Fecha_Alta')),
                instalador=safe_str(row.get('Instalador')),
                fecha_instalacion=safe_date(row.get('Fecha_Instalacion')),
                observaciones=safe_str(row.get('Observaciones')),
                latitud=safe_float(row.get('Latitud')),
                longitud=safe_float(row.get('Longitud'))
            )
            db.session.add(camara)
            count += 1
        db.session.commit()
        print(f"    ✓ {count} cámaras insertadas\n")
        
        # 11. FALLAS
        print("11. Migrando Fallas (con validación anti-duplicados)...")
        admin_user = Usuario.query.filter_by(username='admin').first()
        if not admin_user:
            print("    ⚠ Usuario admin no existe, creando...")
            admin_user = Usuario(
                username='admin',
                rol='admin',
                nombre_completo='Administrador',
                activo=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
        
        count = 0
        rechazadas = 0
        
        try:
            df1 = pd.read_excel(f'{base_path}Fallas_Actualizada.xlsx')
            for _, row in df1.iterrows():
                equipo_tipo = safe_str(row.get('Equipo_Tipo', 'Camara'))
                equipo_id = safe_int(row.get('Equipo_ID'))
                if equipo_id:
                    permitir, _ = validar_falla_duplicada(equipo_tipo, equipo_id)
                    if permitir:
                        falla = Falla(
                            equipo_tipo=equipo_tipo,
                            equipo_id=equipo_id,
                            tipo_falla_id=safe_int(row.get('Tipo_Falla_ID')),
                            descripcion=safe_str(row.get('Descripcion')),
                            prioridad=safe_str(row.get('Prioridad', 'Media')),
                            fecha_reporte=datetime.now(),
                            reportado_por_id=admin_user.id,
                            estado=safe_str(row.get('Estado', 'Pendiente'))
                        )
                        db.session.add(falla)
                        count += 1
                    else:
                        rechazadas += 1
        except Exception as e:
            print(f"    ⚠ Error procesando Fallas_Actualizada.xlsx: {e}")
        
        # 12. MANTENIMIENTOS
        print("12. Migrando Mantenimientos...")
        try:
            df = pd.read_excel(f'{base_path}Mantenimientos.xlsx')
            count = 0
            for _, row in df.iterrows():
                mantenimiento = Mantenimiento(
                    equipo_tipo=safe_str(row.get('Equipo_Tipo', 'Camara')),
                    equipo_id=safe_int(row.get('Equipo_ID')),
                    tipo=safe_str(row.get('Tipo', 'Preventivo')),
                    fecha=datetime.now(),
                    tecnico_id=admin_user.id,
                    descripcion=safe_str(row.get('Descripcion')),
                    materiales_utilizados=safe_str(row.get('Materiales_Utilizados')),
                    tiempo_ejecucion_horas=safe_float(row.get('Tiempo_Ejecucion_Horas')),
                    costo=safe_float(row.get('Costo')),
                    observaciones=safe_str(row.get('Observaciones'))
                )
                db.session.add(mantenimiento)
                count += 1
            db.session.commit()
            print(f"    ✓ {count} mantenimientos insertados\n")
        except Exception as e:
            print(f"    ⚠ Error procesando Mantenimientos.xlsx: {e}\n")
        
        print("=== MIGRACIÓN COMPLETADA EXITOSAMENTE ===")
        print("\n=== RESUMEN DE DATOS ===")
        print(f"Ubicaciones: {Ubicacion.query.count()}")
        print(f"Equipos Técnicos: {EquipoTecnico.query.count()}")
        print(f"Tipos de Fallas: {CatalogoTipoFalla.query.count()}")
        print(f"Gabinetes: {Gabinete.query.count()}")
        print(f"Switches: {Switch.query.count()}")
        print(f"Puertos Switch: {PuertoSwitch.query.count()}")
        print(f"UPS: {UPS.query.count()}")
        print(f"NVR: {NVR.query.count()}")
        print(f"Fuentes de Poder: {FuentePoder.query.count()}")
        print(f"Cámaras: {Camara.query.count()}")
        print(f"Fallas: {Falla.query.count()}")
        print(f"Mantenimientos: {Mantenimiento.query.count()}")
        print(f"Usuarios: {Usuario.query.count()}")
        
    except Exception as e:
        print(f"\n⚠⚠⚠ ERROR EN MIGRACIÓN: {e}")
        db.session.rollback()
        raise
<<<<<<< HEAD
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4


def ejecutar_migracion():
<<<<<<< HEAD
print("="*60)
print("INICIANDO MIGRACIÓN DE DATOS - SISTEMA CAMARAS UFRO")
print("="*60)

with app.app_context():
# Limpiar tablas existentes
print("\nLimpiando base de datos...")
db.drop_all()
db.create_all()
print(" Base de datos limpia")

# Crear usuarios por defecto primero
if Usuario.query.count() == 0:
print("Creando usuarios por defecto...\n")
usuarios = [
Usuario(username='admin', rol='admin', nombre_completo='Administrador', activo=True),
Usuario(username='supervisor', rol='supervisor', nombre_completo='Supervisor', activo=True),
Usuario(username='tecnico1', rol='tecnico', nombre_completo='Técnico 1', activo=True),
Usuario(username='visualizador', rol='visualizador', nombre_completo='Visualizador', activo=True)
]

passwords = ['admin13', 'super13', 'tecnico13', 'viz13']

for user, password in zip(usuarios, passwords):
user.set_password(password)
db.session.add(user)

db.session.commit()
print(" Usuarios creados\n")

# Ejecutar migraciones
try:
migrar_datos()

print("\n" + "="*60)
print("MIGRACIÓN COMPLETADA EXITOSAMENTE")
print("="*60)

except Exception as e:
print(f"\n Error durante la migración: {e}")
import traceback
traceback.print_exc()
=======
=======


def ejecutar_migracion():
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
    print("=" * 60)
    print("INICIANDO MIGRACIÓN DE DATOS - SISTEMA CAMARAS UFRO")
    print("=" * 60)
    
    with app.app_context():
        print("\nLimpiando base de datos...")
        try:
            # FIX: Cambiado a get_tables_for_bind() para evitar NoReferencedTableError
            # durante la ordenación de Foreign Keys. Se aplica DROP CASCADE directamente.
            with db.engine.execution_options(isolation_level="AUTOCOMMIT").connect() as conn:
                # Obtenemos las tablas en el orden inverso en el que fueron creadas por create_all (si es posible)
                # y forzamos el DROP CASCADE usando el nombre de la tabla.
                for tbl_name in reversed(db.get_tables_for_bind()):
                    conn.execute(text(f'DROP TABLE IF EXISTS "{tbl_name}" CASCADE'))
            print("✓ Base de datos limpia")
        except Exception as e:
            print(f"❌ Error al limpiar la base de datos: {e}")
            raise

        try:
            db.create_all()
            print("✓ Esquema creado")
        except Exception as e:
            print(f"❌ Error al crear el esquema: {e}")
            raise

        if Usuario.query.count() == 0:
            print("Creando usuarios por defecto...\n")
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
            print("✓ Usuarios creados\n")

        try:
            migrar_datos()
            print("\n" + "=" * 60)
            print("MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 60)
        except Exception as e:
            print(f"\n❌ Error durante la migración: {e}")
            import traceback
            traceback.print_exc()
<<<<<<< HEAD
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4


if __name__ == '__main__':
<<<<<<< HEAD
ejecutar_migracion()
=======
    ejecutar_migracion()
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
=======


if __name__ == '__main__':
    ejecutar_migracion()
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
