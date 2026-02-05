import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Database: Supabase o desarrollo local
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # Producción (Supabase)
        # Supabase usa postgresql://, no necesita fix
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Desarrollo local
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{os.environ.get('DB_USER')}:"
            f"{os.environ.get('DB_PASSWORD')}@"
            f"{os.environ.get('DB_HOST', 'localhost')}:"
            f"{os.environ.get('DB_PORT', '5432')}/"
            f"{os.environ.get('DB_NAME')}"
        )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # CORS: permitir múltiples orígenes separados por coma
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173')

    # Ya no necesitamos UPLOAD_FOLDER porque usamos Cloudinary
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    
    # Cloudinary (se configura en utils/file.py)
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')