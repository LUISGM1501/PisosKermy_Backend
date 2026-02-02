from flask import Blueprint, request, jsonify
from ..services.category_service import CategoryService
from ..schemas.category import CategoryCreateSchema, CategoryUpdateSchema, CategoryResponseSchema
from ..utils.auth import require_auth
from ..utils.audit import log_audit
from ..utils.errors import ValidationError

category_bp = Blueprint('categories', __name__)


# ---------------------------------------------------------------------------
# Publico — el cliente puede ver categorias sin autenticarse
# ---------------------------------------------------------------------------

@category_bp.route('/api/categories', methods=['GET'])
def list_categories():
    categories = CategoryService.list_all()
    return jsonify(CategoryResponseSchema.serialize_many(categories))


# ---------------------------------------------------------------------------
# Admin — todo el CRUD requiere token
# ---------------------------------------------------------------------------

@category_bp.route('/api/admin/categories', methods=['GET'])
@require_auth
def admin_list_categories():
    categories = CategoryService.list_all()
    return jsonify(CategoryResponseSchema.serialize_many(categories))


@category_bp.route('/api/admin/categories', methods=['POST'])
@require_auth
def create_category():
    validated, errors = CategoryCreateSchema.validate(request.get_json())
    if errors:
        raise ValidationError(errors)

    category = CategoryService.create(validated)

    log_audit(
        admin_id=request.current_admin.id,
        action='CREATE',
        entity='category',
        entity_id=category.id,
        details={'name': category.name}
    )

    return jsonify(CategoryResponseSchema.serialize(category)), 201


@category_bp.route('/api/admin/categories/<int:category_id>', methods=['PUT'])
@require_auth
def update_category(category_id):
    validated, errors = CategoryUpdateSchema.validate(request.get_json())
    if errors:
        raise ValidationError(errors)

    category, old_name = CategoryService.update(category_id, validated)

    log_audit(
        admin_id=request.current_admin.id,
        action='UPDATE',
        entity='category',
        entity_id=category_id,
        details={'old_name': old_name, 'new_name': category.name}
    )

    return jsonify(CategoryResponseSchema.serialize(category))


@category_bp.route('/api/admin/categories/<int:category_id>', methods=['DELETE'])
@require_auth
def delete_category(category_id):
    deleted_name = CategoryService.delete(category_id)

    log_audit(
        admin_id=request.current_admin.id,
        action='DELETE',
        entity='category',
        entity_id=category_id,
        details={'name': deleted_name}
    )

    return jsonify({'message': 'Categoria eliminada'})