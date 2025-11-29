"""
Modelo de equipo técnico para gestión de personal técnico.

Basado en la estructura extraída de Railway con 8 columnas:
id, nombre, apellido, especialidad, telefono, email, estado, fecha_ingreso

Incluye relaciones con fallas y mantenimientos.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.base import TimestampedModel
from models import db
import enum


class TecnicoStatus(enum.Enum):
    """Estados del personal técnico."""
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    DISPONIBLE = "disponible"
    OCUPADO = "ocupado"
    VACACIONES = "vacaciones"
    LICENCIA = "licencia"


class EquipoTecnico(db.Model, TimestampedModel):
    """
    Modelo para gestión del personal técnico del sistema.

    Basado en la estructura de Railway con 8 columnas principales.

    Attributes:
    id (int): ID único del técnico
    nombre (str): Nombre del técnico
    apellido (str): Apellido del técnico
    especialidad (str): Especialidad técnica
    telefono (str): Número de teléfono
    email (str): Correo electrónico
    estado (str): Estado actual del técnico
    fecha_ingreso (date): Fecha de ingreso al equipo
    """

    __tablename__ = 'equipo_tecnico'
    id = Column(Integer, primary_key=True, comment="ID único del técnico")

    # Campos principales basados en estructura Railway
    nombre = Column(String(100), nullable=False, index=True,
                    comment="Nombre del técnico")
    apellido = Column(String(100), nullable=False, index=True,
                      comment="Apellido del técnico")
    especialidad = Column(String(100), nullable=True,
                          comment="Especialidad técnica del técnico")
    telefono = Column(String(50), nullable=True,
                      comment="Número de teléfono")
    email = Column(String(100), nullable=True, index=True,
                   comment="Correo electrónico")
    estado = Column(String(50), nullable=True,
                    comment="Estado actual del técnico")
    fecha_ingreso = Column(Date, nullable=True,
                           comment="Fecha de ingreso al equipo")

    # Campos adicionales para funcionalidad extendida
    codigo_empleado = Column(String(50), nullable=True, unique=True,
                             comment="Código único de empleado")
    cargo = Column(String(100), nullable=True,
                   comment="Cargo o posición")
    departamento = Column(String(100), nullable=True,
                          comment="Departamento de trabajo")
    nivel_experiencia = Column(String(50), nullable=True,
                               comment="Nivel de experiencia")
    certificaciones = Column(db.JSON, nullable=True,
                             comment="Certificaciones técnicas en JSON")
    habilidades = Column(db.JSON, nullable=True,
                         comment="Habilidades técnicas en JSON")
    disponibilidad_horario = Column(db.JSON, nullable=True,
                                    comment="Horario de disponibilidad")
    ubicacion_asignada = Column(String(100), nullable=True,
                                comment="Ubicación de trabajo asignada")

    # Campos de contacto y comunicación
    telefono_emergencia = Column(String(50), nullable=True,
                                comment="Teléfono de emergencia")
    direccion = Column(String(300), nullable=True,
                        comment="Dirección de contacto")
    ciudad = Column(String(100), nullable=True,
                    comment="Ciudad de residencia")
    region = Column(String(100), nullable=True,
                    comment="Región de residencia")
    pais = Column(String(100), nullable=True,
                  comment="País de residencia")

    # Campos de información laboral
    fecha_nacimiento = Column(Date, nullable=True,
                              comment="Fecha de nacimiento")
    genero = Column(String(20), nullable=True,
                    comment="Género")
    estado_civil = Column(String(30), nullable=True,
                          comment="Estado civil")
    numero_legajo = Column(String(50), nullable=True, unique=True,
                           comment="Número de legajo")
    tipo_contrato = Column(String(30), nullable=True,
                           comment="Tipo de contrato laboral")
    supervisor_id = Column(Integer, ForeignKey('equipo_tecnico.id'), nullable=True,
                            comment="ID del supervisor directo")

    # Campos de métricas y evaluación
    evaluaciones_desempeno = Column(db.JSON, nullable=True,
                                    comment="Evaluaciones de desempeño")
    horas_trabajadas_mes = Column(Integer, default=0,
                                  comment="Horas trabajadas en el mes")
    promedio_tiempo_resolucion = Column(Integer, nullable=True,
                                        comment="Promedio de tiempo de resolución en horas")
    total_fallas_asignadas = Column(Integer, default=0,
                                    comment="Total de fallas asignadas")
    total_mantenimientos_asignados = Column(Integer, default=0,
                                            comment="Total de mantenimientos asignados")

    # Campos de competencias técnicas
    especialidades_secundarias = Column(db.JSON, nullable=True,
                                        comment="Especialidades secundarias")
    niveles_habilidad = Column(db.JSON, nullable=True,
                              comment="Niveles de habilidad por tecnología")
    idiomas = Column(db.JSON, nullable=True,
                     comment="Idiomas que habla")
    formacion_academica = Column(db.JSON, nullable=True,
                                 comment="Formación académica")
    cursos_completados = Column(db.JSON, nullable=True,
                                comment="Cursos y capacitaciones completadas")

    # Campos de seguimiento y control
    ultima_actividad = Column(DateTime, nullable=True,
                              comment="Fecha y hora de última actividad")
    dias_disponibles = Column(Integer, default=30,
                              comment="Días de vacaciones disponibles")
    dias_tomados = Column(Integer, default=0,
                          comment="Días de vacaciones tomados")

    # Relaciones
    supervisor = relationship("EquipoTecnico", remote_side=[id], back_populates="subordinados")
    subordinados = relationship("EquipoTecnico", back_populates="supervisor")

    # Relaciones con fallas
    fallas_asignadas = relationship("Falla", back_populates="tecnico_asignado_obj",
                                    foreign_keys="Falla.assigned_to",
                                    cascade="all, delete-orphan")

    # Relaciones con mantenimientos
    mantenimientos_asignados = relationship("Mantenimiento",
                                            back_populates="tecnico_asignado_obj",
                                            foreign_keys="Mantenimiento.technician_id",
                                            cascade="all, delete-orphan")

    # Relaciones con fotografías
    fotografias_subidas = relationship("Fotografia", back_populates="tecnico_responsable",
                                       foreign_keys="Fotografia.tecnico_responsable",
                                       cascade="all, delete-orphan")

    def __repr__(self):
        return f"<EquipoTecnico(id={self.id}, nombre='{self.nombre}', apellido='{self.apellido}', estado='{self.estado}')>"

    def get_nombre_completo(self):
        """Obtiene el nombre completo del técnico."""
        return f"{self.nombre} {self.apellido}"

    def get_iniciales(self):
        """Obtiene las iniciales del técnico."""
        return f"{self.nombre[0] if self.nombre else ''}{self.apellido[0] if self.apellido else ''}"

    def is_available(self):
        """Verifica si el técnico está disponible para asignaciones."""
        return self.estado in [TecnicoStatus.ACTIVO.value, TecnicoStatus.DISPONIBLE.value]

    def get_workload(self):
        """Obtiene la carga de trabajo actual del técnico."""
        fallas_activas = len([f for f in self.fallas_asignadas if f.estado in ['abierta', 'en_proceso']])
        mantenimientos_activos = len([m for m in self.mantenimientos_asignados if m.estado in ['programado', 'en_proceso']])

        return {
            'fallas_activas': fallas_activas,
            'mantenimientos_activos': mantenimientos_activos,
            'total_asignaciones': fallas_activas + mantenimientos_activos
        }

    def get_performance_metrics(self):
        """Obtiene métricas de desempeño del técnico."""
        total_fallas = len(self.fallas_asignadas)
        fallas_resueltas = len([f for f in self.fallas_asignadas if f.estado == 'resuelta'])

        total_mantenimientos = len(self.mantenimientos_asignados)
        mantenimientos_completados = len([m for m in self.mantenimientos_asignados if m.estado == 'completado'])

        tasa_resolucion_fallas = (fallas_resueltas / total_fallas * 100) if total_fallas > 0 else 0
        tasa_completado_mantenimientos = (mantenimientos_completados / total_mantenimientos * 100) if total_mantenimientos > 0 else 0

        return {
            'total_fallas': total_fallas,
            'fallas_resueltas': fallas_resueltas,
            'tasa_resolucion_fallas': round(tasa_resolucion_fallas, ),
            'total_mantenimientos': total_mantenimientos,
            'mantenimientos_completados': mantenimientos_completados,
            'tasa_completado_mantenimientos': round(tasa_completado_mantenimientos, ),
            'promedio_tiempo_resolucion': self.promedio_tiempo_resolucion
        }

    def assign_falla(self, falla_id):
        """Asigna una falla al técnico."""
        from models.falla import Falla
        falla = Falla.query.get(falla_id)
        if falla:
            falla.assigned_to = self.id
            falla.tecnico_asignado = str(self.id)
            falla.assigned_date = datetime.utcnow()
            falla.save()
            return True
        return False

    def assign_mantenimiento(self, mantenimiento_id):
        """Asigna un mantenimiento al técnico."""
        from models.mantenimiento import Mantenimiento
        mantenimiento = Mantenimiento.query.get(mantenimiento_id)
        if mantenimiento:
            mantenimiento.technician_id = self.id
            mantenimiento.tecnico_responsable = self.get_nombre_completo()
            mantenimiento.estado = 'en_proceso'
            mantenimiento.save()
            return True
        return False

    def activate(self):
        """Activa al técnico."""
        self.estado = TecnicoStatus.ACTIVO.value
        self.save()

    def deactivate(self):
        """Desactiva al técnico."""
        self.estado = TecnicoStatus.INACTIVO.value
        self.save()

    def set_available(self):
        """Marca al técnico como disponible."""
        self.estado = TecnicoStatus.DISPONIBLE.value
        self.save()

    def set_busy(self):
        """Marca al técnico como ocupado."""
        self.estado = TecnicoStatus.OCUPADO.value
        self.save()

    def update_last_activity(self):
        """Actualiza la fecha y hora de última actividad."""
        self.ultima_actividad = datetime.utcnow()
        self.save()

    def add_skill(self, skill, level=1):
        """Añade una habilidad al técnico."""
        if not self.habilidades:
            self.habilidades = {}
        self.habilidades[skill] = level
        self.save()

    def add_certification(self, certification, date_obtained=None):
        """Añade una certificación al técnico."""
        if not self.certificaciones:
            self.certificaciones = []
        cert_info = {
            'certification': certification,
            'date_obtained': date_obtained.isoformat() if date_obtained else None,
            'added_date': datetime.utcnow().isoformat()
        }
        self.certificaciones.append(cert_info)
        self.save()

    def get_specialties(self):
        """Obtiene todas las especialidades del técnico."""
        specialties = []
        if self.especialidad:
            specialties.append(self.especialidad)
        if self.especialidades_secundarias:
            specialties.extend(self.especialidades_secundarias)
        return specialties

    def has_skill(self, skill):
        """Verifica si el técnico tiene una habilidad específica."""
        if not self.habilidades:
            return False
        return skill in self.habilidades

    def get_skill_level(self, skill):
        """Obtiene el nivel de una habilidad específica."""
        if not self.habilidades:
            return 0
        return self.habilidades.get(skill, 0)

    def update_performance_metrics(self):
        """Actualiza las métricas de desempeño."""
        # Calcular métricas actuales
        fallas_activas = [f for f in self.fallas_asignadas if f.estado in ['abierta', 'en_proceso']]
        total_fallas_asignadas = len(self.fallas_asignadas)

        mantenimientos_activos = [m for m in self.mantenimientos_asignados if m.estado in ['programado', 'en_proceso']]
        total_mantenimientos_asignados = len(self.mantenimientos_asignados)

        # Actualizar campos
        self.total_fallas_asignadas = total_fallas_asignadas
        self.total_mantenimientos_asignados = total_mantenimientos_asignados

        # Calcular promedio de tiempo de resolución si hay datos
        if self.fallas_asignadas:
            tiempos_resolucion = []
            for falla in self.fallas_asignadas:
                if falla.actual_resolution_time:
                    tiempos_resolucion.append(falla.actual_resolution_time)
            if tiempos_resolucion:
                self.promedio_tiempo_resolucion = sum(tiempos_resolucion) / len(tiempos_resolucion)

        self.save()

    @classmethod
    def get_active_technicians(cls):
        """Obtiene todos los técnicos activos."""
        return cls.query.filter(
            cls.estado.in_([TecnicoStatus.ACTIVO.value, TecnicoStatus.DISPONIBLE.value]),
            cls.deleted == False
        ).all()

    @classmethod
    def get_available_technicians(cls):
        """Obtiene técnicos disponibles para asignaciones."""
        return cls.query.filter(
            cls.estado == TecnicoStatus.DISPONIBLE.value,
            cls.deleted == False
        ).all()

    @classmethod
    def get_by_specialty(cls, specialty):
        """Obtiene técnicos por especialidad."""
        return cls.query.filter(
            cls.especialidad.ilike(f'%{specialty}%'),
            cls.deleted == False
        ).all()

    @classmethod
    def get_by_workload(cls, max_assignments=5):
        """Obtiene técnicos con carga de trabajo baja."""
        technicians = cls.get_active_technicians()
        available_technicians = []

        for tech in technicians:
            workload = tech.get_workload()
            if workload['total_asignaciones'] < max_assignments:
                available_technicians.append(tech)

        return available_technicians

    @classmethod
    def get_with_low_performance(cls, min_completion_rate=70.0):
        """Obtiene técnicos con bajo rendimiento."""
        technicians = cls.get_active_technicians()
        low_performance = []

        for tech in technicians:
            metrics = tech.get_performance_metrics()
            if metrics['tasa_resolucion_fallas'] < min_completion_rate:
                low_performance.append(tech)

        return low_performance

    @classmethod
    def search(cls, query, specialty=None):
        """Busca técnicos por nombre, apellido o especialidad."""
        search_filter = (
            (cls.nombre.ilike(f'%{query}%')) |
            (cls.apellido.ilike(f'%{query}%')) |
            (cls.email.ilike(f'%{query}%'))
        )

        if specialty:
            search_filter = search_filter & (cls.especialidad.ilike(f'%{specialty}%'))

        return cls.query.filter(search_filter, cls.deleted == False).all()

    def to_dict(self):
        """
        Convierte el modelo a un diccionario incluyendo relaciones.

        Returns:
        dict: Diccionario con los atributos del modelo y relaciones
        """
        result = super().to_dict()

        # Añadir datos calculados
        result['nombre_completo'] = self.get_nombre_completo()
        result['iniciales'] = self.get_iniciales()
        result['is_available'] = self.is_available()
        result['workload'] = self.get_workload()
        result['performance_metrics'] = self.get_performance_metrics()
        result['specialties'] = self.get_specialties()

        # Añadir relaciones activas (solo IDs para evitar recursión)
        result['supervisor_id'] = self.supervisor_id
        result['subordinados_ids'] = [s.id for s in self.subordinados]
        result['fallas_asignadas_ids'] = [f.id for f in self.fallas_asignadas]
        result['mantenimientos_asignados_ids'] = [m.id for m in self.mantenimientos_asignados]

        return result