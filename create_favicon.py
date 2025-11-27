#!/usr/bin/env python3
"""
Script para crear un favicon.ico a partir del logo de UFRO
"""
from PIL import Image
import os

def create_favicon():
    """Crear favicon.ico a partir del logo de UFRO"""
    try:
        # Rutas de entrada y salida
        input_logo = '/workspace/sistema-camaras-ufro-limpio/static/images/logo-ufro.png'
        output_favicon = '/workspace/sistema-camaras-ufro-limpio/static/favicon.ico'
        
        # Verificar que existe el logo
        if not os.path.exists(input_logo):
            print(f"❌ Logo no encontrado: {input_logo}")
            return False
        
        # Abrir la imagen original
        img = Image.open(input_logo)
        
        # Convertir a RGBA si es necesario
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Redimensionar a 32x32 píxeles (tamaño estándar para favicon)
        favicon_size = (32, 32)
        favicon = img.resize(favicon_size, Image.Resampling.LANCZOS)
        
        # Crear múltiples tamaños para mejor compatibilidad
        sizes = [(16, 16), (32, 32), (48, 48)]
        favicon_images = []
        
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            favicon_images.append(resized)
        
        # Guardar como favicon.ico con múltiples tamaños
        favicon_images[0].save(
            output_favicon,
            'ICO',
            sizes=[(16, 16), (32, 32), (48, 48)]
        )
        
        print(f"✅ Favicon creado exitosamente: {output_favicon}")
        print(f"📏 Tamaños: {sizes}")
        return True
        
    except Exception as e:
        print(f"❌ Error creando favicon: {e}")
        return False

if __name__ == "__main__":
    create_favicon()