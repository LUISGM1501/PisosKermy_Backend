import os
import uuid
from flask import current_app


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_image(file):
    """Guarda el archivo subido en /uploads con un nombre unico. Retorna el nombre del archivo o None si no es valido."""
    if not file or not allowed_file(file.filename):
        return None

    extension = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{extension}"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return filename


def delete_image(filename):
    """Elimina un archivo de /uploads. No lanza error si el archivo no existe."""
    if not filename:
        return

    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)