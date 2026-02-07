from ..repositories.product_repository import ProductRepository
from ..repositories.category_repository import CategoryRepository
from ..repositories.tag_repository import TagRepository
from ..repositories.provider_repository import ProviderRepository
from ..models.product_image import ProductImage
from ..database import db
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
    def _save_product_images(product, image_files, primary_index=0):
        """
        Guardar múltiples imágenes para un producto.
        
        Args:
            product: Instancia de Product
            image_files: Lista de archivos de imagen
            primary_index: Índice de la imagen que será principal (default: 0)
        
        Returns:
            Lista de ProductImage creadas
        """
        if not image_files:
            return []
        
        saved_images = []
        
        for i, image_file in enumerate(image_files):
            # Guardar archivo físico
            image_path = save_image(image_file)
            if not image_path:
                continue  # Saltar si el tipo no es válido
            
            # Crear ProductImage
            product_image = ProductImage(
                product_id=product.id,
                image_path=image_path,
                is_primary=(i == primary_index),
                display_order=i
            )
            db.session.add(product_image)
            saved_images.append(product_image)
        
        if saved_images:
            db.session.flush()  # Para obtener IDs
            
            # Actualizar product.image_path con la imagen principal (compatibilidad)
            primary_img = next((img for img in saved_images if img.is_primary), saved_images[0])
            product.image_path = primary_img.image_path
        
        return saved_images

    @staticmethod
    def create(validated_data, image_files=None):
        """
        Crear producto con múltiples imágenes.
        
        Args:
            validated_data: Datos validados del producto
            image_files: Lista de archivos de imagen (opcional)
        """
        # Resolver relaciones
        categories = ProductService._resolve_categories(validated_data['category_ids'])
        tags       = ProductService._resolve_tags(validated_data['tag_ids'])
        providers  = ProductService._resolve_providers(validated_data['provider_ids'])

        # Crear producto (sin imágenes aún)
        product = ProductRepository.create(validated_data, categories, tags, providers)
        
        # Guardar imágenes
        if image_files:
            ProductService._save_product_images(product, image_files)
            db.session.commit()  # Commit para guardar imágenes
        
        return product

    @staticmethod
    def update(product_id, validated_data, image_files=None, keep_existing_images=True):
        """
        Actualizar producto.
        
        Args:
            product_id: ID del producto
            validated_data: Datos validados
            image_files: Nueva lista de archivos de imagen (opcional)
            keep_existing_images: Si False, elimina imágenes existentes
        """
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise AppError('Producto no encontrado', 404)

        # Resolver relaciones solo si se incluyen en la actualización
        categories = None
        tags       = None
        providers  = None

        if 'category_ids' in validated_data:
            categories = ProductService._resolve_categories(validated_data.pop('category_ids'))
        if 'tag_ids' in validated_data:
            tags = ProductService._resolve_tags(validated_data.pop('tag_ids'))
        if 'provider_ids' in validated_data:
            providers = ProductService._resolve_providers(validated_data.pop('provider_ids'))

        # Actualizar producto
        updated = ProductRepository.update(product, validated_data, categories, tags, providers)

        # Manejar imágenes nuevas
        if image_files:
            if not keep_existing_images:
                # Eliminar imágenes existentes
                old_images = list(product.images)  # Copiar lista
                for img in old_images:
                    delete_image(img.image_path)
                    db.session.delete(img)
                db.session.flush()
            
            # Guardar nuevas imágenes
            ProductService._save_product_images(product, image_files)
            db.session.commit()

        return updated

    @staticmethod
    def delete_product_image(product_id, image_id):
        """
        Eliminar una imagen específica de un producto.
        
        Args:
            product_id: ID del producto
            image_id: ID de la imagen a eliminar
        """
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise AppError('Producto no encontrado', 404)
        
        # Buscar la imagen
        image = next((img for img in product.images if img.id == image_id), None)
        if not image:
            raise AppError('Imagen no encontrada', 404)
        
        # No permitir eliminar si es la única imagen
        if len(product.images) == 1:
            raise AppError('No se puede eliminar la única imagen del producto', 400)
        
        # Si es la imagen principal, marcar otra como principal
        if image.is_primary and len(product.images) > 1:
            # Marcar la primera imagen restante como principal
            next_primary = next((img for img in product.images if img.id != image_id), None)
            if next_primary:
                next_primary.is_primary = True
                product.image_path = next_primary.image_path  # Actualizar cache
        
        # Eliminar archivo físico
        delete_image(image.image_path)
        
        # Eliminar de BD
        db.session.delete(image)
        db.session.commit()
        
        return True

    @staticmethod
    def set_primary_image(product_id, image_id):
        """
        Marcar una imagen como principal.
        
        Args:
            product_id: ID del producto
            image_id: ID de la imagen a marcar como principal
        """
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise AppError('Producto no encontrado', 404)
        
        # Buscar la imagen
        new_primary = next((img for img in product.images if img.id == image_id), None)
        if not new_primary:
            raise AppError('Imagen no encontrada', 404)
        
        # Desmarcar todas las imágenes como principales
        for img in product.images:
            img.is_primary = False
        
        # Marcar la nueva como principal
        new_primary.is_primary = True
        
        # Actualizar cache en product
        product.image_path = new_primary.image_path
        
        db.session.commit()
        
        return True

    @staticmethod
    def delete(product_id):
        """Eliminar producto y todas sus imágenes"""
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise AppError('Producto no encontrado', 404)

        deleted_name = product.name
        
        # Eliminar todas las imágenes físicas
        for img in product.images:
            delete_image(img.image_path)
        
        # Eliminar imagen legacy si existe
        if product.image_path:
            delete_image(product.image_path)

        # Eliminar producto (cascade eliminará ProductImages automáticamente)
        ProductRepository.delete(product)

        return deleted_name