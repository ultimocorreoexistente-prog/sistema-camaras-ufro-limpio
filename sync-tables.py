<<<<<<< HEAD
<<<<<<< HEAD
#/usr/bin/env python3
=======
#!/usr/bin/env python3
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
=======
#!/usr/bin/env python3
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
# sync-tables.py
"""
Verifica que todas las ForeignKey apunten a tablas que existen.
Evita el error: "NoReferencedTableError: could not find table 'nvrs'"
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.equipo import UPS, Switch, NVR, Gabinete, FuentePoder
from models.usuario import Usuario
from models.ubicacion import Ubicacion
from models.camara import Camara
from models.mantenimiento import Mantenimiento
from models.falla import Falla
from models.fotografia import Fotografia

def check_table_names():
<<<<<<< HEAD
<<<<<<< HEAD
print(" Verificando nombres de tablas y FKs...")

# Tablas reales (de __tablename__)
table_names = {
'usuarios': Usuario,
'ubicaciones': Ubicacion,
'camaras': Camara,
'nvr_dvr': NVR, # tu nombre real
'switches': Switch,
'ups': UPS,
'gabinetes': Gabinete,
'fuente_poder': FuentePoder, # tu nombre real
'mantenimientos': Mantenimiento,
'fallas': Falla,
'fotografias': Fotografia,
}

# FKs esperadas (tabla → [lista de FKs que debe contener])
fk_checks = {
'camaras': ['nvr_dvr.id'], # no 'nvrs.id'
'mantenimientos': ['fuente_poder.id', 'nvr_dvr.id', 'ups.id'],
}

all_good = True
for table, cls in table_names.items():
print(f" {table}: {cls.__tablename__}")

for table, expected_fks in fk_checks.items():
cls = table_names[table]
for col in cls.__table__.columns:
if hasattr(col, 'foreign_keys') and col.foreign_keys:
for fk in col.foreign_keys:
target = f"{fk.column.table.name}.{fk.column.name}"
if target not in expected_fks and not target.startswith('usuarios.id'):
print(f" ADVERTENCIA en {table}: FK inesperada → {target}")
# Verificar que las FKs esperadas estén presentes
cols_fk = [f"{fk.column.table.name}.{fk.column.name}"
for col in cls.__table__.columns
for fk in getattr(col, 'foreign_keys', [])]
for expected in expected_fks:
if expected not in cols_fk:
print(f" FALTA en {table}: FK esperada → {expected}")
all_good = False

if all_good:
print("\n Todas las tablas y FKs están alineadas.")
return True
else:
print("\n Corrige los errores antes de continuar.")
return False

if __name__ == "__main__":
success = check_table_names()
sys.exit(0 if success else 1)
=======
=======
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
    print("🔍 Verificando nombres de tablas y FKs...")
    
    # Tablas reales (de __tablename__)
    table_names = {
        'usuarios': Usuario,
        'ubicaciones': Ubicacion,
        'camaras': Camara,
        'nvr_dvr': NVR,          # ✅ tu nombre real
        'switches': Switch,
        'ups': UPS,
        'gabinetes': Gabinete,
        'fuente_poder': FuentePoder,  # ✅ tu nombre real
        'mantenimientos': Mantenimiento,
        'fallas': Falla,
        'fotografias': Fotografia,
    }

    # FKs esperadas (tabla → [lista de FKs que debe contener])
    fk_checks = {
        'camaras': ['nvr_dvr.id'],  # ❌ no 'nvrs.id'
        'mantenimientos': ['fuente_poder.id', 'nvr_dvr.id', 'ups.id'],
    }

    all_good = True
    for table, cls in table_names.items():
        print(f"  ✅ {table}: {cls.__tablename__}")

    for table, expected_fks in fk_checks.items():
        cls = table_names[table]
        for col in cls.__table__.columns:
            if hasattr(col, 'foreign_keys') and col.foreign_keys:
                for fk in col.foreign_keys:
                    target = f"{fk.column.table.name}.{fk.column.name}"
                    if target not in expected_fks and not target.startswith('usuarios.id'):
                        print(f"  ⚠️  ADVERTENCIA en {table}: FK inesperada → {target}")
        # Verificar que las FKs esperadas estén presentes
        cols_fk = [f"{fk.column.table.name}.{fk.column.name}" 
                   for col in cls.__table__.columns
                   for fk in getattr(col, 'foreign_keys', [])]
        for expected in expected_fks:
            if expected not in cols_fk:
                print(f"  ❌ FALTA en {table}: FK esperada → {expected}")
                all_good = False

    if all_good:
        print("\n✅ Todas las tablas y FKs están alineadas.")
        return True
    else:
        print("\n❌ Corrige los errores antes de continuar.")
        return False

if __name__ == "__main__":
    success = check_table_names()
<<<<<<< HEAD
    sys.exit(0 if success else 1)
>>>>>>> 490f0beca4eaa0ced06723ea308d2616d581f5a4
=======
    sys.exit(0 if success else 1)
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
