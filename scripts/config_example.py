# Configuración de ejemplo para migración de datos
# Copiar a config.py y modificar valores según entorno

# Base de datos PostgreSQL
DATABASE_CONFIG = {
'host': 'localhost',
'database': 'camaras_ufro',
'user': 'postgres',
'password': 'tu_password_aqui',
'port': 543
}

# Directorios de archivos
DIRECTORIOS = {
'entrada': '/workspace/user_input_files/planillas-web',
'salida_limpios': '/workspace/datos_limpios',
'logs': '/workspace/logs',
'backups': '/workspace/backups'
}

# Archivos específicos a migrar
ARCHIVOS_MIGRACION = {
'camaras': 'Listadecámaras_modificada.xlsx',
'nvr': 'NVR_DVR.xlsx',
'switches': 'Switches.xlsx',
'fallas': 'Fallas_Actualizada.xlsx',
'fallas_reales': 'Ejemplos_Fallas_Reales_corregido_051019_00501.xlsx',
'ubicaciones': 'Ubicaciones.xlsx',
'ups': 'UPS.xlsx',
'fuentes': 'Fuentes_Poder.xlsx',
'gabinetes': 'Gabinetes.xlsx',
'mantenimientos': 'Mantenimientos.xlsx',
'equipos_tecnicos': 'Equipos_Tecnicos.xlsx',
'catalogo_fallas': 'Catalogo_Tipos_Fallas.xlsx',
'puertos_switch': 'Puertos_Switch.xlsx'
}

# Configuración de limpieza
LIMPIEZA_CONFIG = {
'normalizar_estados': True,
'validar_ips': True,
'parsear_fechas': True,
'eliminar_duplicados': True,
'generar_json': True
}

# Configuración de validación
VALIDACION_CONFIG = {
'validar_claves_primarias': True,
'validar_ips_unicas': True,
'validar_relaciones_fk': True,
'validar_completitud': True,
'generar_estadisticas': True
}

# Configuración de pruebas
PRUEBAS_CONFIG = {
'usar_db_test': False,
'crear_datos_test': True,
'limpiar_despues': True
}