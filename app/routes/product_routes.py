from flask import Blueprint, request, jsonify
import json
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
    Soporta JSON puro y multipart/form-data con arrays como JSON strings.
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
    
    # Parsear arrays que vienen como JSON strings
    if 'category_ids' in request.form:
        try:
            data['category_ids'] = json.loads(request.form['category_ids'])
        except (json.JSONDecodeError, ValueError):
            data['category_ids'] = []
    
    if 'tag_ids' in request.form:
        try:
            data['tag_ids'] = json.loads(request.form['tag_ids'])
        except (json.JSONDecodeError, ValueError):
            data['tag_ids'] = []
    
    if 'provider_ids' in request.form:
        try:
            data['provider_ids'] = json.loads(request.form['provider_ids'])
        except (json.JSONDecodeError, ValueError):
            data['provider_ids'] = []

    return data


def _get_filter_ids(param_name):
    """
    Obtiene IDs de filtro del request. Acepta tanto valores únicos como múltiples.
    Ejemplo: ?category_id=1 o ?category_id=1&category_id=2
    """
    # Intentar obtener lista de valores múltiples
    ids = request.args.getlist(param_name, type=int)
    
    # Si no hay valores múltiples, intentar valor único
    if not ids:
        single_id = request.args.get(param_name, type=int)
        if single_id:
            ids = [single_id]
    
    return ids if ids else None


# ---------------------------------------------------------------------------
# Publico - catalogo con paginacion y filtros por categoria, etiqueta y búsqueda
# ---------------------------------------------------------------------------

@product_bp.route('/api/products', methods=['GET'])
def list_products():
    page = request.args.get('page', 1, type=int)
    category_ids = _get_filter_ids('category_id')
    tag_ids = _get_filter_ids('tag_id')
    search = request.args.get('search', type=str, default='').strip()  # NUEVO

    paginated = ProductService.list_paginated(
        page=page,
        per_page=PER_PAGE,
        category_ids=category_ids,
        tag_ids=tag_ids,
        search=search if search else None,  # NUEVO
    )

    return jsonify({
        'products': ProductResponseSchema.serialize_many(paginated.items, include_admin_fields=False),
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': paginated.page,
        'per_page': PER_PAGE,
    })


@product_bp.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Obtener un producto por ID (publico, sin precio ni proveedores)"""
    product = ProductService.get_by_id(product_id)
    return jsonify(ProductResponseSchema.serialize(product, include_admin_fields=False))


# ---------------------------------------------------------------------------
# Admin - CRUD completo, incluye precio y proveedores en la respuesta
# ---------------------------------------------------------------------------

@product_bp.route('/api/admin/products', methods=['GET'])
@require_auth
def admin_list_products():
    page = request.args.get('page', 1, type=int)
    category_ids = _get_filter_ids('category_id')
    tag_ids = _get_filter_ids('tag_id')
    provider_ids = _get_filter_ids('provider_id')
    search = request.args.get('search', type=str, default='').strip()  # NUEVO

    paginated = ProductService.list_paginated(
        page=page,
        per_page=PER_PAGE,
        category_ids=category_ids,
        tag_ids=tag_ids,
        provider_ids=provider_ids,
        search=search if search else None,  # NUEVO
    )

    return jsonify({
        'products': ProductResponseSchema.serialize_many(paginated.items, include_admin_fields=True),
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': paginated.page,
        'per_page': PER_PAGE,
    })


@product_bp.route('/api/admin/products/<int:product_id>', methods=['GET'])
@require_auth
def admin_get_product(product_id):
    """Obtener un producto por ID (admin, con precio y proveedores)"""
    product = ProductService.get_by_id(product_id)
    return jsonify(ProductResponseSchema.serialize(product, include_admin_fields=True))


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