"""
Migraciones de base de datos para el Sistema de Cámaras UFRO.
"""

from . import create_initial_tables, create_indexes

__all__ = ['create_initial_tables', 'create_indexes']