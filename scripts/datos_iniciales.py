#import sys
import os
from datetime import datetime, timedelta

# Asegurar que el path incluya la raíz del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db
from models.usuario import Usuario
from models.usuario_roles import UserRole
from models.ubicacion import Ubicacion
from models.gabinete import Gabinete, CabinetType
from models.nvr import NVR, NVRSystemType
from models.switch import Switch, SwitchType
from models.ups import UPS, UPSType
from models.camara import Camara, CameraType
from models.equipo import NetworkConnection


def insert_initial_data():
<<<<<<< HEAD
"""Inserta datos iniciales de ejemplo — solo se ejecuta si se llama directamente."""
with app.app_context():
print(" INSERTANDO DATOS INICIALES")
print("=" * 40)

# 1. Usuarios
if not Usuario.query.filter_by(username="admin").first():
admin = Usuario(
username="admin",
email="admin@sistema.com",
full_name="Administrador del Sistema",
role=UserRole.ADMINISTRADOR,
phone="+56 9 134 5678",
department="TI",
is_active=True
)
admin.set_password("Admin05")
db.session.add(admin)
db.session.commit()
print(f" Usuario admin creado (ID: {admin.id})")

admin = Usuario.query.filter_by(username="admin").first()
if not Usuario.query.filter_by(username="tecnico").first():
tecnico = Usuario(
username="tecnico",
email="tecnico@sistema.com",
full_name="Técnico Principal",
role=UserRole.TECNICO,
phone="+56 9 8765 431",
department="Soporte Técnico",
is_active=True
)
tecnico.set_password("Tecnico05")
db.session.add(tecnico)
db.session.commit()
print(f" Usuario técnico creado (ID: {tecnico.id})")

# . Ubicaciones
if not Ubicacion.query.filter_by(nombre="Campus Principal").first():
campus = Ubicacion(
nombre="Campus Principal",
tipo="campus",
codigo="CP001"
)
db.session.add(campus)
db.session.flush()

edificio = Ubicacion(
nombre="Edificio A",
tipo="edificio",
codigo="EA001",
parent_id=campus.id
)
db.session.add(edificio)
db.session.flush()

sala = Ubicacion(
nombre="Sala de Servidores",
tipo="sala",
codigo="SS001",
parent_id=edificio.id
)
db.session.add(sala)
db.session.flush()

recepcion = Ubicacion(
nombre="Recepción",
tipo="area",
codigo="RC001",
parent_id=edificio.id
)
db.session.add(recepcion)
db.session.commit()
print(" Ubicaciones creadas")

sala = Ubicacion.query.filter_by(codigo="SS001").first()
recepcion = Ubicacion.query.filter_by(codigo="RC001").first()

# 3. Equipos
if not NVR.query.filter_by(nombre="NVR-Principal-01").first():
nvr = NVR(
nombre="NVR-Principal-01",
modelo="Hikvision DS-773NIX-4P",
estado="activo",
ubicacion_id=sala.id,
created_by_user_id=admin.id
)
db.session.add(nvr)
db.session.flush()

switch_core = Switch(
nombre="Switch-Core-01",
modelo="Cisco Catalyst 960X",
estado="activo",
ubicacion_id=sala.id,
created_by_user_id=admin.id
)
db.session.add(switch_core)
db.session.flush()

ups = UPS(
nombre="UPS-Principal-01",
modelo="APC Smart-UPS 6000VA",
estado="activo",
ubicacion_id=sala.id,
created_by_user_id=admin.id
)
db.session.add(ups)
db.session.flush()

camara1 = Camara(
codigo="CAM-RC-001",
nombre="Cámara Recepción",
estado="activo",
ubicacion_id=recepcion.id,
nvr_id=nvr.id,
created_by_user_id=admin.id
)
db.session.add(camara1)

camara = Camara(
codigo="CAM-EN-001",
nombre="Cámara Entrada",
estado="activo",
ubicacion_id=recepcion.id,
nvr_id=nvr.id,
created_by_user_id=admin.id
)
db.session.add(camara)
db.session.commit()
print(" Equipos creados")

# 4. Conexiones (opcional)
if not NetworkConnection.query.first():
conn1 = NetworkConnection(
source_equipment_id=nvr.id,
source_equipment_type="nvr",
target_equipment_id=switch_core.id,
target_equipment_type="switch",
connection_type="ethernet",
is_active=True
)
db.session.add(conn1)
db.session.commit()
print(" Conexiones creadas")

print("\n DATOS INICIALES CREADOS EXITOSAMENTE")
print("\n CREDENCIALES:")
print(" - admin / Admin05")
print(" - tecnico / Tecnico05")


# Solo se ejecuta si se llama directamente: python scripts/datos_iniciales.py
if __name__ == "__main__":
insert_initial_data()
=======
    """Inserta datos iniciales de ejemplo — solo se ejecuta si se llama directamente."""
    with app.app_context():
        print("📊 INSERTANDO DATOS INICIALES")
        print("=" * 40)

        # 1. Usuarios
        if not Usuario.query.filter_by(username="admin").first():
            admin = Usuario(
                username="admin",
                email="admin@sistema.com",
                full_name="Administrador del Sistema",
                role=UserRole.ADMINISTRADOR,
                phone="+56 9 1234 5678",
                department="TI",
                is_active=True
            )
            admin.set_password("Admin2025!")
            db.session.add(admin)
            db.session.commit()
            print(f"   ✅ Usuario admin creado (ID: {admin.id})")

        admin = Usuario.query.filter_by(username="admin").first()
        if not Usuario.query.filter_by(username="tecnico").first():
            tecnico = Usuario(
                username="tecnico",
                email="tecnico@sistema.com",
                full_name="Técnico Principal",
                role=UserRole.TECNICO,
                phone="+56 9 8765 4321",
                department="Soporte Técnico",
                is_active=True
            )
            tecnico.set_password("Tecnico2025!")
            db.session.add(tecnico)
            db.session.commit()
            print(f"   ✅ Usuario técnico creado (ID: {tecnico.id})")

        # 2. Ubicaciones
        if not Ubicacion.query.filter_by(nombre="Campus Principal").first():
            campus = Ubicacion(
                nombre="Campus Principal",
                tipo="campus",
                codigo="CP001"
            )
            db.session.add(campus)
            db.session.flush()

            edificio = Ubicacion(
                nombre="Edificio A",
                tipo="edificio",
                codigo="EA001",
                parent_id=campus.id
            )
            db.session.add(edificio)
            db.session.flush()

            sala = Ubicacion(
                nombre="Sala de Servidores",
                tipo="sala",
                codigo="SS001",
                parent_id=edificio.id
            )
            db.session.add(sala)
            db.session.flush()

            recepcion = Ubicacion(
                nombre="Recepción",
                tipo="area",
                codigo="RC001",
                parent_id=edificio.id
            )
            db.session.add(recepcion)
            db.session.commit()
            print("   ✅ Ubicaciones creadas")

        sala = Ubicacion.query.filter_by(codigo="SS001").first()
        recepcion = Ubicacion.query.filter_by(codigo="RC001").first()

        # 3. Equipos
        if not NVR.query.filter_by(nombre="NVR-Principal-01").first():
            nvr = NVR(
                nombre="NVR-Principal-01",
                modelo="Hikvision DS-7732NIX-4P",
                estado="activo",
                ubicacion_id=sala.id,
                created_by_user_id=admin.id
            )
            db.session.add(nvr)
            db.session.flush()

            switch_core = Switch(
                nombre="Switch-Core-01",
                modelo="Cisco Catalyst 2960X",
                estado="activo",
                ubicacion_id=sala.id,
                created_by_user_id=admin.id
            )
            db.session.add(switch_core)
            db.session.flush()

            ups = UPS(
                nombre="UPS-Principal-01",
                modelo="APC Smart-UPS 6000VA",
                estado="activo",
                ubicacion_id=sala.id,
                created_by_user_id=admin.id
            )
            db.session.add(ups)
            db.session.flush()

            camara1 = Camara(
                codigo="CAM-RC-001",
                nombre="Cámara Recepción",
                estado="activo",
                ubicacion_id=recepcion.id,
                nvr_id=nvr.id,
                created_by_user_id=admin.id
            )
            db.session.add(camara1)

            camara2 = Camara(
                codigo="CAM-EN-001",
                nombre="Cámara Entrada",
                estado="activo",
                ubicacion_id=recepcion.id,
                nvr_id=nvr.id,
                created_by_user_id=admin.id
            )
            db.session.add(camara2)
            db.session.commit()
            print("   ✅ Equipos creados")

        # 4. Conexiones (opcional)
        if not NetworkConnection.query.first():
            conn1 = NetworkConnection(
                source_equipment_id=nvr.id,
                source_equipment_type="nvr",
                target_equipment_id=switch_core.id,
                target_equipment_type="switch",
                connection_type="ethernet",
                is_active=True
            )
            db.session.add(conn1)
            db.session.commit()
            print("   ✅ Conexiones creadas")

        print("\n🎉 DATOS INICIALES CREADOS EXITOSAMENTE")
        print("\n🔑 CREDENCIALES:")
        print("   - admin / Admin2025!")
        print("   - tecnico / Tecnico2025!")


# 🔑 Solo se ejecuta si se llama directamente: python scripts/datos_iniciales.py
if __name__ == "__main__":
    insert_initial_data()
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
