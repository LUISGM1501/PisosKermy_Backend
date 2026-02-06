from flask import Blueprint, request, jsonify
from ..models import Admin
from ..utils.auth import generate_token, require_auth
from ..utils.audit import log_audit

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400

    email    = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email y password requeridos'}), 400

    admin = Admin.query.filter_by(email=email).first()

    if not admin or not admin.is_active or not admin.check_password(password):
        return jsonify({'error': 'Credenciales incorrectas'}), 401

    token = generate_token(admin.id)
    log_audit(admin.id, 'LOGIN')

    return jsonify({
        'token': token,
        'admin': {
            'id':    admin.id,
            'email': admin.email,
            'name':  admin.name,
        }
    })


@auth_bp.route('/api/auth/me', methods=['GET'])
@require_auth
def get_me():
    admin = request.current_admin
    return jsonify({
        'id':        admin.id,
        'email':     admin.email,
        'name':      admin.name,
        'is_active': admin.is_active,
    })

# ---------------------------------------------------------------------------
# Bitacora (solo lectura, solo admins)
# ---------------------------------------------------------------------------

@auth_bp.route('/api/auth/audit', methods=['GET'])
@require_auth
def list_audit_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    from ..models import AuditLog

    paginated = (
        AuditLog.query
        .order_by(AuditLog.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    logs = []
    for log in paginated.items:
        logs.append({
            'id': log.id,
            'admin_id': log.admin_id,
            'admin_email': log.admin.email if log.admin else None,
            'action': log.action,
            'entity': log.entity,
            'entity_id': log.entity_id,
            'details': log.details,
            'ip_address': log.ip_address,
            'created_at': log.created_at.isoformat() if log.created_at else None,
        })

    return jsonify({
        'logs': logs,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': paginated.page,
    })

# ---------------------------------------------------------------------------
# Gestion de Admins (solo admins autenticados)
# ---------------------------------------------------------------------------

@auth_bp.route('/api/auth/admins', methods=['GET'])
@require_auth
def list_admins():
    """Listar todos los administradores"""
    admins = Admin.query.order_by(Admin.created_at.desc()).all()
    
    return jsonify({
        'admins': [
            {
                'id': admin.id,
                'email': admin.email,
                'name': admin.name,
                'is_active': admin.is_active,
                'created_at': admin.created_at.isoformat() if admin.created_at else None,
            }
            for admin in admins
        ]
    })


@auth_bp.route('/api/auth/admins', methods=['POST'])
@require_auth
def create_admin():
    """Crear nuevo administrador"""
    from ..database import db
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400
    
    email = data.get('email', '').strip()
    name = data.get('name', '').strip()
    password = data.get('password', '').strip()
    
    if not all([email, name, password]):
        return jsonify({'error': 'Email, nombre y password son requeridos'}), 400
    
    # Validar formato de email basico
    if '@' not in email or '.' not in email:
        return jsonify({'error': 'Email invalido'}), 400
    
    # Verificar que el email no exista
    if Admin.query.filter_by(email=email).first():
        return jsonify({'error': 'El email ya esta registrado'}), 400
    
    # Crear nuevo admin
    new_admin = Admin(email=email, name=name)
    new_admin.set_password(password)
    
    db.session.add(new_admin)
    db.session.commit()
    
    # Log de auditoria
    log_audit(
        request.current_admin.id, 
        'CREATE_ADMIN',
        entity='admin',
        entity_id=new_admin.id,
        details=f'Nuevo admin creado: {email}'
    )
    
    return jsonify({
        'message': 'Admin creado exitosamente',
        'admin': {
            'id': new_admin.id,
            'email': new_admin.email,
            'name': new_admin.name,
            'is_active': new_admin.is_active,
        }
    }), 201


@auth_bp.route('/api/auth/admins/<int:admin_id>', methods=['PUT'])
@require_auth
def update_admin(admin_id):
    """Actualizar datos de un administrador (nombre, email)"""
    from ..database import db
    
    admin = db.session.get(Admin, admin_id)
    if not admin:
        return jsonify({'error': 'Admin no encontrado'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400
    
    # Actualizar campos si se proporcionan
    if 'name' in data:
        name = data['name'].strip()
        if name:
            admin.name = name
    
    if 'email' in data:
        email = data['email'].strip()
        if not email or '@' not in email:
            return jsonify({'error': 'Email invalido'}), 400
        
        # Verificar que el nuevo email no este en uso por otro admin
        existing = Admin.query.filter(Admin.email == email, Admin.id != admin_id).first()
        if existing:
            return jsonify({'error': 'El email ya esta en uso'}), 400
        
        admin.email = email
    
    db.session.commit()
    
    log_audit(
        request.current_admin.id,
        'UPDATE_ADMIN',
        entity='admin',
        entity_id=admin_id,
        details=f'Admin actualizado: {admin.email}'
    )
    
    return jsonify({
        'message': 'Admin actualizado exitosamente',
        'admin': {
            'id': admin.id,
            'email': admin.email,
            'name': admin.name,
            'is_active': admin.is_active,
        }
    })


@auth_bp.route('/api/auth/admins/<int:admin_id>/password', methods=['PUT'])
@require_auth
def change_admin_password(admin_id):
    """Cambiar contraseña de un administrador"""
    from ..database import db
    
    admin = db.session.get(Admin, admin_id)
    if not admin:
        return jsonify({'error': 'Admin no encontrado'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400
    
    new_password = data.get('password', '').strip()
    
    if not new_password:
        return jsonify({'error': 'Password requerido'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'Password debe tener al menos 6 caracteres'}), 400
    
    # Cambiar contraseña
    admin.set_password(new_password)
    db.session.commit()
    
    log_audit(
        request.current_admin.id,
        'CHANGE_PASSWORD',
        entity='admin',
        entity_id=admin_id,
        details=f'Contraseña cambiada para: {admin.email}'
    )
    
    return jsonify({
        'message': 'Contraseña actualizada exitosamente'
    })


@auth_bp.route('/api/auth/admins/<int:admin_id>/toggle', methods=['PUT'])
@require_auth
def toggle_admin_status(admin_id):
    """Activar/Desactivar un administrador"""
    from ..database import db
    
    # No permitir desactivarse a si mismo
    if admin_id == request.current_admin.id:
        return jsonify({'error': 'No puedes desactivar tu propia cuenta'}), 400
    
    admin = db.session.get(Admin, admin_id)
    if not admin:
        return jsonify({'error': 'Admin no encontrado'}), 404
    
    # Cambiar estado
    admin.is_active = not admin.is_active
    db.session.commit()
    
    action = 'ACTIVATE_ADMIN' if admin.is_active else 'DEACTIVATE_ADMIN'
    log_audit(
        request.current_admin.id,
        action,
        entity='admin',
        entity_id=admin_id,
        details=f'Admin {"activado" if admin.is_active else "desactivado"}: {admin.email}'
    )
    
    return jsonify({
        'message': f'Admin {"activado" if admin.is_active else "desactivado"} exitosamente',
        'admin': {
            'id': admin.id,
            'email': admin.email,
            'name': admin.name,
            'is_active': admin.is_active,
        }
    })