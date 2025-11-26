#!/usr/bin/env python3
"""
Script de Validación Post-Migración
Sistema de Cámaras UFRO
Fecha: 28 de Octubre 2025
"""

from app import app, db
from models import (Usuario, Ubicacion, Camara, Gabinete, Switch, Puerto_Switch, 
                   UPS, NVR_DVR, Fuente_Poder, Catalogo_Tipo_Falla, Falla, 
                   Mantenimiento, Equipo_Tecnico)
from sqlalchemy import text

def mostrar_estadisticas_detalladas():
    """Muestra estadísticas detalladas de la migración"""
    
    print("="*80)
    print("📊 ESTADÍSTICAS DETALLADAS POST-MIGRACIÓN")
    print("Sistema de Cámaras UFRO")
    print("="*80)
    
    with app.app_context():
        # Estadísticas por tabla
        tablas_estadisticas = [
            ("Usuarios", Usuario),
            ("Ubicaciones", Ubicacion),
            ("Personal Técnico", Equipo_Tecnico),
            ("Tipos de Fallas", Catalogo_Tipo_Falla),
            ("Gabinetes", Gabinete),
            ("Switches", Switch),
            ("Puertos Switch", Puerto_Switch),
            ("UPS", UPS),
            ("NVR/DVR", NVR_DVR),
            ("Fuentes de Poder", Fuente_Poder),
            ("Cámaras", Camara),
            ("Fallas", Falla),
            ("Mantenimientos", Mantenimiento)
        ]
        
        total_registros = 0
        print("\n📈 REGISTROS POR TABLA:")
        print("-" * 50)
        
        for nombre, modelo in tablas_estadisticas:
            count = modelo.query.count()
            total_registros += count
            print(f"{nombre:20} : {count:>6} registros")
        
        print("-" * 50)
        print(f"{'TOTAL GENERAL':20} : {total_registros:>6} registros")
        
        # Estadísticas específicas de cámaras
        print("\n📹 DETALLE DE CÁMARAS:")
        print("-" * 40)
        
        # Por tipo de cámara
        tipos_camara = db.session.query(Camara.tipo_camara, db.func.count(Camara.id)).group_by(Camara.tipo_camara).all()
        for tipo, cantidad in tipos_camara:
            print(f"  {tipo or 'Sin especificar':25} : {cantidad:>4} cámaras")
        
        # Por estado
        estados_camara = db.session.query(Camara.estado, db.func.count(Camara.id)).group_by(Camara.estado).all()
        print(f"\nPor Estado:")
        for estado, cantidad in estados_camara:
            print(f"  {estado or 'Sin estado':25} : {cantidad:>4} cámaras")
        
        # Con IP configurada
        camaras_con_ip = Camara.query.filter(Camara.ip.isnot(None)).count()
        camaras_sin_ip = Camara.query.filter(Camara.ip.is_(None)).count()
        print(f"\nConfiguración IP:")
        print(f"  Con IP configurada       : {camaras_con_ip:>4} cámaras")
        print(f"  Sin IP configurada       : {camaras_sin_ip:>4} cámaras")
        
        # Estadísticas de infraestructura
        print("\n🏢 INFRAESTRUCTURA DE RED:")
        print("-" * 40)
        
        # Gabinetes con equipos
        gabinetes_con_switch = Gabinete.query.filter(Gabinete.tiene_switch == True).count()
        gabinetes_con_ups = Gabinete.query.filter(Gabinete.tiene_ups == True).count()
        gabinetes_con_nvr = Gabinete.query.filter(Gabinete.tiene_nvr == True).count()
        
        print(f"Gabinetes con Switch      : {gabinetes_con_switch:>4}")
        print(f"Gabinetes con UPS         : {gabinetes_con_ups:>4}")
        print(f"Gabinetes con NVR         : {gabinetes_con_nvr:>4}")
        
        # Switches con PoE
        switches_con_poe = Switch.query.filter(Switch.capacidad_poe == True).count()
        total_switches = Switch.query.count()
        print(f"Switches con PoE          : {switches_con_poe:>4} de {total_switches}")
        
        # UPS por capacidad
        ups_por_capacidad = db.session.query(UPS.capacidad_va, db.func.count(UPS.id)).group_by(UPS.capacidad_va).all()
        print(f"\nUPS por Capacidad:")
        for capacidad, cantidad in ups_por_capacidad:
            print(f"  {capacidad or 'Sin especificar':20} VA : {cantidad:>4} equipos")
        
        # Estadísticas de usuarios
        print("\n👥 USUARIOS DEL SISTEMA:")
        print("-" * 30)
        
        usuarios_por_rol = db.session.query(Usuario.rol, db.func.count(Usuario.id)).group_by(Usuario.rol).all()
        for rol, cantidad in usuarios_por_rol:
            print(f"  {rol:15} : {cantidad:>4} usuarios")
        
        # Estadísticas de fallas
        print("\n⚠️  ESTADO DE FALLAS:")
        print("-" * 25)
        
        if Falla.query.count() > 0:
            fallas_por_estado = db.session.query(Falla.estado, db.func.count(Falla.id)).group_by(Falla.estado).all()
            for estado, cantidad in fallas_por_estado:
                print(f"  {estado:20} : {cantidad:>4} fallas")
        else:
            print("  No hay fallas registradas")
        
        # Verificación de integridad
        print("\n🔍 VERIFICACIÓN DE INTEGRIDAD:")
        print("-" * 40)
        
        # Cámaras sin código
        camaras_sin_codigo = Camara.query.filter(Camara.codigo.is_(None)).count()
        if camaras_sin_codigo > 0:
            print(f"⚠️  Cámaras sin código     : {camaras_sin_codigo:>4}")
        else:
            print("✅ Todas las cámaras tienen código")
        
        # Cámaras sin IP
        if camaras_sin_ip > 0:
            print(f"⚠️  Cámaras sin IP         : {camaras_sin_ip:>4}")
        else:
            print("✅ Todas las cámaras tienen IP")
        
        # Duplicados potenciales
        codigos_duplicados = db.session.query(Camara.codigo, db.func.count(Camara.id)).group_by(Camara.codigo).having(db.func.count(Camara.id) > 1).all()
        if codigos_duplicados:
            print(f"⚠️  Códigos duplicados     : {len(codigos_duplicados):>4}")
            for codigo, cantidad in codigos_duplicados:
                print(f"    - {codigo}: {cantidad} registros")
        else:
            print("✅ No hay códigos duplicados")
        
        # Referencias huérfanas
        camaras_sin_gabinete = Camara.query.filter(Camara.gabinete_id.isnot(None)).filter(~db.exists().where(Gabinete.id == Camara.gabinete_id)).count()
        if camaras_sin_gabinete > 0:
            print(f"⚠️  Cámaras con gabinete inválido: {camaras_sin_gabinete:>4}")
        else:
            print("✅ Todas las referencias de gabinete son válidas")

def mostrar_muestras_datos():
    """Muestra muestras de los datos migrados"""
    
    print("\n" + "="*80)
    print("🔍 MUESTRAS DE DATOS MIGRADOS")
    print("="*80)
    
    with app.app_context():
        # Muestra de cámaras
        print("\n📹 PRIMERAS 5 CÁMARAS:")
        print("-" * 60)
        camaras = Camara.query.limit(5).all()
        for i, camara in enumerate(camaras, 1):
            print(f"{i}. {camara.codigo} | IP: {camara.ip or 'N/A'} | Tipo: {camara.tipo_camara or 'N/A'}")
        
        # Muestra de gabinetes
        print("\n🏢 GABINETES:")
        print("-" * 30)
        gabinetes = Gabinete.query.all()
        for gabinete in gabinetes:
            print(f"• {gabinete.codigo} | {gabinete.nombre}")
            print(f"  Switch: {'Sí' if gabinete.tiene_switch else 'No'} | UPS: {'Sí' if gabinete.tiene_ups else 'No'}")
        
        # Muestra de switches
        print("\n🔌 SWITCHES:")
        print("-" * 25)
        switches = Switch.query.all()
        for switch in switches:
            print(f"• {switch.codigo} | {switch.nombre} | IP: {switch.ip or 'N/A'}")
            print(f"  Puertos: {switch.puertos_usados or 0}/{switch.puertos_totales or 0} | PoE: {'Sí' if switch.capacidad_poe else 'No'}")

def ejecutar_validaciones_sql():
    """Ejecuta validaciones SQL específicas"""
    
    print("\n" + "="*80)
    print("🔬 VALIDACIONES SQL")
    print("="*80)
    
    with app.app_context():
        # Consulta de integridad de cámaras
        print("\n📊 INTEGRIDAD DE CÁMARAS:")
        print("-" * 35)
        
        # Cámaras por ubicación
        try:
            query = text("""
                SELECT 
                    u.campus,
                    u.edificio,
                    COUNT(c.id) as total_camaras,
                    COUNT(CASE WHEN c.ip IS NOT NULL THEN 1 END) as con_ip
                FROM ubicaciones u
                LEFT JOIN camaras c ON u.id = c.ubicacion_id
                GROUP BY u.id, u.campus, u.edificio
                ORDER BY total_camaras DESC
            """)
            resultados = db.session.execute(query).fetchall()
            
            print("Por Ubicación:")
            for campus, edificio, total, con_ip in resultados:
                print(f"  {campus} - {edificio}: {total} cámaras ({con_ip} con IP)")
        except Exception as e:
            print(f"Error en consulta: {e}")
        
        # Resumen de equipos por gabinete
        print("\n🏢 EQUIPOS POR GABINETE:")
        print("-" * 30)
        
        try:
            query = text("""
                SELECT 
                    g.codigo,
                    g.nombre,
                    COUNT(DISTINCT s.id) as switches,
                    COUNT(DISTINCT u.id) as ups,
                    COUNT(DISTINCT n.id) as nvrs,
                    COUNT(DISTINCT c.id) as camaras
                FROM gabinetes g
                LEFT JOIN switches s ON g.id = s.gabinete_id
                LEFT JOIN ups u ON g.id = u.gabinete_id
                LEFT JOIN nvr_dvr n ON g.id = n.gabinete_id
                LEFT JOIN camaras c ON g.id = c.gabinete_id
                GROUP BY g.id, g.codigo, g.nombre
                ORDER BY g.codigo
            """)
            resultados = db.session.execute(query).fetchall()
            
            for codigo, nombre, switches, ups, nvrs, camaras in resultados:
                print(f"{codigo}: {switches}sw/{ups}ups/{nvrs}nvr/{camaras}cam")
        except Exception as e:
            print(f"Error en consulta: {e}")

if __name__ == '__main__':
    print("Iniciando validación post-migración...")
    
    # Ejecutar todas las validaciones
    mostrar_estadisticas_detalladas()
    mostrar_muestras_datos()
    ejecutar_validaciones_sql()
    
    print("\n" + "="*80)
    print("✅ VALIDACIÓN COMPLETADA")
    print("="*80)
    print("📋 Revisa los resultados arriba para verificar la calidad de la migración")
    print("📞 Si hay problemas, revisa el reporte detallado en /memories/")