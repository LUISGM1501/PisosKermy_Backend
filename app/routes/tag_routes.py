from flask import Blueprint, request, jsonify
from ..services.tag_service import TagService
from ..schemas.tag import TagCreateSchema, TagUpdateSchema, TagResponseSchema
from ..utils.auth import require_auth
from ..utils.audit import log_audit
from ..utils.errors import ValidationError

tag_bp = Blueprint('tags', __name__)


# ---------------------------------------------------------------------------
# Publico
# ---------------------------------------------------------------------------

@tag_bp.route('/api/tags', methods=['GET'])
def list_tags():
    tags = TagService.list_all()
    return jsonify(TagResponseSchema.serialize_many(tags))


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------

@tag_bp.route('/api/admin/tags', methods=['GET'])
@require_auth
def admin_list_tags():
    tags = TagService.list_all()
    return jsonify(TagResponseSchema.serialize_many(tags))


@tag_bp.route('/api/admin/tags', methods=['POST'])
@require_auth
def create_tag():
    validated, errors = TagCreateSchema.validate(request.get_json())
    if errors:
        raise ValidationError(errors)

    tag = TagService.create(validated)

    log_audit(
        admin_id=request.current_admin.id,
        action='CREATE',
        entity='tag',
        entity_id=tag.id,
        details={'name': tag.name}
    )

    return jsonify(TagResponseSchema.serialize(tag)), 201


@tag_bp.route('/api/admin/tags/<int:tag_id>', methods=['PUT'])
@require_auth
def update_tag(tag_id):
    validated, errors = TagUpdateSchema.validate(request.get_json())
    if errors:
        raise ValidationError(errors)

    tag, old_name = TagService.update(tag_id, validated)

    log_audit(
        admin_id=request.current_admin.id,
        action='UPDATE',
        entity='tag',
        entity_id=tag_id,
        details={'old_name': old_name, 'new_name': tag.name}
    )

    return jsonify(TagResponseSchema.serialize(tag))


@tag_bp.route('/api/admin/tags/<int:tag_id>', methods=['DELETE'])
@require_auth
def delete_tag(tag_id):
    deleted_name = TagService.delete(tag_id)

    log_audit(
        admin_id=request.current_admin.id,
        action='DELETE',
        entity='tag',
        entity_id=tag_id,
        details={'name': deleted_name}
    )

    return jsonify({'message': 'Etiqueta eliminada'})