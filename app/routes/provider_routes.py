from flask import Blueprint, request, jsonify
from ..services.provider_service import ProviderService
from ..schemas.provider import ProviderCreateSchema, ProviderUpdateSchema, ProviderResponseSchema
from ..utils.auth import require_auth
from ..utils.audit import log_audit
from ..utils.errors import ValidationError

provider_bp = Blueprint('providers', __name__)


# ---------------------------------------------------------------------------
# Todo el CRUD esta dentro de admin. Los proveedores nunca son visibles publicamente.
# ---------------------------------------------------------------------------

@provider_bp.route('/api/admin/providers', methods=['GET'])
@require_auth
def list_providers():
    providers = ProviderService.list_all()
    return jsonify(ProviderResponseSchema.serialize_many(providers))


@provider_bp.route('/api/admin/providers', methods=['POST'])
@require_auth
def create_provider():
    validated, errors = ProviderCreateSchema.validate(request.get_json())
    if errors:
        raise ValidationError(errors)

    provider = ProviderService.create(validated)

    log_audit(
        admin_id=request.current_admin.id,
        action='CREATE',
        entity='provider',
        entity_id=provider.id,
        details={'name': provider.name}
    )

    return jsonify(ProviderResponseSchema.serialize(provider)), 201


@provider_bp.route('/api/admin/providers/<int:provider_id>', methods=['PUT'])
@require_auth
def update_provider(provider_id):
    validated, errors = ProviderUpdateSchema.validate(request.get_json())
    if errors:
        raise ValidationError(errors)

    provider, old_data = ProviderService.update(provider_id, validated)

    log_audit(
        admin_id=request.current_admin.id,
        action='UPDATE',
        entity='provider',
        entity_id=provider_id,
        details={'old': old_data, 'new': ProviderResponseSchema.serialize(provider)}
    )

    return jsonify(ProviderResponseSchema.serialize(provider))


@provider_bp.route('/api/admin/providers/<int:provider_id>', methods=['DELETE'])
@require_auth
def delete_provider(provider_id):
    deleted_name = ProviderService.delete(provider_id)

    log_audit(
        admin_id=request.current_admin.id,
        action='DELETE',
        entity='provider',
        entity_id=provider_id,
        details={'name': deleted_name}
    )

    return jsonify({'message': 'Proveedor eliminado'})