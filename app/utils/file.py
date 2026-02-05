import os
import cloudinary
import cloudinary.uploader
from flask import current_app


def init_cloudinary():
    """Inicializa Cloudinary con las credenciales del entorno"""
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
        secure=True
    )


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_image(file):
    """
    Sube la imagen a Cloudinary y retorna la URL pública.
    Retorna None si el archivo no es válido.
    """
    if not file or not allowed_file(file.filename):
        return None

    try:
        # Subir a Cloudinary con carpeta 'pisos-kermy'
        result = cloudinary.uploader.upload(
            file,
            folder='pisos-kermy',
            resource_type='image',
            format='webp',  # Convertir a WebP automáticamente
            transformation=[
                {'quality': 'auto'},
                {'fetch_format': 'auto'}
            ]
        )
        return result['secure_url']
    except Exception as e:
        print(f"Error subiendo imagen a Cloudinary: {e}")
        return None


def delete_image(image_url):
    """
    Elimina una imagen de Cloudinary dado su URL.
    Extrae el public_id de la URL y lo elimina.
    """
    if not image_url or not image_url.startswith('https://res.cloudinary.com'):
        return

    try:
        # Extraer public_id de la URL de Cloudinary
        # Ejemplo: https://res.cloudinary.com/xxx/image/upload/v123/pisos-kermy/abc123.webp
        # public_id = pisos-kermy/abc123
        parts = image_url.split('/')
        if 'pisos-kermy' in parts:
            idx = parts.index('pisos-kermy')
            public_id = '/'.join(parts[idx:])
            # Quitar extensión
            public_id = public_id.rsplit('.', 1)[0]
            cloudinary.uploader.destroy(public_id)
    except Exception as e:
        print(f"Error eliminando imagen de Cloudinary: {e}")