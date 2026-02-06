from flask import Blueprint, request, jsonify
from ..models import Admin
from ..services.admin_service import AdminService
from ..schemas.admin_schema import (
    AdminCreateSchema,
    AdminUpdateSchema,
    AdminPasswordSchema,
    AdminResponseSchema
)
from ..utils.auth import generate_token, require_auth
from ..utils.audit import log_audit
from ..utils.errors import ValidationError

auth_bp = Blueprint('auth', __name__)


# ---------------------------------------------------------------------------
# Autenticacion
# ---------------------------------------------------------------------------

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
    """Listar todos los administradores."""
    admins = AdminService.list_all()
    return jsonify({'admins': AdminResponseSchema.serialize_many(admins)})


@auth_bp.route('/api/auth/admins', methods=['POST'])
@require_auth
def create_admin():
    """Crear nuevo administrador."""
    validated, errors = AdminCreateSchema.validate(request.get_json())
    if errors:
        raise ValidationError(errors)

    admin = AdminService.create(validated)

    log_audit(
        admin_id=request.current_admin.id,
        action='CREATE_ADMIN',
        entity='admin',
        entity_id=admin.id,
        details={'email': admin.email, 'name': admin.name}
    )

    return jsonify({
        'message': 'Admin creado exitosamente',
        'admin': AdminResponseSchema.serialize(admin)
    }), 201


@auth_bp.route('/api/auth/admins/<int:admin_id>', methods=['PUT'])
@require_auth
def update_admin(admin_id):
    """Actualizar datos de un administrador (nombre, email)."""
    validated, errors = AdminUpdateSchema.validate(request.get_json())
    if errors:
        raise ValidationError(errors)

    admin, old_data = AdminService.update(admin_id, validated)

    log_audit(
        admin_id=request.current_admin.id,
        action='UPDATE_ADMIN',
        entity='admin',
        entity_id=admin_id,
        details={
            'old_data': old_data,
            'new_data': {'email': admin.email, 'name': admin.name}
        }
    )

    return jsonify({
        'message': 'Admin actualizado exitosamente',
        'admin': AdminResponseSchema.serialize(admin)
    })


@auth_bp.route('/api/auth/admins/<int:admin_id>/password', methods=['PUT'])
@require_auth
def change_admin_password(admin_id):
    """Cambiar contraseña de un administrador."""
    validated, errors = AdminPasswordSchema.validate(request.get_json())
    if errors:
        raise ValidationError(errors)

    admin = AdminService.change_password(admin_id, validated)

    log_audit(
        admin_id=request.current_admin.id,
        action='CHANGE_PASSWORD',
        entity='admin',
        entity_id=admin_id,
        details={'target_admin': admin.email}
    )

    return jsonify({'message': 'Contraseña actualizada exitosamente'})


@auth_bp.route('/api/auth/admins/<int:admin_id>/toggle', methods=['PUT'])
@require_auth
def toggle_admin_status(admin_id):
    """Activar/Desactivar un administrador."""
    admin, action, old_status = AdminService.toggle_status(
        admin_id,
        request.current_admin.id
    )

    log_audit(
        admin_id=request.current_admin.id,
        action=action,
        entity='admin',
        entity_id=admin_id,
        details={
            'email': admin.email,
            'old_status': old_status,
            'new_status': admin.is_active
        }
    )

    status_text = 'activado' if admin.is_active else 'desactivado'
    return jsonify({
        'message': f'Admin {status_text} exitosamente',
        'admin': AdminResponseSchema.serialize(admin)
    })