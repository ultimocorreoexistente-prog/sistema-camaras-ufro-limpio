# Sistema de Gestión de Cámaras UFRO

Sistema web completo para la gestión de infraestructura tecnológica y cámaras de seguridad de la Universidad de La Frontera (UFRO).

## Arquitectura del Proyecto

```
sistema-camaras-ufro-completo/
app.py # Aplicación principal Flask
config.py # Configuraciones del sistema
requirements.txt # Dependencias Python
.env.example # Variables de entorno de ejemplo
Procfile # Configuración para deployment en Railway
templates/ # Templates HTML con Jinja
base.html
dashboard.html
login.html
usuarios/
camaras/
geolocalizacion/
topologia/
fotografias/
fallas/
mantenimientos/
static/ # Archivos estáticos
css/style.css # Estilos principales
js/ # Scripts JavaScript
uploads/ # Archivos subidos
models/ # Modelos SQLAlchemy
__init__.py
base.py
usuario.py
camara.py
equipo.py
fotografia.py
routes/ # Rutas de la aplicación
__init__.py
usuarios.py
camaras.py
topologia.py
fotografias.py
services/ # Lógica de negocio
__init__.py
auth_service.py
foto_service.py
reporte_service.py
utils/ # Utilidades
__init__.py
helpers.py
validators.py
scripts/ # Scripts de migración y utilidad
migrations/ # Migraciones de base de datos
uploads/ # Directorio de archivos subidos
docs/ # Documentación
```

## Instalación y Configuración

### 1. Clonar y Configurar el Entorno

```bash
# Clonar el repositorio
git clone <repository-url>
cd sistema-camaras-ufro-completo

# Crear entorno virtual
python -m venv venv
source venv/bin/activate # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### . Configuración de Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=postgresql://usuario:password@host:puerto/database
FLASK_ENV=development
```

### 3. Configuración de Base de Datos

```bash
# Para desarrollo (SQLite)
export DATABASE_URL='sqlite:///sistema_camaras.db'

# Para producción (Railway PostgreSQL)
export DATABASE_URL='postgresql://usuario:password@host:puerto/database'
```

## Uso de la Aplicación

### Desarrollo Local

```bash
# Ejecutar la aplicación
python app.py

# La aplicación estará disponible en http://localhost:8000
```

### Deployment en Railway

1. Conectar el repositorio a Railway
. Configurar variables de entorno en Railway
3. Railway detectará automáticamente el Procfile
4. La aplicación se desplegará automáticamente

## Modelos de Datos

### Usuario
- Gestión de usuarios con sistema RBAC
- Roles: Administrador, Supervisor, Operador, Visitante
- Sistema de autenticación seguro

### Cámara
- Gestión completa de cámaras de seguridad
- Estados: Online, Offline, Fallando, Mantenimiento
- Geolocalización y especificaciones técnicas

### Equipo de Red
- Gestión de NVR, DVR, Switches, UPS
- Estados de equipos y conexiones
- Topología de red

### Fallas y Mantenimientos
- Registro y seguimiento de fallas
- Programación de mantenimientos
- Historial de intervenciones

### Fotografías
- Gestión de evidencias fotográficas
- Metadatos de imágenes
- Asociación con fallas y mantenimientos

## Funcionalidades Principales

### Dashboard
- Resumen ejecutivo del estado del sistema
- Gráficos de estados de equipos
- Alertas y notificaciones

### Gestión de Usuarios
- CRUD completo de usuarios
- Sistema de roles y permisos
- Auditoría de actividades

### Gestión de Cámaras
- Registro de cámaras con ubicación
- Estados en tiempo real
- Historial de fallas

### Topología de Red
- Visualización de diagramas de red
- Conexiones entre equipos
- Mapeo geográfico

### Fotografías
- Subida y gestión de imágenes
- Organización por categorías
- Visualización y descarga

### Reportes
- Informes de estado
- Estadísticas de mantenimiento
- Exportación de datos

## Seguridad

- Autenticación con Flask-Login
- Protección CSRF
- Validación de datos de entrada
- Hash seguro de contraseñas
- Roles y permisos granulares

## Responsive Design

- Compatible con dispositivos móviles
- Interfaz adaptable
- Navegación optimizada para touch

## Testing

```bash
# Ejecutar tests
python -m pytest tests/

# Verificar cobertura
python -m pytest --cov=. tests/
```

## Logs y Monitoreo

- Logs estructurados con Python logging
- Registro de actividades de usuario
- Monitoreo de base de datos
- Endpoints de diagnóstico

## Contribución

1. Fork del proyecto
. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.

## Soporte

Para soporte técnico o consultas:
<<<<<<< HEAD
- Email: soporte-tecnico@ufro.cl
=======
- Email: soporte-tecnico@ufrontera.cl
>>>>>>> e689c66cd1a8e8cd7d3b1f7c326cf31775409856
- Documentación: `/docs/`
- Issues: GitHub Issues

## Versionado

Este proyecto usa [Semantic Versioning](https://semver.org/) para el versionado.

## Agradecimientos

- Universidad de La Frontera (UFRO)
- Equipo de desarrollo
- Bibliotecas open source utilizadas

---

**Versión:** 1.0.0
**Fecha:** 04
**Estado:** Producción