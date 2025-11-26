#!/usr/bin/env python3
"""
fix_all_models.py — Corrige TODOS los errores en models/
- Añade id = Column(Integer, primary_key=True) donde falta
- Corrige indentación de __tablename__ y docstrings
- Corrige String(0) → String(20/50)
- Corrige priority_level = default=, → default=2

Ejecuta: python fix_all_models.py
"""
import os
import re

MODELS_DIR = "models"
FIXES = [
    # 1. Añadir primary key si falta (después de __tablename__)
    (
        r"(class\s+\w+\s*\(.*?\):\s*\n(?:\s{4}\w+\s*=\s*Column.*\n)*?)(\s{4}__tablename__\s*=\s*['\"][^'\"]+['\"])",
        r"\1\2\n    id = Column(Integer, primary_key=True)"
    ),
    # 2. Corregir indentación de __tablename__ (si está al inicio de línea)
    (r"^(__tablename__\s*=\s*['\"][^'\"]+['\"])$", r"    \1"),
    # 3. Corregir docstrings sin indentar en enums y clases
    (r"(class\s+\w+\s*\(.*?\):\s*\n)(\"\"\".*?\"\"\")", r"\1    \2"),
    # 4. Corregir String(0)
    (r"String\(0\)", "String(20)"),
    (r"(alarm_status\s*=\s*Column\()String\(0\)", r"\1String(50)"),
    (r"(disk_health_status\s*=\s*Column\()String\(0\)", r"\1String(50)"),
    # 5. Corregir priority_level = default=,
    (r"(priority_level\s*=\s*Column\(.*?,\s*default=,)", r"\1 default=2,"),
    # 6. Corregir comparación de estado
    (r"(if\s+self\.status\s*=\s*EquipmentStatus\.ACTIVO)", r"if self.status != EquipmentStatus.ACTIVO.value"),
    # 7. Corregir round(..., )
    (r"round\(([^)]+),\s*\)", r"round(\1, 2)"),
    # 8. Corregir return sin indentar en __repr__
    (r"(\s*def __repr__\([^)]*\):\s*\n)(return\s+f?['\"])", r"\1    \2"),
]

def fix_file(filepath):
    print(f"🔧 Corrigiendo: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        for pattern, repl in FIXES:
            content = re.sub(pattern, repl, content, flags=re.MULTILINE | re.DOTALL)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Corregido")
            return True
        else:
            print(f"  ⚪ Sin cambios")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print("🚀 Iniciando corrección automática de TODOS los modelos...\n")
    
    # Lista de archivos a corregir (ordenados por dependencia)
    files_to_fix = [
        "falla.py", "fotografia.py",  "camara.py",
        "gabinete.py", "switch.py", "nvr.py", "ups.py", "fuente_poder.py",
        "ubicacion.py", "usuario.py"
    ]
    
    fixed = 0
    for filename in files_to_fix:
        filepath = os.path.join(MODELS_DIR, filename)
        if os.path.exists(filepath):
            if fix_file(filepath):
                fixed += 1
    
    print(f"\n✅ {fixed} archivos corregidos.")
    print("🎯 Ejecuta ahora:")
    print("   python -c \"from models import Gabinete, Switch, NVR, UPS; print('✅ OK')\"")

if __name__ == "__main__":
    main()