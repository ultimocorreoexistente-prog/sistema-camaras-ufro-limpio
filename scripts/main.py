"""
Aplicación de ejemplo para inicializar la base de datos y modelos.
"""

from flask import Flask
from models import db, Base, EquipmentStatus
from models.ups import UPS, UPSType, BatteryType, LoadStatus
from models.equipo import Ubicacion, Usuario
from datetime import datetime, timedelta

app = Flask(__name__)
# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa SQLAlchemy con la aplicación Flask
db.init_app(app)

def create_initial_data(app):
    """Crea un usuario y una ubicación de ejemplo, y un registro de UPS."""
    with app.app_context():
        # Crear la estructura de la base de datos
        Base.metadata.create_all(db.engine)

        # Crear datos de ejemplo si no existen
        if Ubicacion.query.count() == 0:
            user = Usuario(username="admin", email="admin@example.com")
            db.session.add(user)
            db.session.commit()

            location = Ubicacion(name="Datacenter Principal", description="Rack A1")
            db.session.add(location)
            db.session.commit()

            print("--- Datos iniciales creados ---")

            # Crear un UPS de ejemplo
            example_ups = UPS(
                name="UPS APC 3000VA",
                manufacturer="APC",
                model="SMT3000RMI2U",
                serial_number="XYZ12345",
                asset_tag="IT-UPS-001",
                ubicacion_id=location.id,
                created_by=user.id,
                status=EquipmentStatus.ACTIVO,
                ups_type=UPSType.LINE_INTERACTIVE,
                capacity_va=3000,
                capacity_watts=2700,
                load_percentage=55.0,
                runtime_minutes=15,
                battery_health_percentage=85.0,
                battery_type=BatteryType.VRLA,
                last_battery_test=datetime.utcnow() - timedelta(days=15),
                next_battery_test=datetime.utcnow() + timedelta(days=15)
            )
            db.session.add(example_ups)
            db.session.commit()

            print(f"UPS creado: {example_ups.name}")
            print(f"Capacidad estimada en Watts: {example_ups.get_capacity_watts_estimated()}")
            print(f"Autonomía estimada actual (min): {example_ups.get_current_runtime_estimate()}")

        else:
            print("La base de datos ya contiene datos. Omitiendo creación de ejemplo.")


if __name__ == '__main__':
    create_initial_data(app)
    # Aquí puedes añadir código para ejecutar la aplicación web si fuera necesario
    # app.run(debug=True)