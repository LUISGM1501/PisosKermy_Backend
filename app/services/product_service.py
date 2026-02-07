from ..repositories.product_repository import ProductRepository
from ..repositories.category_repository import CategoryRepository
from ..repositories.tag_repository import TagRepository
from ..repositories.provider_repository import ProviderRepository
from ..utils.errors import AppError
from ..utils.file import save_image, delete_image


class ProductService:

    @staticmethod
    def list_paginated(page, per_page, category_ids=None, tag_ids=None, provider_ids=None, search=None):
        return ProductRepository.get_paginated(page, per_page, category_ids, tag_ids, provider_ids, search)

    @staticmethod
    def get_by_id(product_id):
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise AppError('Producto no encontrado', 404)
        return product

    @staticmethod
    def _resolve_categories(category_ids):
        """Valida que todas las categorias existan y retorna las instancias."""
        result = []
        for cid in category_ids:
            cat = CategoryRepository.get_by_id(cid)
            if not cat:
                raise AppError(f'Categoria con id {cid} no encontrada', 404)
            result.append(cat)
        return result

    @staticmethod
    def _resolve_tags(tag_ids):
        """Valida que todas las etiquetas existan y retorna las instancias."""
        result = []
        for tid in tag_ids:
            tag = TagRepository.get_by_id(tid)
            if not tag:
                raise AppError(f'Etiqueta con id {tid} no encontrada', 404)
            result.append(tag)
        return result

    @staticmethod
    def _resolve_providers(provider_ids):
        """Valida que todos los proveedores existan y retorna las instancias."""
        result = []
        for pid in provider_ids:
            prov = ProviderRepository.get_by_id(pid)
            if not prov:
                raise AppError(f'Proveedor con id {pid} no encontrado', 404)
            result.append(prov)
        return result

    @staticmethod
    def create(validated_data, image_file=None):
        # Resolver relaciones
        categories = ProductService._resolve_categories(validated_data['category_ids'])
        tags       = ProductService._resolve_tags(validated_data['tag_ids'])
        providers  = ProductService._resolve_providers(validated_data['provider_ids'])

        # Guardar imagen si se envio
        if image_file:
            image_path = save_image(image_file)
            if not image_path:
                raise AppError('Tipo de imagen no permitido. Use: png, jpg, jpeg, webp', 400)
            validated_data['image_path'] = image_path

        return ProductRepository.create(validated_data, categories, tags, providers)

    @staticmethod
    def update(product_id, validated_data, image_file=None):
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise AppError('Producto no encontrado', 404)

        old_image = product.image_path

        # Guardar nueva imagen si se envio
        if image_file:
            new_image = save_image(image_file)
            if not new_image:
                raise AppError('Tipo de imagen no permitido. Use: png, jpg, jpeg, webp', 400)
            validated_data['image_path'] = new_image

        # Resolver relaciones solo si se incluyen en la actualizacion
        categories = None
        tags       = None
        providers  = None

        if 'category_ids' in validated_data:
            categories = ProductService._resolve_categories(validated_data.pop('category_ids'))
        if 'tag_ids' in validated_data:
            tags = ProductService._resolve_tags(validated_data.pop('tag_ids'))
        if 'provider_ids' in validated_data:
            providers = ProductService._resolve_providers(validated_data.pop('provider_ids'))

        updated = ProductRepository.update(product, validated_data, categories, tags, providers)

        # Eliminar imagen antigua solo despues de que el commit tuvo exito
        if image_file and old_image:
            delete_image(old_image)

        return updated, old_image

    @staticmethod
    def delete(product_id):
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise AppError('Producto no encontrado', 404)

        deleted_name  = product.name
        deleted_image = product.image_path

        ProductRepository.delete(product)

        # Eliminar archivo de imagen del disco
        if deleted_image:
            delete_image(deleted_image)

        return deleted_name