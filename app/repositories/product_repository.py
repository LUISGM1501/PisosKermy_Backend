from ..database import db
from ..models import Product
from ..models.product import product_categories, product_tags, product_providers


class ProductRepository:

    @staticmethod
    def get_paginated(page, per_page, category_ids=None, tag_ids=None, provider_ids=None, search=None):
        """Retorna productos paginados. Filtra por categorias, etiquetas, proveedores y/o búsqueda por nombre."""
        query = Product.query

        # Búsqueda por nombre (insensible a mayúsculas/minúsculas)
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(Product.name.ilike(search_pattern))

        if category_ids:
            query = query.filter(
                Product.id.in_(
                    db.session.query(product_categories.c.product_id)
                    .filter(product_categories.c.category_id.in_(category_ids))
                )
            )

        if tag_ids:
            query = query.filter(
                Product.id.in_(
                    db.session.query(product_tags.c.product_id)
                    .filter(product_tags.c.tag_id.in_(tag_ids))
                )
            )

        if provider_ids:
            query = query.filter(
                Product.id.in_(
                    db.session.query(product_providers.c.product_id)
                    .filter(product_providers.c.provider_id.in_(provider_ids))
                )
            )

        return query.order_by(Product.name).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_by_id(product_id):
        return db.session.get(Product, product_id)

    @staticmethod
    def create(data, categories, tags, providers):
        product = Product(
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            image_path=data.get('image_path'),
        )
        product.categories = categories
        product.tags       = tags
        product.providers  = providers
        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def update(product, data, categories=None, tags=None, providers=None):
        """Actualiza producto. Solo modifica relaciones si se pasan."""
        for key, value in data.items():
            if hasattr(product, key):
                setattr(product, key, value)

        if categories is not None:
            product.categories = categories
        if tags is not None:
            product.tags = tags
        if providers is not None:
            product.providers = providers

        db.session.commit()
        return product

    @staticmethod
    def delete(product):
        db.session.delete(product)
        db.session.commit()