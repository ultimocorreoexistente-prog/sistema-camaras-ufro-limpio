"""
Scripts de migración del Sistema de Cámaras UFRO.
"""

from .init_database import init_database, backup_database

__all__ = ['init_database', 'backup_database']