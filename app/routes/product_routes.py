from flask import Blueprint, request, jsonify
from ..services.product_service import ProductService
from ..schemas.product import ProductCreateSchema, ProductUpdateSchema, ProductResponseSchema
from ..utils.auth import require_auth
from ..utils.audit import log_audit
from ..utils.errors import ValidationError

product_bp = Blueprint('products', __name__)

PER_PAGE = 15


def _extract_product_data():
    """
    Extrae los datos del producto del request.
    Soporta JSON puro y tambien multipart/form-data (necesario cuando se sube imagen).
    En multipart, las listas se envian como valores multiples con la misma clave:
        category_ids=1&category_ids=3&category_ids=5
    """
    if request.is_json:
        return request.get_json()

    data = {}

    if 'name' in request.form:
        data['name'] = request.form['name']
    if 'description' in request.form:
        data['description'] = request.form['description']
    if 'price' in request.form:
        data['price'] = request.form['price']
    if 'category_ids' in request.form:
        data['category_ids'] = request.form.getlist('category_ids', type=int)
    if 'tag_ids' in request.form:
        data['tag_ids'] = request.form.getlist('tag_ids', type=int)
    if 'provider_ids' in request.form:
        data['provider_ids'] = request.form.getlist('provider_ids', type=int)

    return data


# ---------------------------------------------------------------------------
# Publico — catalogo con paginacion y filtros por categoria y etiqueta
# ---------------------------------------------------------------------------

@product_bp.route('/api/products', methods=['GET'])
def list_products():
    page        = request.args.get('page', 1, type=int)
    category_ids = request.args.getlist('category_id', type=int)
    tag_ids      = request.args.getlist('tag_id', type=int)

    paginated = ProductService.list_paginated(
        page=page,
        per_page=PER_PAGE,
        category_ids=category_ids or None,
        tag_ids=tag_ids or None,
    )

    return jsonify({
        'products':    ProductResponseSchema.serialize_many(paginated.items, include_admin_fields=False),
        'total':       paginated.total,
        'pages':       paginated.pages,
        'current_page': paginated.page,
        'per_page':    PER_PAGE,
    })


# ---------------------------------------------------------------------------
# Admin — CRUD completo, incluye precio y proveedores en la respuesta
# ---------------------------------------------------------------------------

@product_bp.route('/api/admin/products', methods=['GET'])
@require_auth
def admin_list_products():
    page        = request.args.get('page', 1, type=int)
    category_ids = request.args.getlist('category_id', type=int)
    tag_ids      = request.args.getlist('tag_id', type=int)

    paginated = ProductService.list_paginated(
        page=page,
        per_page=PER_PAGE,
        category_ids=category_ids or None,
        tag_ids=tag_ids or None,
    )

    return jsonify({
        'products':    ProductResponseSchema.serialize_many(paginated.items, include_admin_fields=True),
        'total':       paginated.total,
        'pages':       paginated.pages,
        'current_page': paginated.page,
        'per_page':    PER_PAGE,
    })


@product_bp.route('/api/admin/products', methods=['POST'])
@require_auth
def create_product():
    data = _extract_product_data()
    validated, errors = ProductCreateSchema.validate(data)
    if errors:
        raise ValidationError(errors)

    image_file = request.files.get('image')
    product = ProductService.create(validated, image_file)

    log_audit(
        admin_id=request.current_admin.id,
        action='CREATE',
        entity='product',
        entity_id=product.id,
        details={'name': product.name}
    )

    return jsonify(ProductResponseSchema.serialize(product, include_admin_fields=True)), 201


@product_bp.route('/api/admin/products/<int:product_id>', methods=['PUT'])
@require_auth
def update_product(product_id):
    data = _extract_product_data()
    validated, errors = ProductUpdateSchema.validate(data)
    if errors:
        raise ValidationError(errors)

    image_file = request.files.get('image')
    product, old_image = ProductService.update(product_id, validated, image_file)

    log_audit(
        admin_id=request.current_admin.id,
        action='UPDATE',
        entity='product',
        entity_id=product_id,
        details={'name': product.name, 'image_changed': old_image != product.image_path}
    )

    return jsonify(ProductResponseSchema.serialize(product, include_admin_fields=True))


@product_bp.route('/api/admin/products/<int:product_id>', methods=['DELETE'])
@require_auth
def delete_product(product_id):
    deleted_name = ProductService.delete(product_id)

    log_audit(
        admin_id=request.current_admin.id,
        action='DELETE',
        entity='product',
        entity_id=product_id,
        details={'name': deleted_name}
    )

    return jsonify({'message': 'Producto eliminado'})