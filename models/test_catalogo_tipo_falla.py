"""
Script de prueba para el modelo CatalogoTipoFalla.

Este script demuestra el uso del modelo catalogo_tipo_falla y sus funcionalidades.
"""

from models import db, CatalogoTipoFalla, CategoriaFalla, GravedadFalla, Falla


def test_catalogo_tipo_falla():
"""
Prueba las funcionalidades básicas del modelo CatalogoTipoFalla.
"""
print(" Iniciando pruebas del modelo CatalogoTipoFalla...")

# Test 1: Crear tipos de falla
print("\n1. Creando tipos de falla...")

tipos_falla = [
{
"nombre": "Falla de Conectividad de Red",
"categoria": CategoriaFalla.CONECTIVIDAD,
"descripcion": "Problemas de conexión de red entre equipos",
"gravedad": GravedadFalla.ALTA,
"tiempo_estimado_resolucion": 10
},
{
"nombre": "Falla de Cámara Sin Video",
"categoria": CategoriaFalla.HARDWARE,
"descripcion": "La cámara no transmite imagen",
"gravedad": GravedadFalla.MEDIA,
"tiempo_estimado_resolucion": 90
},
{
"nombre": "Problema de Configuración NVR",
"categoria": CategoriaFalla.CONFIGURACION,
"descripcion": "Configuración incorrecta del equipo NVR",
"gravedad": GravedadFalla.MEDIA,
"tiempo_estimado_resolucion": 60
}
]

for tipo_data in tipos_falla:
# Verificar si ya existe
existe = CatalogoTipoFalla.query.filter_by(nombre=tipo_data["nombre"]).first()
if not existe:
tipo_falla = CatalogoTipoFalla(**tipo_data)
tipo_falla.save()
print(f" Creado: {tipo_falla.nombre}")
else:
print(f" Ya existe: {tipo_data['nombre']}")

# Test : Consultar tipos por categoría
print("\n. Consultando tipos por categoría...")

tipos_conectividad = CatalogoTipoFalla.get_by_categoria(CategoriaFalla.CONECTIVIDAD)
print(f" Tipos de conectividad: {len(tipos_conectividad)}")
for tipo in tipos_conectividad:
print(f" - {tipo.nombre}")

# Test 3: Consultar tipos por gravedad
print("\n3. Consultando tipos por gravedad...")

tipos_alta_gravedad = CatalogoTipoFalla.get_by_gravedad(GravedadFalla.ALTA)
print(f" Tipos de alta gravedad: {len(tipos_alta_gravedad)}")
for tipo in tipos_alta_gravedad:
print(f" - {tipo.nombre} ({tipo.get_gravedad_display()})")

# Test 4: Buscar por nombre
print("\n4. Búsqueda por nombre...")

resultados = CatalogoTipoFalla.search_by_nombre("cámara")
print(f" Resultados para 'cámara': {len(resultados)}")
for tipo in resultados:
print(f" - {tipo.nombre}")

# Test 5: Obtener categorías y gravedades disponibles
print("\n5. Categorías y gravedades disponibles...")

categorias = CatalogoTipoFalla.get_categorias_disponibles()
print(f" Categorías: {categorias}")

gravedades = CatalogoTipoFalla.get_gravedades_disponibles()
print(f" Gravedades: {gravedades}")

# Test 6: Estadísticas por categoría
print("\n6. Estadísticas por categoría...")

stats = CatalogoTipoFalla.get_estadisticas_categoria()
for categoria, datos in stats.items():
print(f" {categoria}: {datos['total_tipos']} tipos, "
f"tiempo promedio: {datos['tiempo_promedio']:.0f} min")

# Test 7: Probar métodos de utilidad
print("\n7. Probando métodos de utilidad...")

primer_tipo = CatalogoTipoFalla.query.first()
if primer_tipo:
print(f" Nombre: {primer_tipo.get_display_name()}")
print(f" Categoría: {primer_tipo.get_categoria_display()}")
print(f" Gravedad: {primer_tipo.get_gravedad_display()}")
print(f" ⏱ Tiempo (horas): {primer_tipo.get_tiempo_estimado_horas()}")
print(f" Gravedad numérica: {primer_tipo.get_numeric_gravedad()}")

# Test 8: Mostrar todos los tipos
print("\n8. Lista completa de tipos de falla:")

todos_tipos = CatalogoTipoFalla.query.all()
for tipo in todos_tipos:
print(f" {tipo.nombre}")
print(f" Categoría: {tipo.get_categoria_display()}")
print(f" Gravedad: {tipo.get_gravedad_display()}")
print(f" Tiempo: {tipo.get_tiempo_estimado_horas()}h")
print()

print(" ¡Pruebas completadas exitosamente")

return True


if __name__ == "__main__":
# Nota: Este script asume que la base de datos ya está configurada
# En un entorno real, necesitarías configurar la app Flask primero

try:
test_catalogo_tipo_falla()
except Exception as e:
print(f" Error durante las pruebas: {e}")
print(" Asegúrate de que la base de datos esté configurada")
