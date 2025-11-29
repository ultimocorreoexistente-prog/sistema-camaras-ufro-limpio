# Endpoint temporal para limpiar tablas específicas
@app.route('/limpiar-tablas-especificas')
def limpiar_tablas_especificas():
<<<<<<< HEAD
"""Endpoint específico para eliminar tablas singulares restantes"""
try:
resultado = {
'timestamp': datetime.now().isoformat(),
'acciones_realizadas': []
}

from sqlalchemy import text, create_engine
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

with engine.connect() as conn:
# Lista específica de tablas a eliminar
tablas_eliminar = [
'switch',
'ubicacion',
'puerto_switch',
'equipo_tecnico',
'camara',
'gabinete',
'mantenimiento',
'falla'
]

for tabla in tablas_eliminar:
try:
# Verificar si existe la tabla
existe_query = text("""
SELECT EXISTS (
SELECT 1 FROM information_schema.tables
WHERE table_name = :tabla AND table_schema = 'public'
)
""")

existe_result = conn.execute(existe_query, {'tabla': tabla}).scalar()

if existe_result:
# Eliminar la tabla
drop_query = text(f"DROP TABLE IF EXISTS {tabla} CASCADE")
conn.execute(drop_query)
resultado['acciones_realizadas'].append(f" Tabla '{tabla}' eliminada")
print(f"Tabla {tabla} eliminada")
else:
resultado['acciones_realizadas'].append(f"ℹ Tabla '{tabla}' no existe")

except Exception as e:
resultado['acciones_realizadas'].append(f" Error con '{tabla}': {str(e)}")

# Commit final
try:
conn.commit()
resultado['commit'] = 'Exitoso'
except Exception as e:
resultado['commit'] = f"Error: {str(e)}"

return jsonify(resultado)

except Exception as e:
return jsonify({'error': f"Error general: {str(e)}"})
=======
    """Endpoint específico para eliminar tablas singulares restantes"""
    try:
        resultado = {
            'timestamp': datetime.now().isoformat(),
            'acciones_realizadas': []
        }
        
        from sqlalchemy import text, create_engine
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        
        with engine.connect() as conn:
            # Lista específica de tablas a eliminar
            tablas_eliminar = [
                'switch',
                'ubicacion', 
                'puerto_switch',
                'equipo_tecnico',
                'camara',
                'gabinete',
                'mantenimiento',
                'falla'
            ]
            
            for tabla in tablas_eliminar:
                try:
                    # Verificar si existe la tabla
                    existe_query = text("""
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.tables 
                            WHERE table_name = :tabla AND table_schema = 'public'
                        )
                    """)
                    
                    existe_result = conn.execute(existe_query, {'tabla': tabla}).scalar()
                    
                    if existe_result:
                        # Eliminar la tabla
                        drop_query = text(f"DROP TABLE IF EXISTS {tabla} CASCADE")
                        conn.execute(drop_query)
                        resultado['acciones_realizadas'].append(f"✅ Tabla '{tabla}' eliminada")
                        print(f"Tabla {tabla} eliminada")
                    else:
                        resultado['acciones_realizadas'].append(f"ℹ️ Tabla '{tabla}' no existe")
                        
                except Exception as e:
                    resultado['acciones_realizadas'].append(f"❌ Error con '{tabla}': {str(e)}")
            
            # Commit final
            try:
                conn.commit()
                resultado['commit'] = 'Exitoso'
            except Exception as e:
                resultado['commit'] = f"Error: {str(e)}"
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'error': f"Error general: {str(e)}"})
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
