# Sistema de Gestión de Cámaras UFRO

Sistema web completo para la gestión de cámaras de seguridad del Campus de la Universidad de la Frontera (UFRO).

## 🎯 Características Principales

- ✅ **Dashboard Interactivo**: Estadísticas en tiempo real con gráficos
- ✅ **Gestión de Equipos**: Cámaras (474), Gabinetes, Switches, UPS, NVR/DVR, Fuentes de poder
- ✅ **Sistema de Fallas**: Workflow completo con validación anti-duplicados
- ✅ **Mantenimientos**: Preventivos, correctivos y predictivos
- ✅ **Mapas de Red**: Topología con Mermaid.js y geolocalización con Leaflet.js
- ✅ **Reportes Avanzados**: Exportación Excel/PNG e impresión optimizada
- ✅ **Autenticación RBAC**: 6 roles de usuario (admin, supervisor, técnico, visualizador)
- ✅ **Responsive Design**: Bootstrap 5 optimizado para móviles

## 🏗️ Arquitectura

- **Backend**: Flask (Python) + SQLAlchemy ORM
- **Base de Datos**: PostgreSQL (producción) / SQLite (desarrollo)
- **Frontend**: Bootstrap 5 + Chart.js + Jinja2 Templates
- **Mapas**: Mermaid.js + Leaflet.js
- **Deploy**: Railway (autodeploy desde GitHub)

## 📊 Datos del Sistema

- **Total Cámaras**: 474 cámaras distribuidas en campus
- **Campus**: Andrés Bello (principal), Pucón, Angol, Medicina
- **Equipos**: 6 categorías de equipos de infraestructura
- **Fallas**: Sistema de workflow con 6 estados
- **Mantenimientos**: Registro completo de intervenciones

## 🔧 Instalación Local

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/sistema-camaras-ufro.git
cd sistema-camaras-ufro

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Inicializar base de datos
python init_db.py

# Ejecutar aplicación
python app.py
```

## 🚀 Deploy en Railway

1. Conectar repositorio a Railway
2. Configurar variables de entorno:
   - `DATABASE_URL`: URL de PostgreSQL
   - `SECRET_KEY`: Clave secreta para producción
3. Railway hará auto-deploy desde rama `main`

## 🔐 Credenciales por Defecto

- **Usuario**: charles@ufro.cl
- **Contraseña**: ufro2025
- **Rol**: Superadministrador

## 📝 Estructura del Proyecto

```
sistema-camaras-ufro/
├── app.py                  # Aplicación Flask principal
├── models.py              # Modelos SQLAlchemy
├── migrate_data.py        # Script de migración Excel
├── requirements.txt       # Dependencias Python
├── templates/             # Templates Jinja2
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── camaras/
│   ├── fallas/
│   ├── mantenimientos/
│   └── informes/
├── static/                # Assets estáticos
│   ├── css/
│   ├── js/
│   └── images/
└── planillas/             # Archivos Excel de datos
```

## 🏢 Funcionalidades por Módulo

### Dashboard
- Estadísticas generales en tiempo real
- Gráficos de estado de equipos
- Alertas y notificaciones
- Resumen de fallas activas

### Gestión de Cámaras
- CRUD completo de 474 cámaras
- Información técnica detallada
- Historial de fallas por cámara
- Estado operativo en tiempo real

### Sistema de Fallas
- **Estados**: Pendiente → Asignada → En Proceso → Reparada → Cerrada → Cancelada
- **Validación Anti-Duplicados**: Previene fallas duplicadas
- **Asignación de Técnicos**: Sistema de roles y permisos
- **Seguimiento Completo**: Fecha, hora, técnico, solución aplicada

### Mantenimientos
- **Preventivo**: Mantenimientos programados
- **Correctivo**: Reparaciones de fallas
- **Predictivo**: Análisis de tendencias
- **Costos**: Registro completo de gastos

### Mapas y Reportes
- **Topología de Red**: Visualización jerárquica con Mermaid.js
- **Geolocalización**: Mapas interactivos con Leaflet.js
- **Informes**: Exportación Excel y PNG
- **Impresión**: CSS optimizado para impresora

## 👥 Sistema de Usuarios RBAC

- **Superadministrador**: Acceso completo al sistema
- **Administrador**: Gestión de usuarios y configuración
- **Supervisor**: Supervisión y reportes
- **Técnico**: Mantenimientos y reparaciones
- **Visualizador**: Solo lectura
- **Invitado**: Acceso limitado

## 🔒 Seguridad

- Autenticación Flask-Login
- Hash de contraseñas con Werkzeug
- Validación de sesiones
- Protección CSRF
- Sanitización de inputs

## 📱 Responsive Design

- Bootstrap 5 framework
- Mobile-first approach
- Optimización para tablets y móviles
- Iconografía FontAwesome
- Temas personalizados

## 🧪 Testing

```bash
# Ejecutar tests (cuando estén implementados)
python -m pytest tests/

# Verificar cobertura
python -m pytest --cov=app tests/
```

## 📈 Performance

- SQLAlchemy ORM optimizado
- Paginación de resultados
- Cache de consultas frecuentes
- Lazy loading de relaciones
- Minificación de assets

## 🔄 Migración de Datos

El sistema incluye herramientas para migrar datos desde Excel:

```bash
# Ejecutar migración completa
python migrate_data.py

# Migración específica por módulo
python migrate_data.py --module=camaras
python migrate_data.py --module=fallas
```

## 📚 Documentación

- README.md (este archivo)
- Documentación de API en `/docs/api/`
- Guías de usuario en `/docs/user/`
- Documentación técnica en `/docs/tech/`

## 🤝 Contribuir

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

- **Email**: soporte@ufro.cl
- **Issues**: GitHub Issues
- **Documentación**: `/docs/`

## 🏆 Estado del Proyecto

- ✅ **Desarrollo**: Completado
- ✅ **Testing**: En progreso  
- ✅ **Deploy**: Railway configurado
- ✅ **Documentación**: Parcialmente completa

---

**Sistema de Gestión de Cámaras UFRO** - Desarrollado para la Universidad de la Frontera