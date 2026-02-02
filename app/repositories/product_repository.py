from ..database import db
from ..models import Product
from ..models.product import product_categories, product_tags


class ProductRepository:

    @staticmethod
    def get_paginated(page, per_page, category_ids=None, tag_ids=None):
        """Retorna productos paginados. Filtra por categorias y/o etiquetas si se pasan."""
        query = Product.query

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
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = data['price']
        if 'image_path' in data:
            product.image_path = data['image_path']

        # Solo reemplaza las relaciones si se pasan explicitamente
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