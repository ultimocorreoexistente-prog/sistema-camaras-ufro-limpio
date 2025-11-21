"""
Modelo SQLAlchemy para catalogo_tipo_falla.

Proporciona la estructura y métodos para gestionar el catálogo de tipos de fallas
del sistema, incluyendo categorización, niveles de gravedad y estimaciones de tiempo.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db
from models.enums.categoria_falla import CategoriaFalla
from models.enums.gravedad_falla import GravedadFalla


class CatalogoTipoFalla(BaseModel, db.Model):
"""
Catálogo de tipos de fallas del sistema.

Almacena los diferentes tipos de fallas que pueden ocurrir en el sistema,
clasificados por categoría y nivel de gravedad, con tiempos estimados de resolución.

Attributes:
nombre (str): Nombre del tipo de falla
categoria (str): Categoría de la falla
descripcion (str): Descripción detallada
gravedad (str): Nivel de gravedad
tiempo_estimado_resolucion (int): Tiempo estimado en minutos
"""

__tablename__ = 'catalogo_tipo_falla'

# Campos de la tabla (Railway schema)
nombre = Column(String(100), nullable=False, unique=True, index=True,
comment="Nombre único del tipo de falla")
categoria = Column(String(50), nullable=True, index=True,
comment="Categoría de la falla")
descripcion = Column(Text, nullable=True,
comment="Descripción detallada del tipo de falla")
gravedad = Column(String(0), nullable=True, index=True,
comment="Nivel de gravedad de la falla")
tiempo_estimado_resolucion = Column(Integer, nullable=True,
comment="Tiempo estimado de resolución en minutos")

# Relaciones
fallas = relationship("Falla", back_populates="tipo_falla",
cascade="all, delete-orphan",
doc="Fallas que pertenecen a este tipo")

def __repr__(self):
return f"<CatalogoTipoFalla(id={self.id}, nombre='{self.nombre}', categoria='{self.categoria}')>"

def to_dict(self, include_relations=False):
"""
Convierte el modelo a diccionario.

Args:
include_relations (bool): Si incluir relaciones

Returns:
dict: Representación en diccionario
"""
data = {
'id': self.id,
'nombre': self.nombre,
'categoria': self.categoria,
'descripcion': self.descripcion,
'gravedad': self.gravedad,
'tiempo_estimado_resolucion': self.tiempo_estimado_resolucion,
'created_at': self.created_at.isoformat() if self.created_at else None,
'updated_at': self.updated_at.isoformat() if self.updated_at else None,
'deleted': self.deleted
}

if include_relations:
data['fallas'] = [falla.to_dict() for falla in self.fallas]
data['total_fallas'] = len(self.fallas)

return data

def get_display_name(self):
"""
Obtiene el nombre para mostrar en la interfaz.

Returns:
str: Nombre completo con categoría
"""
if self.categoria:
return f"{self.nombre} ({self.categoria})"
return self.nombre

def is_valid_categoria(self):
"""
Valida si la categoría está en la lista de categorías válidas.

Returns:
bool: True si es válida
"""
return self.categoria in CategoriaFalla.get_values()

def is_valid_gravedad(self):
"""
Valida si la gravedad está en la lista de gravedades válidas.

Returns:
bool: True si es válida
"""
return self.gravedad in GravedadFalla.get_values()

def get_numeric_gravedad(self):
"""
Obtiene el valor numérico de la gravedad para ordenamiento.

Returns:
int: Valor numérico (mayor = más grave)
"""
return GravedadFalla.get_numeric_value(self.gravedad)

def get_categoria_display(self):
"""
Obtiene la categoría en formato legible.

Returns:
str: Categoría en formato legible
"""
choices = dict(CategoriaFalla.get_choices())
return choices.get(self.categoria, self.categoria or "Sin categoría")

def get_gravedad_display(self):
"""
Obtiene la gravedad en formato legible.

Returns:
str: Gravedad en formato legible
"""
choices = dict(GravedadFalla.get_choices())
return choices.get(self.gravedad, self.gravedad or "Sin definir")

def get_tiempo_estimado_horas(self):
"""
Obtiene el tiempo estimado en horas.

Returns:
float: Tiempo en horas
"""
if self.tiempo_estimado_resolucion:
return round(self.tiempo_estimado_resolucion / 60.0, )
return None

def save(self, commit=True):
"""
Guarda el registro y valida los datos.

Args:
commit (bool): Si hacer commit en la base de datos
"""
# Validaciones
if self.categoria and not self.is_valid_categoria():
raise ValueError(f"Categoría '{self.categoria}' no es válida")

if self.gravedad and not self.is_valid_gravedad():
raise ValueError(f"Gravedad '{self.gravedad}' no es válida")

# Llamar al save del padre
super().save(commit=commit)

@classmethod
def create_tipo_falla(cls, nombre, categoria=None, descripcion=None,
gravedad=None, tiempo_estimado_resolucion=None):
"""
Crea un nuevo tipo de falla con validación.

Args:
nombre (str): Nombre del tipo de falla
categoria (str): Categoría opcional
descripcion (str): Descripción opcional
gravedad (str): Gravedad opcional
tiempo_estimado_resolucion (int): Tiempo en minutos opcional

Returns:
CatalogoTipoFalla: Instancia creada
"""
tipo_falla = cls(
nombre=nombre,
categoria=categoria,
descripcion=descripcion,
gravedad=gravedad,
tiempo_estimado_resolucion=tiempo_estimado_resolucion
)

tipo_falla.save()
return tipo_falla

@classmethod
def get_by_categoria(cls, categoria):
"""
Obtiene tipos de falla por categoría.

Args:
categoria (str): Categoría a filtrar

Returns:
list: Lista de tipos de falla de la categoría
"""
return cls.query.filter_by(categoria=categoria, deleted=False).all()

@classmethod
def get_by_gravedad(cls, gravedad):
"""
Obtiene tipos de falla por gravedad.

Args:
gravedad (str): Gravedad a filtrar

Returns:
list: Lista de tipos de falla con esa gravedad
"""
return cls.query.filter_by(gravedad=gravedad, deleted=False).all()

@classmethod
def get_with_fallas_count(cls):
"""
Obtiene todos los tipos de falla con el conteo de fallas asociadas.

Returns:
list: Lista de tipos de falla con conteo de fallas
"""
return db.session.query(
cls,
db.func.count(Falla.id).label('fallas_count')
).outerjoin(Falla).filter(
cls.deleted == False,
Falla.deleted == False
).group_by(cls.id).all()

@classmethod
def get_most_frequent_tipos(cls, limit=10):
"""
Obtiene los tipos de falla más frecuentes.

Args:
limit (int): Límite de resultados

Returns:
list: Lista de tipos ordenados por frecuencia
"""
return db.session.query(
cls,
db.func.count(Falla.id).label('fallas_count')
).join(Falla).filter(
cls.deleted == False,
Falla.deleted == False
).group_by(cls.id).order_by(
db.desc('fallas_count')
).limit(limit).all()

@classmethod
def get_categorias_disponibles(cls):
"""
Obtiene la lista de categorías disponibles.

Returns:
list: Lista de categorías únicas en el sistema
"""
result = db.session.query(cls.categoria).filter(
cls.deleted == False,
cls.categoria.isnot(None)
).distinct().all()
return [row[0] for row in result]

@classmethod
def get_gravedades_disponibles(cls):
"""
Obtiene la lista de gravedades disponibles.

Returns:
list: Lista de gravedades únicas en el sistema
"""
result = db.session.query(cls.gravedad).filter(
cls.deleted == False,
cls.gravedad.isnot(None)
).distinct().all()
return [row[0] for row in result]

@classmethod
def search_by_nombre(cls, search_term):
"""
Busca tipos de falla por nombre.

Args:
search_term (str): Término de búsqueda

Returns:
list: Lista de tipos de falla que coinciden
"""
return cls.query.filter(
cls.deleted == False,
cls.nombre.ilike(f"%{search_term}%")
).all()

@classmethod
def get_estadisticas_categoria(cls):
"""
Obtiene estadísticas por categoría.

Returns:
dict: Estadísticas por categoría
"""
from sqlalchemy import func

stats = db.session.query(
cls.categoria,
func.count(cls.id).label('total_tipos'),
func.avg(cls.tiempo_estimado_resolucion).label('tiempo_promedio')
).filter(
cls.deleted == False,
cls.categoria.isnot(None)
).group_by(cls.categoria).all()

return {row.categoria: {
'total_tipos': row.total_tipos,
'tiempo_promedio': row.tiempo_promedio or 0
} for row in stats}


# Crear índices para optimizar consultas
Index('idx_catalogo_tipo_falla_nombre', CatalogoTipoFalla.nombre)
Index('idx_catalogo_tipo_falla_categoria', CatalogoTipoFalla.categoria)
Index('idx_catalogo_tipo_falla_gravedad', CatalogoTipoFalla.gravedad)
Index('idx_catalogo_tipo_falla_composite', CatalogoTipoFalla.categoria, CatalogoTipoFalla.gravedad)
