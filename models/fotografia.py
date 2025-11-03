"""
Modelo de fotografías y documentación visual.

Incluye gestión de imágenes asociadas a equipos, fallas y mantenimientos.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.base import BaseModel
from models import db, PhotoStatus, PhotoType
import enum


class PhotoFormat(enum.Enum):
    """Formatos de imagen soportados."""
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    WEBP = "webp"


class CameraOrientation(enum.Enum):
    """Orientación de la cámara."""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    SQUARE = "square"


class Fotografia(BaseModel, db.Model):
    """
    Modelo de fotografías para documentación.
    
    Attributes:
        filename (str): Nombre del archivo
        original_filename (str): Nombre original del archivo
        file_path (str): Ruta física del archivo
        file_size (int): Tamaño del archivo en bytes
        mime_type (str): Tipo MIME del archivo
        photo_format (str): Formato de la imagen
        width (int): Ancho en píxeles
        height (int): Alto en píxeles
        orientation (str): Orientación de la imagen
        dpi_x (int): DPI horizontal
        dpi_y (int): DPI vertical
        photo_type (str): Tipo de fotografía
        status (str): Estado de la fotografía
        title (str): Título descriptivo
        description (str): Descripción detallada
        tags (str): Etiquetas separadas por comas
        equipment_id (int): ID del equipo relacionado
        equipment_type (str): Tipo del equipo
        camara_id (int): ID de la cámara origen
        nvr_id (int): ID del NVR que capturó la imagen
        switch_id (int): ID del switch relacionado
        ups_id (int): ID del UPS relacionado
        fuente_poder_id (int): ID de la fuente de poder relacionada
        gabinete_id (int): ID del gabinete relacionado
        ubicacion_id (int): ID de la ubicación donde se tomó
        falla_id (int): ID de la falla documentada
        mantenimiento_id (int): ID del mantenimiento documentado
        uploaded_by (int): ID del usuario que subió la imagen
        capture_date (datetime): Fecha y hora de captura
        upload_date (datetime): Fecha y hora de subida
        processed_date (datetime): Fecha y hora de procesamiento
        thumbnail_path (str): Ruta de la miniatura
        preview_path (str): Ruta de la vista previa
        full_size_path (str): Ruta del tamaño completo
        web_optimized_path (str): Ruta de la versión optimizada para web
        compression_quality (float): Calidad de compresión (0-100)
        exif_data (str): Datos EXIF en formato JSON
        gps_coordinates (str): Coordenadas GPS en formato JSON
        color_profile (str): Perfil de color
        white_balance (str): Balance de blancos
        exposure_time (str): Tiempo de exposición
        aperture (str): Apertura
        iso (int): Valor ISO
        flash (bool): Si el flash estuvo activado
        focal_length (str): Longitud focal
        digital_zoom (float): Zoom digital
        original_camera (str): Cámara original utilizada
        software_used (str): Software utilizado para procesamiento
        color_space (str): Espacio de color
        bits_per_channel (int): Bits por canal
        channels (int): Número de canales de color
        histogram (str): Histograma de la imagen
        average_brightness (float): Brillo promedio
        contrast_level (float): Nivel de contraste
        sharpness (float): Nivel de nitidez
        noise_level (float): Nivel de ruido
        faces_detected (int): Número de caras detectadas
        text_ocr (str): Texto extraído por OCR
        quality_score (float): Puntaje de calidad automático (0-100)
        security_classification (str): Clasificación de seguridad
        privacy_filtered (bool): Si se aplicó filtro de privacidad
        copyright_info (str): Información de derechos de autor
        license_type (str): Tipo de licencia
        retention_period (int): Período de retención en días
        archive_date (datetime): Fecha de archivo
        public_url (str): URL pública para acceso
        access_count (int): Número de accesos
        download_count (int): Número de descargas
        last_accessed (datetime): Última fecha de acceso
        is_featured (bool): Si está marcada como destacada
        sort_order (int): Orden de clasificación
        parent_photo_id (int): ID de foto padre (para versiones/ediciones)
        related_photos (str): IDs de fotos relacionadas
        processing_log (str): Log de procesamiento
        approval_date (datetime): Fecha de aprobación
        approved_by (int): ID de quien aprobó
        rejection_reason (str): Razón de rechazo
        notes (str): Notas adicionales
    """
    
    __tablename__ = 'fotografias'
    
    # Información básica del archivo
    filename = Column(String(255), nullable=False,
                     comment="Nombre del archivo")
    original_filename = Column(String(255), nullable=True,
                              comment="Nombre original del archivo")
    file_path = Column(String(500), nullable=False,
                      comment="Ruta física del archivo")
    file_size = Column(Integer, nullable=True,
                      comment="Tamaño del archivo en bytes")
    mime_type = Column(String(100), nullable=True,
                      comment="Tipo MIME del archivo")
    
    # Propiedades de la imagen
    photo_format = Column(Enum(PhotoFormat), nullable=True,
                         comment="Formato de la imagen")
    width = Column(Integer, nullable=True,
                  comment="Ancho en píxeles")
    height = Column(Integer, nullable=True,
                   comment="Alto en píxeles")
    orientation = Column(Enum(CameraOrientation), nullable=True,
                        comment="Orientación de la imagen")
    dpi_x = Column(Integer, nullable=True,
                  comment="DPI horizontal")
    dpi_y = Column(Integer, nullable=True,
                  comment="DPI vertical")
    
    # Clasificación
    photo_type = Column(Enum(PhotoType), nullable=False,
                       comment="Tipo de fotografía")
    status = Column(String(20), nullable=False, default=PhotoStatus.PROCESANDO,
                   comment="Estado de la fotografía")
    title = Column(String(200), nullable=True,
                  comment="Título descriptivo")
    description = Column(Text, nullable=True,
                        comment="Descripción detallada")
    tags = Column(Text, nullable=True,
                 comment="Etiquetas separadas por comas")
    
    # Relaciones con otros modelos
    equipment_id = Column(Integer, nullable=True,
                         comment="ID del equipo relacionado")
    equipment_type = Column(String(30), nullable=True,
                           comment="Tipo del equipo")
    camara_id = Column(Integer, ForeignKey('camaras.id'), nullable=True,
                      comment="ID de la cámara origen")
    nvr_id = Column(Integer, ForeignKey('nvrs.id'), nullable=True,
                   comment="ID del NVR que capturó la imagen")
    switch_id = Column(Integer, ForeignKey('switches.id'), nullable=True,
                      comment="ID del switch relacionado")
    ups_id = Column(Integer, ForeignKey('ups.id'), nullable=True,
                   comment="ID del UPS relacionado")
    fuente_poder_id = Column(Integer, ForeignKey('fuentes_poder.id'), nullable=True,
                            comment="ID de la fuente de poder relacionada")
    gabinete_id = Column(Integer, ForeignKey('gabinetes.id'), nullable=True,
                        comment="ID del gabinete relacionado")
    ubicacion_id = Column(Integer, ForeignKey('ubicaciones.id'), nullable=True,
                         comment="ID de la ubicación donde se tomó")
    falla_id = Column(Integer, ForeignKey('fallas.id'), nullable=True,
                     comment="ID de la falla documentada")
    mantenimiento_id = Column(Integer, ForeignKey('mantenimientos.id'), nullable=True,
                             comment="ID del mantenimiento documentado")
    
    # Usuario y fechas
    uploaded_by = Column(Integer, ForeignKey('usuarios.id'), nullable=False,
                        comment="ID del usuario que subió la imagen")
    capture_date = Column(DateTime, nullable=True,
                         comment="Fecha y hora de captura")
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False,
                        comment="Fecha y hora de subida")
    processed_date = Column(DateTime, nullable=True,
                           comment="Fecha y hora de procesamiento")
    
    # Versiones de archivo
    thumbnail_path = Column(String(500), nullable=True,
                          comment="Ruta de la miniatura")
    preview_path = Column(String(500), nullable=True,
                         comment="Ruta de la vista previa")
    full_size_path = Column(String(500), nullable=True,
                           comment="Ruta del tamaño completo")
    web_optimized_path = Column(String(500), nullable=True,
                               comment="Ruta de la versión optimizada para web")
    
    # Procesamiento
    compression_quality = Column(Float, nullable=True,
                                comment="Calidad de compresión (0-100)")
    exif_data = Column(Text, nullable=True,
                      comment="Datos EXIF en formato JSON")
    gps_coordinates = Column(Text, nullable=True,
                           comment="Coordenadas GPS en formato JSON")
    
    # Propiedades técnicas
    color_profile = Column(String(50), nullable=True,
                          comment="Perfil de color")
    white_balance = Column(String(30), nullable=True,
                          comment="Balance de blancos")
    exposure_time = Column(String(20), nullable=True,
                          comment="Tiempo de exposición")
    aperture = Column(String(20), nullable=True,
                     comment="Apertura")
    iso = Column(Integer, nullable=True,
                comment="Valor ISO")
    flash = Column(Boolean, nullable=True,
                  comment="Si el flash estuvo activado")
    focal_length = Column(String(20), nullable=True,
                         comment="Longitud focal")
    digital_zoom = Column(Float, nullable=True,
                         comment="Zoom digital")
    original_camera = Column(String(100), nullable=True,
                           comment="Cámara original utilizada")
    software_used = Column(String(100), nullable=True,
                          comment="Software utilizado para procesamiento")
    
    # Análisis de imagen
    color_space = Column(String(30), nullable=True,
                        comment="Espacio de color")
    bits_per_channel = Column(Integer, nullable=True,
                             comment="Bits por canal")
    channels = Column(Integer, nullable=True,
                     comment="Número de canales de color")
    histogram = Column(Text, nullable=True,
                      comment="Histograma de la imagen")
    average_brightness = Column(Float, nullable=True,
                               comment="Brillo promedio")
    contrast_level = Column(Float, nullable=True,
                           comment="Nivel de contraste")
    sharpness = Column(Float, nullable=True,
                      comment="Nivel de nitidez")
    noise_level = Column(Float, nullable=True,
                       comment="Nivel de ruido")
    
    # Detección y análisis automático
    faces_detected = Column(Integer, default=0, nullable=False,
                           comment="Número de caras detectadas")
    text_ocr = Column(Text, nullable=True,
                     comment="Texto extraído por OCR")
    quality_score = Column(Float, default=0.0, nullable=False,
                          comment="Puntaje de calidad automático (0-100)")
    
    # Seguridad y privacidad
    security_classification = Column(String(30), nullable=True,
                                    comment="Clasificación de seguridad")
    privacy_filtered = Column(Boolean, default=False, nullable=False,
                             comment="Si se aplicó filtro de privacidad")
    copyright_info = Column(Text, nullable=True,
                           comment="Información de derechos de autor")
    license_type = Column(String(50), nullable=True,
                         comment="Tipo de licencia")
    
    # Retención y archivo
    retention_period = Column(Integer, nullable=True,
                             comment="Período de retención en días")
    archive_date = Column(DateTime, nullable=True,
                         comment="Fecha de archivo")
    
    # Acceso y URLs
    public_url = Column(String(500), nullable=True,
                       comment="URL pública para acceso")
    access_count = Column(Integer, default=0, nullable=False,
                         comment="Número de accesos")
    download_count = Column(Integer, default=0, nullable=False,
                           comment="Número de descargas")
    last_accessed = Column(DateTime, nullable=True,
                          comment="Última fecha de acceso")
    
    # Organización
    is_featured = Column(Boolean, default=False, nullable=False,
                        comment="Si está marcada como destacada")
    sort_order = Column(Integer, default=0, nullable=False,
                       comment="Orden de clasificación")
    
    # Relaciones
    parent_photo_id = Column(Integer, ForeignKey('fotografias.id'), nullable=True,
                            comment="ID de foto padre (para versiones/ediciones)")
    related_photos = Column(Text, nullable=True,
                           comment="IDs de fotos relacionadas")
    
    # Procesamiento y logs
    processing_log = Column(Text, nullable=True,
                           comment="Log de procesamiento")
    approval_date = Column(DateTime, nullable=True,
                          comment="Fecha de aprobación")
    approved_by = Column(Integer, ForeignKey('usuarios.id'), nullable=True,
                        comment="ID de quien aprobó")
    rejection_reason = Column(Text, nullable=True,
                             comment="Razón de rechazo")
    notes = Column(Text, nullable=True,
                  comment="Notas adicionales")
    
    # Relaciones
    created_by_user = relationship("Usuario", foreign_keys=[created_by], back_populates="created_fotografias")
    uploader = relationship("Usuario", foreign_keys=[uploaded_by])
    approver = relationship("Usuario", foreign_keys=[approved_by])
    
    # Relaciones con otros modelos
    ubicacion = relationship("Ubicacion", back_populates="fotografias")
    camara = relationship("Camara", back_populates="fotografias")
    nvr = relationship("NVR", back_populates="fotografias")
    switch = relationship("Switch", back_populates="fotografias")
    ups = relationship("UPS", back_populates="fotografias")
    fuente_poder = relationship("FuentePoder", back_populates="fotografias")
    gabinete = relationship("Gabinete", back_populates="fotografias")
    falla = relationship("Falla", back_populates="fotografias")
    mantenimiento = relationship("Mantenimiento", back_populates="fotografias")
    
    # Autorreferencia para versiones relacionadas
    parent_photo = relationship("Fotografia", remote_side=[id], backref="versions")
    
    def __repr__(self):
        return f"<Fotografia(filename='{self.filename}', type='{self.photo_type.value}', status='{self.status}')>"
    
    def get_aspect_ratio(self):
        """
        Calcula la relación de aspecto de la imagen.
        
        Returns:
            float: Relación de aspecto o None
        """
        if not self.width or not self.height or self.height == 0:
            return None
        return round(self.width / self.height, 2)
    
    def get_file_size_mb(self):
        """
        Obtiene el tamaño del archivo en MB.
        
        Returns:
            float: Tamaño en MB
        """
        if not self.file_size:
            return None
        return round(self.file_size / (1024 * 1024), 2)
    
    def get_dimensions_string(self):
 """
        Obtiene las dimensiones como string.
        
        Returns:
            str: Dimensiones en formato "W x H"
        """
        if not self.width or not self.height:
            return None
        return f"{self.width} x {self.height}"
    
    def increment_access_count(self):
        """
        Incrementa el contador de accesos.
        """
        self.access_count += 1
        self.last_accessed = datetime.utcnow()
        self.save()
    
    def increment_download_count(self):
        """
        Incrementa el contador de descargas.
        """
        self.download_count += 1
        self.save()
    
    def approve_photo(self, approver_id, notes=None):
        """
        Aprueba la fotografía.
        
        Args:
            approver_id (int): ID del usuario que aprueba
            notes (str): Notas opcionales
            
        Returns:
            bool: True si se aprobó exitosamente
        """
        self.status = PhotoStatus.APROBADO
        self.approved_by = approver_id
        self.approval_date = datetime.utcnow()
        
        if notes:
            self.notes = f"Aprobada: {notes}"
        
        self.save()
        return True
    
    def reject_photo(self, reason):
        """
        Rechaza la fotografía.
        
        Args:
            reason (str): Razón del rechazo
            
        Returns:
            bool: True si se rechazó exitosamente
        """
        self.status = PhotoStatus.RECHAZADO
        self.rejection_reason = reason
        self.save()
        return True
    
    def get_gps_coordinates_dict(self):
        """
        Obtiene las coordenadas GPS como diccionario.
        
        Returns:
            dict: Coordenadas GPS o None
        """
        if not self.gps_coordinates:
            return None
        
        try:
            import json
            return json.loads(self.gps_coordinates)
        except:
            return None
    
    def set_gps_coordinates(self, latitude, longitude, altitude=None):
        """
        Establece las coordenadas GPS.
        
        Args:
            latitude (float): Latitud
            longitude (float): Longitud
            altitude (float): Altitud opcional
        """
        import json
        
        coords = {
            'latitude': latitude,
            'longitude': longitude
        }
        
        if altitude is not None:
            coords['altitude'] = altitude
        
        self.gps_coordinates = json.dumps(coords)
        self.save()
    
    def get_exif_data_dict(self):
        """
        Obtiene los datos EXIF como diccionario.
        
        Returns:
            dict: Datos EXIF o None
        """
        if not self.exif_data:
            return None
        
        try:
            import json
            return json.loads(self.exif_data)
        except:
            return None
    
    def add_tag(self, tag):
        """
        Agrega una etiqueta a la fotografía.
        
        Args:
            tag (str): Etiqueta a agregar
        """
        if not self.tags:
            self.tags = tag
        elif tag not in self.tags.split(','):
            self.tags += f", {tag}"
        
        self.save()
    
    def remove_tag(self, tag):
        """
        Remueve una etiqueta de la fotografía.
        
        Args:
            tag (str): Etiqueta a remover
        """
        if not self.tags:
            return
        
        tags_list = [t.strip() for t in self.tags.split(',')]
        if tag in tags_list:
            tags_list.remove(tag)
            self.tags = ', '.join(tags_list)
            self.save()
    
    def get_tags_list(self):
        """
        Obtiene las etiquetas como lista.
        
        Returns:
            list: Lista de etiquetas
        """
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',')]
    
    def is_archived(self):
        """
        Verifica si la fotografía está archivada.
        
        Returns:
            bool: True si está archivada
        """
        return self.archive_date is not None
    
    def archive_photo(self):
        """
        Archiva la fotografía.
        
        Returns:
            bool: True si se archivó exitosamente
        """
        self.archive_date = datetime.utcnow()
        self.save()
        return True
    
    def is_retention_expired(self):
        """
        Verifica si el período de retención ha expirado.
        
        Returns:
            bool: True si ha expirado
        """
        if not self.retention_period or not self.upload_date:
            return False
        
        expiration_date = self.upload_date + timedelta(days=self.retention_period)
        return datetime.utcnow() > expiration_date
    
    def get_related_photos_list(self):
        """
        Obtiene las fotos relacionadas como lista de IDs.
        
        Returns:
            list: Lista de IDs de fotos relacionadas
        """
        if not self.related_photos:
            return []
        
        try:
            return [int(id.strip()) for id in self.related_photos.split(',')]
        except:
            return []
    
    def add_related_photo(self, photo_id):
        """
        Agrega una foto relacionada.
        
        Args:
            photo_id (int): ID de la foto relacionada
        """
        if not self.related_photos:
            self.related_photos = str(photo_id)
        else:
            related_ids = self.get_related_photos_list()
            if photo_id not in related_ids:
                related_ids.append(photo_id)
                self.related_photos = ', '.join(map(str, related_ids))
        
        self.save()
    
    def remove_related_photo(self, photo_id):
        """
        Remueve una foto relacionada.
        
        Args:
            photo_id (int): ID de la foto a remover
        """
        related_ids = self.get_related_photos_list()
        if photo_id in related_ids:
            related_ids.remove(photo_id)
            self.related_photos = ', '.join(map(str, related_ids))
            self.save()
    
    def get_quality_rating(self):
        """
        Obtiene la calificación de calidad.
        
        Returns:
            str: Calificación de calidad
        """
        score = self.quality_score or 0
        
        if score >= 90:
            return "Excelente"
        elif score >= 75:
            return "Buena"
        elif score >= 60:
            return "Regular"
        elif score >= 40:
            return "Pobre"
        else:
            return "Muy pobre"
    
    def is_ready_for_use(self):
        """
        Verifica si la fotografía está lista para usar.
        
        Returns:
            bool: True si está lista
        """
        return self.status == PhotoStatus.APROBADO and not self.is_archived()
    
    @classmethod
    def get_by_equipment(cls, equipment_id, equipment_type):
        """
        Obtiene fotografías de un equipo específico.
        
        Args:
            equipment_id (int): ID del equipo
            equipment_type (str): Tipo del equipo
            
        Returns:
            list: Lista de fotografías del equipo
        """
        return cls.query.filter_by(
            equipment_id=equipment_id,
            equipment_type=equipment_type,
            deleted=False
        ).all()
    
    @classmethod
    def get_by_type(cls, photo_type):
        """
        Obtiene fotografías de un tipo específico.
        
        Args:
            photo_type (PhotoType): Tipo de fotografía
            
        Returns:
            list: Lista de fotografías del tipo especificado
        """
        return cls.query.filter_by(photo_type=photo_type, deleted=False).all()
    
    @classmethod
    def get_by_status(cls, status):
        """
        Obtiene fotografías por estado.
        
        Args:
            status (PhotoStatus): Estado de la fotografía
            
        Returns:
            list: Lista de fotografías del estado especificado
        """
        return cls.query.filter_by(status=status, deleted=False).all()
    
    @classmethod
    def get_by_uploader(cls, uploader_id):
        """
        Obtiene fotografías subidas por un usuario específico.
        
        Args:
            uploader_id (int): ID del usuario
            
        Returns:
            list: Lista de fotografías del usuario
        """
        return cls.query.filter_by(uploaded_by=uploader_id, deleted=False).all()
    
    @classmethod
    def get_expired_retention(cls):
        """
        Obtiene fotografías que han expirado su retención.
        
        Returns:
            list: Lista de fotografías con retención expirada
        """
        fotos = cls.query.filter(
            cls.retention_period.isnot(None),
            cls.upload_date.isnot(None),
            cls.deleted == False
        ).all()
        
        expired = []
        for foto in fotos:
            if foto.is_retention_expired():
                expired.append(foto)
        
        return expired
    
    @classmethod
    def get_featured_photos(cls):
        """
        Obtiene las fotografías destacadas.
        
        Returns:
            list: Lista de fotografías destacadas
        """
        return cls.query.filter_by(
            is_featured=True,
            deleted=False,
            archive_date=None
        ).all()


class FotografiaMetadata(BaseModel, db.Model):
    """
    Metadatos adicionales para fotografías.
    
    Attributes:
        fotografia_id (int): ID de la fotografía
        metadata_key (str): Clave del metadato
        metadata_value (str): Valor del metadato
        data_type (str): Tipo de dato
        is_public (bool): Si es público
    """
    
    __tablename__ = 'fotografia_metadata'
    
    fotografia_id = Column(Integer, ForeignKey('fotografias.id'), nullable=False,
                          comment="ID de la fotografía")
    metadata_key = Column(String(100), nullable=False,
                         comment="Clave del metadato")
    metadata_value = Column(Text, nullable=True,
                           comment="Valor del metadato")
    data_type = Column(String(20), default="string", nullable=False,
                      comment="Tipo de dato (string, integer, float, boolean, json)")
    is_public = Column(Boolean, default=False, nullable=False,
                      comment="Si el metadato es público")
    
    def __repr__(self):
        return f"<FotografiaMetadata(foto={self.fotografia_id}, key='{self.metadata_key}')>"
    
    @classmethod
    def get_by_fotografia(cls, fotografia_id):
        """
        Obtiene metadatos de una fotografía específica.
        
        Args:
            fotografia_id (int): ID de la fotografía
            
        Returns:
            list: Lista de metadatos
        """
        return cls.query.filter_by(fotografia_id=fotografia_id, deleted=False).all()
    
    @classmethod
    def get_by_key(cls, metadata_key):
        """
        Obtiene metadatos por clave.
        
        Args:
            metadata_key (str): Clave del metadato
            
        Returns:
            list: Lista de metadatos con esa clave
        """
        return cls.query.filter_by(metadata_key=metadata_key, deleted=False).all()