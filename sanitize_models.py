#!/usr/bin/env python3
"""
sanitize_models.py
Corrige el problema de código ejecutable global en models/
Moviendo scripts de ejemplo a scripts/ y encapsulándolos en if __name__ == "__main__"
"""

import os
import shutil
import re

def move_and_sanitize(src_path, dst_path):
    """Mueve un archivo y lo envuelve en if __name__ == '__main__' si no lo tiene"""
    if not os.path.exists(src_path):
        print(f"⚠️  {src_path} no existe. Saltando.")
        return False

    print(f"🔧 Procesando: {src_path} → {dst_path}")

    # Leer contenido
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Si ya tiene `if __name__ == "__main__":`, no modificar
    if 'if __name__ == "__main__":' in content or 'if __name__ == \'__main__\':' in content:
        print(f"   ✅ Ya tiene protección. Solo moviendo.")
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.move(src_path, dst_path)
        return True

    # Detectar contenido "main" (todo lo que no sea import, class, def, docstring)
    lines = content.splitlines()
    main_lines = []
    in_docstring = False
    in_import_section = True

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            main_lines.append(line)
            continue

        # Fin de la sección de imports/clases/def
        if in_import_section and not (
            stripped.startswith(('import ', 'from ', 'class ', 'def ', '__', '#', '"""', "'''"))
            or (i == 0 and stripped.startswith('#'))
        ):
            in_import_section = False

        if not in_import_section:
            # Saltar líneas de docstring
            if '"""' in line or "'''" in line:
                in_docstring = not in_docstring
                main_lines.append(line)
            elif not in_docstring:
                main_lines.append(line)

    # Si hay código ejecutable global, envolverlo
    if main_lines and any(line.strip() and not line.strip().startswith('#') for line in main_lines):
        # Separar imports/clases/def del código ejecutable
        top_lines = []
        in_import_section = True
        for line in lines:
            stripped = line.strip()
            if in_import_section and (
                stripped.startswith(('import ', 'from ', 'class ', 'def ', '__'))
                or not stripped
                or stripped.startswith('#')
                or '"""' in line or "'''" in line
            ):
                top_lines.append(line)
            else:
                in_import_section = False
                break

        # Construir nuevo contenido
        new_content = '\n'.join(top_lines).rstrip() + '\n\n'
        new_content += 'if __name__ == "__main__":\n'
        for line in main_lines:
            new_content += '    ' + line + '\n'
        new_content += '\n'

        # Guardar en destino
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        with open(dst_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        # Borrar original
        os.remove(src_path)
        print(f"   ✅ Sanitizado y movido.")
        return True
    else:
        # Solo mover
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.move(src_path, dst_path)
        print(f"   ✅ Movido sin cambios.")
        return True


def main():
    print("🧹 Sanitizando models/ — moviendo scripts a scripts/ y añadiendo protección...")
    print("=" * 70)

    # Archivos a mover y sanitizar
    to_move = [
        ("models/datos_iniciales.py", "scripts/datos_iniciales.py"),
        ("models/ejemplo_uso.py", "scripts/ejemplo_uso.py"),
        ("models/install.py", "scripts/install.py"),
    ]

    moved = 0
    for src, dst in to_move:
        if move_and_sanitize(src, dst):
            moved += 1

    print("=" * 70)
    print(f"✅ {moved} archivos sanitizados y movidos a scripts/")
    print("\n📌 Siguiente paso recomendado:")
    print("   python scripts/create_superadmin.py")
    print("   python app.py")


if __name__ == "__main__":
    main()