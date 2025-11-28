#!/bin/bash

echo "🔧 Aplicando correcciones para UsuarioLog..."

echo "✅ 1. Eliminado archivo duplicado usuario_log.py"
echo "✅ 2. Agregada relación 'logs' al modelo Usuario"
echo "✅ 3. UsuarioLog agregado a __all__ en models/__init__.py"
echo "✅ 4. Importación de UsuarioLog agregada a models/__init__.py"

echo ""
echo "🚀 Aplicando cambios a Git..."
git add models/usuario.py models/__init__.py models/usuario_logs.py

echo "💬 Creando commit..."
git commit -m "fix: resolver duplicación de UsuarioLog y agregar relación logs

- Eliminar archivo duplicado usuario_log.py 
- Agregar relación 'logs' al modelo Usuario para back_populates
- UsuarioLog agregado a __all__ e importaciones en models/__init__.py
- Sistema de auditoría y logs ahora completamente funcional"

echo ""
echo "📤 Enviando a Railway..."
git push origin main

echo ""
echo "🎉 Correcciones aplicadas! Railway redesplegará en 2-3 minutos"