"""
Schemas para Product con soporte de múltiples imágenes
"""

from ..utils.file import get_image_url


class ProductImageSchema:
    """Schema para serializar ProductImage"""
    
    @staticmethod
    def serialize(product_image):
        """Serializar una imagen de producto"""
        if not product_image:
            return None
        
        return {
            'id': product_image.id,
            'image_url': get_image_url(product_image.image_path),
            'is_primary': product_image.is_primary,
            'display_order': product_image.display_order,
        }
    
    @staticmethod
    def serialize_many(product_images):
        """Serializar múltiples imágenes"""
        return [ProductImageSchema.serialize(img) for img in product_images]


class ProductResponseSchema:
    """Schema para respuestas de productos"""
    
    @staticmethod
    def serialize(product, include_admin_fields=False):
        """
        Serializar un producto.
        
        Args:
            product: Instancia de Product
            include_admin_fields: Si True, incluye precio y proveedores (solo admin)
        """
        if not product:
            return None
        
        # Datos básicos (públicos)
        data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'categories': [{'id': c.id, 'name': c.name} for c in product.categories],
            'tags': [{'id': t.id, 'name': t.name} for t in product.tags],
            
            # NUEVO: Múltiples imágenes
            'images': ProductImageSchema.serialize_many(product.images),
            
            # Compatibilidad: imagen principal
            'image_url': product.image_url,
        }
        
        # Campos solo para admin
        if include_admin_fields:
            data['price'] = float(product.price) if product.price else 0.0
            data['providers'] = [{'id': p.id, 'name': p.name} for p in product.providers]
        
        return data
    
    @staticmethod
    def serialize_many(products, include_admin_fields=False):
        """Serializar múltiples productos"""
        return [ProductResponseSchema.serialize(p, include_admin_fields) for p in products]


class ProductCreateSchema:
    """Schema para crear producto"""
    
    @staticmethod
    def validate(data):
        """
        Validar datos para crear producto.
        
        Returns:
            (validated_data, errors)
        """
        errors = {}
        
        # Validar nombre
        if not data.get('name'):
            errors['name'] = 'El nombre es requerido'
        elif len(data['name']) > 200:
            errors['name'] = 'El nombre no puede tener más de 200 caracteres'
        
        # Validar precio
        if 'price' not in data:
            errors['price'] = 'El precio es requerido'
        else:
            try:
                price = float(data['price'])
                if price < 0:
                    errors['price'] = 'El precio no puede ser negativo'
            except (ValueError, TypeError):
                errors['price'] = 'El precio debe ser un número válido'
        
        # Validar arrays (pueden estar vacíos)
        for field in ['category_ids', 'tag_ids', 'provider_ids']:
            if field not in data:
                data[field] = []
            elif not isinstance(data[field], list):
                errors[field] = f'{field} debe ser un array'
        
        if errors:
            return None, errors
        
        return data, None


class ProductUpdateSchema:
    """Schema para actualizar producto"""
    
    @staticmethod
    def validate(data):
        """
        Validar datos para actualizar producto.
        Similar a ProductCreateSchema pero todos los campos son opcionales.
        
        Returns:
            (validated_data, errors)
        """
        errors = {}
        
        # Validar nombre (opcional)
        if 'name' in data:
            if not data['name']:
                errors['name'] = 'El nombre no puede estar vacío'
            elif len(data['name']) > 200:
                errors['name'] = 'El nombre no puede tener más de 200 caracteres'
        
        # Validar precio (opcional)
        if 'price' in data:
            try:
                price = float(data['price'])
                if price < 0:
                    errors['price'] = 'El precio no puede ser negativo'
            except (ValueError, TypeError):
                errors['price'] = 'El precio debe ser un número válido'
        
        # Validar arrays (opcionales)
        for field in ['category_ids', 'tag_ids', 'provider_ids']:
            if field in data and not isinstance(data[field], list):
                errors[field] = f'{field} debe ser un array'
        
        if errors:
            return None, errors
        
        return data, None