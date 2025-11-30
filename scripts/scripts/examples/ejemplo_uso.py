"""
Ejemplo de uso de los modelos SQLAlchemy.

Este archivo demuestra cómo usar los modelos creados para el sistema de gestión
de infraestructura tecnológica.
"""

from datetime import datetime, timedelta
from models import db, init_db
from models.usuario import Usuario
from models.ubicacion import Ubicacion
from models.camara import Camara
from models.falla import Falla
from models.mantenimiento import Mantenimiento
from models.fotografia import Fotografia
from models.equipo import NetworkConnection, ConnectionType

# Crear una aplicación Flask de ejemplo
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///infraestructura.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
init_db(app)

def ejemplo_completo():
<<<<<<< HEAD
"""
Ejemplo completo de uso de los modelos.
"""
with app.app_context():
print("=== EJEMPLO DE USO DE MODELOS SQLALCHEMY ===\n")

# 1. CREAR USUARIOS
print("1. Creando usuarios...")
admin = Usuario(
username="admin",
email="admin@sistema.com",
full_name="Administrador del Sistema",
role="administrador",
phone="+56 9 134 5678",
department="IT"
)
admin.set_password("admin13")
admin.save()

tecnico = Usuario(
username="tecnico1",
email="tecnico@sistema.com",
full_name="Técnico Principal",
role="tecnico",
phone="+56 9 8765 431",
department="Soporte Técnico"
)
tecnico.set_password("tecnico13")
tecnico.save()

print(f" Usuario creado: {admin.username} (ID: {admin.id})")
print(f" Usuario creado: {tecnico.username} (ID: {tecnico.id})")

# . CREAR UBICACIONES
print("\n. Creando ubicaciones...")
edificio_principal = Ubicacion(
name="Edificio Principal",
description="Edificio principal de la empresa",
address="Av. Principal 13, Ciudad",
location_type="edificio",
building="Edificio Principal",
floor="Piso 1",
campus="Campus Central"
)
edificio_principal.save()

sala_servidores = Ubicacion(
name="Sala de Servidores",
description="Sala principal de servidores",
location_type="sala",
building="Edificio Principal",
floor="Sótano",
parent_id=edificio_principal.id
)
sala_servidores.save()

print(f" Ubicación creada: {edificio_principal.name} (ID: {edificio_principal.id})")
print(f" Ubicación creada: {sala_servidores.name} (ID: {sala_servidores.id})")
print(f" Ruta completa: {sala_servidores.get_full_path()}")

# 3. CREAR EQUIPOS NVR
print("\n3. Creando equipos NVR...")
nvr_principal = NVR(
name="NVR-001",
model="Hikvision DS-773NIX",
manufacturer="Hikvision",
serial_number="NV040001",
inventory_number="INV-NVR-001",
ip_address="19.168.1.10",
system_type="nvr",
channels=16,
max_channels=3,
storage_capacity=000, # TB
ubicacion_id=sala_servidores.id,
created_by=admin.id
)
nvr_principal.save()

print(f" NVR creado: {nvr_principal.name} (ID: {nvr_principal.id})")
print(f" Capacidad: {nvr_principal.get_total_recording_capacity_days()} días estimados")

# 4. CREAR CÁMARAS
print("\n4. Creando cámaras...")
camara_entrada = Camara(
name="Cámara Entrada Principal",
model="Hikvision DS-CD145FWD-I",
manufacturer="Hikvision",
camera_type="domo",
ip_address="19.168.1.101",
mac_address="AA:BB:CC:DD:EE:01",
port=554,
connection_type="ethernet",
power_over_ethernet=True,
resolution="190x1080",
frame_rate=30,
codec="H.64",
nvr_id=nvr_principal.id,
ubicacion_id=edificio_principal.id,
created_by=admin.id
)
camara_entrada.save()

# Agregar cámara al NVR
nvr_principal.add_camera(camara_entrada)

print(f" Cámara creada: {camara_entrada.name} (ID: {camara_entrada.id})")
print(f" Conectada al NVR: {camara_entrada.nvr.name}")

# 5. CREAR FALLAS
print("\n5. Creando fallas...")
falla_camara = Falla(
title="Cámara sin señal",
description="La cámara de entrada principal no muestra señal de video",
falla_type="conectividad",
priority="alta",
equipment_id=camara_entrada.id,
equipment_type="camara",
camara_id=camara_entrada.id,
ubicacion_id=edificio_principal.id,
reported_by=tecnico.id,
start_date=datetime.utcnow(),
assigned_to=tecnico.id,
assigned_date=datetime.utcnow(),
estimated_resolution_time=
)
falla_camara.save()

print(f" Falla creada: {falla_camara.title} (ID: {falla_camara.id})")
print(f" Estado: {falla_camara.status}")
print(f" Asignada a: {falla_camara.assigned_user.full_name}")

# 6. CREAR MANTENIMIENTOS
print("\n6. Creando mantenimientos...")
mantenimiento_nvr = Mantenimiento(
title="Mantenimiento preventivo NVR",
description="Limpieza de filtros, verificación de discos duros, actualización de firmware",
maintenance_type="preventivo",
category="inspeccion",
priority="media",
equipment_id=nvr_principal.id,
equipment_type="nvr",
nvr_id=nvr_principal.id,
ubicacion_id=sala_servidores.id,
scheduled_start=datetime.utcnow() + timedelta(days=7),
duration_estimated=3,
technician_id=tecnico.id,
supervisor_id=admin.id,
maintenance_cost=0,
parts_cost=0,
labor_cost=150,
external_cost=0,
customer_notification=True,
work_order_number=f"WO-{datetime.utcnow().strftime('%Y%m%d')}-001"
)
mantenimiento_nvr.save()

print(f" Mantenimiento creado: {mantenimiento_nvr.title} (ID: {mantenimiento_nvr.id})")
print(f" Programado para: {mantenimiento_nvr.scheduled_start}")
print(f" Orden de trabajo: {mantenimiento_nvr.work_order_number}")

# 7. CREAR FOTOGRAFÍAS
print("\n7. Creando fotografías...")
foto_falla = Fotografia(
filename="falla_camara_entrada.jpg",
file_path="/uploads/fallas/falla_camara_entrada.jpg",
file_size=048576, # MB
mime_type="image/jpeg",
photo_format="jpeg",
width=190,
height=1080,
photo_type="falla",
status="procesando",
title="Foto de falla en cámara de entrada",
description="Captura mostrando ausencia de señal en cámara principal",
equipment_id=camara_entrada.id,
equipment_type="camara",
camara_id=camara_entrada.id,
ubicacion_id=edificio_principal.id,
falla_id=falla_camara.id,
uploaded_by=tecnico.id,
capture_date=datetime.utcnow(),
quality_score=85.5
)
foto_falla.save()

print(f" Fotografía creada: {foto_falla.filename} (ID: {foto_falla.id})")
print(f" Tamaño: {foto_falla.get_file_size_mb()} MB")
print(f" Dimensiones: {foto_falla.get_dimensions_string()}")
print(f" Calidad: {foto_falla.get_quality_rating()}")

# 8. CREAR CONEXIONES DE RED
print("\n8. Creando conexiones de red...")
conexion = NetworkConnection(
source_equipment_id=nvr_principal.id,
source_equipment_type="nvr",
target_equipment_id=camara_entrada.id,
target_equipment_type="camara",
connection_type="ethernet",
cable_type="Cat6",
cable_length=50.0,
port_source="eth0",
port_target="eth0",
is_active=True,
bandwidth_limit=100 # Mbps
)
conexion.save()

print(f" Conexión creada entre {nvr_principal.name} y {camara_entrada.name}")

# 9. CONSULTAS Y RESÚMENES
print("\n9. Consultas y resúmenes...")

# Resumen de cámaras en ubicación
camaras_ubicacion = Camara.get_by_location(edificio_principal.id)
print(f" Cámaras en {edificio_principal.name}: {len(camaras_ubicacion)}")

# Resumen de fallas activas
fallas_activas = Falla.get_active_fallas()
print(f" Fallas activas en el sistema: {len(fallas_activas)}")

# Resumen de mantenimientos programados
mantenimientos_programados = [m for m in Mantenimiento.query.all() if m.status == "programado"]
print(f" Mantenimientos programados: {len(mantenimientos_programados)}")

# Resumen de NVR
summary_nvr = nvr_principal.get_cameras_status_summary()
print(f" Estado de cámaras en {nvr_principal.name}: {summary_nvr}")

print("\n=== EJEMPLO COMPLETADO EXITOSAMENTE ===")

def ejemplo_consultas_avanzadas():
"""
Ejemplo de consultas avanzadas con los modelos.
"""
with app.app_context():
print("\n=== CONSULTAS AVANZADAS ===\n")

# Consulta 1: Equipos por ubicación con falla
print("1. Ubicaciones con equipos con fallas activas:")
ubicaciones = Ubicacion.query.all()
for ubicacion in ubicaciones:
fallas_ubicacion = Falla.get_by_location(ubicacion.id)
if fallas_ubicacion:
print(f" - {ubicacion.name}: {len(fallas_ubicacion)} fallas activas")

# Consulta : Técnicos con carga de trabajo
print("\n. Carga de trabajo de técnicos:")
tecnicos = Usuario.query.filter_by(role="tecnico").all()
for tecnico in tecnicos:
mantenimientos_tecnico = Mantenimiento.get_by_technician(tecnico.id)
fallas_tecnico = Falla.get_by_technician(tecnico.id)
print(f" - {tecnico.full_name}: {len(mantenimientos_tecnico)} mantenimientos, {len(fallas_tecnico)} fallas")

# Consulta 3: Equipos por tipo y estado
print("\n3. Resumen de equipos por tipo:")
# Esta consulta requeriría una unión más compleja en SQL real
equipos_nvr = NVR.query.count()
equipos_camara = Camara.query.count()
print(f" - NVRs: {equipos_nvr}")
print(f" - Cámaras: {equipos_camara}")

print("\n=== CONSULTAS COMPLETADAS ===")

if __name__ == "__main__":
# Ejecutar ejemplos
ejemplo_completo()
ejemplo_consultas_avanzadas()

print("\nPara usar estos modelos en tu aplicación Flask:")
print("""
=======
    """
    Ejemplo completo de uso de los modelos.
    """
    with app.app_context():
        print("=== EJEMPLO DE USO DE MODELOS SQLALCHEMY ===\n")
        
        # 1. CREAR USUARIOS
        print("1. Creando usuarios...")
        admin = Usuario(
            username="admin",
            email="admin@sistema.com",
            full_name="Administrador del Sistema",
            role="administrador",
            phone="+56 9 1234 5678",
            department="IT"
        )
        admin.set_password("admin123")
        admin.save()
        
        tecnico = Usuario(
            username="tecnico1",
            email="tecnico@sistema.com",
            full_name="Técnico Principal",
            role="tecnico",
            phone="+56 9 8765 4321",
            department="Soporte Técnico"
        )
        tecnico.set_password("tecnico123")
        tecnico.save()
        
        print(f"   Usuario creado: {admin.username} (ID: {admin.id})")
        print(f"   Usuario creado: {tecnico.username} (ID: {tecnico.id})")
        
        # 2. CREAR UBICACIONES
        print("\n2. Creando ubicaciones...")
        edificio_principal = Ubicacion(
            name="Edificio Principal",
            description="Edificio principal de la empresa",
            address="Av. Principal 123, Ciudad",
            location_type="edificio",
            building="Edificio Principal",
            floor="Piso 1",
            campus="Campus Central"
        )
        edificio_principal.save()
        
        sala_servidores = Ubicacion(
            name="Sala de Servidores",
            description="Sala principal de servidores",
            location_type="sala",
            building="Edificio Principal",
            floor="Sótano",
            parent_id=edificio_principal.id
        )
        sala_servidores.save()
        
        print(f"   Ubicación creada: {edificio_principal.name} (ID: {edificio_principal.id})")
        print(f"   Ubicación creada: {sala_servidores.name} (ID: {sala_servidores.id})")
        print(f"   Ruta completa: {sala_servidores.get_full_path()}")
        
        # 3. CREAR EQUIPOS NVR
        print("\n3. Creando equipos NVR...")
        nvr_principal = NVR(
            name="NVR-001",
            model="Hikvision DS-7732NIX",
            manufacturer="Hikvision",
            serial_number="NV20240001",
            inventory_number="INV-NVR-001",
            ip_address="192.168.1.10",
            system_type="nvr",
            channels=16,
            max_channels=32,
            storage_capacity=2000,  # 2TB
            ubicacion_id=sala_servidores.id,
            created_by=admin.id
        )
        nvr_principal.save()
        
        print(f"   NVR creado: {nvr_principal.name} (ID: {nvr_principal.id})")
        print(f"   Capacidad: {nvr_principal.get_total_recording_capacity_days()} días estimados")
        
        # 4. CREAR CÁMARAS
        print("\n4. Creando cámaras...")
        camara_entrada = Camara(
            name="Cámara Entrada Principal",
            model="Hikvision DS-2CD2145FWD-I",
            manufacturer="Hikvision",
            camera_type="domo",
            ip_address="192.168.1.101",
            mac_address="AA:BB:CC:DD:EE:01",
            port=554,
            connection_type="ethernet",
            power_over_ethernet=True,
            resolution="1920x1080",
            frame_rate=30,
            codec="H.264",
            nvr_id=nvr_principal.id,
            ubicacion_id=edificio_principal.id,
            created_by=admin.id
        )
        camara_entrada.save()
        
        # Agregar cámara al NVR
        nvr_principal.add_camera(camara_entrada)
        
        print(f"   Cámara creada: {camara_entrada.name} (ID: {camara_entrada.id})")
        print(f"   Conectada al NVR: {camara_entrada.nvr.name}")
        
        # 5. CREAR FALLAS
        print("\n5. Creando fallas...")
        falla_camara = Falla(
            title="Cámara sin señal",
            description="La cámara de entrada principal no muestra señal de video",
            falla_type="conectividad",
            priority="alta",
            equipment_id=camara_entrada.id,
            equipment_type="camara",
            camara_id=camara_entrada.id,
            ubicacion_id=edificio_principal.id,
            reported_by=tecnico.id,
            start_date=datetime.utcnow(),
            assigned_to=tecnico.id,
            assigned_date=datetime.utcnow(),
            estimated_resolution_time=2
        )
        falla_camara.save()
        
        print(f"   Falla creada: {falla_camara.title} (ID: {falla_camara.id})")
        print(f"   Estado: {falla_camara.status}")
        print(f"   Asignada a: {falla_camara.assigned_user.full_name}")
        
        # 6. CREAR MANTENIMIENTOS
        print("\n6. Creando mantenimientos...")
        mantenimiento_nvr = Mantenimiento(
            title="Mantenimiento preventivo NVR",
            description="Limpieza de filtros, verificación de discos duros, actualización de firmware",
            maintenance_type="preventivo",
            category="inspeccion",
            priority="media",
            equipment_id=nvr_principal.id,
            equipment_type="nvr",
            nvr_id=nvr_principal.id,
            ubicacion_id=sala_servidores.id,
            scheduled_start=datetime.utcnow() + timedelta(days=7),
            duration_estimated=3,
            technician_id=tecnico.id,
            supervisor_id=admin.id,
            maintenance_cost=0,
            parts_cost=0,
            labor_cost=150,
            external_cost=0,
            customer_notification=True,
            work_order_number=f"WO-{datetime.utcnow().strftime('%Y%m%d')}-001"
        )
        mantenimiento_nvr.save()
        
        print(f"   Mantenimiento creado: {mantenimiento_nvr.title} (ID: {mantenimiento_nvr.id})")
        print(f"   Programado para: {mantenimiento_nvr.scheduled_start}")
        print(f"   Orden de trabajo: {mantenimiento_nvr.work_order_number}")
        
        # 7. CREAR FOTOGRAFÍAS
        print("\n7. Creando fotografías...")
        foto_falla = Fotografia(
            filename="falla_camara_entrada.jpg",
            file_path="/uploads/fallas/falla_camara_entrada.jpg",
            file_size=2048576,  # 2MB
            mime_type="image/jpeg",
            photo_format="jpeg",
            width=1920,
            height=1080,
            photo_type="falla",
            status="procesando",
            title="Foto de falla en cámara de entrada",
            description="Captura mostrando ausencia de señal en cámara principal",
            equipment_id=camara_entrada.id,
            equipment_type="camara",
            camara_id=camara_entrada.id,
            ubicacion_id=edificio_principal.id,
            falla_id=falla_camara.id,
            uploaded_by=tecnico.id,
            capture_date=datetime.utcnow(),
            quality_score=85.5
        )
        foto_falla.save()
        
        print(f"   Fotografía creada: {foto_falla.filename} (ID: {foto_falla.id})")
        print(f"   Tamaño: {foto_falla.get_file_size_mb()} MB")
        print(f"   Dimensiones: {foto_falla.get_dimensions_string()}")
        print(f"   Calidad: {foto_falla.get_quality_rating()}")
        
        # 8. CREAR CONEXIONES DE RED
        print("\n8. Creando conexiones de red...")
        conexion = NetworkConnection(
            source_equipment_id=nvr_principal.id,
            source_equipment_type="nvr",
            target_equipment_id=camara_entrada.id,
            target_equipment_type="camara",
            connection_type="ethernet",
            cable_type="Cat6",
            cable_length=50.0,
            port_source="eth0",
            port_target="eth0",
            is_active=True,
            bandwidth_limit=100  # Mbps
        )
        conexion.save()
        
        print(f"   Conexión creada entre {nvr_principal.name} y {camara_entrada.name}")
        
        # 9. CONSULTAS Y RESÚMENES
        print("\n9. Consultas y resúmenes...")
        
        # Resumen de cámaras en ubicación
        camaras_ubicacion = Camara.get_by_location(edificio_principal.id)
        print(f"   Cámaras en {edificio_principal.name}: {len(camaras_ubicacion)}")
        
        # Resumen de fallas activas
        fallas_activas = Falla.get_active_fallas()
        print(f"   Fallas activas en el sistema: {len(fallas_activas)}")
        
        # Resumen de mantenimientos programados
        mantenimientos_programados = [m for m in Mantenimiento.query.all() if m.status == "programado"]
        print(f"   Mantenimientos programados: {len(mantenimientos_programados)}")
        
        # Resumen de NVR
        summary_nvr = nvr_principal.get_cameras_status_summary()
        print(f"   Estado de cámaras en {nvr_principal.name}: {summary_nvr}")
        
        print("\n=== EJEMPLO COMPLETADO EXITOSAMENTE ===")

def ejemplo_consultas_avanzadas():
    """
    Ejemplo de consultas avanzadas con los modelos.
    """
    with app.app_context():
        print("\n=== CONSULTAS AVANZADAS ===\n")
        
        # Consulta 1: Equipos por ubicación con falla
        print("1. Ubicaciones con equipos con fallas activas:")
        ubicaciones = Ubicacion.query.all()
        for ubicacion in ubicaciones:
            fallas_ubicacion = Falla.get_by_location(ubicacion.id)
            if fallas_ubicacion:
                print(f"   - {ubicacion.name}: {len(fallas_ubicacion)} fallas activas")
        
        # Consulta 2: Técnicos con carga de trabajo
        print("\n2. Carga de trabajo de técnicos:")
        tecnicos = Usuario.query.filter_by(role="tecnico").all()
        for tecnico in tecnicos:
            mantenimientos_tecnico = Mantenimiento.get_by_technician(tecnico.id)
            fallas_tecnico = Falla.get_by_technician(tecnico.id)
            print(f"   - {tecnico.full_name}: {len(mantenimientos_tecnico)} mantenimientos, {len(fallas_tecnico)} fallas")
        
        # Consulta 3: Equipos por tipo y estado
        print("\n3. Resumen de equipos por tipo:")
        # Esta consulta requeriría una unión más compleja en SQL real
        equipos_nvr = NVR.query.count()
        equipos_camara = Camara.query.count()
        print(f"   - NVRs: {equipos_nvr}")
        print(f"   - Cámaras: {equipos_camara}")
        
        print("\n=== CONSULTAS COMPLETADAS ===")

if __name__ == "__main__":
    # Ejecutar ejemplos
    ejemplo_completo()
    ejemplo_consultas_avanzadas()
    
    print("\nPara usar estos modelos en tu aplicación Flask:")
    print("""
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
from flask import Flask
from models import init_db, Usuario, Camara, etc.

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:pass@localhost/dbname'

# Inicializar la base de datos
init_db(app)

# Usar los modelos
with app.app_context():
<<<<<<< HEAD
usuario = Usuario(username="nuevo", email="nuevo@ejemplo.com")
usuario.save()
=======
    usuario = Usuario(username="nuevo", email="nuevo@ejemplo.com")
    usuario.save()
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
""")