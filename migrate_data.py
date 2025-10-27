import pandas as pd
from datetime import datetime
from app import app, db
from models import (Usuario, Ubicacion, Camara, Gabinete, Switch, Puerto_Switch, 
                   UPS, NVR_DVR, Fuente_Poder, Catalogo_Tipo_Falla, Falla, 
                   Mantenimiento, Equipo_Tecnico)
from werkzeug.security import generate_password_hash
import os
import re

def safe_int(value):
    """Convierte valor a int manejando NaN"""
    try:
        if pd.isna(value):
            return None
        return int(value)
    except:
        return None

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
    """Convierte valor a date manejando NaN"""
    try:
        if pd.isna(value):
            return None
        if isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d').date()
        return value.date() if hasattr(value, 'date') else None
    except:
        return None

def verificar_existe_registro(modelo, **kwargs):
    """Verifica si ya existe un registro con los parámetros dados"""
    query = modelo.query
    for key, value in kwargs.items():
        if value is not None:
            query = query.filter(getattr(modelo, key) == value)
    return query.first() is not None

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
    """Extrae fallas del INFORME DE CAMARAS.docx (convertido a markdown)"""
    informe_path = '../docs/INFORME_DE_CAMARAS.md'
    fallas_extraidas = []
    
    if not os.path.exists(informe_path):
        print(f"   ⚠ Archivo {informe_path} no encontrado")
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
        if '|' in linea and not linea.strip().startswith('|  |'):
            partes = linea.split('|')
            if len(partes) >= 5:
                zona_candidata = partes[0].strip()
                if zona_candidata and zona_candidata != '' and not zona_candidata.isspace():
                    zona_actual = zona_candidata
                
                observacion = partes[4].strip() if len(partes) > 4 else ''
                
                # Buscar fallas en la observación
                if observacion and observacion != 'OBSERVACION':
                    for patron, tipo_falla, prioridad in patrones_fallas:
                        matches = re.finditer(patron, observacion, re.IGNORECASE)
                        for match in matches:
                            nombre_camara = match.group(1)
                            fallas_extraidas.append({
                                'nombre_camara': nombre_camara,
                                'tipo_falla': tipo_falla,
                                'prioridad': prioridad,
                                'zona': zona_actual,
                                'observacion': observacion[:200]
                            })
    
    return fallas_extraidas

def migrar_datos():
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
                piso=safe_str(row.get('Piso/Nivel')),
                descripcion=safe_str(row.get('Zona')),
                latitud=safe_float(row.get('Latitud')),
                longitud=safe_float(row.get('Longitud')),
                activo=True
            )
            db.session.add(ubicacion)
            count += 1
        db.session.commit()
        print(f"   ✓ {count} ubicaciones insertadas\n")
        
        # 2. EQUIPOS TÉCNICOS (Personal - crear algunos registros de ejemplo)
        print("2. Creando Personal Técnico...")
        personal_ejemplo = [
            {
                'nombre': 'Carlos',
                'apellido': 'Rodríguez',
                'especialidad': 'Cámaras de Seguridad',
                'telefono': '+56912345678',
                'email': 'carlos.rodriguez@ufro.cl',
                'estado': 'Activo'
            },
            {
                'nombre': 'María',
                'apellido': 'González',
                'especialidad': 'Redes y Conectividad',
                'telefono': '+56987654321',
                'email': 'maria.gonzalez@ufro.cl',
                'estado': 'Activo'
            },
            {
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'especialidad': 'Mantenimiento Preventivo',
                'telefono': '+56911223344',
                'email': 'juan.perez@ufro.cl',
                'estado': 'Activo'
            }
        ]
        
        count = 0
        for personal in personal_ejemplo:
            equipo = Equipo_Tecnico(
                nombre=personal['nombre'],
                apellido=personal['apellido'],
                especialidad=personal['especialidad'],
                telefono=personal['telefono'],
                email=personal['email'],
                estado=personal['estado'],
                fecha_ingreso=datetime.now().date()
            )
            db.session.add(equipo)
            count += 1
        db.session.commit()
        print(f"   ✓ {count} personal técnico creado\n")
        
        # 3. CATÁLOGO TIPOS DE FALLAS
        print("3. Migrando Catálogo de Tipos de Fallas...")
        df = pd.read_excel(f'{base_path}Catalogo_Tipos_Fallas.xlsx')
        count = 0
        for _, row in df.iterrows():
            # Mapear prioridad sugerida a gravedad
            prioridad = safe_str(row.get('Prioridad Sugerida', 'Media'))
            if 'Alta' in prioridad:
                gravedad = 'Alta'
            elif 'Baja' in prioridad:
                gravedad = 'Baja'
            else:
                gravedad = 'Media'
                
            tipo_falla = Catalogo_Tipo_Falla(
                nombre=safe_str(row.get('Tipo de Falla')),
                categoria=safe_str(row.get('Categoría Principal')),
                descripcion=safe_str(row.get('Descripción')),
                gravedad=gravedad,
                tiempo_estimado_resolucion=60  # 60 minutos por defecto
            )
            db.session.add(tipo_falla)
            count += 1
        db.session.commit()
        print(f"   ✓ {count} tipos de fallas insertados\n")
        
        # 4. GABINETES
        print("4. Migrando Gabinetes...")
        df = pd.read_excel(f'{base_path}Gabinetes.xlsx')
        count = 0
        omitidos_sin_codigo = 0
        for _, row in df.iterrows():
            codigo = safe_str(row.get('ID Gabinete'))
            if not codigo:
                omitidos_sin_codigo += 1
                continue
                
            gabinete = Gabinete(
                codigo=codigo,
                nombre=safe_str(row.get('Nombre de Gabinete')),
                tipo_ubicacion_general=safe_str(row.get('Tipo de Ubicación General')),
                tipo_ubicacion_detallada=safe_str(row.get('Tipo de Ubicación Detallada')),
                ubicacion_id=None,  # Se asignará después si es necesario
                capacidad=safe_int(row.get('Capacidad')),
                tiene_ups=bool(safe_str(row.get('Tiene UPS', '')) == 'Sí'),
                tiene_switch=bool(safe_str(row.get('Tiene Switch', '')) == 'Sí'),
                tiene_nvr=bool(safe_str(row.get('Tiene NVR', '')) == 'Sí'),
                conexion_fibra=bool(safe_str(row.get('Conexión Fibra', '')) == 'Sí'),
                estado=safe_str(row.get('Estado', 'Activo')),
                fecha_alta=safe_date(row.get('Fecha Instalación')),
                observaciones=safe_str(row.get('Observaciones')),
                latitud=safe_float(row.get('Latitud')),
                longitud=safe_float(row.get('Longitud'))
            )
            db.session.add(gabinete)
            count += 1
        db.session.commit()
        mensaje = f"   ✓ {count} gabinetes insertados"
        if omitidos_sin_codigo > 0:
            mensaje += f" ({omitidos_sin_codigo} registros sin código omitidos)"
        print(mensaje + "\n")
        
        # 5. SWITCHES
        print("5. Migrando Switches...")
        df = pd.read_excel(f'{base_path}Switches.xlsx')
        count = 0
        omitidos_sin_codigo = 0
        for _, row in df.iterrows():
            codigo = safe_str(row.get('ID Switch'))
            if not codigo:
                omitidos_sin_codigo += 1
                continue
                
            # Obtener ID del gabinete por nombre
            gabinete_nombre = safe_str(row.get('Gabinete Asociado'))
            gabinete_obj = None
            if gabinete_nombre:
                gabinete_obj = Gabinete.query.filter_by(nombre=gabinete_nombre).first()
            
            switch = Switch(
                codigo=codigo,
                nombre=safe_str(row.get('Nombre/Modelo')),
                ip=safe_str(row.get('Dirección IP')),
                modelo=safe_str(row.get('Nombre/Modelo')),
                marca=safe_str(row.get('Marca')),
                numero_serie=safe_str(row.get('Número de Serie')),
                gabinete_id=gabinete_obj.id if gabinete_obj else None,
                puertos_totales=safe_int(row.get('Número de Puertos')),
                puertos_usados=safe_int(row.get('Puertos Usados', 0)),
                puertos_disponibles=safe_int(row.get('Puertos Disponibles')),
                capacidad_poe=bool(safe_str(row.get('Capacidad PoE', '')) == 'Sí'),
                estado=safe_str(row.get('Estado', 'Activo')),
                fecha_alta=safe_date(row.get('Fecha Instalación')),
                observaciones=safe_str(row.get('Observaciones')),
                latitud=safe_float(row.get('Latitud')),
                longitud=safe_float(row.get('Longitud'))
            )
            db.session.add(switch)
            count += 1
        db.session.commit()
        mensaje = f"   ✓ {count} switches insertados"
        if omitidos_sin_codigo > 0:
            mensaje += f" ({omitidos_sin_codigo} registros sin código omitidos)"
        print(mensaje + "\n")
        
        # 6. PUERTOS SWITCH
        print("6. Migrando Puertos de Switch...")
        df = pd.read_excel(f'{base_path}Puertos_Switch.xlsx')
        count = 0
        for _, row in df.iterrows():
            # Obtener ID del switch por código
            switch_codigo = safe_str(row.get('ID Switch'))
            switch_obj = None
            if switch_codigo:
                switch_obj = Switch.query.filter_by(codigo=switch_codigo).first()
            
            puerto = Puerto_Switch(
                switch_id=switch_obj.id if switch_obj else None,
                numero_puerto=safe_int(row.get('Número de Puerto')),
                camara_id=None,  # Se asignará después si es necesario
                ip_dispositivo=safe_str(row.get('IP Dispositivo')),
                estado=safe_str(row.get('Estado Puerto', 'Disponible')),
                tipo_conexion=safe_str(row.get('Tipo de Conexión')),
                nvr_id=None,  # Se asignará después si es necesario
                puerto_nvr=safe_str(row.get('Puerto NVR (Puerto)'))
            )
            db.session.add(puerto)
            count += 1
        db.session.commit()
        print(f"   ✓ {count} puertos de switch insertados\n")
        
        # 7. UPS
        print("7. Migrando UPS...")
        df = pd.read_excel(f'{base_path}UPS.xlsx')
        count = 0
        duplicados_omitidos = 0
        for _, row in df.iterrows():
            codigo = safe_str(row.get('ID UPS'))
            if not codigo:
                continue
                
            # Verificar si ya existe
            if verificar_existe_registro(UPS, codigo=codigo):
                duplicados_omitidos += 1
                continue
                
            ups = UPS(
                codigo=codigo,
                modelo=safe_str(row.get('Modelo')),
                marca=safe_str(row.get('Marca')),
                capacidad_va=safe_int(row.get('Capacidad (VA)')),
                numero_baterias=safe_int(row.get('Número de Baterías')),
                ubicacion_id=None,  # Se asignará después si es necesario
                gabinete_id=None,  # Se asignará después si es necesario
                equipos_que_alimenta=safe_str(row.get('Alimenta a')),
                estado=safe_str(row.get('Estado', 'Activo')),
                fecha_alta=safe_date(row.get('Fecha de Instalación')),
                observaciones=safe_str(row.get('Observaciones')),
                latitud=safe_float(row.get('Latitud')),
                longitud=safe_float(row.get('Longitud'))
            )
            db.session.add(ups)
            count += 1
        db.session.commit()
        if duplicados_omitidos > 0:
            print(f"   ✓ {count} UPS insertados ({duplicados_omitidos} duplicados omitidos)\n")
        else:
            print(f"   ✓ {count} UPS insertados\n")
        
        # 8. NVR/DVR
        print("8. Migrando NVR/DVR...")
        df = pd.read_excel(f'{base_path}NVR_DVR.xlsx')
        count = 0
        duplicados_omitidos = 0
        omitidos_sin_codigo = 0
        for _, row in df.iterrows():
            codigo = safe_str(row.get('ID NVR'))
            if not codigo:
                omitidos_sin_codigo += 1
                continue
                
            # Verificar si ya existe
            if verificar_existe_registro(NVR_DVR, codigo=codigo):
                duplicados_omitidos += 1
                continue
                
            nvr = NVR_DVR(
                codigo=codigo,
                tipo=safe_str(row.get('Tipo', 'NVR')),
                modelo=safe_str(row.get('Modelo')),
                marca=safe_str(row.get('Marca')),
                canales_totales=safe_int(row.get('Número de Canales')),
                canales_usados=safe_int(row.get('Canales Usados', 0)),
                ip=safe_str(row.get('Dirección IP')),
                ubicacion_id=None,  # Se asignará después si es necesario
                gabinete_id=None,  # Se asignará después si es necesario
                estado=safe_str(row.get('Estado', 'Activo')),
                fecha_alta=safe_date(row.get('Fecha Instalación')),
                observaciones=safe_str(row.get('Observaciones')),
                latitud=safe_float(row.get('Latitud')),
                longitud=safe_float(row.get('Longitud'))
            )
            db.session.add(nvr)
            count += 1
        db.session.commit()
        mensaje = f"   ✓ {count} NVR/DVR insertados"
        if duplicados_omitidos > 0:
            mensaje += f" ({duplicados_omitidos} duplicados omitidos)"
        if omitidos_sin_codigo > 0:
            mensaje += f" ({omitidos_sin_codigo} registros sin código omitidos)"
        print(mensaje + "\n")
        
        # 9. FUENTES DE PODER
        print("9. Migrando Fuentes de Poder...")
        df = pd.read_excel(f'{base_path}Fuentes_Poder.xlsx')
        count = 0
        omitidos_sin_codigo = 0
        for _, row in df.iterrows():
            codigo = safe_str(row.get('ID Fuente'))
            if not codigo:
                omitidos_sin_codigo += 1
                continue
                
            fuente = Fuente_Poder(
                codigo=codigo,
                modelo=safe_str(row.get('Modelo')),
                voltaje=safe_str(row.get('Voltaje (V)')),
                amperaje=safe_str(row.get('Amperaje (A)')),
                equipos_que_alimenta=safe_str(row.get('Equipos que Alimenta')),
                ubicacion_id=None,  # Se asignará después si es necesario
                gabinete_id=None,  # Se asignará después si es necesario
                estado=safe_str(row.get('Estado', 'Activo')),
                fecha_alta=safe_date(row.get('Fecha Instalación')),
                observaciones=safe_str(row.get('Observaciones'))
            )
            db.session.add(fuente)
            count += 1
        db.session.commit()
        mensaje = f"   ✓ {count} fuentes de poder insertadas"
        if omitidos_sin_codigo > 0:
            mensaje += f" ({omitidos_sin_codigo} registros sin código omitidos)"
        print(mensaje + "\n")
        
        # 10. CÁMARAS (467 unidades)
        print("10. Migrando Cámaras...")
        df = pd.read_excel(f'{base_path}Listadecámaras_modificada.xlsx')
        count = 0
        duplicados_omitidos = 0
        for _, row in df.iterrows():
            codigo = safe_str(row.get('Nombre de Cámara'))
            if not codigo:
                continue
                
            # Verificar si ya existe
            if verificar_existe_registro(Camara, codigo=codigo):
                duplicados_omitidos += 1
                continue
                
            camara = Camara(
                codigo=codigo,
                nombre=safe_str(row.get('Nombre de Cámara')),
                ip=safe_str(row.get('IP de Cámara')),
                modelo=safe_str(row.get('Modelo')),
                fabricante=safe_str(row.get('Fabricante')),
                tipo_camara=safe_str(row.get('Tipo de Cámara', 'Domo')),
                ubicacion_id=None,  # Se asignará después si es necesario
                gabinete_id=None,  # Se asignará después si es necesario
                switch_id=None,  # Se asignará después si es necesario
                puerto_switch_id=None,  # Se asignará después si es necesario
                nvr_id=None,  # Se asignará después si es necesario
                puerto_nvr=safe_str(row.get('Puerto NVR')),
                requiere_poe_adicional=bool(safe_str(row.get('Requiere PoE Adicional', '')) == 'Sí'),
                tipo_conexion=safe_str(row.get('Tipo de Conexión')),
                estado=safe_str(row.get('Estado', 'Activo')),
                fecha_alta=safe_date(row.get('Fecha de Instalación')),
                instalador=safe_str(row.get('Instalador')),
                fecha_instalacion=safe_date(row.get('Fecha de Instalación')),
                observaciones=safe_str(row.get('Observaciones')),
                latitud=safe_float(row.get('Latitud')),
                longitud=safe_float(row.get('Longitud'))
            )
            db.session.add(camara)
            count += 1
        db.session.commit()
        if duplicados_omitidos > 0:
            print(f"   ✓ {count} cámaras insertadas ({duplicados_omitidos} duplicados omitidos)\n")
        else:
            print(f"   ✓ {count} cámaras insertadas\n")
        
        # 11. FALLAS (con validación anti-duplicados)
        print("11. Migrando Fallas (con validación anti-duplicados)...")
        
        # Obtener usuario admin para reportado_por
        admin_user = Usuario.query.filter_by(username='admin').first()
        if not admin_user:
            print("   ⚠ Usuario admin no existe, creando...")
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
        
        # Mapear tipos de falla del catálogo a IDs
        tipos_falla_map = {}
        tipos_falla = Catalogo_Tipo_Falla.query.all()
        for tipo in tipos_falla:
            tipos_falla_map[tipo.nombre.lower()] = tipo.id
        
        # Fallas_Actualizada.xlsx
        try:
            df1 = pd.read_excel(f'{base_path}Fallas_Actualizada.xlsx')
            for _, row in df1.iterrows():
                # Buscar cámara por nombre o código
                nombre_camara = safe_str(row.get('Dispositivo Afectado'))
                camara = None
                
                if nombre_camara:
                    camara = Camara.query.filter(
                        Camara.nombre.ilike(f"%{nombre_camara}%")
                    ).first()
                    
                    if not camara:
                        camara = Camara.query.filter(
                            Camara.codigo.ilike(f"%{nombre_camara}%")
                        ).first()
                
                if camara:
                    # Validar anti-duplicados
                    permitir, mensaje = validar_falla_duplicada('Camara', camara.id)
                    if not permitir:
                        rechazadas += 1
                        continue
                    
                    # Mapear tipo de falla
                    tipo_falla_nombre = safe_str(row.get('Tipo de Falla', '')).lower()
                    tipo_falla_id = 1  # Default
                    for nombre_tipo, id_tipo in tipos_falla_map.items():
                        if nombre_tipo in tipo_falla_nombre or tipo_falla_nombre in nombre_tipo:
                            tipo_falla_id = id_tipo
                            break
                    
                    falla = Falla(
                        equipo_tipo='Camara',
                        equipo_id=camara.id,
                        tipo_falla_id=tipo_falla_id,
                        descripcion=safe_str(row.get('Descripción del Problema')),
                        prioridad=safe_str(row.get('Prioridad', 'Media')),
                        fecha_reporte=safe_date(row.get('Fecha de Reporte')) or datetime.now(),
                        reportado_por_id=admin_user.id,
                        estado=safe_str(row.get('Estado', 'Pendiente'))
                    )
                    db.session.add(falla)
                    count += 1
        except Exception as e:
            print(f"   ⚠ Error procesando Fallas_Actualizada.xlsx: {e}")
        
        # Ejemplos_Fallas_Reales.xlsx
        try:
            df2 = pd.read_excel(f'{base_path}Ejemplos_Fallas_Reales.xlsx')
            for _, row in df2.iterrows():
                # Buscar cámara por nombre o código
                nombre_camara = safe_str(row.get('Dispositivo Afectado'))
                camara = None
                
                if nombre_camara:
                    camara = Camara.query.filter(
                        Camara.nombre.ilike(f"%{nombre_camara}%")
                    ).first()
                    
                    if not camara:
                        camara = Camara.query.filter(
                            Camara.codigo.ilike(f"%{nombre_camara}%")
                        ).first()
                
                if camara:
                    # Validar anti-duplicados
                    permitir, mensaje = validar_falla_duplicada('Camara', camara.id)
                    if not permitir:
                        rechazadas += 1
                        continue
                    
                    # Mapear tipo de falla
                    tipo_falla_nombre = safe_str(row.get('Tipo de Falla', '')).lower()
                    tipo_falla_id = 1  # Default
                    for nombre_tipo, id_tipo in tipos_falla_map.items():
                        if nombre_tipo in tipo_falla_nombre or tipo_falla_nombre in nombre_tipo:
                            tipo_falla_id = id_tipo
                            break
                    
                    falla = Falla(
                        equipo_tipo='Camara',
                        equipo_id=camara.id,
                        tipo_falla_id=tipo_falla_id,
                        descripcion=safe_str(row.get('Descripción del Problema')),
                        prioridad=safe_str(row.get('Prioridad', 'Media')),
                        fecha_reporte=safe_date(row.get('Fecha de Reporte')) or datetime.now(),
                        reportado_por_id=admin_user.id,
                        estado=safe_str(row.get('Estado', 'Pendiente'))
                    )
                    db.session.add(falla)
                    count += 1
        except Exception as e:
            print(f"   ⚠ Error procesando Ejemplos_Fallas_Reales.xlsx: {e}")
        
        # INFORME DE CAMARAS - Fallas documentadas 12-10-2025
        print("\n   Extrayendo fallas del INFORME DE CAMARAS (12-10-2025)...")
        try:
            fallas_informe = extraer_fallas_informe()
            print(f"   Total fallas extraídas del informe: {len(fallas_informe)}")
            
            if fallas_informe:
                # Mapear tipos de falla a IDs del catálogo
                tipo_falla_map = {
                    'telas de araña': 1,
                    'imagen borrosa': 1,
                    'mica rallada': 2,
                    'desconectada': 3,
                    'mancha en lente': 1,
                    'empañada': 1,
                    'sin conexión': 3,
                    'intermitencia': 3,
                    'vandalismo/destruida': 2
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
                        tipo_falla_nombre = falla_info['tipo_falla'].lower()
                        tipo_falla_id = 1  # Default
                        for nombre_tipo, id_tipo in tipo_falla_map.items():
                            if nombre_tipo in tipo_falla_nombre:
                                tipo_falla_id = id_tipo
                                break
                        
                        falla = Falla(
                            equipo_tipo='Camara',
                            equipo_id=camara.id,
                            tipo_falla_id=tipo_falla_id,
                            descripcion=f"{falla_info['tipo_falla']} en {camara.nombre}",
                            prioridad=falla_info['prioridad'],
                            fecha_reporte=datetime(2025, 10, 12),  # Fecha del informe
                            reportado_por_id=admin_user.id,
                            estado='Pendiente',
                            observaciones=falla_info['observacion']
                        )
                        db.session.add(falla)
                        informe_insertadas += 1
                
                db.session.commit()
                count += informe_insertadas
                rechazadas += informe_rechazadas
                print(f"   ✓ {informe_insertadas} fallas del informe insertadas")
                print(f"   ⚠ {informe_rechazadas} fallas del informe rechazadas por duplicado")
        except Exception as e:
            print(f"   ⚠ Error procesando INFORME DE CAMARAS: {e}")
        
        db.session.commit()
        print(f"\n   ✓ TOTAL: {count} fallas insertadas ({rechazadas} rechazadas por duplicado)\n")
        
        # 12. MANTENIMIENTOS
        print("12. Migrando Mantenimientos...")
        try:
            df = pd.read_excel(f'{base_path}Mantenimientos.xlsx')
            count = 0
            omitidos_sin_equipo = 0
            for _, row in df.iterrows():
                # Buscar cámara por nombre si existe
                nombre_camara = safe_str(row.get('Dispositivo/Equipo'))
                camara = None
                
                if nombre_camara:
                    camara = Camara.query.filter(
                        Camara.nombre.ilike(f"%{nombre_camara}%")
                    ).first()
                    
                    if not camara:
                        camara = Camara.query.filter(
                            Camara.codigo.ilike(f"%{nombre_camara}%")
                        ).first()
                
                if not camara:
                    omitidos_sin_equipo += 1
                    continue
                
                mantenimiento = Mantenimiento(
                    equipo_tipo='Camara',
                    equipo_id=camara.id,
                    tipo=safe_str(row.get('Tipo de Mantenimiento', 'Preventivo')),
                    fecha=safe_date(row.get('Fecha de Realización')) or datetime.now(),
                    tecnico_id=admin_user.id,
                    descripcion=safe_str(row.get('Descripción del Trabajo Realizado')),
                    materiales_utilizados=safe_str(row.get('Materiales Utilizados')),
                    tiempo_ejecucion_horas=safe_float(row.get('Tiempo de Ejecución (horas)')),
                    costo=safe_float(row.get('Costo Total')),
                    observaciones=safe_str(row.get('Observaciones'))
                )
                db.session.add(mantenimiento)
                count += 1
            db.session.commit()
            mensaje = f"   ✓ {count} mantenimientos insertados"
            if omitidos_sin_equipo > 0:
                mensaje += f" ({omitidos_sin_equipo} registros sin equipo asociado omitidos)"
            print(mensaje + "\n")
        except Exception as e:
            print(f"   ⚠ Error procesando Mantenimientos.xlsx: {e}\n")
        
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
        print(f"\n⚠⚠⚠ ERROR EN MIGRACIÓN: {e}")
        db.session.rollback()
        raise

def ejecutar_migracion():
    print("="*60)
    print("INICIANDO MIGRACIÓN DE DATOS - SISTEMA CAMARAS UFRO")
    print("="*60)
    
    with app.app_context():
        # Limpiar tablas existentes
        print("\nLimpiando base de datos...")
        db.drop_all()
        db.create_all()
        print("✓ Base de datos limpia")
        
        # Crear usuarios por defecto primero
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
        
        # Ejecutar migraciones
        try:
            migrar_datos()
            
            print("\n" + "="*60)
            print("MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ Error durante la migración: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    ejecutar_migracion()
