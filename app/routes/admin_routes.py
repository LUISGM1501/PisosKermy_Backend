from flask import Blueprint, request, jsonify
from ..services.admin_service import AdminService
from ..schemas.admin_schema import (
    AdminCreateSchema,
    AdminUpdateSchema,
    AdminPasswordSchema,
    AdminResponseSchema
)
from ..utils.auth import require_auth
from ..utils.audit import log_audit
from ..utils.errors import ValidationError

admin_bp = Blueprint('admins', __name__)


# ---------------------------------------------------------------------------
# Gestion de Admins (solo admins autenticados)
# ---------------------------------------------------------------------------

@admin_bp.route('/api/auth/admins', methods=['GET'])
@require_auth
def list_admins():
    """Listar todos los administradores."""
    admins = AdminService.list_all()
    return jsonify({'admins': AdminResponseSchema.serialize_many(admins)})


@admin_bp.route('/api/auth/admins', methods=['POST'])
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


@admin_bp.route('/api/auth/admins/<int:admin_id>', methods=['PUT'])
@require_auth
def update_admin(admin_id):
    """Actualizar datos de un administrador (nombre, email).
    
    PROTECCION: Solo admin 1 puede modificar admin 1
    """
    validated, errors = AdminUpdateSchema.validate(request.get_json())
    if errors:
        raise ValidationError(errors)

    admin, old_data = AdminService.update(admin_id, validated, request.current_admin.id)

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


@admin_bp.route('/api/auth/admins/<int:admin_id>/password', methods=['PUT'])
@require_auth
def change_admin_password(admin_id):
    """Cambiar contraseña de un administrador.
    
    PROTECCION: Solo admin 1 puede cambiar password de admin 1
    """
    validated, errors = AdminPasswordSchema.validate(request.get_json())
    if errors:
        raise ValidationError(errors)

    admin = AdminService.change_password(admin_id, validated, request.current_admin.id)

    log_audit(
        admin_id=request.current_admin.id,
        action='CHANGE_PASSWORD',
        entity='admin',
        entity_id=admin_id,
        details={'target_admin': admin.email}
    )

    return jsonify({'message': 'Contraseña actualizada exitosamente'})


@admin_bp.route('/api/auth/admins/<int:admin_id>/toggle', methods=['PUT'])
@require_auth
def toggle_admin_status(admin_id):
    """Activar/Desactivar un administrador.
    
    PROTECCIONES:
    - No puede desactivarse a si mismo
    - NO se puede desactivar admin 1 (nunca)
    """
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