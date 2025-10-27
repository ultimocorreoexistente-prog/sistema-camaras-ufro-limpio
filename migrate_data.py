import pandas as pd
<<<<<<< HEAD
import os
from datetime import datetime
from app import app, db
from models import (Camaras, Gabinetes, Switches, PuertosSwitch, EquiposTecnicos, 
                    Fallas, Mantenimientos, Ubicaciones, TiposFalla)

def limpiar_valor(valor):
    """Limpia valores NaN y None"""
    if pd.isna(valor) or valor is None:
        return None
    return str(valor).strip() if isinstance(valor, str) else valor

def parsear_fecha(fecha_str):
    """Parsea fechas en diferentes formatos"""
    if pd.isna(fecha_str) or fecha_str is None:
        return None
    try:
        if isinstance(fecha_str, str):
            return datetime.strptime(fecha_str, '%Y-%m-%d').date()
        return fecha_str.date() if hasattr(fecha_str, 'date') else None
    except:
        return None

def migrar_ubicaciones():
    print("\nMigrando Ubicaciones...")
    df = pd.read_excel('planillas/Ubicaciones.xlsx')
    for _, row in df.iterrows():
        ubicacion = Ubicaciones(
            campus=limpiar_valor(row.get('Campus')),
            edificio=limpiar_valor(row.get('Edificio')),
            piso=limpiar_valor(row.get('Piso/Nivel')),
            zona=limpiar_valor(row.get('Zona')),
            gabinetes_en_ubicacion=limpiar_valor(row.get('Gabinetes en Ubicación')),
            cantidad_camaras=int(row.get('Cantidad de Cámaras', 0)) if pd.notna(row.get('Cantidad de Cámaras')) else None,
            observaciones=limpiar_valor(row.get('Observaciones'))
        )
        db.session.add(ubicacion)
    db.session.commit()
    print(f"✓ {len(df)} ubicaciones migradas")

def migrar_gabinetes():
    print("\nMigrando Gabinetes...")
    df = pd.read_excel('planillas/Gabinetes.xlsx')
    for _, row in df.iterrows():
        gabinete = Gabinetes(
            codigo=limpiar_valor(row.get('ID Gabinetes')),
            nombre=limpiar_valor(row.get('Nombre de Gabinetes')),
            ubicacion=limpiar_valor(row.get('Ubicación Detallada')),
            campus=limpiar_valor(row.get('Campus')),
            edificio=limpiar_valor(row.get('Edificio')),
            piso=limpiar_valor(row.get('Piso')),
            coordenadas=limpiar_valor(row.get('Coordenadas')),
            tipo=limpiar_valor(row.get('Tipo de Gabinetes')),
            estado=limpiar_valor(row.get('Estado')),
            switch_principal=limpiar_valor(row.get('Switches Principales')),
            nvr_asociado=limpiar_valor(row.get('NVR Asociado')),
            camaras_conectadas=int(row.get('Número de Cámaras Conectadas', 0)) if pd.notna(row.get('Número de Cámaras Conectadas')) else None,
            fecha_instalacion=parsear_fecha(row.get('Fecha de Instalación')),
            observaciones=limpiar_valor(row.get('Observaciones'))
        )
        db.session.add(gabinete)
    db.session.commit()
    print(f"✓ {len(df)} gabinetes migrados")

def migrar_switches():
    print("\nMigrando Switches...")
    df = pd.read_excel('planillas/Switches.xlsx')
    for _, row in df.iterrows():
        # Buscar gabinete asociado
        gabinete_codigo = limpiar_valor(row.get('Gabinetes Asociados'))
        gabinete = Gabinetes.query.filter_by(codigo=gabinete_codigo).first() if gabinete_codigo else None
        
        switch = Switches(
            codigo=limpiar_valor(row.get('ID Switches')),
            nombre=limpiar_valor(row.get('Nombre/Modelo')),
            marca=limpiar_valor(row.get('Marca')),
            numero_serie=limpiar_valor(row.get('Número de Serie')),
            gabinete_id=gabinete.id if gabinete else None,
            puertos_totales=int(row.get('Número Total de Puertos', 0)) if pd.notna(row.get('Número Total de Puertos')) else None,
            puertos_usados=int(row.get('Puertos Usados', 0)) if pd.notna(row.get('Puertos Usados')) else None,
            puertos_disponibles=int(row.get('Puertos Disponibles', 0)) if pd.notna(row.get('Puertos Disponibles')) else None,
            soporta_poe=row.get('Soporta PoE') == 'Sí' if pd.notna(row.get('Soporta PoE')) else False,
            estado=limpiar_valor(row.get('Estado')),
            fecha_instalacion=parsear_fecha(row.get('Fecha de Instalación')),
            fecha_ultimo_mantenimiento=parsear_fecha(row.get('Fecha de Último Mantenimiento')),
            observaciones=limpiar_valor(row.get('Observaciones'))
        )
        db.session.add(switch)
    db.session.commit()
    print(f"✓ {len(df)} switches migrados")

def migrar_puertos_switch():
    print("\nMigrando Puertos de Switch...")
    df = pd.read_excel('planillas/Puertos_Switch.xlsx')
    for _, row in df.iterrows():
        # Buscar switch asociado
        switch_codigo = limpiar_valor(row.get('ID Switches'))
        switch = Switches.query.filter_by(codigo=switch_codigo).first() if switch_codigo else None
        
        puerto = PuertosSwitch(
            switch_id=switch.id if switch else None,
            numero_puerto=int(row.get('Número de Puerto', 0)) if pd.notna(row.get('Número de Puerto')) else None,
            estado=limpiar_valor(row.get('Estado Puerto')),
            dispositivo_conectado=limpiar_valor(row.get('Dispositivo Conectado')),
            ip_dispositivo=limpiar_valor(row.get('IP Dispositivo')),
            tipo_conexion=limpiar_valor(row.get('Tipo de Conexión')),
            nvr_asociado=limpiar_valor(row.get('NVR Asociado (Puerto)')),
            puerto_nvr=limpiar_valor(row.get('Puerto NVR (Puerto)')),
            observaciones=limpiar_valor(row.get('Observaciones'))
        )
        db.session.add(puerto)
    db.session.commit()
    print(f"✓ {len(df)} puertos migrados")

def migrar_camaras():
    print("\nMigrando Cámaras...")
    df = pd.read_excel('planillas/Listadecámaras_modificada.xlsx')
    for _, row in df.iterrows():
        camara = Camaras(
            codigo=limpiar_valor(row.get('Código Cámara')),
            nombre=limpiar_valor(row.get('Nombre de Cámara')),
            campus=limpiar_valor(row.get('Campus')),
            edificio=limpiar_valor(row.get('Edificio')),
            piso=limpiar_valor(row.get('Piso')),
            ubicacion=limpiar_valor(row.get('Ubicación Detallada')),
            ip=limpiar_valor(row.get('Dirección IP')),
            marca=limpiar_valor(row.get('Marca')),
            modelo=limpiar_valor(row.get('Modelo')),
            tipo=limpiar_valor(row.get('Tipo de Cámara')),
            resolucion=limpiar_valor(row.get('Resolución')),
            estado=limpiar_valor(row.get('Estado')),
            gabinete_asociado=limpiar_valor(row.get('Gabinetes Asociados')),
            switch_conectado=limpiar_valor(row.get('Switches Conectados')),
            puerto_switch=limpiar_valor(row.get('Puertos Switches')),
            nvr_asociado=limpiar_valor(row.get('NVR Asociado')),
            puerto_nvr=limpiar_valor(row.get('Puerto NVR')),
            fecha_instalacion=parsear_fecha(row.get('Fecha de Instalación')),
            observaciones=limpiar_valor(row.get('Observaciones'))
        )
        db.session.add(camara)
    db.session.commit()
    print(f"✓ {len(df)} cámaras migradas")

def migrar_equipos_tecnicos():
    print("\nMigrando Equipos Técnicos...")
    df = pd.read_excel('planillas/Equipos_Tecnicos.xlsx')
    for _, row in df.iterrows():
        # Buscar gabinete asociado
        ubicacion_str = limpiar_valor(row.get('Ubicación'))
        gabinete = Gabinetes.query.filter(Gabinetes.codigo.like(f'%{ubicacion_str}%')).first() if ubicacion_str else None
        
        equipo = EquiposTecnicos(
            tipo=limpiar_valor(row.get('Tipo de Equipo')),
            marca=limpiar_valor(row.get('Marca')),
            modelo=limpiar_valor(row.get('Modelo')),
            numero_serie=limpiar_valor(row.get('Número de Serie')),
            capacidad=limpiar_valor(row.get('Capacidad (VA/W/Canales)')),
            ubicacion=ubicacion_str,
            gabinete_id=gabinete.id if gabinete else None,
            estado=limpiar_valor(row.get('Estado')),
            fecha_instalacion=parsear_fecha(row.get('Fecha de Instalación')),
            fecha_ultimo_mantenimiento=parsear_fecha(row.get('Última Revisión')),
            proximo_mantenimiento=parsear_fecha(row.get('Próximo Mantenimiento Programado')),
            observaciones=limpiar_valor(row.get('Observaciones'))
        )
        db.session.add(equipo)
    db.session.commit()
    print(f"✓ {len(df)} equipos técnicos migrados")

def migrar_fallas():
    print("\nMigrando Fallas...")
    df = pd.read_excel('planillas/Fallas_Actualizada.xlsx')
    for _, row in df.iterrows():
        # Buscar cámara asociada
        camara_codigo = limpiar_valor(row.get('Cámara Afectada'))
        camara = Camaras.query.filter_by(codigo=camara_codigo).first() if camara_codigo else None
        
        falla = Fallas(
            fecha_reporte=parsear_fecha(row.get('Fecha de Reporte')),
            reportado_por=limpiar_valor(row.get('Reportado Por')),
            tipo=limpiar_valor(row.get('Tipo')),
            subtipo=limpiar_valor(row.get('Subtipo')),
            camara_id=camara.id if camara else None,
            camara_afectada=camara_codigo,
            ubicacion=limpiar_valor(row.get('Ubicación')),
            descripcion=limpiar_valor(row.get('Descripción')),
            impacto_visibilidad=limpiar_valor(row.get('Impacto en Visibilidad')),
            afecta_vision_nocturna=limpiar_valor(row.get('Afecta Visión Nocturna')),
            estado=limpiar_valor(row.get('Estado')),
            prioridad=limpiar_valor(row.get('Prioridad')),
            tecnico_asignado=limpiar_valor(row.get('Técnico Asignado')),
            observaciones=limpiar_valor(row.get('Observaciones'))
        )
        db.session.add(falla)
    db.session.commit()
    print(f"✓ {len(df)} fallas migradas")

def migrar_ejemplos_fallas_reales():
    print("\nMigrando Ejemplos de Fallas Reales...")
    try:
        df = pd.read_excel('planillas/Ejemplos_Fallas_Reales.xlsx')
        for _, row in df.iterrows():
            # Buscar cámara asociada
            camara_codigo = limpiar_valor(row.get('Cámara Afectada'))
            camara = Camaras.query.filter_by(codigo=camara_codigo).first() if camara_codigo else None
            
            falla = Fallas(
                fecha_reporte=parsear_fecha(row.get('Fecha de Reporte')),
                reportado_por=limpiar_valor(row.get('Reportado Por')),
                tipo=limpiar_valor(row.get('Tipos de Fallas')),
                subtipo=limpiar_valor(row.get('Subtipo')),
                camara_id=camara.id if camara else None,
                camara_afectada=camara_codigo,
                ubicacion=limpiar_valor(row.get('Ubicación')),
                descripcion=limpiar_valor(row.get('Descripción')),
                impacto_visibilidad=limpiar_valor(row.get('Impacto en Visibilidad')),
                afecta_vision_nocturna=limpiar_valor(row.get('Afecta Visión Nocturna')),
                estado=limpiar_valor(row.get('Estado')),
                prioridad=limpiar_valor(row.get('Prioridad')),
                tecnico_asignado=limpiar_valor(row.get('Técnico Asignado')),
                observaciones=limpiar_valor(row.get('Observaciones'))
            )
            db.session.add(falla)
        db.session.commit()
        print(f"✓ {len(df)} casos reales migrados")
    except Exception as e:
        print(f"Error en migración de casos reales: {e}")

def migrar_mantenimientos():
    print("\nMigrando Mantenimientos...")
    df = pd.read_excel('planillas/Mantenimientos.xlsx')
    for _, row in df.iterrows():
        mantenimiento = Mantenimientos(
            fecha_programada=parsear_fecha(row.get('Fecha Programada')),
            fecha_realizacion=parsear_fecha(row.get('Fecha de Realización')),
            tipo=limpiar_valor(row.get('Tipos de Mantenimiento')),
            categoria=limpiar_valor(row.get('Categoría')),
            equipo_gabinete=limpiar_valor(row.get('Equipos/Gabinetes')),
            ubicacion=limpiar_valor(row.get('Ubicación')),
            descripcion=limpiar_valor(row.get('Descripción del Trabajo')),
            estado=limpiar_valor(row.get('Estado')),
            tecnico_responsable=limpiar_valor(row.get('Técnico Responsable')),
            materiales_utilizados=limpiar_valor(row.get('Materiales Utilizados')),
            costo_aproximado=float(row.get('Costo Aproximado', 0)) if pd.notna(row.get('Costo Aproximado')) else None,
            equipos_camaras_afectadas=limpiar_valor(row.get('Equipos/Cámaras Afectadas')),
            tiempo_ejecucion=limpiar_valor(row.get('Tiempo de Ejecución')),
            observaciones=limpiar_valor(row.get('Observaciones'))
        )
        db.session.add(mantenimiento)
    db.session.commit()
    print(f"✓ {len(df)} mantenimientos migrados")

def migrar_tipos_fallas():
    print("\nMigrando Catálogo de Tipos de Fallas...")
    df = pd.read_excel('planillas/Catalogo_Tipos_Fallas.xlsx')
    for _, row in df.iterrows():
        tipo_falla = TiposFalla(
            categoria_principal=limpiar_valor(row.get('Categoría Principal')),
            tipo_falla=limpiar_valor(row.get('Tipos de Fallas')),
            impacto_tipico=limpiar_valor(row.get('Impacto Típico')),
            tipo_mantenimiento=limpiar_valor(row.get('Tipos de Mantenimiento')),
            prioridad_sugerida=limpiar_valor(row.get('Prioridad Sugerida')),
            frecuencia_observada=limpiar_valor(row.get('Frecuencia Observada'))
        )
        db.session.add(tipo_falla)
    db.session.commit()
    print(f"✓ {len(df)} tipos de fallas migrados")

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
        
        # Ejecutar migraciones en orden
        try:
            migrar_ubicaciones()
            migrar_gabinetes()
            migrar_switches()
            migrar_puertos_switch()
            migrar_camaras()
            migrar_equipos_tecnicos()
            migrar_tipos_fallas()
            migrar_fallas()
            migrar_ejemplos_fallas_reales()
            migrar_mantenimientos()
            
            print("\n" + "="*60)
            print("MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("="*60)
            
            # Estadísticas finales
            print("\nEstadísticas:")
            print(f"  - Ubicaciones: {Ubicaciones.query.count()}")
            print(f"  - Gabinetes: {Gabinetes.query.count()}")
            print(f"  - Switches: {Switches.query.count()}")
            print(f"  - Puertos: {PuertosSwitch.query.count()}")
            print(f"  - Cámaras: {Camaras.query.count()}")
            print(f"  - Equipos Técnicos: {EquiposTecnicos.query.count()}")
            print(f"  - Fallas: {Fallas.query.count()}")
            print(f"  - Mantenimientos: {Mantenimientos.query.count()}")
            print(f"  - Tipos de Fallas: {TiposFalla.query.count()}")
            
        except Exception as e:
            print(f"\n❌ Error durante la migración: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    ejecutar_migracion()
=======
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
    informe_path = 'docs/INFORME_DE_CAMARAS.md'
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
                piso=safe_str(row.get('Piso')),
                descripcion=safe_str(row.get('Descripcion')),
                latitud=safe_float(row.get('Latitud')),
                longitud=safe_float(row.get('Longitud')),
                activo=True
            )
            db.session.add(ubicacion)
            count += 1
        db.session.commit()
        print(f"   ✓ {count} ubicaciones insertadas\n")
        
        # 2. EQUIPOS TÉCNICOS
        print("2. Migrando Equipos Técnicos...")
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
        print(f"   ✓ {count} equipos técnicos insertados\n")
        
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
        print(f"   ✓ {count} tipos de fallas insertados\n")
        
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
        print(f"   ✓ {count} gabinetes insertados\n")
        
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
        print(f"   ✓ {count} switches insertados\n")
        
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
        print(f"   ✓ {count} puertos de switch insertados\n")
        
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
        print(f"   ✓ {count} UPS insertados\n")
        
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
        print(f"   ✓ {count} NVR/DVR insertados\n")
        
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
        print(f"   ✓ {count} fuentes de poder insertadas\n")
        
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
            print(f"   ⚠ Error procesando Fallas_Actualizada.xlsx: {e}")
        
        # Ejemplos_Fallas_Reales.xlsx
        try:
            df2 = pd.read_excel(f'{base_path}Ejemplos_Fallas_Reales.xlsx')
            for _, row in df2.iterrows():
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
            print(f"   ⚠ Error procesando Ejemplos_Fallas_Reales.xlsx: {e}")
        
        # INFORME DE CAMARAS - Fallas documentadas 12-10-2025
        print("\n   Extrayendo fallas del INFORME DE CAMARAS (12-10-2025)...")
        try:
            fallas_informe = extraer_fallas_informe()
            print(f"   Total fallas extraídas del informe: {len(fallas_informe)}")
            
            if fallas_informe:
                # Mapear tipos de falla a IDs del catálogo
                tipo_falla_map = {
                    'Telas de araña': 1,  # Limpieza
                    'Imagen borrosa': 1,   # Limpieza
                    'Mica rallada': 2,     # Reparación
                    'Desconectada': 3,     # Técnica
                    'Mancha en lente': 1,  # Limpieza
                    'Empañada': 1,        # Limpieza
                    'Sin conexión': 3,    # Técnica
                    'Intermitencia': 3,    # Técnica
                    'Vandalismo/Destruida': 2  # Reparación
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
            print(f"   ✓ {count} mantenimientos insertados\n")
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

if __name__ == '__main__':
    with app.app_context():
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
        
        migrar_datos()
>>>>>>> 012ede52e80dbeaefc51c29b43d6fdc1ee5a799d
