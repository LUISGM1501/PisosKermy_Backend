import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify


def generate_token(admin_id):
    payload = {
        'admin_id': admin_id,
        'exp': datetime.utcnow() + timedelta(hours=8),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, os.environ.get('SECRET_KEY'), algorithm='HS256')


def decode_token(token):
    try:
        return jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=['HS256'])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def require_auth(f):
    """Decorador que protege una ruta. Setea request.current_admin si el token es valido."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token requerido'}), 401

        token = auth_header.split(' ')[1]
        payload = decode_token(token)

        if not payload:
            return jsonify({'error': 'Token invalido o expirado'}), 401

        from ..models import Admin
        from ..database import db

        admin = db.session.get(Admin, payload['admin_id'])
        if not admin or not admin.is_active:
            return jsonify({'error': 'Admin no encontrado o inactivo'}), 401

        request.current_admin = admin
        return f(*args, **kwargs)
    return decorated